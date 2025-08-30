"""
Factory for creating LLM adapters with optional enhanced error handling.

This module provides a factory that can create either legacy or enhanced
adapters based on configuration, allowing for gradual migration.
"""

import os
import httpx
from typing import Union, Optional

from app.services.llm_adapters import (
    OpenAIAdapter,
    AnthropicAdapter,
    GeminiAdapter,
    HuggingFaceAdapter,
    CLIENT
)
from app.services.enhanced_llm_adapters import (
    EnhancedOpenAIAdapter,
    EnhancedAnthropicAdapter,
    EnhancedGeminiAdapter,
    EnhancedHuggingFaceAdapter
)


class LLMAdapterFactory:
    """Factory for creating LLM adapters with configurable error handling."""
    
    # Feature flag for enhanced error handling
    USE_ENHANCED_ADAPTERS = os.getenv("USE_ENHANCED_LLM_ADAPTERS", "false").lower() == "true"
    
    @classmethod
    def create_adapter(
        cls,
        provider: str,
        api_key: str,
        model: str,
        force_enhanced: Optional[bool] = None,
        client: Optional[httpx.AsyncClient] = None
    ) -> Union[OpenAIAdapter, AnthropicAdapter, GeminiAdapter, HuggingFaceAdapter,
               EnhancedOpenAIAdapter, EnhancedAnthropicAdapter, EnhancedGeminiAdapter, EnhancedHuggingFaceAdapter]:
        """
        Create an LLM adapter for the specified provider.
        
        Args:
            provider: Provider name (openai, anthropic, google, huggingface)
            api_key: API key for the provider
            model: Model name/ID
            force_enhanced: Override the global setting for enhanced adapters
            client: HTTP client to use (defaults to shared CLIENT)
        
        Returns:
            LLM adapter instance
        
        Raises:
            ValueError: If provider is unknown
        """
        use_enhanced = force_enhanced if force_enhanced is not None else cls.USE_ENHANCED_ADAPTERS
        http_client = client or CLIENT
        
        if provider == "openai":
            if use_enhanced:
                return EnhancedOpenAIAdapter(api_key, model, http_client)
            else:
                return OpenAIAdapter(api_key, model)
        
        elif provider == "anthropic":
            if use_enhanced:
                return EnhancedAnthropicAdapter(api_key, model, http_client)
            else:
                return AnthropicAdapter(api_key, model)
        
        elif provider == "google":
            if use_enhanced:
                return EnhancedGeminiAdapter(api_key, model, http_client)
            else:
                return GeminiAdapter(api_key, model)
        
        elif provider == "huggingface":
            if use_enhanced:
                return EnhancedHuggingFaceAdapter(api_key, model, http_client)
            else:
                return HuggingFaceAdapter(api_key, model)
        
        else:
            raise ValueError(f"Unknown provider: {provider}")
    
    @classmethod
    def create_from_model_name(
        cls,
        model: str,
        force_enhanced: Optional[bool] = None,
        client: Optional[httpx.AsyncClient] = None
    ) -> Optional[Union[OpenAIAdapter, AnthropicAdapter, GeminiAdapter, HuggingFaceAdapter,
                        EnhancedOpenAIAdapter, EnhancedAnthropicAdapter, EnhancedGeminiAdapter, EnhancedHuggingFaceAdapter]]:
        """
        Create an adapter based on model name, inferring the provider.
        
        Args:
            model: Model name (e.g., "gpt-4", "claude-3-sonnet", "gemini-pro")
            force_enhanced: Override the global setting for enhanced adapters
            client: HTTP client to use
        
        Returns:
            LLM adapter instance or None if API key is missing
        """
        # Determine provider from model name
        if model.startswith("gpt") or model.startswith("o1"):
            provider = "openai"
            api_key = os.getenv("OPENAI_API_KEY")
        elif model.startswith("claude"):
            provider = "anthropic"
            api_key = os.getenv("ANTHROPIC_API_KEY")
        elif model.startswith("gemini"):
            provider = "google"
            api_key = os.getenv("GOOGLE_API_KEY")
        elif "/" in model:  # HuggingFace model format
            provider = "huggingface"
            api_key = os.getenv("HUGGINGFACE_API_KEY")
        else:
            raise ValueError(f"Cannot determine provider for model: {model}")
        
        if not api_key:
            return None
        
        return cls.create_adapter(provider, api_key, model, force_enhanced, client)