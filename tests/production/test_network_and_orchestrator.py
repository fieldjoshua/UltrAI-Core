import os
import socket
import pytest
from fastapi.testclient import TestClient

from app.main import create_production_app


@pytest.mark.production
@pytest.mark.skipif(
    not os.getenv("OPENAI_API_KEY") or not os.getenv("ANTHROPIC_API_KEY"),
    reason="Production tests require OPENAI_API_KEY and ANTHROPIC_API_KEY"
)
@pytest.mark.asyncio
async def test_external_endpoints_reachable():
    """Check that essential external provider hosts are reachable on port 443."""

    hosts = [
        "api.openai.com",
        "api.anthropic.com",
        "generativelanguage.googleapis.com",
    ]
    unreachable = []
    for host in hosts:
        try:
            sock = socket.create_connection((host, 443), timeout=5)
            sock.close()
        except OSError:
            unreachable.append(host)

    assert not unreachable, f"Unable to reach {unreachable} on port 443"


@pytest.mark.production
@pytest.mark.skipif(
    not os.getenv("OPENAI_API_KEY"),
    reason="Production test requires OPENAI_API_KEY"
)
def test_orchestrator_pipeline_openai():
    """Run the full orchestrator pipeline against OpenAI with real key."""

    api_key = os.getenv("OPENAI_API_KEY")
    # No need to fail here since skipif handles it

    # Restrict to a single model to limit cost
    request_payload = {
        "query": "Briefly describe the Eiffel Tower in two sentences.",
        "selected_models": ["gpt-3.5-turbo"],
    }

    app = create_production_app()
    client = TestClient(app)

    response = client.post("/api/orchestrator/analyze", json=request_payload)
    assert response.status_code == 200, response.text

    data = response.json()
    assert data["success"], f"Pipeline reported failure: {data.get('error')}"

    ultra = data["results"].get("ultra_synthesis", {})
    assert ultra, "ultra_synthesis missing from response"
    synthesis_text = ultra.get("synthesis") or ultra.get("output") or ""
    assert len(synthesis_text.split()) >= 20, "Synthesis text too short"
