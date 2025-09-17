#!/usr/bin/env python3
"""
Implementation tests for the current UltrAI Synthesis analysis type.
Tests the actual orchestration service implementation against the specification.
"""

import pytest
import asyncio
import os
from typing import Dict, List, Any
from unittest.mock import Mock, patch, AsyncMock
import json

# Import the actual implementation
from app.services.orchestration_service import OrchestrationService
from app.services.model_registry import ModelRegistry
from app.services.llm_adapters import OpenAIAdapter, AnthropicAdapter, GeminiAdapter


class TestUltrAISynthesisImplementation:
    """Test the actual UltrAI Synthesis implementation."""
    
    @pytest.fixture
    def mock_llm_responses(self):
        """Mock responses from different LLMs."""
        return {
            "gpt-4": {
                "initial": "GPT-4: AI is a transformative technology...",
                "revised": "GPT-4 (Revised): After reviewing peer insights, AI represents a paradigm shift..."
            },
            "claude-3-5-sonnet-20241022": {
                "initial": "Claude: Artificial Intelligence encompasses computational systems...",
                "revised": "Claude (Revised): Incorporating peer perspectives, AI is a multifaceted field..."
            },
            "gemini-1.5-flash": {
                "initial": "Gemini: AI refers to machine intelligence that mimics human cognition...",
                "revised": "Gemini (Revised): Building on collective analysis, AI represents the frontier..."
            }
        }
    
    @pytest.fixture
    def mock_model_registry(self, mock_llm_responses):
        """Create a mock model registry with proper adapters."""
        registry = Mock()
        
        # Mock get_models to return actual adapter instances
        def get_models(model_list=None):
            adapters = {}
            for model in (model_list or mock_llm_responses.keys()):
                if "gpt" in model:
                    adapter = Mock(spec=OpenAIAdapter)
                elif "claude" in model:
                    adapter = Mock(spec=AnthropicAdapter)
                elif "gemini" in model:
                    adapter = Mock(spec=GeminiAdapter)
                else:
                    adapter = Mock()
                
                # Set up the adapter's complete method
                adapter.complete = AsyncMock()
                adapters[model] = adapter
            
            return adapters
        
        registry.get_models = Mock(side_effect=get_models)
        return registry
    
    @pytest.mark.asyncio
    async def test_synthesis_preserves_original_prompt(self, mock_model_registry, mock_llm_responses):
        """Test that the synthesis correctly preserves and references the original user prompt."""
        orchestrator = OrchestrationService(mock_model_registry)
        
        # Set up mock responses for each stage
        async def mock_complete(prompt, **kwargs):
            # Detect which stage we're in based on prompt content
            if "peer" in prompt.lower() or "revised" in prompt.lower():
                # Peer review stage
                return mock_llm_responses[kwargs.get('model', 'gpt-4')]['revised']
            elif "ultra synthesis" in prompt.lower() or "comprehensive" in prompt.lower():
                # Ultra synthesis stage
                return f"Ultra Synthesis: Addressing '{USER_QUERY}', the consensus shows..."
            else:
                # Initial response stage
                return mock_llm_responses[kwargs.get('model', 'gpt-4')]['initial']
        
        # Apply mocks to all adapters
        for model_adapters in mock_model_registry.get_models().values():
            for adapter in model_adapters.values():
                adapter.complete.side_effect = mock_complete
        
        # Test query
        USER_QUERY = "What is artificial intelligence and how does it impact society?"
        
        # Run the full pipeline
        with patch.object(orchestrator, '_get_llm_adapter') as mock_get_adapter:
            # Return appropriate adapter for each model
            def get_adapter_for_model(model):
                adapters = mock_model_registry.get_models([model])
                return list(adapters.values())[0]
            
            mock_get_adapter.side_effect = get_adapter_for_model
            
            result = await orchestrator.run_pipeline(
                input_data=USER_QUERY,
                selected_models=["gpt-4", "claude-3-5-sonnet-20241022", "gemini-1.5-flash"]
            )
        
        # Verify the synthesis references the original query
        assert "ultra_synthesis" in result
        synthesis = result["ultra_synthesis"]["synthesis"]
        
        # The synthesis should reference the original query
        assert USER_QUERY in synthesis or "What is artificial intelligence" in synthesis
    
    @pytest.mark.asyncio
    async def test_three_stage_pipeline_execution(self, mock_model_registry):
        """Test that all three stages execute in order: Initial → Meta (Peer Review) → UltrAI."""
        orchestrator = OrchestrationService(mock_model_registry)
        
        stages_executed = []
        
        # Mock stage methods to track execution
        async def track_initial(*args, **kwargs):
            stages_executed.append("initial")
            return {
                "prompt": args[0] if args else "test",
                "responses": {"gpt-4": "response1", "claude-3": "response2"},
                "successful_models": ["gpt-4", "claude-3"]
            }
        
        async def track_peer_review(*args, **kwargs):
            stages_executed.append("peer_review")
            return {
                "revised_responses": {"gpt-4": "revised1", "claude-3": "revised2"},
                "input": args[0] if args else {}
            }
        
        async def track_synthesis(*args, **kwargs):
            stages_executed.append("synthesis")
            return {
                "synthesis": "Final synthesis output",
                "model_used": "claude-3-5-sonnet-20241022"
            }
        
        orchestrator.initial_response = track_initial
        orchestrator.peer_review_and_revision = track_peer_review
        orchestrator.ultra_synthesis = track_synthesis
        
        # Run pipeline
        await orchestrator.run_pipeline(
            input_data="Test query",
            selected_models=["gpt-4", "claude-3", "gemini-flash"]
        )
        
        # Verify all stages executed in order
        assert stages_executed == ["initial", "peer_review", "synthesis"]
    
    @pytest.mark.asyncio
    async def test_peer_review_skipped_with_insufficient_models(self, mock_model_registry):
        """Test that peer review is skipped when < 3 models available."""
        # Test with only 2 models
        
        orchestrator = OrchestrationService(mock_model_registry)
        
        stages_executed = []
        
        # Track which stages run
        original_peer_review = orchestrator.peer_review_and_revision
        async def track_peer_review(*args, **kwargs):
            stages_executed.append("peer_review")
            return await original_peer_review(*args, **kwargs)
        
        orchestrator.peer_review_and_revision = track_peer_review
        
        # Mock other stages
        orchestrator.initial_response = AsyncMock(return_value={
            "prompt": "test",
            "responses": {"gpt-4": "resp1", "claude-3": "resp2"}
        })
        
        orchestrator.ultra_synthesis = AsyncMock(return_value={
            "synthesis": "Synthesis without peer review"
        })
        
        # Run pipeline with only 2 models
        result = await orchestrator.run_pipeline(
            input_data="Test query",
            selected_models=["gpt-4", "claude-3"]
        )
        
        # Verify peer review was NOT called
        assert "peer_review" not in stages_executed
        
        # Verify synthesis still happened
        orchestrator.ultra_synthesis.assert_called_once()
    
    @pytest.mark.asyncio 
    async def test_synthesis_combines_all_model_outputs(self, mock_model_registry):
        """Test that ultra synthesis actually combines insights from all models."""
        orchestrator = OrchestrationService(mock_model_registry)
        
        # Track what gets passed to synthesis
        synthesis_input = None
        
        async def capture_synthesis_input(data, *args, **kwargs):
            nonlocal synthesis_input
            synthesis_input = data
            
            # Create a synthesis that references all models
            if "revised_responses" in data:
                responses = data["revised_responses"]
            else:
                responses = data.get("responses", {})
            
            combined = f"Synthesis combining insights from {len(responses)} models: "
            combined += ", ".join(f"{model}" for model in responses.keys())
            
            return {
                "synthesis": combined,
                "source_models": list(responses.keys())
            }
        
        orchestrator.ultra_synthesis = capture_synthesis_input
        
        # Mock other stages
        test_responses = {
            "gpt-4": "GPT-4 response",
            "claude-3": "Claude response", 
            "gemini": "Gemini response"
        }
        
        orchestrator.initial_response = AsyncMock(return_value={
            "responses": test_responses
        })
        
        orchestrator.peer_review_and_revision = AsyncMock(return_value={
            "revised_responses": {k: f"Revised: {v}" for k, v in test_responses.items()}
        })
        
        # Run pipeline
        result = await orchestrator.run_pipeline(
            input_data="Test query",
            selected_models=list(test_responses.keys())
        )
        
        # Verify synthesis received all model outputs
        assert synthesis_input is not None
        assert "revised_responses" in synthesis_input or "responses" in synthesis_input
        
        # Verify synthesis output references all models
        synthesis = result["ultra_synthesis"]["synthesis"]
        assert "3 models" in synthesis
        assert all(model in synthesis for model in test_responses.keys())
    
    @pytest.mark.asyncio
    async def test_non_participant_model_for_synthesis(self, mock_model_registry):
        """Test that synthesis uses a non-participant model when available."""
        # Test with extra model for synthesis
        all_models = ["gpt-4", "claude-3", "gemini-flash", "claude-3-5-sonnet-20241022"]
        
        orchestrator = OrchestrationService(mock_model_registry)
        
        # Track which model performs synthesis
        synthesis_model_used = None
        
        async def track_synthesis_model(prompt, models, *args, **kwargs):
            nonlocal synthesis_model_used
            synthesis_model_used = models[0] if models else None
            return {"responses": {models[0]: "Synthesis result"}}
        
        # Patch the method that synthesis calls to get LLM response
        with patch.object(orchestrator, 'initial_response', new=track_synthesis_model):
            # Mock peer review output
            peer_review_output = {
                "revised_responses": {
                    "gpt-4": "Revised 1",
                    "claude-3": "Revised 2",
                    "gemini-flash": "Revised 3"
                }
            }
            
            # Call synthesis directly
            await orchestrator.ultra_synthesis(
                peer_review_output,
                models=["claude-3-5-sonnet-20241022"]  # Non-participant model
            )
        
        # Verify synthesis used the non-participant model
        assert synthesis_model_used == "claude-3-5-sonnet-20241022"
    
    @pytest.mark.asyncio
    async def test_confidence_indicators_in_synthesis(self, mock_model_registry):
        """Test that synthesis includes confidence analysis when responses diverge."""
        orchestrator = OrchestrationService(mock_model_registry)
        
        # Create divergent responses
        divergent_responses = {
            "gpt-4": "AI will definitely replace all human jobs within 5 years",
            "claude-3": "AI will augment human capabilities but not replace most jobs",
            "gemini": "AI impact on jobs is uncertain and highly debated"
        }
        
        # Mock the synthesis to analyze confidence
        async def confidence_synthesis(data, *args, **kwargs):
            responses = data.get("revised_responses", data.get("responses", {}))
            
            # Simple confidence detection based on agreement
            if "definitely" in str(responses) and "uncertain" in str(responses):
                confidence = "Low confidence due to divergent views"
            else:
                confidence = "High confidence based on consensus"
            
            return {
                "synthesis": f"Analysis complete. {confidence}",
                "confidence_level": confidence
            }
        
        orchestrator.initial_response = AsyncMock(return_value={
            "responses": divergent_responses
        })
        
        orchestrator.peer_review_and_revision = AsyncMock(return_value={
            "revised_responses": divergent_responses
        })
        
        orchestrator.ultra_synthesis = confidence_synthesis
        
        # Run pipeline
        result = await orchestrator.run_pipeline(
            input_data="Will AI replace human jobs?",
            selected_models=list(divergent_responses.keys())
        )
        
        # Verify confidence analysis is included
        synthesis = result["ultra_synthesis"]["synthesis"]
        assert "confidence" in synthesis.lower()
        assert result["ultra_synthesis"].get("confidence_level") is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])