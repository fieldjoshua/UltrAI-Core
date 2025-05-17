"""
Metrics adapter wrapper for tracking LLM usage metrics.

This module provides a wrapper for LLM adapters that adds metrics tracking
to all adapter method calls.
"""

import logging
import time
from typing import Any, Dict, List, Optional, Type

from src.adapters.base_adapter import BaseAdapter
from src.orchestration.config import ModelConfig

# Import metrics if available
try:
    from backend.utils.metrics import MetricsCollector

    METRICS_AVAILABLE = True
except ImportError:
    METRICS_AVAILABLE = False

logger = logging.getLogger(__name__)


class MetricsAdapterWrapper(BaseAdapter):
    """
    Wrapper for BaseAdapter that adds metrics tracking.

    This wrapper can be applied to any adapter implementation to add
    automatic metrics tracking to all API calls.
    """

    def __init__(self, wrapped_adapter: BaseAdapter):
        """
        Initialize with a wrapped adapter.

        Args:
            wrapped_adapter: The adapter to wrap with metrics
        """
        self.adapter = wrapped_adapter
        self.model_config = wrapped_adapter.model_config

        # Extract provider and model for metrics
        self.provider = self._get_provider_name()
        self.model = self._get_model_name()

    def _get_provider_name(self) -> str:
        """Get the provider name from the adapter class name."""
        adapter_class = self.adapter.__class__.__name__
        if "Adapter" in adapter_class:
            provider = adapter_class.replace("Adapter", "").lower()
            return provider
        return "unknown"

    def _get_model_name(self) -> str:
        """Get the model name from the adapter."""
        if hasattr(self.adapter, "model_id"):
            return self.adapter.model_id
        return getattr(self.model_config, "model_id", "unknown")

    async def generate(
        self,
        prompt: str,
        max_tokens: int = None,
        temperature: float = None,
        timeout: int = None,
        **kwargs,
    ) -> str:
        """
        Generate text with metrics tracking.

        Args:
            prompt: The prompt to send to the model
            max_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature
            timeout: Request timeout in seconds
            **kwargs: Additional parameters for the API call

        Returns:
            Generated text

        Raises:
            Exception: If the API call fails
        """
        start_time = time.time()
        input_tokens = len(prompt.split())  # Simple approximation

        try:
            # Call the wrapped adapter
            result = await self.adapter.generate(
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                timeout=timeout,
                **kwargs,
            )

            # Record success metrics
            if METRICS_AVAILABLE:
                try:
                    output_tokens = len(result.split())  # Simple approximation

                    metrics = MetricsCollector()
                    metrics.track_llm_request(
                        provider=self.provider,
                        model=self.model,
                        start_time=start_time,
                        token_count_input=input_tokens,
                        token_count_output=output_tokens,
                        status="success",
                    )
                except Exception as e:
                    logger.warning(f"Failed to record metrics: {str(e)}")

            return result

        except Exception as e:
            # Record error metrics
            if METRICS_AVAILABLE:
                try:
                    metrics = MetricsCollector()
                    metrics.track_llm_request(
                        provider=self.provider,
                        model=self.model,
                        start_time=start_time,
                        token_count_input=input_tokens,
                        token_count_output=0,
                        status="error",
                    )
                except Exception as metrics_error:
                    logger.warning(
                        f"Failed to record error metrics: {str(metrics_error)}"
                    )

            # Re-raise the original exception
            raise

    async def get_embedding(self, text: str, **kwargs) -> List[float]:
        """
        Get embeddings for text with metrics tracking.

        Args:
            text: Text to embed
            **kwargs: Additional parameters for the API call

        Returns:
            List of embedding values

        Raises:
            Exception: If the API call fails
        """
        start_time = time.time()
        input_tokens = len(text.split())  # Simple approximation

        try:
            # Call the wrapped adapter
            result = await self.adapter.get_embedding(text, **kwargs)

            # Record success metrics
            if METRICS_AVAILABLE:
                try:
                    metrics = MetricsCollector()
                    metrics.track_llm_request(
                        provider=f"{self.provider}_embedding",
                        model=self.model,
                        start_time=start_time,
                        token_count_input=input_tokens,
                        token_count_output=len(result),
                        status="success",
                    )
                except Exception as e:
                    logger.warning(f"Failed to record embedding metrics: {str(e)}")

            return result

        except Exception as e:
            # Record error metrics
            if METRICS_AVAILABLE:
                try:
                    metrics = MetricsCollector()
                    metrics.track_llm_request(
                        provider=f"{self.provider}_embedding",
                        model=self.model,
                        start_time=start_time,
                        token_count_input=input_tokens,
                        token_count_output=0,
                        status="error",
                    )
                except Exception as metrics_error:
                    logger.warning(
                        f"Failed to record embedding error metrics: {str(metrics_error)}"
                    )

            # Re-raise the original exception
            raise

    def is_available(self) -> bool:
        """
        Check if the adapter is available for use.

        Returns:
            True if the adapter is available, False otherwise
        """
        return self.adapter.is_available()


def with_metrics(adapter_class: Type[BaseAdapter]) -> Type[BaseAdapter]:
    """
    Decorator to add metrics tracking to an adapter class.

    Usage:
        @with_metrics
        class MyAdapter(BaseAdapter):
            ...

    Args:
        adapter_class: The adapter class to decorate

    Returns:
        The decorated adapter class with metrics tracking
    """
    original_init = adapter_class.__init__

    def __init__(self, *args, **kwargs):
        original_init(self, *args, **kwargs)
        self = MetricsAdapterWrapper(self)

    adapter_class.__init__ = __init__
    return adapter_class
