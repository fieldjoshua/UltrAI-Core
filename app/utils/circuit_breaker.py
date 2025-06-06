"""Circuit breaker implementation for external service calls.

This module provides a circuit breaker pattern implementation to prevent
cascading failures when external services are unavailable.
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, Optional, Union

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states."""

    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, rejecting calls
    HALF_OPEN = "half_open"  # Testing if service recovered


@dataclass
class CircuitConfig:
    """Configuration for circuit breaker."""

    name: str
    failure_threshold: int = 5  # Number of failures before opening
    recovery_timeout: int = 60  # Seconds before attempting recovery
    success_threshold: int = 3  # Successful calls to close circuit
    timeout: int = 30  # Timeout for individual calls
    exclude_exceptions: tuple = ()  # Exceptions that don't count as failures


@dataclass
class CircuitStats:
    """Statistics for circuit breaker monitoring."""

    failure_count: int = 0
    success_count: int = 0
    last_failure_time: Optional[datetime] = None
    last_success_time: Optional[datetime] = None
    total_requests: int = 0
    state_changes: list = field(default_factory=list)


class CircuitBreaker:
    """Circuit breaker implementation."""

    def __init__(self, config: CircuitConfig):
        """Initialize circuit breaker with configuration."""
        self.config = config
        self.state = CircuitState.CLOSED
        self.stats = CircuitStats()
        self._half_open_counter = 0
        self._state_changed_at = datetime.now()
        self._lock = asyncio.Lock()

    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection."""
        async with self._lock:
            if not await self._can_make_request():
                raise CircuitOpenError(
                    f"Circuit breaker '{self.config.name}' is OPEN. "
                    f"Service unavailable."
                )

        try:
            # Add timeout to the call
            result = await asyncio.wait_for(
                func(*args, **kwargs), timeout=self.config.timeout
            )
            await self._on_success()
            return result

        except asyncio.TimeoutError:
            await self._on_failure(TimeoutError("Call timed out"))
            raise
        except Exception as e:
            if not isinstance(e, self.config.exclude_exceptions):
                await self._on_failure(e)
            raise

    async def _can_make_request(self) -> bool:
        """Check if a request can be made based on circuit state."""
        if self.state == CircuitState.CLOSED:
            return True

        if self.state == CircuitState.OPEN:
            if self._should_attempt_recovery():
                await self._transition_to_half_open()
                return True
            return False

        # HALF_OPEN state - allow limited requests
        return True

    def _should_attempt_recovery(self) -> bool:
        """Check if enough time has passed to attempt recovery."""
        if self.stats.last_failure_time is None:
            return True

        time_since_failure = datetime.now() - self._state_changed_at
        return time_since_failure.total_seconds() >= self.config.recovery_timeout

    async def _on_success(self):
        """Handle successful call."""
        async with self._lock:
            self.stats.success_count += 1
            self.stats.total_requests += 1
            self.stats.last_success_time = datetime.now()

            if self.state == CircuitState.HALF_OPEN:
                self._half_open_counter += 1
                if self._half_open_counter >= self.config.success_threshold:
                    await self._transition_to_closed()

            logger.debug(
                f"Circuit breaker '{self.config.name}': Success recorded. "
                f"State: {self.state.value}"
            )

    async def _on_failure(self, error: Exception):
        """Handle failed call."""
        async with self._lock:
            self.stats.failure_count += 1
            self.stats.total_requests += 1
            self.stats.last_failure_time = datetime.now()

            if self.state == CircuitState.CLOSED:
                if self.stats.failure_count >= self.config.failure_threshold:
                    await self._transition_to_open()

            elif self.state == CircuitState.HALF_OPEN:
                # Single failure in half-open returns to open
                await self._transition_to_open()

            logger.warning(
                f"Circuit breaker '{self.config.name}': Failure recorded. "
                f"Error: {str(error)}. State: {self.state.value}"
            )

    async def _transition_to_open(self):
        """Transition circuit to OPEN state."""
        self.state = CircuitState.OPEN
        self._state_changed_at = datetime.now()
        self.stats.state_changes.append(
            {
                "from": self.state.value,
                "to": CircuitState.OPEN.value,
                "timestamp": self._state_changed_at,
            }
        )

        logger.error(
            f"Circuit breaker '{self.config.name}' opened. "
            f"Failure count: {self.stats.failure_count}"
        )

    async def _transition_to_half_open(self):
        """Transition circuit to HALF_OPEN state."""
        self.state = CircuitState.HALF_OPEN
        self._state_changed_at = datetime.now()
        self._half_open_counter = 0
        self.stats.state_changes.append(
            {
                "from": self.state.value,
                "to": CircuitState.HALF_OPEN.value,
                "timestamp": self._state_changed_at,
            }
        )

        logger.info(
            f"Circuit breaker '{self.config.name}' half-opened. " f"Testing recovery..."
        )

    async def _transition_to_closed(self):
        """Transition circuit to CLOSED state."""
        self.state = CircuitState.CLOSED
        self._state_changed_at = datetime.now()
        self.stats.failure_count = 0  # Reset failure count
        self.stats.state_changes.append(
            {
                "from": self.state.value,
                "to": CircuitState.CLOSED.value,
                "timestamp": self._state_changed_at,
            }
        )

        logger.info(
            f"Circuit breaker '{self.config.name}' closed. " f"Service recovered."
        )

    def get_status(self) -> Dict[str, Any]:
        """Get circuit breaker status for monitoring."""
        return {
            "name": self.config.name,
            "state": self.state.value,
            "stats": {
                "failure_count": self.stats.failure_count,
                "success_count": self.stats.success_count,
                "total_requests": self.stats.total_requests,
                "last_failure": (
                    self.stats.last_failure_time.isoformat()
                    if self.stats.last_failure_time
                    else None
                ),
                "last_success": (
                    self.stats.last_success_time.isoformat()
                    if self.stats.last_success_time
                    else None
                ),
            },
            "config": {
                "failure_threshold": self.config.failure_threshold,
                "recovery_timeout": self.config.recovery_timeout,
                "success_threshold": self.config.success_threshold,
            },
        }


class CircuitOpenError(Exception):
    """Raised when circuit breaker is open."""

    pass


class CircuitBreakerManager:
    """Manages multiple circuit breakers for different services."""

    def __init__(self):
        """Initialize circuit breaker manager."""
        self._breakers: Dict[str, CircuitBreaker] = {}

    def register_service(self, config: CircuitConfig) -> CircuitBreaker:
        """Register a service with circuit breaker protection."""
        if config.name in self._breakers:
            return self._breakers[config.name]

        breaker = CircuitBreaker(config)
        self._breakers[config.name] = breaker
        logger.info(f"Registered circuit breaker for service: {config.name}")
        return breaker

    def get_breaker(self, service_name: str) -> Optional[CircuitBreaker]:
        """Get circuit breaker for a service."""
        return self._breakers.get(service_name)

    def get_all_statuses(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all circuit breakers."""
        return {name: breaker.get_status() for name, breaker in self._breakers.items()}

    async def reset_breaker(self, service_name: str) -> bool:
        """Reset a circuit breaker to closed state."""
        breaker = self._breakers.get(service_name)
        if breaker:
            async with breaker._lock:
                await breaker._transition_to_closed()
            return True
        return False


# Global circuit breaker manager instance
circuit_manager = CircuitBreakerManager()


def with_circuit_breaker(config: CircuitConfig):
    """Decorator to add circuit breaker protection to async functions."""

    def decorator(func: Callable):
        async def wrapper(*args, **kwargs):
            breaker = circuit_manager.register_service(config)
            return await breaker.call(func, *args, **kwargs)

        return wrapper

    return decorator
