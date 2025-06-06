"""
Extended adapters for the Simple Core Orchestrator.

This module provides additional adapter implementations for more LLM providers
like Deepseek and Ollama.
"""

import asyncio
import logging
import os
from typing import Any, Dict, Optional

from src.simple_core.adapter import Adapter
from src.simple_core.config import ModelDefinition

# Try to import provider-specific libraries
try:
    import httpx
except ImportError:
    httpx = None

try:
    import ollama
except ImportError:
    ollama = None


class DeepseekAdapter(Adapter):
    """Adapter for Deepseek AI models."""

    def __init__(self, model_def: ModelDefinition):
        """Initialize the Deepseek adapter."""
        super().__init__(model_def)

        # Get API key from model_def or environment
        api_key = model_def.api_key or os.environ.get("DEEPSEEK_API_KEY")
        if not api_key:
            raise ValueError("Deepseek API key is required")

        # Get API base URL from environment or use default
        self.api_base = os.environ.get("DEEPSEEK_API_BASE", "https://api.deepseek.com")

        # Get model ID from options or use default
        self.model_id = model_def.options.get("model_id", "deepseek-chat")

        # Initialize the client
        if httpx is None:
            raise ImportError("httpx library is required for DeepseekAdapter")

        self.client = httpx.AsyncClient(
            base_url=self.api_base, headers={"Authorization": f"Bearer {api_key}"}
        )

        self.logger.info(f"Initialized DeepseekAdapter for model {self.model_id}")

    async def generate(self, prompt: str, options: Dict[str, Any] = None) -> str:
        """
        Generate a response from Deepseek AI.

        Args:
            prompt: The prompt to send
            options: Additional options

        Returns:
            The generated text
        """
        options = options or {}

        # Extract options with defaults
        max_tokens = options.get("max_tokens", 1000)
        temperature = options.get("temperature", 0.7)
        system_message = options.get("system_message", "You are a helpful assistant.")

        try:
            # Create the request payload
            payload = {
                "model": self.model_id,
                "messages": [
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt},
                ],
                "max_tokens": max_tokens,
                "temperature": temperature,
            }

            # Call the Deepseek API
            response = await self.client.post("/v1/chat/completions", json=payload)
            response.raise_for_status()
            result = response.json()

            # Extract and return the response text
            return result["choices"][0]["message"]["content"]

        except Exception as e:
            self.logger.error(f"Deepseek API error: {str(e)}")
            raise

    async def __del__(self):
        """Clean up resources."""
        if hasattr(self, "client") and self.client:
            await self.client.aclose()


class OllamaAdapter(Adapter):
    """Adapter for Ollama local models."""

    def __init__(self, model_def: ModelDefinition):
        """Initialize the Ollama adapter."""
        super().__init__(model_def)

        # Check if Ollama library is available
        if ollama is None:
            raise ImportError("ollama library is required for OllamaAdapter")

        # Get base URL from environment or use default
        self.base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")

        # Get model name from options or environment
        self.model_name = model_def.options.get("model_id") or os.environ.get(
            "OLLAMA_MODEL", "llama3"
        )

        self.logger.info(
            f"Initialized OllamaAdapter for model {self.model_name} at {self.base_url}"
        )

    async def generate(self, prompt: str, options: Dict[str, Any] = None) -> str:
        """
        Generate a response from Ollama.

        Args:
            prompt: The prompt to send
            options: Additional options

        Returns:
            The generated text
        """
        options = options or {}

        # Extract options with defaults
        temperature = options.get("temperature", 0.7)
        system_message = options.get("system_message", "")

        try:
            # Set up client configuration
            ollama.set_host(self.base_url)

            # Prepare the request
            request = {
                "model": self.model_name,
                "prompt": prompt,
                "options": {"temperature": temperature},
            }

            # Add system message if provided
            if system_message:
                request["system"] = system_message

            # Run in executor since Ollama's API isn't async
            loop = asyncio.get_running_loop()
            response_text = await loop.run_in_executor(
                None, lambda: ollama.generate(**request)["response"]
            )

            return response_text

        except Exception as e:
            self.logger.error(f"Ollama error: {str(e)}")
            raise
