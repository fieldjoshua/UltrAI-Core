import os
import pytest
import re
from playwright.sync_api import Page, expect

# Base URL of the running web UI.  Override with env var for CI / production.
BASE_URL = os.getenv("WEB_APP_URL", "http://localhost:3000")

QUERY = "Briefly describe the Eiffel Tower"


@pytest.mark.e2e
@pytest.mark.playwright
def test_ultra_synthesis_via_ui(page: Page):
    """Drive the web interface and ensure Ultra-Synthesis returns a real answer."""
    # 1. Load homepage
    page.goto(BASE_URL, timeout=60_000)

    # 2. Enter a query – assumes a textarea or input with placeholder text
    #    Adjust selector if the UI changes.
    # Prefer a stable data-testid if present; fallback to role
    if page.locator("[data-testid='prompt-input']").count():
        page.locator("[data-testid='prompt-input']").fill(QUERY)
    else:
        page.get_by_role("textbox").fill(QUERY)

    # 3. Click the primary analyse / run button (case-insensitive label search)
    if page.locator("[data-testid='run-analysis']").count():
        page.locator("[data-testid='run-analysis']").click()
    else:
        run_button = page.get_by_role("button", name=re.compile(r"(run|analy)", re.I))
        run_button.click()

    # 4. Wait for the XHR/fetch sent to the orchestrator endpoint, then grab JSON
    resp = page.wait_for_response(  # type: ignore[attr-defined]
        lambda r: "/orchestrator/analyze" in r.url and r.status == 200,
        timeout=120_000,
    )
    data = resp.json()

    # 5. Validate Ultra-Synthesis part of payload
    ultra = (
        data.get("results", {}).get("ultra_synthesis")
        if "results" in data
        else data.get("ultra_synthesis", {})
    )
    assert ultra, "ultra_synthesis section missing from API response"
    assert ultra.get("error") is None, f"Ultra-Synthesis error: {ultra.get('error')}"

    # When successful, response may store synthesis under 'synthesis' or 'output'
    synthesis_text = ultra.get("synthesis") or ultra.get("output") or ""
    # Basic sanity: should not be empty and should not contain model header artefacts
    assert len(synthesis_text.split()) > 30, "Ultra synthesis text too short"
    assert (
        "Model " not in synthesis_text.split("\n")[0]
    ), "Ultra synthesis appears to be stacked responses, not a single synthesis"

    # 6. Also ensure the UI shows something in the Ultra pane (if data-testid wired)
    #    Non-fatal check: only run if selector exists.
    if page.locator("[data-testid='ultra-synthesis']").count():
        expect(page.locator("[data-testid='ultra-synthesis']")).to_contain_text(
            synthesis_text[:30]
        )
