"""
LLM Adapter Module.

This module provides a standardized interface for interacting with different
Large Language Model (LLM) providers through a common adapter pattern.
"""

import asyncio
import logging
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

import cohere
import google.generativeai as genai
from anthropic import AsyncAnthropic
from mistralai.async_client import MistralAsyncClient
from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential


class LLMAdapter(ABC):
    """Base adapter for LLM integrations."""

    def __init__(self, name: str, api_key: Optional[str] = None):
        """
        Initialize the LLM adapter.

        Args:
            name: The name of the LLM
            api_key: Optional API key
        """
        self.name = name
        self.api_key = api_key
        self.logger = logging.getLogger(f"llm_adapter.{name}")
        self.last_call_time = 0
        self.rate_limit_seconds = 0.5  # Default rate limiting

    @abstractmethod
    async def generate(self, prompt: str, **options) -> str:
        """
        Generate a response from the LLM.

        Args:
            prompt: The input prompt
            **options: Additional provider-specific options

        Returns:
            The generated text response
        """
        pass

    async def check_availability(self) -> bool:
        """
        Check if the LLM is available.

        Returns:
            True if the LLM is available, False otherwise
        """
        try:
            # Simple availability check - attempt to generate a simple response
            response = await self.generate("Hello", max_tokens=10)
            return bool(response)
        except Exception as e:
            self.logger.warning(f"Availability check failed: {e}")
            return False

    def get_capabilities(self) -> Dict[str, Any]:
        """
        Get LLM capabilities.

        Returns:
            Dictionary of capabilities
        """
        return {
            "name": self.name,
            "supports_streaming": False,
            "max_tokens": 4000,
            "supports_functions": False,
            "supports_vision": False,
        }

    async def _respect_rate_limit(self):
        """Respect rate limiting by waiting if needed."""
        now = time.time()
        time_since_last_call = now - self.last_call_time

        if time_since_last_call < self.rate_limit_seconds:
            wait_time = self.rate_limit_seconds - time_since_last_call
            await asyncio.sleep(wait_time)

        self.last_call_time = time.time()


class OpenAIAdapter(LLMAdapter):
    """Adapter for OpenAI models."""

    def __init__(self, api_key: str, model: str = "gpt-4"):
        super().__init__(name="openai", api_key=api_key)
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model
        self.rate_limit_seconds = 0.5  # OpenAI rate limiting

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def generate(self, prompt: str, **options) -> str:
        """
        Generate a response from OpenAI.

        Args:
            prompt: The input prompt
            **options: Additional options including:
                model: Model to use (default: self.model)
                max_tokens: Maximum tokens (default: 1500)
                temperature: Temperature (default: 0.7)
                system_message: System message (default: "You are a helpful assistant.")

        Returns:
            The generated text response
        """
        await self._respect_rate_limit()

        try:
            model = options.get("model", self.model)
            max_tokens = options.get("max_tokens", 1500)
            temperature = options.get("temperature", 0.7)
            system_msg = options.get("system_message", "You are a helpful assistant.")

            response = await self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=max_tokens,
                temperature=temperature,
            )
            return response.choices[0].message.content
        except Exception as e:
            self.logger.error(f"OpenAI API call failed: {e}")
            raise

    def get_capabilities(self) -> Dict[str, Any]:
        """Get OpenAI capabilities."""
        capabilities = super().get_capabilities()
        capabilities.update(
            {
                "supports_streaming": True,
                "supports_functions": True,
                "supports_vision": self.model.startswith("gpt-4-vision")
                or self.model == "gpt-4",
                "max_tokens": 4096 if self.model == "gpt-3.5-turbo" else 8192,
            }
        )
        return capabilities


class AnthropicAdapter(LLMAdapter):
    """Adapter for Anthropic Claude models."""

    def __init__(self, api_key: str, model: str = "claude-3-opus-20240229"):
        super().__init__(name="anthropic", api_key=api_key)
        self.client = AsyncAnthropic(api_key=api_key)
        self.model = model
        self.rate_limit_seconds = 0.5  # Anthropic rate limiting

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def generate(self, prompt: str, **options) -> str:
        """
        Generate a response from Anthropic Claude.

        Args:
            prompt: The input prompt
            **options: Additional options including:
                model: Model to use (default: self.model)
                max_tokens: Maximum tokens (default: 4000)
                temperature: Temperature (default: 0.7)

        Returns:
            The generated text response
        """
        await self._respect_rate_limit()

        try:
            model = options.get("model", self.model)
            max_tokens = options.get("max_tokens", 4000)
            temperature = options.get("temperature", 0.7)

            response = await self.client.messages.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
            )
            return response.content[0].text
        except Exception as e:
            self.logger.error(f"Anthropic API call failed: {e}")
            raise

    def get_capabilities(self) -> Dict[str, Any]:
        """Get Anthropic capabilities."""
        capabilities = super().get_capabilities()
        capabilities.update(
            {
                "supports_streaming": True,
                "supports_vision": "claude-3" in self.model,
                "max_tokens": 100000 if "opus" in self.model else 50000,
            }
        )
        return capabilities


class GeminiAdapter(LLMAdapter):
    """Adapter for Google Gemini models."""

    def __init__(self, api_key: str, model: str = "gemini-pro"):
        super().__init__(name="gemini", api_key=api_key)
        genai.configure(api_key=api_key)
        self.model = model
        self.rate_limit_seconds = 1.0  # Gemini rate limiting

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def generate(self, prompt: str, **options) -> str:
        """
        Generate a response from Google Gemini.

        Args:
            prompt: The input prompt
            **options: Additional options including:
                model: Model to use (default: self.model)
                max_tokens: Maximum tokens (default: 2048)
                temperature: Temperature (default: 0.7)

        Returns:
            The generated text response
        """
        await self._respect_rate_limit()

        try:
            model = options.get("model", self.model)
            temperature = options.get("temperature", 0.7)

            # Use asyncio.to_thread since Gemini doesn't have native async support
            response = await asyncio.to_thread(
                genai.GenerativeModel(model).generate_content,
                prompt,
                generation_config={"temperature": temperature},
            )

            return response.text
        except Exception as e:
            self.logger.error(f"Gemini API call failed: {e}")
            raise

    def get_capabilities(self) -> Dict[str, Any]:
        """Get Gemini capabilities."""
        capabilities = super().get_capabilities()
        capabilities.update(
            {
                "supports_vision": self.model == "gemini-pro-vision",
                "max_tokens": 8192,
            }
        )
        return capabilities


class MistralAdapter(LLMAdapter):
    """Adapter for Mistral AI models."""

    def __init__(self, api_key: str, model: str = "mistral-large-latest"):
        super().__init__(name="mistral", api_key=api_key)
        self.client = MistralAsyncClient(api_key=api_key)
        self.model = model
        self.rate_limit_seconds = 0.5  # Mistral rate limiting

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def generate(self, prompt: str, **options) -> str:
        """
        Generate a response from Mistral AI.

        Args:
            prompt: The input prompt
            **options: Additional options including:
                model: Model to use (default: self.model)
                max_tokens: Maximum tokens (default: 1000)
                temperature: Temperature (default: 0.7)

        Returns:
            The generated text response
        """
        await self._respect_rate_limit()

        try:
            model = options.get("model", self.model)
            max_tokens = options.get("max_tokens", 1000)
            temperature = options.get("temperature", 0.7)

            chat_response = await self.client.chat(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
            )

            return chat_response.choices[0].message.content
        except Exception as e:
            self.logger.error(f"Mistral API call failed: {e}")
            raise

    def get_capabilities(self) -> Dict[str, Any]:
        """Get Mistral capabilities."""
        capabilities = super().get_capabilities()
        capabilities.update(
            {
                "supports_streaming": True,
                "max_tokens": 8192 if "large" in self.model else 4096,
            }
        )
        return capabilities


class CohereAdapter(LLMAdapter):
    """Adapter for Cohere models."""

    def __init__(self, api_key: str, model: str = "command"):
        super().__init__(name="cohere", api_key=api_key)
        self.client = cohere.AsyncClient(api_key)
        self.model = model
        self.rate_limit_seconds = 0.5  # Cohere rate limiting

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def generate(self, prompt: str, **options) -> str:
        """
        Generate a response from Cohere.

        Args:
            prompt: The input prompt
            **options: Additional options including:
                model: Model to use (default: self.model)
                max_tokens: Maximum tokens (default: 1000)
                temperature: Temperature (default: 0.7)

        Returns:
            The generated text response
        """
        await self._respect_rate_limit()

        try:
            model = options.get("model", self.model)
            max_tokens = options.get("max_tokens", 1000)
            temperature = options.get("temperature", 0.7)

            response = await self.client.generate(
                prompt=prompt,
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
            )

            return response.generations[0].text
        except Exception as e:
            self.logger.error(f"Cohere API call failed: {e}")
            raise

    def get_capabilities(self) -> Dict[str, Any]:
        """Get Cohere capabilities."""
        capabilities = super().get_capabilities()
        capabilities.update(
            {
                "max_tokens": 4096,
            }
        )
        return capabilities


# Helper function to create the appropriate adapter
def create_adapter(provider: str, api_key: str, **options) -> LLMAdapter:
    """
    Create an LLM adapter for the specified provider.

    Args:
        provider: The LLM provider ("openai", "anthropic", etc.)
        api_key: The API key
        **options: Additional provider-specific options

    Returns:
        An instance of the appropriate LLMAdapter

    Raises:
        ValueError: If the provider is not supported
    """
    model = options.get("model")

    if provider.lower() == "openai":
        return OpenAIAdapter(api_key, model=model or "gpt-4")
    elif provider.lower() == "anthropic":
        return AnthropicAdapter(api_key, model=model or "claude-3-opus-20240229")
    elif provider.lower() == "gemini":
        return GeminiAdapter(api_key, model=model or "gemini-pro")
    elif provider.lower() == "mistral":
        return MistralAdapter(api_key, model=model or "mistral-large-latest")
    elif provider.lower() == "cohere":
        return CohereAdapter(api_key, model=model or "command")
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")
