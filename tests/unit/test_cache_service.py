import pytest
from app.services.cache_service import CacheService, cache_service


@pytest.fixture(autouse=True)
def disable_redis(monkeypatch):
    # Force Redis unavailable to use MemoryCache
    monkeypatch.setattr(cache_service, "is_redis_available", lambda: False)


def test_sync_cache_operations():
    service = CacheService()
    key = "key1"
    assert service.get(key) is None
    assert not service.exists(key)
    assert service.set(key, 1) is True
    assert service.exists(key)
    assert service.get(key) == 1
    assert service.increment(key, amount=2) == 3
    assert service.get(key) == 3


def test_delete_and_flush():
    service = CacheService()
    service.set("a", 1)
    service.set("b", 2)
    assert service.delete("a") is True
    assert not service.exists("a")
    assert service.flush() is True
    assert not service.exists("b")


@pytest.mark.asyncio
async def test_async_json_operations():
    service = CacheService()
    prefix = "pref"
    data = {"id": 1}
    payload = {"a": 1}
    assert await service.set_json(prefix, data, payload) is True
    assert await service.exists_json(prefix, data) is True
    assert await service.get_json(prefix, data) == payload
    assert await service.delete_json(prefix, data) is True
