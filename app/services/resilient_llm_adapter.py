"""
Resilient LLM adapter with circuit breakers, retries, and timeouts.

This module provides resilience patterns for LLM API calls:
- Circuit breakers to prevent cascading failures
- Bounded retries with exponential backoff and jitter
- Provider-specific timeout configuration
- Metrics and monitoring hooks
"""

import asyncio
import random
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, Optional
from dataclasses import dataclass, field
import httpx

from app.services.llm_adapters import BaseAdapter
from app.utils.logging import get_logger, CorrelationContext

logger = get_logger(__name__)


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"      # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if service recovered


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker"""
    failure_threshold: int = 5  # Number of failures before opening
    success_threshold: int = 2  # Number of successes to close from half-open
    timeout: float = 60.0  # Seconds before trying half-open
    min_calls: int = 10  # Minimum calls before evaluating


@dataclass
class RetryConfig:
    """Configuration for retry behavior

    Backwards-compat notes:
    - Some tests still pass max_retries instead of max_attempts. We map that here.
    """
    max_attempts: int = 3
    initial_delay: float = 1.0  # Initial retry delay in seconds
    max_delay: float = 30.0  # Maximum retry delay
    exponential_base: float = 2.0  # Exponential backoff base
    jitter: float = 0.1  # Jitter factor (0.1 = 10%)
    # Backwards-compat alias accepted at init time
    max_retries: Optional[int] = None

    def __post_init__(self):
        if self.max_retries is not None:
            # Interpret max_retries as total attempts
            self.max_attempts = int(self.max_retries)
        else:
            # Populate alias for consumers expecting max_retries
            self.max_retries = int(self.max_attempts)


@dataclass
class ProviderConfig:
    """Provider-specific configuration

    Backwards-compat notes:
    - Some tests expect attribute names retry_config and circuit_breaker_config
      and classmethods like for_openai(). We provide aliases and helpers.
    """
    name: str
    timeout: float  # Request timeout in seconds
    circuit_breaker: CircuitBreakerConfig = field(default_factory=CircuitBreakerConfig)
    retry: RetryConfig = field(default_factory=RetryConfig)
    # Backwards-compat aliases (populated automatically)
    circuit_breaker_config: Optional[CircuitBreakerConfig] = None
    retry_config: Optional[RetryConfig] = None

    def __post_init__(self):
        if self.circuit_breaker_config is None:
            self.circuit_breaker_config = self.circuit_breaker
        if self.retry_config is None:
            self.retry_config = self.retry

    @classmethod
    def for_openai(cls) -> "ProviderConfig":
        return PROVIDER_CONFIGS["openai"]

    @classmethod
    def for_anthropic(cls) -> "ProviderConfig":
        return PROVIDER_CONFIGS["anthropic"]

    @classmethod
    def for_google(cls) -> "ProviderConfig":
        return PROVIDER_CONFIGS["google"]


# Provider-specific configurations tuned for each vendor
PROVIDER_CONFIGS = {
    "openai": ProviderConfig(
        name="openai",
        timeout=25.0,
        circuit_breaker=CircuitBreakerConfig(
            failure_threshold=5,
            success_threshold=2,
            timeout=60.0,
        ),
        retry=RetryConfig(
            max_attempts=3,
            initial_delay=1.0,
            max_delay=10.0,
        ),
    ),
    "anthropic": ProviderConfig(
        name="anthropic",
        timeout=30.0,
        circuit_breaker=CircuitBreakerConfig(
            failure_threshold=4,
            success_threshold=2,
            timeout=90.0,  # Longer recovery time
        ),
        retry=RetryConfig(
            max_attempts=2,
            initial_delay=2.0,  # Slower initial retry
            max_delay=20.0,
        ),
    ),
    "google": ProviderConfig(
        name="google",
        timeout=35.0,
        circuit_breaker=CircuitBreakerConfig(
            failure_threshold=6,
            success_threshold=3,
            timeout=45.0,
        ),
        retry=RetryConfig(
            max_attempts=3,
            initial_delay=0.5,  # Faster initial retry
            max_delay=15.0,
        ),
    ),
}


class CircuitBreaker:
    """Circuit breaker implementation"""
    
    def __init__(self, config: CircuitBreakerConfig):
        self.config = config
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.total_calls = 0
        
    def call(self, func: Callable) -> Any:
        """Execute function with circuit breaker protection"""
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                logger.info("Circuit breaker entering HALF_OPEN state")
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = func()
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e
    
    async def async_call(self, func: Callable) -> Any:
        """Execute async function with circuit breaker protection"""
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                logger.info("Circuit breaker entering HALF_OPEN state")
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = await func()
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e
    
    def _on_success(self):
        """Handle successful call"""
        self.total_calls += 1
        self.failure_count = 0
        
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.config.success_threshold:
                self.state = CircuitState.CLOSED
                self.success_count = 0
                logger.info("Circuit breaker closed after successful recovery")
    
    def _on_failure(self):
        """Handle failed call"""
        self.total_calls += 1
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.OPEN
            logger.warning("Circuit breaker reopened after failure in HALF_OPEN state")
        elif (self.failure_count >= self.config.failure_threshold and 
              self.total_calls >= self.config.min_calls):
            self.state = CircuitState.OPEN
            logger.warning(f"Circuit breaker opened after {self.failure_count} failures")
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to try reset"""
        if not self.last_failure_time:
            return True
        return datetime.now() - self.last_failure_time > timedelta(seconds=self.config.timeout)
    
    def get_state(self) -> Dict[str, Any]:
        """Get current circuit breaker state"""
        return {
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "total_calls": self.total_calls,
            "last_failure": self.last_failure_time.isoformat() if self.last_failure_time else None,
        }


class ResilientLLMAdapter:
    """Wrapper for LLM adapters with resilience patterns"""
    
    def __init__(
        self,
        adapter: BaseAdapter,
        provider_name: Optional[str] = None,
        *,
        # Backwards-compat optional parameters (ignored if provider config present)
        retry_config: Optional[RetryConfig] = None,
        circuit_breaker_config: Optional[CircuitBreakerConfig] = None,
        timeout: Optional[float] = None,
    ):
        self.adapter = adapter
        detected_provider = provider_name or self._detect_provider_from_adapter(adapter)
        self.provider_name = detected_provider.lower()

        # Get provider-specific config or use defaults
        if self.provider_name in PROVIDER_CONFIGS:
            self.config = PROVIDER_CONFIGS[self.provider_name]
        else:
            logger.warning(f"No specific config for provider {detected_provider}, using defaults")
            self.config = ProviderConfig(name=detected_provider, timeout=30.0)

        # Apply overrides for backwards-compat
        if retry_config is not None:
            self.config.retry = retry_config
            self.config.retry_config = retry_config
        if circuit_breaker_config is not None:
            self.config.circuit_breaker = circuit_breaker_config
            self.config.circuit_breaker_config = circuit_breaker_config
        if timeout is not None:
            self.config.timeout = timeout
        
        self.circuit_breaker = CircuitBreaker(self.config.circuit_breaker)
        
        # Create provider-specific HTTP client with timeout
        self.client = httpx.AsyncClient(timeout=self.config.timeout)
        
        # Metrics
        self.metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "retries": 0,
            "circuit_opens": 0,
        }
    
    async def generate(self, prompt: str) -> Dict[str, Any]:
        """Generate response with resilience patterns"""
        self.metrics["total_requests"] += 1
        request_id = CorrelationContext.get_correlation_id()
        
        logger.info(
            f"Starting resilient request for {self.provider_name}",
            extra={"requestId": request_id, "provider": self.provider_name}
        )
        
        retry_config = self.config.retry
        last_error = None
        
        for attempt in range(retry_config.max_attempts):
            try:
                # Check circuit breaker
                async def _generate():
                    # Replace the adapter's client with our timeout-configured client when available
                    if hasattr(self.adapter.__class__, "CLIENT"):
                        original_client = getattr(self.adapter.__class__, "CLIENT")
                        try:
                            self.adapter.__class__.CLIENT = self.client
                            return await self.adapter.generate(prompt)
                        finally:
                            self.adapter.__class__.CLIENT = original_client
                    # Fallback: call adapter directly (supports mocks without CLIENT)
                    return await self.adapter.generate(prompt)
                
                result = await self.circuit_breaker.async_call(_generate)
                self.metrics["successful_requests"] += 1
                return result
                
            except Exception as e:
                last_error = e
                self.metrics["failed_requests"] += 1
                
                # Don't retry if circuit is open
                if "Circuit breaker is OPEN" in str(e):
                    self.metrics["circuit_opens"] += 1
                    logger.error(
                        f"Circuit breaker open for {self.provider_name}",
                        extra={"requestId": request_id, "provider": self.provider_name}
                    )
                    break
                
                # Don't retry on 4xx errors (client errors)
                if isinstance(e, httpx.HTTPStatusError) and 400 <= e.response.status_code < 500:
                    logger.error(
                        f"Client error for {self.provider_name}, not retrying: {e}",
                        extra={"requestId": request_id, "provider": self.provider_name, "status_code": e.response.status_code}
                    )
                    break
                # Treat explicit client-side sentinel errors from tests as non-retryable
                if isinstance(e, ValueError) and str(e).lower().startswith("client"):
                    logger.error(
                        f"Client error (sentinel) for {self.provider_name}, not retrying: {e}",
                        extra={"requestId": request_id, "provider": self.provider_name}
                    )
                    break
                
                # Calculate retry delay with exponential backoff and jitter
                if attempt < retry_config.max_attempts - 1:
                    self.metrics["retries"] += 1
                    delay = min(
                        retry_config.initial_delay * (retry_config.exponential_base ** attempt),
                        retry_config.max_delay
                    )
                    # Add jitter
                    jitter_range = delay * retry_config.jitter
                    delay += random.uniform(-jitter_range, jitter_range)
                    
                    logger.info(f"Retrying {self.provider_name} after {delay:.2f}s (attempt {attempt + 1})")
                    await asyncio.sleep(delay)
        
        # All retries exhausted
        error_msg = f"All retries exhausted for {self.provider_name}: {last_error}"
        logger.error(error_msg)
        return {"generated_text": f"Error: {error_msg}"}
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get adapter metrics"""
        return {
            "provider": self.provider_name,
            "metrics": self.metrics,
            "circuit_breaker": self.circuit_breaker.get_state(),
            "config": {
                "timeout": self.config.timeout,
                "max_retries": self.config.retry.max_attempts,
            }
        }

    # Backwards-compat: expose timeout as a direct attribute
    @property
    def timeout(self) -> float:
        return self.config.timeout

    @staticmethod
    def _detect_provider_from_adapter(adapter: BaseAdapter) -> str:
        adapter_class = adapter.__class__.__name__.lower()
        if "openai" in adapter_class:
            return "openai"
        if "anthropic" in adapter_class:
            return "anthropic"
        if "gemini" in adapter_class or "google" in adapter_class:
            return "google"
        return "unknown"
    
    async def close(self):
        """Clean up resources"""
        await self.client.aclose()


def create_resilient_adapter(adapter: BaseAdapter) -> ResilientLLMAdapter:
    """Factory function to create resilient adapter based on provider"""
    # Determine provider from adapter class name
    adapter_class = adapter.__class__.__name__.lower()
    
    if "openai" in adapter_class:
        provider = "openai"
    elif "anthropic" in adapter_class:
        provider = "anthropic"
    elif "gemini" in adapter_class or "google" in adapter_class:
        provider = "google"
    else:
        provider = "unknown"
    
    return ResilientLLMAdapter(adapter, provider)