import pytest
from app.services.rate_limiter import RateLimiter


@pytest.mark.asyncio
async def test_register_endpoint_and_stats():
    service = RateLimiter()
    service.register_endpoint("ep", requests_per_minute=5, burst_limit=10)
    stats = service.get_endpoint_stats("ep")
    assert stats["requests_per_minute"] == 5
    assert stats["current_requests"] == 0
    assert stats["backoff_factor"] == 1.0


@pytest.mark.asyncio
async def test_acquire_unregistered_raises():
    service = RateLimiter()
    with pytest.raises(ValueError):
        await service.acquire("nope")


@pytest.mark.asyncio
async def test_acquire_increments_current_requests():
    service = RateLimiter()
    service.register_endpoint("ep2", requests_per_minute=2)
    stats_before = service.get_endpoint_stats("ep2")
    assert stats_before["current_requests"] == 0

    await service.acquire("ep2")
    stats_after = service.get_endpoint_stats("ep2")
    assert stats_after["current_requests"] == 1


@pytest.mark.asyncio
async def test_release_unregistered_does_nothing_and_stats_empty():
    service = RateLimiter()
    # Should not raise
    await service.release("nope", success=True)
    assert service.get_endpoint_stats("nope") == {}


@pytest.mark.asyncio
async def test_release_adjusts_backoff():
    service = RateLimiter()
    service.register_endpoint("ep3", requests_per_minute=2)
    # Simulate failure
    await service.release("ep3", success=False)
    stats_fail = service.get_endpoint_stats("ep3")
    assert stats_fail["backoff_factor"] == 2.0

    # Simulate success
    await service.release("ep3", success=True)
    stats_success = service.get_endpoint_stats("ep3")
    assert stats_success["backoff_factor"] == 1.0
