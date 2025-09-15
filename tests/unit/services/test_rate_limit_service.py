"""
Comprehensive tests for rate limit service functionality.
"""

import pytest
import asyncio
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock

from app.services.rate_limit_service import (
    RateLimitService,
    RateLimitInterval,
    RateLimitTier,
    RateLimitResult,
    TIER_LIMITS,
)
from app.database.models.user import SubscriptionTier


class TestRateLimitService:
    """Test rate limit service core functionality"""

    @pytest.fixture
    def rate_limit_service(self):
        """Create a rate limit service instance"""
        return RateLimitService()

    @pytest.fixture
    def mock_redis(self):
        """Create a mock Redis client"""
        redis_mock = AsyncMock()
        redis_mock.get.return_value = None
        redis_mock.incr.return_value = 1
        redis_mock.expire.return_value = True
        return redis_mock

    def test_rate_limit_result_properties(self):
        """Test RateLimitResult object properties"""
        result = RateLimitResult(
            allowed=True,
            limit=100,
            remaining=75,
            reset_time=int(time.time()) + 3600
        )
        
        assert result.allowed is True
        assert result.limit == 100
        assert result.remaining == 75
        assert result.reset_time > time.time()
        
        # Test headers generation
        headers = result.to_headers()
        assert headers["X-RateLimit-Limit"] == "100"
        assert headers["X-RateLimit-Remaining"] == "75"
        assert "X-RateLimit-Reset" in headers

    @pytest.mark.asyncio
    async def test_check_rate_limit_first_request(self, rate_limit_service, mock_redis):
        """Test rate limit check for first request"""
        rate_limit_service.redis_client = mock_redis
        
        result = await rate_limit_service.check_rate_limit(
            identifier="user123",
            endpoint="api.analyze",
            tier=SubscriptionTier.FREE
        )
        
        # First request should be allowed
        assert result.allowed is True
        assert result.remaining == TIER_LIMITS[SubscriptionTier.FREE].analyze_limit - 1
        assert result.limit == TIER_LIMITS[SubscriptionTier.FREE].analyze_limit
        
        # Redis should have been called to increment
        mock_redis.incr.assert_called_once()
        mock_redis.expire.assert_called_once()

    @pytest.mark.asyncio
    async def test_check_rate_limit_exceeded(self, rate_limit_service, mock_redis):
        """Test rate limit exceeded scenario"""
        # Mock Redis to return count at limit
        tier_limit = TIER_LIMITS[SubscriptionTier.FREE].analyze_limit
        mock_redis.get.return_value = str(tier_limit).encode()
        rate_limit_service.redis_client = mock_redis
        
        result = await rate_limit_service.check_rate_limit(
            identifier="user123",
            endpoint="api.analyze",
            tier=SubscriptionTier.FREE
        )
        
        # Should not be allowed
        assert result.allowed is False
        assert result.remaining == 0
        assert result.limit == tier_limit
        
        # Should not increment when at limit
        mock_redis.incr.assert_not_called()

    @pytest.mark.asyncio
    async def test_rate_limit_with_different_tiers(self, rate_limit_service, mock_redis):
        """Test rate limits for different subscription tiers"""
        rate_limit_service.redis_client = mock_redis
        
        # Test each tier
        for tier in SubscriptionTier:
            mock_redis.get.return_value = None  # Reset for each tier
            mock_redis.incr.return_value = 1
            
            result = await rate_limit_service.check_rate_limit(
                identifier=f"user_{tier.value}",
                endpoint="api.analyze",
                tier=tier
            )
            
            expected_limit = TIER_LIMITS[tier].analyze_limit
            assert result.allowed is True
            assert result.limit == expected_limit
            assert result.remaining == expected_limit - 1

    @pytest.mark.asyncio
    async def test_rate_limit_window_expiration(self, rate_limit_service, mock_redis):
        """Test rate limit window expiration"""
        rate_limit_service.redis_client = mock_redis
        
        # Get the window duration for FREE tier analyze endpoint
        tier_config = TIER_LIMITS[SubscriptionTier.FREE]
        window_seconds = tier_config.get_window_seconds(tier_config.analyze_interval)
        
        result = await rate_limit_service.check_rate_limit(
            identifier="user123",
            endpoint="api.analyze",
            tier=SubscriptionTier.FREE
        )
        
        # Check that expire was called with correct window
        mock_redis.expire.assert_called_with(
            mock_redis.incr.return_value,
            window_seconds
        )

    @pytest.mark.asyncio
    async def test_rate_limit_different_endpoints(self, rate_limit_service, mock_redis):
        """Test rate limits are tracked separately per endpoint"""
        rate_limit_service.redis_client = mock_redis
        mock_redis.incr.side_effect = [1, 1]  # Different counters
        
        # Check rate limit for analyze endpoint
        result1 = await rate_limit_service.check_rate_limit(
            identifier="user123",
            endpoint="api.analyze",
            tier=SubscriptionTier.FREE
        )
        
        # Check rate limit for document endpoint
        result2 = await rate_limit_service.check_rate_limit(
            identifier="user123",
            endpoint="api.document",
            tier=SubscriptionTier.FREE
        )
        
        # Both should be allowed (separate limits)
        assert result1.allowed is True
        assert result2.allowed is True
        
        # Different limits for different endpoints
        assert result1.limit == TIER_LIMITS[SubscriptionTier.FREE].analyze_limit
        assert result2.limit == TIER_LIMITS[SubscriptionTier.FREE].document_limit

    @pytest.mark.asyncio
    async def test_rate_limit_per_user_isolation(self, rate_limit_service, mock_redis):
        """Test rate limits are isolated per user"""
        rate_limit_service.redis_client = mock_redis
        mock_redis.incr.side_effect = [1, 1]  # Different counters
        
        # Check rate limit for user1
        result1 = await rate_limit_service.check_rate_limit(
            identifier="user1",
            endpoint="api.analyze",
            tier=SubscriptionTier.FREE
        )
        
        # Check rate limit for user2
        result2 = await rate_limit_service.check_rate_limit(
            identifier="user2",
            endpoint="api.analyze",
            tier=SubscriptionTier.FREE
        )
        
        # Both users should be allowed
        assert result1.allowed is True
        assert result2.allowed is True
        assert result1.remaining == result2.remaining

    @pytest.mark.asyncio
    async def test_rate_limit_redis_failure_fallback(self, rate_limit_service):
        """Test fallback behavior when Redis is unavailable"""
        # Mock Redis to raise exception
        mock_redis = AsyncMock()
        mock_redis.get.side_effect = Exception("Redis connection failed")
        rate_limit_service.redis_client = mock_redis
        
        # Should fall back to allowing request
        result = await rate_limit_service.check_rate_limit(
            identifier="user123",
            endpoint="api.analyze",
            tier=SubscriptionTier.FREE
        )
        
        # Should allow when Redis fails (fail open)
        assert result.allowed is True
        assert result.limit > 0
        assert result.remaining > 0

    def test_rate_limit_key_generation(self, rate_limit_service):
        """Test rate limit key generation"""
        key = rate_limit_service._generate_key(
            identifier="user123",
            endpoint="api.analyze",
            window_start=datetime(2024, 1, 1, 12, 0, 0)
        )
        
        assert "rate_limit" in key
        assert "user123" in key
        assert "api.analyze" in key
        assert "2024-01-01" in key

    @pytest.mark.asyncio
    async def test_rate_limit_headers_on_success(self, rate_limit_service, mock_redis):
        """Test rate limit headers are properly set on successful request"""
        rate_limit_service.redis_client = mock_redis
        mock_redis.incr.return_value = 5
        
        result = await rate_limit_service.check_rate_limit(
            identifier="user123",
            endpoint="api.analyze",
            tier=SubscriptionTier.PRO
        )
        
        headers = result.to_headers()
        
        # Verify all required headers are present
        assert "X-RateLimit-Limit" in headers
        assert "X-RateLimit-Remaining" in headers
        assert "X-RateLimit-Reset" in headers
        
        # Verify header values
        expected_limit = TIER_LIMITS[SubscriptionTier.PRO].analyze_limit
        assert headers["X-RateLimit-Limit"] == str(expected_limit)
        assert headers["X-RateLimit-Remaining"] == str(expected_limit - 5)
        assert int(headers["X-RateLimit-Reset"]) > time.time()

    @pytest.mark.asyncio
    async def test_concurrent_rate_limit_checks(self, rate_limit_service, mock_redis):
        """Test concurrent rate limit checks handle correctly"""
        rate_limit_service.redis_client = mock_redis
        
        # Simulate incrementing counter
        call_count = 0
        def increment_side_effect(*args):
            nonlocal call_count
            call_count += 1
            return call_count
        
        mock_redis.incr.side_effect = increment_side_effect
        
        # Make concurrent requests
        tasks = [
            rate_limit_service.check_rate_limit(
                identifier="user123",
                endpoint="api.analyze",
                tier=SubscriptionTier.FREE
            )
            for _ in range(5)
        ]
        
        results = await asyncio.gather(*tasks)
        
        # All requests should have different remaining counts
        remaining_counts = [r.remaining for r in results]
        assert len(set(remaining_counts)) == 5  # All unique
        
        # All should be allowed (under limit)
        assert all(r.allowed for r in results)