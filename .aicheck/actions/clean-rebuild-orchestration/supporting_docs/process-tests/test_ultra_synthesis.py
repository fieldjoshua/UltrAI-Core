"""
Test specifications for Ultra Synthesis implementation
Tests the three-stage process: Initial → Meta → Ultra
"""
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
import time


class TestUltraSynthesis:
    """Test suite for Ultra Synthesis orchestration"""
    
    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator instance for testing"""
        from backend.services.minimal_orchestrator import MinimalOrchestrator
        return MinimalOrchestrator()
    
    @pytest.mark.asyncio
    async def test_three_stage_process(self, orchestrator):
        """Test that Ultra Synthesis follows Initial → Meta → Ultra stages"""
        prompt = "What is the capital of France?"
        models = ["gpt4o", "claude37"]
        
        result = await orchestrator.orchestrate(prompt, models)
        
        # Should have responses from all stages
        assert "initial_responses" in result
        assert "meta_responses" in result
        assert "ultra_response" in result
        
        # Each stage should have correct number of responses
        assert len(result["initial_responses"]) == 2
        assert len(result["meta_responses"]) == 2
        assert isinstance(result["ultra_response"], str)
    
    @pytest.mark.asyncio
    async def test_initial_stage_isolation(self, orchestrator):
        """Test that initial stage models don't see each other's responses"""
        # This is tested by ensuring initial prompts don't contain other responses
        prompt = "Test prompt"
        models = ["gpt4o", "claude37"]
        
        # Mock the adapters to capture prompts
        with patch.object(orchestrator, '_call_model', new_callable=AsyncMock) as mock_call:
            mock_call.return_value = {"response": "Test response", "time": 1.0}
            
            await orchestrator.orchestrate(prompt, models)
            
            # Check initial stage calls - should only have original prompt
            initial_calls = mock_call.call_args_list[:2]
            for call in initial_calls:
                assert call[0][1] == prompt  # Second arg is prompt
                assert "fellow LLMs" not in call[0][1]
    
    @pytest.mark.asyncio
    async def test_meta_stage_sees_all_responses(self, orchestrator):
        """Test that meta stage includes all initial responses"""
        prompt = "Original question"
        models = ["gpt4o", "claude37"]
        
        with patch.object(orchestrator, '_call_model', new_callable=AsyncMock) as mock_call:
            # Set up different responses for initial stage
            mock_call.side_effect = [
                {"response": "GPT4 initial response", "time": 1.0},
                {"response": "Claude initial response", "time": 1.2},
                {"response": "GPT4 meta response", "time": 1.1},
                {"response": "Claude meta response", "time": 1.3},
                {"response": "Ultra synthesis", "time": 0.8}
            ]
            
            await orchestrator.orchestrate(prompt, models)
            
            # Check meta stage calls include initial responses
            meta_calls = mock_call.call_args_list[2:4]
            for call in meta_calls:
                meta_prompt = call[0][1]
                assert "fellow LLMs" in meta_prompt
                assert "GPT4 initial response" in meta_prompt
                assert "Claude initial response" in meta_prompt
    
    @pytest.mark.asyncio 
    async def test_ultra_stage_synthesis(self, orchestrator):
        """Test that ultra stage synthesizes all meta responses"""
        prompt = "Original question"
        models = ["gpt4o", "claude37"]
        ultra_model = "gpt4o"
        
        with patch.object(orchestrator, '_call_model', new_callable=AsyncMock) as mock_call:
            mock_call.side_effect = [
                {"response": "Initial 1", "time": 1.0},
                {"response": "Initial 2", "time": 1.0},
                {"response": "Meta 1", "time": 1.0},
                {"response": "Meta 2", "time": 1.0},
                {"response": "Final Ultra Synthesis", "time": 1.0}
            ]
            
            result = await orchestrator.orchestrate(prompt, models, ultra_model)
            
            # Check ultra stage call
            ultra_call = mock_call.call_args_list[-1]
            ultra_prompt = ultra_call[0][1]
            assert "Ultra Synthesis" in ultra_prompt
            assert "fully-integrated intelligence synthesis" in ultra_prompt
            assert "Meta 1" in ultra_prompt
            assert "Meta 2" in ultra_prompt
    
    @pytest.mark.asyncio
    async def test_stage_timing(self, orchestrator):
        """Test that stages execute in correct order"""
        prompt = "Test"
        models = ["gpt4o", "claude37"]
        
        stage_order = []
        
        async def mock_call_model(model, prompt, stage):
            stage_order.append(stage)
            await asyncio.sleep(0.1)  # Simulate API delay
            return {"response": f"{stage} response", "time": 0.1}
        
        orchestrator._call_model = mock_call_model
        
        await orchestrator.orchestrate(prompt, models)
        
        # Verify stage order
        assert stage_order[:2] == ["initial", "initial"]  # Initial stage parallel
        assert stage_order[2:4] == ["meta", "meta"]      # Meta stage parallel
        assert stage_order[4] == "ultra"                  # Ultra stage last
    
    @pytest.mark.asyncio
    async def test_model_name_mapping_for_frontend(self, orchestrator):
        """Test that frontend model names map correctly"""
        # Frontend uses: gpt4o, claude37, gemini15
        # Backend uses: gpt-4, claude-3, gemini-pro
        
        mappings = {
            "gpt4o": "gpt-4",
            "gpt4turbo": "gpt-4-turbo", 
            "claude37": "claude-3",
            "claude3opus": "claude-3-opus",
            "gemini15": "gemini-pro"
        }
        
        for frontend_name, backend_name in mappings.items():
            assert orchestrator._map_model_name(frontend_name) == backend_name
    
    @pytest.mark.asyncio
    async def test_response_format_matches_frontend(self, orchestrator):
        """Test response format matches what frontend expects"""
        result = await orchestrator.orchestrate("Test", ["gpt4o"])
        
        # Frontend expects this exact structure
        assert result["status"] in ["success", "partial_success", "error"]
        assert "model_responses" in result
        assert isinstance(result["model_responses"], dict)
        assert "ultra_response" in result
        assert isinstance(result["ultra_response"], str)
        assert "performance" in result
        assert "total_time_seconds" in result["performance"]
        assert "model_times" in result["performance"]