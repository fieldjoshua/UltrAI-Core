"""
Core configuration classes for the Simple Core Orchestrator.

This module provides the fundamental configuration classes for the
orchestrator, including ModelDefinition and Config.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ModelDefinition:
    """Definition for a single LLM model."""

    name: str
    provider: str
    priority: int = 0
    api_key: Optional[str] = None
    options: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate model definition after initialization."""
        if not self.name:
            raise ValueError("Model name cannot be empty")
        if not self.provider:
            raise ValueError("Model provider cannot be empty")


@dataclass
class Config:
    """Configuration for the Simple Core Orchestrator."""

    models: List[ModelDefinition]
    parallel: bool = True
    timeout: float = 30.0
    cache_enabled: bool = False
    retry_count: int = 1
    options: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate configuration after initialization."""
        if not self.models:
            raise ValueError("At least one model must be defined")

        # Set default options
        default_options = {
            "log_level": "INFO",
            "max_tokens": 1000,
            "temperature": 0.7,
        }

        # Apply defaults for any missing options
        for key, value in default_options.items():
            if key not in self.options:
                self.options[key] = value

    def get_models_by_priority(self) -> List[ModelDefinition]:
        """Get models sorted by priority (highest first)."""
        return sorted(self.models, key=lambda m: m.priority, reverse=True)

    def get_primary_model(self) -> ModelDefinition:
        """Get the primary model (highest priority)."""
        models = self.get_models_by_priority()
        return models[0] if models else None

    def to_cache_key(self) -> str:
        """Generate a string representation of config for cache keys."""
        model_str = "_".join(m.name for m in sorted(self.models, key=lambda x: x.name))
        return f"{model_str}_{self.parallel}_{self.options.get('temperature', 0.7)}"
