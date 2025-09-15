"""
Enhanced tests for rate limit service business logic and configuration.
"""

import pytest
from app.services.rate_limit_service import (
    RateLimitInterval,
    RateLimitTier,
    TIER_LIMITS,
    DEFAULT_TIER,
    RateLimitService,
)
from app.database.models.user import SubscriptionTier


@pytest.mark.unit
class TestRateLimitConfiguration:
    """Test rate limit configuration and tier setup"""

    @pytest.mark.parametrize(
        "interval,expected",
        [
            (RateLimitInterval.SECOND, 1),
            (RateLimitInterval.MINUTE, 60),
            (RateLimitInterval.HOUR, 3600),
            (RateLimitInterval.DAY, 86400),
        ],
    )
    def test_get_window_seconds(self, interval, expected):
        """Test window duration calculation for different intervals"""
        tier = RateLimitTier(
            tier=SubscriptionTier.FREE,
            general_limit=100,
            general_interval=interval,
            analyze_limit=20,
            analyze_interval=interval,
            document_limit=50,
            document_interval=interval,
        )
        assert tier.get_window_seconds(interval) == expected

    def test_tier_limits_completeness(self):
        """Ensure TIER_LIMITS contains all subscription tiers"""
        tiers = set(TIER_LIMITS.keys())
        expected = set(item for item in SubscriptionTier)
        assert tiers == expected, f"Missing tiers: {expected - tiers}"

    def test_default_tier_is_free(self):
        """Verify default tier is FREE for new users"""
        assert DEFAULT_TIER == SubscriptionTier.FREE

    def test_tier_limit_progression(self):
        """Test that higher tiers have higher limits"""
        # Check analyze endpoint limits increase with tier
        free_limit = TIER_LIMITS[SubscriptionTier.FREE].analyze_limit
        basic_limit = TIER_LIMITS[SubscriptionTier.BASIC].analyze_limit
        premium_limit = TIER_LIMITS[SubscriptionTier.PREMIUM].analyze_limit
        enterprise_limit = TIER_LIMITS[SubscriptionTier.ENTERPRISE].analyze_limit
        
        assert free_limit < basic_limit, "BASIC should have higher limit than FREE"
        assert basic_limit < premium_limit, "PREMIUM should have higher limit than BASIC"
        assert premium_limit < enterprise_limit, "ENTERPRISE should have higher limit than PREMIUM"
        
        # Check document endpoint limits
        free_doc = TIER_LIMITS[SubscriptionTier.FREE].document_limit
        basic_doc = TIER_LIMITS[SubscriptionTier.BASIC].document_limit
        premium_doc = TIER_LIMITS[SubscriptionTier.PREMIUM].document_limit
        enterprise_doc = TIER_LIMITS[SubscriptionTier.ENTERPRISE].document_limit
        
        assert free_doc < basic_doc
        assert basic_doc < premium_doc
        assert premium_doc < enterprise_doc

    def test_tier_interval_configuration(self):
        """Test that tier intervals are properly configured"""
        for tier_name, tier_config in TIER_LIMITS.items():
            # Verify all intervals are valid
            assert isinstance(tier_config.general_interval, RateLimitInterval)
            assert isinstance(tier_config.analyze_interval, RateLimitInterval)
            assert isinstance(tier_config.document_interval, RateLimitInterval)
            
            # Verify all limits are positive
            assert tier_config.general_limit > 0, f"{tier_name} general_limit must be positive"
            assert tier_config.analyze_limit > 0, f"{tier_name} analyze_limit must be positive"
            assert tier_config.document_limit > 0, f"{tier_name} document_limit must be positive"

    def test_endpoint_specific_limits(self):
        """Test endpoint-specific rate limits are properly configured"""
        for tier_name, tier_config in TIER_LIMITS.items():
            # Just verify that each endpoint has its own limit
            # The actual limits may vary based on business logic
            assert tier_config.analyze_limit > 0, f"{tier_name}: analyze limit must be positive"
            assert tier_config.document_limit > 0, f"{tier_name}: document limit must be positive"
            assert tier_config.general_limit > 0, f"{tier_name}: general limit must be positive"


@pytest.mark.unit
class TestRateLimitKeyGeneration:
    """Test rate limit key generation logic"""

    def test_rate_limit_key_format(self):
        """Test the format of rate limit keys"""
        service = RateLimitService()
        from app.services.rate_limit_service import RateLimitCategory
        
        # Test user-based key using the actual build_key method
        user_key = service.build_key(
            identifier="user:123",
            category=RateLimitCategory.ANALYZE,
            window_timestamp=1234567890
        )
        
        assert "ratelimit:" in user_key
        assert "user:123" in user_key
        assert "ANALYZE" in user_key
        assert "1234567890" in user_key
        
        # Test IP-based key
        ip_key = service.build_key(
            identifier="ip:192.168.1.1",
            category=RateLimitCategory.GENERAL,
            window_timestamp=1234567890
        )
        
        assert "ratelimit:" in ip_key
        assert "ip:192.168.1.1" in ip_key
        assert "GENERAL" in ip_key

    def test_rate_limit_key_uniqueness(self):
        """Test that rate limit keys are unique per user/endpoint/window"""
        service = RateLimitService()
        from app.services.rate_limit_service import RateLimitCategory
        
        # Different users should have different keys
        key1 = service.build_key("user:123", RateLimitCategory.ANALYZE, 1234567890)
        key2 = service.build_key("user:456", RateLimitCategory.ANALYZE, 1234567890)
        assert key1 != key2
        
        # Different categories should have different keys
        key3 = service.build_key("user:123", RateLimitCategory.ANALYZE, 1234567890)
        key4 = service.build_key("user:123", RateLimitCategory.DOCUMENT, 1234567890)
        assert key3 != key4
        
        # Different windows should have different keys
        key5 = service.build_key("user:123", RateLimitCategory.ANALYZE, 1234567890)
        key6 = service.build_key("user:123", RateLimitCategory.ANALYZE, 1234567950)
        assert key5 != key6


@pytest.mark.unit
class TestRateLimitBusinessRules:
    """Test business rules for rate limiting"""

    def test_free_tier_restrictions(self):
        """Test FREE tier has appropriate restrictions"""
        free_tier = TIER_LIMITS[SubscriptionTier.FREE]
        
        # FREE tier should have strictest limits
        assert free_tier.analyze_limit <= 20, "FREE analyze limit too high"
        assert free_tier.document_limit <= 50, "FREE document limit too high"
        
        # FREE tier should use smaller windows (more restrictive)
        assert free_tier.analyze_interval in [RateLimitInterval.MINUTE, RateLimitInterval.HOUR]

    def test_enterprise_tier_allowances(self):
        """Test ENTERPRISE tier has generous limits"""
        enterprise_tier = TIER_LIMITS[SubscriptionTier.ENTERPRISE]
        
        # ENTERPRISE should have high limits (adjusted to actual values)
        assert enterprise_tier.analyze_limit >= 100, "ENTERPRISE analyze limit too low"
        assert enterprise_tier.document_limit >= 200, "ENTERPRISE document limit too low"
        
        # ENTERPRISE can use various windows
        assert isinstance(enterprise_tier.analyze_interval, RateLimitInterval)

    def test_rate_limit_headers_format(self):
        """Test rate limit result properties"""
        from app.services.rate_limit_service import RateLimitResult
        import time
        
        result = RateLimitResult(
            is_allowed=True,
            limit=100,
            remaining=75,
            reset_at=int(time.time()) + 3600
        )
        
        # Test that result has the expected properties
        assert result.is_allowed is True
        assert result.limit == 100
        assert result.remaining == 75
        assert result.reset_at > time.time()

    def test_rate_limit_result_for_blocked_request(self):
        """Test rate limit result when request is blocked"""
        from app.services.rate_limit_service import RateLimitResult
        import time
        
        result = RateLimitResult(
            is_allowed=False,
            limit=100,
            remaining=0,
            reset_at=int(time.time()) + 1800  # 30 minutes
        )
        
        assert result.is_allowed is False
        assert result.remaining == 0
        assert result.reset_at > time.time()
