"""
Tests for global error handling system.

This module tests the functionality of the global error handling system.
"""

import pytest
from fastapi import FastAPI, status, HTTPException
from fastapi.testclient import TestClient

from backend.utils.global_error_handler import (
    setup_error_handling,
    UltraBaseException,
    ErrorCode,
    CircuitBreaker,
    with_retry,
)


@pytest.fixture
def app_with_error_handling():
    """Create a FastAPI application with global error handling"""
    app = FastAPI()
    setup_error_handling(app, include_debug_details=True)

    # Regular endpoint
    @app.get("/test")
    def test_endpoint():
        return {"message": "test"}

    # Endpoint that raises a regular exception
    @app.get("/error/standard")
    def standard_error():
        raise ValueError("Standard error message")

    # Endpoint that raises an HTTP exception
    @app.get("/error/http")
    def http_error():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Bad request"
        )

    # Endpoint that raises a custom UltraBaseException
    @app.get("/error/custom")
    def custom_error():
        raise UltraBaseException(
            message="Custom error message",
            code=ErrorCode.INVALID_INPUT,
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    # Endpoint with a breaking service
    broken_service = CircuitBreaker(
        failure_threshold=2,
        reset_timeout=1,
        half_open_success_threshold=1,
    )

    @app.get("/error/circuit-breaker")
    @broken_service
    async def circuit_breaker_test():
        # Always fail to trigger circuit breaker
        raise ConnectionError("Service unavailable")

    # Endpoint with retry mechanism
    counter = {"value": 0}

    @app.get("/test/retry")
    @with_retry(max_retries=3, initial_backoff=0.01, max_backoff=0.1)
    async def retry_test():
        counter["value"] += 1
        # Fail first two times, succeed on third
        if counter["value"] < 3:
            raise ConnectionError("Temporary connection error")
        return {"message": "success", "attempts": counter["value"]}

    return app


def test_successful_request(app_with_error_handling):
    """Test that successful requests work normally"""
    client = TestClient(app_with_error_handling)
    response = client.get("/test")

    assert response.status_code == 200
    assert response.json() == {"message": "test"}
    assert "X-Correlation-ID" in response.headers


def test_standard_error(app_with_error_handling):
    """Test handling of standard Python exceptions"""
    client = TestClient(app_with_error_handling)
    response = client.get("/error/standard")

    assert response.status_code == 400  # Mapped from ValueError
    assert response.json()["status"] == "error"
    assert response.json()["code"] == ErrorCode.INVALID_INPUT
    assert "Standard error message" in response.json()["message"]
    assert "X-Correlation-ID" in response.headers


def test_http_error(app_with_error_handling):
    """Test handling of HTTP exceptions"""
    client = TestClient(app_with_error_handling)
    response = client.get("/error/http")

    assert response.status_code == 400
    assert response.json()["status"] == "error"
    assert response.json()["code"] == "http_400"
    assert response.json()["message"] == "Bad request"
    assert "X-Correlation-ID" in response.headers


def test_custom_error(app_with_error_handling):
    """Test handling of custom UltraBaseException"""
    client = TestClient(app_with_error_handling)
    response = client.get("/error/custom")

    assert response.status_code == 400
    assert response.json()["status"] == "error"
    assert response.json()["code"] == ErrorCode.INVALID_INPUT
    assert response.json()["message"] == "Custom error message"
    assert "X-Correlation-ID" in response.headers


def test_circuit_breaker(app_with_error_handling):
    """Test circuit breaker functionality"""
    client = TestClient(app_with_error_handling)

    # First request - fails but circuit still closed
    response1 = client.get("/error/circuit-breaker")
    assert response1.status_code == 502  # Bad Gateway for ConnectionError

    # Second request - fails and circuit opens
    response2 = client.get("/error/circuit-breaker")
    assert response2.status_code == 502  # Still a ConnectionError

    # Third request - circuit is open, fails fast
    response3 = client.get("/error/circuit-breaker")
    assert response3.status_code == 503  # Service Unavailable for circuit open
    assert response3.json()["code"] == ErrorCode.CIRCUIT_OPEN

    # Wait for circuit to go half-open
    import time

    time.sleep(1.1)

    # Fourth request - circuit is half-open, allows one request
    response4 = client.get("/error/circuit-breaker")
    assert response4.status_code == 502  # ConnectionError again

    # Fifth request - circuit is open again
    response5 = client.get("/error/circuit-breaker")
    assert response5.status_code == 503  # Service Unavailable
    assert response5.json()["code"] == ErrorCode.CIRCUIT_OPEN


def test_retry_mechanism(app_with_error_handling):
    """Test retry mechanism functionality"""
    client = TestClient(app_with_error_handling)

    # This call should retry twice and succeed on the third attempt
    response = client.get("/test/retry")

    assert response.status_code == 200
    assert response.json()["message"] == "success"
    assert response.json()["attempts"] == 3
