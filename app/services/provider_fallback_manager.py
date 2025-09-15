"""
Provider Fallback Manager for handling rate limit scenarios.

This service manages provider prioritization when rate limits are encountered,
ensuring smooth failover to alternative providers.
"""

import os
from typing import List, Dict, Optional, Set
from dataclasses import dataclass
from enum import Enum

from app.utils.logging import get_logger

logger = get_logger("provider_fallback_manager")


class ProviderPriority(Enum):
    """Provider priority levels for fallback scenarios."""
    PRIMARY = 1
    SECONDARY = 2
    TERTIARY = 3
    BACKUP = 4


@dataclass
class ProviderConfig:
    """Configuration for a provider including priority and models."""
    name: str
    priority: ProviderPriority
    models: List[str]
    rate_limited: bool = False
    api_key_configured: bool = False


class ProviderFallbackManager:
    """Manages provider fallback logic when rate limits are encountered."""

    # Default provider priorities (configurable via environment)
    DEFAULT_PRIORITIES = {
        "anthropic": ProviderPriority.PRIMARY,
        "google": ProviderPriority.PRIMARY,
        "openai": ProviderPriority.SECONDARY,
        "huggingface": ProviderPriority.BACKUP
    }

    def __init__(self):
        """Initialize the provider fallback manager."""
        self._providers = self._initialize_providers()
        self._rate_limited_providers: Set[str] = set()
        
    def _initialize_providers(self) -> Dict[str, ProviderConfig]:
        """Initialize provider configurations based on environment."""
        providers = {}
        
        # OpenAI configuration
        if os.getenv("OPENAI_API_KEY"):
            providers["openai"] = ProviderConfig(
                name="openai",
                priority=self._get_provider_priority("openai"),
                models=["gpt-4o", "gpt-4o-mini", "gpt-4", "gpt-3.5-turbo", "o1-preview", "o1-mini"],
                api_key_configured=True
            )
        
        # Anthropic configuration
        if os.getenv("ANTHROPIC_API_KEY"):
            providers["anthropic"] = ProviderConfig(
                name="anthropic",
                priority=self._get_provider_priority("anthropic"),
                models=["claude-3-5-sonnet-20241022", "claude-3-5-haiku-20241022", 
                        "claude-3-opus-20240229", "claude-3-sonnet-20240229"],
                api_key_configured=True
            )
        
        # Google configuration
        if os.getenv("GOOGLE_API_KEY"):
            providers["google"] = ProviderConfig(
                name="google",
                priority=self._get_provider_priority("google"),
                models=["gemini-1.5-pro", "gemini-1.5-flash", "gemini-2.0-flash-exp"],
                api_key_configured=True
            )
        
        # HuggingFace configuration
        if os.getenv("HUGGINGFACE_API_KEY"):
            providers["huggingface"] = ProviderConfig(
                name="huggingface",
                priority=self._get_provider_priority("huggingface"),
                models=["meta-llama/Meta-Llama-3-70B-Instruct", "mistralai/Mixtral-8x7B-Instruct-v0.1"],
                api_key_configured=True
            )
        
        return providers
    
    def _get_provider_priority(self, provider: str) -> ProviderPriority:
        """Get provider priority from environment or use defaults."""
        env_key = f"{provider.upper()}_PRIORITY"
        env_value = os.getenv(env_key)
        
        if env_value:
            try:
                return ProviderPriority(int(env_value))
            except (ValueError, KeyError):
                logger.warning(f"Invalid priority value for {provider}: {env_value}")
        
        return self.DEFAULT_PRIORITIES.get(provider, ProviderPriority.BACKUP)
    
    def mark_rate_limited(self, provider: str) -> None:
        """Mark a provider as rate limited."""
        self._rate_limited_providers.add(provider)
        if provider in self._providers:
            self._providers[provider].rate_limited = True
            logger.warning(f"Provider {provider} marked as rate limited")
    
    def clear_rate_limit(self, provider: str) -> None:
        """Clear rate limit status for a provider."""
        self._rate_limited_providers.discard(provider)
        if provider in self._providers:
            self._providers[provider].rate_limited = False
            logger.info(f"Rate limit cleared for provider {provider}")
    
    def get_available_providers(self, exclude_rate_limited: bool = True) -> List[str]:
        """Get list of available providers sorted by priority."""
        available = []
        
        for provider, config in self._providers.items():
            if config.api_key_configured:
                if not exclude_rate_limited or not config.rate_limited:
                    available.append((provider, config.priority.value))
        
        # Sort by priority (lower value = higher priority)
        available.sort(key=lambda x: x[1])
        return [provider for provider, _ in available]
    
    def get_fallback_models(self, original_provider: str, model_count: int = 2) -> List[str]:
        """Get fallback models when a provider is rate limited."""
        if original_provider not in self._providers:
            logger.error(f"Unknown provider: {original_provider}")
            return []
        
        # Mark the original provider as rate limited
        self.mark_rate_limited(original_provider)
        
        # Get alternative providers
        available_providers = self.get_available_providers(exclude_rate_limited=True)
        
        # Remove the original provider
        if original_provider in available_providers:
            available_providers.remove(original_provider)
        
        # Collect models from alternative providers
        fallback_models = []
        for provider in available_providers:
            if provider in self._providers:
                models = self._providers[provider].models
                # Take up to model_count models from each provider
                fallback_models.extend(models[:model_count])
                if len(fallback_models) >= model_count:
                    break
        
        logger.info(f"Fallback models for {original_provider}: {fallback_models[:model_count]}")
        return fallback_models[:model_count]
    
    def get_provider_for_model(self, model: str) -> Optional[str]:
        """Get the provider for a specific model."""
        for provider, config in self._providers.items():
            if model in config.models:
                return provider
        return None
    
    def suggest_alternative_provider(self, rate_limited_provider: str) -> Optional[str]:
        """Suggest an alternative provider when rate limited."""
        available = self.get_available_providers(exclude_rate_limited=True)
        
        # Remove the rate limited provider
        if rate_limited_provider in available:
            available.remove(rate_limited_provider)
        
        if available:
            suggestion = available[0]  # Highest priority alternative
            logger.info(f"Suggesting {suggestion} as alternative to rate-limited {rate_limited_provider}")
            return suggestion
        
        logger.warning("No alternative providers available")
        return None
    
    def get_environment_config_summary(self) -> Dict[str, any]:
        """Get summary of environment-specific configuration."""
        environment = os.getenv("ENVIRONMENT", "development")
        
        summary = {
            "environment": environment,
            "configured_providers": list(self._providers.keys()),
            "provider_priorities": {
                name: config.priority.name 
                for name, config in self._providers.items()
            },
            "rate_limited_providers": list(self._rate_limited_providers),
            "recommendations": []
        }
        
        # Add environment-specific recommendations
        if environment == "production":
            if "openai" in self._providers and self._providers["openai"].priority == ProviderPriority.PRIMARY:
                summary["recommendations"].append(
                    "Consider prioritizing Anthropic/Google over OpenAI in production to avoid rate limits"
                )
        
        # Check for shared API keys
        if environment != "production":
            summary["recommendations"].append(
                f"Ensure {environment} uses separate API keys from production"
            )
        
        return summary


# Singleton instance
provider_fallback_manager = ProviderFallbackManager()