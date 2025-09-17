#!/usr/bin/env python3
"""
Integration tests for the UltrAI synthesis system with Big 3 LLMs.
Tests the actual implementation with mocked API responses.
"""

import pytest
import os
from unittest.mock import patch, AsyncMock, Mock
from app.main import create_app
from httpx import AsyncClient


class TestSynthesisIntegration:
    """Test the synthesis system integration with Big 3 LLMs."""
    
    @pytest.fixture
    async def test_app(self):
        """Create test app instance."""
        app = create_app()
        return app
    
    @pytest.fixture
    async def test_client(self, test_app):
        """Create test client."""
        async with AsyncClient(app=test_app, base_url="http://test") as client:
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
            with patch("app.services.llm_adapters.OpenAIAdapter") as MockOpenAI, \
                 patch("app.services.llm_adapters.AnthropicAdapter") as MockAnthropic, \
                 patch("app.services.llm_adapters.GeminiAdapter") as MockGemini:
                
                # Set up mock responses
                mock_openai = AsyncMock()
                mock_openai.generate.return_value = {
                    "generated_text": "GPT-4: Renewable energy offers sustainability..."
                }
                MockOpenAI.return_value = mock_openai
                
                mock_anthropic = AsyncMock()
                mock_anthropic.generate.return_value = {
                    "generated_text": "Claude: Key benefits include environmental protection..."
                }
                MockAnthropic.return_value = mock_anthropic
                
                mock_gemini = AsyncMock()
                mock_gemini.generate.return_value = {
                    "generated_text": "Gemini: Renewable energy provides energy independence..."
                }
                MockGemini.return_value = mock_gemini
                
                # Make request
                response = await test_client.post(
                    "/api/orchestrate",
                    json={
                        "prompt": USER_PROMPT,
                        "models": ["gpt-4", "claude-3-5-sonnet-20241022", "gemini-1.5-flash"]
                    }
                )
                
                assert response.status_code == 200
                data = response.json()
                
                # Verify synthesis includes original prompt
                assert "ultra_synthesis" in data.get("pipeline_results", {})
                synthesis = data["pipeline_results"]["ultra_synthesis"]
                
                # The synthesis should reference the original query
                assert USER_PROMPT in synthesis.get("synthesis", "") or \
                       "renewable energy" in synthesis.get("synthesis", "").lower()
    
    @pytest.mark.asyncio
    async def test_minimum_models_requirement(self, test_client):
        """Test that system requires minimum 3 models from Big 3 providers."""
        # Test with only 2 models - should fail
        with patch.dict(os.environ, {
            "OPENAI_API_KEY": "test-key",
            "ANTHROPIC_API_KEY": "test-key"
        }):
            response = await test_client.post(
                "/api/orchestrate",
                json={
                    "prompt": "Test query",
                    "models": ["gpt-4", "claude-3"]
                }
            )
            
            # Should return 503 Service Unavailable
            assert response.status_code == 503
            data = response.json()
            assert "SERVICE_UNAVAILABLE" in str(data)
    
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
            with patch("app.services.llm_adapters.OpenAIAdapter") as MockOpenAI, \
                 patch("app.services.llm_adapters.AnthropicAdapter") as MockAnthropic, \
                 patch("app.services.llm_adapters.GeminiAdapter") as MockGemini:
                
                # Set up mocks
                for MockClass in [MockOpenAI, MockAnthropic, MockGemini]:
                    mock_instance = AsyncMock()
                    mock_instance.generate.side_effect = mock_generate
                    MockClass.return_value = mock_instance
                
                response = await test_client.post(
                    "/api/orchestrate", 
                    json={
                        "prompt": "Test parallel execution",
                        "models": ["gpt-4", "claude-3-5-sonnet-20241022", "gemini-1.5-flash"]
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
                    "/api/orchestrate",
                    json={
                        "prompt": "Explain quantum computing",
                        "models": ["gpt-4", "claude-3-5-sonnet-20241022", "gemini-1.5-flash"]
                    }
                )
                
                assert response.status_code == 200
                data = response.json()
                
                # Check pipeline results structure
                assert "pipeline_results" in data
                results = data["pipeline_results"]
                
                # Should have all 3 stages
                assert "initial_response" in results
                assert "peer_review" in results
                assert "ultra_synthesis" in results
                
                # Ultra synthesis should have synthesis text
                synthesis = results["ultra_synthesis"]
                assert "synthesis" in synthesis
                assert len(synthesis["synthesis"]) > 20  # Not empty or stub


if __name__ == "__main__":
    pytest.main([__file__, "-v"])