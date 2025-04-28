"""
Circuit Breaker Module.

This module implements the Circuit Breaker pattern for fault tolerance,
preventing cascading failures by failing fast when a service is unavailable.
"""

import time
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional


class CircuitState(Enum):
    """State of a circuit breaker."""

    CLOSED = "closed"  # Normal operation, requests allowed
    OPEN = "open"  # Failure detected, requests blocked
    HALF_OPEN = "half_open"  # Testing if service is available again


@dataclass
class CircuitStats:
    """
    Statistics for a circuit breaker.

    Attributes:
        success_count: Number of successful requests
        failure_count: Number of failed requests
        last_failure_time: Time of the last failure
        last_success_time: Time of the last success
        open_time: Time when the circuit was opened
        total_open_time: Total time the circuit has been open
    """

    success_count: int = 0
    failure_count: int = 0
    last_failure_time: float = 0
    last_success_time: float = 0
    open_time: float = 0
    total_open_time: float = 0


class CircuitBreaker:
    """
    Circuit breaker implementation.

    This class implements the Circuit Breaker pattern, which helps prevent
    cascading failures by failing fast when a service is unavailable.
    """

    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
    ):
        """
        Initialize the circuit breaker.

        Args:
            name: Name of the circuit breaker
            failure_threshold: Number of failures before opening the circuit
            recovery_timeout: Seconds to wait before testing if service is available
        """
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.state = CircuitState.CLOSED
        self.stats = CircuitStats()

    def allow_request(self) -> bool:
        """
        Check if a request should be allowed.

        Returns:
            True if the request is allowed, False otherwise
        """
        current_time = time.time()

        if self.state == CircuitState.CLOSED:
            return True

        if self.state == CircuitState.OPEN:
            # Check if recovery timeout has elapsed
            if current_time - self.stats.open_time >= self.recovery_timeout:
                # Transition to half-open state to test service
                self.state = CircuitState.HALF_OPEN
                return True
            return False

        # In half-open state, allow one request
        return True

    def record_success(self) -> None:
        """Record a successful request."""
        current_time = time.time()
        self.stats.success_count += 1
        self.stats.last_success_time = current_time

        if self.state == CircuitState.HALF_OPEN:
            # Service is working again, close the circuit
            if self.stats.open_time > 0:
                self.stats.total_open_time += current_time - self.stats.open_time
                self.stats.open_time = 0
            self.state = CircuitState.CLOSED
            self.stats.failure_count = 0  # Reset failure count

    def record_failure(self) -> bool:
        """
        Record a failed request.

        Returns:
            True if the circuit was opened, False otherwise
        """
        current_time = time.time()
        self.stats.failure_count += 1
        self.stats.last_failure_time = current_time

        if self.state == CircuitState.HALF_OPEN:
            # Service is still failing, open the circuit again
            self.state = CircuitState.OPEN
            self.stats.open_time = current_time
            return True

        if (
            self.state == CircuitState.CLOSED
            and self.stats.failure_count >= self.failure_threshold
        ):
            # Too many failures, open the circuit
            self.state = CircuitState.OPEN
            self.stats.open_time = current_time
            return True

        return False

    def reset(self) -> None:
        """Reset the circuit breaker to closed state."""
        self.state = CircuitState.CLOSED
        self.stats = CircuitStats()

    def get_status(self) -> Dict[str, str]:
        """
        Get the current status of the circuit breaker.

        Returns:
            Dictionary with circuit breaker status
        """
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": str(self.stats.failure_count),
            "success_count": str(self.stats.success_count),
            "failure_threshold": str(self.failure_threshold),
            "recovery_timeout": str(self.recovery_timeout),
        }


class CircuitBreakerRegistry:
    """
    Registry for circuit breakers.

    This class manages a collection of circuit breakers, allowing them to be
    retrieved or created as needed.
    """

    def __init__(self):
        """Initialize the circuit breaker registry."""
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}

    def get(self, name: str) -> Optional[CircuitBreaker]:
        """
        Get a circuit breaker by name.

        Args:
            name: Name of the circuit breaker

        Returns:
            The circuit breaker, or None if not found
        """
        return self.circuit_breakers.get(name)

    def register(self, circuit: CircuitBreaker) -> None:
        """
        Register a circuit breaker.

        Args:
            circuit: The circuit breaker to register
        """
        self.circuit_breakers[circuit.name] = circuit

    def get_or_create(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
    ) -> CircuitBreaker:
        """
        Get a circuit breaker, creating it if it doesn't exist.

        Args:
            name: Name of the circuit breaker
            failure_threshold: Number of failures before opening the circuit
            recovery_timeout: Seconds to wait before testing if service is available

        Returns:
            The circuit breaker
        """
        if name not in self.circuit_breakers:
            self.circuit_breakers[name] = CircuitBreaker(
                name=name,
                failure_threshold=failure_threshold,
                recovery_timeout=recovery_timeout,
            )
        return self.circuit_breakers[name]

    def reset_all(self) -> None:
        """Reset all circuit breakers."""
        for circuit in self.circuit_breakers.values():
            circuit.reset()

    def get_all_status(self) -> Dict[str, Dict[str, str]]:
        """
        Get the status of all circuit breakers.

        Returns:
            Dictionary with circuit breaker statuses
        """
        return {
            name: circuit.get_status()
            for name, circuit in self.circuit_breakers.items()
        }
