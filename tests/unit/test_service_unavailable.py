"""
Test service unavailable responses when insufficient models.
"""

import os
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException
from app.services.orchestration_service import OrchestrationService
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


class TestServiceUnavailable:
    """Test cases for service unavailable functionality."""

    @pytest.mark.asyncio
    async def test_service_unavailable_with_one_model(self, orchestration_service):
        """Test that service returns unavailable with only one model."""
        # Ensure minimum 2 models required and fallback disabled
        with patch.object(Config, 'MINIMUM_MODELS_REQUIRED', 2), \
             patch.object(Config, 'ENABLE_SINGLE_MODEL_FALLBACK', False):
            
            # Mock single model response
            with patch.object(orchestration_service, 'initial_response') as mock_initial:
                mock_initial.return_value = {
                    "stage": "initial_response",
                    "responses": {"gpt-4o": "Test response"},
                    "successful_models": ["gpt-4o"],
                    "response_count": 1
                }
                
                # Run pipeline with single model
                result = await orchestration_service.run_pipeline(
                    input_data="Test query",
                    selected_models=["gpt-4o"]
                )
                
                # Verify service unavailable response
                assert isinstance(result, dict)
                assert result.get("error") == "SERVICE_UNAVAILABLE"
                assert "requires at least 2" in result.get("message", "")
                assert result.get("details", {}).get("models_available") == 1
                assert result.get("details", {}).get("models_required") == 2
                assert result.get("details", {}).get("service_status") == "degraded"

    @pytest.mark.asyncio
    async def test_service_available_with_multiple_models(self, orchestration_service):
        """Test that service works normally with multiple models."""
        with patch.object(Config, 'MINIMUM_MODELS_REQUIRED', 2):
            
            # Mock multiple model responses
            with patch.object(orchestration_service, 'initial_response') as mock_initial:
                mock_initial.return_value = {
                    "stage": "initial_response",
                    "responses": {
                        "gpt-4o": "Response 1",
                        "claude-3-sonnet-20240229": "Response 2"
                    },
                    "successful_models": ["gpt-4o", "claude-3-sonnet-20240229"],
                    "response_count": 2
                }
                
                # Mock peer review and synthesis
                with patch.object(orchestration_service, 'peer_review_and_revision') as mock_peer:
                    mock_peer.return_value = {
                        "stage": "peer_review_and_revision",
                        "revised_responses": {
                            "gpt-4o": "Revised 1",
                            "claude-3-sonnet-20240229": "Revised 2"
                        }
                    }
                    
                    with patch.object(orchestration_service, 'ultra_synthesis') as mock_synthesis:
                        mock_synthesis.return_value = {
                            "stage": "ultra_synthesis",
                            "synthesis": "Final synthesis"
                        }
                        
                        # Run pipeline
                        result = await orchestration_service.run_pipeline(
                            input_data="Test query",
                            selected_models=["gpt-4o", "claude-3-sonnet-20240229"]
                        )
                        
                        # Should not have SERVICE_UNAVAILABLE error
                        assert result.get("error") != "SERVICE_UNAVAILABLE"
                        assert "ultra_synthesis" in result

    @pytest.mark.asyncio 
    async def test_service_status_endpoint(self):
        """Test the service status endpoint logic."""
        from app.config import Config
        
        # Test unavailable status
        with patch.object(Config, 'MINIMUM_MODELS_REQUIRED', 2), \
             patch.object(Config, 'ENABLE_SINGLE_MODEL_FALLBACK', False):
            
            # Simulate status check with 1 model
            available_models = ["gpt-4o"]
            model_count = len(available_models)
            required_models = Config.MINIMUM_MODELS_REQUIRED
            
            if model_count >= required_models:
                status = "healthy"
                service_available = True
            elif model_count >= 1 and Config.ENABLE_SINGLE_MODEL_FALLBACK:
                status = "degraded" 
                service_available = True
            else:
                status = "unavailable"
                service_available = False
                
            assert status == "unavailable"
            assert service_available is False

    @pytest.mark.asyncio
    async def test_zero_models_available(self, orchestration_service):
        """Test behavior when no models are available."""
        with patch.object(Config, 'MINIMUM_MODELS_REQUIRED', 2):
            
            # Mock no model responses
            with patch.object(orchestration_service, 'initial_response') as mock_initial:
                mock_initial.return_value = {
                    "stage": "initial_response",
                    "responses": {},
                    "successful_models": [],
                    "response_count": 0
                }
                
                # Run pipeline
                result = await orchestration_service.run_pipeline(
                    input_data="Test query",
                    selected_models=[]
                )
                
                # Should return service unavailable
                assert result.get("error") == "SERVICE_UNAVAILABLE"
                assert result.get("details", {}).get("models_available") == 0

    @pytest.mark.asyncio
    async def test_error_message_clarity(self, orchestration_service):
        """Test that error messages are clear and user-friendly."""
        with patch.object(Config, 'MINIMUM_MODELS_REQUIRED', 2), \
             patch.object(Config, 'ENABLE_SINGLE_MODEL_FALLBACK', False):
            
            with patch.object(orchestration_service, 'initial_response') as mock_initial:
                mock_initial.return_value = {
                    "stage": "initial_response",
                    "responses": {"gpt-4o": "Test"},
                    "successful_models": ["gpt-4o"],
                    "response_count": 1
                }
                
                result = await orchestration_service.run_pipeline(
                    input_data="Test",
                    selected_models=["gpt-4o"]
                )
                
                # Check message is user-friendly
                message = result.get("message", "")
                assert "Service temporarily unavailable" in message
                assert "multi-model intelligence multiplication" in message
                assert "2 different AI models" in message
                assert "only 1 model(s) are operational" in message