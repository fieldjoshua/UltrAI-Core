import pytest
from app.services.cache_service import CacheService


@pytest.fixture(autouse=True)
def disable_redis(monkeypatch):
    # Force Redis dependency to fail to use MemoryCache
    monkeypatch.setattr("app.services.cache_service.REDIS_URL", "invalid://url")


def test_memory_cache_basic_operations():
    service = CacheService()
    key = "test_key"
    # Should return None initially
    assert service.get(key) is None
    assert not service.exists(key)
    # Set value and TTL
    assert service.set(key, 1, ttl=1)
    assert service.exists(key)
    assert service.get(key) == 1
    # Increment value
    assert service.increment(key, amount=2) == 3
    # Delete key
    assert service.delete(key)
    assert service.get(key) is None


def test_memory_cache_dict_operations():
    service = CacheService()
    data_key = "dict_key"
    data = {"a": 1}
    assert service.set_dict(data_key, data)
    assert service.get_dict(data_key) == data
    # Test exists_json, delete_json
    import pytest
    import asyncio


@pytest.mark.asyncio
async def test_async_json_operations():
    service = CacheService()
    prefix = "prefix"
    payload = {"b": 2}
    success = await service.set_json(prefix, {"id": 1}, payload)
    assert success
    exists = await service.exists_json(prefix, {"id": 1})
    assert exists
    value = await service.get_json(prefix, {"id": 1})
    assert value == payload
    deleted = await service.delete_json(prefix, {"id": 1})
    assert deleted
