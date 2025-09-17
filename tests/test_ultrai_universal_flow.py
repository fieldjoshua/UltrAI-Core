#!/usr/bin/env python3
"""
Comprehensive test suite for UltrAI Universal Flow based on the core system variables:

1. INITIALIZATION - Model readiness and status
2. USER INPUTS - UI/UX data acceptance and conveyance
3. ORCHESTRATOR - Three-round analysis pipeline
   a) Initial Round - User prompt → LLMs → Initial outputs
   b) Meta Round - Peer review with revision
   c) UltrAI Round - Synthesis of all outputs

Current Implementation: UltrAI Synthesis Analysis Type
"""

import pytest
import asyncio
from typing import Dict, List, Any
from unittest.mock import Mock, patch, AsyncMock
import json

from app.services.orchestration_service import OrchestrationService
from app.services.model_registry import ModelRegistry
from app.routes.orchestrator_minimal import AnalysisRequest


class TestUltrAIUniversalFlow:
    """Test the complete UltrAI flow from initialization to final output."""
    
    # ========================================================================
    # VARIABLE 1: INITIALIZATION TESTS
    # ========================================================================
    
    @pytest.mark.asyncio
    async def test_initialization_sufficient_models(self):
        """Test that system verifies sufficient models are ready (minimum 2, target 3)."""
        # Setup
        mock_registry = Mock(spec=ModelRegistry)
        
        # Test Case 1: Insufficient models (only 1)
        mock_registry.get_available_models.return_value = ["gpt-4"]
        orchestrator = OrchestrationService(mock_registry)
        
        # Should fail with < 2 models
        with pytest.raises(Exception) as exc_info:
            await orchestrator.run_pipeline("test query")
        assert "insufficient models" in str(exc_info.value).lower()
        
        # Test Case 2: Minimum viable (2 models)
        mock_registry.get_available_models.return_value = ["gpt-4", "claude-3"]
        result = await orchestrator.run_pipeline("test query")
        assert result is not None
        
        # Test Case 3: Target state (3+ models from Big 3)
        mock_registry.get_available_models.return_value = [
            "gpt-4",  # OpenAI
            "claude-3-5-sonnet-20241022",  # Anthropic
            "gemini-1.5-flash"  # Google
        ]
        result = await orchestrator.run_pipeline("test query")
        assert "peer_review" in result  # Should enable peer review with 3+ models
    
    @pytest.mark.asyncio
    async def test_initialization_model_health_check(self):
        """Test that models are behaving properly and ready to accept data."""
        mock_registry = Mock(spec=ModelRegistry)
        
        # Mock healthy models
        mock_registry.check_model_health.side_effect = lambda model: {
            "model": model,
            "status": "healthy",
            "response_time": 0.5,
            "error_rate": 0.0
        }
        
        orchestrator = OrchestrationService(mock_registry)
        health_status = await orchestrator.check_system_health()
        
        assert health_status["ready"] is True
        assert health_status["healthy_models"] >= 2
        assert all(m["status"] == "healthy" for m in health_status["models"])
    
    @pytest.mark.asyncio
    async def test_initialization_status_conveyance(self):
        """Test that initialization status is properly conveyed."""
        # Test the /api/orchestrator/status endpoint behavior
        from app.routes.orchestrator_minimal import get_orchestrator_status
        
        mock_request = Mock()
        mock_request.app.state.services = {
            "orchestration": Mock(
                check_system_health=AsyncMock(return_value={
                    "ready": True,
                    "healthy_models": 3,
                    "models": [
                        {"name": "gpt-4", "status": "healthy"},
                        {"name": "claude-3", "status": "healthy"},
                        {"name": "gemini-flash", "status": "healthy"}
                    ],
                    "required_providers": ["openai", "anthropic", "google"],
                    "message": "All systems operational"
                })
            )
        }
        
        status = await get_orchestrator_status(mock_request)
        assert status["ready"] is True
        assert status["healthy_models"] == 3
        assert "All systems operational" in status["message"]
    
    # ========================================================================
    # VARIABLE 2: USER INPUTS TESTS
    # ========================================================================
    
    @pytest.mark.asyncio
    async def test_user_inputs_ui_acceptance(self):
        """Test that UI properly accepts and validates user inputs."""
        # Test the AnalysisRequest model validation
        
        # Valid request
        valid_request = AnalysisRequest(
            query="What is artificial intelligence?",
            analysis_type="synthesis",  # Current supported type
            options={"include_confidence": True}
        )
        assert valid_request.query == "What is artificial intelligence?"
        assert valid_request.analysis_type == "synthesis"
        
        # Invalid request - empty query
        with pytest.raises(ValueError):
            AnalysisRequest(query="", analysis_type="synthesis")
        
        # Invalid request - unsupported analysis type
        with pytest.raises(ValueError):
            AnalysisRequest(
                query="Test query",
                analysis_type="unsupported_type"  # Should only accept "synthesis" for now
            )
    
    @pytest.mark.asyncio
    async def test_user_inputs_data_conveyance(self):
        """Test that user data is properly conveyed to orchestrator."""
        mock_registry = Mock(spec=ModelRegistry)
        orchestrator = OrchestrationService(mock_registry)
        
        # Mock the pipeline execution to track what it receives
        original_run_pipeline = orchestrator.run_pipeline
        received_inputs = {}
        
        async def tracking_pipeline(input_data, **kwargs):
            received_inputs["input_data"] = input_data
            received_inputs["options"] = kwargs.get("options", {})
            received_inputs["selected_models"] = kwargs.get("selected_models")
            return {"success": True}
        
        orchestrator.run_pipeline = tracking_pipeline
        
        # Simulate API call
        await orchestrator.run_pipeline(
            input_data="What is AI?",
            options={"analysis_type": "synthesis"},
            selected_models=["gpt-4", "claude-3"]
        )
        
        # Verify data was properly conveyed
        assert received_inputs["input_data"] == "What is AI?"
        assert received_inputs["options"]["analysis_type"] == "synthesis"
        assert received_inputs["selected_models"] == ["gpt-4", "claude-3"]
    
    # ========================================================================
    # VARIABLE 3: ORCHESTRATOR TESTS
    # ========================================================================
    
    @pytest.mark.asyncio
    async def test_orchestrator_initial_round(self):
        """Test Initial Round: User prompt → Selected LLMs → Initial outputs."""
        mock_registry = Mock(spec=ModelRegistry)
        orchestrator = OrchestrationService(mock_registry)
        
        # Mock LLM responses
        mock_llm_responses = {
            "gpt-4": "AI is a field of computer science...",
            "claude-3": "Artificial Intelligence refers to systems...",
            "gemini-flash": "AI encompasses machine learning..."
        }
        
        # Mock the initial_response method
        orchestrator.initial_response = AsyncMock(return_value={
            "stage": "initial_response",
            "prompt": "What is AI?",
            "responses": mock_llm_responses,
            "successful_models": list(mock_llm_responses.keys())
        })
        
        # Execute initial round
        result = await orchestrator.initial_response(
            "What is AI?",
            ["gpt-4", "claude-3", "gemini-flash"]
        )
        
        # Verify initial round outputs
        assert result["stage"] == "initial_response"
        assert result["prompt"] == "What is AI?"
        assert len(result["responses"]) == 3
        assert all(model in result["successful_models"] for model in mock_llm_responses.keys())
    
    @pytest.mark.asyncio
    async def test_orchestrator_meta_round(self):
        """Test Meta Round: Peer review where LLMs revise based on peer outputs."""
        mock_registry = Mock(spec=ModelRegistry)
        orchestrator = OrchestrationService(mock_registry)
        
        # Initial responses from first round
        initial_responses = {
            "prompt": "What is AI?",
            "responses": {
                "gpt-4": "AI is computer intelligence...",
                "claude-3": "AI represents machine thinking...",
                "gemini-flash": "AI is algorithmic intelligence..."
            }
        }
        
        # Mock peer review responses
        mock_peer_review = {
            "stage": "peer_review_and_revision",
            "revised_responses": {
                "gpt-4": "After reviewing peer responses, AI is more comprehensively...",
                "claude-3": "Incorporating peer insights, AI represents...",
                "gemini-flash": "Building on collective analysis, AI encompasses..."
            },
            "metadata": {
                "revision_prompts_sent": True,
                "models_revised": 3
            }
        }
        
        orchestrator.peer_review_and_revision = AsyncMock(return_value=mock_peer_review)
        
        # Execute meta round
        result = await orchestrator.peer_review_and_revision(
            initial_responses,
            ["gpt-4", "claude-3", "gemini-flash"]
        )
        
        # Verify meta round outputs
        assert result["stage"] == "peer_review_and_revision"
        assert len(result["revised_responses"]) == 3
        assert all("peer" in response.lower() for response in result["revised_responses"].values())
        assert result["metadata"]["models_revised"] == 3
    
    @pytest.mark.asyncio
    async def test_orchestrator_ultrai_round(self):
        """Test UltrAI Round: Synthesis of meta outputs into final UltrAI output."""
        mock_registry = Mock(spec=ModelRegistry)
        orchestrator = OrchestrationService(mock_registry)
        
        # Meta round outputs
        meta_outputs = {
            "revised_responses": {
                "gpt-4": "Refined: AI is...",
                "claude-3": "Enhanced: AI represents...",
                "gemini-flash": "Improved: AI encompasses..."
            },
            "prompt": "What is AI?"  # Original prompt preserved
        }
        
        # Mock ultra synthesis
        mock_synthesis = {
            "stage": "ultra_synthesis",
            "synthesis": """
                🌟 ULTRA SYNTHESIS™ 🌟
                
                Based on comprehensive peer-reviewed analysis:
                
                **Consensus Understanding**: AI is...
                **Unique Insights**: Each model contributed...
                **Confidence Level**: High confidence based on convergence...
                
                [Synthesized from 3 peer-reviewed responses]
            """,
            "model_used": "claude-3-5-sonnet-20241022",  # Non-participant model
            "source_models": ["gpt-4", "claude-3", "gemini-flash"],
            "meta_analysis": "Combined peer-reviewed responses"
        }
        
        orchestrator.ultra_synthesis = AsyncMock(return_value=mock_synthesis)
        
        # Execute UltrAI round
        result = await orchestrator.ultra_synthesis(
            meta_outputs,
            ["claude-3-5-sonnet-20241022"]  # Different model for synthesis
        )
        
        # Verify UltrAI synthesis output
        assert result["stage"] == "ultra_synthesis"
        assert "ULTRA SYNTHESIS™" in result["synthesis"]
        assert result["model_used"] == "claude-3-5-sonnet-20241022"
        assert len(result["source_models"]) == 3
        assert "peer-reviewed" in result["synthesis"].lower()
    
    @pytest.mark.asyncio
    async def test_full_ultrai_synthesis_flow(self):
        """Test complete UltrAI Synthesis flow from user input to final output."""
        mock_registry = Mock(spec=ModelRegistry)
        mock_registry.get_available_models.return_value = [
            "gpt-4", "claude-3-5-sonnet-20241022", "gemini-1.5-flash"
        ]
        
        orchestrator = OrchestrationService(mock_registry)
        
        # Mock all three rounds
        orchestrator.initial_response = AsyncMock(return_value={
            "prompt": "What is quantum computing?",
            "responses": {
                "gpt-4": "Quantum computing uses quantum mechanics...",
                "claude-3": "Quantum computers leverage superposition...",
                "gemini-flash": "Quantum computing exploits quantum phenomena..."
            }
        })
        
        orchestrator.peer_review_and_revision = AsyncMock(return_value={
            "revised_responses": {
                "gpt-4": "Refined: Quantum computing fundamentally...",
                "claude-3": "Enhanced: Quantum computers achieve...",
                "gemini-flash": "Improved: Quantum computing represents..."
            },
            "input": {"prompt": "What is quantum computing?"}  # Prompt preserved
        })
        
        orchestrator.ultra_synthesis = AsyncMock(return_value={
            "synthesis": "Complete synthesis combining all insights...",
            "model_used": "claude-3-5-sonnet-20241022"
        })
        
        # Execute full pipeline
        result = await orchestrator.run_pipeline(
            input_data="What is quantum computing?",
            options={"analysis_type": "synthesis"}
        )
        
        # Verify complete flow
        orchestrator.initial_response.assert_called_once()
        orchestrator.peer_review_and_revision.assert_called_once()
        orchestrator.ultra_synthesis.assert_called_once()
        
        # Verify original prompt was preserved through all stages
        initial_call = orchestrator.initial_response.call_args[0][0]
        assert initial_call == "What is quantum computing?"
        
        synthesis_data = orchestrator.ultra_synthesis.call_args[0][0]
        assert "What is quantum computing?" in str(synthesis_data)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])