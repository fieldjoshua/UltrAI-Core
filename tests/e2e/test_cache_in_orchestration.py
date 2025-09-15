"""
End-to-end tests for cache usage in orchestration pipeline.
"""

# flake8: noqa

import json
import os
# Set environment variables BEFORE any app imports
os.environ["TESTING"] = "true"
os.environ["JWT_SECRET_KEY"] = "test-secret-key"

from unittest.mock import AsyncMock, patch, Mock
import uuid

import pytest
from fastapi.testclient import TestClient
import httpx

from app.app import create_app

# Skip entire file due to intermittent Starlette TestClient portal deadlock
pytestmark = pytest.mark.skip(
    reason=(
        "Skip flaky TestClient-based e2e cache tests under Python 3.13/anyio; "
        "refactor to httpx.AsyncClient + ASGITransport + lifespan manager"
    )
)
from app.services.cache_service import cache_key, get_cache_service
from app.services.auth_service import AuthService


@pytest.fixture(scope="module")
def auth_token():
    """Generate a valid JWT token for testing."""
    auth_service = AuthService()
    user_id = str(uuid.uuid4())
    return auth_service.create_access_token(user_id=user_id)["access_token"]


@pytest.mark.e2e
class TestCacheInOrchestration:
    """Test cache behavior in orchestration workflow"""

    @pytest.fixture
    def client(self, mock_llm_adapters):
        """Create test client with mocked LLMs"""
        # The mock_llm_adapters fixture from conftest.py handles mocking
        app = create_app()
        return TestClient(app)

    @pytest.fixture
    def cache_service(self):
        """Get cache service and clear it"""
        service = get_cache_service()
        service.flush()
        service._stats = {"hits": 0, "misses": 0, "errors": 0, "memory_fallbacks": 0}
        return service

    def test_orchestration_caching_workflow(self, client, cache_service, auth_token):
        """Test that orchestration properly caches responses"""
        # Make first request
        request_data = {
            "query": "What is machine learning?",
            "selected_models": ["gpt-4", "claude-3-opus"],
            "options": {"temperature": 0.7}
        }
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Track cache stats before
        stats_before = cache_service.get_stats()
        initial_misses = stats_before["misses"]
        
        # First request - should be cache miss
        response1 = client.post("/api/orchestrator/analyze", json=request_data, headers=headers)
        assert response1.status_code == 200
        
        # Check cache stats after first request
        stats_after1 = cache_service.get_stats()
        assert stats_after1["misses"] > initial_misses  # Cache miss occurred
        
        # Generate expected cache key
        expected_key = cache_key(
            "orchestration",
            {
                "query": request_data["query"],
                "models": sorted(request_data["selected_models"]),
                "options": request_data["options"]
            }
        )
        
        # Verify response was cached
        cached_value = cache_service.get(expected_key)
        assert cached_value is not None
        
        # Second identical request - should be cache hit
        response2 = client.post("/api/orchestrator/analyze", json=request_data, headers=headers)
        assert response2.status_code == 200
        
        # Check cache stats after second request
        stats_after2 = cache_service.get_stats()
        assert stats_after2["hits"] > stats_after1["hits"]  # Cache hit occurred
        
        # Responses should be identical
        assert response1.json() == response2.json()

    def test_orchestration_cache_invalidation_on_different_params(self, client, cache_service, auth_token):
        """Test that different parameters generate different cache keys"""
        base_request = {
            "query": "Explain quantum computing",
            "selected_models": ["gpt-4", "claude-3-opus"],
            "options": {"temperature": 0.7}
        }
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # First request
        response1 = client.post("/api/orchestrator/analyze", json=base_request, headers=headers)
        assert response1.status_code == 200
        result1 = response1.json()
        
        # Different query - should not use cache
        different_query = base_request.copy()
        different_query["query"] = "Explain blockchain technology"
        response2 = client.post("/api/orchestrator/analyze", json=different_query, headers=headers)
        assert response2.status_code == 200
        result2 = response2.json()
        
        # Results should be different (different queries)
        assert result1["results"]["initial_response"]["output"]["responses"] != \
               result2["results"]["initial_response"]["output"]["responses"]
        
        # Different models - should not use cache
        different_models = base_request.copy()
        different_models["selected_models"] = ["gpt-4", "gemini-pro"]
        response3 = client.post("/api/orchestrator/analyze", json=different_models, headers=headers)
        assert response3.status_code == 200
        
        # Different options - should not use cache
        different_options = base_request.copy()
        different_options["options"]["temperature"] = 0.9
        response4 = client.post("/api/orchestrator/analyze", json=different_options, headers=headers)
        assert response4.status_code == 200
        
        # Check that we had multiple cache misses
        stats = cache_service.get_stats()
        assert stats["misses"] >= 4  # At least 4 different requests

    def test_orchestration_without_caching(self, client, cache_service, auth_token):
        """Test orchestration when caching is disabled"""
        request_data = {
            "query": "What is artificial intelligence?",
            "selected_models": ["gpt-4", "claude-3-opus"],
            "options": {}
        }
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        with patch("app.config.Config.ENABLE_ORCHESTRATION_CACHING", False):
            # Make two identical requests
            response1 = client.post("/api/orchestrator/analyze", json=request_data, headers=headers)
            response2 = client.post("/api/orchestrator/analyze", json=request_data, headers=headers)
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # Cache should not have been used
        stats = cache_service.get_stats()
        assert stats["hits"] == 0  # No cache hits

    def test_cache_ttl_in_orchestration(self, client, cache_service, monkeypatch, auth_token):
        """Test that cached orchestration responses expire"""
        # Set very short cache TTL
        monkeypatch.setattr("app.config.Config.CACHE_TTL_ORCHESTRATION", 1)  # 1 second
        
        request_data = {
            "query": "Explain neural networks",
            "selected_models": ["gpt-4", "claude-3-opus"],
            "options": {}
        }
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # First request
        response1 = client.post("/api/orchestrator/analyze", json=request_data, headers=headers)
        assert response1.status_code == 200
        
        # Immediate second request - should hit cache
        response2 = client.post("/api/orchestrator/analyze", json=request_data, headers=headers)
        assert response2.status_code == 200
        
        stats_before_expiry = cache_service.get_stats()
        hits_before = stats_before_expiry["hits"]
        
        # Wait for cache to expire
        import time
        time.sleep(1.5)
        
        # Third request - should miss cache (expired)
        response3 = client.post("/api/orchestrator/analyze", json=request_data, headers=headers)
        assert response3.status_code == 200
        
        stats_after_expiry = cache_service.get_stats()
        # Should have same number of hits (no new hit after expiry)
        assert stats_after_expiry["hits"] == hits_before
        assert stats_after_expiry["misses"] > stats_before_expiry["misses"]

    @pytest.mark.asyncio
    async def test_concurrent_orchestration_caching(self, client, cache_service, auth_token):
        """Test cache behavior under concurrent orchestration requests"""
        import asyncio
        
        os.environ["USE_MOCK"] = "true"
        app = create_app()
        
        async def make_request(async_client, request_id):
            request_data = {
                "query": "What is deep learning?",  # Same query for all
                "selected_models": ["gpt-4", "claude-3-opus"],
                "options": {"temperature": 0.7}
            }
            headers = {"Authorization": f"Bearer {auth_token}"}
            response = await async_client.post("/api/orchestrator/analyze", json=request_data, headers=headers)
            return response.status_code, request_id
        
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as async_client:
            # Make 10 concurrent requests with same parameters
            tasks = [make_request(async_client, i) for i in range(10)]
            results = await asyncio.gather(*tasks)
        
        # All should succeed
        assert all(status == 200 for status, _ in results)
        
        # Check cache stats
        stats = cache_service.get_stats()
        # Should have at least 1 miss (first request) and multiple hits
        assert stats["misses"] >= 1
        assert stats["hits"] >= 5  # At least some should hit cache

    def test_cache_clear_affects_orchestration(self, client, cache_service, auth_token):
        """Test that clearing cache affects orchestration"""
        request_data = {
            "query": "Explain machine learning algorithms",
            "selected_models": ["gpt-4", "claude-3-opus"],
            "options": {}
        }
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # First request - cache miss
        response1 = client.post("/api/orchestrator/analyze", json=request_data, headers=headers)
        assert response1.status_code == 200
        
        # Second request - cache hit
        response2 = client.post("/api/orchestrator/analyze", json=request_data, headers=headers)
        assert response2.status_code == 200
        
        stats_before_clear = cache_service.get_stats()
        assert stats_before_clear["hits"] > 0
        
        # Clear cache
        client.post("/api/cache/clear", json={}, headers=headers)
        
        # Third request - cache miss again
        response3 = client.post("/api/orchestrator/analyze", json=request_data, headers=headers)
        assert response3.status_code == 200
        
        # Should have more misses after cache clear
        stats_after_clear = cache_service.get_stats()
        assert stats_after_clear["misses"] > stats_before_clear["misses"]

    def test_cache_pattern_clear_orchestration(self, client, cache_service, auth_token):
        """Test pattern-based cache clearing for orchestration"""
        # Make requests with different queries
        queries = [
            "What is AI?",
            "What is ML?",
            "What is DL?"
        ]
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        for query in queries:
            request_data = {
                "query": query,
                "selected_models": ["gpt-4", "claude-3-opus"],
                "options": {}
            }
            response = client.post("/api/orchestrator/analyze", json=request_data, headers=headers)
            assert response.status_code == 200
        
        # Clear only orchestration cache
        result = client.post("/api/cache/clear", json={"pattern": "orchestration:*"}, headers=headers)
        assert result.status_code == 200
        
        # All orchestration entries should be cleared
        cleared_count = result.json()["cleared"]
        assert cleared_count >= len(queries)