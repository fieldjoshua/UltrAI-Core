"""
Recovery strategies for handling failures in the UltraAI backend.

This module provides various recovery strategies to handle failures in a resilient way, including:
- Retry mechanisms with exponential backoff
- Circuit breaker patterns
- Fallback mechanisms
- Bulkhead patterns
- Rate limiting
"""

import asyncio
import functools
import inspect
import logging
import time
from enum import Enum
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Set, Type, TypeVar, Union, cast

from backend.utils.domain_exceptions import (
    CircuitOpenException,
    ServiceUnavailableException,
    TimeoutException,
)
from backend.utils.unified_error_handler import ErrorCode, UltraBaseException

# Configure logger
logger = logging.getLogger("recovery_strategies")

# Type variables
T = TypeVar("T")
F = TypeVar("F", bound=Callable[..., Any])


class RetryableErrorType(Enum):
    """Types of errors that can be retried"""

    # Network related errors
    CONNECTION = "connection"
    TIMEOUT = "timeout"

    # Service related errors
    SERVICE_UNAVAILABLE = "service_unavailable"
    EXTERNAL_SERVICE = "external_service"

    # Resource related errors
    RESOURCE_EXHAUSTED = "resource_exhausted"
    INSUFFICIENT_RESOURCES = "insufficient_resources"

    # Rate limiting
    RATE_LIMIT = "rate_limit"
    THROTTLED = "throttled"


# Mapping of error codes to retryable error types
ERROR_CODE_TO_RETRY_TYPE = {
    # Service errors
    ErrorCode.SERVICE_UNAVAILABLE: RetryableErrorType.SERVICE_UNAVAILABLE,
    ErrorCode.EXTERNAL_SERVICE_ERROR: RetryableErrorType.EXTERNAL_SERVICE,
    ErrorCode.TIMEOUT: RetryableErrorType.TIMEOUT,
    ErrorCode.CONNECTION_ERROR: RetryableErrorType.CONNECTION,
    # Resource errors
    ErrorCode.RESOURCE_EXHAUSTED: RetryableErrorType.RESOURCE_EXHAUSTED,
    ErrorCode.INSUFFICIENT_RESOURCES: RetryableErrorType.INSUFFICIENT_RESOURCES,
    # Rate limiting errors
    ErrorCode.RATE_LIMIT_EXCEEDED: RetryableErrorType.RATE_LIMIT,
    ErrorCode.THROTTLED: RetryableErrorType.THROTTLED,
}

# Mapping of exception types to retryable error types
EXCEPTION_TO_RETRY_TYPE = {
    TimeoutError: RetryableErrorType.TIMEOUT,
    ConnectionError: RetryableErrorType.CONNECTION,
    ConnectionRefusedError: RetryableErrorType.CONNECTION,
    ConnectionAbortedError: RetryableErrorType.CONNECTION,
    ConnectionResetError: RetryableErrorType.CONNECTION,
}


class RetryStrategy:
    """Base class for retry strategies"""

    def __init__(self, name: str):
        """
        Initialize the retry strategy

        Args:
            name: Name of the retry strategy
        """
        self.name = name

    async def execute_with_retry(
        self,
        func: Callable[..., Any],
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Execute a function with retry according to the strategy

        Args:
            func: Function to execute
            args: Positional arguments for the function
            kwargs: Keyword arguments for the function

        Returns:
            Result of the function

        Raises:
            Exception: If the function fails after all retries
        """
        raise NotImplementedError("Subclasses must implement execute_with_retry")


class NoRetryStrategy(RetryStrategy):
    """Strategy that does not retry"""

    def __init__(self):
        super().__init__("no_retry")

    async def execute_with_retry(
        self,
        func: Callable[..., Any],
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Execute a function without retry

        Args:
            func: Function to execute
            args: Positional arguments for the function
            kwargs: Keyword arguments for the function

        Returns:
            Result of the function

        Raises:
            Exception: If the function fails
        """
        if inspect.iscoroutinefunction(func):
            return await func(*args, **kwargs)
        else:
            return func(*args, **kwargs)


class FixedRetryStrategy(RetryStrategy):
    """Strategy that retries a fixed number of times with a fixed delay"""

    def __init__(
        self,
        max_retries: int = 3,
        delay: float = 1.0,
        retryable_errors: Optional[List[RetryableErrorType]] = None,
    ):
        """
        Initialize the fixed retry strategy

        Args:
            max_retries: Maximum number of retries
            delay: Delay between retries in seconds
            retryable_errors: Types of errors to retry
        """
        super().__init__("fixed_retry")
        self.max_retries = max_retries
        self.delay = delay
        self.retryable_errors = retryable_errors or list(RetryableErrorType)

    async def execute_with_retry(
        self,
        func: Callable[..., Any],
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Execute a function with fixed retry

        Args:
            func: Function to execute
            args: Positional arguments for the function
            kwargs: Keyword arguments for the function

        Returns:
            Result of the function

        Raises:
            Exception: If the function fails after all retries
        """
        retries = 0
        last_exception = None

        while retries <= self.max_retries:
            try:
                if inspect.iscoroutinefunction(func):
                    return await func(*args, **kwargs)
                else:
                    return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                retries += 1

                # Check if the exception is retryable
                retry_type = self._get_retry_type(e)
                if retry_type is None or retry_type not in self.retryable_errors:
                    # Not retryable, re-raise
                    raise

                if retries > self.max_retries:
                    # Max retries exceeded, re-raise the last exception
                    logger.warning(
                        f"Max retries ({self.max_retries}) exceeded for {func.__name__}",
                        extra={
                            "exception": str(last_exception),
                            "retry_count": retries,
                        },
                    )
                    raise

                # Log the retry
                logger.info(
                    f"Retrying {func.__name__} after exception: {str(e)}, "
                    f"retry {retries}/{self.max_retries}, delay {self.delay}s",
                    extra={
                        "exception": str(e),
                        "retry_count": retries,
                        "max_retries": self.max_retries,
                        "delay": self.delay,
                    },
                )

                # Wait before retrying
                await asyncio.sleep(self.delay)

    def _get_retry_type(self, exception: Exception) -> Optional[RetryableErrorType]:
        """
        Get the retry type for an exception

        Args:
            exception: Exception to check

        Returns:
            Retry type if the exception is retryable, None otherwise
        """
        # Check if it's an UltraBaseException with a known error code
        if isinstance(exception, UltraBaseException):
            return ERROR_CODE_TO_RETRY_TYPE.get(exception.code)

        # Check if it's a known exception type
        for exc_type, retry_type in EXCEPTION_TO_RETRY_TYPE.items():
            if isinstance(exception, exc_type):
                return retry_type

        return None


class ExponentialBackoffRetryStrategy(RetryStrategy):
    """Strategy that retries with exponential backoff"""

    def __init__(
        self,
        max_retries: int = 3,
        initial_delay: float = 0.1,
        max_delay: float = 10.0,
        backoff_factor: float = 2.0,
        jitter: bool = True,
        retryable_errors: Optional[List[RetryableErrorType]] = None,
    ):
        """
        Initialize the exponential backoff retry strategy

        Args:
            max_retries: Maximum number of retries
            initial_delay: Initial delay between retries in seconds
            max_delay: Maximum delay between retries in seconds
            backoff_factor: Factor to increase delay by after each retry
            jitter: Whether to add random jitter to delays
            retryable_errors: Types of errors to retry
        """
        super().__init__("exponential_backoff_retry")
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.backoff_factor = backoff_factor
        self.jitter = jitter
        self.retryable_errors = retryable_errors or list(RetryableErrorType)

    async def execute_with_retry(
        self,
        func: Callable[..., Any],
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Execute a function with exponential backoff retry

        Args:
            func: Function to execute
            args: Positional arguments for the function
            kwargs: Keyword arguments for the function

        Returns:
            Result of the function

        Raises:
            Exception: If the function fails after all retries
        """
        retries = 0
        delay = self.initial_delay
        last_exception = None

        while retries <= self.max_retries:
            try:
                if inspect.iscoroutinefunction(func):
                    return await func(*args, **kwargs)
                else:
                    return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                retries += 1

                # Check if the exception is retryable
                retry_type = self._get_retry_type(e)
                if retry_type is None or retry_type not in self.retryable_errors:
                    # Not retryable, re-raise
                    raise

                if retries > self.max_retries:
                    # Max retries exceeded, re-raise the last exception
                    logger.warning(
                        f"Max retries ({self.max_retries}) exceeded for {func.__name__}",
                        extra={
                            "exception": str(last_exception),
                            "retry_count": retries,
                        },
                    )
                    raise

                # Calculate the next delay with jitter if enabled
                if self.jitter:
                    actual_delay = delay * (0.5 + asyncio.get_event_loop().time() % 1.0)
                else:
                    actual_delay = delay

                # Ensure the delay doesn't exceed the maximum
                actual_delay = min(actual_delay, self.max_delay)

                # Log the retry
                logger.info(
                    f"Retrying {func.__name__} after exception: {str(e)}, "
                    f"retry {retries}/{self.max_retries}, delay {actual_delay:.2f}s",
                    extra={
                        "exception": str(e),
                        "retry_count": retries,
                        "max_retries": self.max_retries,
                        "delay": actual_delay,
                    },
                )

                # Wait before retrying
                await asyncio.sleep(actual_delay)

                # Increase the delay for the next retry
                delay = min(delay * self.backoff_factor, self.max_delay)

    def _get_retry_type(self, exception: Exception) -> Optional[RetryableErrorType]:
        """
        Get the retry type for an exception

        Args:
            exception: Exception to check

        Returns:
            Retry type if the exception is retryable, None otherwise
        """
        # Check if it's an UltraBaseException with a known error code
        if isinstance(exception, UltraBaseException):
            return ERROR_CODE_TO_RETRY_TYPE.get(exception.code)

        # Check if it's a known exception type
        for exc_type, retry_type in EXCEPTION_TO_RETRY_TYPE.items():
            if isinstance(exception, exc_type):
                return retry_type

        return None


class CircuitBreaker:
    """
    Circuit breaker for protecting against failing external services.

    When a service fails repeatedly, the circuit breaker opens and
    fails fast, preventing cascading failures.
    """

    # Circuit breaker states
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing fast
    HALF_OPEN = "half_open"  # Testing if the service is recovered

    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        reset_timeout: int = 30,
        half_open_success_threshold: int = 2,
    ):
        """
        Initialize the circuit breaker

        Args:
            name: Name of the circuit breaker (typically the service name)
            failure_threshold: Number of consecutive failures before opening the circuit
            reset_timeout: Time in seconds before trying to close the circuit again
            half_open_success_threshold: Number of successful requests needed to close the circuit
        """
        self.name = name
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.half_open_success_threshold = half_open_success_threshold

        self.failure_count = 0
        self.last_failure_time = 0
        self.state = self.CLOSED
        self.success_count = 0

        logger.info(
            f"Initialized circuit breaker {name} with "
            f"failure_threshold={failure_threshold}, "
            f"reset_timeout={reset_timeout}s, "
            f"half_open_success_threshold={half_open_success_threshold}"
        )

    def register_failure(self) -> None:
        """Register a failure and potentially open the circuit"""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.state == self.CLOSED and self.failure_count >= self.failure_threshold:
            self.state = self.OPEN
            logger.warning(
                f"Circuit {self.name} opened after {self.failure_count} consecutive failures"
            )

        elif self.state == self.HALF_OPEN:
            self.state = self.OPEN
            self.failure_count = self.failure_threshold
            logger.warning(
                f"Circuit {self.name} reopened after a failure in half-open state"
            )

    def register_success(self) -> None:
        """Register a success and potentially close the circuit"""
        if self.state == self.HALF_OPEN:
            self.success_count += 1

            if self.success_count >= self.half_open_success_threshold:
                self.state = self.CLOSED
                self.failure_count = 0
                self.success_count = 0
                logger.info(
                    f"Circuit {self.name} closed after {self.success_count} successful requests in half-open state"
                )

        elif self.state == self.CLOSED:
            self.failure_count = 0

    def allow_request(self) -> bool:
        """Check if a request should be allowed to proceed"""
        # If circuit is closed, allow request
        if self.state == self.CLOSED:
            return True

        # If circuit is open, check if reset timeout has elapsed
        if self.state == self.OPEN:
            elapsed = time.time() - self.last_failure_time

            if elapsed >= self.reset_timeout:
                # Allow one request to go through
                self.state = self.HALF_OPEN
                self.success_count = 0
                logger.info(f"Circuit {self.name} half-opened, allowing trial request")
                return True

            return False

        # If circuit is half-open, allow request
        return self.state == self.HALF_OPEN

    async def execute(
        self,
        func: Callable[..., Any],
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Execute a function with circuit breaker protection

        Args:
            func: Function to execute
            args: Positional arguments for the function
            kwargs: Keyword arguments for the function

        Returns:
            Result of the function

        Raises:
            CircuitOpenException: If the circuit is open
            Exception: If the function fails
        """
        if not self.allow_request():
            raise CircuitOpenException(
                service_name=self.name,
                message=f"Service {self.name} temporarily unavailable due to circuit breaker",
                retry_after=max(
                    0, int(self.reset_timeout - (time.time() - self.last_failure_time))
                ),
            )

        try:
            if inspect.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)

            self.register_success()
            return result

        except Exception as e:
            self.register_failure()
            raise e

    def __call__(self, func: F) -> F:
        """
        Decorator to apply circuit breaker to a function

        Args:
            func: Function to decorate

        Returns:
            Decorated function
        """

        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            return await self.execute(func, *args, **kwargs)

        # Handle sync functions
        if not inspect.iscoroutinefunction(func):

            @wraps(func)
            def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
                return asyncio.run(wrapper(*args, **kwargs))

            return cast(F, sync_wrapper)

        return cast(F, wrapper)


class Bulkhead:
    """
    Bulkhead pattern for limiting concurrent requests.

    This pattern isolates failures and prevents them from consuming all resources.
    """

    def __init__(
        self,
        name: str,
        max_concurrent_calls: int = 10,
        max_queue_size: int = 10,
    ):
        """
        Initialize the bulkhead

        Args:
            name: Name of the bulkhead
            max_concurrent_calls: Maximum number of concurrent calls
            max_queue_size: Maximum size of the queue for waiting calls
        """
        self.name = name
        self.max_concurrent_calls = max_concurrent_calls
        self.max_queue_size = max_queue_size

        self.semaphore = asyncio.Semaphore(max_concurrent_calls)
        self.queue_semaphore = asyncio.Semaphore(max_concurrent_calls + max_queue_size)
        self.active_calls = 0
        self.queue_size = 0

        logger.info(
            f"Initialized bulkhead {name} with "
            f"max_concurrent_calls={max_concurrent_calls}, "
            f"max_queue_size={max_queue_size}"
        )

    async def execute(
        self,
        func: Callable[..., Any],
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Execute a function with bulkhead protection

        Args:
            func: Function to execute
            args: Positional arguments for the function
            kwargs: Keyword arguments for the function

        Returns:
            Result of the function

        Raises:
            ServiceUnavailableException: If the bulkhead is full and queue is full
            Exception: If the function fails
        """
        # Check if we can queue the request
        queue_acquired = False
        try:
            queue_acquired = await asyncio.wait_for(
                self.queue_semaphore.acquire(),
                timeout=0.1,  # Short timeout for queue acquisition
            )
        except asyncio.TimeoutError:
            queue_acquired = False

        if not queue_acquired:
            raise ServiceUnavailableException(
                service_name=self.name,
                message=f"Service {self.name} is at capacity (queue full)",
                details={
                    "max_concurrent_calls": self.max_concurrent_calls,
                    "max_queue_size": self.max_queue_size,
                },
            )

        self.queue_size += 1

        try:
            # Try to acquire the semaphore for execution
            semaphore_acquired = False
            try:
                semaphore_acquired = await asyncio.wait_for(
                    self.semaphore.acquire(),
                    timeout=5.0,  # Longer timeout for execution acquisition
                )
            except asyncio.TimeoutError:
                semaphore_acquired = False

            if not semaphore_acquired:
                raise ServiceUnavailableException(
                    service_name=self.name,
                    message=f"Service {self.name} is at capacity (execution timeout)",
                    details={"max_concurrent_calls": self.max_concurrent_calls},
                )

            self.active_calls += 1
            self.queue_size -= 1

            try:
                if inspect.iscoroutinefunction(func):
                    return await func(*args, **kwargs)
                else:
                    return func(*args, **kwargs)
            finally:
                self.active_calls -= 1
                self.semaphore.release()
        finally:
            if queue_acquired:
                self.queue_semaphore.release()

    def __call__(self, func: F) -> F:
        """
        Decorator to apply bulkhead to a function

        Args:
            func: Function to decorate

        Returns:
            Decorated function
        """

        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            return await self.execute(func, *args, **kwargs)

        # Handle sync functions
        if not inspect.iscoroutinefunction(func):

            @wraps(func)
            def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
                return asyncio.run(wrapper(*args, **kwargs))

            return cast(F, sync_wrapper)

        return cast(F, wrapper)


class Fallback:
    """
    Fallback pattern for providing alternative responses when a service fails.

    This pattern helps maintain functionality even when a service is unavailable.
    """

    def __init__(
        self,
        fallback_function: Callable[..., Any],
        should_fallback_on: Optional[List[Type[Exception]]] = None,
    ):
        """
        Initialize the fallback

        Args:
            fallback_function: Function to call as a fallback
            should_fallback_on: List of exception types that should trigger the fallback
        """
        self.fallback_function = fallback_function
        self.should_fallback_on = should_fallback_on or [Exception]

        logger.info(
            f"Initialized fallback with "
            f"fallback_function={fallback_function.__name__}, "
            f"should_fallback_on={[e.__name__ for e in self.should_fallback_on]}"
        )

    async def execute(
        self,
        func: Callable[..., Any],
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Execute a function with fallback

        Args:
            func: Function to execute
            args: Positional arguments for the function
            kwargs: Keyword arguments for the function

        Returns:
            Result of the function or fallback

        Raises:
            Exception: If the function and fallback both fail
        """
        try:
            if inspect.iscoroutinefunction(func):
                return await func(*args, **kwargs)
            else:
                return func(*args, **kwargs)
        except Exception as e:
            # Check if we should fallback on this exception
            should_fallback = False
            for exc_type in self.should_fallback_on:
                if isinstance(e, exc_type):
                    should_fallback = True
                    break

            if not should_fallback:
                raise

            logger.warning(
                f"Falling back for {func.__name__} after exception: {str(e)}",
                extra={"exception": str(e)},
            )

            # Execute the fallback
            if inspect.iscoroutinefunction(self.fallback_function):
                return await self.fallback_function(*args, **kwargs)
            else:
                return self.fallback_function(*args, **kwargs)

    def __call__(self, func: F) -> F:
        """
        Decorator to apply fallback to a function

        Args:
            func: Function to decorate

        Returns:
            Decorated function
        """

        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            return await self.execute(func, *args, **kwargs)

        # Handle sync functions
        if not inspect.iscoroutinefunction(func):

            @wraps(func)
            def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
                return asyncio.run(wrapper(*args, **kwargs))

            return cast(F, sync_wrapper)

        return cast(F, wrapper)


class RateLimiter:
    """
    Rate limiter to control the rate of requests.

    This pattern prevents abuse and ensures fair resource allocation.
    """

    def __init__(
        self,
        name: str,
        max_calls: int = 10,
        period: float = 1.0,
    ):
        """
        Initialize the rate limiter

        Args:
            name: Name of the rate limiter
            max_calls: Maximum number of calls allowed in the period
            period: Time period in seconds
        """
        self.name = name
        self.max_calls = max_calls
        self.period = period

        self.calls = []  # List of timestamps of calls
        self._lock = asyncio.Lock()

        logger.info(
            f"Initialized rate limiter {name} with "
            f"max_calls={max_calls}, "
            f"period={period}s"
        )

    async def execute(
        self,
        func: Callable[..., Any],
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Execute a function with rate limiting

        Args:
            func: Function to execute
            args: Positional arguments for the function
            kwargs: Keyword arguments for the function

        Returns:
            Result of the function

        Raises:
            ServiceUnavailableException: If the rate limit is exceeded
            Exception: If the function fails
        """
        async with self._lock:
            # Clean up old calls
            now = time.time()
            self.calls = [t for t in self.calls if now - t < self.period]

            # Check if we can make a new call
            if len(self.calls) >= self.max_calls:
                retry_after = int(self.period - (now - self.calls[0])) + 1
                raise ServiceUnavailableException(
                    service_name=self.name,
                    message=f"Rate limit exceeded for {self.name}",
                    details={
                        "max_calls": self.max_calls,
                        "period": self.period,
                        "retry_after": retry_after,
                    },
                    retry_after=retry_after,
                )

            # Record this call
            self.calls.append(now)

        # Execute the function
        if inspect.iscoroutinefunction(func):
            return await func(*args, **kwargs)
        else:
            return func(*args, **kwargs)

    def __call__(self, func: F) -> F:
        """
        Decorator to apply rate limiting to a function

        Args:
            func: Function to decorate

        Returns:
            Decorated function
        """

        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            return await self.execute(func, *args, **kwargs)

        # Handle sync functions
        if not inspect.iscoroutinefunction(func):

            @wraps(func)
            def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
                return asyncio.run(wrapper(*args, **kwargs))

            return cast(F, sync_wrapper)

        return cast(F, wrapper)


class Timeout:
    """
    Timeout pattern to limit the time a function can take.

    This pattern prevents functions from taking too long and blocking resources.
    """

    def __init__(
        self,
        timeout_seconds: float,
    ):
        """
        Initialize the timeout

        Args:
            timeout_seconds: Timeout in seconds
        """
        self.timeout_seconds = timeout_seconds

        logger.info(f"Initialized timeout with timeout_seconds={timeout_seconds}s")

    async def execute(
        self,
        func: Callable[..., Any],
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Execute a function with timeout

        Args:
            func: Function to execute
            args: Positional arguments for the function
            kwargs: Keyword arguments for the function

        Returns:
            Result of the function

        Raises:
            TimeoutException: If the function times out
            Exception: If the function fails
        """
        try:
            if inspect.iscoroutinefunction(func):
                return await asyncio.wait_for(
                    func(*args, **kwargs),
                    timeout=self.timeout_seconds,
                )
            else:
                # For sync functions, use a thread to avoid blocking
                loop = asyncio.get_event_loop()
                return await asyncio.wait_for(
                    loop.run_in_executor(None, lambda: func(*args, **kwargs)),
                    timeout=self.timeout_seconds,
                )
        except asyncio.TimeoutError:
            logger.warning(
                f"Timeout for {func.__name__} after {self.timeout_seconds}s",
                extra={"timeout_seconds": self.timeout_seconds},
            )
            raise TimeoutException(
                service_name=func.__name__,
                message=f"Operation timed out after {self.timeout_seconds}s",
                timeout_seconds=self.timeout_seconds,
            )

    def __call__(self, func: F) -> F:
        """
        Decorator to apply timeout to a function

        Args:
            func: Function to decorate

        Returns:
            Decorated function
        """

        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            return await self.execute(func, *args, **kwargs)

        # Handle sync functions
        if not inspect.iscoroutinefunction(func):

            @wraps(func)
            def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
                return asyncio.run(wrapper(*args, **kwargs))

            return cast(F, sync_wrapper)

        return cast(F, wrapper)


# Composite patterns combining multiple resilience patterns


class ResilienceComposite:
    """
    Composites multiple resilience patterns together.

    The execution order is:
    1. Rate limiter
    2. Circuit breaker
    3. Bulkhead
    4. Timeout
    5. Retry with fallback
    """

    def __init__(
        self,
        name: str,
        rate_limiter: Optional[RateLimiter] = None,
        circuit_breaker: Optional[CircuitBreaker] = None,
        bulkhead: Optional[Bulkhead] = None,
        timeout: Optional[Timeout] = None,
        retry_strategy: Optional[RetryStrategy] = None,
        fallback: Optional[Fallback] = None,
    ):
        """
        Initialize the composite

        Args:
            name: Name of the composite
            rate_limiter: Rate limiter to use
            circuit_breaker: Circuit breaker to use
            bulkhead: Bulkhead to use
            timeout: Timeout to use
            retry_strategy: Retry strategy to use
            fallback: Fallback to use
        """
        self.name = name
        self.rate_limiter = rate_limiter
        self.circuit_breaker = circuit_breaker
        self.bulkhead = bulkhead
        self.timeout = timeout
        self.retry_strategy = retry_strategy or NoRetryStrategy()
        self.fallback = fallback

        logger.info(f"Initialized resilience composite {name}")

    async def execute(
        self,
        func: Callable[..., Any],
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Execute a function with all resilience patterns

        Args:
            func: Function to execute
            args: Positional arguments for the function
            kwargs: Keyword arguments for the function

        Returns:
            Result of the function

        Raises:
            Exception: If the function fails and no fallback is available
        """

        # Build the function chain from the inside out
        async def execute_func(*inner_args: Any, **inner_kwargs: Any) -> Any:
            if inspect.iscoroutinefunction(func):
                return await func(*inner_args, **inner_kwargs)
            else:
                return func(*inner_args, **inner_kwargs)

        # Apply timeout if available
        if self.timeout:
            original_execute = execute_func

            async def execute_with_timeout(
                *inner_args: Any, **inner_kwargs: Any
            ) -> Any:
                return await self.timeout.execute(
                    original_execute, *inner_args, **inner_kwargs
                )

            execute_func = execute_with_timeout

        # Use the retry strategy with fallback if available
        if self.fallback:
            original_execute = execute_func

            async def execute_with_retry_and_fallback(
                *inner_args: Any, **inner_kwargs: Any
            ) -> Any:
                try:
                    return await self.retry_strategy.execute_with_retry(
                        original_execute, *inner_args, **inner_kwargs
                    )
                except Exception as e:
                    return await self.fallback.execute(
                        lambda *a, **kw: asyncio.sleep(
                            0
                        ),  # Dummy function that will fail
                        *inner_args,
                        **inner_kwargs,
                    )

            execute_func = execute_with_retry_and_fallback
        else:
            original_execute = execute_func

            async def execute_with_retry(*inner_args: Any, **inner_kwargs: Any) -> Any:
                return await self.retry_strategy.execute_with_retry(
                    original_execute, *inner_args, **inner_kwargs
                )

            execute_func = execute_with_retry

        # Apply bulkhead if available
        if self.bulkhead:
            original_execute = execute_func

            async def execute_with_bulkhead(
                *inner_args: Any, **inner_kwargs: Any
            ) -> Any:
                return await self.bulkhead.execute(
                    original_execute, *inner_args, **inner_kwargs
                )

            execute_func = execute_with_bulkhead

        # Apply circuit breaker if available
        if self.circuit_breaker:
            original_execute = execute_func

            async def execute_with_circuit_breaker(
                *inner_args: Any, **inner_kwargs: Any
            ) -> Any:
                return await self.circuit_breaker.execute(
                    original_execute, *inner_args, **inner_kwargs
                )

            execute_func = execute_with_circuit_breaker

        # Apply rate limiter if available
        if self.rate_limiter:
            original_execute = execute_func

            async def execute_with_rate_limiter(
                *inner_args: Any, **inner_kwargs: Any
            ) -> Any:
                return await self.rate_limiter.execute(
                    original_execute, *inner_args, **inner_kwargs
                )

            execute_func = execute_with_rate_limiter

        # Execute the function chain
        return await execute_func(*args, **kwargs)

    def __call__(self, func: F) -> F:
        """
        Decorator to apply all resilience patterns to a function

        Args:
            func: Function to decorate

        Returns:
            Decorated function
        """

        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            return await self.execute(func, *args, **kwargs)

        # Handle sync functions
        if not inspect.iscoroutinefunction(func):

            @wraps(func)
            def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
                return asyncio.run(wrapper(*args, **kwargs))

            return cast(F, sync_wrapper)

        return cast(F, wrapper)


# Factory functions for common resilience patterns


def create_standard_retry(
    max_retries: int = 3, initial_delay: float = 0.1
) -> RetryStrategy:
    """
    Create a standard retry strategy with exponential backoff

    Args:
        max_retries: Maximum number of retries
        initial_delay: Initial delay between retries in seconds

    Returns:
        RetryStrategy: The retry strategy
    """
    return ExponentialBackoffRetryStrategy(
        max_retries=max_retries,
        initial_delay=initial_delay,
        max_delay=10.0,
        backoff_factor=2.0,
        jitter=True,
    )


def create_circuit_breaker(
    service_name: str,
    failure_threshold: int = 5,
) -> CircuitBreaker:
    """
    Create a circuit breaker for a service

    Args:
        service_name: Name of the service
        failure_threshold: Number of consecutive failures before opening the circuit

    Returns:
        CircuitBreaker: The circuit breaker
    """
    return CircuitBreaker(
        name=service_name,
        failure_threshold=failure_threshold,
        reset_timeout=30,
        half_open_success_threshold=2,
    )


def create_bulkhead(
    service_name: str,
    max_concurrent_calls: int = 10,
) -> Bulkhead:
    """
    Create a bulkhead for a service

    Args:
        service_name: Name of the service
        max_concurrent_calls: Maximum number of concurrent calls

    Returns:
        Bulkhead: The bulkhead
    """
    return Bulkhead(
        name=service_name,
        max_concurrent_calls=max_concurrent_calls,
        max_queue_size=50,
    )


def create_rate_limiter(
    service_name: str,
    max_calls: int = 50,
    period: float = 1.0,
) -> RateLimiter:
    """
    Create a rate limiter for a service

    Args:
        service_name: Name of the service
        max_calls: Maximum number of calls allowed in the period
        period: Time period in seconds

    Returns:
        RateLimiter: The rate limiter
    """
    return RateLimiter(
        name=service_name,
        max_calls=max_calls,
        period=period,
    )


def create_timeout(timeout_seconds: float = 30.0) -> Timeout:
    """
    Create a timeout

    Args:
        timeout_seconds: Timeout in seconds

    Returns:
        Timeout: The timeout
    """
    return Timeout(timeout_seconds=timeout_seconds)


def create_resilience_composite(
    service_name: str,
    max_retries: int = 3,
    failure_threshold: int = 5,
    max_concurrent_calls: int = 10,
    timeout_seconds: float = 30.0,
    rate_limit_max_calls: int = 50,
    rate_limit_period: float = 1.0,
    fallback_function: Optional[Callable[..., Any]] = None,
) -> ResilienceComposite:
    """
    Create a resilience composite with all patterns

    Args:
        service_name: Name of the service
        max_retries: Maximum number of retries
        failure_threshold: Number of consecutive failures before opening the circuit
        max_concurrent_calls: Maximum number of concurrent calls
        timeout_seconds: Timeout in seconds
        rate_limit_max_calls: Maximum number of calls allowed in the period
        rate_limit_period: Time period in seconds
        fallback_function: Function to call as a fallback

    Returns:
        ResilienceComposite: The resilience composite
    """
    retry_strategy = create_standard_retry(max_retries=max_retries)
    circuit_breaker = create_circuit_breaker(
        service_name=service_name,
        failure_threshold=failure_threshold,
    )
    bulkhead = create_bulkhead(
        service_name=service_name,
        max_concurrent_calls=max_concurrent_calls,
    )
    timeout = create_timeout(timeout_seconds=timeout_seconds)
    rate_limiter = create_rate_limiter(
        service_name=service_name,
        max_calls=rate_limit_max_calls,
        period=rate_limit_period,
    )

    fallback = None
    if fallback_function:
        fallback = Fallback(fallback_function=fallback_function)

    return ResilienceComposite(
        name=service_name,
        rate_limiter=rate_limiter,
        circuit_breaker=circuit_breaker,
        bulkhead=bulkhead,
        timeout=timeout,
        retry_strategy=retry_strategy,
        fallback=fallback,
    )
