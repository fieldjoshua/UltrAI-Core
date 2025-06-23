import os
import re
import random
import pytest
from playwright.sync_api import Page, expect
import json
from difflib import SequenceMatcher

# LIVE_ONLINE test – uses the actual running web application and real LLM providers.
# No internal stubs or TESTING shortcuts are active.

BASE_URL = os.getenv("WEB_APP_URL", "http://localhost:3000")

# Five diverse prompts; one will be chosen at random for every run so we
# exercise different token counts and knowledge domains.
PROMPTS = [
    "Briefly describe the Eiffel Tower.",
    "Summarize the plot of Shakespeare's Hamlet in two sentences.",
    "Explain Newton's first law of motion as if teaching a 12-year-old.",
    "List three key differences between HTTP/1.1 and HTTP/2.",
    "Provide a short biography of Ada Lovelace highlighting her contributions to computing.",
]

# Pick one prompt nondeterministically (pytest shows which via test id)
QUERY = random.choice(PROMPTS)


@pytest.mark.live_online
@pytest.mark.playwright
def test_live_ultra_synthesis_via_ui(page: Page):
    """Simulate a real user running an analysis through the UI with live models."""

    # 1. Load homepage (front-end is assumed to be running separately)
    page.goto(BASE_URL, timeout=90_000)

    # 2. Enter prompt – prefer stable data-testid selector
    if page.locator("[data-testid='prompt-input']").count():
        page.locator("[data-testid='prompt-input']").fill(QUERY)
    else:
        page.get_by_role("textbox").fill(QUERY)

    # 3. Click run button
    if page.locator("[data-testid='run-analysis']").count():
        page.locator("[data-testid='run-analysis']").click()
    else:
        page.get_by_role("button", name=re.compile(r"(run|analy)", re.I)).click()

    resp = page.wait_for_event(
        "response",
        lambda r: (
            "/orchestrator/analyze" in r.url or "/api/orchestrator/analyze" in r.url
        )
        and r.status == 200,
        timeout=180_000,
    )
    payload = resp.json()

    # 5. Validate Ultra-Synthesis in payload
    ultra = payload.get("results", {}).get("ultra_synthesis", {})
    assert ultra, "ultra_synthesis missing in live response"
    assert ultra.get("error") is None, f"Ultra-Synthesis error: {ultra.get('error')}"

    synthesis_val = ultra.get("synthesis") or ultra.get("output") or ""
    if isinstance(synthesis_val, dict):
        synthesis_text = synthesis_val.get("content") or synthesis_val.get("text") or ""
    else:
        synthesis_text = synthesis_val

    assert (
        isinstance(synthesis_text, str) and len(synthesis_text.split()) >= 20
    ), "Synthesis text unexpectedly short (live)"

    # 6. Confirm UI rendered some of the synthesis
    if page.locator("[data-testid='ultra-synthesis']").count():
        expect(page.locator("[data-testid='ultra-synthesis']")).to_contain_text(
            synthesis_text[:30]
        )

    # 7. Verify that every model attempted by the backend produced a response
    initial = payload.get("results", {}).get("initial_response", {})
    responses = (
        initial.get("output", {}).get("responses")
        if isinstance(initial.get("output"), dict)
        else None
    ) or {}

    meta_attempted = set(initial.get("output", {}).get("models_attempted", []))
    attempted = meta_attempted or set(responses.keys())
    succeeded = {
        m
        for m, txt in responses.items()
        if isinstance(txt, str) and not txt.lower().startswith("error:") and txt.strip()
    }
    missing = attempted - succeeded

    # Fail if at least one model that was attempted didn't return a usable answer.
    assert not missing, (
        "\nLive backend attempted models that failed: "
        f"{', '.join(sorted(missing))}."
        "\nFull responses: " + json.dumps(responses, indent=2)[:500]
    )

    # 8. Guard against copy-paste: fail if Ultra-Synthesis is ≥90 % identical to any single peer response
    if responses:
        worst_overlap = max(
            SequenceMatcher(None, synthesis_text.lower(), peer.lower()).ratio()
            for peer in responses.values()
            if isinstance(peer, str)
        )

        assert worst_overlap < 0.90, (
            f"Ultra-Synthesis appears to be {worst_overlap:.0%} duplicated from a peer response. "
            "Possible copy-paste instead of synthesis."
        )
