import pytest
import asyncio
from src.orchestrator import TriLLMOrchestrator
from src.models import ModelResponse, QualityMetrics


class MockErrorLLMClient:
    def __init__(self, name, error_type=None):
        self.name = name
        self.error_type = error_type
        self.calls = 0

    async def generate(self, prompt):
        self.calls += 1
        if self.error_type == "timeout":
            await asyncio.sleep(10)  # Simulate timeout
        elif self.error_type == "value":
            raise ValueError("Invalid input")
        elif self.error_type == "connection":
            raise ConnectionError("Connection failed")
        return f"Response from {self.name}"


@pytest.fixture
def error_orchestrator():
    return TriLLMOrchestrator(
        llama_client=MockErrorLLMClient("Llama", "timeout"),
        chatgpt_client=MockErrorLLMClient("ChatGPT", "value"),
        gemini_client=MockErrorLLMClient("Gemini", "connection"),
        cache_enabled=True,
        max_retries=2,
    )


@pytest.mark.asyncio
async def test_timeout_handling(error_orchestrator):
    with pytest.raises(asyncio.TimeoutError):
        await error_orchestrator.get_model_response(
            error_orchestrator.llama, "test prompt", "test"
        )


@pytest.mark.asyncio
async def test_value_error_handling(error_orchestrator):
    with pytest.raises(ValueError):
        await error_orchestrator.get_model_response(
            error_orchestrator.chatgpt, "test prompt", "test"
        )


@pytest.mark.asyncio
async def test_connection_error_handling(error_orchestrator):
    with pytest.raises(ConnectionError):
        await error_orchestrator.get_model_response(
            error_orchestrator.gemini, "test prompt", "test"
        )


@pytest.mark.asyncio
async def test_retry_mechanism(error_orchestrator):
    # Test that retries are attempted
    with pytest.raises(ConnectionError):
        await error_orchestrator.get_model_response(
            error_orchestrator.gemini, "test prompt", "test"
        )
    assert error_orchestrator.gemini.calls == 2  # Should have retried once


@pytest.mark.asyncio
async def test_invalid_prompt_handling(error_orchestrator):
    with pytest.raises(ValueError):
        await error_orchestrator.process_responses("")


@pytest.mark.asyncio
async def test_none_prompt_handling(error_orchestrator):
    with pytest.raises(ValueError):
        await error_orchestrator.process_responses(None)


@pytest.mark.asyncio
async def test_empty_response_handling(error_orchestrator):
    with pytest.raises(ValueError):
        await error_orchestrator.process_responses("   ")  # Only whitespace


@pytest.mark.asyncio
async def test_quality_evaluation_error(error_orchestrator):
    response = ModelResponse(
        model_name="TestModel",
        content="",  # Empty content should cause evaluation error
        stage="test",
        timestamp=0,
    )

    with pytest.raises(ValueError):
        await error_orchestrator.evaluate_quality(response)
