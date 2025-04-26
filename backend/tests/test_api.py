import json
import os

import pytest
from fastapi import status, HTTPException

from backend.core.api import APIRouter, APIResponse


# Test basic API health check
def test_health_check(client):
    """Test the health check endpoint returns a 200 OK response."""
    response = client.get("/api/health")
    assert response.status_code == status.HTTP_200_OK
    assert "status" in response.json()
    assert response.json()["status"] == "ok"


# Test document upload and analysis
def test_document_upload(client, test_document_file):
    """Test the document upload endpoint works correctly."""
    with open(test_document_file, "rb") as f:
        response = client.post(
            "/api/upload-files",
            files={"files": (os.path.basename(test_document_file), f, "text/plain")},
        )

    assert response.status_code == status.HTTP_200_OK
    assert "documents" in response.json()
    assert len(response.json()["documents"]) > 0


# Test analyze endpoint
def test_analyze_prompt(client):
    """Test the analyze prompt endpoint works correctly."""
    test_data = {
        "prompt": "Test prompt for analysis",
        "selectedModels": ["mock_model_1", "mock_model_2"],
        "ultraModel": "mock_ultra",
        "pattern": "Confidence Analysis",
        "options": {},
    }

    response = client.post("/api/analyze", json=test_data)

    assert response.status_code == status.HTTP_200_OK
    assert "status" in response.json()

    # Check if we're in mock mode, then verify the mock response structure
    results = response.json().get("results", {})
    assert isinstance(results, dict)


# Test error handling
def test_error_handling(client):
    """Test that API error responses are properly formatted."""
    # Test with invalid JSON body
    response = client.post(
        "/api/analyze",
        data="invalid json data",
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # Ensure the error response follows the standard format
    assert "detail" in response.json()

    # Test with missing required fields
    response = client.post(
        "/api/analyze", json={"prompt": "Test prompt"}  # Missing required fields
    )

    assert response.status_code in [
        status.HTTP_422_UNPROCESSABLE_ENTITY,
        status.HTTP_400_BAD_REQUEST,
    ]

    # Check for Sentry test endpoint
    response = client.get("/api/sentry-debug", allow_redirects=False)

    # This should raise an error internally but return 500
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


# Test environment-specific configurations
def test_environment_config(client, mock_environment):
    """Test that environment-specific configurations are loaded correctly."""

    # This test checks if the application properly uses environment variables
    # In a real test, you'd want to check environment-specific behavior

    # For example, checking CORS configuration based on environment
    response = client.options("/api/analyze")
    assert response.status_code == status.HTTP_200_OK

    # Check that Access-Control-Allow-Origin is properly configured
    assert "Access-Control-Allow-Origin" in response.headers


def test_api_response_initialization():
    """Test API response initialization."""
    response = APIResponse(status="success", message="Test message")
    assert response.status == "success"
    assert response.message == "Test message"
    assert response.data is None


def test_api_response_with_data():
    """Test API response with data."""
    data = {"key": "value"}
    response = APIResponse(status="success", message="Test message", data=data)
    assert response.data == data


def test_api_router_initialization(api_router):
    """Test API router initialization."""
    assert api_router.app is not None
    assert api_router._oauth2_scheme is not None


def test_api_router_add_route_get(api_router):
    """Test adding a GET route."""

    async def test_handler():
        return {"message": "test"}

    api_router.add_route("/test", "get", test_handler)
    assert api_router.app.routes[-1].path == "/test"
    assert api_router.app.routes[-1].methods == {"GET"}


def test_api_router_add_route_post(api_router):
    """Test adding a POST route."""

    async def test_handler():
        return {"message": "test"}

    api_router.add_route("/test", "post", test_handler)
    assert api_router.app.routes[-1].path == "/test"
    assert api_router.app.routes[-1].methods == {"POST"}


def test_api_router_add_route_invalid_method(api_router):
    """Test adding a route with an invalid method."""

    async def test_handler():
        return {"message": "test"}

    with pytest.raises(ValueError, match="Unsupported HTTP method: invalid"):
        api_router.add_route("/test", "invalid", test_handler)


def test_api_router_create_response(api_router):
    """Test creating a standardized API response."""
    response = api_router.create_response("success", "Test message")
    assert isinstance(response, APIResponse)
    assert response.status == "success"
    assert response.message == "Test message"


def test_api_router_create_response_with_data(api_router):
    """Test creating a standardized API response with data."""
    data = {"key": "value"}
    response = api_router.create_response("success", "Test message", data)
    assert response.data == data


def test_api_router_handle_http_error(api_router):
    """Test handling an HTTP error."""
    error = HTTPException(status_code=404, detail="Not found")
    response = api_router.handle_error(error)
    assert response.status == "error"
    assert response.message == "Not found"
    assert response.data["code"] == 404


def test_api_router_handle_generic_error(api_router):
    """Test handling a generic error."""
    error = ValueError("Test error")
    response = api_router.handle_error(error)
    assert response.status == "error"
    assert response.message == "Test error"
    assert response.data["code"] == 500
