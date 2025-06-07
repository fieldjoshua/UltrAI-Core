import pytest
from fastapi.testclient import TestClient

from app.app import create_app


@pytest.fixture(scope="session")
def client():
    """
    Create a TestClient for the FastAPI application.
    """
    app = create_app()
    with TestClient(app) as c:
        yield c


@pytest.mark.integration
def test_health_endpoint_basic(client):
    """
    Test the /health endpoint returns status and correct structure.
    """
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "status" in data


@pytest.mark.integration
def test_health_services_endpoint(client):
    """
    Test the /health/services endpoint returns detailed service info.
    """
    response = client.get("/health/services")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    # Ensure detailed keys are present
    assert data.get("services") is not None
