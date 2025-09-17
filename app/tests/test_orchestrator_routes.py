import os
import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient

from app.app import create_app


@pytest.fixture
def client():
    os.environ["TESTING"] = "true"
    app = create_app()
    return TestClient(app)


def test_orchestrator_status_ready(client):
    """Smoke test for status ready: mock 3 healthy providers → expect ready: true."""
    with patch('app.services.provider_health_manager.ProviderHealthManager.get_health_summary', new_callable=AsyncMock) as mock_health:
        mock_health.return_value = {
            "_system": {
                "available_providers": ["openai", "anthropic", "google"],
                "total_providers": 3,
                "meets_requirements": True
            }
        }
        
        response = client.get("/api/orchestrator/status")
        assert response.status_code == 200
        data = response.json()
        assert data["service_available"] is True
        assert data["status"] == "healthy"

def test_orchestrator_status_not_ready_and_analyze_503(client):
    """Smoke test for status not ready: missing provider → expect 503 on analyze with full details."""
    with patch('app.services.provider_health_manager.ProviderHealthManager.get_health_summary', new_callable=AsyncMock) as mock_health:
        mock_health.return_value = {
            "_system": {
                "available_providers": ["openai", "anthropic"],
                "total_providers": 3,
                "meets_requirements": False
            }
        }
        
        # Check status endpoint
        status_response = client.get("/api/orchestrator/status")
        assert status_response.status_code == 200
        status_data = status_response.json()
        assert status_data["service_available"] is False
        assert "unavailable" in status_data["status"]

        # Check analyze endpoint
        analyze_response = client.post(
            "/api/orchestrator/analyze",
            json={"query": "test", "selected_models": ["gpt-4o", "claude-3-haiku-20240307"]},
            headers={"Authorization": "Bearer test-token"}
        )
        assert analyze_response.status_code == 503
        error_data = analyze_response.json()
        assert "detail" in error_data
        assert "error_details" in error_data
        assert error_data["error_details"]["required_providers"] == ["anthropic", "google", "openai"]
        assert error_data["error_details"]["providers_present"] == ["anthropic", "openai"]

def test_orchestrator_analyze_schema_validation(client):
    # Missing required field 'query'
    resp = client.post("/api/orchestrator/analyze", json={"analysis_type": "confidence"}, headers={"Authorization": "Bearer test-token"})
    assert resp.status_code == 422


def test_orchestrator_analyze_success_smoke(client, monkeypatch):
    # Bypass auth/db checks in test mode
    headers = {"Authorization": "Bearer test-token"}
    payload = {
        "query": "Say hi",
        "analysis_type": "confidence",
        "selected_models": ["gpt-4o", "claude-3-5-sonnet-20241022", "gemini-1.5-pro"],
        "options": {},
        "user_id": "route-test",
        "save_outputs": False,
        "include_pipeline_details": False,
        "include_initial_responses": False,
    }

    with patch('app.services.provider_health_manager.ProviderHealthManager.get_health_summary', new_callable=AsyncMock) as mock_health:
        mock_health.return_value = {
            "_system": {
                "available_providers": ["openai", "anthropic", "google"],
                "total_providers": 3,
                "meets_requirements": True
            }
        }
        
        resp = client.post("/api/orchestrator/analyze", json=payload, headers=headers)
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert isinstance(data, dict)
        assert "success" in data
        assert data["success"] is True


