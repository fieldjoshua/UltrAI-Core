"""
Model Registry Service for managing LLM models and their capabilities.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import logging
from dataclasses import dataclass, field

from app.utils.hardware import get_device_info, get_optimal_device

logger = logging.getLogger(__name__)


@dataclass
class ModelCapability:
    """Represents a model's capabilities and performance metrics."""

    name: str
    provider: str
    max_tokens: int
    context_window: int
    cost_per_1k_tokens: float
    supported_tasks: List[str]
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class ModelInstance:
    """Represents an instance of a model with its current state."""

    model_id: str
    capability: ModelCapability
    is_available: bool = True
    current_load: float = 0.0
    error_count: int = 0
    last_used: Optional[datetime] = None
    device: str = field(default_factory=get_optimal_device)


class ModelRegistry:
    """Central registry for managing LLM models and their capabilities."""

    def __init__(self):
        self._models: Dict[str, ModelInstance] = {}
        self._capabilities: Dict[str, ModelCapability] = {}
        self._device_info = get_device_info()
        logger.info(
            f"Initialized ModelRegistry with device: {self._device_info['device']}"
        )

    def register_model(
        self,
        model_id: str,
        name: str,
        provider: str,
        max_tokens: int,
        context_window: int,
        cost_per_1k_tokens: float,
        supported_tasks: List[str],
    ) -> None:
        """
        Register a new model with its capabilities.

        Args:
            model_id: Unique identifier for the model
            name: Display name of the model
            provider: Provider of the model (e.g., 'openai', 'anthropic')
            max_tokens: Maximum tokens the model can generate
            context_window: Maximum context window size
            cost_per_1k_tokens: Cost per 1000 tokens
            supported_tasks: List of tasks the model supports
        """
        capability = ModelCapability(
            name=name,
            provider=provider,
            max_tokens=max_tokens,
            context_window=context_window,
            cost_per_1k_tokens=cost_per_1k_tokens,
            supported_tasks=supported_tasks,
        )

        self._capabilities[model_id] = capability
        self._models[model_id] = ModelInstance(
            model_id=model_id,
            capability=capability,
        )
        logger.info(f"Registered model: {name} ({model_id})")

    def get_model(self, model_id: str) -> Optional[ModelInstance]:
        """
        Get a model instance by ID.

        Args:
            model_id: The model's unique identifier

        Returns:
            Optional[ModelInstance]: The model instance if found, None otherwise
        """
        return self._models.get(model_id)

    def get_available_models(self, task: Optional[str] = None) -> List[ModelInstance]:
        """
        Get all available models, optionally filtered by task.

        Args:
            task: Optional task to filter models by

        Returns:
            List[ModelInstance]: List of available model instances
        """
        models = [model for model in self._models.values() if model.is_available]

        if task:
            models = [
                model for model in models if task in model.capability.supported_tasks
            ]

        return models

    def update_model_metrics(
        self,
        model_id: str,
        metrics: Dict[str, float],
    ) -> None:
        """
        Update a model's performance metrics.

        Args:
            model_id: The model's unique identifier
            metrics: Dictionary of metric names and values
        """
        if model_id in self._models:
            self._models[model_id].capability.performance_metrics.update(metrics)
            self._models[model_id].capability.last_updated = datetime.now()
            logger.debug(f"Updated metrics for model: {model_id}")

    def mark_model_unavailable(self, model_id: str) -> None:
        """
        Mark a model as unavailable.

        Args:
            model_id: The model's unique identifier
        """
        if model_id in self._models:
            self._models[model_id].is_available = False
            self._models[model_id].error_count += 1
            logger.warning(f"Marked model as unavailable: {model_id}")

    def mark_model_available(self, model_id: str) -> None:
        """
        Mark a model as available.

        Args:
            model_id: The model's unique identifier
        """
        if model_id in self._models:
            self._models[model_id].is_available = True
            logger.info(f"Marked model as available: {model_id}")

    def get_model_stats(self) -> Dict[str, Any]:
        """
        Get statistics about all registered models.

        Returns:
            Dict[str, Any]: Statistics about the models
        """
        return {
            "total_models": len(self._models),
            "available_models": len(self.get_available_models()),
            "models_by_provider": {
                provider: len(
                    [
                        model
                        for model in self._models.values()
                        if model.capability.provider == provider
                    ]
                )
                for provider in set(
                    model.capability.provider for model in self._models.values()
                )
            },
            "device_info": self._device_info,
        }
