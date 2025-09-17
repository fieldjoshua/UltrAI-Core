"""
Fast E2E test with Big 3 providers.

This test verifies the full orchestration pipeline works with 
all three major providers (OpenAI, Anthropic, Google) using mocks.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from app.services.orchestration_service import OrchestrationService
from app.services.rate_limiter import RateLimiter
from app.services.quality_evaluation import QualityEvaluationService


@pytest.mark.asyncio
async def test_e2e_big3_orchestration():
    """Test end-to-end orchestration with Big 3 providers."""
    # Create orchestration service
    model_registry = Mock()
    quality_evaluator = QualityEvaluationService()
    rate_limiter = RateLimiter()
    
    orchestration_service = OrchestrationService(
        model_registry=model_registry,
        quality_evaluator=quality_evaluator,
        rate_limiter=rate_limiter
    )
    
    # Mock the model selection to return Big 3
    orchestration_service._default_models_from_env = AsyncMock(
        return_value=["gpt-4", "claude-3-5-sonnet-20241022", "gemini-1.5-flash"]
    )
    
    # Mock the LLM adapters
    mock_responses = {
        "gpt-4": {"generated_text": "OpenAI GPT-4 analysis: This is a comprehensive response."},
        "claude-3-5-sonnet-20241022": {"generated_text": "Claude 3.5 analysis: Here's my detailed perspective."},
        "gemini-1.5-flash": {"generated_text": "Gemini analysis: Let me provide insights on this."}
    }
    
    # Mock adapter creation
    def create_mock_adapter(model_name):
        adapter = Mock()
        adapter.generate = AsyncMock(return_value=mock_responses[model_name])
        return adapter
    
    # Patch the adapter creation
    with patch('app.services.orchestration_service.OpenAIAdapter', side_effect=lambda *args, **kwargs: create_mock_adapter('gpt-4')):
        with patch('app.services.orchestration_service.AnthropicAdapter', side_effect=lambda *args, **kwargs: create_mock_adapter('claude-3-5-sonnet-20241022')):
            with patch('app.services.orchestration_service.GeminiAdapter', side_effect=lambda *args, **kwargs: create_mock_adapter('gemini-1.5-flash')):
                # Mock environment variables
                with patch.dict('os.environ', {
                    'OPENAI_API_KEY': 'test-key',
                    'ANTHROPIC_API_KEY': 'test-key',
                    'GOOGLE_API_KEY': 'test-key'
                }):
                    # Run the pipeline
                    result = await orchestration_service.run_pipeline(
                        input_data="What are the key principles of effective software architecture?",
                        options={},
                        selected_models=["gpt-4", "claude-3-5-sonnet-20241022", "gemini-1.5-flash"]
                    )
    
    # Verify results
    assert isinstance(result, dict)
    assert "initial_response" in result
    assert "peer_review_and_revision" in result
    assert "ultra_synthesis" in result
    
    # Verify all three models participated in initial response
    initial_responses = result["initial_response"]
    if hasattr(initial_responses, "output"):
        responses = initial_responses.output.get("responses", {})
    else:
        responses = initial_responses.get("responses", {})
    
    assert len(responses) == 3
    assert "gpt-4" in responses
    assert "claude-3-5-sonnet-20241022" in responses
    assert "gemini-1.5-flash" in responses
    
    # Verify synthesis was created
    synthesis = result["ultra_synthesis"]
    if hasattr(synthesis, "output"):
        synthesis_output = synthesis.output
    else:
        synthesis_output = synthesis
    
    # Check that synthesis has content
    if isinstance(synthesis_output, dict) and "synthesis" in synthesis_output:
        assert synthesis_output["synthesis"]
    else:
        assert synthesis_output  # Should have some content
    
    print("✅ E2E test with Big 3 providers completed successfully!")


@pytest.mark.asyncio
async def test_e2e_big3_gating():
    """Test that service correctly enforces Big 3 gating."""
    # Create orchestration service
    model_registry = Mock()
    orchestration_service = OrchestrationService(
        model_registry=model_registry,
        rate_limiter=Mock()
    )
    
    # Test with only 2 providers (missing Google)
    orchestration_service._default_models_from_env = AsyncMock(
        return_value=["gpt-4", "claude-3-5-sonnet-20241022"]
    )
    
    # Mock adapter creation for available models
    with patch('app.services.orchestration_service.OpenAIAdapter'):
        with patch('app.services.orchestration_service.AnthropicAdapter'):
            with patch.dict('os.environ', {
                'OPENAI_API_KEY': 'test-key',
                'ANTHROPIC_API_KEY': 'test-key',
                'MINIMUM_MODELS_REQUIRED': '3'
            }):
                result = await orchestration_service.run_pipeline(
                    input_data="Test query",
                    options={},
                    selected_models=["gpt-4", "claude-3-5-sonnet-20241022"]
                )
    
    # Should return SERVICE_UNAVAILABLE
    assert isinstance(result, dict)
    assert result.get("error") == "SERVICE_UNAVAILABLE"
    assert "Insufficient healthy models" in result.get("message", "")
    
    print("✅ Gating test passed - correctly rejected with only 2 models!")


if __name__ == "__main__":
    # Run tests
    asyncio.run(test_e2e_big3_orchestration())
    asyncio.run(test_e2e_big3_gating())
    print("✅ All E2E tests passed!")