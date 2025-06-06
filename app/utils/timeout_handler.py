"""Timeout handler for external API calls.

This module provides timeout management for external service calls
with configurable timeouts and proper error handling.
"""

import asyncio
import logging
import time
from dataclasses import dataclass
from functools import wraps
from typing import Any, Callable, Dict, Optional, Union

logger = logging.getLogger(__name__)


@dataclass
class TimeoutConfig:
    """Configuration for timeout behavior."""

    default_timeout: float = 30.0  # seconds
    connect_timeout: float = 10.0  # connection timeout
    read_timeout: float = 30.0  # read timeout
    operation_timeouts: Dict[str, float] = None  # Per-operation timeouts
    enable_adaptive: bool = False  # Adapt timeout based on response times

    def __post_init__(self):
        if self.operation_timeouts is None:
            self.operation_timeouts = {}


class TimeoutError(Exception):
    """Raised when operation times out."""

    def __init__(self, message: str, operation: str, timeout: float):
        super().__init__(message)
        self.operation = operation
        self.timeout = timeout


class TimeoutHandler:
    """Handles timeout logic for external calls."""

    def __init__(self, config: TimeoutConfig):
        """Initialize timeout handler."""
        self.config = config
        self.response_times: Dict[str, list] = {}
        self.timeout_stats = {
            "total_calls": 0,
            "timeouts": 0,
            "average_response_time": 0,
        }

    async def execute(
        self,
        func: Callable,
        *args,
        operation: str = None,
        timeout: float = None,
        **kwargs,
    ) -> Any:
        """Execute function with timeout."""
        # Determine timeout value
        if timeout is None:
            timeout = self._get_timeout(operation or func.__name__)

        self.timeout_stats["total_calls"] += 1
        start_time = time.time()

        try:
            # Execute with timeout
            result = await asyncio.wait_for(
                self._call_function(func, *args, **kwargs), timeout=timeout
            )

            # Record response time for adaptive timeout
            response_time = time.time() - start_time
            self._record_response_time(operation or func.__name__, response_time)

            return result

        except asyncio.TimeoutError:
            self.timeout_stats["timeouts"] += 1

            raise TimeoutError(
                f"Operation '{operation or func.__name__}' timed out after {timeout}s",
                operation=operation or func.__name__,
                timeout=timeout,
            )

    async def _call_function(self, func: Callable, *args, **kwargs) -> Any:
        """Call function, handling both sync and async."""
        if asyncio.iscoroutinefunction(func):
            return await func(*args, **kwargs)
        else:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, func, *args, **kwargs)

    def _get_timeout(self, operation: str) -> float:
        """Get timeout value for operation."""
        # Check for specific operation timeout
        if operation in self.config.operation_timeouts:
            timeout = self.config.operation_timeouts[operation]
        else:
            timeout = self.config.default_timeout

        # Apply adaptive timeout if enabled
        if self.config.enable_adaptive:
            timeout = self._calculate_adaptive_timeout(operation, timeout)

        return timeout

    def _calculate_adaptive_timeout(self, operation: str, base_timeout: float) -> float:
        """Calculate adaptive timeout based on historical data."""
        if operation not in self.response_times or not self.response_times[operation]:
            return base_timeout

        # Calculate P95 response time
        sorted_times = sorted(self.response_times[operation])
        p95_index = int(len(sorted_times) * 0.95)
        p95_time = (
            sorted_times[p95_index]
            if p95_index < len(sorted_times)
            else sorted_times[-1]
        )

        # Add buffer (50% above P95)
        adaptive_timeout = p95_time * 1.5

        # Ensure within reasonable bounds
        min_timeout = base_timeout * 0.5
        max_timeout = base_timeout * 2.0

        return max(min_timeout, min(adaptive_timeout, max_timeout))

    def _record_response_time(self, operation: str, response_time: float):
        """Record response time for adaptive timeout calculation."""
        if operation not in self.response_times:
            self.response_times[operation] = []

        self.response_times[operation].append(response_time)

        # Keep only recent data (last 100 calls)
        if len(self.response_times[operation]) > 100:
            self.response_times[operation] = self.response_times[operation][-100:]

        # Update average response time
        all_times = []
        for times in self.response_times.values():
            all_times.extend(times)

        if all_times:
            self.timeout_stats["average_response_time"] = sum(all_times) / len(
                all_times
            )

    def get_stats(self) -> Dict[str, Any]:
        """Get timeout statistics."""
        return {
            **self.timeout_stats,
            "timeout_rate": (
                self.timeout_stats["timeouts"] / self.timeout_stats["total_calls"]
                if self.timeout_stats["total_calls"] > 0
                else 0
            ),
            "operation_stats": self._get_operation_stats(),
        }

    def _get_operation_stats(self) -> Dict[str, Dict[str, float]]:
        """Get per-operation statistics."""
        stats = {}

        for operation, times in self.response_times.items():
            if times:
                stats[operation] = {
                    "average": sum(times) / len(times),
                    "min": min(times),
                    "max": max(times),
                    "count": len(times),
                }

        return stats


def with_timeout(timeout: Union[float, TimeoutConfig] = 30.0, operation: str = None):
    """Decorator to add timeout to functions."""
    if isinstance(timeout, (int, float)):
        config = TimeoutConfig(default_timeout=float(timeout))
    else:
        config = timeout

    handler = TimeoutHandler(config)

    def decorator(func: Callable):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            return await handler.execute(
                func, *args, operation=operation or func.__name__, **kwargs
            )

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            return asyncio.run(
                handler.execute(
                    func, *args, operation=operation or func.__name__, **kwargs
                )
            )

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


class SmartTimeoutHandler(TimeoutHandler):
    """Enhanced timeout handler with advanced features."""

    def __init__(self, config: TimeoutConfig):
        """Initialize smart timeout handler."""
        super().__init__(config)
        self.critical_operations = set()
        self.timeout_patterns: Dict[str, Dict[str, Any]] = {}

    def mark_critical(self, operation: str):
        """Mark an operation as critical (never timeout)."""
        self.critical_operations.add(operation)

    async def execute(
        self,
        func: Callable,
        *args,
        operation: str = None,
        timeout: float = None,
        allow_partial: bool = False,
        **kwargs,
    ) -> Any:
        """Execute with smart timeout handling."""
        op_name = operation or func.__name__

        # Critical operations have no timeout
        if op_name in self.critical_operations:
            return await self._call_function(func, *args, **kwargs)

        # Check for timeout patterns
        if self._should_skip_timeout(op_name):
            return await self._call_function(func, *args, **kwargs)

        try:
            return await super().execute(
                func, *args, operation=operation, timeout=timeout, **kwargs
            )
        except TimeoutError as e:
            # Record timeout pattern
            self._record_timeout_pattern(op_name, args, kwargs)

            # Handle partial results if allowed
            if allow_partial:
                partial_result = await self._get_partial_result(op_name, args, kwargs)
                if partial_result is not None:
                    return partial_result

            raise

    def _should_skip_timeout(self, operation: str) -> bool:
        """Check if timeout should be skipped based on patterns."""
        if operation not in self.timeout_patterns:
            return False

        pattern = self.timeout_patterns[operation]

        # Skip timeout if operation frequently times out
        # (might be a long-running operation by design)
        timeout_rate = pattern["timeouts"] / pattern["total_calls"]
        return timeout_rate > 0.8 and pattern["total_calls"] > 10

    def _record_timeout_pattern(self, operation: str, args: tuple, kwargs: dict):
        """Record timeout pattern for analysis."""
        if operation not in self.timeout_patterns:
            self.timeout_patterns[operation] = {
                "total_calls": 0,
                "timeouts": 0,
                "patterns": [],
            }

        pattern = self.timeout_patterns[operation]
        pattern["total_calls"] += 1
        pattern["timeouts"] += 1

        # Record argument pattern (simplified)
        arg_pattern = {
            "arg_count": len(args),
            "has_kwargs": bool(kwargs),
            "timestamp": time.time(),
        }

        pattern["patterns"].append(arg_pattern)

        # Keep only recent patterns
        if len(pattern["patterns"]) > 50:
            pattern["patterns"] = pattern["patterns"][-50:]

    async def _get_partial_result(
        self, operation: str, args: tuple, kwargs: dict
    ) -> Optional[Any]:
        """Get partial result for timed-out operation."""
        # This is operation-specific and would need custom implementations
        # For now, return None
        return None

    def get_insights(self) -> Dict[str, Any]:
        """Get timeout insights and recommendations."""
        insights = {
            "frequently_timing_out": [],
            "recommended_timeout_adjustments": {},
            "critical_operations": list(self.critical_operations),
        }

        # Find frequently timing out operations
        for operation, pattern in self.timeout_patterns.items():
            if pattern["total_calls"] > 5:
                timeout_rate = pattern["timeouts"] / pattern["total_calls"]
                if timeout_rate > 0.3:
                    insights["frequently_timing_out"].append(
                        {
                            "operation": operation,
                            "timeout_rate": timeout_rate,
                            "total_calls": pattern["total_calls"],
                        }
                    )

        # Recommend timeout adjustments
        for operation, times in self.response_times.items():
            if len(times) > 10:
                p95_time = sorted(times)[int(len(times) * 0.95)]
                current_timeout = self._get_timeout(operation)

                if p95_time > current_timeout * 0.8:
                    # Recommend increase
                    insights["recommended_timeout_adjustments"][operation] = {
                        "current": current_timeout,
                        "recommended": p95_time * 1.5,
                        "reason": "P95 response time is close to timeout",
                    }

        return insights


# Utility functions for common timeout scenarios


async def with_connect_timeout(
    coro: Callable, connect_timeout: float = 10.0, read_timeout: float = 30.0
):
    """Apply separate connect and read timeouts."""
    # This would be used with HTTP clients that support
    # separate connect and read timeouts
    return await asyncio.wait_for(coro, timeout=connect_timeout + read_timeout)


def create_timeout_aware_session(
    connect_timeout: float = 10.0,
    read_timeout: float = 30.0,
    total_timeout: float = 60.0,
):
    """Create HTTP session with timeout configuration."""
    import aiohttp

    timeout = aiohttp.ClientTimeout(
        connect=connect_timeout, sock_read=read_timeout, total=total_timeout
    )

    return aiohttp.ClientSession(timeout=timeout)
