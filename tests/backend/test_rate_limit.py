"""
Tests for rate limiting middleware and service.

This module tests the functionality of the rate limiting middleware and service.
"""

import time
import pytest
from fastapi import FastAPI, Request, Response, Depends
from fastapi.testclient import TestClient

from backend.services.rate_limit_service import RateLimitService
from backend.utils.rate_limit_middleware import RateLimitMiddleware


@pytest.fixture
def rate_limit_service():
    """Create a RateLimitService instance for testing"""
    return RateLimitService()


@pytest.fixture
def app_with_rate_limit():
    """Create a FastAPI application with rate limiting middleware"""
    app = FastAPI()

    # Add rate limiting middleware
    app.add_middleware(RateLimitMiddleware, exclude_paths=["/excluded"])

    @app.get("/test")
    def test_endpoint():
        return {"message": "test"}

    @app.get("/excluded")
    def excluded_endpoint():
        return {"message": "excluded from rate limiting"}

    return app


def test_rate_limit_service_initialization(rate_limit_service):
    """Test rate limit service initialization"""
    assert rate_limit_service is not None
    assert hasattr(rate_limit_service, "in_memory_store")
    assert "ip" in rate_limit_service.in_memory_store
    assert "user" in rate_limit_service.in_memory_store


def test_rate_limit_service_get_rate_limit(rate_limit_service):
    """Test getting rate limit based on user tier"""
    # Anonymous rate limit
    assert rate_limit_service.get_rate_limit() == 60

    # Test with mock user objects
    class MockUser:
        def __init__(self, tier):
            self.subscription_tier = tier

    # Different subscription tiers
    assert rate_limit_service.get_rate_limit(MockUser("free")) == 100
    assert rate_limit_service.get_rate_limit(MockUser("basic")) == 300
    assert rate_limit_service.get_rate_limit(MockUser("premium")) == 600
    assert rate_limit_service.get_rate_limit(MockUser("enterprise")) == 1200

    # Unknown tier should fall back to free
    assert rate_limit_service.get_rate_limit(MockUser("unknown")) == 100


def test_internal_service_bypass(rate_limit_service):
    """Test internal service rate limit bypass"""
    # Register an internal service
    token = rate_limit_service.register_internal_service("test-service", "secret123")

    # Verify token was created
    assert token is not None
    assert len(token) > 0

    # Check that the service is recognized
    assert rate_limit_service.is_internal_service(token) is True

    # Check rate limit with internal token (should bypass)
    is_limited, info = rate_limit_service.check_rate_limit(
        "127.0.0.1", internal_token=token
    )
    assert is_limited is False

    # Unregister the service
    rate_limit_service.unregister_internal_service(token)

    # Verify it's no longer recognized
    assert rate_limit_service.is_internal_service(token) is False


def test_middleware_skips_excluded_paths(app_with_rate_limit):
    """Test that middleware skips excluded paths"""
    client = TestClient(app_with_rate_limit)

    # Request to excluded endpoint should not have rate limit headers
    response = client.get("/excluded")
    assert response.status_code == 200
    assert "X-RateLimit-Limit" not in response.headers

    # Request to normal endpoint should have rate limit headers
    response = client.get("/test")
    assert response.status_code == 200
    assert "X-RateLimit-Limit" in response.headers
    assert "X-RateLimit-Remaining" in response.headers
    assert "X-RateLimit-Reset" in response.headers


def test_middleware_adds_rate_limit_headers(app_with_rate_limit):
    """Test that middleware adds rate limit headers to responses"""
    client = TestClient(app_with_rate_limit)

    # Make a request
    response = client.get("/test")
    assert response.status_code == 200

    # Check rate limit headers
    assert "X-RateLimit-Limit" in response.headers
    assert "X-RateLimit-Remaining" in response.headers
    assert "X-RateLimit-Reset" in response.headers

    # Values should be valid
    assert int(response.headers["X-RateLimit-Limit"]) > 0
    assert int(response.headers["X-RateLimit-Remaining"]) >= 0
    assert int(response.headers["X-RateLimit-Reset"]) > 0


def test_rate_limit_enforcement(rate_limit_service):
    """Test rate limit enforcement"""
    # Set a very low limit for testing
    original_limit = rate_limit_service.get_rate_limit(None)

    # Mock the get_rate_limit method to return a very low limit
    original_get_rate_limit = rate_limit_service.get_rate_limit
    rate_limit_service.get_rate_limit = lambda user: 5

    try:
        # Make multiple requests
        ip = "127.0.0.1"
        for i in range(5):
            is_limited, info = rate_limit_service.check_rate_limit(ip)
            assert is_limited is False
            assert info["remaining"] >= 0

        # Next request should hit the limit
        is_limited, info = rate_limit_service.check_rate_limit(ip)
        assert is_limited is True
        assert info["remaining"] == 0

    finally:
        # Restore original method
        rate_limit_service.get_rate_limit = original_get_rate_limit

        # Clear rate limits
        rate_limit_service.clear_rate_limits()


def test_user_based_rate_limiting(rate_limit_service):
    """Test user-based rate limiting"""
    # Test with different users
    user1 = "user1"
    user2 = "user2"

    # Mock get_rate_limit to return constant value
    original_get_rate_limit = rate_limit_service.get_rate_limit
    rate_limit_service.get_rate_limit = lambda user: 10

    try:
        # User 1 makes requests
        for i in range(5):
            is_limited, info = rate_limit_service.check_rate_limit(
                "127.0.0.1", user_id=user1
            )
            assert is_limited is False

        # User 2 should not be affected by User 1's rate limit
        is_limited, info = rate_limit_service.check_rate_limit(
            "127.0.0.1", user_id=user2
        )
        assert is_limited is False
        assert info["remaining"] > 0

        # Check usage report
        report = rate_limit_service.get_usage_report(user_id=user1)
        assert report is not None
        assert isinstance(report, dict)

    finally:
        # Restore original method
        rate_limit_service.get_rate_limit = original_get_rate_limit

        # Clear rate limits
        rate_limit_service.clear_rate_limits()
