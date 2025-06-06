"""
Adapter factory for creating LLM adapters.

This module provides factory functions for creating adapter instances
based on model configurations.
"""

import logging
import os
from typing import Any, Dict, Optional

from src.orchestration.config import LLMProvider, ModelConfig

# Import metrics wrapper if available
try:
    from src.adapters.metrics_adapter_wrapper import MetricsAdapterWrapper

    METRICS_AVAILABLE = True
except ImportError:
    METRICS_AVAILABLE = False

logger = logging.getLogger(__name__)


def get_adapter_for_model(model_config: ModelConfig) -> Optional[Any]:
    """
    Get the appropriate adapter for a model configuration.

    This factory function instantiates and returns the correct adapter
    based on the provider specified in the model configuration.

    Args:
        model_config: Configuration for the model

    Returns:
        An instance of the appropriate adapter, or None if adapter creation fails
    """
    provider = model_config.provider

    try:
        if provider == LLMProvider.MOCK:
            from src.adapters.mock_adapter import MockAdapter

            return MockAdapter(model_config)

        elif provider == LLMProvider.OPENAI:
            from src.adapters.openai_adapter import OpenAIAdapter

            return OpenAIAdapter(model_config)

        elif provider == LLMProvider.ANTHROPIC:
            from src.adapters.anthropic_adapter import AnthropicAdapter

            return AnthropicAdapter(model_config)

        elif provider == LLMProvider.GOOGLE:
            from src.adapters.google_adapter import GoogleAdapter

            return GoogleAdapter(model_config)

        elif provider == LLMProvider.COHERE:
            from src.adapters.cohere_adapter import CohereAdapter

            return CohereAdapter(model_config)

        elif provider == LLMProvider.MISTRAL:
            from src.adapters.mistral_adapter import MistralAdapter

            return MistralAdapter(model_config)

        elif provider == LLMProvider.CUSTOM:
            from src.adapters.custom_adapter import CustomAdapter

            return CustomAdapter(model_config)

        else:
            logger.error(f"Unsupported provider: {provider}")
            return None

    except ImportError as e:
        logger.error(f"Failed to import adapter for {provider}: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Error creating adapter for {provider}: {str(e)}")
        return None


def get_available_providers() -> Dict[LLMProvider, bool]:
    """
    Check which LLM providers are available based on environment configuration.

    Returns:
        Dictionary mapping providers to availability status
    """
    result = {}

    # Check OpenAI
    result[LLMProvider.OPENAI] = bool(os.environ.get("OPENAI_API_KEY"))

    # Check Anthropic
    result[LLMProvider.ANTHROPIC] = bool(os.environ.get("ANTHROPIC_API_KEY"))

    # Check Google
    result[LLMProvider.GOOGLE] = bool(os.environ.get("GOOGLE_API_KEY"))

    # Check Cohere
    result[LLMProvider.COHERE] = bool(os.environ.get("COHERE_API_KEY"))

    # Check Mistral
    result[LLMProvider.MISTRAL] = bool(os.environ.get("MISTRAL_API_KEY"))

    # Mock is always available
    result[LLMProvider.MOCK] = True

    # Custom depends on implementation
    result[LLMProvider.CUSTOM] = False

    return result


def get_adapter_names() -> list:
    """
    Get a list of available adapter names based on environment variables.

    Returns:
        List of adapter names
    """
    adapters = []

    # Always check for real providers first
    # OpenAI
    if os.environ.get("OPENAI_API_KEY"):
        adapters.append("openai-gpt4o")

    # Anthropic
    if os.environ.get("ANTHROPIC_API_KEY"):
        adapters.append("anthropic-claude")

    # Google
    if os.environ.get("GOOGLE_API_KEY"):
        adapters.append("google-gemini")

    # Check for mock mode only if no real providers found
    use_mock = os.environ.get("USE_MOCK", "false").lower() == "true"
    if not adapters and use_mock:
        adapters.append("mock-llm")

    # If no adapters found at all, use mock as last resort
    if not adapters:
        adapters.append("mock-llm")

    return adapters


def create_adapter(model_name: str) -> Any:
    """
    Create an adapter instance for the specified model name.

    Args:
        model_name: Name of the model in format provider-model

    Returns:
        Adapter instance
    """
    # Handle explicit mock requests
    if model_name.startswith("mock"):
        from src.adapters.simple_mock_adapter import create_mock_adapter

        return create_mock_adapter(model_name)

    # For real providers, parse provider and model from the name
    parts = model_name.split("-", 1)
    if len(parts) < 2:
        provider_name = "mock"
        model_id = model_name
    else:
        provider_name, model_id = parts

    # Map provider name to enum
    provider_map = {
        "openai": LLMProvider.OPENAI,
        "anthropic": LLMProvider.ANTHROPIC,
        "google": LLMProvider.GOOGLE,
        "cohere": LLMProvider.COHERE,
        "mistral": LLMProvider.MISTRAL,
        "mock": LLMProvider.MOCK,
        "custom": LLMProvider.CUSTOM,
    }

    provider = provider_map.get(provider_name.lower(), LLMProvider.MOCK)

    # Check if we have the API key for this provider
    api_key = os.environ.get(f"{provider_name.upper()}_API_KEY")

    # Create model config
    model_config = ModelConfig(
        provider=provider,
        model_id=model_id,
        api_key=api_key,
        api_base=os.environ.get(f"{provider_name.upper()}_API_BASE"),
        is_primary=(model_name == os.environ.get("DEFAULT_LEAD_MODEL")),
    )

    # Only use mock as fallback if requested or if API key is missing
    use_mock = os.environ.get("USE_MOCK", "false").lower() == "true"
    use_mock_if_needed = api_key is None and use_mock

    if provider != LLMProvider.MOCK and not api_key:
        logger.warning(
            f"No API key found for {provider_name}. {'Using mock adapter instead.' if use_mock else 'Will likely fail.'}"
        )

    try:
        # Create adapter
        async_adapter = get_adapter_for_model(model_config)

        # If we couldn't create it and fallback is allowed, use mock
        if not async_adapter and use_mock_if_needed:
            logger.warning(f"Falling back to mock adapter for {model_name}")
            from src.adapters.simple_mock_adapter import create_mock_adapter

            return create_mock_adapter(model_name)

        if async_adapter:
            # Set provider attribute
            setattr(async_adapter, "provider", provider_name)

            # Wrap adapter with metrics if available
            if METRICS_AVAILABLE and not isinstance(
                async_adapter, MetricsAdapterWrapper
            ):
                async_adapter = MetricsAdapterWrapper(async_adapter)
                logger.info(f"Added metrics tracking to {model_name} adapter")

            # Wrap async adapter in a synchronous wrapper
            from src.adapters.sync_adapter_wrapper import SyncAdapterWrapper

            return SyncAdapterWrapper(async_adapter)

        return None
    except Exception as e:
        logger.error(f"Error creating adapter for {model_name}: {str(e)}")

        # Only fall back to mock if explicitly allowed
        if use_mock_if_needed:
            logger.warning(f"Falling back to mock adapter for {model_name} after error")
            from src.adapters.simple_mock_adapter import create_mock_adapter

            return create_mock_adapter(model_name)
        else:
            # Re-raise the exception if mock fallback is not allowed
            raise
