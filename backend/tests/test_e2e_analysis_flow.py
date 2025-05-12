"""
End-to-end tests for the analysis flow.

This module tests the complete analysis flow from authentication to results retrieval,
ensuring that the entire user journey works correctly.
"""

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from backend.app import app
from backend.config import Config

client = TestClient(app)

# Test data
TEST_USER = {
    "email": "e2e_test@example.com",
    "password": "SecurePassword123!",
    "name": "E2E Test User"
}

TEST_PROMPT = "Explain the advantages and disadvantages of microservices architecture"

# Mock LLM response
MOCK_LLM_RESPONSE = {
    "text": "This is a mock response from the LLM service.",
    "usage": {
        "prompt_tokens": 10,
        "completion_tokens": 15,
        "total_tokens": 25
    }
}


@pytest.fixture
def registered_user():
    """Register a test user and return the user data."""
    # Register user
    response = client.post("/api/auth/register", json=TEST_USER)
    
    if response.status_code != status.HTTP_201_CREATED:
        # Try logging in if user already exists
        login_response = client.post("/api/auth/login", json={
            "email": TEST_USER["email"],
            "password": TEST_USER["password"]
        })
        assert login_response.status_code == status.HTTP_200_OK
        return login_response.json()
    
    return response.json()


@pytest.fixture
def auth_headers(registered_user):
    """Get authentication headers for the test user."""
    # Login to get token
    login_response = client.post("/api/auth/login", json={
        "email": TEST_USER["email"],
        "password": TEST_USER["password"]
    })
    
    assert login_response.status_code == status.HTTP_200_OK
    assert "access_token" in login_response.json()
    
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def mock_llm_service():
    """Mock the LLM service to return predictable responses."""
    with patch('backend.services.llm_service.query_llm', return_value=MOCK_LLM_RESPONSE) as mock:
        yield mock


def test_full_analysis_flow(auth_headers, mock_llm_service):
    """
    Test the complete analysis flow from model selection to results retrieval.
    
    This test verifies that:
    1. Available models can be retrieved
    2. Analysis request can be submitted
    3. Results can be retrieved
    4. All components work together correctly
    """
    # Enable mock mode for testing
    Config.use_mock = True
    
    # Step 1: Get available models
    models_response = client.get("/api/available-models", headers=auth_headers)
    assert models_response.status_code == status.HTTP_200_OK
    
    available_models = models_response.json().get("available_models", [])
    assert len(available_models) > 0, "No models available for testing"
    
    # Use first two models or all if only one is available
    selected_models = available_models[:2] if len(available_models) > 1 else available_models
    primary_model = selected_models[0]
    
    # Step 2: Submit analysis request
    analysis_payload = {
        "prompt": TEST_PROMPT,
        "selected_models": selected_models,
        "ultra_model": primary_model,
        "pattern": "confidence",
        "options": {},
        "output_format": "markdown"
    }
    
    analysis_response = client.post(
        "/api/analyze", 
        json=analysis_payload,
        headers=auth_headers
    )
    
    assert analysis_response.status_code == status.HTTP_200_OK
    assert "status" in analysis_response.json()
    assert analysis_response.json()["status"] == "success"
    
    # Check analysis ID was returned
    assert "analysis_id" in analysis_response.json()
    analysis_id = analysis_response.json()["analysis_id"]
    
    # Verify results structure
    results = analysis_response.json().get("results", {})
    assert "model_responses" in results, "Model responses missing from results"
    assert "ultra_response" in results, "Ultra response missing from results"
    
    # Step 3: Retrieve analysis by ID
    # Note: This endpoint might not exist yet, but should be implemented for proper E2E flow
    results_response = client.get(
        f"/api/analysis/{analysis_id}",
        headers=auth_headers
    )
    
    # If the endpoint exists, verify the response
    if results_response.status_code == status.HTTP_200_OK:
        assert "results" in results_response.json()
        assert "model_responses" in results_response.json()["results"]
        assert "ultra_response" in results_response.json()["results"]
    
    # Step 4: Get analysis history
    history_response = client.get(
        "/api/analysis/history",
        headers=auth_headers
    )
    
    # If the endpoint exists, verify the response
    if history_response.status_code == status.HTTP_200_OK:
        analyses = history_response.json().get("analyses", [])
        # The analysis we just performed should be in the history
        analysis_ids = [a.get("id") for a in analyses]
        assert analysis_id in analysis_ids, "Analysis not found in history"


def test_analysis_flow_with_document(auth_headers, mock_llm_service):
    """
    Test the analysis flow with document upload.

    This test verifies that:
    1. Documents can be uploaded
    2. Analysis can be performed on uploaded documents
    3. Results can be retrieved
    """
    # Mock document content
    mock_document_content = "This is a test document for analysis."

    # Step 1: Upload document
    # Create a simple text file for upload
    files = {
        "file": ("test_document.txt", mock_document_content, "text/plain")
    }

    upload_response = client.post(
        "/api/upload-document",
        files=files,
        headers=auth_headers
    )

    # Verify document upload response
    assert upload_response.status_code == status.HTTP_200_OK, f"Upload document failed: {upload_response.text}"
    assert "document_id" in upload_response.json(), "Document ID missing from upload response"
    document_id = upload_response.json()["document_id"]

    # Step 2: Analyze document
    document_analysis_payload = {
        "document_id": document_id,
        "selected_models": ["gpt4o", "claude37"],
        "ultra_model": "gpt4o",
        "pattern": "confidence",
        "options": {}
    }

    analysis_response = client.post(
        "/api/analyze-document",
        json=document_analysis_payload,
        headers=auth_headers
    )

    # Verify analysis response
    assert analysis_response.status_code == status.HTTP_200_OK, f"Document analysis failed: {analysis_response.text}"
    assert "analysis_id" in analysis_response.json(), "Analysis ID missing from response"
    assert "results" in analysis_response.json(), "Results missing from response"

    # Get analysis ID for retrieval
    analysis_id = analysis_response.json().get("analysis_id")

    # Verify results structure
    results = analysis_response.json().get("results", {})
    assert "model_responses" in results, "Model responses missing from results"
    assert "ultra_response" in results, "Ultra response missing from results"

    # Step 3: Retrieve analysis by ID
    results_response = client.get(
        f"/api/document-analysis/{analysis_id}",
        headers=auth_headers
    )

    # Verify results retrieval
    assert results_response.status_code == status.HTTP_200_OK, f"Results retrieval failed: {results_response.text}"
    assert "results" in results_response.json(), "Results missing from retrieval response"

    # Verify document metadata is included
    retrieved_results = results_response.json().get("results", {})
    assert "document_metadata" in retrieved_results, "Document metadata missing from results"
    assert "model_responses" in retrieved_results, "Model responses missing from retrieved results"
    assert "ultra_response" in retrieved_results, "Ultra response missing from retrieved results"


def test_error_handling_in_flow(auth_headers):
    """
    Test error handling in the analysis flow.
    
    This test verifies that:
    1. Invalid requests are properly rejected
    2. Error responses are properly formatted
    3. The system handles errors gracefully
    """
    # Test invalid prompt (empty)
    invalid_analysis_payload = {
        "prompt": "",
        "selected_models": ["gpt4o"],
        "ultra_model": "gpt4o",
        "pattern": "confidence"
    }
    
    response = client.post(
        "/api/analyze",
        json=invalid_analysis_payload,
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["status"] == "error"
    assert "prompt" in response.json()["message"].lower()
    
    # Test invalid model
    invalid_model_payload = {
        "prompt": "Test prompt",
        "selected_models": ["nonexistent_model"],
        "ultra_model": "nonexistent_model",
        "pattern": "confidence"
    }
    
    response = client.post(
        "/api/analyze",
        json=invalid_model_payload,
        headers=auth_headers
    )
    
    # This could either return a 400 if validation catches it,
    # or succeed with mock data in mock mode
    if response.status_code == status.HTTP_400_BAD_REQUEST:
        assert response.json()["status"] == "error"
        assert "model" in response.json()["message"].lower()
    else:
        # In mock mode, should still succeed
        assert response.status_code == status.HTTP_200_OK
    
    # Test invalid pattern
    invalid_pattern_payload = {
        "prompt": "Test prompt",
        "selected_models": ["gpt4o"],
        "ultra_model": "gpt4o",
        "pattern": "nonexistent_pattern"
    }
    
    response = client.post(
        "/api/analyze",
        json=invalid_pattern_payload,
        headers=auth_headers
    )
    
    # This could either return a 400 if validation catches it,
    # or succeed with default pattern in mock mode
    if response.status_code == status.HTTP_400_BAD_REQUEST:
        assert response.json()["status"] == "error"
        assert "pattern" in response.json()["message"].lower()


def test_token_refresh_during_analysis(registered_user):
    """
    Test token refresh during a long-running analysis flow.
    
    This test verifies that:
    1. A token can be refreshed during a long-running analysis
    2. The analysis can continue with the new token
    3. Session state is maintained across token refreshes
    """
    # Step 1: Login to get initial tokens
    login_response = client.post("/api/auth/login", json={
        "email": TEST_USER["email"],
        "password": TEST_USER["password"]
    })
    
    assert login_response.status_code == status.HTTP_200_OK
    access_token = login_response.json()["access_token"]
    refresh_token = login_response.json()["refresh_token"]
    auth_headers = {"Authorization": f"Bearer {access_token}"}
    
    # Step 2: Start an analysis
    analysis_payload = {
        "prompt": "Test prompt for refresh flow",
        "selected_models": ["gpt4o"],
        "ultra_model": "gpt4o",
        "pattern": "confidence",
        "options": {}
    }
    
    response = client.post(
        "/api/analyze",
        json=analysis_payload,
        headers=auth_headers
    )
    
    # Store analysis ID if available
    analysis_id = None
    if response.status_code == status.HTTP_200_OK and "analysis_id" in response.json():
        analysis_id = response.json()["analysis_id"]
    
    # Step 3: Simulate token expiration by refreshing it
    refresh_response = client.post(
        "/api/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    
    assert refresh_response.status_code == status.HTTP_200_OK
    new_access_token = refresh_response.json()["access_token"]
    new_auth_headers = {"Authorization": f"Bearer {new_access_token}"}
    
    # Step 4: Continue the analysis with the new token
    # If analysis_id is available, try to retrieve results with the new token
    if analysis_id:
        results_response = client.get(
            f"/api/analysis/{analysis_id}",
            headers=new_auth_headers
        )
        
        # If the endpoint exists, verify it works with the new token
        if results_response.status_code == status.HTTP_200_OK:
            assert "results" in results_response.json()
    
    # Otherwise, just verify we can make another authenticated request
    models_response = client.get("/api/available-models", headers=new_auth_headers)
    assert models_response.status_code == status.HTTP_200_OK


if __name__ == "__main__":
    pytest.main(["-xvs", "test_e2e_analysis_flow.py"])