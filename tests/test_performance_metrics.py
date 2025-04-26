import pytest
import asyncio
from datetime import datetime
from src.orchestrator import TriLLMOrchestrator
from src.models import ModelResponse, QualityMetrics


class MockPerformanceLLMClient:
    def __init__(self, name, response_time=0.1):
        self.name = name
        self.response_time = response_time
        self.calls = 0

    async def generate(self, prompt):
        self.calls += 1
        await asyncio.sleep(self.response_time)
        return f"Response from {self.name}"


@pytest.fixture
def performance_orchestrator():
    return TriLLMOrchestrator(
        llama_client=MockPerformanceLLMClient("Llama", 0.1),
        chatgpt_client=MockPerformanceLLMClient("ChatGPT", 0.2),
        gemini_client=MockPerformanceLLMClient("Gemini", 0.3),
        cache_enabled=True,
    )


@pytest.mark.asyncio
async def test_response_time_tracking(performance_orchestrator):
    prompt = "Test performance"
    await performance_orchestrator.process_responses(prompt)

    metrics = performance_orchestrator.metrics
    assert "response_times" in metrics
    assert len(metrics["response_times"]) > 0

    # Verify response times are being tracked
    for time in metrics["response_times"]:
        assert isinstance(time, float)
        assert time >= 0.0


@pytest.mark.asyncio
async def test_success_rate_tracking(performance_orchestrator):
    prompt = "Test success rates"
    await performance_orchestrator.process_responses(prompt)

    metrics = performance_orchestrator.metrics
    assert "success_rates" in metrics

    # Verify success rates for each model
    for model in ["Llama", "ChatGPT", "Gemini"]:
        assert model in metrics["success_rates"]
        assert "success" in metrics["success_rates"][model]
        assert "total" in metrics["success_rates"][model]
        assert metrics["success_rates"][model]["success"] > 0
        assert metrics["success_rates"][model]["total"] > 0


@pytest.mark.asyncio
async def test_token_usage_tracking(performance_orchestrator):
    prompt = "Test token usage"
    await performance_orchestrator.process_responses(prompt)

    metrics = performance_orchestrator.metrics
    assert "token_usage" in metrics

    # Verify token usage for each model
    for model in ["Llama", "ChatGPT", "Gemini"]:
        assert model in metrics["token_usage"]
        assert metrics["token_usage"][model] > 0


@pytest.mark.asyncio
async def test_quality_score_tracking(performance_orchestrator):
    prompt = "Test quality scores"
    await performance_orchestrator.process_responses(prompt)

    metrics = performance_orchestrator.metrics
    assert "quality_scores" in metrics

    # Verify quality scores for each model
    for model in ["Llama", "ChatGPT", "Gemini"]:
        assert model in metrics["quality_scores"]
        assert len(metrics["quality_scores"][model]) > 0
        for score in metrics["quality_scores"][model]:
            assert 0 <= score <= 1


@pytest.mark.asyncio
async def test_metrics_persistence(performance_orchestrator):
    # First run
    prompt1 = "Test persistence 1"
    await performance_orchestrator.process_responses(prompt1)

    # Second run
    prompt2 = "Test persistence 2"
    await performance_orchestrator.process_responses(prompt2)

    metrics = performance_orchestrator.metrics

    # Verify metrics are accumulating
    assert len(metrics["response_times"]) > 3  # At least 3 responses per run
    assert metrics["success_rates"]["Llama"]["total"] > 1
    assert metrics["token_usage"]["Llama"] > 0
    assert len(metrics["quality_scores"]["Llama"]) > 1


@pytest.mark.asyncio
async def test_metrics_reset(performance_orchestrator):
    # Initial run
    prompt = "Test reset"
    await performance_orchestrator.process_responses(prompt)

    # Reset metrics
    performance_orchestrator.metrics = {
        "response_times": [],
        "success_rates": {},
        "token_usage": {},
        "quality_scores": {},
    }

    # Verify reset
    metrics = performance_orchestrator.metrics
    assert len(metrics["response_times"]) == 0
    assert len(metrics["success_rates"]) == 0
    assert len(metrics["token_usage"]) == 0
    assert len(metrics["quality_scores"]) == 0
