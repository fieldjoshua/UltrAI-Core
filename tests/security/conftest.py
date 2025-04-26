import pytest
from fastapi.testclient import TestClient
from mock_app import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI application."""
    return TestClient(app)
