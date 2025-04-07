import pytest
import json
import os
from fastapi import status

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
            files={"files": (os.path.basename(test_document_file), f, "text/plain")}
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
        "options": {}
    }
    
    response = client.post(
        "/api/analyze",
        json=test_data
    )
    
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
        headers={"Content-Type": "application/json"}
    )
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    # Ensure the error response follows the standard format
    assert "detail" in response.json()
    
    # Test with missing required fields
    response = client.post(
        "/api/analyze",
        json={"prompt": "Test prompt"}  # Missing required fields
    )
    
    assert response.status_code in [
        status.HTTP_422_UNPROCESSABLE_ENTITY, 
        status.HTTP_400_BAD_REQUEST
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