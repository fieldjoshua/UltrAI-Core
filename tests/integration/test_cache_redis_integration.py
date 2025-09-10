"""
Integration tests for cache service with Redis.
"""

import asyncio
import os
import time
from unittest.mock import patch, MagicMock

import pytest
import redis.asyncio as redis

from app.services.cache_service import CacheService, get_cache_service
from fastapi.testclient import TestClient
from app.app import create_app
from app.services.auth_service import AuthService


@pytest.mark.integration
class TestCacheRedisIntegration:
    """Test cache service integration with Redis"""

    @pytest.fixture
    async def redis_client(self):
        """Get Redis client for testing"""
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/1")
        client = redis.from_url(redis_url, decode_responses=True)
        try:
            await client.ping()
            yield client
        except Exception:
            pytest.skip("Redis not available for integration tests")
        finally:
            await client.aclose()

    @pytest.fixture
    async def cache_with_real_redis(self, redis_client):
        """Create cache service with real Redis"""
        # Use test database
        os.environ["REDIS_URL"] = os.getenv("REDIS_URL", "redis://localhost:6379/1")
        service = CacheService()
        # Wait for Redis initialization
        await asyncio.sleep(0.1)
        
        # Clear test database
        if service.redis:
            await service.redis.flushdb()
        
        yield service
        
        # Cleanup
        if service.redis:
            await service.redis.flushdb()
        await service.close()

    @pytest.mark.asyncio
    @pytest.mark.skipif(not os.getenv("REDIS_URL"), reason="Redis URL not configured")
    async def test_redis_connection_and_operations(self, cache_with_real_redis):
        """Test real Redis connection and operations"""
        if not cache_with_real_redis.is_redis_available():
            pytest.skip("Redis not available")
        
        # Test basic operations
        assert await cache_with_real_redis.aset("test_key", "test_value") is True
        assert await cache_with_real_redis.aget("test_key") == "test_value"
        assert await cache_with_real_redis.aexists("test_key") is True
        assert await cache_with_real_redis.adelete("test_key") is True
        assert await cache_with_real_redis.aexists("test_key") is False

    @pytest.mark.asyncio
    @pytest.mark.skipif(not os.getenv("REDIS_URL"), reason="Redis URL not configured")
    async def test_redis_ttl_expiration(self, cache_with_real_redis):
        """Test TTL expiration in Redis"""
        if not cache_with_real_redis.is_redis_available():
            pytest.skip("Redis not available")
        
        # Set with short TTL
        await cache_with_real_redis.aset("expiring_key", "value", ttl=1)
        assert await cache_with_real_redis.aget("expiring_key") == "value"
        
        # Wait for expiration
        await asyncio.sleep(1.5)
        assert await cache_with_real_redis.aget("expiring_key") is None

    @pytest.mark.asyncio
    @pytest.mark.skipif(not os.getenv("REDIS_URL"), reason="Redis URL not configured")
    async def test_redis_increment_operations(self, cache_with_real_redis):
        """Test increment operations in Redis"""
        if not cache_with_real_redis.is_redis_available():
            pytest.skip("Redis not available")
        
        # Increment non-existent key
        assert await cache_with_real_redis.aincrement("counter") == 1
        assert await cache_with_real_redis.aincrement("counter", 5) == 6
        
        # Verify value
        assert await cache_with_real_redis.aget("counter") == "6"

    @pytest.mark.asyncio
    @pytest.mark.skipif(not os.getenv("REDIS_URL"), reason="Redis URL not configured")
    async def test_redis_pattern_operations(self, cache_with_real_redis):
        """Test pattern-based operations in Redis"""
        if not cache_with_real_redis.is_redis_available():
            pytest.skip("Redis not available")
        
        # Set multiple keys
        await cache_with_real_redis.aset("user:1:name", "Alice")
        await cache_with_real_redis.aset("user:1:email", "alice@example.com")
        await cache_with_real_redis.aset("user:2:name", "Bob")
        await cache_with_real_redis.aset("post:1:title", "Hello")
        
        # Clear pattern
        deleted = await cache_with_real_redis.clear_pattern("user:1:*")
        assert deleted >= 2
        
        # Verify deletion
        assert await cache_with_real_redis.aget("user:1:name") is None
        assert await cache_with_real_redis.aget("user:1:email") is None
        assert await cache_with_real_redis.aget("user:2:name") == "Bob"
        assert await cache_with_real_redis.aget("post:1:title") == "Hello"

    @pytest.mark.asyncio
    @pytest.mark.skipif(not os.getenv("REDIS_URL"), reason="Redis URL not configured")
    async def test_redis_json_operations(self, cache_with_real_redis):
        """Test JSON serialization with Redis"""
        if not cache_with_real_redis.is_redis_available():
            pytest.skip("Redis not available")
        
        # Complex JSON data
        data = {
            "query": "test query",
            "models": ["gpt-4", "claude-3"],
            "options": {"temperature": 0.7, "max_tokens": 1000}
        }
        
        result = {
            "responses": [
                {"model": "gpt-4", "text": "Response 1"},
                {"model": "claude-3", "text": "Response 2"}
            ],
            "metadata": {"timestamp": time.time()}
        }
        
        # Store and retrieve
        assert await cache_with_real_redis.set_json("analysis", data, result) is True
        retrieved = await cache_with_real_redis.get_json("analysis", data)
        assert retrieved["responses"][0]["model"] == "gpt-4"
        assert len(retrieved["responses"]) == 2

    @pytest.mark.asyncio
    @pytest.mark.skipif(not os.getenv("REDIS_URL"), reason="Redis URL not configured")
    async def test_redis_fallback_on_connection_loss(self, cache_with_real_redis):
        """Test fallback to memory when Redis connection is lost"""
        if not cache_with_real_redis.is_redis_available():
            pytest.skip("Redis not available")
        
        # Set value in Redis
        await cache_with_real_redis.aset("persistent_key", "redis_value")
        
        # Simulate connection loss
        original_redis = cache_with_real_redis.redis
        cache_with_real_redis.redis = None
        cache_with_real_redis._is_redis_available = False
        
        # Should fall back to memory cache
        assert await cache_with_real_redis.aset("memory_key", "memory_value") is True
        assert await cache_with_real_redis.aget("memory_key") == "memory_value"
        
        # Stats should show fallbacks
        stats = cache_with_real_redis.get_stats()
        assert stats["memory_fallbacks"] > 0
        
        # Restore Redis
        cache_with_real_redis.redis = original_redis
        cache_with_real_redis._is_redis_available = True

    @pytest.mark.asyncio
    @pytest.mark.skipif(not os.getenv("REDIS_URL"), reason="Redis URL not configured")
    async def test_redis_concurrent_operations(self, cache_with_real_redis):
        """Test concurrent operations with Redis"""
        if not cache_with_real_redis.is_redis_available():
            pytest.skip("Redis not available")
        
        async def concurrent_increment(key, count):
            results = []
            for _ in range(count):
                result = await cache_with_real_redis.aincrement(key)
                results.append(result)
            return results
        
        # Run concurrent increments
        key = "concurrent_counter"
        tasks = [concurrent_increment(key, 10) for _ in range(5)]
        all_results = await asyncio.gather(*tasks)
        
        # Flatten results
        all_values = [val for results in all_results for val in results]
        
        # Should have all unique values from 1 to 50
        assert len(set(all_values)) == 50
        assert min(all_values) >= 1
        assert max(all_values) == 50

    @pytest.mark.asyncio
    @pytest.mark.skipif(not os.getenv("REDIS_URL"), reason="Redis URL not configured")
    async def test_redis_performance_comparison(self, cache_with_real_redis):
        """Compare performance of Redis vs memory cache"""
        if not cache_with_real_redis.is_redis_available():
            pytest.skip("Redis not available")
        
        # Test Redis performance
        redis_start = time.time()
        for i in range(100):
            await cache_with_real_redis.aset(f"redis_key_{i}", f"value_{i}")
            await cache_with_real_redis.aget(f"redis_key_{i}")
        redis_time = time.time() - redis_start
        
        # Switch to memory only
        cache_with_real_redis._is_redis_available = False
        
        # Test memory performance
        memory_start = time.time()
        for i in range(100):
            cache_with_real_redis.set(f"memory_key_{i}", f"value_{i}")
            cache_with_real_redis.get(f"memory_key_{i}")
        memory_time = time.time() - memory_start
        
        # Memory should be significantly faster for small operations
        assert memory_time < redis_time
        
        # Restore Redis
        cache_with_real_redis._is_redis_available = True


@pytest.fixture(scope="module")
def admin_token():
    """Generate a token for an admin user."""
    auth_service = AuthService()
    # In a real app, you'd fetch an admin user from the DB
    # For tests, we can create a dummy admin identity
    token_data = auth_service.create_access_token(user_id=1)
    return token_data["access_token"]

@pytest.mark.integration
class TestCacheRouteIntegration:
    """Test cache-related API routes"""

    @pytest.fixture
    def mock_cache_service(self):
        """Fixture to mock the cache service."""
        mock_service = MagicMock(spec=CacheService)
        mock_service.get_stats.return_value = {
            "hits": 10,
            "misses": 5,
            "hit_rate": 0.66,
            "memory_size": 1,
            "redis_size": 0,
            "errors": 0,
            "memory_fallbacks": 0,
        }
        mock_service.is_redis_available.return_value = True
        mock_service.memory_cache = {"key": "value"}
        
        async def mock_clear_pattern(pattern):
            return 5

        async def mock_flush():
            pass

        mock_service.clear_pattern = MagicMock(side_effect=mock_clear_pattern)
        mock_service.flush = MagicMock(side_effect=mock_flush)
        
        with patch("app.routes.cache_routes.get_cache_service", return_value=mock_service) as mock:
            yield mock_service

    @pytest.fixture
    def client(self, admin_token):
        """Create test client with admin auth."""
        os.environ["TESTING"] = "true"
        os.environ["JWT_SECRET_KEY"] = "test-secret"
        app = create_app()
        
        client = TestClient(app)
        client.headers["Authorization"] = f"Bearer {admin_token}"
        return client

    def test_cache_stats_endpoint(self, client, mock_cache_service):
        """Test /cache/stats endpoint"""
        response = client.get("/cache/stats")
        assert response.status_code == 200
        
        data = response.json()
        assert "stats" in data
        assert "hits" in data["stats"]
        assert "misses" in data["stats"]
        assert "hit_rate" in data["stats"]
        mock_cache_service.get_stats.assert_called_once()

    def test_cache_health_endpoint(self, client, mock_cache_service):
        """Test /cache/health endpoint"""
        response = client.get("/cache/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["healthy"] is True
        assert data["redis_available"] is True
        assert data["memory_cache_size"] == 1
        mock_cache_service.is_redis_available.assert_called_once()

    def test_cache_clear_endpoint(self, client, mock_cache_service):
        """Test /cache/clear endpoint"""
        response = client.post("/cache/clear", json={"pattern": "test:*"})
        assert response.status_code == 200
        
        data = response.json()
        assert data["cleared"] == 5
        assert data["pattern"] == "test:*"
        mock_cache_service.clear_pattern.assert_called_once_with("test:*")
        
        # Test without pattern (clears all)
        response = client.post("/cache/clear", json={})
        assert response.status_code == 200
        mock_cache_service.flush.assert_called_once()