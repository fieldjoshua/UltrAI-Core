"""
LLM Configuration Service

This service manages the available LLMs, their configurations, and capabilities.
It provides functions to:
- List available LLMs
- Get LLM details
- Check LLM status and availability
- Register and update LLM configurations
"""

import time
from typing import Dict, List, Optional, Any

from backend.models.enhanced_orchestrator import (
    OrchestratorConfig,
    EnhancedOrchestrator,
)
from backend.utils.logging import get_logger

logger = get_logger("llm_config_service", "logs/llm_config.log")


class LLMConfigService:
    """Service for managing LLM configurations and availability"""

    def __init__(self):
        """Initialize the LLM configuration service"""
        self.orchestrator = None
        self._available_models = {}
        self._capabilities_cache = {}
        self._last_update = 0
        self._refresh_interval = 300  # 5 minutes cache validity

        # Try to initialize the orchestrator
        try:
            config = OrchestratorConfig()
            self.orchestrator = EnhancedOrchestrator(config)
            logger.info("LLM Config Service initialized with orchestrator")
        except Exception as e:
            logger.error(f"Failed to initialize orchestrator: {str(e)}")
            self.orchestrator = None

    def refresh_models_if_needed(self):
        """Refresh model information if cache is stale"""
        current_time = time.time()

        # If the cache is still valid, return
        if (
            current_time - self._last_update < self._refresh_interval
            and self._available_models
        ):
            return

        # Refresh the models list
        if self.orchestrator:
            try:
                self._available_models = {}
                # Get information from all registered models
                for name, registration in self.orchestrator.model_registry.items():
                    self._available_models[name] = {
                        "name": name,
                        "provider": registration.provider,
                        "model": registration.model,
                        "weight": registration.weight,
                        "capabilities": registration.capabilities,
                        "tags": registration.tags,
                        "available": True,
                        "status": "ready",
                    }
                self._last_update = current_time
                logger.info(
                    f"Refreshed model information. Found {len(self._available_models)} models."
                )
            except Exception as e:
                logger.error(f"Failed to refresh models: {str(e)}")
        else:
            # No orchestrator available, provide default models
            self._available_models = {
                "gpt-4": {
                    "name": "gpt-4",
                    "provider": "openai",
                    "model": "gpt-4",
                    "weight": 1.0,
                    "capabilities": {
                        "max_tokens": 8192,
                        "supports_streaming": True,
                        "supports_tools": True,
                    },
                    "tags": ["premium", "reasoning"],
                    "available": True,
                    "status": "ready",
                },
                "gpt-3.5-turbo": {
                    "name": "gpt-3.5-turbo",
                    "provider": "openai",
                    "model": "gpt-3.5-turbo",
                    "weight": 0.8,
                    "capabilities": {
                        "max_tokens": 4096,
                        "supports_streaming": True,
                        "supports_tools": True,
                    },
                    "tags": ["fast", "cost-effective"],
                    "available": True,
                    "status": "ready",
                },
                "claude-3-opus": {
                    "name": "claude-3-opus",
                    "provider": "anthropic",
                    "model": "claude-3-opus",
                    "weight": 0.9,
                    "capabilities": {
                        "max_tokens": 100000,
                        "supports_streaming": True,
                        "supports_tools": False,
                    },
                    "tags": ["premium", "reasoning"],
                    "available": True,
                    "status": "ready",
                },
            }
            self._last_update = current_time
            logger.warning(
                "Using default model information due to missing orchestrator"
            )

    def get_available_models(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all available LLM models

        Returns:
            Dictionary of model information keyed by model name
        """
        self.refresh_models_if_needed()
        return self._available_models

    def get_model_details(self, model_name: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific model

        Args:
            model_name: Name of the model to retrieve

        Returns:
            Dictionary with model details or None if not found
        """
        self.refresh_models_if_needed()
        return self._available_models.get(model_name)

    def get_models_by_tags(self, tags: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Get models that have the specified tags

        Args:
            tags: List of tags to filter by

        Returns:
            Dictionary of matching models
        """
        self.refresh_models_if_needed()
        result = {}

        for name, model in self._available_models.items():
            if all(tag in model.get("tags", []) for tag in tags):
                result[name] = model

        return result

    def get_models_by_capability(
        self, capability: str, value: Any = True
    ) -> Dict[str, Dict[str, Any]]:
        """
        Get models that have a specific capability

        Args:
            capability: The capability to filter by
            value: The expected value of the capability

        Returns:
            Dictionary of matching models
        """
        self.refresh_models_if_needed()
        result = {}

        for name, model in self._available_models.items():
            if model.get("capabilities", {}).get(capability) == value:
                result[name] = model

        return result

    def get_model_status(self, model_name: str) -> Dict[str, Any]:
        """
        Get the current status of a model

        Args:
            model_name: Name of the model to check

        Returns:
            Dictionary with status information
        """
        model = self.get_model_details(model_name)

        if not model:
            return {
                "name": model_name,
                "available": False,
                "status": "not_found",
                "message": f"Model {model_name} not found",
            }

        # Check if the orchestrator has circuit breakers for this model
        if self.orchestrator and self.orchestrator.config.circuit_breaker_enabled:
            circuit = self.orchestrator.circuit_breakers.get(model_name)
            if circuit and not circuit.allow_request():
                return {
                    "name": model_name,
                    "available": False,
                    "status": "circuit_open",
                    "message": f"Circuit breaker open for {model_name}",
                    "recovery_time": circuit.expected_recovery_time(),
                }

        return {
            "name": model_name,
            "available": model.get("available", True),
            "status": model.get("status", "ready"),
            "message": "Model is available and ready",
        }

    def get_available_analysis_patterns(self) -> List[str]:
        """
        Get all available analysis patterns

        Returns:
            List of available pattern names
        """
        if self.orchestrator:
            try:
                return list(self.orchestrator.patterns.keys())
            except Exception as e:
                logger.error(f"Failed to get patterns: {str(e)}")

        # Default patterns if orchestrator not available
        return [
            "gut",
            "confidence",
            "perspective",
            "investigative",
            "comparative",
            "comprehensive",
            "concise",
            "creative",
        ]

    def get_available_analysis_modes(self) -> List[Dict[str, Any]]:
        """
        Get all available analysis modes

        Returns:
            List of available analysis modes with details
        """
        if self.orchestrator:
            try:
                modes = []
                for name, mode in self.orchestrator.config.analysis_modes.items():
                    modes.append(
                        {
                            "name": name,
                            "pattern": mode.pattern,
                            "model_selection_strategy": mode.model_selection_strategy,
                            "timeout": mode.timeout,
                            "description": self._get_mode_description(name),
                        }
                    )
                return modes
            except Exception as e:
                logger.error(f"Failed to get analysis modes: {str(e)}")

        # Default modes if orchestrator not available
        return [
            {
                "name": "standard",
                "pattern": "gut",
                "model_selection_strategy": "weighted",
                "timeout": None,
                "description": "Balanced analysis using all available models",
            },
            {
                "name": "fast",
                "pattern": "gut",
                "model_selection_strategy": "best",
                "timeout": 30.0,
                "description": "Quick analysis optimized for speed",
            },
            {
                "name": "thorough",
                "pattern": "confidence",
                "model_selection_strategy": "all",
                "timeout": None,
                "description": "Comprehensive analysis using all models",
            },
        ]

    def _get_mode_description(self, mode_name: str) -> str:
        """Get a human-readable description for an analysis mode"""
        descriptions = {
            "standard": "Balanced analysis using all available models",
            "fast": "Quick analysis optimized for speed",
            "thorough": "Comprehensive analysis using all models",
            "creative": "Analysis focused on generating novel perspectives",
        }
        return descriptions.get(mode_name, f"Analysis using the {mode_name} approach")


# Create a singleton instance
llm_config_service = LLMConfigService()
