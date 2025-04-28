import pytest
from src.orchestrator import MultiLLMOrchestrator

# pylint: disable=assert-used


def check_equals(actual, expected, message=None):
    """Custom assertion helper to check equality without using 'assert'"""
    if actual != expected:
        msg = f"Expected {expected}, got {actual}"
        if message:
            msg = f"{message}: {msg}"
        pytest.fail(msg)


def check_contains(container, item, message=None):
    """Custom assertion helper to check contains without using 'assert'"""
    if item not in container:
        msg = f"Expected {container} to contain {item}"
        if message:
            msg = f"{message}: {msg}"
        pytest.fail(msg)


class MockLLM:
    def __init__(self, name):
        self.name = name

    async def generate(self, prompt):
        return f"{self.name} response to: {prompt}"


@pytest.mark.asyncio
async def test_multi_llm_orchestrator_basic():
    orchestrator = MultiLLMOrchestrator()
    orchestrator.register_model("llama", MockLLM("llama"))
    orchestrator.register_model("chatgpt", MockLLM("chatgpt"))
    orchestrator.register_model("gemini", MockLLM("gemini"))

    prompt = "Test prompt"
    results = await orchestrator.process_responses(prompt)

    check_equals(results["status"], "success")
    check_equals(len(results["initial_responses"]), 3)
    check_contains(results, "final_synthesis")


@pytest.mark.asyncio
async def test_orchestrator_error_handling():
    class FailingLLM:
        async def generate(self, prompt):
            raise RuntimeError("Model failure")

    orchestrator = MultiLLMOrchestrator(max_retries=2)
    orchestrator.register_model("failing_model", FailingLLM())

    prompt = "Test prompt"
    with pytest.raises(RuntimeError, match="All attempts failed for model"):
        await orchestrator.process_responses(prompt)


@pytest.mark.asyncio
async def test_orchestrator_cache_functionality():
    class CachingLLM:
        async def generate(self, prompt):
            return "Cached response"

    orchestrator = MultiLLMOrchestrator()
    orchestrator.register_model("caching_model", CachingLLM())

    prompt = "Test prompt"
    # First call to populate cache
    await orchestrator.process_responses(prompt)
    # Second call should hit cache
    results = await orchestrator.process_responses(prompt)

    check_equals(results["status"], "success")
    check_equals(len(results["initial_responses"]), 1)
    check_equals(results["initial_responses"][0]["content"], "Cached response")


@pytest.mark.asyncio
async def test_orchestrator_pipeline_stages():
    orchestrator = MultiLLMOrchestrator()
    orchestrator.register_model("llama", MockLLM("llama"))

    prompt = "Test prompt"
    stages = ["initial", "meta", "synthesis"]
    results = await orchestrator.process_responses(prompt, stages=stages)

    check_equals(results["status"], "success")
    check_equals(len(results["initial_responses"]), 1)
    check_contains(results, "meta_responses")
    check_contains(results, "final_synthesis")


@pytest.mark.asyncio
async def test_orchestrator_model_prioritization():
    orchestrator = MultiLLMOrchestrator()

    # Register models with different weights
    orchestrator.register_model("llama", MockLLM("llama"), weight=1.0)
    orchestrator.register_model("chatgpt", MockLLM("chatgpt"), weight=3.0)
    orchestrator.register_model("gemini", MockLLM("gemini"), weight=2.0)

    # Get prioritized models list
    prioritized_models = orchestrator.get_prioritized_models()

    # Check that models are sorted by weight (highest first)
    check_equals(prioritized_models[0], "chatgpt")
    check_equals(prioritized_models[1], "gemini")
    check_equals(prioritized_models[2], "llama")

    # Update weight for llama
    orchestrator.set_model_weight("llama", 4.0)

    # Check updated prioritization
    updated_prioritized_models = orchestrator.get_prioritized_models()
    check_equals(updated_prioritized_models[0], "llama")

    # Run process with only specific models
    prompt = "Test prompt"
    results = await orchestrator.process_responses(prompt, models=["llama", "gemini"])

    # Check that only the specified models were used
    check_equals(len(results["initial_responses"]), 2)

    # Models should be used in priority order (highest weight first)
    model_names = [r["model_name"] for r in results["initial_responses"]]
    check_equals(model_names[0], "MockLLM")
