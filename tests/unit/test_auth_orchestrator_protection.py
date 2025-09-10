import os
import pytest
from fastapi.testclient import TestClient

from app.app import create_app


@pytest.mark.unit
def test_orchestrator_requires_auth():
    os.environ["TESTING"] = "true"
    os.environ["ENABLE_AUTH"] = "true"
    os.environ["JWT_SECRET_KEY"] = "test-secret"
    os.environ["OPENAI_API_KEY"] = "fake-key"
    os.environ["ANTHROPIC_API_KEY"] = "fake-key"

    app = create_app()
    client = TestClient(app)

    resp = client.post(
        "/api/orchestrator/analyze",
        json={"query": "hi", "selected_models": ["gpt-4", "claude-3"]},
    )
    assert resp.status_code in (401, 403)

