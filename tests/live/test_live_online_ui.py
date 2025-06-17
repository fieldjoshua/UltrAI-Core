import os
import re
import random
import pytest
from playwright.sync_api import Page, expect
import json

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

    # Dynamically build the model list so we only request providers whose API
    # keys are present in the environment.  This makes the test truly reflect
    # the capabilities of the current deployment.

    selected_models = []
    if os.getenv("OPENAI_API_KEY"):
        selected_models.extend(["gpt-4", "gpt-3.5-turbo"])
    if os.getenv("ANTHROPIC_API_KEY"):
        selected_models.append("claude-3-5-sonnet-20241022")
    if os.getenv("GOOGLE_API_KEY"):
        selected_models.append("gemini-1.5-pro")
    if os.getenv("HF_API_TOKEN") or os.getenv("HUGGINGFACE_API_KEY"):
        selected_models.append("meta-llama/Meta-Llama-3.1-70B-Instruct")

    assert (
        selected_models
    ), "LIVE_ONLINE test cannot run: no provider API keys found in environment"

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

    # Intercept the orchestrator request to inject selected_models; use
    # Playwright request interception.

    def _route_intercept(route, request):
        if request.url.endswith("/orchestrator/analyze") and request.method == "POST":
            original = request.post_data_json
            original.update({"selected_models": selected_models})
            route.continue_(post_data=json.dumps(original))
        else:
            route.continue_()

    page.route(re.compile(r"/orchestrator/analyze"), _route_intercept)

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
    initial_meta = payload.get("results", {}).get("initial_response", {})
    attempted = set(initial_meta.get("models_attempted", []))
    succeeded = set(initial_meta.get("successful_models", []))
    missing = attempted - succeeded
    assert (
        not missing
    ), f"Models attempted but with no successful response: {sorted(missing)}"
