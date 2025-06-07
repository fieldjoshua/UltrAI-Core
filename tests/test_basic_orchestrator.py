import sys
import types


# Define a dummy adapter class for testing
class DummyAdapter:
    def __init__(self, api_key, model):
        self.api_key = api_key
        self.model = model

    async def generate(self, prompt):
        return {"generated_text": f"resp_{self.model}"}


# Inject dummy llm_adapter module to satisfy BasicOrchestrator imports
module_name = "app.models.llm_adapter"
llm_adapter_mod = types.ModuleType(module_name)
setattr(llm_adapter_mod, "OpenAIAdapter", DummyAdapter)
setattr(llm_adapter_mod, "AnthropicAdapter", DummyAdapter)
setattr(llm_adapter_mod, "GeminiAdapter", DummyAdapter)
sys.modules[module_name] = llm_adapter_mod

import pytest
from app.services.basic_orchestrator import BasicOrchestrator


@pytest.fixture(autouse=True)
def env_keys(monkeypatch):
    # Ensure only OpenAI key is set for this test
    monkeypatch.setenv("OPENAI_API_KEY", "key")
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    return monkeypatch


@pytest.mark.asyncio
async def test_orchestrate_basic_success(env_keys, monkeypatch):
    # Patch the underlying OpenAIAdapter to our dummy
    monkeypatch.setattr("app.services.basic_orchestrator.OpenAIAdapter", DummyAdapter)
    orchestrator = BasicOrchestrator()
    result = await orchestrator.orchestrate_basic("hi", ["gpt4o"])
    assert result["status"] == "success"
    # Should have model_responses with correct mapping
    assert "gpt4o" in result["model_responses"]
    assert result["model_responses"]["gpt4o"] == "resp_gpt-4"


@pytest.mark.asyncio
async def test_orchestrate_basic_empty_prompt(env_keys):
    orchestrator = BasicOrchestrator()
    with pytest.raises(ValueError):
        await orchestrator.orchestrate_basic("", ["gpt4o"])


@pytest.mark.asyncio
async def test_orchestrate_basic_no_models_defaults(env_keys, monkeypatch):
    # Patch adapter and test default models path
    monkeypatch.setattr("app.services.basic_orchestrator.OpenAIAdapter", DummyAdapter)
    orchestrator = BasicOrchestrator()
    # Call with empty models list, should use defaults
    result = await orchestrator.orchestrate_basic("hello", [])
    assert result["status"] == "success"
    # Default list includes gpt4o and claude37, but we only patched OpenAIAdapter
    assert "gpt4o" in result["model_responses"]
