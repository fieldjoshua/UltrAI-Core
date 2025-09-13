import os
import pytest

from app.services.llm_adapter_factory import LLMAdapterFactory


pytestmark = pytest.mark.live


def _has(key: str) -> bool:
    return bool(os.getenv(key))


@pytest.mark.asyncio
@pytest.mark.skipif(not _has("OPENAI_API_KEY"), reason="OPENAI_API_KEY not set")
async def test_openai_smoke():
    adapter = LLMAdapterFactory.create_adapter(
        provider="openai",
        api_key=os.environ["OPENAI_API_KEY"],
        model="gpt-4o",
    )
    result = await adapter.generate("Say 'ok' once.")
    assert result is not None


@pytest.mark.asyncio
@pytest.mark.skipif(not _has("ANTHROPIC_API_KEY"), reason="ANTHROPIC_API_KEY not set")
async def test_anthropic_smoke():
    adapter = LLMAdapterFactory.create_adapter(
        provider="anthropic",
        api_key=os.environ["ANTHROPIC_API_KEY"],
        model="claude-3-5-haiku-20241022",
    )
    result = await adapter.generate("Say 'ok' once.")
    assert result is not None


@pytest.mark.asyncio
@pytest.mark.skipif(not _has("GOOGLE_API_KEY"), reason="GOOGLE_API_KEY not set")
async def test_gemini_smoke():
    adapter = LLMAdapterFactory.create_adapter(
        provider="google",
        api_key=os.environ["GOOGLE_API_KEY"],
        model="gemini-1.5-pro",
    )
    result = await adapter.generate("Say 'ok' once.")
    assert result is not None


@pytest.mark.asyncio
@pytest.mark.skipif(not _has("HUGGINGFACE_API_KEY"), reason="HUGGINGFACE_API_KEY not set")
async def test_huggingface_smoke():
    adapter = LLMAdapterFactory.create_adapter(
        provider="huggingface",
        api_key=os.environ["HUGGINGFACE_API_KEY"],
        model="mistralai/Mistral-7B-Instruct-v0.1",
    )
    result = await adapter.generate("Say 'ok' once.")
    assert result is not None
