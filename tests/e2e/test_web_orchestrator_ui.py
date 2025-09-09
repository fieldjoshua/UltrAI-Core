import os
import pytest
import re

# Skip this entire module if Playwright isn't installed or not explicitly enabled
try:
    from playwright.sync_api import Page, expect  # type: ignore
    _playwright_import_ok = True
except Exception:
    Page = None  # type: ignore
    expect = None  # type: ignore
    _playwright_import_ok = False

# Disable Playwright tests by default; enable by setting ENABLE_PLAYWRIGHT=true
if not _playwright_import_ok or os.getenv("ENABLE_PLAYWRIGHT", "false").lower() != "true":
    pytestmark = pytest.mark.skip(reason="Playwright E2E disabled by default or not available. Set ENABLE_PLAYWRIGHT=true and install Playwright to run.")

# Base URL of the running web UI.  Override with env var for CI / production.
BASE_URL = os.getenv("WEB_APP_URL", "https://ultrai-core.onrender.com")

QUERY = "Compare renewable energy vs fossil fuels briefly"


@pytest.mark.e2e
@pytest.mark.playwright
def test_ultra_synthesis_via_ui(page: Page):
    """Drive the web interface and ensure Ultra-Synthesis returns a real answer."""
    # 1. Load homepage
    page.goto(BASE_URL, timeout=60_000)

    # 2. Enter a query – prefer stable data-testid, fallback to role
    if page.locator("[data-testid='prompt-input']").count():
        page.locator("[data-testid='prompt-input']").fill(QUERY)
    else:
        page.get_by_role("textbox").fill(QUERY)

    # 3. Click run button – prefer stable data-testid, fallback to role
    if page.locator("[data-testid='run-analysis']").count():
        page.locator("[data-testid='run-analysis']").click()
    else:
        page.get_by_role("button", name=re.compile(r"(generate|run|analy)", re.I)).click()

    # 4. Wait for the XHR/fetch sent to the orchestrator endpoint, then grab JSON
    resp = page.wait_for_event(
        "response",
        lambda r: (
            "/orchestrator/analyze" in r.url or "/api/orchestrator/analyze" in r.url
        )
        and r.status == 200,
        timeout=120_000,
    )
    data = resp.json()

    # 5. Validate multi-provider functionality worked
    initial_response = data.get("results", {}).get("initial_response", {})
    successful_models = []
    models_attempted = []
    if initial_response:
        initial_output = initial_response.get("output", {})
        successful_models = initial_output.get("successful_models", [])
        models_attempted = initial_output.get("models_attempted", [])
        print(f"Models attempted: {models_attempted}")
        print(f"Successful models: {successful_models}")
        # Validate that multiple models were attempted and succeeded
        assert len(models_attempted) >= 2, f"Expected multiple models attempted, got {len(models_attempted)}: {models_attempted}"
        assert len(successful_models) >= 2, f"Expected multiple successful models, got {len(successful_models)}: {successful_models}"
    # 6. Validate Ultra-Synthesis part of payload
    ultra = (
        data.get("results", {}).get("ultra_synthesis")
        if "results" in data
        else data.get("ultra_synthesis", {})
    )
    assert ultra, "ultra_synthesis section missing from API response"
    # Handle case where ultra might be a string directly
    if isinstance(ultra, str):
        synthesis_text = ultra
    else:
        assert ultra.get("error") is None, f"Ultra-Synthesis error: {ultra.get('error')}"
        # When successful, response may store synthesis under 'synthesis' or 'output'
        synthesis_text = ultra.get("synthesis") or ultra.get("output") or ""
        if not synthesis_text and isinstance(ultra.get("output"), dict):
            synthesis_text = ultra["output"].get("synthesis", "")
        if isinstance(synthesis_text, dict):
            synthesis_text = (
                synthesis_text.get("content") or synthesis_text.get("text") or ""
            )
    # Basic sanity: should not be empty and should not contain model header artefacts
    assert len(synthesis_text.split()) >= 20, "Ultra synthesis text unexpectedly short"
    assert (
        "Model " not in synthesis_text.split("\n")[0]
    ), "Ultra synthesis appears to be stacked responses, not a single synthesis"
    # Validate that synthesis contains topic-relevant content (not generic)
    topic_keywords = ['renewable', 'energy', 'fossil', 'fuel', 'benefit', 'environment']
    synthesis_lower = synthesis_text.lower()
    topic_matches = sum(1 for keyword in topic_keywords if keyword in synthesis_lower)
    assert topic_matches >= 2, f"Ultra synthesis doesn't contain relevant topic content (only {topic_matches} matches)"
    print("✅ Multi-provider E2E test passed!")
    print(f"   Successful models: {len(successful_models)}")
    print(f"   Synthesis length: {len(synthesis_text.split())} words")
    print(f"   Topic relevance: {topic_matches} keywords matched")

    # 6. Also ensure the UI shows something in the Ultra pane (if data-testid wired)
    #    Non-fatal check: only run if selector exists.
    if page.locator("[data-testid='ultra-synthesis']").count():
        expect(page.locator("[data-testid='ultra-synthesis']")).to_contain_text(
            synthesis_text[:30]
        )
