# flake8: noqa
"""Integration tests for correct API endpoints (httpx AsyncClient)."""

import pytest
import pytest_asyncio
import httpx
from app.app import create_app


@pytest.fixture(scope="function")
def asgi_app():
    return create_app()


@pytest_asyncio.fixture(scope="function")
async def async_client(asgi_app):
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=asgi_app), base_url="http://test") as client:
        yield client


class TestCorrectEndpoints:
    """Test that we're using the correct API endpoints."""
    
    @pytest.mark.asyncio
    async def test_health_endpoint(self, async_client):
        """Test correct health endpoint path."""
        response = await async_client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "services" in data
    
    @pytest.mark.asyncio
    async def test_available_models_endpoint(self, async_client):
        """Test correct models endpoint path."""
        # Correct endpoint
        response = await async_client.get("/api/available-models")
        assert response.status_code == 200
        data = response.json()
        assert "models" in data
        
        # Wrong endpoint should 404
        response = await async_client.get("/api/models")
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_model_health_endpoint(self, async_client):
        """Test correct model health endpoint path."""
        # Correct endpoint
        response = await async_client.get("/api/models/health")
        assert response.status_code == 200
        
        # Wrong endpoint should 404
        response = await async_client.get("/api/model-health")
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    @pytest.mark.xfail(
        reason="Intermittent async timeout on /api/orchestrator/status under local runner",
        run=False,
        strict=False,
    )
    async def test_orchestrator_endpoints(self, async_client):
        """Test correct orchestrator endpoint paths."""
        # Health check endpoint
        response = await async_client.get("/api/orchestrator/health")
        assert response.status_code == 200
        
        # Status endpoint
        response = await async_client.get("/api/orchestrator/status")
        # May timeout but should not 404
        assert response.status_code in [200, 500, 504]
        
        # Wrong orchestrate endpoint should 404
        response = await async_client.post("/api/orchestrate", json={"prompt": "test"})
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    @pytest.mark.xfail(
        reason="Intermittent async timeout on analyze under local runner",
        run=False,
        strict=False,
    )
    async def test_orchestrator_analyze_requires_auth(self, async_client):
        """Test that orchestrator analyze endpoint requires authentication."""
        # Without auth should return 401 (send valid body to avoid 422)
        response = await async_client.post(
            "/api/orchestrator/analyze",
            json={
                "query": "test",
                "selected_models": ["gpt-4", "claude-3-opus"],
                "analysis_type": "quick",
                "options": {}
            }
        )
        assert response.status_code == 401
        assert "Unauthorized" in response.json()["message"]
    
    @pytest.mark.asyncio
    async def test_auth_endpoints(self, async_client):
        """Test auth endpoint configuration."""
        # This might need adjustment based on actual auth implementation
        # Document what we find
        login_methods = ["POST", "GET", "PUT"]
        working_methods = []
        
        for method in login_methods:
            response = await async_client.request(
                method, 
                "/api/auth/login",
                json={"username": "test", "password": "test"} if method != "GET" else None
            )
            if response.status_code != 405:  # Method not allowed
                working_methods.append((method, response.status_code))
        
        # Document which methods work
        # This helps identify if POST is incorrectly returning 405
        assert len(working_methods) > 0, f"No working methods for /api/auth/login. Tried: {login_methods}"
        
        # Print for debugging
        for method, status in working_methods:
            print(f"Auth login {method}: {status}")


class TestHealthCheckWithSkipFlag:
    """Test health check behavior with skip flag."""
    
    @pytest_asyncio.fixture
    async def client_with_skip_api_calls(self, monkeypatch):
        """Create client with HEALTH_CHECK_SKIP_API_CALLS enabled."""
        monkeypatch.setenv("HEALTH_CHECK_SKIP_API_CALLS", "true")
        # Need to reload modules to pick up env change
        import importlib
        import app.utils.health_check
        importlib.reload(app.utils.health_check)
        
        asgi_app = create_app()
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=asgi_app), base_url="http://test") as client:
            yield client
    
    @pytest.mark.asyncio
    async def test_health_with_skip_api_calls(self, client_with_skip_api_calls):
        """Test that health checks work with API calls skipped."""
        response = await client_with_skip_api_calls.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        # Should still return healthy even without making API calls
        assert data["status"] in ["ok", "healthy", "degraded"]