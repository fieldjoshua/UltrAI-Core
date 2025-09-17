"""
This file contains shared fixtures for the pytest test suite.

Fixtures defined here are automatically available to all tests in this directory
and its subdirectories without needing to be imported.
"""

import os
import pytest
from fastapi.testclient import TestClient
from app.app import create_app

@pytest.fixture(scope="session")
def client():
    """
    A TestClient instance for making requests to the FastAPI application.
    This fixture has a 'session' scope, meaning it is created once per test session.
    """
    os.environ["TESTING"] = "true"
    app = create_app()
    with TestClient(app) as test_client:
        yield test_client