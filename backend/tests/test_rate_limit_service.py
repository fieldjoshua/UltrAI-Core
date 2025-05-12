"""
Unit tests for the rate limit service.

This module contains tests for the RateLimitService class that provides rate limiting
based on IP address, user ID, subscription tier, path, and method.
"""

import time
import json
import uuid
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

import pytest
import redis

from backend.utils.rate_limit_service import (
    RateLimitService,
    DEFAULT_RATE_LIMITS,
    DEFAULT_PATH_LIMITS,
    METHOD_WEIGHTS,
)


@pytest.fixture
def rate_limit_service():
    """Create a fresh instance of RateLimitService for testing"""
    with patch("backend.utils.rate_limit_service.redis") as mock_redis:
        # Mock redis to avoid actual connections
        mock_redis.from_url.return_value = Mock()
        mock_redis.from_url.return_value.ping.side_effect = Exception("No Redis")
        
        service = RateLimitService()
        service.redis = None  # Ensure we're using in-memory mode
        yield service


@pytest.fixture
def redis_rate_limit_service():
    """Create a RateLimitService with mocked Redis for testing"""
    with patch("backend.utils.rate_limit_service.redis") as mock_redis:
        # Create a mock Redis client
        mock_redis_client = MagicMock()
        mock_redis.from_url.return_value = mock_redis_client
        mock_redis_client.ping.return_value = True
        
        # Setup zcount, zcard behavior to simulate rate limits
        mock_redis_client.zcard.return_value = 0
        
        # Setup pipeline for multi-command transactions
        mock_pipeline = MagicMock()
        mock_redis_client.pipeline.return_value = mock_pipeline
        mock_pipeline.execute.return_value = [1, 1, 0, 1]  # zadd, zrem, zcard, expire
        
        # Simulated key existence check
        mock_redis_client.exists.return_value = False
        
        service = RateLimitService()
        service.redis = mock_redis_client
        yield service, mock_redis_client


def test_get_rate_limit_default(rate_limit_service):
    """Test default rate limits by tier"""
    # Test anonymous tier
    limit = rate_limit_service.get_rate_limit()
    assert limit == DEFAULT_RATE_LIMITS["anonymous"]
    
    # Test with user having different tiers
    for tier in ["free", "basic", "premium", "enterprise"]:
        user = Mock()
        user.subscription_tier = tier
        limit = rate_limit_service.get_rate_limit(user=user)
        assert limit == DEFAULT_RATE_LIMITS[tier]


def test_get_rate_limit_path_specific(rate_limit_service):
    """Test path-specific rate limits"""
    user = Mock()
    user.subscription_tier = "premium"
    
    # Test default path
    limit = rate_limit_service.get_rate_limit(user=user, path="/api/other")
    assert limit == DEFAULT_RATE_LIMITS["premium"]
    
    # Test LLM API path
    limit = rate_limit_service.get_rate_limit(user=user, path="/api/llm/chat")
    assert limit == DEFAULT_PATH_LIMITS["/api/llm/"]["premium"]
    
    # Test document API path
    limit = rate_limit_service.get_rate_limit(user=user, path="/api/document/upload")
    assert limit == DEFAULT_PATH_LIMITS["/api/document/"]["premium"]
    
    # Test analyze API path
    limit = rate_limit_service.get_rate_limit(user=user, path="/api/analyze/text")
    assert limit == DEFAULT_PATH_LIMITS["/api/analyze/"]["premium"]


def test_get_rate_limit_method_weight(rate_limit_service):
    """Test method weight affects rate limits"""
    user = Mock()
    user.subscription_tier = "basic"
    base_limit = DEFAULT_RATE_LIMITS["basic"]
    
    # Test with different methods
    for method, weight in METHOD_WEIGHTS.items():
        limit = rate_limit_service.get_rate_limit(user=user, method=method)
        expected_limit = max(1, int(base_limit / weight))
        assert limit == expected_limit


def test_check_rate_limit_basic(rate_limit_service):
    """Test basic rate limiting functionality with in-memory storage"""
    ip_address = "192.168.1.1"
    
    # First request should not be rate limited
    is_limited, info = rate_limit_service.check_rate_limit(ip_address=ip_address)
    assert not is_limited
    assert info["limit"] > 0
    assert info["remaining"] == info["limit"] - 1
    
    # Make many requests to exceed limit
    limit = info["limit"]
    for _ in range(limit):
        rate_limit_service.check_rate_limit(ip_address=ip_address)
    
    # Next request should be rate limited
    is_limited, info = rate_limit_service.check_rate_limit(ip_address=ip_address)
    assert is_limited
    assert info["remaining"] == 0


def test_check_rate_limit_with_user_id(rate_limit_service):
    """Test rate limiting based on user ID rather than IP"""
    user_id = "test_user_123"
    ip_address = "192.168.1.1"
    
    # First request should not be rate limited
    is_limited, info = rate_limit_service.check_rate_limit(
        ip_address=ip_address, user_id=user_id
    )
    assert not is_limited
    
    # Make many requests to exceed limit
    limit = info["limit"]
    for _ in range(limit):
        rate_limit_service.check_rate_limit(
            ip_address=ip_address, user_id=user_id
        )
    
    # Next request should be rate limited for this user
    is_limited, info = rate_limit_service.check_rate_limit(
        ip_address=ip_address, user_id=user_id
    )
    assert is_limited
    
    # Different user should not be rate limited
    is_limited, info = rate_limit_service.check_rate_limit(
        ip_address=ip_address, user_id="different_user"
    )
    assert not is_limited


def test_check_rate_limit_path_quota(rate_limit_service):
    """Test rate limiting with explicit path quota override"""
    ip_address = "192.168.1.1"
    path = "/api/custom"
    custom_limit = 5
    
    # Check rate limit with custom path quota
    is_limited, info = rate_limit_service.check_rate_limit(
        ip_address=ip_address, path=path, path_quota=custom_limit
    )
    assert not is_limited
    assert info["limit"] == custom_limit
    
    # Make enough requests to exceed custom limit
    for _ in range(custom_limit):
        rate_limit_service.check_rate_limit(
            ip_address=ip_address, path=path, path_quota=custom_limit
        )
    
    # Next request should be rate limited
    is_limited, info = rate_limit_service.check_rate_limit(
        ip_address=ip_address, path=path, path_quota=custom_limit
    )
    assert is_limited
    assert info["limit"] == custom_limit
    assert info["remaining"] == 0


def test_internal_service_token(rate_limit_service):
    """Test internal service tokens bypass rate limits"""
    ip_address = "192.168.1.1"
    
    # Register an internal service
    token = rate_limit_service.register_internal_service(
        service_name="test_service",
        secret_key="test_secret",
        ttl_hours=1
    )
    
    # Request with internal service token should bypass rate limits
    is_limited, info = rate_limit_service.check_rate_limit(
        ip_address=ip_address, internal_token=token
    )
    assert not is_limited
    assert info["source"] == "internal_service"
    assert info["service_name"] == "test_service"
    
    # Verify token validity check
    assert rate_limit_service.is_internal_service(token)
    assert not rate_limit_service.is_internal_service("invalid_token")
    
    # Unregister service
    success = rate_limit_service.unregister_internal_service(token)
    assert success
    
    # Token should no longer bypass rate limits
    assert not rate_limit_service.is_internal_service(token)


def test_internal_service_token_expiry(rate_limit_service):
    """Test internal service token expiry"""
    # Register an internal service with short expiry
    token = rate_limit_service.register_internal_service(
        service_name="expiring_service",
        secret_key="test_secret",
        ttl_hours=0.01  # Very short expiry (36 seconds)
    )

    # Token should be valid initially
    assert rate_limit_service.is_internal_service(token)

    # Directly manipulate the expiry time in the service's token store to simulate expiration
    # This avoids mocking datetime.now which can be complex
    service_info = rate_limit_service.internal_service_tokens[token]
    original_expiry = service_info["expiry"]

    # Set the expiry to a time in the past
    past_time = (datetime.now() - timedelta(hours=1)).isoformat()
    rate_limit_service.internal_service_tokens[token]["expiry"] = past_time

    # Token should now be expired
    assert not rate_limit_service.is_internal_service(token)

    # Token should be removed from internal_service_tokens
    assert token not in rate_limit_service.internal_service_tokens


def test_bypass_key(rate_limit_service):
    """Test bypass keys for rate limiting"""
    ip_address = "192.168.1.1"
    
    # Register a bypass key
    bypass_key = f"ip:{ip_address}"
    rate_limit_service.register_bypass_key(bypass_key, "testing")
    
    # Request should bypass rate limits
    is_limited, info = rate_limit_service.check_rate_limit(ip_address=ip_address)
    assert not is_limited
    assert info["source"] == "bypass"


def test_track_request(rate_limit_service):
    """Test request tracking functionality"""
    user_id = "test_user_456"
    ip_address = "192.168.1.1"
    path = "/api/test"
    method = "GET"
    subscription_tier = "premium"
    
    # Track a request
    rate_limit_service.track_request(
        user_id=user_id,
        ip_address=ip_address,
        path=path,
        method=method,
        subscription_tier=subscription_tier
    )
    
    # In-memory tracking is minimal, so we can't easily verify the results
    # This test primarily ensures the method runs without errors


def test_get_usage_report(rate_limit_service):
    """Test usage report generation"""
    user_id = "test_user_789"
    
    # Get usage report for user with no activity
    report = rate_limit_service.get_usage_report(user_id=user_id, days=3)
    
    # Report should contain entries for last 3 days
    assert len(report) == 3
    for date in report:
        assert report[date]["count"] == 0


def test_get_path_usage_report(rate_limit_service):
    """Test path usage report generation"""
    # Get path usage report
    report = rate_limit_service.get_path_usage_report(days=1)
    
    # Should have paths key
    assert "paths" in report


def test_clear_rate_limits(rate_limit_service):
    """Test clearing rate limits"""
    ip_address = "192.168.1.1"
    user_id = "test_user_to_clear"
    
    # Add some rate limit data
    rate_limit_service.check_rate_limit(ip_address=ip_address, user_id=user_id)
    
    # Clear rate limits for user
    rate_limit_service.clear_rate_limits(user_id=user_id)
    
    # User's rate limit data should be cleared
    assert user_id not in rate_limit_service.in_memory_store["user"]
    
    # Add data again
    rate_limit_service.check_rate_limit(ip_address=ip_address)
    
    # Clear all rate limits
    rate_limit_service.clear_rate_limits()
    
    # All rate limit data should be cleared
    assert len(rate_limit_service.in_memory_store["ip"]) == 0
    assert len(rate_limit_service.in_memory_store["user"]) == 0


def test_redis_rate_limit(redis_rate_limit_service):
    """Test rate limiting with Redis"""
    service, mock_redis = redis_rate_limit_service
    ip_address = "192.168.1.1"
    
    # Configure mock to simulate incremental usage
    mock_pipeline = mock_redis.pipeline.return_value
    
    # First call, not rate limited
    mock_pipeline.execute.return_value = [1, 1, 5, 1]  # zadd, zrem, zcard, expire
    is_limited, info = service.check_rate_limit(ip_address=ip_address)
    assert not is_limited
    assert info["count"] == 5
    
    # Second call, not rate limited
    mock_pipeline.execute.return_value = [1, 1, 10, 1]  # zadd, zrem, zcard, expire
    is_limited, info = service.check_rate_limit(ip_address=ip_address)
    assert not is_limited
    assert info["count"] == 10
    
    # Third call, rate limited (count > limit)
    mock_pipeline.execute.return_value = [1, 1, 100, 1]  # zadd, zrem, zcard, expire
    is_limited, info = service.check_rate_limit(ip_address=ip_address)
    assert is_limited
    assert info["count"] == 100
    assert info["remaining"] == 0


def test_redis_usage_report(redis_rate_limit_service):
    """Test usage report generation with Redis"""
    service, mock_redis = redis_rate_limit_service
    user_id = "test_redis_user"
    
    # Configure Redis mock for usage report
    mock_redis.exists.return_value = True
    mock_redis.hget.return_value = b"42"  # 42 requests
    mock_redis.hkeys.return_value = [b"requests", b"path:/api/test"]
    
    # Get usage report
    report = service.get_usage_report(user_id=user_id, days=1)
    
    # Should have entry for today with 42 requests
    assert len(report) == 1
    for date in report:
        assert report[date]["count"] == 42


def test_window_expiration(rate_limit_service):
    """Test rate limit window expiration"""
    ip_address = "192.168.0.1"
    
    # Make initial request to establish rate limit
    is_limited, info = rate_limit_service.check_rate_limit(ip_address=ip_address)
    limit = info["limit"]
    
    # Make enough requests to reach the limit
    for _ in range(limit):
        rate_limit_service.check_rate_limit(ip_address=ip_address)
    
    # Next request should be rate limited
    is_limited, _ = rate_limit_service.check_rate_limit(ip_address=ip_address)
    assert is_limited
    
    # Simulate time passing - modify timestamps in the store directly
    current_time = int(time.time())
    rate_limit_service.in_memory_store["ip"][ip_address] = [current_time - 61]  # 61 seconds ago
    
    # Now request should not be rate limited because window has passed
    is_limited, _ = rate_limit_service.check_rate_limit(ip_address=ip_address)
    assert not is_limited


def test_method_specific_rate_limiting(rate_limit_service):
    """Test rate limiting with different HTTP methods"""
    ip_address = "192.168.1.2"
    path = "/api/test"
    
    # Check limits for different methods
    methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    limits = {}
    
    for method in methods:
        is_limited, info = rate_limit_service.check_rate_limit(
            ip_address=ip_address, path=path, method=method
        )
        limits[method] = info["limit"]
    
    # POST/PUT/DELETE should have lower limits than GET due to higher weights
    assert limits["GET"] > limits["POST"]
    assert limits["GET"] > limits["PUT"]
    assert limits["GET"] > limits["DELETE"]
    
    # OPTIONS should have higher limit than GET due to lower weight
    assert limits["OPTIONS"] > limits["GET"]