"""
Test auth and rate limiting for P1 implementation.

This tests:
1. ENABLE_AUTH=true protects admin and debug routes
2. Per-user rate limiting works correctly
3. API key rate limiting works correctly
"""

import asyncio
import os
from unittest.mock import Mock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx import AsyncClient

from app.app import create_app
from app.config import Config
from app.database.models.user import SubscriptionTier, User
from app.services.auth_service import auth_service
from app.services.rate_limit_service import rate_limit_service

# Set test environment variables
os.environ["TESTING"] = "true"
os.environ["JWT_SECRET_KEY"] = "test-secret-key"


@pytest.fixture
def mock_user():
    """Create a mock user for testing"""
    user = Mock(spec=User)
    user.id = 1
    user.email = "test@example.com"
    user.subscription_tier = SubscriptionTier.BASIC
    return user


@pytest.fixture
def test_app():
    """Create test application with auth enabled"""
    # Force auth and rate limiting to be enabled
    Config.ENABLE_AUTH = True
    Config.ENABLE_RATE_LIMIT = True
    # Set test tier for consistent testing
    os.environ["TEST_RATE_LIMIT_TIER"] = "BASIC"
    
    app = create_app()
    return app


@pytest.fixture
def client(test_app):
    """Create test client"""
    return TestClient(test_app)


@pytest.fixture
async def async_client(test_app):
    """Create async test client"""
    async with AsyncClient(app=test_app, base_url="http://test") as ac:
        yield ac


class TestAuthMiddleware:
    """Test authentication middleware"""

    def test_public_endpoints_no_auth(self, client):
        """Test that public endpoints don't require authentication"""
        # Health check should work without auth
        response = client.get("/api/health")
        assert response.status_code == 200
        
        # Auth endpoints should work without auth
        response = client.post("/api/auth/login", json={"email": "test", "password": "test"})
        # Will fail due to invalid credentials, but shouldn't be 401 unauthorized
        assert response.status_code != 401

    def test_admin_endpoints_require_auth(self, client):
        """Test that admin endpoints require authentication"""
        # Without auth header, should get 401
        response = client.get("/api/admin/users")
        assert response.status_code == 401
        assert response.json()["code"] == "authentication_required"

    def test_debug_endpoints_require_auth(self, client):
        """Test that debug endpoints require authentication"""
        # Without auth header, should get 401
        response = client.get("/api/debug/environment-variables")
        assert response.status_code == 401
        assert response.json()["code"] == "authentication_required"

    @patch.object(auth_service, 'get_user')
    @patch('app.middleware.combined_auth_middleware.decode_token')
    @patch('app.middleware.combined_auth_middleware.is_token_expired')
    def test_valid_jwt_token_allows_access(self, mock_expired, mock_decode, mock_get_user, client, mock_user):
        """Test that valid JWT token allows access to protected endpoints"""
        # Mock token validation
        mock_expired.return_value = False
        mock_decode.return_value = {"sub": "1", "type": "access"}
        mock_get_user.return_value = mock_user
        
        # Request with valid token should succeed
        headers = {"Authorization": "Bearer valid-token"}
        response = client.get("/api/admin/test", headers=headers)
        # Will get 404 since route doesn't exist, but not 401
        assert response.status_code != 401

    @patch.object(auth_service, 'verify_api_key')
    def test_valid_api_key_allows_access(self, mock_verify_api_key, client, mock_user):
        """Test that valid API key allows access to protected endpoints"""
        # Mock API key validation
        mock_verify_api_key.return_value = mock_user
        
        # Request with valid API key should succeed
        headers = {"X-API-Key": "valid-api-key"}
        response = client.get("/api/admin/test", headers=headers)
        # Will get 404 since route doesn't exist, but not 401
        assert response.status_code != 401

    def test_invalid_auth_rejected(self, client):
        """Test that invalid authentication is rejected"""
        # Invalid JWT token
        headers = {"Authorization": "Bearer invalid-token"}
        response = client.get("/api/admin/users", headers=headers)
        assert response.status_code == 401
        
        # Invalid API key
        headers = {"X-API-Key": "invalid-key"}
        response = client.get("/api/debug/environment-variables", headers=headers)
        assert response.status_code == 401


class TestRateLimiting:
    """Test rate limiting middleware"""

    @patch.object(rate_limit_service, 'redis')
    def test_rate_limit_headers_added(self, mock_redis, client):
        """Test that rate limit headers are added to responses"""
        # Mock Redis to simulate rate limiting
        mock_redis.incr.return_value = 1
        mock_redis.expire.return_value = True
        
        response = client.get("/api/health")
        assert response.status_code == 200
        
        # Check rate limit headers
        assert "X-RateLimit-Limit" in response.headers
        assert "X-RateLimit-Remaining" in response.headers
        assert "X-RateLimit-Reset" in response.headers

    @patch.object(rate_limit_service, 'redis')
    def test_rate_limit_exceeded_returns_429(self, mock_redis, client):
        """Test that exceeding rate limit returns 429"""
        # Mock Redis to simulate rate limit exceeded
        mock_redis.incr.return_value = 1000  # Exceed limit
        
        response = client.get("/api/orchestrator/test")
        assert response.status_code == 429
        assert response.json()["code"] == "rate_limit_exceeded"
        assert "Retry-After" in response.headers

    @patch.object(rate_limit_service, 'redis')
    @patch.object(auth_service, 'get_user')
    @patch('app.middleware.combined_auth_middleware.decode_token')
    @patch('app.middleware.combined_auth_middleware.is_token_expired')
    def test_per_user_rate_limiting(self, mock_expired, mock_decode, mock_get_user, mock_redis, client, mock_user):
        """Test that rate limiting is per-user when authenticated"""
        # Mock token validation
        mock_expired.return_value = False
        mock_decode.return_value = {"sub": "1", "type": "access"}
        mock_get_user.return_value = mock_user
        
        # Mock Redis
        mock_redis.incr.return_value = 1
        
        # Make authenticated request
        headers = {"Authorization": "Bearer valid-token"}
        response = client.get("/api/orchestrator/test", headers=headers)
        
        # Verify Redis was called with user-specific key
        mock_redis.incr.assert_called()
        call_args = mock_redis.incr.call_args[0][0]
        assert "user:1" in call_args  # User ID should be in the key

    @patch.object(rate_limit_service, 'redis')
    def test_ip_based_rate_limiting_for_unauthenticated(self, mock_redis, client):
        """Test that rate limiting is IP-based for unauthenticated requests"""
        # Mock Redis
        mock_redis.incr.return_value = 1
        
        # Make unauthenticated request
        response = client.get("/api/health")
        
        # Verify Redis was called with IP-based key
        mock_redis.incr.assert_called()
        call_args = mock_redis.incr.call_args[0][0]
        assert "ip:" in call_args  # IP should be in the key

    @patch.object(rate_limit_service, 'redis', new_callable=Mock)
    def test_rate_limiting_disabled_when_redis_unavailable(self, mock_redis, client):
        """Test that rate limiting is disabled when Redis is unavailable"""
        # With Redis unavailable, requests should still work
        mock_redis.ping.side_effect = ConnectionError
        
        response = client.get("/api/health")
        assert response.status_code == 200
        
        # Rate limit headers should not be present when redis is down
        assert "X-RateLimit-Limit" not in response.headers


@pytest.mark.integration
class TestAuthRateLimitIntegration:
    """Integration tests for auth and rate limiting together"""

    @patch.object(auth_service, 'get_user')
    @patch.object(auth_service, 'verify_api_key')
    @patch.object(rate_limit_service, 'redis')
    @patch('app.middleware.combined_auth_middleware.decode_token')
    @patch('app.middleware.combined_auth_middleware.is_token_expired')
    def test_authenticated_user_gets_tier_based_limits(
        self, mock_expired, mock_decode, mock_redis, mock_verify_api_key, mock_get_user, client
    ):
        """Test that authenticated users get rate limits based on their subscription tier"""
        # Create users with different tiers
        basic_user = Mock(spec=User)
        basic_user.id = 1
        basic_user.subscription_tier = SubscriptionTier.BASIC
        
        premium_user = Mock(spec=User)
        premium_user.id = 2
        premium_user.subscription_tier = SubscriptionTier.PREMIUM
        
        # Mock token validation for basic user
        mock_expired.return_value = False
        mock_decode.return_value = {"sub": "1", "type": "access"}
        mock_get_user.return_value = basic_user
        mock_redis.incr.return_value = 1
        
        # Basic user request
        headers = {"Authorization": "Bearer basic-user-token"}
        response = client.get("/api/orchestrator/test", headers=headers)
        
        # Check basic tier limits (300 req/min for general API)
        assert response.headers["X-RateLimit-Limit"] == "300"
        assert response.headers["X-RateLimit-Remaining"] == "299"  # First request
        
        # Mock token validation for premium user
        mock_decode.return_value = {"sub": "2", "type": "access"}
        mock_get_user.return_value = premium_user
        
        # Premium user request
        headers = {"Authorization": "Bearer premium-user-token"}
        response = client.get("/api/orchestrator/test", headers=headers)
        
        # Check premium tier limits (1000 req/min for general API)
        assert response.headers["X-RateLimit-Limit"] == "1000"

    def test_env_variable_controls(self, monkeypatch):
        """Test that ENABLE_AUTH and ENABLE_RATE_LIMIT env variables work"""
        # Disable auth
        monkeypatch.setenv("ENABLE_AUTH", "false")
        Config.ENABLE_AUTH = False
        app = create_app()
        client = TestClient(app)
        
        # Admin endpoint should be accessible without auth
        response = client.get("/api/admin/test")
        assert response.status_code != 401
        
        # Disable rate limiting
        monkeypatch.setenv("ENABLE_RATE_LIMIT", "false")
        Config.ENABLE_RATE_LIMIT = False
        app = create_app()
        client = TestClient(app)
        
        # No rate limit headers should be present
        response = client.get("/api/health")
        assert "X-RateLimit-Limit" not in response.headers
    
    @patch.object(rate_limit_service, 'redis')
    def test_rate_limit_tier_override_in_testing(self, mock_redis, monkeypatch):
        """Test that TEST_RATE_LIMIT_TIER env var overrides tier in testing"""
        # Set testing mode and tier override
        monkeypatch.setenv("TESTING", "true")
        monkeypatch.setenv("TEST_RATE_LIMIT_TIER", "PREMIUM")
        Config.ENABLE_RATE_LIMIT = True
        
        app = create_app()
        client = TestClient(app)
        
        # Mock Redis
        mock_redis.incr.return_value = 1
        
        # Make unauthenticated request (normally FREE tier)
        response = client.get("/api/orchestrator/test")
        
        # Should get PREMIUM tier limits (1000) instead of FREE (60)
        assert response.headers["X-RateLimit-Limit"] == "1000"