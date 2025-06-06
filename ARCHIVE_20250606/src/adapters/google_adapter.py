"""
Google adapter for interacting with Google AI models like Gemini.

This module provides an adapter for Google AI models.
"""

import asyncio
import logging
import os
from typing import Any, Dict, List, Optional

from src.adapters.base_adapter import BaseAdapter
from src.orchestration.config import ModelConfig

logger = logging.getLogger(__name__)


class GoogleAdapter(BaseAdapter):
    """
    Adapter for Google AI models.

    This adapter interacts with the Google AI API to generate text
    using models like Gemini.
    """

    def __init__(self, model_config: ModelConfig):
        """
        Initialize the Google adapter.

        Args:
            model_config: Configuration for the Google model
        """
        super().__init__(model_config)
        self.api_key = model_config.api_key or os.environ.get("GOOGLE_API_KEY")
        self.api_base = model_config.api_base or os.environ.get("GOOGLE_API_BASE")
        self.model_id = model_config.model_id

        # Map model IDs to actual Google model names
        self.model_map = {
            "gemini": "gemini-1.0-pro",
            "geminipro": "gemini-1.0-pro",
            "geminiultra": "gemini-1.0-ultra",
            "geminiprovision": "gemini-1.0-pro-vision",
            "geminipro": "gemini-pro",
            "text": "text-bison",
        }

        # Get the actual model name
        self.google_model = self.model_map.get(self.model_id, self.model_id)

        # Initialize Google client if API key is available
        if self.api_key:
            try:
                # Dynamically import Google Generative AI client
                import google.generativeai as genai

                genai.configure(api_key=self.api_key)
                self.client = genai
                logger.info(
                    f"Initialized Google AI client for model {self.google_model}"
                )
            except (ImportError, Exception) as e:
                logger.error(f"Failed to initialize Google AI client: {str(e)}")
                self.client = None
        else:
            logger.warning("No Google API key found, adapter will not be functional")
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
        Generate text using Google AI API.

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
            raise Exception("Google AI client not initialized (missing API key?)")

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
            logger.error(f"Error in Google generate: {str(e)}")
            raise

    async def _generate_async(
        self, prompt: str, max_tokens: int, temperature: float, **kwargs
    ) -> str:
        """
        Make the async API call to Google AI.

        This method is separated to allow for proper timeout handling.
        """
        try:
            # Use a thread to make the synchronous API call
            loop = asyncio.get_event_loop()
            generation_config = {
                "max_output_tokens": max_tokens,
                "temperature": temperature,
                **kwargs,
            }

            # Create the model
            model = self.client.GenerativeModel(
                model_name=self.google_model, generation_config=generation_config
            )

            # Generate the response
            response = await loop.run_in_executor(
                None, lambda: model.generate_content(prompt)
            )

            # Extract the response text
            return response.text
        except Exception as e:
            logger.error(f"Google AI API error: {str(e)}")
            raise

    async def get_embedding(self, text: str, **kwargs) -> List[float]:
        """
        Get embeddings for text using Google AI API.

        Args:
            text: Text to embed
            **kwargs: Additional parameters for the API call

        Returns:
            List of embedding values

        Raises:
            Exception: If the API call fails
        """
        if not self.client:
            raise Exception("Google AI client not initialized (missing API key?)")

        try:
            # Use a thread to make the synchronous API call
            loop = asyncio.get_event_loop()
            embedding_model = "embedding-001"  # Google's embedding model

            response = await loop.run_in_executor(
                None,
                lambda: self.client.embed_content(
                    model=embedding_model, content=text, **kwargs
                ),
            )

            # Extract embeddings
            return response.embedding
        except Exception as e:
            logger.error(f"Google AI embedding error: {str(e)}")
            raise

    def is_available(self) -> bool:
        """
        Check if the Google adapter is available for use.

        Returns:
            True if the adapter is available, False otherwise
        """
        return self.client is not None
