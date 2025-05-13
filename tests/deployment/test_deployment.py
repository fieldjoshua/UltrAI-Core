"""
Deployment verification tests for the Ultra MVP.

These tests are run after deployment to verify that all critical systems
are functioning correctly. They test connectivity, authentication, and core
functionality without modifying any data.
"""

import os
import time
import pytest
import requests
from urllib.parse import urljoin

# Configuration
BASE_URL = os.environ.get("TEST_API_URL", "http://localhost:8000")
AUTH_ENABLED = os.environ.get("ENABLE_AUTH", "false").lower() in ("true", "1", "yes")
MODEL_RUNNER_ENABLED = os.environ.get("ENABLE_MODEL_RUNNER", "false").lower() in ("true", "1", "yes")
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds


# Test helper functions
def api_request(method, endpoint, **kwargs):
    """Make a request to the API with retry logic."""
    url = urljoin(BASE_URL, endpoint)

    for attempt in range(MAX_RETRIES):
        try:
            response = method(url, **kwargs)
            return response
        except requests.RequestException as e:
            if attempt == MAX_RETRIES - 1:
                raise
            print(f"Request failed, retrying in {RETRY_DELAY}s: {e}")
            time.sleep(RETRY_DELAY)


# Core system tests
def test_health_endpoint():
    """Verify that the health endpoint is accessible and reports healthy status."""
    response = api_request(requests.get, "/health")

    assert response.status_code == 200, f"Health endpoint failed with status {response.status_code}"

    data = response.json()
    assert "status" in data, "Health response missing 'status' field"
    assert data["status"] in ["ok", "degraded"], f"Health status is '{data['status']}', expected 'ok' or 'degraded'"

    # Print reason if degraded
    if data["status"] == "degraded" and "degraded_services" in data:
        print(f"Health status is 'degraded' due to services: {data['degraded_services']}")


def test_database_connectivity():
    """Verify database connectivity."""
    response = api_request(requests.get, "/health/database")

    assert response.status_code == 200, f"Database health check failed with status {response.status_code}"

    data = response.json()
    assert data["status"] == "healthy", f"Database is not healthy: {data.get('message', 'Unknown error')}"


def test_redis_connectivity():
    """Verify Redis connectivity if cache is enabled."""
    if os.environ.get("ENABLE_CACHE", "true").lower() in ("true", "1", "yes"):
        response = api_request(requests.get, "/health/cache")

        assert response.status_code == 200, f"Cache health check failed with status {response.status_code}"

        data = response.json()
        assert data["status"] == "healthy", f"Redis cache is not healthy: {data.get('message', 'Unknown error')}"


def test_llm_providers():
    """Verify that at least one LLM provider is available."""
    # Skip if in mock mode
    if os.environ.get("USE_MOCK", "false").lower() in ("true", "1", "yes"):
        pytest.skip("Skipping LLM provider test in mock mode")

    response = api_request(requests.get, "/health/llm/providers")

    assert response.status_code == 200, f"LLM providers health check failed with status {response.status_code}"

    data = response.json()

    if os.environ.get("USE_MOCK", "false").lower() in ("true", "1", "yes"):
        assert data["mock_mode"] is True, "System should be in mock mode"
    else:
        # In real mode, at least one provider should be available
        assert data["available_count"] > 0, "No LLM providers are available"


# API endpoint tests
def test_api_models_endpoint():
    """Verify that the models API endpoint is accessible."""
    response = api_request(requests.get, "/api/models")

    assert response.status_code == 200, f"Models API endpoint failed with status {response.status_code}"

    data = response.json()
    assert isinstance(data, list), "Models API should return a list"
    assert len(data) > 0, "No models returned from the API"


def test_api_analysis_patterns_endpoint():
    """Verify that the analysis patterns API endpoint is accessible."""
    response = api_request(requests.get, "/api/analysis-patterns")

    assert response.status_code == 200, f"Analysis patterns API endpoint failed with status {response.status_code}"

    data = response.json()
    assert isinstance(data, list), "Analysis patterns API should return a list"
    assert len(data) > 0, "No analysis patterns returned from the API"


# Authentication tests (if enabled)
@pytest.mark.skipif(not AUTH_ENABLED, reason="Auth not enabled")
def test_auth_endpoints():
    """Verify that auth endpoints are accessible when auth is enabled."""
    # Test login endpoint
    response = api_request(requests.post, "/api/auth/login",
                           json={"username": "test", "password": "invalid"})

    # We expect a 401 for invalid credentials, but the endpoint should be accessible
    assert response.status_code in [401, 422], f"Login endpoint failed with unexpected status {response.status_code}"


# Docker Model Runner tests (if enabled)
@pytest.mark.skipif(not MODEL_RUNNER_ENABLED, reason="Model Runner not enabled")
def test_model_runner_connectivity():
    """Verify that Docker Model Runner is accessible when enabled."""
    response = api_request(requests.get, "/health/llm/providers")

    assert response.status_code == 200, f"LLM providers health check failed with status {response.status_code}"

    data = response.json()
    assert "providers" in data, "Missing providers in response"
    assert "model_runner" in data["providers"], "Model Runner provider not found"
    assert data["providers"]["model_runner"]["status"] == "healthy", "Model Runner is not healthy"


# Simple smoke test for a full request flow
def test_simple_request_flow():
    """Test a complete request flow with a simple prompt."""
    # Skip detailed verification in mock mode
    is_mock = os.environ.get("USE_MOCK", "false").lower() in ("true", "1", "yes")

    # Simple prompt for testing
    prompt_data = {
        "prompt": "Hello, this is a test prompt. Please respond with a short message.",
        "max_tokens": 20
    }

    response = api_request(requests.post, "/api/llm/completion", json=prompt_data)

    assert response.status_code == 200, f"LLM completion request failed with status {response.status_code}"

    data = response.json()
    assert "text" in data, "Response missing 'text' field"
    assert isinstance(data["text"], str), "Response 'text' should be a string"

    if not is_mock:
        # In real mode, verify that the response has content
        assert len(data["text"]) > 0, "Empty response from LLM"

    # Print a sample of the response for verification
    print(f"LLM response sample: {data['text'][:50]}...")


# Performance/load tests - optional
@pytest.mark.skip(reason="Skipping performance tests in basic deployment verification")
def test_api_performance():
    """Optional performance test for API endpoints."""
    start_time = time.time()
    api_request(requests.get, "/health")
    response_time = time.time() - start_time

    assert response_time < 1.0, f"Health endpoint response time too slow: {response_time:.2f}s"

