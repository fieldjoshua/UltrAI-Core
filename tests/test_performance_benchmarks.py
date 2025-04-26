import pytest
import asyncio
import time
from datetime import datetime
from src.orchestrator import TriLLMOrchestrator
from src.models import ModelResponse, QualityMetrics


class MockBenchmarkLLMClient:
    def __init__(self, name, response_time=0.1):
        self.name = name
        self.response_time = response_time
        self.calls = 0

    async def generate(self, prompt):
        self.calls += 1
        await asyncio.sleep(self.response_time)
        return f"Response from {self.name} for: {prompt}"


@pytest.fixture
def benchmark_orchestrator():
    return TriLLMOrchestrator(
        llama_client=MockBenchmarkLLMClient("Llama", 0.1),
        chatgpt_client=MockBenchmarkLLMClient("ChatGPT", 0.2),
        gemini_client=MockBenchmarkLLMClient("Gemini", 0.3),
        cache_enabled=True,
    )


@pytest.mark.asyncio
async def test_response_time_benchmark(benchmark_orchestrator):
    prompt = "Test response time"
    start_time = time.time()

    result = await benchmark_orchestrator.process_responses(prompt)

    end_time = time.time()
    total_time = end_time - start_time

    # Verify total response time is within expected range
    # Expected time: sum of all model response times + overhead
    expected_min = 0.1 + 0.2 + 0.3  # Sum of model response times
    expected_max = expected_min * 1.5  # Allow 50% overhead

    assert expected_min <= total_time <= expected_max

    # Verify individual response times
    metrics = result["metrics"]
    assert len(metrics["response_times"]) > 0
    for time in metrics["response_times"]:
        assert isinstance(time, float)
        assert time >= 0.0


@pytest.mark.asyncio
async def test_concurrent_requests(benchmark_orchestrator):
    prompts = [f"Test concurrent {i}" for i in range(5)]

    start_time = time.time()

    # Run multiple requests concurrently
    results = await asyncio.gather(
        *[benchmark_orchestrator.process_responses(prompt) for prompt in prompts]
    )

    end_time = time.time()
    total_time = end_time - start_time

    # Verify all requests completed successfully
    for result in results:
        assert result["status"] == "success"

    # Verify total time is less than sequential execution
    sequential_time = (0.1 + 0.2 + 0.3) * len(prompts)
    assert total_time < sequential_time


@pytest.mark.asyncio
async def test_cache_performance(benchmark_orchestrator):
    prompt = "Test cache performance"

    # First call (no cache)
    start_time1 = time.time()
    result1 = await benchmark_orchestrator.process_responses(prompt)
    end_time1 = time.time()
    time1 = end_time1 - start_time1

    # Second call (with cache)
    start_time2 = time.time()
    result2 = await benchmark_orchestrator.process_responses(prompt)
    end_time2 = time.time()
    time2 = end_time2 - start_time2

    # Verify cached call is faster
    assert time2 < time1

    # Verify results are identical
    assert result1["initial_responses"] == result2["initial_responses"]
    assert result1["meta_responses"] == result2["meta_responses"]
    assert result1["final_synthesis"] == result2["final_synthesis"]


@pytest.mark.asyncio
async def test_memory_usage(benchmark_orchestrator):
    import psutil
    import os

    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss

    # Run multiple requests
    prompts = [f"Test memory {i}" for i in range(10)]
    for prompt in prompts:
        await benchmark_orchestrator.process_responses(prompt)

    final_memory = process.memory_info().rss
    memory_increase = final_memory - initial_memory

    # Verify memory usage is reasonable (less than 100MB)
    assert memory_increase < 100 * 1024 * 1024  # 100MB in bytes


@pytest.mark.asyncio
async def test_error_recovery_performance(benchmark_orchestrator):
    # Test performance with error recovery
    start_time = time.time()

    # Run multiple requests with potential errors
    prompts = ["", None, "   ", "Valid prompt"]
    results = []

    for prompt in prompts:
        try:
            result = await benchmark_orchestrator.process_responses(prompt)
            results.append(result)
        except ValueError:
            continue

    end_time = time.time()
    total_time = end_time - start_time

    # Verify error handling doesn't significantly impact performance
    assert total_time < 2.0  # Should complete within 2 seconds

    # Verify successful requests completed
    assert len(results) > 0
    for result in results:
        assert result["status"] == "success"
