import sys
import types

# Create dummy errors module
err_mod = types.ModuleType("app.utils.errors")


class LLMError(Exception):
    pass


class NetworkError(Exception):
    pass


class SystemError(Exception):
    pass


setattr(err_mod, "LLMError", LLMError)
setattr(err_mod, "NetworkError", NetworkError)
setattr(err_mod, "SystemError", SystemError)
sys.modules["app.utils.errors"] = err_mod

import pytest
from unittest.mock import AsyncMock
from app.services.api_failure_handler import APIFailureHandler, APIProvider


@pytest.mark.asyncio
async def test_get_statistics_initial():
    handler = APIFailureHandler()
    stats = handler.get_statistics()
    assert stats["total_calls"] == 0
    assert stats["successful_calls"] == 0
    assert stats["failed_calls"] == 0
    assert stats["cache_hits"] == 0


@pytest.mark.asyncio
async def test_execute_api_call_cache_hit(monkeypatch):
    handler = APIFailureHandler()
    # Stub cache_service.get to return cached response
    monkeypatch.setattr(
        "app.services.api_failure_handler.cache_service.get",
        AsyncMock(return_value="cached"),
    )
    # Ensure _call_provider is not called
    handler._call_provider = AsyncMock()
    result = await handler.execute_api_call(
        APIProvider.OPENAI, AsyncMock(), operation="op"
    )
    assert result == "cached"
    stats = handler.get_statistics()
    assert stats["cache_hits"] == 1
    assert stats["total_calls"] == 1


@pytest.mark.asyncio
async def test_execute_api_call_provider_success(monkeypatch):
    handler = APIFailureHandler()
    # No cache hit
    monkeypatch.setattr(
        "app.services.api_failure_handler.cache_service.get",
        AsyncMock(return_value=None),
    )
    # Stub provider call
    handler._call_provider = AsyncMock(return_value={"data": 123})
    # Stub cache_service.set to no-op
    monkeypatch.setattr(
        "app.services.api_failure_handler.cache_service.set", AsyncMock()
    )
    result = await handler.execute_api_call(
        APIProvider.ANTHROPIC, AsyncMock(), operation="gen"
    )
    assert result == {"data": 123}
    stats = handler.get_statistics()
    assert stats["successful_calls"] == 1
    assert stats["provider_statistics"]["anthropic"]["success"] == 1
    assert stats["total_calls"] == 1
