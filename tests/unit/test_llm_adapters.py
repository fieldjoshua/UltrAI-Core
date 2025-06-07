import pytest
import httpx
from app.services.llm_adapters import (
    BaseAdapter,
    OpenAIAdapter,
    AnthropicAdapter,
    GeminiAdapter,
    CLIENT,
)


@pytest.mark.asyncio
async def test_base_adapter_missing_api_key():
    with pytest.raises(ValueError):
        BaseAdapter(api_key="", model="m")


@pytest.mark.asyncio
async def test_openai_adapter_error(monkeypatch):
    adapter = OpenAIAdapter(api_key="key", model="m")

    class Dummy:
        def raise_for_status(self):
            raise httpx.ReadTimeout("timeout")

        def json(self):
            return {}

    async def dummy_post(*args, **kwargs):
        return Dummy()

    monkeypatch.setattr(CLIENT, "post", dummy_post)
    result = await adapter.generate("prompt")
    assert "generated_text" in result


@pytest.mark.asyncio
async def test_anthropic_adapter_error(monkeypatch):
    adapter = AnthropicAdapter(api_key="key", model="m")

    class Dummy:
        def raise_for_status(self):
            raise httpx.ReadTimeout("timeout")

        def json(self):
            return {}

    async def dummy_post(*args, **kwargs):
        return Dummy()

    monkeypatch.setattr(CLIENT, "post", dummy_post)
    result = await adapter.generate("prompt")
    assert "generated_text" in result


@pytest.mark.asyncio
async def test_gemini_adapter_error(monkeypatch):
    adapter = GeminiAdapter(api_key="key", model="m")

    class Dummy:
        def raise_for_status(self):
            raise httpx.ReadTimeout("timeout")

        def json(self):
            return {}

    async def dummy_post(*args, **kwargs):
        return Dummy()

    monkeypatch.setattr(CLIENT, "post", dummy_post)
    result = await adapter.generate("prompt")
    assert "generated_text" in result
