"""
Test suite for basic orchestrator implementation
Focus: Reliability, Speed, Simplicity
"""
import asyncio
import time
from unittest.mock import Mock, patch, AsyncMock
import pytest

from backend.services.minimal_orchestrator import MinimalOrchestrator


class TestBasicOrchestrator:
    """Test basic orchestration functionality"""
    
    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator instance for testing"""
        with patch.dict('os.environ', {
            'OPENAI_API_KEY': 'test-key',
            'ANTHROPIC_API_KEY': 'test-key',
            'GOOGLE_API_KEY': 'test-key'
        }):
            return MinimalOrchestrator()
    
    @pytest.mark.asyncio
    async def test_basic_parallel_call(self, orchestrator):
        """Test: Basic parallel calls to multiple models"""
        # Mock the adapters
        mock_response = {"generated_text": "Test response"}
        
        for provider_models in orchestrator.adapters.values():
            for adapter in provider_models.values():
                adapter.generate = AsyncMock(return_value=mock_response)
        
        # Call with 2 models
        result = await orchestrator.orchestrate(
            prompt="Test prompt",
            models=["gpt4o", "claude37"]
        )
        
        # Verify basic structure
        assert result["status"] == "success"
        assert "model_responses" in result
        assert len(result["model_responses"]) == 2
        assert "performance" in result
        assert result["performance"]["total_time_seconds"] < 10  # Under 10 seconds
    
    @pytest.mark.asyncio
    async def test_single_model_failure_handling(self, orchestrator):
        """Test: System continues when one model fails"""
        # Mock one success, one failure
        mock_success = {"generated_text": "Success response"}
        mock_failure = Exception("Model unavailable")
        
        # Set up mixed responses
        if "openai" in orchestrator.adapters:
            for adapter in orchestrator.adapters["openai"].values():
                adapter.generate = AsyncMock(return_value=mock_success)
        
        if "anthropic" in orchestrator.adapters:
            for adapter in orchestrator.adapters["anthropic"].values():
                adapter.generate = AsyncMock(side_effect=mock_failure)
        
        # Call should still succeed
        result = await orchestrator.orchestrate(
            prompt="Test prompt",
            models=["gpt4o", "claude37"]
        )
        
        assert result["status"] == "success"
        assert "gpt4o" in result["model_responses"]
        assert "Error:" in result["model_responses"]["claude37"]
    
    @pytest.mark.asyncio
    async def test_timeout_protection(self, orchestrator):
        """Test: Timeouts don't crash the system"""
        # Mock a slow response
        async def slow_response():
            await asyncio.sleep(35)  # Longer than timeout
            return {"generated_text": "Too late"}
        
        for provider_models in orchestrator.adapters.values():
            for adapter in provider_models.values():
                adapter.generate = slow_response
        
        start = time.time()
        result = await orchestrator.orchestrate(
            prompt="Test prompt",
            models=["gpt4o"]
        )
        elapsed = time.time() - start
        
        # Should timeout gracefully
        assert elapsed < 35  # Didn't wait for full response
        assert "timeout" in result["model_responses"]["gpt4o"].lower()
    
    @pytest.mark.asyncio
    async def test_empty_prompt_handling(self, orchestrator):
        """Test: Empty prompts are rejected cleanly"""
        with pytest.raises(ValueError) as exc_info:
            await orchestrator.orchestrate(
                prompt="",
                models=["gpt4o"]
            )
        assert "empty" in str(exc_info.value).lower()
    
    @pytest.mark.asyncio
    async def test_model_name_mapping(self, orchestrator):
        """Test: Frontend model names map correctly"""
        # Test mapping
        assert orchestrator._map_model_name("gpt4o") == "gpt-4"
        assert orchestrator._map_model_name("claude37") == "claude-3"
        assert orchestrator._map_model_name("gemini15") == "gemini-pro"
    
    @pytest.mark.asyncio
    async def test_no_models_uses_defaults(self, orchestrator):
        """Test: Empty model list uses sensible defaults"""
        mock_response = {"generated_text": "Default response"}
        
        for provider_models in orchestrator.adapters.values():
            for adapter in provider_models.values():
                adapter.generate = AsyncMock(return_value=mock_response)
        
        result = await orchestrator.orchestrate(
            prompt="Test prompt",
            models=[]  # Empty list
        )
        
        assert result["status"] == "success"
        assert len(result["model_responses"]) >= 2  # At least 2 default models
    
    @pytest.mark.asyncio  
    async def test_performance_tracking(self, orchestrator):
        """Test: Performance metrics are tracked correctly"""
        mock_response = {"generated_text": "Fast response"}
        
        for provider_models in orchestrator.adapters.values():
            for adapter in provider_models.values():
                adapter.generate = AsyncMock(return_value=mock_response)
        
        result = await orchestrator.orchestrate(
            prompt="Test prompt",
            models=["gpt4o", "claude37"]
        )
        
        # Check performance data
        perf = result["performance"]
        assert "total_time_seconds" in perf
        assert "model_times" in perf
        assert perf["total_time_seconds"] > 0
        assert len(perf["model_times"]) > 0


class TestBasicReliability:
    """Test reliability features"""
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(self):
        """Test: Multiple concurrent orchestrations work"""
        orchestrator = MinimalOrchestrator()
        
        # Mock fast responses
        mock_response = {"generated_text": "Concurrent response"}
        for provider_models in orchestrator.adapters.values():
            for adapter in provider_models.values():
                adapter.generate = AsyncMock(return_value=mock_response)
        
        # Launch multiple requests
        tasks = []
        for i in range(5):
            task = orchestrator.orchestrate(
                prompt=f"Test prompt {i}",
                models=["gpt4o"]
            )
            tasks.append(task)
        
        # All should complete successfully
        results = await asyncio.gather(*tasks)
        assert all(r["status"] == "success" for r in results)
    
    @pytest.mark.asyncio
    async def test_adapter_initialization_failure(self):
        """Test: System works even if some adapters fail to initialize"""
        with patch.dict('os.environ', {
            'OPENAI_API_KEY': 'test-key',
            # Missing other keys
        }):
            orchestrator = MinimalOrchestrator()
            
            # Should have at least OpenAI
            assert len(orchestrator.adapters) >= 1
            assert any("gpt-4" in models for models in orchestrator.adapters.values())