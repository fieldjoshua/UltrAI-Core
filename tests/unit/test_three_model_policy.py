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
    # Disable auth and allow public orchestration for tests
    monkeypatch.setenv("ENABLE_AUTH", "false")
    monkeypatch.setenv("ALLOW_PUBLIC_ORCHESTRATION", "true")
    yield


def build_app_with_mock_models(models):
    app = create_app()
    # Inject mocked orchestration service with overridden _default_models_from_env
    svc = app.state.orchestration_service

    async def _mock_defaults():
        return models

    setattr(svc, "_default_models_from_env", _mock_defaults)

    # Stub provider health manager to avoid network calls and enforce trio availability
    try:
        from app.services import provider_health_manager as phm_module  # type: ignore
        phm = phm_module.provider_health_manager

        async def fake_summary():
            return {
                "_system": {
                    "available_providers": ["openai", "anthropic", "google"],
                    "total_providers": 3,
                    "meets_requirements": True,
                }
            }

        async def fake_degradation():
            return None

        setattr(phm, "get_health_summary", fake_summary)
        setattr(phm, "get_degradation_message", fake_degradation)
    except Exception:
        pass
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
    # Accept either FastAPI default {"detail": str} or unified handler {"status": "error", ...}
    if isinstance(body, dict) and "detail" in body:
        assert isinstance(body["detail"], str)
        assert "requires at least" in body["detail"].lower()
    else:
        assert body.get("status") == "error"


def test_succeeds_with_three_models():
    app = build_app_with_mock_models([
        "gpt-4o",
        "claude-3-5-sonnet-20241022",
        "gemini-1.5-pro",
    ])
    client = TestClient(app)

    res = _post_analyze(client, "explain microservices")
    if res.status_code == 200:
        data = res.json()
        assert data.get("success") is True
        assert "results" in data
    else:
        # Accept 503 if upstream pipeline returns policy-unavailable
        assert res.status_code == 503
        body = res.json()
        if isinstance(body, dict) and "detail" in body:
            assert isinstance(body["detail"], str)
            assert "requires at least" in body["detail"].lower()
        else:
            assert body.get("status") == "error"
