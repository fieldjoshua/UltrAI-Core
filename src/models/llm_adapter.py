"""
LLM Adapter Module.

This module provides a standardized interface for interacting with different
Large Language Model (LLM) providers through a common adapter pattern.
"""

import asyncio
import logging
import os
import time
from abc import ABC, abstractmethod
from typing import Any, AsyncGenerator, Dict, Optional
from urllib.parse import urlparse

import cohere
import google.generativeai as genai
from anthropic import AsyncAnthropic
from mistralai.async_client import MistralAsyncClient
from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

# Import URL validation utilities if available
try:
    from backend.utils.validation import is_url_safe, validate_url

    URL_VALIDATION_AVAILABLE = True
except ImportError:
    # Create stub functions if validation module is not available
    def validate_url(url, check_ips=True):
        """Stub function when validation module is not available."""
        return True

    def is_url_safe(url, check_ips=True):
        """Stub function when validation module is not available."""
        return True

    URL_VALIDATION_AVAILABLE = False


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

    async def stream_generate(
        self, prompt: str, **options
    ) -> AsyncGenerator[str, None]:
        """
        Generate a streaming response from the LLM.

        Args:
            prompt: The input prompt
            **options: Additional provider-specific options

        Yields:
            Chunks of the generated text response

        Note:
            Default implementation returns the full response as a single chunk.
            Providers that support streaming should override this method.
        """
        # Default implementation for providers that don't support streaming
        full_response = await self.generate(prompt, **options)
        yield full_response

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

    def __init__(self, api_key: str, model: str = "gpt-4", **kwargs):
        super().__init__(name="openai", api_key=api_key)

        # Extract and validate base_url if provided
        base_url = kwargs.get("base_url")
        if base_url and URL_VALIDATION_AVAILABLE:
            try:
                validate_url(base_url)
                self.logger.info(f"Using custom base URL for OpenAI: {base_url}")
                self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)
            except ValueError as e:
                self.logger.warning(f"Invalid base URL, using default: {e}")
                self.client = AsyncOpenAI(api_key=api_key)
        else:
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

        # Check if we're in mock mode (using a placeholder API key or USE_MOCK is enabled)
        use_mock = os.environ.get("USE_MOCK", "false").lower() in ("true", "1", "yes")
        if self.api_key.startswith("sk-mock") or (not self.api_key and use_mock):
            # Return mock response
            if use_mock:
                await asyncio.sleep(1)  # Add a short delay to simulate API call

                # Import local only when in mock mode to avoid circular imports
                try:
                    from backend.mock_llm_service import MOCK_RESPONSES

                    model = options.get("model", self.model)
                    mock_response = MOCK_RESPONSES.get(
                        model,
                        f"Mock response from OpenAI {model}. This would be an intelligent analysis of your prompt.",
                    )

                    self.logger.info(
                        f"Returning mock response for OpenAI model {model}"
                    )
                    return f"{mock_response}\n\n[Note: This is a mock response as Ultra is running in mock mode]"
                except ImportError:
                    # Fallback if mock_llm_service is not available
                    return f"Mock response from OpenAI {self.model}: The capital of France is Paris."
            else:
                # If USE_MOCK isn't set but we have a mock key, return a message about needing an API key
                return "To use OpenAI models, please provide a valid API key by setting OPENAI_API_KEY in your environment."

        try:
            model = options.get("model", self.model)
            max_tokens = options.get("max_tokens", 1500)
            temperature = options.get("temperature", 0.7)
            system_msg = options.get("system_message", "You are a helpful assistant.")

            self.logger.debug(
                f"Calling OpenAI model {model} with prompt: {prompt[:50]}..."
            )
            response = await self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=max_tokens,
                temperature=temperature,
            )
            self.logger.debug(f"OpenAI call successful for model {model}")
            return response.choices[0].message.content
        except Exception as e:
            self.logger.error(
                f"OpenAI API call failed for model {options.get('model', self.model)}: {e}",
                exc_info=True,
            )
            if os.environ.get("USE_MOCK", "false").lower() in ("true", "1", "yes"):
                self.logger.info("Falling back to mock response due to error")
                return f"Mock response from OpenAI {self.model} (fallback after error): The capital of France is Paris."
            else:
                raise

    async def stream_generate(
        self, prompt: str, **options
    ) -> AsyncGenerator[str, None]:
        """
        Generate a streaming response from OpenAI.

        Args:
            prompt: The input prompt
            **options: Additional options including:
                model: Model to use (default: self.model)
                max_tokens: Maximum tokens (default: 1500)
                temperature: Temperature (default: 0.7)
                system_message: System message (default: "You are a helpful assistant.")

        Yields:
            Chunks of the generated text response
        """
        await self._respect_rate_limit()

        try:
            model = options.get("model", self.model)
            max_tokens = options.get("max_tokens", 1500)
            temperature = options.get("temperature", 0.7)
            system_msg = options.get("system_message", "You are a helpful assistant.")

            stream = await self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=max_tokens,
                temperature=temperature,
                stream=True,
            )

            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            self.logger.error(f"OpenAI streaming API call failed: {e}")
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

    def __init__(self, api_key: str, model: str = "claude-3-opus-20240229", **kwargs):
        super().__init__(name="anthropic", api_key=api_key)

        # Extract and validate base_url if provided
        base_url = kwargs.get("base_url")
        if base_url and URL_VALIDATION_AVAILABLE:
            try:
                validate_url(base_url)
                self.logger.info(f"Using custom base URL for Anthropic: {base_url}")
                self.client = AsyncAnthropic(api_key=api_key, base_url=base_url)
            except ValueError as e:
                self.logger.warning(f"Invalid base URL, using default: {e}")
                self.client = AsyncAnthropic(api_key=api_key)
        else:
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

        # Check if we're in mock mode (using a placeholder API key or USE_MOCK is enabled)
        use_mock = os.environ.get("USE_MOCK", "false").lower() in ("true", "1", "yes")
        if self.api_key.startswith("sk-ant-mock") or (not self.api_key and use_mock):
            # Return mock response
            if use_mock:
                await asyncio.sleep(1.2)  # Add a short delay to simulate API call

                # Import local only when in mock mode to avoid circular imports
                try:
                    from backend.mock_llm_service import MOCK_RESPONSES

                    model = options.get("model", self.model)
                    mock_response = MOCK_RESPONSES.get(
                        model,
                        f"Mock response from Anthropic {model}. I would provide a thoughtful and nuanced analysis if this were a real Claude model.",
                    )

                    self.logger.info(
                        f"Returning mock response for Anthropic model {model}"
                    )
                    return f"{mock_response}\n\n[Note: This is a mock response as Ultra is running in mock mode]"
                except ImportError:
                    # Fallback if mock_llm_service is not available
                    return f"Mock response from Anthropic {self.model}: The capital of France is Paris."
            else:
                # If USE_MOCK isn't set but we have a mock key, return a message about needing an API key
                return "To use Anthropic/Claude models, please provide a valid API key by setting ANTHROPIC_API_KEY in your environment."

        try:
            model = options.get("model", self.model)
            max_tokens = options.get("max_tokens", 4000)
            temperature = options.get("temperature", 0.7)

            self.logger.debug(
                f"Calling Anthropic model {model} with prompt: {prompt[:50]}..."
            )
            response = await self.client.messages.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
            )
            self.logger.debug(f"Anthropic call successful for model {model}")
            return response.content[0].text
        except Exception as e:
            self.logger.error(
                f"Anthropic API call failed for model {options.get('model', self.model)}: {e}",
                exc_info=True,
            )
            if os.environ.get("USE_MOCK", "false").lower() in ("true", "1", "yes"):
                self.logger.info("Falling back to mock response due to error")
                return f"Mock response from Anthropic {self.model} (fallback after error): The capital of France is Paris."
            else:
                raise

    async def stream_generate(
        self, prompt: str, **options
    ) -> AsyncGenerator[str, None]:
        """
        Generate a streaming response from Anthropic Claude.

        Args:
            prompt: The input prompt
            **options: Additional options including:
                model: Model to use (default: self.model)
                max_tokens: Maximum tokens (default: 4000)
                temperature: Temperature (default: 0.7)

        Yields:
            Chunks of the generated text response
        """
        await self._respect_rate_limit()

        try:
            model = options.get("model", self.model)
            max_tokens = options.get("max_tokens", 4000)
            temperature = options.get("temperature", 0.7)

            stream = await self.client.messages.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
                stream=True,
            )

            async for chunk in stream:
                # Handle different versions of anthropic-sdk
                if (
                    hasattr(chunk, "delta")
                    and hasattr(chunk.delta, "text")
                    and chunk.delta.text
                ):
                    yield chunk.delta.text
                elif hasattr(chunk, "type") and chunk.type == "content_block_delta":
                    if hasattr(chunk, "delta") and hasattr(chunk.delta, "text"):
                        yield chunk.delta.text
                elif (
                    hasattr(chunk, "content")
                    and chunk.content
                    and len(chunk.content) > 0
                ):
                    for content_block in chunk.content:
                        if hasattr(content_block, "text") and content_block.text:
                            yield content_block.text

        except Exception as e:
            self.logger.error(f"Anthropic streaming API call failed: {e}")
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
        # Only configure genai with API key if it's valid
        # Otherwise it will error and we can't use mock mode
        if api_key and not api_key.startswith("AIza-mock") and len(api_key) > 10:
            try:
                genai.configure(api_key=api_key)
            except Exception as e:
                self.logger.warning(f"Failed to configure Gemini with API key: {e}")
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

        # Check if we're in mock mode (using a placeholder API key or USE_MOCK is enabled)
        use_mock = os.environ.get("USE_MOCK", "false").lower() in ("true", "1", "yes")
        if self.api_key.startswith("AIza-mock") or (not self.api_key and use_mock):
            # Return mock response
            if use_mock:
                await asyncio.sleep(0.8)  # Add a short delay to simulate API call

                # Import local only when in mock mode to avoid circular imports
                try:
                    from backend.mock_llm_service import MOCK_RESPONSES

                    model = options.get("model", self.model)
                    mock_response = MOCK_RESPONSES.get(
                        model,
                        f"Mock response from Google Gemini {model}. This would be an insightful analysis if using the actual Gemini model.",
                    )

                    self.logger.info(
                        f"Returning mock response for Gemini model {model}"
                    )
                    return f"{mock_response}\n\n[Note: This is a mock response as Ultra is running in mock mode]"
                except ImportError:
                    # Fallback if mock_llm_service is not available
                    return f"Mock response from Google Gemini {self.model}: The capital of France is Paris."
            else:
                # If USE_MOCK isn't set but we have a mock key, return a message about needing an API key
                return "To use Google/Gemini models, please provide a valid API key by setting GOOGLE_API_KEY in your environment."

        try:
            model = options.get("model", self.model)
            temperature = options.get("temperature", 0.7)

            # If Google key is empty or invalid, we can't initialize the API
            if (
                not self.api_key
                or len(self.api_key) < 10
                or self.api_key.startswith("AIza-mock")
            ):
                raise ValueError("Invalid or missing Google API key")

            # Check if Google SDK is already configured
            try:
                self.logger.debug(
                    f"Calling Gemini model {self.model} with prompt: {prompt[:50]}..."
                )
                client = genai.GenerativeModel(self.model)
                response = await client.generate_content_async(prompt)
                self.logger.debug(f"Gemini call successful for model {self.model}")
                return response.text
            except Exception as e:
                self.logger.error(f"Gemini API call failed with error: {e}")
                # In mock mode, return a mock response even for API errors
                if use_mock:
                    return f"Mock response from Google Gemini {self.model} (fallback): The capital of France is Paris."
                else:
                    raise
        except Exception as e:
            self.logger.error(
                f"Gemini API call failed for model {self.model}: {e}", exc_info=True
            )
            if use_mock:
                self.logger.info("Falling back to mock response due to error")
                return f"Mock response from Google Gemini {self.model} (fallback after error): The capital of France is Paris."
            else:
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

    async def stream_generate(
        self, prompt: str, **options
    ) -> AsyncGenerator[str, None]:
        """
        Generate a streaming response from Mistral AI.

        Args:
            prompt: The input prompt
            **options: Additional options including:
                model: Model to use (default: self.model)
                max_tokens: Maximum tokens (default: 1000)
                temperature: Temperature (default: 0.7)

        Yields:
            Chunks of the generated text response
        """
        await self._respect_rate_limit()

        try:
            model = options.get("model", self.model)
            max_tokens = options.get("max_tokens", 1000)
            temperature = options.get("temperature", 0.7)

            stream = await self.client.chat_stream(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
            )

            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            self.logger.error(f"Mistral streaming API call failed: {e}")
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


# Helper function to create the appropriate adapter (sync version)
def create_adapter(provider: str, api_key: str = None, **options) -> LLMAdapter:
    """
    Create an LLM adapter for the specified provider (synchronous version).

    Args:
        provider: The LLM provider ("openai", "anthropic", etc.)
        api_key: The API key (optional for providers like Docker Model Runner)
        **options: Additional provider-specific options

    Returns:
        An instance of the appropriate LLMAdapter

    Raises:
        ValueError: If the provider is not supported or if API endpoints don't validate

    Note:
        For providers that require async initialization, use create_adapter_async instead.
    """
    # This is the synchronous version that only works with adapters that don't need async init
    # Check if trying to use Docker Model Runner with CLI adapter
    if (
        provider.lower() == "docker_modelrunner"
        and os.environ.get("MODEL_RUNNER_TYPE", "cli").lower() == "cli"
    ):
        raise ValueError(
            "Docker Model Runner with CLI adapter requires asynchronous initialization. "
            "Use create_adapter_async instead."
        )

    return _create_adapter_internal(provider, api_key, **options)


# Helper function to create the appropriate adapter (async version)
async def create_adapter_async(
    provider: str, api_key: str = None, **options
) -> LLMAdapter:
    """
    Create an LLM adapter for the specified provider (asynchronous version).

    Args:
        provider: The LLM provider ("openai", "anthropic", etc.)
        api_key: The API key (optional for providers like Docker Model Runner)
        **options: Additional provider-specific options

    Returns:
        An instance of the appropriate LLMAdapter

    Raises:
        ValueError: If the provider is not supported or if API endpoints don't validate
    """
    # Special handling for providers that need async initialization
    if (
        provider.lower() == "docker_modelrunner"
        and os.environ.get("MODEL_RUNNER_TYPE", "cli").lower() == "cli"
    ):
        # Import CLI adapter
        from src.models.docker_modelrunner_cli_adapter import (
            create_modelrunner_cli_adapter,
        )

        model = options.get("model") or os.environ.get("DEFAULT_MODEL", "ai/smollm2")
        return await create_modelrunner_cli_adapter(model=model)

    # For other providers, use the sync implementation
    return _create_adapter_internal(provider, api_key, **options)


# Internal helper function used by both sync and async versions
def _create_adapter_internal(
    provider: str, api_key: str = None, **options
) -> LLMAdapter:
    """Internal implementation for adapter creation."""
    model = options.get("model")
    base_url = options.get("base_url")

    # Validate base_url if provided and validation is available
    if base_url and URL_VALIDATION_AVAILABLE:
        try:
            validate_url(base_url)
        except ValueError as e:
            raise ValueError(f"Invalid base URL for {provider}: {e}")

    # Get endpoint from environment variable if available, otherwise use defaults
    endpoint_env_var = f"{provider.upper()}_API_ENDPOINT"
    endpoint = os.environ.get(endpoint_env_var)

    if endpoint and URL_VALIDATION_AVAILABLE:
        try:
            validate_url(endpoint)
        except ValueError as e:
            # Log but don't fail - fall back to default endpoints
            logging.warning(
                f"Invalid endpoint from environment ({endpoint_env_var}): {e}"
            )
            endpoint = None

    # Pass endpoint to adapter if provided
    if endpoint:
        options["base_url"] = endpoint

    # Remove model from options to avoid "multiple values for keyword argument" error
    adapter_options = options.copy()
    if "model" in adapter_options:
        del adapter_options["model"]

    if provider.lower() == "openai":
        return OpenAIAdapter(api_key, model=model or "gpt-4", **adapter_options)
    elif provider.lower() == "anthropic":
        return AnthropicAdapter(
            api_key, model=model or "claude-3-opus-20240229", **adapter_options
        )
    elif provider.lower() == "gemini":
        return GeminiAdapter(api_key, model=model or "gemini-pro", **adapter_options)
    elif provider.lower() == "mistral":
        return MistralAdapter(
            api_key, model=model or "mistral-large-latest", **adapter_options
        )
    elif provider.lower() == "cohere":
        return CohereAdapter(api_key, model=model or "command", **adapter_options)
    elif (
        provider.lower() == "docker_modelrunner"
        and os.environ.get("MODEL_RUNNER_TYPE", "cli").lower() != "cli"
    ):
        # Only handle API adapter here, CLI adapter is handled in create_adapter_async
        from src.models.docker_modelrunner_adapter import DockerModelRunnerAdapter

        return DockerModelRunnerAdapter(
            model=model or os.environ.get("DEFAULT_MODEL", "phi3:mini"), **options
        )
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")
