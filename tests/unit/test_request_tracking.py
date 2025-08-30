"""
Unit tests for request ID tracking functionality.

This module tests the request tracking middleware and integration
with the orchestration service.
"""

import pytest
import uuid
from unittest.mock import Mock, patch, AsyncMock
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from app.middleware.request_id_middleware import RequestIDMiddleware
from app.middleware.request_tracking_middleware import RequestTrackingMiddleware, RequestIDInjector
from app.utils.logging import CorrelationContext
from app.services.tracked_orchestration_service import TrackedOrchestrationService
from app.services.tracked_llm_adapters import TrackedOpenAIAdapter, TRACKED_CLIENT


@pytest.fixture
def test_app():
    """Create a test FastAPI app with request tracking."""
    app = FastAPI()
    
    # Add request ID middleware
    app.add_middleware(RequestIDMiddleware)
    
    @app.get("/test")
    async def test_endpoint(request: Request):
        return {
            "request_id": getattr(request.state, "request_id", None),
            "correlation_id": getattr(request.state, "correlation_id", None)
        }
    
    return app


@pytest.fixture
def client(test_app):
    """Create test client."""
    return TestClient(test_app)


class TestRequestIDMiddleware:
    """Test request ID middleware functionality."""
    
    def test_generates_request_id(self, client):
        """Test that middleware generates request ID when not provided."""
        response = client.get("/test")
        
        assert response.status_code == 200
        assert "X-Request-ID" in response.headers
        assert response.headers["X-Request-ID"].startswith("req_")
        
        data = response.json()
        assert data["request_id"] == response.headers["X-Request-ID"]
    
    def test_preserves_existing_request_id(self, client):
        """Test that middleware preserves existing request ID."""
        request_id = "existing-request-123"
        response = client.get("/test", headers={"X-Request-ID": request_id})
        
        assert response.status_code == 200
        assert response.headers["X-Request-ID"] == request_id
        
        data = response.json()
        assert data["request_id"] == request_id
    
    def test_correlation_id_handling(self, client):
        """Test correlation ID handling."""
        request_id = "req-123"
        correlation_id = "corr-456"
        
        response = client.get(
            "/test",
            headers={
                "X-Request-ID": request_id,
                "X-Correlation-ID": correlation_id
            }
        )
        
        assert response.status_code == 200
        assert response.headers["X-Correlation-ID"] == correlation_id
        
        data = response.json()
        assert data["correlation_id"] == correlation_id
    
    def test_uses_request_id_as_correlation_fallback(self, client):
        """Test that request ID is used as correlation ID when not provided."""
        request_id = "req-789"
        
        response = client.get("/test", headers={"X-Request-ID": request_id})
        
        assert response.status_code == 200
        assert response.headers["X-Correlation-ID"] == request_id
        
        data = response.json()
        assert data["correlation_id"] == request_id


class TestRequestIDInjector:
    """Test request ID injector functionality."""
    
    def test_inject_headers(self):
        """Test header injection."""
        headers = {"Content-Type": "application/json"}
        
        updated = RequestIDInjector.inject_headers(
            headers,
            request_id="req-123",
            correlation_id="corr-456"
        )
        
        assert updated["X-Request-ID"] == "req-123"
        assert updated["X-Correlation-ID"] == "corr-456"
        assert updated["Content-Type"] == "application/json"
    
    def test_from_request(self):
        """Test extracting IDs from request."""
        request = Mock(spec=Request)
        request.state = Mock()
        request.state.request_id = "req-123"
        request.state.correlation_id = "corr-456"
        
        headers = {}
        updated = RequestIDInjector.from_request(request, headers)
        
        assert updated["X-Request-ID"] == "req-123"
        assert updated["X-Correlation-ID"] == "corr-456"


class TestTrackedOrchestrationService:
    """Test tracked orchestration service."""
    
    @pytest.fixture
    def mock_dependencies(self):
        """Create mock dependencies."""
        return {
            "model_registry": Mock(),
            "quality_evaluator": Mock(),
            "rate_limiter": Mock()
        }
    
    @pytest.fixture
    def tracked_service(self, mock_dependencies):
        """Create tracked orchestration service."""
        return TrackedOrchestrationService(**mock_dependencies)
    
    def test_set_request_context(self, tracked_service):
        """Test setting request context."""
        request = Mock(spec=Request)
        request.state = Mock()
        request.state.request_id = "req-123"
        request.state.correlation_id = "corr-456"
        
        tracked_service.set_request_context(request)
        
        assert tracked_service._current_request_id == "req-123"
        assert tracked_service._current_correlation_id == "corr-456"
    
    @pytest.mark.asyncio
    async def test_create_adapter_with_tracking(self, tracked_service):
        """Test adapter creation includes tracking."""
        tracked_service._current_request_id = "req-123"
        tracked_service._current_correlation_id = "corr-456"
        
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
            adapter, model = tracked_service._create_adapter("gpt-4")
            
            assert adapter is not None
            assert isinstance(adapter, TrackedOpenAIAdapter)
            assert adapter._request_id == "req-123"
            assert adapter._correlation_id == "corr-456"


class TestTrackedLLMAdapters:
    """Test tracked LLM adapter functionality."""
    
    @pytest.mark.asyncio
    async def test_tracked_adapter_logging(self):
        """Test that tracked adapter logs requests with IDs."""
        # Create mock base adapter
        mock_adapter = Mock()
        mock_adapter.model = "gpt-4"
        mock_adapter.generate = AsyncMock(return_value={"generated_text": "Test response"})
        
        # Create tracked adapter
        from app.services.tracked_llm_adapters import TrackedLLMAdapter
        tracked = TrackedLLMAdapter(mock_adapter)
        tracked.set_tracking_ids("req-123", "corr-456")
        
        # Generate response
        result = await tracked.generate("Test prompt")
        
        assert result["generated_text"] == "Test response"
        mock_adapter.generate.assert_called_once_with("Test prompt")
    
    def test_tracked_http_client(self):
        """Test tracked HTTP client adds headers."""
        TRACKED_CLIENT.set_tracking_ids("req-123", "corr-456")
        
        # The client should now include tracking headers in all requests
        assert TRACKED_CLIENT._request_id == "req-123"
        assert TRACKED_CLIENT._correlation_id == "corr-456"


class TestCorrelationContext:
    """Test correlation context functionality."""
    
    def test_correlation_context_lifecycle(self):
        """Test setting and clearing correlation context."""
        # Initially no correlation ID
        first_id = CorrelationContext.get_correlation_id()
        assert first_id is not None
        
        # Set specific ID
        CorrelationContext.set_correlation_id("test-corr-123")
        assert CorrelationContext.get_correlation_id() == "test-corr-123"
        
        # Clear context
        CorrelationContext.clear_correlation_id()
        
        # New ID should be generated
        new_id = CorrelationContext.get_correlation_id()
        assert new_id != "test-corr-123"
        assert new_id is not None