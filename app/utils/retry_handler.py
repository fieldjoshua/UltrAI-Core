"""Retry handler with exponential backoff for external service calls.

This module provides retry logic with exponential backoff, jitter,
and circuit breaker integration for handling transient failures.
"""

import asyncio
import logging
import random
import time
from dataclasses import dataclass
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Type, Union

from .circuit_breaker import CircuitOpenError

logger = logging.getLogger(__name__)


@dataclass
class RetryConfig:
    """Configuration for retry behavior."""

    max_attempts: int = 3
    initial_delay: float = 1.0  # seconds
    max_delay: float = 60.0  # seconds
    exponential_base: float = 2.0
    jitter: bool = True
    retry_on: tuple = (Exception,)  # Exceptions to retry on
    exclude: tuple = ()  # Exceptions to never retry
    on_retry: Optional[Callable] = None  # Callback on each retry
    on_failure: Optional[Callable] = None  # Callback on final failure


class RetryError(Exception):
    """Raised when all retry attempts are exhausted."""

    def __init__(self, message: str, last_error: Exception, attempts: int):
        super().__init__(message)
        self.last_error = last_error
        self.attempts = attempts


class RetryHandler:
    """Handles retry logic with exponential backoff."""

    def __init__(self, config: RetryConfig):
        """Initialize retry handler with configuration."""
        self.config = config

    async def execute(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with retry logic."""
        last_error = None

        for attempt in range(self.config.max_attempts):
            try:
                result = await self._call_function(func, *args, **kwargs)

                if attempt > 0:
                    logger.info(
                        f"Retry successful after {attempt} attempts for {func.__name__}"
                    )

                return result

            except self.config.exclude as e:
                # Don't retry on excluded exceptions
                logger.error(f"Non-retryable error in {func.__name__}: {str(e)}")
                raise

            except self.config.retry_on as e:
                last_error = e

                if attempt == self.config.max_attempts - 1:
                    # Last attempt failed
                    if self.config.on_failure:
                        await self._call_callback(
                            self.config.on_failure, e, attempt + 1
                        )

                    raise RetryError(
                        f"Failed after {self.config.max_attempts} attempts",
                        last_error,
                        self.config.max_attempts,
                    )

                # Calculate delay for next attempt
                delay = self._calculate_delay(attempt)

                logger.warning(
                    f"Attempt {attempt + 1}/{self.config.max_attempts} failed "
                    f"for {func.__name__}: {str(e)}. "
                    f"Retrying in {delay:.2f}s..."
                )

                if self.config.on_retry:
                    await self._call_callback(self.config.on_retry, e, attempt + 1)

                await asyncio.sleep(delay)

    async def _call_function(self, func: Callable, *args, **kwargs) -> Any:
        """Call the function, handling both sync and async functions."""
        if asyncio.iscoroutinefunction(func):
            return await func(*args, **kwargs)
        else:
            # Run sync function in executor to avoid blocking
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, func, *args, **kwargs)

    async def _call_callback(self, callback: Callable, error: Exception, attempt: int):
        """Call retry callback, handling both sync and async."""
        try:
            if asyncio.iscoroutinefunction(callback):
                await callback(error, attempt)
            else:
                callback(error, attempt)
        except Exception as e:
            logger.error(f"Error in retry callback: {str(e)}")

    def _calculate_delay(self, attempt: int) -> float:
        """Calculate delay for next retry attempt."""
        # Exponential backoff
        delay = self.config.initial_delay * (self.config.exponential_base**attempt)

        # Cap at max delay
        delay = min(delay, self.config.max_delay)

        # Add jitter to prevent thundering herd
        if self.config.jitter:
            jitter_range = delay * 0.1  # 10% jitter
            delay += random.uniform(-jitter_range, jitter_range)

        return max(delay, 0)  # Ensure non-negative


def with_retry(config: Union[RetryConfig, Dict[str, Any]]):
    """Decorator to add retry logic to functions."""
    if isinstance(config, dict):
        config = RetryConfig(**config)

    def decorator(func: Callable):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            handler = RetryHandler(config)
            return await handler.execute(func, *args, **kwargs)

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # For sync functions, run in async context
            handler = RetryHandler(config)
            return asyncio.run(handler.execute(func, *args, **kwargs))

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


class ExponentialBackoff:
    """Utility class for exponential backoff calculations."""

    @staticmethod
    def calculate_delay(
        attempt: int,
        initial_delay: float = 1.0,
        exponential_base: float = 2.0,
        max_delay: float = 60.0,
        jitter: bool = True,
    ) -> float:
        """Calculate exponential backoff delay."""
        delay = initial_delay * (exponential_base**attempt)
        delay = min(delay, max_delay)

        if jitter:
            jitter_range = delay * 0.1
            delay += random.uniform(-jitter_range, jitter_range)

        return max(delay, 0)

    @staticmethod
    def get_delays(
        max_attempts: int,
        initial_delay: float = 1.0,
        exponential_base: float = 2.0,
        max_delay: float = 60.0,
    ) -> List[float]:
        """Get list of delays for visualization/planning."""
        return [
            ExponentialBackoff.calculate_delay(
                i, initial_delay, exponential_base, max_delay, jitter=False
            )
            for i in range(max_attempts)
        ]


class AdaptiveRetry:
    """Adaptive retry mechanism that adjusts based on success rate."""

    def __init__(self, base_config: RetryConfig):
        """Initialize adaptive retry handler."""
        self.base_config = base_config
        self.stats = {"success_count": 0, "failure_count": 0, "total_attempts": 0}
        self._current_multiplier = 1.0

    async def execute(self, func: Callable, *args, **kwargs) -> Any:
        """Execute with adaptive retry logic."""
        # Adjust configuration based on recent success rate
        adjusted_config = self._adjust_config()
        handler = RetryHandler(adjusted_config)

        try:
            result = await handler.execute(func, *args, **kwargs)
            self._record_success()
            return result
        except Exception as e:
            self._record_failure()
            raise

    def _adjust_config(self) -> RetryConfig:
        """Adjust retry configuration based on success rate."""
        if self.stats["total_attempts"] < 10:
            return self.base_config

        success_rate = self.stats["success_count"] / self.stats["total_attempts"]

        # Adjust multiplier based on success rate
        if success_rate < 0.5:
            self._current_multiplier = min(self._current_multiplier * 1.1, 2.0)
        elif success_rate > 0.9:
            self._current_multiplier = max(self._current_multiplier * 0.9, 0.5)

        # Create adjusted config
        return RetryConfig(
            max_attempts=int(self.base_config.max_attempts * self._current_multiplier),
            initial_delay=self.base_config.initial_delay * self._current_multiplier,
            max_delay=self.base_config.max_delay,
            exponential_base=self.base_config.exponential_base,
            jitter=self.base_config.jitter,
            retry_on=self.base_config.retry_on,
            exclude=self.base_config.exclude,
            on_retry=self.base_config.on_retry,
            on_failure=self.base_config.on_failure,
        )

    def _record_success(self):
        """Record successful execution."""
        self.stats["success_count"] += 1
        self.stats["total_attempts"] += 1

    def _record_failure(self):
        """Record failed execution."""
        self.stats["failure_count"] += 1
        self.stats["total_attempts"] += 1

    def get_stats(self) -> Dict[str, Any]:
        """Get retry statistics."""
        return {
            **self.stats,
            "success_rate": (
                self.stats["success_count"] / self.stats["total_attempts"]
                if self.stats["total_attempts"] > 0
                else 0
            ),
            "current_multiplier": self._current_multiplier,
        }
