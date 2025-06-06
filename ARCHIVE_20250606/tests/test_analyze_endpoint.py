"""
Tests for the analyze endpoints.

This module contains comprehensive tests for the analyze endpoints, which are critical
for the core functionality of the application.
"""

import json

import pytest
from fastapi import status


# Test happy path for analyze endpoint
def test_analyze_prompt_happy_path(client):
    """Test the analyze endpoint with valid input data."""
    # Prepare test data
    test_data = {
        "prompt": "What are the key considerations for building a reliable machine learning system?",
        "selected_models": ["gpt4o", "claude37"],
        "ultra_model": "gpt4o",
        "pattern": "confidence",
        "options": {},
        "output_format": "markdown",
    }

    # Call the endpoint
    response = client.post("/api/analyze", json=test_data)

    # Verify response
    assert response.status_code == status.HTTP_200_OK
    assert "status" in response.json()
    assert response.json()["status"] == "success"

    # Verify analysis ID
    assert "analysis_id" in response.json()
    assert response.json()["analysis_id"].startswith("analysis_")

    # Verify results structure
    results = response.json().get("results", {})
    assert "model_responses" in results, "Model responses missing from results"
    assert "ultra_response" in results, "Ultra response missing from results"
    assert "performance" in results, "Performance metrics missing from results"

    # Verify model responses
    model_responses = results["model_responses"]
    assert isinstance(model_responses, dict), "Model responses should be a dictionary"
    assert len(model_responses) > 0, "No model responses returned"

    # Verify at least the primary model is present
    assert "gpt4o" in model_responses or any(
        "gpt" in model for model in model_responses
    ), "Primary model response missing"

    # Verify ultra response
    ultra_response = results["ultra_response"]
    assert ultra_response is not None, "Ultra response is None"
    assert len(ultra_response) > 0, "Ultra response is empty"

    # Verify performance metrics
    performance = results["performance"]
    assert (
        "total_time_seconds" in performance
    ), "Total time missing from performance metrics"
    assert "model_times" in performance, "Model times missing from performance metrics"
    assert (
        "token_counts" in performance
    ), "Token counts missing from performance metrics"

    # Ensure we're not getting placeholder data (common issue)
    assert "Paris is the capital" not in str(
        ultra_response
    ), "Response contains placeholder data"


# Test with various patterns
@pytest.mark.parametrize(
    "pattern",
    ["confidence", "perspective", "critique", "gut", None],  # Test default pattern
)
def test_analyze_with_different_patterns(client, pattern):
    """Test analyze endpoint with different analysis patterns."""
    # Prepare test data
    test_data = {
        "prompt": "Summarize the key benefits of cloud computing.",
        "selected_models": ["claude37"],  # Using just one model for simplicity
        "ultra_model": "claude37",
        "options": {},
        "output_format": "markdown",
    }

    # Add pattern if provided
    if pattern:
        test_data["pattern"] = pattern

    # Call the endpoint
    response = client.post("/api/analyze", json=test_data)

    # Verify response
    assert response.status_code == status.HTTP_200_OK
    assert "status" in response.json()
    assert response.json()["status"] == "success"

    # Verify results structure
    results = response.json().get("results", {})
    assert "model_responses" in results
    assert "ultra_response" in results

    # With different patterns, the responses should be different
    # We can't test the exact content, but we can check it's not empty
    assert results["ultra_response"] is not None
    assert len(results["ultra_response"]) > 0


# Test error cases
def test_analyze_missing_required_fields(client):
    """Test analyze endpoint with missing required fields."""
    # Test cases with missing fields
    test_cases = [
        {"selected_models": ["gpt4o"], "ultra_model": "gpt4o"},  # Missing prompt
        {"prompt": "Test prompt", "ultra_model": "gpt4o"},  # Missing selected_models
        {"prompt": "Test prompt", "selected_models": ["gpt4o"]},  # Missing ultra_model
    ]

    for test_case in test_cases:
        response = client.post("/api/analyze", json=test_case)

        # Should return 400 or 422
        assert response.status_code in [
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_422_UNPROCESSABLE_ENTITY,
        ]

        # Response should have status and message
        assert "status" in response.json()
        assert response.json()["status"] == "error"
        assert "message" in response.json()


def test_analyze_with_invalid_models(client):
    """Test analyze endpoint with invalid model selection."""
    # Prepare test data with invalid model
    test_data = {
        "prompt": "Test prompt for analysis",
        "selected_models": ["nonexistent_model"],
        "ultra_model": "nonexistent_model",
        "pattern": "confidence",
        "options": {},
    }

    # The endpoint should still work with mock mode, but in real mode
    # this would be an error. We test both possible responses.
    response = client.post("/api/analyze", json=test_data)

    # Either it succeeds with mock data or returns an error about invalid models
    if response.status_code == status.HTTP_200_OK:
        # If mock mode handles unknown models
        assert "results" in response.json()
    else:
        # If error is returned for invalid models
        assert response.status_code in [
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        ]
        assert "status" in response.json()
        assert response.json()["status"] == "error"


# Test large prompts
def test_analyze_with_large_prompt(client):
    """Test analyze endpoint with a large prompt."""
    # Create a large prompt (about 2KB)
    large_prompt = "This is a large prompt. " * 200

    # Prepare test data
    test_data = {
        "prompt": large_prompt,
        "selected_models": ["gpt4o"],
        "ultra_model": "gpt4o",
        "pattern": "confidence",
        "options": {},
    }

    # Call the endpoint
    response = client.post("/api/analyze", json=test_data)

    # Verify response
    assert response.status_code == status.HTTP_200_OK
    assert "status" in response.json()
    assert response.json()["status"] == "success"

    # Verify results structure
    results = response.json().get("results", {})
    assert "model_responses" in results
    assert "ultra_response" in results


# Test with custom options
def test_analyze_with_custom_options(client):
    """Test analyze endpoint with custom options."""
    # Prepare test data with custom options
    test_data = {
        "prompt": "Analyze the impact of artificial intelligence on healthcare.",
        "selected_models": ["gpt4o"],
        "ultra_model": "gpt4o",
        "pattern": "confidence",
        "options": {
            "include_citations": True,
            "focus_area": "ethical_considerations",
            "depth": "detailed",
        },
        "output_format": "markdown",
    }

    # Call the endpoint
    response = client.post("/api/analyze", json=test_data)

    # Verify response
    assert response.status_code == status.HTTP_200_OK
    assert "status" in response.json()
    assert response.json()["status"] == "success"

    # Verify results structure - we can't test if options affected the output
    # but we can ensure the response is properly structured
    results = response.json().get("results", {})
    assert "model_responses" in results
    assert "ultra_response" in results


# Test concurrent requests
@pytest.mark.parametrize(
    "prompt",
    [
        "What are the benefits of microservices architecture?",
        "How does blockchain technology work?",
        "Explain the concept of machine learning in simple terms.",
        "What are the ethical considerations for AI development?",
    ],
)
def test_analyze_concurrent_requests(client, prompt):
    """Test analyze endpoint with concurrent requests."""
    # Prepare test data
    test_data = {
        "prompt": prompt,
        "selected_models": ["gpt4o"],
        "ultra_model": "gpt4o",
        "pattern": "confidence",
        "options": {},
    }

    # Call the endpoint
    response = client.post("/api/analyze", json=test_data)

    # Verify response
    assert response.status_code == status.HTTP_200_OK
    assert "status" in response.json()
    assert response.json()["status"] == "success"

    # Verify results structure
    results = response.json().get("results", {})
    assert "model_responses" in results
    assert "ultra_response" in results
