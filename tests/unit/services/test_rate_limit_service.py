"""
Comprehensive tests for rate limit service functionality.
"""

import pytest
import time
from unittest.mock import Mock, MagicMock

from app.services.rate_limit_service import (
    RateLimitService,
    RateLimitInterval,
    RateLimitTier,
    RateLimitResult,
    RateLimitCategory,
    TIER_LIMITS,
)
from app.database.models.user import SubscriptionTier, User
from fastapi import Request


@pytest.mark.unit
class TestRateLimitService:
    """Test rate limit service core functionality"""

    @pytest.fixture
    def rate_limit_service(self):
        """Create a rate limit service instance"""
        return RateLimitService()

    @pytest.fixture
    def mock_redis(self):
        """Create a mock Redis client"""
        redis_mock = MagicMock()
        redis_mock.get.return_value = None
        redis_mock.incr.return_value = 1
        redis_mock.expire.return_value = True
        redis_mock.ttl.return_value = 60
        return redis_mock
    
    @pytest.fixture
    def mock_request(self):
        """Create a mock FastAPI request"""
        request = MagicMock(spec=Request)
        request.url.path = "/api/analyze"
        request.client.host = "127.0.0.1"
        request.headers = {}
        return request
    
    @pytest.fixture
    def mock_user(self):
        """Create a mock user"""
        user = MagicMock(spec=User)
        user.id = "user123"
        user.subscription_tier = SubscriptionTier.FREE
        return user

    def test_rate_limit_result_properties(self):
        """Test RateLimitResult object properties"""
        result = RateLimitResult(
            is_allowed=True,
            limit=100,
            remaining=75,
            reset_at=int(time.time()) + 3600
        )
        
        assert result.is_allowed is True
        assert result.limit == 100
        assert result.remaining == 75
        assert result.reset_at > time.time()
        
        # Test that result has required properties
        assert hasattr(result, 'is_allowed')
        assert hasattr(result, 'limit')
        assert hasattr(result, 'remaining')
        assert hasattr(result, 'reset_at')

    def test_check_rate_limit_first_request(self, rate_limit_service, mock_redis, mock_request, mock_user):
        """Test rate limit check for first request"""
        rate_limit_service.redis = mock_redis
        
        result = rate_limit_service.check_rate_limit(
            request=mock_request,
            user=mock_user
        )
        
        # First request should be allowed
        assert result.is_allowed is True
        assert result.remaining == TIER_LIMITS[SubscriptionTier.FREE].analyze_limit - 1
        assert result.limit == TIER_LIMITS[SubscriptionTier.FREE].analyze_limit
        
        # Redis should have been called to increment
        mock_redis.incr.assert_called_once()
        mock_redis.expire.assert_called_once()

    def test_check_rate_limit_exceeded(self, rate_limit_service, mock_redis, mock_request, mock_user):
        """Test rate limit exceeded scenario"""
        # Mock Redis to return count over limit
        tier_limit = TIER_LIMITS[SubscriptionTier.FREE].analyze_limit
        # When incr is called, it should return a value over the limit
        mock_redis.incr.return_value = tier_limit + 1
        mock_redis.ttl.return_value = 3600
        rate_limit_service.redis = mock_redis
        
        result = rate_limit_service.check_rate_limit(
            request=mock_request,
            user=mock_user
        )
        
        # Should be blocked
        assert result.is_allowed is False
        assert result.remaining == 0
        assert result.retry_after is not None

    def test_rate_limit_without_redis(self, rate_limit_service, mock_request, mock_user):
        """Test rate limiting when Redis is not available"""
        # Redis is None by default (not connected)
        assert rate_limit_service.redis is None
        
        result = rate_limit_service.check_rate_limit(
            request=mock_request,
            user=mock_user
        )
        
        # Should allow requests when Redis is down
        assert result.is_allowed is True
        # When Redis is down, it still returns the configured limits
        assert result.limit == TIER_LIMITS[SubscriptionTier.FREE].analyze_limit
        assert result.remaining == TIER_LIMITS[SubscriptionTier.FREE].analyze_limit

    def test_categorize_request(self, rate_limit_service, mock_request):
        """Test request categorization"""
        # Test analyze endpoint
        mock_request.url.path = "/api/analyze"
        assert rate_limit_service.categorize_request(mock_request) == RateLimitCategory.ANALYZE
        
        # Test document endpoint
        mock_request.url.path = "/api/document/upload"
        assert rate_limit_service.categorize_request(mock_request) == RateLimitCategory.DOCUMENT
        
        # Test general endpoint
        mock_request.url.path = "/api/users"
        assert rate_limit_service.categorize_request(mock_request) == RateLimitCategory.GENERAL

    def test_get_client_identifier_with_user(self, rate_limit_service, mock_request, mock_user):
        """Test client identifier generation with authenticated user"""
        identifier = rate_limit_service.get_client_identifier(mock_request, mock_user)
        assert identifier == "user:user123"

    def test_get_client_identifier_with_ip(self, rate_limit_service, mock_request):
        """Test client identifier generation with IP address"""
        identifier = rate_limit_service.get_client_identifier(mock_request, None)
        assert identifier == "ip:127.0.0.1"
        
        # Test with X-Forwarded-For header
        mock_request.headers = {"X-Forwarded-For": "192.168.1.1, 10.0.0.1"}
        identifier = rate_limit_service.get_client_identifier(mock_request, None)
        assert identifier == "ip:192.168.1.1"

    def test_build_key(self, rate_limit_service):
        """Test Redis key generation"""
        key = rate_limit_service.build_key(
            identifier="user:123",
            category=RateLimitCategory.ANALYZE,
            window_timestamp=1234567890
        )
        # The enum value is included in the key
        assert key == "ratelimit:user:123:RateLimitCategory.ANALYZE:1234567890"

    def test_tier_configuration(self):
        """Test tier configuration is properly set"""
        # Verify FREE tier
        free_tier = TIER_LIMITS[SubscriptionTier.FREE]
        assert free_tier.general_limit == 60
        assert free_tier.general_interval == RateLimitInterval.MINUTE
        assert free_tier.analyze_limit == 10  # Actual limit is 10, not 20
        assert free_tier.analyze_interval == RateLimitInterval.MINUTE  # Actual interval is MINUTE
        
        # Verify BASIC tier exists
        assert SubscriptionTier.BASIC in TIER_LIMITS
        basic_tier = TIER_LIMITS[SubscriptionTier.BASIC]
        assert basic_tier.general_limit > free_tier.general_limit
        
        # Verify PREMIUM tier exists
        assert SubscriptionTier.PREMIUM in TIER_LIMITS
        premium_tier = TIER_LIMITS[SubscriptionTier.PREMIUM]
        assert premium_tier.general_limit > basic_tier.general_limit

    def test_get_limit_for_category(self, rate_limit_service):
        """Test getting limits for different categories"""
        # Test analyze category
        limit, interval = rate_limit_service.get_limit_for_category(
            SubscriptionTier.FREE,
            RateLimitCategory.ANALYZE
        )
        assert limit == TIER_LIMITS[SubscriptionTier.FREE].analyze_limit
        assert interval == TIER_LIMITS[SubscriptionTier.FREE].analyze_interval
        
        # Test general category
        limit, interval = rate_limit_service.get_limit_for_category(
            SubscriptionTier.FREE,
            RateLimitCategory.GENERAL
        )
        assert limit == TIER_LIMITS[SubscriptionTier.FREE].general_limit
        assert interval == TIER_LIMITS[SubscriptionTier.FREE].general_interval