import os
from unittest.mock import AsyncMock

from fastapi.testclient import TestClient
from app.app import create_app


def test_orchestrator_auto_selects_model_when_missing():
    os.environ["ENVIRONMENT"] = "development"
    os.environ["TESTING"] = "true"

    app = create_app()
    client = TestClient(app)

    # Ensure service is attached
    assert hasattr(app.state, "services")
    selector = app.state.services.get("model_selector")
    assert selector is not None

    # Mock choose_models to return a known model
    selector.choose_models = AsyncMock(return_value=["gpt-4o"])

    payload = {
        "query": "test query",
        "analysis_type": "technical",
        "options": {},
        "save_outputs": False,
        "include_pipeline_details": False,
    }

    r = client.post("/api/orchestrator/analyze", json=payload, headers={"X-Test-Mode": "true"})
    assert r.status_code == 200
    data = r.json()
    assert data.get("success") is True
    assert data.get("pipeline_info", {}).get("models_used") == ["gpt-4o"]  # noqa: W391

