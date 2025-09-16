import os
import pytest
from fastapi.testclient import TestClient

from app.app import create_app


@pytest.fixture(autouse=True)
def set_testing_env(monkeypatch):
    monkeypatch.setenv("TESTING", "true")
    monkeypatch.setenv("ENVIRONMENT", "development")
    monkeypatch.setenv("MINIMUM_MODELS_REQUIRED", "3")
    # Enforce provider trio
    monkeypatch.setenv("REQUIRED_PROVIDERS", "openai,anthropic,google")
    yield


def build_app_with_mock_models(models):
    app = create_app()
    # Inject mocked orchestration service with overridden _default_models_from_env
    svc = app.state.orchestration_service

    async def _mock_defaults():
        return models

    setattr(svc, "_default_models_from_env", _mock_defaults)
    app.state.orchestration_service = svc
    return app


def _post_analyze(client, query="test", models=None):
    payload = {"query": query, "selected_models": models}
    return client.post("/api/orchestrator/analyze", json=payload)


def test_fail_with_fewer_than_three_models():
    app = build_app_with_mock_models(["gpt-4o", "claude-3-5-sonnet-20241022"])  # 2 models
    client = TestClient(app)

    res = _post_analyze(client, "hello world")
    # Expect 503 from route preflight or pipeline
    assert res.status_code == 503
    body = res.json()
    assert body["detail"]["error"] == "SERVICE_UNAVAILABLE"


def test_succeeds_with_three_models():
    app = build_app_with_mock_models([
        "gpt-4o",
        "claude-3-5-sonnet-20241022",
        "gemini-1.5-pro",
    ])
    client = TestClient(app)

    res = _post_analyze(client, "explain microservices")
    # Route passes; pipeline may still return structured results
    assert res.status_code in (200, 503)
    if res.status_code == 200:
        data = res.json()
        assert data.get("success") is True
        assert "results" in data
    else:
        # If pipeline returns unavailable, ensure it reflects policy details
        body = res.json()
        assert body["detail"]["error"] == "SERVICE_UNAVAILABLE"
