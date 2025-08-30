import os
import pytest
from fastapi.testclient import TestClient

from app.app import create_app


@pytest.fixture
def client():
    os.environ["TESTING"] = "true"
    app = create_app()
    return TestClient(app)


def test_orchestrator_analyze_schema_validation(client):
    # Missing required field 'query'
    resp = client.post("/api/orchestrator/analyze", json={"analysis_type": "confidence"})
    assert resp.status_code in (400, 422)


def test_orchestrator_analyze_success_smoke(client, monkeypatch):
    # Bypass auth/db checks in test mode
    headers = {"X-Test-Mode": "true", "X-Skip-DB-Check": "true"}
    payload = {
        "query": "Say hi",
        "analysis_type": "confidence",
        "selected_models": ["gpt-4"],
        "options": {},
        "user_id": "route-test",
        "save_outputs": False,
        "include_pipeline_details": False,
        "include_initial_responses": False,
    }

    resp = client.post("/api/orchestrator/analyze", json=payload, headers=headers)
    # Should not 401 and should return JSON with success key
    assert resp.status_code in (200, 503, 429)
    data = resp.json()
    assert isinstance(data, dict)
    # success may be True/False depending on upstream availability, but key should exist
    assert "success" in data


