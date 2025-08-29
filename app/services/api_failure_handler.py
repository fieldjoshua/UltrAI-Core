"""API Failure Handler Service for Phase 3 Implementation.

This module integrates circuit breakers, retry logic, timeouts, and rate limiting
specifically for API calls, providing comprehensive failure handling.
"""

import asyncio
import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from app.services.cache_service import cache_service
from app.utils.circuit_breaker import (
    CircuitBreaker,
    CircuitConfig,
    CircuitOpenError,
)
from app.utils.error_rate_limiter import ErrorRateLimitConfig, ErrorRateLimiter
from app.utils.errors import LLMError, NetworkError, SystemError
from app.utils.logging import get_logger
from app.utils.retry_handler import RetryConfig, RetryError, RetryHandler
from app.utils.timeout_handler import TimeoutConfig, TimeoutError, TimeoutHandler

logger = get_logger("api_failure_handler", "logs/api_failure_handler.log")


class APIProvider(Enum):
    """Supported API providers."""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    MISTRAL = "mistral"
    GROQ = "groq"
    DOCKER_MODEL_RUNNER = "docker_model_runner"


@dataclass
class APICallContext:
    """Context for API calls to track metadata."""

    provider: APIProvider
    operation: str
    client_id: Optional[str] = None
    request_id: Optional[str] = None
    attempt: int = 0
    start_time: float = 0


class APIFailureHandler:
    """Comprehensive API failure handler integrating all resilience patterns."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize API failure handler with configuration."""
        self.config = config or {}

        # Initialize circuit breakers per provider
        self.circuit_breakers: Dict[APIProvider, CircuitBreaker] = {}
        for provider in APIProvider:
            circuit_config = CircuitConfig(
                name=f"{provider.value}_circuit",
                failure_threshold=self.config.get("circuit_failure_threshold", 5),
                recovery_timeout=self.config.get("circuit_recovery_timeout", 60),
                success_threshold=self.config.get("circuit_success_threshold", 3),
                timeout=self.config.get("api_timeout", 30),
                exclude_exceptions=(
                    ValueError,
                    KeyError,
                ),  # Don't count validation errors
            )
            self.circuit_breakers[provider] = CircuitBreaker(circuit_config)

        # Initialize retry handler
        retry_config = RetryConfig(
            max_attempts=self.config.get("max_retry_attempts", 3),
            initial_delay=self.config.get("retry_initial_delay", 1.0),
            max_delay=self.config.get("retry_max_delay", 60.0),
            exponential_base=2.0,
            jitter=True,
            retry_on=(NetworkError, TimeoutError, LLMError),
            exclude=(ValueError, KeyError, CircuitOpenError),
        )
        self.retry_handler = RetryHandler(retry_config)

        # Initialize timeout handler
        timeout_config = TimeoutConfig(
            default_timeout=self.config.get("default_timeout", 30.0),
            connect_timeout=self.config.get("connect_timeout", 10.0),
            operation_timeouts={
                "generate": self.config.get("generate_timeout", 60.0),
                "embeddings": self.config.get("embeddings_timeout", 30.0),
                "completion": self.config.get("completion_timeout", 45.0),
            },
            enable_adaptive=self.config.get("enable_adaptive_timeout", True),
        )
        self.timeout_handler = TimeoutHandler(timeout_config)

        # Initialize error rate limiter
        rate_limit_config = ErrorRateLimitConfig(
            window_size=self.config.get("rate_limit_window", 60),
            max_errors_per_window=self.config.get("max_errors_per_window", 50),
            enable_progressive_delay=True,
        )
        self.error_rate_limiter = ErrorRateLimiter(rate_limit_config)

        # Provider fallback order
        self.fallback_order = self.config.get(
            "fallback_order",
            [
                APIProvider.OPENAI,
                APIProvider.ANTHROPIC,
                APIProvider.GOOGLE,
                APIProvider.MISTRAL,
                APIProvider.GROQ,
                APIProvider.DOCKER_MODEL_RUNNER,
            ],
        )

        # Statistics tracking
        self.stats = {
            "total_calls": 0,
            "successful_calls": 0,
            "failed_calls": 0,
            "fallback_used": 0,
            "circuit_open_rejections": 0,
            "rate_limited_calls": 0,
            "cache_hits": 0,
            "provider_statistics": {
                p.value: {"success": 0, "failure": 0} for p in APIProvider
            },
        }

    async def execute_api_call(
        self,
        primary_provider: APIProvider,
        api_function: Callable,
        *args,
        operation: str = "unknown",
        client_id: Optional[str] = None,
        request_id: Optional[str] = None,
        enable_fallback: bool = True,
        enable_cache: bool = True,
        **kwargs,
    ) -> Any:
        """Execute API call with comprehensive failure handling.

        Args:
            primary_provider: Primary API provider to use
            api_function: The API function to call
            operation: Name of the operation (e.g., "generate", "embeddings")
            client_id: Optional client identifier for rate limiting
            request_id: Optional request ID for tracing
            enable_fallback: Whether to use fallback providers on failure
            enable_cache: Whether to use cached responses on failure

        Returns:
            API response or cached/fallback response

        Raises:
            LLMError: If all providers fail and no cache available
        """
        context = APICallContext(
            provider=primary_provider,
            operation=operation,
            client_id=client_id,
            request_id=request_id,
            start_time=time.time(),
        )

        self.stats["total_calls"] += 1

        # Check cache first if enabled
        if enable_cache:
            cache_key = self._generate_cache_key(context, args, kwargs)
            try:
                cached_response = await cache_service.aget(cache_key)
            except Exception:
                cached_response = cache_service.get(cache_key)
            if cached_response:
                self.stats["cache_hits"] += 1
                logger.info(f"Cache hit for {operation} on {primary_provider.value}")
                return cached_response

        # Try primary provider first
        try:
            result = await self._call_provider(
                primary_provider, api_function, context, *args, **kwargs
            )

            # Cache successful response
            if enable_cache:
                try:
                    await cache_service.aset(
                        cache_key, result, ttl=self.config.get("cache_ttl", 3600)
                    )
                except Exception:
                    cache_service.set(cache_key, result, ttl=self.config.get("cache_ttl", 3600))

            self.stats["successful_calls"] += 1
            self.stats["provider_statistics"][primary_provider.value]["success"] += 1
            return result

        except CircuitOpenError as e:
            logger.warning(f"Circuit open for {primary_provider.value}: {str(e)}")
            self.stats["circuit_open_rejections"] += 1

        except Exception as e:
            logger.error(f"Primary provider {primary_provider.value} failed: {str(e)}")
            self.stats["provider_statistics"][primary_provider.value]["failure"] += 1

        # Try fallback providers if enabled
        if enable_fallback:
            for fallback_provider in self.fallback_order:
                if fallback_provider == primary_provider:
                    continue

                try:
                    logger.info(f"Trying fallback provider: {fallback_provider.value}")
                    context.provider = fallback_provider
                    context.attempt += 1

                    result = await self._call_provider(
                        fallback_provider, api_function, context, *args, **kwargs
                    )

                    self.stats["fallback_used"] += 1
                    self.stats["successful_calls"] += 1
                    self.stats["provider_statistics"][fallback_provider.value][
                        "success"
                    ] += 1

                    # Cache successful fallback response
                    if enable_cache:
                        try:
                            await cache_service.aset(
                                cache_key,
                                result,
                                ttl=self.config.get("fallback_cache_ttl", 7200),
                            )
                        except Exception:
                            cache_service.set(
                                cache_key,
                                result,
                                ttl=self.config.get("fallback_cache_ttl", 7200),
                            )

                    return result

                except Exception as e:
                    logger.error(
                        f"Fallback provider {fallback_provider.value} failed: {str(e)}"
                    )
                    self.stats["provider_statistics"][fallback_provider.value][
                        "failure"
                    ] += 1
                    continue

        # All providers failed - check for degraded response
        if enable_cache:
            # Try to get any cached response, even if expired
            try:
                degraded_response = await cache_service.aget(cache_key, ignore_ttl=True)
            except Exception:
                degraded_response = cache_service.get(cache_key, ignore_ttl=True)
            if degraded_response:
                logger.warning(
                    f"Using degraded (expired) cache response for {operation}"
                )
                return degraded_response

        # Complete failure
        self.stats["failed_calls"] += 1
        raise LLMError(
            message=f"All API providers failed for operation '{operation}'",
            code="LLM_004",
            status_code=503,
            severity="HIGH",
            context={
                "operation": operation,
                "providers_tried": [p.value for p in self.fallback_order],
                "request_id": request_id,
            },
        )

    async def _call_provider(
        self,
        provider: APIProvider,
        api_function: Callable,
        context: APICallContext,
        *args,
        **kwargs,
    ) -> Any:
        """Make API call to specific provider with all resilience patterns."""
        # Check rate limit first
        should_limit, delay = await self.error_rate_limiter.check_limit(
            error_type=f"api_{provider.value}", client_id=context.client_id
        )

        if should_limit:
            self.stats["rate_limited_calls"] += 1
            if delay:
                logger.warning(f"Rate limited, delaying {delay}s for {provider.value}")
                await asyncio.sleep(delay)
            else:
                raise LLMError(
                    message="API rate limit exceeded",
                    code="LLM_005",
                    status_code=429,
                    severity="MEDIUM",
                )

        # Get circuit breaker for provider
        circuit_breaker = self.circuit_breakers[provider]

        # Create wrapped function with timeout and retry
        async def wrapped_call():
            return await self.timeout_handler.execute(
                api_function, *args, operation=context.operation, **kwargs
            )

        # Execute through circuit breaker with retry
        async def circuit_wrapped_call():
            return await circuit_breaker.call(wrapped_call)

        # Execute with retry handler
        return await self.retry_handler.execute(circuit_wrapped_call)

    def _generate_cache_key(
        self, context: APICallContext, args: tuple, kwargs: dict
    ) -> str:
        """Generate cache key for API call."""
        import hashlib
        import json

        key_data = {
            "provider": context.provider.value,
            "operation": context.operation,
            "args": str(args),
            "kwargs": json.dumps(kwargs, sort_keys=True, default=str),
        }

        key_string = json.dumps(key_data, sort_keys=True)
        return f"api:response:{hashlib.sha256(key_string.encode()).hexdigest()}"

    async def get_provider_health(self) -> Dict[str, Any]:
        """Get health status of all providers."""
        health = {}

        for provider, circuit in self.circuit_breakers.items():
            stats = self.stats["provider_statistics"][provider.value]
            total = stats["success"] + stats["failure"]

            health[provider.value] = {
                "circuit_state": circuit.state.value,
                "total_calls": total,
                "success_rate": stats["success"] / total if total > 0 else 0,
                "failure_count": stats["failure"],
                "last_failure": getattr(circuit.stats, "last_failure_time", None),
                "recovery_in": (
                    self._get_recovery_time(circuit)
                    if circuit.state.value == "open"
                    else None
                ),
            }

        return health

    def _get_recovery_time(self, circuit: CircuitBreaker) -> float:
        """Get remaining recovery time for open circuit."""
        if circuit.state.value != "open":
            return 0

        time_since_open = time.time() - circuit._state_changed_at.timestamp()
        recovery_remaining = circuit.config.recovery_timeout - time_since_open
        return max(0, recovery_remaining)

    async def reset_provider(self, provider: APIProvider):
        """Manually reset a provider's circuit breaker."""
        circuit = self.circuit_breakers[provider]
        circuit.state = circuit.state.CLOSED
        circuit.stats.failure_count = 0
        circuit.stats.success_count = 0
        logger.info(f"Manually reset circuit breaker for {provider.value}")

    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics."""
        return {
            **self.stats,
            "provider_health": asyncio.create_task(self.get_provider_health()),
            "uptime": time.time() - getattr(self, "_start_time", time.time()),
            "success_rate": (
                self.stats["successful_calls"] / self.stats["total_calls"]
                if self.stats["total_calls"] > 0
                else 0
            ),
        }


# Global instance
api_failure_handler = APIFailureHandler()
