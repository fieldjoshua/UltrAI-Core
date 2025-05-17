"""End-to-end tests for recovery procedures.

Tests both automatic and manual recovery mechanisms to ensure
they work correctly in various failure scenarios.
"""

import asyncio
import time
from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch

import pytest

from backend.utils.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerManager,
    CircuitConfig,
    CircuitState,
)
from backend.utils.fallback_handler import (
    DefaultValueStrategy,
    FallbackConfig,
    FallbackHandler,
)
from backend.utils.recovery_workflows import (
    CircuitBreakerRecoveryAction,
    RecoveryConfig,
    RecoveryWorkflow,
)
from backend.utils.retry_handler import RetryConfig, RetryHandler
from backend.utils.timeout_handler import TimeoutConfig, TimeoutHandler


@pytest.fixture
def circuit_config():
    """Circuit breaker configuration for testing."""
    return CircuitConfig(
        name="test_service",
        failure_threshold=3,
        recovery_timeout=1,  # Short timeout for testing
        success_threshold=2,
    )


@pytest.fixture
def circuit_breaker(circuit_config):
    """Circuit breaker instance for testing."""
    return CircuitBreaker(circuit_config)


@pytest.fixture
def retry_config():
    """Retry configuration for testing."""
    return RetryConfig(
        max_attempts=3,
        initial_delay=0.1,
        max_delay=1.0,
        jitter=False,  # Disable jitter for predictable tests
    )


@pytest.fixture
def fallback_config():
    """Fallback configuration for testing."""
    return FallbackConfig(
        use_cache=True, use_defaults=True, use_alternative_providers=True
    )


@pytest.fixture
def recovery_config():
    """Recovery configuration for testing."""
    return RecoveryConfig(
        max_recovery_attempts=3,
        recovery_interval=1,  # Short interval for testing
        enable_auto_recovery=True,
        recovery_timeout=10,
    )


@pytest.fixture
def recovery_workflow(recovery_config):
    """Recovery workflow instance for testing."""
    return RecoveryWorkflow(recovery_config)


class TestCircuitBreakerRecovery:
    """Test circuit breaker recovery mechanisms."""

    @pytest.mark.asyncio
    async def test_circuit_opens_on_failures(self, circuit_breaker):
        """Test that circuit opens after threshold failures."""

        async def failing_function():
            raise Exception("Service unavailable")

        # Trigger failures to open circuit
        for _ in range(3):
            with pytest.raises(Exception):
                await circuit_breaker.call(failing_function)

        assert circuit_breaker.state == CircuitState.OPEN

        # Verify circuit rejects calls when open
        with pytest.raises(Exception) as exc_info:
            await circuit_breaker.call(failing_function)

        assert "Circuit breaker" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_circuit_recovery_after_timeout(self, circuit_breaker):
        """Test circuit recovers after timeout period."""

        async def failing_then_success():
            if circuit_breaker.stats.total_requests < 3:
                raise Exception("Service unavailable")
            return "success"

        # Open the circuit
        for _ in range(3):
            with pytest.raises(Exception):
                await circuit_breaker.call(failing_then_success)

        assert circuit_breaker.state == CircuitState.OPEN

        # Wait for recovery timeout
        await asyncio.sleep(1.5)

        # Circuit should transition to half-open and allow test
        result = await circuit_breaker.call(failing_then_success)
        assert result == "success"
        assert circuit_breaker.state == CircuitState.HALF_OPEN

        # Another success should close the circuit
        result = await circuit_breaker.call(failing_then_success)
        assert circuit_breaker.state == CircuitState.CLOSED


class TestRetryMechanisms:
    """Test retry mechanisms with exponential backoff."""

    @pytest.mark.asyncio
    async def test_retry_with_eventual_success(self, retry_config):
        """Test retry succeeds after initial failures."""
        call_count = 0

        async def failing_then_success():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("Temporary failure")
            return "success"

        handler = RetryHandler(retry_config)
        result = await handler.execute(failing_then_success)

        assert result == "success"
        assert call_count == 3

    @pytest.mark.asyncio
    async def test_retry_exhaustion(self, retry_config):
        """Test retry exhaustion after max attempts."""
        call_count = 0

        async def always_failing():
            nonlocal call_count
            call_count += 1
            raise Exception("Permanent failure")

        handler = RetryHandler(retry_config)

        with pytest.raises(Exception) as exc_info:
            await handler.execute(always_failing)

        assert call_count == retry_config.max_attempts
        assert "Failed after" in str(exc_info.value)


class TestFallbackMechanisms:
    """Test fallback mechanisms for service failures."""

    @pytest.mark.asyncio
    async def test_default_value_fallback(self, fallback_config):
        """Test fallback to default values."""
        handler = FallbackHandler(fallback_config)

        # Register default value strategy
        defaults = {"get_user": {"id": "default", "name": "Guest"}}
        handler.register_strategy("defaults", DefaultValueStrategy(defaults))

        # Test fallback on error
        error = Exception("Service unavailable")
        context = {"operation": "get_user"}

        result = await handler.handle_failure(error, context)
        assert result == {"id": "default", "name": "Guest"}

    @pytest.mark.asyncio
    async def test_cache_fallback(self, fallback_config):
        """Test fallback to cached responses."""
        cache_service = Mock()
        cache_service.get = AsyncMock(return_value={"cached": True})

        handler = FallbackHandler(fallback_config)

        # Mock cache strategy
        from backend.utils.fallback_handler import CachedResponseStrategy

        cache_strategy = CachedResponseStrategy(cache_service)
        handler.register_strategy("cache", cache_strategy)

        error = Exception("Service unavailable")
        context = {"cache_key": "test_key"}

        result = await handler.handle_failure(error, context)
        assert result == {"cached": True}


class TestTimeoutHandling:
    """Test timeout handling for external calls."""

    @pytest.mark.asyncio
    async def test_timeout_enforcement(self):
        """Test that timeouts are enforced."""
        config = TimeoutConfig(default_timeout=0.5)
        handler = TimeoutHandler(config)

        async def slow_function():
            await asyncio.sleep(1.0)
            return "success"

        with pytest.raises(Exception) as exc_info:
            await handler.execute(slow_function)

        assert "timed out" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_adaptive_timeout(self):
        """Test adaptive timeout calculation."""
        config = TimeoutConfig(default_timeout=1.0, enable_adaptive=True)
        handler = TimeoutHandler(config)

        # Record some fast response times
        async def fast_function():
            await asyncio.sleep(0.1)
            return "success"

        for _ in range(5):
            await handler.execute(fast_function, operation="test_op")

        # Check that adaptive timeout is calculated
        timeout = handler._get_timeout("test_op")
        assert timeout < config.default_timeout  # Should be faster than default


class TestRecoveryWorkflows:
    """Test automated recovery workflows."""

    @pytest.mark.asyncio
    async def test_automatic_recovery_trigger(self, recovery_workflow):
        """Test automatic recovery triggers on failure."""
        # Create mock recovery action
        mock_action = Mock()
        mock_action.can_recover = Mock(return_value=True)
        mock_action.execute = AsyncMock(return_value=True)

        recovery_workflow.register_action(mock_action)

        # Trigger recovery
        result = await recovery_workflow.handle_failure(
            "TEST_ERROR", {"service_name": "test_service"}
        )

        assert result is True
        mock_action.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_recovery_retry_attempts(self, recovery_workflow):
        """Test recovery retries on failure."""
        attempt_count = 0

        # Create mock action that fails twice, then succeeds
        mock_action = Mock()
        mock_action.can_recover = Mock(return_value=True)

        async def mock_execute(context):
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 3:
                return False
            return True

        mock_action.execute = AsyncMock(side_effect=mock_execute)

        recovery_workflow.register_action(mock_action)

        result = await recovery_workflow.handle_failure(
            "TEST_ERROR", {"service_name": "test_service"}
        )

        assert result is True
        assert attempt_count == 3


class TestEndToEndRecovery:
    """Test complete recovery scenarios end-to-end."""

    @pytest.mark.asyncio
    async def test_llm_failure_recovery(self):
        """Test LLM service failure and recovery."""
        # Setup circuit breaker for LLM service
        circuit_config = CircuitConfig(
            name="openai", failure_threshold=3, recovery_timeout=1
        )
        circuit = CircuitBreaker(circuit_config)

        # Setup retry handler
        retry_config = RetryConfig(max_attempts=3, initial_delay=0.1)
        retry_handler = RetryHandler(retry_config)

        # Setup fallback handler
        fallback_handler = FallbackHandler(FallbackConfig())
        fallback_handler.register_strategy(
            "defaults", DefaultValueStrategy({"analyze": {"result": "fallback"}})
        )

        # Simulate service with intermittent failures
        call_count = 0

        async def llm_service():
            nonlocal call_count
            call_count += 1

            # Fail first 5 times to trigger circuit
            if call_count <= 5:
                raise Exception("Service unavailable")

            return {"result": "success"}

        # Compose recovery mechanisms
        async def resilient_llm_call():
            try:
                # Try with circuit breaker
                result = await circuit.call(lambda: retry_handler.execute(llm_service))
                return result
            except Exception as e:
                # Fallback on circuit open or retries exhausted
                return await fallback_handler.handle_failure(
                    e, {"operation": "analyze"}
                )

        # Test recovery sequence
        results = []

        # First calls should fallback
        for _ in range(3):
            result = await resilient_llm_call()
            results.append(result)

        # Wait for circuit recovery
        await asyncio.sleep(1.5)

        # Later calls should recover
        for _ in range(3):
            result = await resilient_llm_call()
            results.append(result)

        # Verify recovery sequence
        assert results[0] == {"result": "fallback"}  # Circuit opened
        assert results[-1] == {"result": "success"}  # Service recovered

    @pytest.mark.asyncio
    async def test_cascading_failure_recovery(self):
        """Test recovery from cascading failures."""
        # Setup multiple services with dependencies
        services = {"database": Mock(), "cache": Mock(), "llm": Mock()}

        # Create recovery workflow
        recovery_config = RecoveryConfig(max_recovery_attempts=3, recovery_interval=0.5)
        recovery_workflow = RecoveryWorkflow(recovery_config)

        # Register recovery actions for each service
        for service_name, service_mock in services.items():
            action = Mock()
            action.can_recover = Mock(
                side_effect=lambda error, ctx: ctx.get("service_name") == service_name
            )
            action.execute = AsyncMock(return_value=True)
            recovery_workflow.register_action(action)

        # Simulate cascading failure
        failures = [
            ("database", "DB_CONNECTION_LOST"),
            ("cache", "CACHE_CONNECTION_LOST"),
            ("llm", "SERVICE_UNAVAILABLE"),
        ]

        # Trigger recovery for each failure
        recovery_results = []

        for service_name, error_type in failures:
            result = await recovery_workflow.handle_failure(
                error_type, {"service_name": service_name}
            )
            recovery_results.append((service_name, result))

        # Verify all services recovered
        for service_name, result in recovery_results:
            assert result is True, f"Recovery failed for {service_name}"

    @pytest.mark.asyncio
    async def test_monitoring_and_alerting(self):
        """Test recovery monitoring and alerting."""
        from backend.services.recovery_monitoring_service import (
            AlertConfig,
            RecoveryMonitoringService,
        )

        # Create monitoring service
        circuit_manager = CircuitBreakerManager()
        recovery_workflow = RecoveryWorkflow(RecoveryConfig())
        metrics_collector = Mock()

        alert_config = AlertConfig(recovery_failure_threshold=2, alert_cooldown=1)

        monitoring_service = RecoveryMonitoringService(
            recovery_workflow, circuit_manager, metrics_collector, alert_config
        )

        # Track alerts
        alerts_sent = []

        async def mock_send_alert(alert):
            alerts_sent.append(alert)

        monitoring_service._send_alert = mock_send_alert

        # Simulate consecutive failures
        monitoring_service.consecutive_failures["test_service"] = 2

        # Trigger alert check
        await monitoring_service._trigger_alert(
            "recovery_failure", {"service": "test_service", "consecutive_failures": 2}
        )

        # Verify alert was sent
        assert len(alerts_sent) == 1
        assert alerts_sent[0]["type"] == "recovery_failure"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
