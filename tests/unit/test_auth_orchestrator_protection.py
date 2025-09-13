import os
# Set environment variables BEFORE any app imports
os.environ["TESTING"] = "true"
os.environ["JWT_SECRET_KEY"] = "test-secret-key"

import pytest
from fastapi.testclient import TestClient

from app.app import create_app
from app.config import Config


@pytest.mark.unit
def test_orchestrator_requires_auth():
    # Additional test-specific environment
    os.environ["ENABLE_AUTH"] = "true"
    os.environ["OPENAI_API_KEY"] = "fake-key"
    os.environ["ANTHROPIC_API_KEY"] = "fake-key"
    
    # Ensure config is updated for the test app instance
    Config.ENABLE_AUTH = True

    app = create_app()
    client = TestClient(app)

    resp = client.post(
        "/api/orchestrator/analyze",
        json={"query": "hi", "selected_models": ["gpt-4", "claude-3"]},
    )
    assert resp.status_code in (401, 403)

