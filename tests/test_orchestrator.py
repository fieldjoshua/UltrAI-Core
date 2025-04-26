import asyncio
from unittest.mock import Mock, patch
from datetime import datetime

import pytest

from ..config import Config
from ..models import ModelResponse, QualityMetrics
from ..orchestrator import TriLLMOrchestrator
from ..models import ResponseCache


@pytest.fixture
def config():
    return Config("tests/test_config.yaml")


@pytest.fixture
async def orchestrator(config):
    mock_llama = Mock()
    mock_chatgpt = Mock()
    mock_gemini = Mock()

    orchestrator = TriLLMOrchestrator(
        mock_llama, mock_chatgpt, mock_gemini, config.orchestrator
    )

    return orchestrator


@pytest.mark.asyncio
async def test_get_model_response(orchestrator):
    mock_model = Mock()
    mock_model.generate.return_value = "Test response"

    response = await orchestrator.get_model_response(mock_model, "Test prompt", "test")

    assert isinstance(response, ModelResponse)
    assert response.content == "Test response"
    assert response.stage == "test"


@pytest.mark.asyncio
async def test_process_responses_success(orchestrator):
    # Setup mock responses
    orchestrator.llama.generate.return_value = "Llama response"
    orchestrator.chatgpt.generate.return_value = "ChatGPT response"
    orchestrator.gemini.generate.return_value = "Gemini response"

    result = await orchestrator.process_responses("Test prompt")

    assert result["status"] == "success"
    assert len(result["initial_responses"]) == 3
    assert result["final_synthesis"] is not None


class MockLLMClient:
    def __init__(self, name, response_delay=0.1):
        self.name = name
        self.response_delay = response_delay
        self.calls = 0

    async def generate(self, prompt):
        self.calls += 1
        await asyncio.sleep(self.response_delay)
        return f"Response from {self.name} for: {prompt}"


@pytest.fixture
def mock_clients():
    return {
        "llama": MockLLMClient("Llama"),
        "chatgpt": MockLLMClient("ChatGPT"),
        "gemini": MockLLMClient("Gemini"),
    }


@pytest.fixture
def orchestrator(mock_clients):
    return TriLLMOrchestrator(
        llama_client=mock_clients["llama"],
        chatgpt_client=mock_clients["chatgpt"],
        gemini_client=mock_clients["gemini"],
        cache_enabled=True,
    )


@pytest.mark.asyncio
async def test_orchestrator_initialization(orchestrator):
    assert orchestrator.llama is not None
    assert orchestrator.chatgpt is not None
    assert orchestrator.gemini is not None
    assert orchestrator.cache is not None
    assert orchestrator.max_retries == 3


@pytest.mark.asyncio
async def test_get_model_response(orchestrator):
    prompt = "Test prompt"
    response = await orchestrator.get_model_response(
        orchestrator.chatgpt, prompt, "test"
    )

    assert isinstance(response, ModelResponse)
    assert response.model_name == "MockLLMClient"
    assert response.stage == "test"
    assert response.content.startswith("Response from ChatGPT")
    assert response.tokens_used > 0
    assert isinstance(response.quality, QualityMetrics)


@pytest.mark.asyncio
async def test_response_caching(orchestrator):
    prompt = "Cache test prompt"

    # First call
    response1 = await orchestrator.get_model_response(
        orchestrator.chatgpt, prompt, "test"
    )

    # Second call should use cache
    response2 = await orchestrator.get_model_response(
        orchestrator.chatgpt, prompt, "test"
    )

    assert response1.content == response2.content
    assert orchestrator.chatgpt.calls == 1  # Only one actual API call


@pytest.mark.asyncio
async def test_quality_evaluation(orchestrator):
    response = ModelResponse(
        model_name="TestModel",
        content="This is a test response with technical details and strategic insights.",
        stage="test",
        timestamp=datetime.now().timestamp(),
    )

    quality = await orchestrator.evaluate_quality(response)
    assert isinstance(quality, QualityMetrics)
    assert 0 <= quality.coherence_score <= 1
    assert 0 <= quality.technical_depth <= 1
    assert 0 <= quality.strategic_value <= 1
    assert 0 <= quality.uniqueness <= 1


@pytest.mark.asyncio
async def test_process_responses(orchestrator):
    prompt = "Test processing pipeline"
    result = await orchestrator.process_responses(prompt)

    assert result["status"] == "success"
    assert "initial_responses" in result
    assert "meta_responses" in result
    assert "final_synthesis" in result
    assert "metrics" in result
    assert "timestamp" in result

    # Verify all models were called
    assert orchestrator.llama.calls > 0
    assert orchestrator.chatgpt.calls > 0
    assert orchestrator.gemini.calls > 0


@pytest.mark.asyncio
async def test_error_handling(orchestrator):
    # Test with invalid prompt
    with pytest.raises(ValueError):
        await orchestrator.process_responses("")

    # Test with None prompt
    with pytest.raises(ValueError):
        await orchestrator.process_responses(None)


@pytest.mark.asyncio
async def test_metrics_tracking(orchestrator):
    prompt = "Test metrics"
    await orchestrator.process_responses(prompt)

    metrics = orchestrator.metrics
    assert "response_times" in metrics
    assert "success_rates" in metrics
    assert "token_usage" in metrics
    assert "quality_scores" in metrics

    # Verify metrics are being collected
    assert len(metrics["response_times"]) > 0
    assert "MockLLMClient" in metrics["success_rates"]
    assert "MockLLMClient" in metrics["token_usage"]
    assert "MockLLMClient" in metrics["quality_scores"]
