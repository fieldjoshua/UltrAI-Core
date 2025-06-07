import pytest
from app.services.rate_limit_service import (
    RateLimitInterval,
    RateLimitTier,
    TIER_LIMITS,
    DEFAULT_TIER,
)
from app.database.models.user import SubscriptionTier


@pytest.mark.parametrize(
    "interval,expected",
    [
        (RateLimitInterval.SECOND, 1),
        (RateLimitInterval.MINUTE, 60),
        (RateLimitInterval.HOUR, 3600),
        (RateLimitInterval.DAY, 86400),
    ],
)
def test_get_window_seconds(interval, expected):
    tier = RateLimitTier(
        tier=SubscriptionTier.FREE,
        general_limit=0,
        general_interval=interval,
        analyze_limit=0,
        analyze_interval=interval,
        document_limit=0,
        document_interval=interval,
    )
    assert tier.get_window_seconds(interval) == expected


def test_tier_limits_keys():
    # Ensure TIER_LIMITS contains all subscription tiers
    tiers = set(TIER_LIMITS.keys())
    expected = set(item for item in SubscriptionTier)
    assert tiers == expected


def test_default_tier_is_free():
    assert DEFAULT_TIER == SubscriptionTier.FREE
