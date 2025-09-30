"""
LLM Configuration Service for health checks and model discovery.

This service provides information about available LLM models based on
configured API keys.
"""

import os
from typing import Dict, List


class LLMConfigService:
    """Service for managing LLM configuration and model availability."""

    # Model definitions for each provider
    PROVIDER_MODELS = {
        "openai": [
            {"provider": "openai", "model": "gpt-4o"},
            {"provider": "openai", "model": "gpt-4o-mini"},
            {"provider": "openai", "model": "gpt-4-turbo"},
            {"provider": "openai", "model": "o1-preview"},
            {"provider": "openai", "model": "o1-mini"},
        ],
        "anthropic": [
            {"provider": "anthropic", "model": "claude-3-5-sonnet-20241022"},
            {"provider": "anthropic", "model": "claude-3-5-haiku-20241022"},
            {"provider": "anthropic", "model": "claude-3-opus-20240229"},
        ],
        "google": [
            {"provider": "google", "model": "gemini-1.5-pro"},
            {"provider": "google", "model": "gemini-1.5-flash"},
            {"provider": "google", "model": "gemini-2.0-flash-exp"},
        ],
        "huggingface": [
            {"provider": "huggingface", "model": "mistralai/Mistral-7B-v0.1"},
        ],
    }

    def get_available_models(self) -> Dict[str, Dict[str, str]]:
        """
        Return dictionary of available models based on configured API keys.
        
        Returns dict format expected by health_service:
        {
            "gpt-4o": {"provider": "openai", "model": "gpt-4o"},
            "claude-3-5-sonnet-20241022": {"provider": "anthropic", "model": "claude-3-5-sonnet-20241022"},
            ...
        }

        Returns:
            Dictionary mapping model names to model info dicts
        """
        available_models = {}

        # Check each provider and add models if API key is configured
        if os.getenv("OPENAI_API_KEY"):
            for model_info in self.PROVIDER_MODELS["openai"]:
                available_models[model_info["model"]] = model_info

        if os.getenv("ANTHROPIC_API_KEY"):
            for model_info in self.PROVIDER_MODELS["anthropic"]:
                available_models[model_info["model"]] = model_info

        if os.getenv("GOOGLE_API_KEY"):
            for model_info in self.PROVIDER_MODELS["google"]:
                available_models[model_info["model"]] = model_info

        if os.getenv("HUGGINGFACE_API_KEY"):
            for model_info in self.PROVIDER_MODELS["huggingface"]:
                available_models[model_info["model"]] = model_info

        return available_models

    def get_providers_with_keys(self) -> List[str]:
        """
        Get list of providers that have API keys configured.

        Returns:
            List of provider names (e.g., ['openai', 'anthropic'])
        """
        providers = []

        if os.getenv("OPENAI_API_KEY"):
            providers.append("openai")

        if os.getenv("ANTHROPIC_API_KEY"):
            providers.append("anthropic")

        if os.getenv("GOOGLE_API_KEY"):
            providers.append("google")

        if os.getenv("HUGGINGFACE_API_KEY"):
            providers.append("huggingface")

        return providers

    def get_model_count_by_provider(self) -> Dict[str, int]:
        """
        Get count of available models for each provider.

        Returns:
            Dictionary mapping provider name to model count
        """
        models = self.get_available_models()
        counts = {}

        for model_info in models:
            provider = model_info["provider"]
            counts[provider] = counts.get(provider, 0) + 1

        return counts


# Export singleton instance
llm_config_service = LLMConfigService()