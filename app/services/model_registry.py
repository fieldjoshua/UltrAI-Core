"""
Model Registry Service

This service manages model instances, configurations, and lifecycle.
"""

from typing import Any, Dict, List, Optional, Type
from dataclasses import dataclass
from datetime import datetime

from app.utils.logging import get_logger

logger = get_logger("model_registry")


@dataclass
class ModelConfig:
    """Configuration for a model instance."""

    name: str
    version: str
    provider: str
    max_tokens: int
    temperature: float
    timeout_seconds: int
    rate_limit: Dict[str, int]  # requests per minute
    is_active: bool = True
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()


@dataclass
class ModelInstance:
    """A registered model instance."""

    config: ModelConfig
    instance: Any
    last_used: Optional[datetime] = None
    error_count: int = 0
    success_count: int = 0


class ModelRegistry:
    """
    Service for managing model instances and configurations.
    """

    def __init__(self):
        """Initialize the model registry."""
        self._models: Dict[str, ModelInstance] = {}
        self._model_classes: Dict[str, Type[Any]] = {}

    def register_model_class(
        self, name: str, model_class: Type[Any], config: ModelConfig
    ) -> None:
        """
        Register a model class with its configuration.

        Args:
            name: Unique identifier for the model
            model_class: The model class to register
            config: Model configuration
        """
        if name in self._model_classes:
            raise ValueError(f"Model class {name} is already registered")

        self._model_classes[name] = model_class
        logger.info(f"Registered model class: {name}")

    def unregister_model_class(self, name: str) -> None:
        """
        Unregister a model class.

        Args:
            name: Name of the model to unregister
        """
        if name not in self._model_classes:
            raise ValueError(f"Model class {name} is not registered")

        del self._model_classes[name]
        logger.info(f"Unregistered model class: {name}")

    def create_model_instance(self, name: str, **kwargs: Any) -> ModelInstance:
        """
        Create a new model instance.

        Args:
            name: Name of the registered model class
            **kwargs: Additional arguments for model initialization

        Returns:
            ModelInstance: The created model instance
        """
        if name not in self._model_classes:
            raise ValueError(f"Model class {name} is not registered")

        model_class = self._model_classes[name]
        instance = model_class(**kwargs)

        model_instance = ModelInstance(
            config=ModelConfig(
                name=name,
                version=kwargs.get("version", "1.0.0"),
                provider=kwargs.get("provider", "unknown"),
                max_tokens=kwargs.get("max_tokens", 2048),
                temperature=kwargs.get("temperature", 0.7),
                timeout_seconds=kwargs.get("timeout_seconds", 30),
                rate_limit=kwargs.get("rate_limit", {"requests_per_minute": 60}),
            ),
            instance=instance,
        )

        self._models[name] = model_instance
        logger.info(f"Created model instance: {name}")
        return model_instance

    def get_model_instance(self, name: str) -> Optional[ModelInstance]:
        """
        Get a model instance by name.

        Args:
            name: Name of the model instance

        Returns:
            Optional[ModelInstance]: The model instance if found
        """
        return self._models.get(name)

    def list_models(self) -> List[Dict[str, Any]]:
        """
        List all registered models and their status.

        Returns:
            List[Dict[str, Any]]: List of model information
        """
        return [
            {
                "name": name,
                "config": instance.config.__dict__,
                "last_used": instance.last_used,
                "error_count": instance.error_count,
                "success_count": instance.success_count,
            }
            for name, instance in self._models.items()
        ]

    def update_model_config(self, name: str, config_updates: Dict[str, Any]) -> None:
        """
        Update a model's configuration.

        Args:
            name: Name of the model to update
            config_updates: Dictionary of configuration updates
        """
        if name not in self._models:
            raise ValueError(f"Model {name} is not registered")

        instance = self._models[name]
        for key, value in config_updates.items():
            if hasattr(instance.config, key):
                setattr(instance.config, key, value)

        instance.config.updated_at = datetime.now()
        logger.info(f"Updated model config: {name}")

    def record_model_usage(self, name: str, success: bool) -> None:
        """
        Record model usage statistics.

        Args:
            name: Name of the model
            success: Whether the usage was successful
        """
        if name not in self._models:
            raise ValueError(f"Model {name} is not registered")

        instance = self._models[name]
        instance.last_used = datetime.now()

        if success:
            instance.success_count += 1
        else:
            instance.error_count += 1

        logger.debug(f"Recorded model usage: {name} (success={success})")

    def get_model_stats(self, name: str) -> Dict[str, Any]:
        """
        Get usage statistics for a model.

        Args:
            name: Name of the model

        Returns:
            Dict[str, Any]: Model usage statistics
        """
        if name not in self._models:
            raise ValueError(f"Model {name} is not registered")

        instance = self._models[name]
        return {
            "name": name,
            "last_used": instance.last_used,
            "error_count": instance.error_count,
            "success_count": instance.success_count,
            "success_rate": (
                instance.success_count / (instance.success_count + instance.error_count)
                if (instance.success_count + instance.error_count) > 0
                else 0
            ),
        }
