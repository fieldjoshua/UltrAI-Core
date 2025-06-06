"""
Anthropic adapter for interacting with Claude models.

This module provides an adapter for Anthropic models like Claude.
"""

import asyncio
import logging
import os
import time
from typing import Any, Dict, List, Optional

from src.adapters.base_adapter import BaseAdapter
from src.orchestration.config import ModelConfig

# Import metrics if available
try:
    from backend.utils.metrics import MetricsCollector, track_llm_metrics

    METRICS_AVAILABLE = True
except ImportError:
    METRICS_AVAILABLE = False

logger = logging.getLogger(__name__)


class AnthropicAdapter(BaseAdapter):
    """
    Adapter for Anthropic Claude models.

    This adapter interacts with the Anthropic API to generate text
    using Claude models.
    """

    def __init__(self, model_config: ModelConfig):
        """
        Initialize the Anthropic adapter.

        Args:
            model_config: Configuration for the Anthropic model
        """
        super().__init__(model_config)
        self.api_key = model_config.api_key or os.environ.get("ANTHROPIC_API_KEY")
        self.api_base = model_config.api_base or os.environ.get("ANTHROPIC_API_BASE")
        self.model_id = model_config.model_id

        # Map model IDs to actual Anthropic model names
        self.model_map = {
            "claude": "claude-3-opus-20240229",
            "claudesonnet": "claude-3-sonnet-20240229",
            "claudehaiku": "claude-3-haiku-20240307",
            "claude2": "claude-2.1",
            "claude1": "claude-1.2",
        }

        # Get the actual model name
        self.anthropic_model = self.model_map.get(self.model_id, self.model_id)

        # Initialize Anthropic client if API key is available
        if self.api_key:
            try:
                # Dynamically import Anthropic to avoid requiring it for all users
                import anthropic

                self.client = anthropic.Anthropic(api_key=self.api_key)
                logger.info(
                    f"Initialized Anthropic client for model {self.anthropic_model}"
                )
            except (ImportError, Exception) as e:
                logger.error(f"Failed to initialize Anthropic client: {str(e)}")
                self.client = None
        else:
            logger.warning("No Anthropic API key found, adapter will not be functional")
            self.client = None

    async def generate(
        self,
        prompt: str,
        max_tokens: int = None,
        temperature: float = None,
        timeout: int = None,
        **kwargs,
    ) -> str:
        """
        Generate text using Anthropic API.

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
        if not self.client:
            raise Exception("Anthropic client not initialized (missing API key?)")

        # Get default values from model config if not provided
        max_tokens = max_tokens or self.model_config.max_tokens
        temperature = temperature or self.model_config.temperature
        timeout = timeout or self.model_config.timeout

        try:
            # Make the API call with a timeout
            response = await asyncio.wait_for(
                self._generate_async(prompt, max_tokens, temperature, **kwargs),
                timeout=timeout,
            )
            return response
        except asyncio.TimeoutError:
            raise TimeoutError(f"Request timed out after {timeout} seconds")
        except Exception as e:
            logger.error(f"Error in Anthropic generate: {str(e)}")
            raise

    async def _generate_async(
        self, prompt: str, max_tokens: int, temperature: float, **kwargs
    ) -> str:
        """
        Make the async API call to Anthropic.

        This method is separated to allow for proper timeout handling.
        """
        start_time = time.time()
        prompt_tokens = len(prompt.split())  # Simple approximation for input tokens
        status = "success"

        try:
            # Use a thread to make the synchronous API call
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.messages.create(
                    model=self.anthropic_model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    messages=[{"role": "user", "content": prompt}],
                    **kwargs,
                ),
            )

            # Get token counts if available
            input_tokens = (
                response.usage.input_tokens
                if hasattr(response, "usage")
                else prompt_tokens
            )
            output_tokens = (
                response.usage.output_tokens
                if hasattr(response, "usage")
                else len(response.content[0].text.split())
            )

            # Track metrics if available
            if METRICS_AVAILABLE:
                try:
                    metrics = MetricsCollector()
                    metrics.track_llm_request(
                        provider="anthropic",
                        model=self.anthropic_model,
                        start_time=start_time,
                        token_count_input=input_tokens,
                        token_count_output=output_tokens,
                        status="success",
                    )
                except Exception as metrics_error:
                    logger.warning(f"Failed to record metrics: {str(metrics_error)}")

            # Extract the response text
            return response.content[0].text
        except Exception as e:
            logger.error(f"Anthropic API error: {str(e)}")

            # Track error metrics if available
            if METRICS_AVAILABLE:
                try:
                    metrics = MetricsCollector()
                    metrics.track_llm_request(
                        provider="anthropic",
                        model=self.anthropic_model,
                        start_time=start_time,
                        token_count_input=prompt_tokens,
                        token_count_output=0,
                        status="error",
                    )
                except Exception as metrics_error:
                    logger.warning(
                        f"Failed to record error metrics: {str(metrics_error)}"
                    )

            raise

    async def get_embedding(self, text: str, **kwargs) -> List[float]:
        """
        Get embeddings for text.

        Note: As of early 2024, Anthropic doesn't have a native embedding API.
        This method uses a third-party service or falls back to a simple approach.

        Args:
            text: Text to embed
            **kwargs: Additional parameters for the API call

        Returns:
            List of embedding values

        Raises:
            Exception: If the API call fails
        """
        # Currently, Anthropic doesn't have a native embedding API
        # This is a placeholder that raises an exception
        raise NotImplementedError("Anthropic does not currently support embeddings")

    def is_available(self) -> bool:
        """
        Check if the Anthropic adapter is available for use.

        Returns:
            True if the adapter is available, False otherwise
        """
        return self.client is not None
