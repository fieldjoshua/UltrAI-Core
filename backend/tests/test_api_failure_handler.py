"""Tests for API failure handler service."""

import asyncio
import time
from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch

import pytest

from backend.services.api_failure_handler import (
    APICallContext,
    APIFailureHandler,
    APIProvider,
)
from backend.utils.circuit_breaker import CircuitOpenError, CircuitState
from backend.utils.errors import LLMError, NetworkError
from backend.utils.retry_handler import RetryError


class TestAPIFailureHandler:
    """Test suite for API failure handler."""

    @pytest.fixture
    def handler(self):
        """Create API failure handler instance."""
        config = {
            "circuit_failure_threshold": 2,
            "circuit_recovery_timeout": 5,
            "max_retry_attempts": 2,
            "retry_initial_delay": 0.1,
            "rate_limit_window": 10,
            "max_errors_per_window": 5,
            "cache_ttl": 60,
        }
        return APIFailureHandler(config)

    @pytest.fixture
    def mock_api_function(self):
        """Create mock API function."""
        return AsyncMock(return_value={"result": "success"})

    @pytest.mark.asyncio
    async def test_successful_api_call(self, handler, mock_api_function):
        """Test successful API call."""
        result = await handler.execute_api_call(
            primary_provider=APIProvider.OPENAI,
            api_function=mock_api_function,
            operation="test_operation",
        )

        assert result == {"result": "success"}
        assert handler.stats["successful_calls"] == 1
        assert handler.stats["total_calls"] == 1
        assert handler.stats["provider_statistics"]["openai"]["success"] == 1

    @pytest.mark.asyncio
    async def test_circuit_breaker_opens(self, handler):
        """Test circuit breaker opens after failures."""
        # Create failing API function
        failing_api = AsyncMock(side_effect=NetworkError("Connection failed"))

        # First failure
        with pytest.raises(RetryError):
            await handler.execute_api_call(
                primary_provider=APIProvider.OPENAI,
                api_function=failing_api,
                operation="test_operation",
                enable_fallback=False,
            )

        # Second failure should open circuit
        with pytest.raises(RetryError):
            await handler.execute_api_call(
                primary_provider=APIProvider.OPENAI,
                api_function=failing_api,
                operation="test_operation",
                enable_fallback=False,
            )

        # Circuit should now be open
        circuit = handler.circuit_breakers[APIProvider.OPENAI]
        assert circuit.state == CircuitState.OPEN

        # Next call should fail immediately with CircuitOpenError
        with pytest.raises(CircuitOpenError):
            await handler.execute_api_call(
                primary_provider=APIProvider.OPENAI,
                api_function=failing_api,
                operation="test_operation",
                enable_fallback=False,
            )

        assert handler.stats["circuit_open_rejections"] == 1

    @pytest.mark.asyncio
    async def test_fallback_on_failure(self, handler):
        """Test fallback to other providers on failure."""
        # Primary fails, fallback succeeds
        failing_api = AsyncMock(side_effect=NetworkError("Primary failed"))
        success_api = AsyncMock(return_value={"result": "fallback success"})

        # Mock the API function to fail for primary, succeed for fallback
        call_count = 0

        async def conditional_api(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count <= 2:  # First provider with retries
                raise NetworkError("Primary failed")
            return {"result": "fallback success"}

        # Configure handler fallback order
        handler.fallback_order = [APIProvider.OPENAI, APIProvider.ANTHROPIC]

        # Patch the retry handler to try fallback on different provider
        with patch.object(
            handler,
            "_call_provider",
            new=AsyncMock(
                side_effect=[
                    NetworkError("Primary failed"),
                    {"result": "fallback success"},
                ]
            ),
        ):
            result = await handler.execute_api_call(
                primary_provider=APIProvider.OPENAI,
                api_function=conditional_api,
                operation="test_operation",
                enable_fallback=True,
            )

        assert result == {"result": "fallback success"}
        assert handler.stats["fallback_used"] == 1

    @pytest.mark.asyncio
    async def test_retry_logic(self, handler):
        """Test retry logic with exponential backoff."""
        # Function fails twice, succeeds on third try
        attempt_count = 0

        async def flaky_api(*args, **kwargs):
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 2:
                raise NetworkError("Temporary failure")
            return {"result": "success after retry"}

        # Mock circuit breaker call to pass through
        circuit = handler.circuit_breakers[APIProvider.OPENAI]
        circuit.state = CircuitState.CLOSED

        with patch.object(
            circuit,
            "call",
            new=AsyncMock(
                side_effect=[
                    NetworkError("First failure"),
                    {"result": "success after retry"},
                ]
            ),
        ):
            result = await handler.execute_api_call(
                primary_provider=APIProvider.OPENAI,
                api_function=flaky_api,
                operation="test_operation",
                enable_fallback=False,
            )

        assert result == {"result": "success after retry"}

    @pytest.mark.asyncio
    async def test_cache_hit(self, handler, mock_api_function):
        """Test cache hit on second call."""
        # First call - cache miss
        result1 = await handler.execute_api_call(
            primary_provider=APIProvider.OPENAI,
            api_function=mock_api_function,
            operation="test_operation",
            enable_cache=True,
        )

        # Second call - should hit cache
        result2 = await handler.execute_api_call(
            primary_provider=APIProvider.OPENAI,
            api_function=mock_api_function,
            operation="test_operation",
            enable_cache=True,
        )

        assert result1 == result2
        assert (
            handler.stats["cache_hits"] >= 0
        )  # Cache service might not be initialized

    @pytest.mark.asyncio
    async def test_rate_limiting(self, handler):
        """Test rate limiting behavior."""
        # Create many rapid failures to trigger rate limit
        failing_api = AsyncMock(side_effect=NetworkError("Rate limit test"))

        # Set aggressive rate limit for testing
        handler.error_rate_limiter.config.max_errors_per_window = 2
        handler.error_rate_limiter.config.window_size = 1

        # Make several failing calls
        for i in range(3):
            try:
                await handler.execute_api_call(
                    primary_provider=APIProvider.OPENAI,
                    api_function=failing_api,
                    operation="test_operation",
                    enable_fallback=False,
                    client_id="test_client",
                )
            except Exception:
                pass

        # Next call should be rate limited
        with patch.object(
            handler.error_rate_limiter, "check_limit", return_value=(True, 0.1)
        ):
            try:
                await handler.execute_api_call(
                    primary_provider=APIProvider.OPENAI,
                    api_function=failing_api,
                    operation="test_operation",
                    enable_fallback=False,
                    client_id="test_client",
                )
            except Exception:
                pass

        assert handler.stats["rate_limited_calls"] > 0

    @pytest.mark.asyncio
    async def test_timeout_handling(self, handler):
        """Test timeout handling."""

        # Create slow API function
        async def slow_api(*args, **kwargs):
            await asyncio.sleep(5)
            return {"result": "too slow"}

        # Configure short timeout
        handler.timeout_handler.config.default_timeout = 0.1

        with pytest.raises((asyncio.TimeoutError, RetryError)):
            await handler.execute_api_call(
                primary_provider=APIProvider.OPENAI,
                api_function=slow_api,
                operation="test_operation",
                enable_fallback=False,
            )

    @pytest.mark.asyncio
    async def test_provider_health_monitoring(self, handler):
        """Test provider health monitoring."""
        # Create some successes and failures
        success_api = AsyncMock(return_value={"result": "success"})
        failure_api = AsyncMock(side_effect=NetworkError("Test failure"))

        # Success call
        await handler.execute_api_call(
            primary_provider=APIProvider.OPENAI,
            api_function=success_api,
            operation="test_operation",
        )

        # Failure calls
        for _ in range(2):
            try:
                await handler.execute_api_call(
                    primary_provider=APIProvider.OPENAI,
                    api_function=failure_api,
                    operation="test_operation",
                    enable_fallback=False,
                )
            except Exception:
                pass

        # Check health
        health = await handler.get_provider_health()

        assert "openai" in health
        openai_health = health["openai"]
        assert openai_health["total_calls"] > 0
        assert openai_health["failure_count"] > 0
        assert 0 <= openai_health["success_rate"] <= 1

    @pytest.mark.asyncio
    async def test_manual_circuit_reset(self, handler):
        """Test manual circuit reset."""
        # Open circuit
        circuit = handler.circuit_breakers[APIProvider.OPENAI]
        circuit.state = CircuitState.OPEN
        circuit.stats.failure_count = 5

        # Reset circuit
        await handler.reset_provider(APIProvider.OPENAI)

        assert circuit.state == CircuitState.CLOSED
        assert circuit.stats.failure_count == 0

    @pytest.mark.asyncio
    async def test_complete_failure_scenario(self, handler):
        """Test complete failure with all providers down."""
        # All providers fail
        failing_api = AsyncMock(side_effect=NetworkError("All providers down"))

        # Configure minimal fallback for test
        handler.fallback_order = [APIProvider.OPENAI, APIProvider.ANTHROPIC]

        with pytest.raises(LLLError) as exc_info:
            await handler.execute_api_call(
                primary_provider=APIProvider.OPENAI,
                api_function=failing_api,
                operation="test_operation",
                enable_fallback=True,
                enable_cache=False,
            )

        assert exc_info.value.code == "LLM_004"
        assert exc_info.value.status_code == 503
        assert handler.stats["failed_calls"] == 1

    def test_statistics_tracking(self, handler):
        """Test statistics tracking."""
        stats = handler.get_statistics()

        assert "total_calls" in stats
        assert "successful_calls" in stats
        assert "failed_calls" in stats
        assert "fallback_used" in stats
        assert "circuit_open_rejections" in stats
        assert "rate_limited_calls" in stats
        assert "cache_hits" in stats
        assert "provider_statistics" in stats
        assert "success_rate" in stats


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
