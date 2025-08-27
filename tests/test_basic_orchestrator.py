import pytest
import os
from unittest.mock import Mock, AsyncMock, patch
from app.services.orchestration_service import OrchestrationService
from app.services.model_registry import ModelRegistry
from app.services.quality_evaluation import QualityEvaluationService
from app.services.rate_limiter import RateLimiter


@pytest.fixture
def orchestrator():
    """Create an orchestration service with mocked dependencies."""
    model_registry = Mock(spec=ModelRegistry)
    quality_evaluator = Mock(spec=QualityEvaluationService)
    rate_limiter = Mock(spec=RateLimiter)
    
    # Configure rate limiter mock to handle async calls
    rate_limiter.acquire = AsyncMock(return_value=None)
    rate_limiter.release = AsyncMock(return_value=None)
    rate_limiter.get_endpoint_stats = Mock(return_value={})
    rate_limiter.register_endpoint = Mock(return_value=None)
    
    orchestrator = OrchestrationService(
        model_registry=model_registry,
        quality_evaluator=quality_evaluator,
        rate_limiter=rate_limiter
    )
    
    return orchestrator


@pytest.fixture(autouse=True)
def env_keys(monkeypatch):
    # Set test environment with mock keys
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    monkeypatch.setenv("GOOGLE_API_KEY", "test-key")
    monkeypatch.setenv("USE_MOCK", "true")
    monkeypatch.setenv("MOCK_MODE", "true")
    return monkeypatch


@pytest.mark.asyncio
async def test_orchestrate_basic_success(orchestrator, monkeypatch):
    # Mock the LLM adapters to return test responses
    with patch('app.services.orchestration_service.OpenAIAdapter') as mock_openai:
        mock_adapter = AsyncMock()
        mock_adapter.generate = AsyncMock(return_value={"generated_text": "Test response from GPT-4"})
        mock_openai.return_value = mock_adapter
        
        # Run the pipeline
        result = await orchestrator.run_pipeline(
            input_data="hi",
            selected_models=["gpt-4o"]
        )
        
        # Check that pipeline ran successfully
        assert "initial_response" in result
        assert result["initial_response"].error is None
        assert result["initial_response"].output is not None


@pytest.mark.asyncio
async def test_orchestrate_basic_empty_prompt(orchestrator):
    # Empty prompt should still be processed (the service doesn't validate prompt content)
    result = await orchestrator.run_pipeline(
        input_data="",
        selected_models=["gpt-4o"]
    )
    # Pipeline should still run but may have errors or empty responses
    assert "initial_response" in result


@pytest.mark.asyncio
async def test_orchestrate_basic_no_models_defaults(orchestrator, env_keys):
    # When no models are specified, it should use default models from environment
    with patch('app.services.orchestration_service.OpenAIAdapter') as mock_openai, \
         patch('app.services.orchestration_service.AnthropicAdapter') as mock_anthropic:
        
        mock_openai_adapter = AsyncMock()
        mock_openai_adapter.generate = AsyncMock(return_value={"generated_text": "Test GPT response"})
        mock_openai.return_value = mock_openai_adapter
        
        mock_anthropic_adapter = AsyncMock()
        mock_anthropic_adapter.generate = AsyncMock(return_value={"generated_text": "Test Claude response"})
        mock_anthropic.return_value = mock_anthropic_adapter
        
        # Call with None for models (should use defaults)
        result = await orchestrator.run_pipeline(
            input_data="hello",
            selected_models=None
        )
        
        assert "initial_response" in result
        assert result["initial_response"].error is None
