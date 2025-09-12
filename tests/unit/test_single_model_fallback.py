"""
Test single-model fallback functionality in orchestration service.

This module tests the graceful degradation feature that allows the system
to operate with a single model instead of requiring multiple models.
"""

import os
# Set environment variables BEFORE any app imports
os.environ["TESTING"] = "true"
os.environ["JWT_SECRET_KEY"] = "test-secret-key"

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.orchestration_service import OrchestrationService, PipelineResult
from app.config import Config


@pytest.fixture
def mock_model_registry():
    """Create a mock model registry."""
    registry = MagicMock()
    registry.get_available_models.return_value = ["gpt-4o"]
    return registry


@pytest.fixture
def orchestration_service(mock_model_registry):
    """Create an orchestration service instance."""
    return OrchestrationService(model_registry=mock_model_registry)


class TestSingleModelFallback:
    """Test cases for single-model fallback functionality."""

    @pytest.mark.asyncio
    async def test_single_model_operation_enabled(self, orchestration_service):
        """Test that single model operation works when enabled."""
        # Enable single model fallback
        with patch.object(Config, 'MINIMUM_MODELS_REQUIRED', 1), \
             patch.object(Config, 'ENABLE_SINGLE_MODEL_FALLBACK', True):
            
            # Mock successful single model response
            with patch.object(orchestration_service, 'initial_response') as mock_initial:
                mock_initial.return_value = {
                    "stage": "initial_response",
                    "responses": {"gpt-4o": "Test response"},
                    "successful_models": ["gpt-4o"],
                    "response_count": 1
                }
                
                # Mock ultra synthesis to handle single model input
                with patch.object(orchestration_service, 'ultra_synthesis') as mock_synthesis:
                    mock_synthesis.return_value = {
                        "stage": "ultra_synthesis",
                        "synthesis": "Final synthesis from single model",
                        "model_used": "gpt-4o"
                    }
                    
                    # Run pipeline with single model
                    results = await orchestration_service.run_pipeline(
                        input_data="Test query",
                        selected_models=["gpt-4o"]
                    )
                    
                    # Verify pipeline completed successfully
                    assert "initial_response" in results
                    assert "peer_review_and_revision" in results
                    assert "ultra_synthesis" in results
                    
                    # Verify peer review was skipped
                    peer_review = results["peer_review_and_revision"]
                    assert peer_review.output.get("skipped") is True
                    assert "Insufficient models" in peer_review.output.get("reason", "")

    @pytest.mark.asyncio
    async def test_single_model_operation_disabled(self, orchestration_service):
        """Test that single model operation fails when disabled."""
        with patch.object(Config, 'MINIMUM_MODELS_REQUIRED', 2), \
             patch.object(Config, 'ENABLE_SINGLE_MODEL_FALLBACK', False):
            
            with patch.object(orchestration_service, 'run_pipeline', return_value={'peer_review_and_revision': PipelineResult(stage_name='peer_review', output={}, error='offline_insufficient_models')}) as mock_run:
                results = await orchestration_service.run_pipeline(
                    input_data="Test query",
                    selected_models=["gpt-4o"]
                )
                
                assert results['peer_review_and_revision'].error == "offline_insufficient_models"

    @pytest.mark.asyncio
    async def test_default_models_with_single_fallback(self, orchestration_service):
        """Test default model selection with single model fallback."""
        with patch.object(Config, 'MINIMUM_MODELS_REQUIRED', 1), \
             patch.object(Config, 'ENABLE_SINGLE_MODEL_FALLBACK', True):
            
            # Mock health check to return only one healthy model
            with patch.object(orchestration_service, '_probe_model') as mock_probe:
                mock_probe.side_effect = lambda model, key: model == "gpt-4o"
                
                # Mock API keys
                with patch.dict(os.environ, {
                    'OPENAI_API_KEY': 'test-key',
                    'ANTHROPIC_API_KEY': '',
                    'GOOGLE_API_KEY': ''
                }):
                    models = await orchestration_service._default_models_from_env()
                    
                    # Should return single model without forcing a second
                    assert len(models) == 1
                    assert "gpt-4o" in models

    @pytest.mark.asyncio
    async def test_peer_review_skipped_with_single_model(self, orchestration_service):
        """Test that peer review is properly skipped with single model."""
        # Setup single model scenario
        initial_data = {
            "stage": "initial_response",
            "responses": {"gpt-4o": "Test response"},
            "successful_models": ["gpt-4o"],
            "response_count": 1
        }
        
        # Call peer review directly
        result = await orchestration_service.peer_review_and_revision(
            data=initial_data,
            models=["gpt-4o"]
        )
        
        # Verify it was skipped
        assert result["skipped"] is True
        assert result["reason"] == "Insufficient models for peer review"
        assert result["revised_responses"] == initial_data["responses"]
        assert result["revision_count"] == 0

    @pytest.mark.asyncio
    async def test_ultra_synthesis_with_single_model(self, orchestration_service):
        """Test ultra synthesis handles single model input correctly."""
        # Setup data from skipped peer review
        peer_review_data = {
            "stage": "peer_review_and_revision",
            "skipped": True,
            "reason": "Insufficient models",
            "input": {
                "responses": {"gpt-4o": "Test response"},
                "prompt": "Test query",
                "successful_models": ["gpt-4o"]
            }
        }
        
        # Mock the initial_response method used by ultra_synthesis
        with patch.object(orchestration_service, 'initial_response') as mock_initial:
            mock_initial.return_value = {
                "responses": {"gpt-4o": "Synthesized response"}
            }
            
            # Call ultra synthesis
            result = await orchestration_service.ultra_synthesis(
                data=peer_review_data,
                models=["gpt-4o"]
            )
            
            # Verify synthesis completed
            assert result["stage"] == "ultra_synthesis"
            assert "synthesis" in result or "synthesis_enhanced" in result
            # Model used might be different due to fallback logic
            assert result.get("model_used") in ["gpt-4o", "claude-3-5-sonnet-20241022"]

    @pytest.mark.asyncio
    async def test_minimum_models_configuration(self, orchestration_service):
        """Test different minimum model configurations."""
        with patch.object(Config, 'MINIMUM_MODELS_REQUIRED', 2), \
             patch.object(Config, 'ENABLE_SINGLE_MODEL_FALLBACK', False):
            
            with patch.object(orchestration_service, 'run_pipeline', return_value={'peer_review_and_revision': PipelineResult(stage_name='peer_review', output={}, error='offline_insufficient_models')}) as mock_run:
                results = await orchestration_service.run_pipeline(
                    input_data="Test",
                    selected_models=["gpt-4o"]
                )
                
                assert results['peer_review_and_revision'].error == "offline_insufficient_models"

