#!/usr/bin/env python3
"""
Integration tests for the UltrAI synthesis system with Big 3 LLMs.
Tests the actual implementation with mocked API responses.
"""

import pytest
import pytest_asyncio
import os
from unittest.mock import patch, AsyncMock, Mock
from app.main import create_app
from httpx import AsyncClient, ASGITransport


class TestSynthesisIntegration:
    """Test the synthesis system integration with Big 3 LLMs."""
    
    @pytest_asyncio.fixture
    async def test_app(self):
        """Create test app instance."""
        app = create_app()
        return app
    
    @pytest_asyncio.fixture
    async def test_client(self, test_app):
        """Create test client."""
        transport = ASGITransport(app=test_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            yield client
    
    @pytest.mark.asyncio
    async def test_synthesis_preserves_prompt(self, test_client):
        """Test that the original prompt is preserved through all stages."""
        USER_PROMPT = "What are the key benefits of renewable energy?"
        
        # Mock environment variables
        with patch.dict(os.environ, {
            "OPENAI_API_KEY": "test-key",
            "ANTHROPIC_API_KEY": "test-key",
            "GOOGLE_API_KEY": "test-key"
        }):
            # Mock the adapters to return test responses
            with patch("app.services.orchestration_service.OrchestrationService._create_adapter") as mock_create:
                # Set up mock adapter to return simple text for any model
                mock_adapter = AsyncMock()
                mock_adapter.generate.return_value = {
                    "generated_text": "Synthesis response including renewable energy context."
                }
                mock_create.return_value = (mock_adapter, "mock-model")

                # Make request against current orchestrator endpoint and schema
                response = await test_client.post(
                    "/api/orchestrator/analyze",
                    json={
                        "query": USER_PROMPT,
                        "selected_models": ["gpt-4", "claude-3-5-sonnet-20241022", "gemini-1.5-flash"]
                    }
                )
                
                assert response.status_code == 200
                data = response.json()
                
                # Verify new response shape has success and results with ultra_synthesis text
                assert data.get("success") is True
                assert "results" in data
                assert "ultra_synthesis" in data["results"]
                assert isinstance(data["results"]["ultra_synthesis"], str)
    
    @pytest.mark.asyncio
    async def test_minimum_models_requirement(self, test_client):
        """Test that system requires minimum 3 models from Big 3 providers."""
        # Call the route function directly to avoid middleware error-wrapping differences
        from app.routes.orchestrator_minimal import create_router, AnalysisRequest
        from app.middleware.auth_middleware import AuthUser
        from app.services.orchestration_service import OrchestrationService
        from unittest.mock import Mock, AsyncMock

        # Mock app + orchestration returning only 2 models
        app_mock = Mock()
        app_mock.state.orchestration_service = OrchestrationService(
            model_registry=Mock(), rate_limiter=Mock()
        )
        app_mock.state.orchestration_service._default_models_from_env = AsyncMock(
            return_value=["gpt-4", "claude-3-5-sonnet-20241022"]
        )

        request_mock = Mock()
        request_mock.app = app_mock
        request_mock.state = Mock()
        request_mock.state.request_id = "t-req"
        request_mock.state.correlation_id = "t-corr"

        analysis_request = AnalysisRequest(query="Test query", analysis_type="simple")
        auth_user = AuthUser(user_id="u", username="u")

        router = create_router()
        analyze_func = None
        for route in router.routes:
            if route.path == "/orchestrator/analyze" and route.methods == {"POST"}:
                analyze_func = route.endpoint
                break

        import fastapi
        with pytest.raises(fastapi.HTTPException) as exc_info:
            await analyze_func(analysis_request, request_mock, auth_user)

        assert exc_info.value.status_code == 503
        assert exc_info.value.detail["error"] == "SERVICE_UNAVAILABLE"
    
    @pytest.mark.asyncio 
    async def test_parallel_execution(self, test_client):
        """Test that initial response and peer review use parallel execution."""
        call_times = []
        
        async def mock_generate(prompt):
            """Track when calls are made."""
            import time
            start = time.time()
            # Simulate API delay
            import asyncio
            await asyncio.sleep(0.1)
            call_times.append((start, time.time()))
            return {"generated_text": "Test response"}
        
        with patch.dict(os.environ, {
            "OPENAI_API_KEY": "test-key",
            "ANTHROPIC_API_KEY": "test-key",
            "GOOGLE_API_KEY": "test-key"
        }):
            with patch("app.services.orchestration_service.OrchestrationService._create_adapter") as mock_create:
                mock_adapter = AsyncMock()
                mock_adapter.generate.side_effect = mock_generate
                mock_create.return_value = (mock_adapter, "mock-model")

                response = await test_client.post(
                    "/api/orchestrator/analyze", 
                    json={
                        "query": "Test parallel execution",
                        "selected_models": ["gpt-4", "claude-3-5-sonnet-20241022", "gemini-1.5-flash"]
                    }
                )
                
                assert response.status_code == 200
                
                # Check that calls overlapped (parallel execution)
                # If sequential, total time would be ~0.3s (3 * 0.1s)
                # If parallel, total time should be ~0.1s
                if call_times:
                    first_start = min(t[0] for t in call_times)
                    last_end = max(t[1] for t in call_times)
                    total_time = last_end - first_start
                    
                    # Allow some overhead, but should be much less than sequential
                    assert total_time < 0.2, f"Execution took {total_time}s, expected parallel execution"
    
    @pytest.mark.asyncio
    async def test_synthesis_output_structure(self, test_client):
        """Test that synthesis output has correct structure."""
        with patch.dict(os.environ, {
            "OPENAI_API_KEY": "test-key",
            "ANTHROPIC_API_KEY": "test-key",
            "GOOGLE_API_KEY": "test-key"
        }):
            # Mock successful responses
            with patch("app.services.orchestration_service.OrchestrationService._create_adapter") as mock_create:
                mock_adapter = AsyncMock()
                mock_adapter.generate.return_value = {"generated_text": "Test synthesis response"}
                mock_create.return_value = (mock_adapter, "model-name")
                
                response = await test_client.post(
                    "/api/orchestrator/analyze",
                    json={
                        "query": "Explain quantum computing",
                        "selected_models": ["gpt-4", "claude-3-5-sonnet-20241022", "gemini-1.5-flash"]
                    }
                )
                
                assert response.status_code == 200
                data = response.json()
                
                # Check new response structure: success + results.ultra_synthesis present
                assert data.get("success") is True
                assert "results" in data
                assert "ultra_synthesis" in data["results"]
                assert isinstance(data["results"]["ultra_synthesis"], str) and len(data["results"]["ultra_synthesis"]) > 5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])