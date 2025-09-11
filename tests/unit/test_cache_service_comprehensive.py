"""
Comprehensive unit tests for cache service functionality.
"""

import asyncio
import json
import time
from unittest.mock import AsyncMock, Mock, patch

import pytest
import redis.asyncio as redis

from app.services.cache_service import CacheService, cache_key, cached, get_cache_service


class TestCacheKeyGeneration:
    """Test cache key generation functionality"""

    def test_cache_key_simple_types(self):
        """Test cache key generation with simple types"""
        assert cache_key("test", 123) == "test:123"
        assert cache_key("prefix", "suffix") == "prefix:suffix"
        assert cache_key("bool", True) == "bool:True"

    def test_cache_key_complex_types(self):
        """Test cache key generation with complex types"""
        # Dict should produce consistent hash
        key1 = cache_key("dict", {"a": 1, "b": 2})
        key2 = cache_key("dict", {"b": 2, "a": 1})  # Different order, same content
        assert key1 == key2
        assert key1.startswith("dict:")
        
        # List
        key = cache_key("list", [1, 2, 3])
        assert key.startswith("list:")
        
        # Nested structures
        complex_data = {"models": ["gpt-4", "claude"], "options": {"temperature": 0.7}}
        key = cache_key("complex", complex_data)
        assert key.startswith("complex:")

    def test_cache_key_none_handling(self):
        """Test cache key handles None values"""
        assert cache_key("test", None) == "test:None"
        assert cache_key("test") == "test"


class TestCacheService:
    """Test core CacheService functionality"""

    @pytest.fixture
    def mock_redis(self):
        """Mock Redis client"""
        mock = AsyncMock()
        mock.ping = AsyncMock(return_value=True)
        mock.get = AsyncMock(return_value=None)
        mock.set = AsyncMock(return_value=True)
        mock.delete = AsyncMock(return_value=1)
        mock.exists = AsyncMock(return_value=0)
        mock.incr = AsyncMock(return_value=1)
        mock.flushdb = AsyncMock()
        mock.close = AsyncMock()
        return mock

    @pytest.fixture
    def cache_with_redis(self, mock_redis):
        """Create cache service with mocked Redis"""
        service = CacheService()
        service.redis = mock_redis
        service._is_redis_available = True
        return service

    @pytest.fixture
    def cache_memory_only(self):
        """Create cache service with memory only"""
        service = CacheService()
        service.redis = None
        service._is_redis_available = False
        return service

    def test_initialization_without_redis(self, monkeypatch):
        """Test cache initializes correctly when Redis unavailable"""
        monkeypatch.setenv("REDIS_URL", "")
        service = CacheService()
        assert service.redis is None
        assert not service.is_redis_available()
        assert service._memory_cache == {}

    @pytest.mark.asyncio
    async def test_initialization_with_redis(self, monkeypatch):
        """Test cache initializes with Redis when available"""
        monkeypatch.setenv("REDIS_URL", "redis://localhost:6379")
        
        with patch("redis.asyncio.from_url") as mock_from_url:
            mock_client = AsyncMock()
            mock_client.ping = AsyncMock(return_value=True)
            mock_from_url.return_value = mock_client
            
            service = CacheService()
            await asyncio.sleep(0.1)  # Let initialization complete
            
            assert service.redis is not None
            mock_from_url.assert_called_once()

    def test_memory_cache_operations(self, cache_memory_only):
        """Test memory cache basic operations"""
        # Set and get
        assert cache_memory_only.set("key1", "value1") is True
        assert cache_memory_only.get("key1") == "value1"
        
        # Exists
        assert cache_memory_only.exists("key1") is True
        assert cache_memory_only.exists("nonexistent") is False
        
        # Delete
        assert cache_memory_only.delete("key1") is True
        assert cache_memory_only.exists("key1") is False
        
        # Increment
        cache_memory_only.set("counter", 5)
        assert cache_memory_only.increment("counter", 3) == 8
        assert cache_memory_only.increment("new_counter") == 1

    def test_memory_cache_ttl(self, cache_memory_only):
        """Test memory cache TTL functionality"""
        # Set with TTL
        cache_memory_only.set("expiring", "value", ttl=1)
        assert cache_memory_only.get("expiring") == "value"
        
        # Wait for expiration
        time.sleep(1.1)
        assert cache_memory_only.get("expiring") is None
        
        # Test ignore_ttl parameter
        cache_memory_only.set("expiring2", "value2", ttl=1)
        time.sleep(1.1)
        assert cache_memory_only.get("expiring2", ignore_ttl=True) == "value2"

    @pytest.mark.asyncio
    async def test_redis_operations(self, cache_with_redis, mock_redis):
        """Test Redis-backed operations"""
        # Async set
        assert await cache_with_redis.aset("key1", "value1") is True
        mock_redis.set.assert_called_with("key1", "value1", ex=None)
        
        # Async get
        mock_redis.get.return_value = b"value1"
        assert await cache_with_redis.aget("key1") == "value1"
        
        # Async exists
        mock_redis.exists.return_value = 1
        assert await cache_with_redis.aexists("key1") is True
        
        # Async delete
        assert await cache_with_redis.adelete("key1") is True
        mock_redis.delete.assert_called_with("key1")

    @pytest.mark.asyncio
    async def test_redis_fallback_to_memory(self, cache_with_redis, mock_redis):
        """Test fallback to memory cache when Redis fails"""
        # Make Redis operations fail
        mock_redis.set.side_effect = Exception("Redis error")
        mock_redis.get.side_effect = Exception("Redis error")
        
        # Should fall back to memory cache
        assert await cache_with_redis.aset("key1", "value1") is True
        assert await cache_with_redis.aget("key1") == "value1"
        
        # Check stats
        stats = cache_with_redis.get_stats()
        assert stats["errors"] > 0
        assert stats["memory_fallbacks"] > 0

    @pytest.mark.asyncio
    async def test_json_operations(self, cache_memory_only):
        """Test JSON serialization operations"""
        prefix = "test"
        data = {"id": 123, "name": "test"}
        payload = {"result": "success", "items": [1, 2, 3]}
        
        # Set JSON
        assert await cache_memory_only.set_json(prefix, data, payload) is True
        
        # Get JSON
        retrieved = await cache_memory_only.get_json(prefix, data)
        assert retrieved == payload
        
        # Exists JSON
        assert await cache_memory_only.exists_json(prefix, data) is True
        
        # Delete JSON
        assert await cache_memory_only.delete_json(prefix, data) is True
        assert await cache_memory_only.exists_json(prefix, data) is False

    def test_clear_pattern(self, cache_memory_only):
        """Test pattern-based cache clearing"""
        # Set multiple keys
        cache_memory_only.set("user:1:profile", "data1")
        cache_memory_only.set("user:1:settings", "data2")
        cache_memory_only.set("user:2:profile", "data3")
        cache_memory_only.set("post:1", "data4")
        
        # Clear pattern
        deleted = cache_memory_only.clear_pattern("user:1:*")
        assert deleted == 2
        assert not cache_memory_only.exists("user:1:profile")
        assert not cache_memory_only.exists("user:1:settings")
        assert cache_memory_only.exists("user:2:profile")
        assert cache_memory_only.exists("post:1")

    def test_get_stats(self, cache_memory_only):
        """Test cache statistics tracking"""
        # Initial stats
        stats = cache_memory_only.get_stats()
        assert stats["hits"] == 0
        assert stats["misses"] == 0
        
        # Generate some stats
        cache_memory_only.set("key1", "value1")
        cache_memory_only.get("key1")  # Hit
        cache_memory_only.get("key2")  # Miss
        
        stats = cache_memory_only.get_stats()
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert stats["hit_rate"] == 0.5

    def test_cleanup_memory_cache(self, cache_memory_only):
        """Test memory cache cleanup of expired entries"""
        # Set entries with different TTLs
        cache_memory_only.set("keep", "value", ttl=10)
        cache_memory_only.set("expire1", "value", ttl=0.1)
        cache_memory_only.set("expire2", "value", ttl=0.1)
        
        # Wait for expiration
        time.sleep(0.2)
        
        # Cleanup
        cache_memory_only._cleanup_memory_cache()
        
        # Check results
        assert cache_memory_only.exists("keep")
        assert not cache_memory_only.exists("expire1")
        assert not cache_memory_only.exists("expire2")

    @pytest.mark.asyncio
    async def test_close(self, cache_with_redis, mock_redis):
        """Test cache service cleanup"""
        await cache_with_redis.close()
        mock_redis.close.assert_called_once()


class TestCacheDecorator:
    """Test @cached decorator functionality"""

    @pytest.fixture
    def cache_service(self):
        """Get cache service instance"""
        service = CacheService()
        service.redis = None
        service._is_redis_available = False
        service._memory_cache.clear()
        return service

    def test_cached_sync_function(self, cache_service, monkeypatch):
        """Test @cached decorator with sync function"""
        monkeypatch.setattr("app.services.cache_service.cache_service", cache_service)
        
        call_count = 0
        
        @cached(prefix="test")
        def expensive_function(x, y):
            nonlocal call_count
            call_count += 1
            return x + y
        
        # First call - should execute
        result1 = expensive_function(1, 2)
        assert result1 == 3
        assert call_count == 1
        
        # Second call - should use cache
        result2 = expensive_function(1, 2)
        assert result2 == 3
        assert call_count == 1  # Not incremented
        
        # Different args - should execute
        result3 = expensive_function(2, 3)
        assert result3 == 5
        assert call_count == 2

    @pytest.mark.asyncio
    async def test_cached_async_function(self, cache_service, monkeypatch):
        """Test @cached decorator with async function"""
        monkeypatch.setattr("app.services.cache_service.cache_service", cache_service)
        
        call_count = 0
        
        @cached(prefix="async_test")
        async def async_expensive_function(x):
            nonlocal call_count
            call_count += 1
            await asyncio.sleep(0.01)
            return x * 2
        
        # First call
        result1 = await async_expensive_function(5)
        assert result1 == 10
        assert call_count == 1
        
        # Cached call
        result2 = await async_expensive_function(5)
        assert result2 == 10
        assert call_count == 1

    def test_cached_with_ttl(self, cache_service, monkeypatch):
        """Test @cached decorator with TTL"""
        monkeypatch.setattr("app.services.cache_service.cache_service", cache_service)
        
        call_count = 0
        
        @cached(prefix="ttl_test", ttl=1)
        def short_lived_function():
            nonlocal call_count
            call_count += 1
            return call_count
        
        # First call
        assert short_lived_function() == 1
        
        # Cached call
        assert short_lived_function() == 1
        
        # After TTL expires
        time.sleep(1.1)
        assert short_lived_function() == 2


class TestCacheSingleton:
    """Test cache service singleton pattern"""

    def test_get_cache_service_singleton(self):
        """Test get_cache_service returns same instance"""
        service1 = get_cache_service()
        service2 = get_cache_service()
        assert service1 is service2

    @pytest.mark.asyncio
    async def test_close_cache_service(self):
        """Test close_cache_service cleanup"""
        from app.services.cache_service import close_cache_service
        
        service = get_cache_service()
        mock_redis = AsyncMock()
        service.redis = mock_redis
        
        await close_cache_service()
        
        # Should have called close if Redis was available
        if service.redis:
            mock_redis.close.assert_called_once()


class TestCacheIntegrationScenarios:
    """Test real-world cache usage scenarios"""

    @pytest.fixture
    def cache_service(self):
        """Get clean cache service"""
        service = CacheService()
        service.redis = None
        service._is_redis_available = False
        service._memory_cache.clear()
        service._stats = {"hits": 0, "misses": 0, "errors": 0, "memory_fallbacks": 0}
        return service

    def test_orchestration_response_caching(self, cache_service):
        """Test caching pattern used in orchestration service"""
        # Simulate orchestration caching
        query = "What is AI?"
        models = ["gpt-4", "claude-3"]
        
        # Create cache key like orchestration does
        key = cache_key("orchestration", {"query": query, "models": sorted(models)})
        
        # Cache miss
        cached_response = cache_service.get(key)
        assert cached_response is None
        
        # Store response
        response = {
            "initial_response": {"output": "AI is..."},
            "peer_review": {"reviews": []},
            "ultra_synthesis": {"synthesis": "Comprehensive AI explanation"}
        }
        cache_service.set(key, json.dumps(response), ttl=300)
        
        # Cache hit
        cached_response = cache_service.get(key)
        assert cached_response is not None
        assert json.loads(cached_response)["ultra_synthesis"]["synthesis"] == "Comprehensive AI explanation"

    @pytest.mark.asyncio
    async def test_concurrent_cache_access(self, cache_service):
        """Test cache under concurrent access"""
        async def cache_operation(i):
            key = f"concurrent:{i % 5}"  # Use 5 keys repeatedly
            await cache_service.aset(key, f"value{i}")
            result = await cache_service.aget(key)
            return result
        
        # Run 20 concurrent operations
        tasks = [cache_operation(i) for i in range(20)]
        results = await asyncio.gather(*tasks)
        
        # All operations should complete successfully
        assert len(results) == 20
        assert all(r is not None for r in results)

    def test_cache_size_limits(self, cache_service):
        """Test cache behavior with many entries"""
        # Add many entries
        for i in range(1000):
            cache_service.set(f"key{i}", f"value{i}")
        
        # Should handle large cache gracefully
        assert cache_service.get("key0") == "value0"
        assert cache_service.get("key999") == "value999"
        
        # Cleanup should work
        assert cache_service.flush() is True
        assert len(cache_service._memory_cache) == 0