"""
Resilient LLM client for Ultra.

This module provides a resilient LLM client implementation that can handle failures gracefully
using circuit breakers, retries, timeouts, rate limiting, and fallbacks.
"""

import logging
from typing import Any, Callable, Dict, List, Optional, Union

from backend.utils.domain_exceptions import (
    CircuitOpenException,
    ExternalServiceException,
    ModelException,
    ModelTimeoutException,
    ModelUnavailableException,
    ServiceUnavailableException,
    TimeoutException,
)
from backend.utils.recovery_strategies import (
    CircuitBreaker,
    ExponentialBackoffRetryStrategy,
    Fallback,
    ResilienceComposite,
    RetryableErrorType,
    Timeout,
    create_circuit_breaker,
    create_rate_limiter,
    create_timeout,
)

# Configure logger
logger = logging.getLogger("resilient_llm_client")


class ResilientLLMClient:
    """
    Resilient LLM client with built-in resilience features.

    This client provides resilience features such as circuit breakers, retries,
    timeouts, rate limiting, and fallbacks for LLM providers.
    """

    def __init__(
        self,
        provider_name: str,
        api_key: str,
        client_implementation: Callable,
        fallback_client: Optional["ResilientLLMClient"] = None,
        max_retries: int = 2,
        timeout_seconds: float = 30.0,
        failure_threshold: int = 5,
        rate_limit_max_calls: int = 60,
        rate_limit_period: float = 60.0,
    ):
        """
        Initialize a new resilient LLM client.

        Args:
            provider_name: Name of the LLM provider
            api_key: API key for the provider
            client_implementation: Function to create the actual client
            fallback_client: Optional fallback client to use when this client fails
            max_retries: Maximum number of retry attempts
            timeout_seconds: Timeout in seconds for requests
            failure_threshold: Number of failures before opening the circuit
            rate_limit_max_calls: Maximum number of calls in the rate limit period
            rate_limit_period: Rate limit period in seconds
        """
        self.provider_name = provider_name
        self.api_key = api_key

        # Create the actual client
        self.client = client_implementation(api_key)
        self.fallback_client = fallback_client

        # Create resilience components
        self.circuit_breaker = create_circuit_breaker(
            service_name=f"llm_{provider_name}",
            failure_threshold=failure_threshold,
        )

        self.retry_strategy = ExponentialBackoffRetryStrategy(
            max_retries=max_retries,
            initial_delay=0.5,
            max_delay=5.0,
            backoff_factor=2.0,
            jitter=True,
            retryable_errors=[
                RetryableErrorType.SERVICE_UNAVAILABLE,
                RetryableErrorType.TIMEOUT,
                RetryableErrorType.CONNECTION,
            ],
        )

        self.rate_limiter = create_rate_limiter(
            service_name=f"llm_{provider_name}",
            max_calls=rate_limit_max_calls,
            period=rate_limit_period,
        )

        self.timeout = create_timeout(timeout_seconds=timeout_seconds)

        # Create fallback if provided
        self.fallback = None
        if fallback_client:

            async def fallback_function(*args, **kwargs):
                logger.warning(
                    f"Falling back from {provider_name} to {fallback_client.provider_name}"
                )
                return await fallback_client.generate(*args, **kwargs)

            self.fallback = Fallback(
                fallback_function=fallback_function,
                should_fallback_on=[
                    ServiceUnavailableException,
                    TimeoutException,
                    CircuitOpenException,
                    ModelUnavailableException,
                    ModelTimeoutException,
                ],
            )

        # Create composite resilience strategy
        components = {
            "name": f"llm_{provider_name}",
            "circuit_breaker": self.circuit_breaker,
            "retry_strategy": self.retry_strategy,
            "rate_limiter": self.rate_limiter,
            "timeout": self.timeout,
        }

        if self.fallback:
            components["fallback"] = self.fallback

        self.composite = ResilienceComposite(**components)

        logger.info(f"Initialized resilient LLM client for {provider_name}")

    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Generate text with resilience features.

        Args:
            prompt: The prompt to generate text from
            model: The model to use for generation
            **kwargs: Additional arguments for the generation

        Returns:
            The generated text response

        Raises:
            ModelException: If there's an error with the model
            ServiceUnavailableException: If the service is unavailable
            TimeoutException: If the request times out
        """
        try:
            return await self.composite.execute(
                self._generate_internal, prompt, model, **kwargs
            )
        except Exception as e:
            # Convert generic exceptions to specific ones
            if isinstance(e, TimeoutException):
                raise ModelTimeoutException(
                    model_name=model or "unknown",
                    message=f"Request to {self.provider_name} model timed out",
                    provider=self.provider_name,
                    timeout_seconds=self.timeout.timeout_seconds,
                )
            elif isinstance(e, ServiceUnavailableException):
                raise ModelUnavailableException(
                    model_name=model or "unknown",
                    message=f"Model from {self.provider_name} is currently unavailable",
                    provider=self.provider_name,
                )
            elif isinstance(e, CircuitOpenException):
                raise ModelUnavailableException(
                    model_name=model or "unknown",
                    message=f"Circuit breaker is open for {self.provider_name}",
                    provider=self.provider_name,
                )
            elif isinstance(e, ExternalServiceException):
                raise ModelException(
                    model_name=model or "unknown",
                    message=f"Error from {self.provider_name}: {str(e)}",
                    provider=self.provider_name,
                    original_exception=e,
                )
            else:
                raise ModelException(
                    model_name=model or "unknown",
                    message=f"Error generating text with {self.provider_name}: {str(e)}",
                    provider=self.provider_name,
                    original_exception=e,
                )

    async def _generate_internal(
        self,
        prompt: str,
        model: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Internal method to call the actual client's generation method.

        Args:
            prompt: The prompt to generate text from
            model: The model to use for generation
            **kwargs: Additional arguments for the generation

        Returns:
            The generated text response
        """
        try:
            response = await self.client.generate(prompt, model, **kwargs)
            return response
        except Exception as e:
            logger.error(
                f"Error generating text with {self.provider_name}: {str(e)}",
                exc_info=True,
            )
            raise ExternalServiceException(
                service_name=self.provider_name,
                message=f"Error from {self.provider_name} service: {str(e)}",
                original_error=e,
            )
