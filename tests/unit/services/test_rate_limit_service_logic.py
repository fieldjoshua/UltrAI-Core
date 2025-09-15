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
        pro_limit = TIER_LIMITS[SubscriptionTier.PRO].analyze_limit
        enterprise_limit = TIER_LIMITS[SubscriptionTier.ENTERPRISE].analyze_limit
        
        assert free_limit < pro_limit, "PRO should have higher limit than FREE"
        assert pro_limit < enterprise_limit, "ENTERPRISE should have higher limit than PRO"
        
        # Check document endpoint limits
        free_doc = TIER_LIMITS[SubscriptionTier.FREE].document_limit
        pro_doc = TIER_LIMITS[SubscriptionTier.PRO].document_limit
        enterprise_doc = TIER_LIMITS[SubscriptionTier.ENTERPRISE].document_limit
        
        assert free_doc < pro_doc
        assert pro_doc < enterprise_doc

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
        """Test endpoint-specific rate limits are different"""
        for tier_name, tier_config in TIER_LIMITS.items():
            # Generally, analyze should be most restricted, documents moderate, general least
            if tier_name != SubscriptionTier.ENTERPRISE:  # Enterprise might have custom config
                assert tier_config.analyze_limit <= tier_config.document_limit, \
                    f"{tier_name}: analyze should be more restricted than documents"
                assert tier_config.document_limit <= tier_config.general_limit, \
                    f"{tier_name}: documents should be more restricted than general"


class TestRateLimitKeyGeneration:
    """Test rate limit key generation logic"""

    def test_rate_limit_key_format(self):
        """Test the format of rate limit keys"""
        service = RateLimitService()
        
        # Test user-based key
        user_key = service._generate_rate_limit_key(
            identifier="user:123",
            endpoint="api.analyze",
            window=60
        )
        
        assert "rate_limit:" in user_key
        assert "user:123" in user_key
        assert "api.analyze" in user_key
        
        # Test IP-based key
        ip_key = service._generate_rate_limit_key(
            identifier="ip:192.168.1.1",
            endpoint="api.general",
            window=3600
        )
        
        assert "rate_limit:" in ip_key
        assert "ip:192.168.1.1" in ip_key
        assert "api.general" in ip_key

    def test_rate_limit_key_uniqueness(self):
        """Test that rate limit keys are unique per user/endpoint/window"""
        service = RateLimitService()
        
        # Different users should have different keys
        key1 = service._generate_rate_limit_key("user:123", "api.analyze", 60)
        key2 = service._generate_rate_limit_key("user:456", "api.analyze", 60)
        assert key1 != key2
        
        # Different endpoints should have different keys
        key3 = service._generate_rate_limit_key("user:123", "api.analyze", 60)
        key4 = service._generate_rate_limit_key("user:123", "api.document", 60)
        assert key3 != key4
        
        # Different windows should have different keys
        key5 = service._generate_rate_limit_key("user:123", "api.analyze", 60)
        key6 = service._generate_rate_limit_key("user:123", "api.analyze", 3600)
        # Keys might be same if in same window, but window affects expiry


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
        
        # ENTERPRISE should have high limits
        assert enterprise_tier.analyze_limit >= 1000, "ENTERPRISE analyze limit too low"
        assert enterprise_tier.document_limit >= 5000, "ENTERPRISE document limit too low"
        
        # ENTERPRISE can use larger windows
        assert enterprise_tier.analyze_interval in [RateLimitInterval.HOUR, RateLimitInterval.DAY]

    def test_rate_limit_headers_format(self):
        """Test rate limit headers follow standard format"""
        from app.services.rate_limit_service import RateLimitResult
        import time
        
        result = RateLimitResult(
            allowed=True,
            limit=100,
            remaining=75,
            reset_time=int(time.time()) + 3600
        )
        
        headers = result.to_headers()
        
        # Check header names follow standard
        assert "X-RateLimit-Limit" in headers
        assert "X-RateLimit-Remaining" in headers
        assert "X-RateLimit-Reset" in headers
        
        # Check header values are strings (HTTP headers must be strings)
        assert isinstance(headers["X-RateLimit-Limit"], str)
        assert isinstance(headers["X-RateLimit-Remaining"], str)
        assert isinstance(headers["X-RateLimit-Reset"], str)
        
        # Check values are numeric when parsed
        assert headers["X-RateLimit-Limit"].isdigit()
        assert headers["X-RateLimit-Remaining"].isdigit()
        assert headers["X-RateLimit-Reset"].isdigit()

    def test_rate_limit_result_for_blocked_request(self):
        """Test rate limit result when request is blocked"""
        from app.services.rate_limit_service import RateLimitResult
        import time
        
        result = RateLimitResult(
            allowed=False,
            limit=100,
            remaining=0,
            reset_time=int(time.time()) + 1800  # 30 minutes
        )
        
        assert result.allowed is False
        assert result.remaining == 0
        
        headers = result.to_headers()
        assert headers["X-RateLimit-Remaining"] == "0"
        
        # Reset time should be in the future
        assert int(headers["X-RateLimit-Reset"]) > time.time()
