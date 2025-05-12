"""
Configuration classes for the BaseOrchestrator.

This module contains the configuration classes used by the BaseOrchestrator
and related components. These classes define the structure for configuring
LLM providers, models, and orchestration parameters.
"""

from enum import Enum
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field


class LLMProvider(str, Enum):
    """Enum representing supported LLM providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    COHERE = "cohere"
    MISTRAL = "mistral"
    CUSTOM = "custom"
    MOCK = "mock"


class ModelConfig(BaseModel):
    """Configuration for a single LLM model."""
    
    provider: LLMProvider
    model_id: str
    api_key: Optional[str] = None
    api_base: Optional[str] = None
    timeout: int = 120
    max_tokens: int = 1000
    temperature: float = 0.7
    weight: float = 1.0
    is_primary: bool = False
    extra_params: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    class Config:
        arbitrary_types_allowed = True


class OrchestratorConfig(BaseModel):
    """Configuration for the BaseOrchestrator."""
    
    models: List[ModelConfig]
    cache_enabled: bool = True
    cache_ttl: int = 3600  # seconds
    parallel_execution: bool = True
    request_timeout: int = 300  # seconds
    max_retries: int = 3
    retry_delay: int = 2  # seconds
    log_level: str = "INFO"
    extra_config: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    class Config:
        arbitrary_types_allowed = True
    
    def get_primary_model(self) -> Optional[ModelConfig]:
        """Get the primary model configuration if defined."""
        for model in self.models:
            if model.is_primary:
                return model
        return self.models[0] if self.models else None
    
    def get_models_by_provider(self, provider: LLMProvider) -> List[ModelConfig]:
        """Get all models for a specific provider."""
        return [model for model in self.models if model.provider == provider]


class RequestConfig(BaseModel):
    """Configuration for a single LLM request."""
    
    prompt: str
    model_configs: Optional[List[ModelConfig]] = None
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    timeout: Optional[int] = None
    extra_params: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    class Config:
        arbitrary_types_allowed = True