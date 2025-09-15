import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.api_failure_handler import APIFailureHandler, APIProvider
from app.services.cache_service import CacheService


@pytest.mark.unit
@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_statistics_initial():
    handler = APIFailureHandler()
    stats = handler.get_statistics()
    assert stats["total_calls"] == 0
    assert stats["successful_calls"] == 0
    assert stats["failed_calls"] == 0
    assert stats["cache_hits"] == 0


@pytest.mark.unit
@pytest.mark.asyncio
async def test_execute_api_call_cache_hit(monkeypatch):
    handler = APIFailureHandler()
    # Create mock cache service
    mock_cache = CacheService()
    mock_cache.aget = AsyncMock(return_value="cached")
    
    # Replace cache_service with our mock
    import app.services.api_failure_handler
    app.services.api_failure_handler.cache_service = mock_cache
    
    # Ensure _call_provider is not called
    handler._call_provider = AsyncMock()
    result = await handler.execute_api_call(
        APIProvider.OPENAI, AsyncMock(), operation="op"
    )
    assert result == "cached"
    stats = handler.get_statistics()
    assert stats["cache_hits"] == 1
    assert stats["total_calls"] == 1


@pytest.mark.unit
@pytest.mark.asyncio
async def test_execute_api_call_provider_success(monkeypatch):
    handler = APIFailureHandler()
    # Create mock cache service with no cache hit
    mock_cache = CacheService()
    mock_cache.aget = AsyncMock(return_value=None)
    mock_cache.aset = AsyncMock()
    
    # Replace cache_service with our mock
    import app.services.api_failure_handler
    app.services.api_failure_handler.cache_service = mock_cache
    
    # Stub provider call
    handler._call_provider = AsyncMock(return_value={"data": 123})
    
    result = await handler.execute_api_call(
        APIProvider.ANTHROPIC, AsyncMock(), operation="gen"
    )
    assert result == {"data": 123}
    stats = handler.get_statistics()
    assert stats["successful_calls"] == 1
    assert stats["provider_statistics"]["anthropic"]["success"] == 1
    assert stats["total_calls"] == 1
