import pytest
from fastapi.testclient import TestClient

from app.app import create_app


@pytest.fixture(scope="session")
def client():
    """
    Create a TestClient for the FastAPI application.
    """
    import os
    # Ensure we're in test mode
    os.environ["TESTING"] = "true"
    os.environ["JWT_SECRET_KEY"] = "test-secret-key"
    app = create_app()
    with TestClient(app) as c:
        yield c


@pytest.mark.integration
def test_health_endpoint_basic(client):
    """
    Test the /api/health endpoint returns status and correct structure.
    """
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "status" in data
    assert data["status"] == "ok"
    # Should have additional fields
    assert "timestamp" in data
    assert "environment" in data
    assert "services" in data


@pytest.mark.integration
def test_health_services_endpoint(client):
    """
    Test the /api/health/services endpoint returns correct shape.
    """
    response = client.get("/api/health/services")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    # Should have exactly this shape
    assert "status" in data
    assert "services" in data
    assert isinstance(data["services"], dict)
    # Services should include at minimum database and cache
    services = data["services"]
    assert "database" in services or "db" in services
    assert "cache" in services


@pytest.mark.integration
def test_health_endpoints_not_caught_by_spa(client):
    """
    Test that health endpoints are registered before SPA catchall.
    """
    # These should return JSON, not HTML index page
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.headers.get("content-type", "").startswith("application/json")
    
    response = client.get("/api/health/services")
    assert response.status_code == 200
    assert response.headers.get("content-type", "").startswith("application/json")
    
    # This non-existent API route should return JSON error, not HTML
    response = client.get("/api/nonexistent")
    assert response.status_code == 404
    # Should get JSON error, not HTML
    assert "text/html" not in response.headers.get("content-type", "")
