"""
Unit tests for rate limiting middleware.

This module contains tests for the rate limiting functionality.
"""

import time
from unittest.mock import Mock

import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from backend.utils.rate_limit_middleware import (
    check_rate_limit,
    get_client_identifier,
    get_user_identifier,
    rate_limit_middleware,
    RATE_LIMIT_MAX_REQUESTS,
    RATE_LIMIT_WINDOW,
)

# Create test app
app = FastAPI()


@app.get("/test")
async def test_endpoint(request: Request):
    """Test endpoint for rate limiting"""
    return {"status": "success"}


# Add rate limiting middleware
app.middleware("http")(rate_limit_middleware)

# Create test client
client = TestClient(app)


def test_get_client_identifier():
    """Test getting client identifier"""
    # Test with client
    request = Mock()
    request.client = Mock()
    request.client.host = "127.0.0.1"
    pytest.assume(get_client_identifier(request) == "127.0.0.1")

    # Test without client
    request.client = None
    pytest.assume(get_client_identifier(request) == "default")


def test_get_user_identifier():
    """Test getting user identifier"""
    # Test with valid token
    request = Mock()
    request.headers = {"Authorization": "Bearer test_token"}
    pytest.assume(get_user_identifier(request) == "test_token")

    # Test with invalid scheme
    request.headers = {"Authorization": "Basic test_token"}
    pytest.assume(get_user_identifier(request) is None)

    # Test without header
    request.headers = {}
    pytest.assume(get_user_identifier(request) is None)

    # Test with malformed header
    request.headers = {"Authorization": "Bearer"}
    pytest.assume(get_user_identifier(request) is None)


def test_check_rate_limit():
    """Test rate limit checking"""
    request = Mock()
    request.client = Mock()
    request.client.host = "127.0.0.1"

    # Test first request
    is_rate_limited, rate_limit_info = check_rate_limit(request)
    pytest.assume(not is_rate_limited)
    pytest.assume(rate_limit_info["limit"] == RATE_LIMIT_MAX_REQUESTS)
    pytest.assume(rate_limit_info["remaining"] == RATE_LIMIT_MAX_REQUESTS - 1)

    # Test multiple requests
    for _ in range(RATE_LIMIT_MAX_REQUESTS):
        is_rate_limited, rate_limit_info = check_rate_limit(request)

    # Should be rate limited
    pytest.assume(is_rate_limited)
    pytest.assume(rate_limit_info["limit"] == RATE_LIMIT_MAX_REQUESTS)
    pytest.assume(rate_limit_info["remaining"] == 0)


def test_rate_limit_middleware():
    """Test rate limiting middleware"""
    # Test successful request
    response = client.get("/test")
    pytest.assume(response.status_code == 200)
    pytest.assume(response.headers["X-RateLimit-Limit"] == str(RATE_LIMIT_MAX_REQUESTS))
    pytest.assume(
        response.headers["X-RateLimit-Remaining"] == str(RATE_LIMIT_MAX_REQUESTS - 1)
    )
    pytest.assume("X-RateLimit-Reset" in response.headers)

    # Test rate limited request
    for _ in range(RATE_LIMIT_MAX_REQUESTS):
        response = client.get("/test")

    pytest.assume(response.status_code == 429)
    pytest.assume(response.headers["X-RateLimit-Limit"] == str(RATE_LIMIT_MAX_REQUESTS))
    pytest.assume(response.headers["X-RateLimit-Remaining"] == "0")
    pytest.assume("X-RateLimit-Reset" in response.headers)


def test_rate_limit_window():
    """Test rate limit window expiration"""
    request = Mock()
    request.client = Mock()
    request.client.host = "127.0.0.1"

    # Make requests up to limit
    for _ in range(RATE_LIMIT_MAX_REQUESTS):
        is_rate_limited, _ = check_rate_limit(request)

    # Should be rate limited
    pytest.assume(is_rate_limited)

    # Wait for window to expire
    time.sleep(RATE_LIMIT_WINDOW + 1)

    # Should not be rate limited
    is_rate_limited, _ = check_rate_limit(request)
    pytest.assume(not is_rate_limited)
