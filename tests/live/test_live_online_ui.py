import os
import re
import pytest
from playwright.sync_api import Page, expect

# LIVE_ONLINE test – uses the actual running web application and real LLM providers.
# No internal stubs or TESTING shortcuts are active.

BASE_URL = os.getenv("WEB_APP_URL", "http://localhost:3000")
QUERY = "Briefly describe the Eiffel Tower"


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

    # 4. Wait for backend response (either /orchestrator or /api/orchestrator path)
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
