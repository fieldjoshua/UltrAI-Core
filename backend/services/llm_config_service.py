"""
LLM Configuration Service

This service manages the available LLMs, their configurations, and capabilities.
It provides functions to:
- List available LLMs
- Get LLM details
- Check LLM status and availability
- Register and update LLM configurations
"""

import json
import logging
import os
import sys
import time
from typing import Any, Dict, List, Optional

# Robustly add 'src' to the path to ensure correct module resolution.
# This is a targeted fix to bypass the faulty facade import mechanism.
SRC_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

from src.models.enhanced_orchestrator import (
    AnalysisMode,
    EnhancedOrchestrator,
    OrchestratorConfig,
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

            logger.info("Attempting to register models with orchestrator...")

            # Load keys/config from environment
            openai_key = os.getenv("OPENAI_API_KEY")
            # Assuming OPENAI_ORG_ID is read by the OpenAI adapter internally
            anthropic_key = os.getenv("ANTHROPIC_API_KEY")
            google_key = os.getenv("GOOGLE_API_KEY")
            # Assuming OLLAMA_BASE_URL is read by the Ollama adapter internally

            # Check if mock mode is enabled
            use_mock = os.getenv("USE_MOCK", "false").lower() in ("true", "1", "yes")

            # Check if we should automatically register models even without API keys
            auto_register = os.getenv("AUTO_REGISTER_PROVIDERS", "true").lower() in (
                "true",
                "1",
                "yes",
            )

            # Import the adapter classes directly
            from backend.models.llm_adapter import (
                AnthropicAdapter,
                GeminiAdapter,
                OpenAIAdapter,
            )

            # Register OpenAI models
            try:
                # Create OpenAI adapters directly - will use mock mode if no key and USE_MOCK=true
                if openai_key or use_mock or auto_register:
                    # In mock mode or auto-register mode, we'll use a placeholder key if none is provided
                    if not openai_key and (use_mock or auto_register):
                        openai_key = "sk-mock-key-for-openai"
                        logger.info("Using mock OpenAI key for auto-registration")

                    gpt4o_adapter = OpenAIAdapter(openai_key, model="gpt-4o")
                    gpt4turbo_adapter = OpenAIAdapter(
                        openai_key, model="gpt-4-turbo-preview"
                    )

                    # Manually add to orchestrator.model_registry
                    if hasattr(self.orchestrator, "model_registry"):
                        self.orchestrator.model_registry["gpt4o"] = {
                            "provider": "openai",
                            "model": "gpt-4o",
                            "weight": 1.0,
                            "capabilities": gpt4o_adapter.get_capabilities(),
                            "tags": ["premium", "reasoning"],
                            "available": bool(openai_key)
                            or use_mock,  # Only truly available with key or in mock mode
                            "status": (
                                "ready"
                                if (bool(openai_key) or use_mock)
                                else "needs_key"
                            ),
                        }
                        self.orchestrator.model_registry["gpt4turbo"] = {
                            "provider": "openai",
                            "model": "gpt-4-turbo-preview",
                            "weight": 0.9,
                            "capabilities": gpt4turbo_adapter.get_capabilities(),
                            "tags": ["premium", "reasoning"],
                            "available": bool(openai_key)
                            or use_mock,  # Only truly available with key or in mock mode
                            "status": (
                                "ready"
                                if (bool(openai_key) or use_mock)
                                else "needs_key"
                            ),
                        }
                        logger.info(
                            "Registered OpenAI models directly to model_registry"
                        )
                    else:
                        logger.warning("No model_registry attribute in orchestrator")
                else:
                    logger.warning(
                        "OPENAI_API_KEY not found and auto-register disabled, skipping OpenAI registration."
                    )
            except Exception as e:
                logger.error(f"Failed to register OpenAI models directly: {e}")

            # Register Anthropic models
            try:
                # Create Anthropic adapters - will use mock mode if no key and USE_MOCK=true
                if anthropic_key or use_mock or auto_register:
                    # In mock mode or auto-register mode, we'll use a placeholder key if none is provided
                    if not anthropic_key and (use_mock or auto_register):
                        anthropic_key = "sk-ant-mock-key-for-anthropic"
                        logger.info("Using mock Anthropic key for auto-registration")

                    claude3opus_adapter = AnthropicAdapter(
                        anthropic_key, model="claude-3-opus-20240229"
                    )
                    claude3sonnet_adapter = AnthropicAdapter(
                        anthropic_key, model="claude-3-sonnet-20240229"
                    )

                    # Manually add to orchestrator.model_registry
                    if hasattr(self.orchestrator, "model_registry"):
                        self.orchestrator.model_registry["claude3opus"] = {
                            "provider": "anthropic",
                            "model": "claude-3-opus-20240229",
                            "weight": 1.0,
                            "capabilities": claude3opus_adapter.get_capabilities(),
                            "tags": ["premium", "reasoning"],
                            "available": bool(anthropic_key)
                            or use_mock,  # Only truly available with key or in mock mode
                            "status": (
                                "ready"
                                if (bool(anthropic_key) or use_mock)
                                else "needs_key"
                            ),
                        }
                        self.orchestrator.model_registry["claude3sonnet"] = {
                            "provider": "anthropic",
                            "model": "claude-3-sonnet-20240229",
                            "weight": 0.9,
                            "capabilities": claude3sonnet_adapter.get_capabilities(),
                            "tags": ["premium", "reasoning"],
                            "available": bool(anthropic_key)
                            or use_mock,  # Only truly available with key or in mock mode
                            "status": (
                                "ready"
                                if (bool(anthropic_key) or use_mock)
                                else "needs_key"
                            ),
                        }
                        logger.info(
                            "Registered Anthropic models directly to model_registry"
                        )
                    else:
                        logger.warning("No model_registry attribute in orchestrator")
                else:
                    logger.warning(
                        "ANTHROPIC_API_KEY not found and auto-register disabled, skipping Anthropic registration."
                    )
            except Exception as e:
                logger.error(f"Failed to register Anthropic models directly: {e}")

            # Register Google Gemini models
            try:
                # Create Gemini adapters - will use mock mode if no key and USE_MOCK=true
                if google_key or use_mock or auto_register:
                    # In mock mode or auto-register mode, we'll use a placeholder key if none is provided
                    if not google_key and (use_mock or auto_register):
                        google_key = "AIza-mock-key-for-google"
                        logger.info("Using mock Google key for auto-registration")

                    gemini15_flash_adapter = GeminiAdapter(
                        google_key, model="gemini-1.5-flash-latest"
                    )
                    gemini15_pro_adapter = GeminiAdapter(
                        google_key, model="gemini-1.5-pro-latest"
                    )

                    # Manually add to orchestrator.model_registry
                    if hasattr(self.orchestrator, "model_registry"):
                        self.orchestrator.model_registry["gemini15flash"] = {
                            "provider": "gemini",
                            "model": "gemini-1.5-flash-latest",
                            "weight": 0.8,
                            "capabilities": gemini15_flash_adapter.get_capabilities(),
                            "tags": ["fast", "reasoning"],
                            "available": bool(google_key)
                            or use_mock,  # Only truly available with key or in mock mode
                            "status": (
                                "ready"
                                if (bool(google_key) or use_mock)
                                else "needs_key"
                            ),
                        }
                        self.orchestrator.model_registry["gemini15pro"] = {
                            "provider": "gemini",
                            "model": "gemini-1.5-pro-latest",
                            "weight": 0.9,
                            "capabilities": gemini15_pro_adapter.get_capabilities(),
                            "tags": ["premium", "reasoning"],
                            "available": bool(google_key)
                            or use_mock,  # Only truly available with key or in mock mode
                            "status": (
                                "ready"
                                if (bool(google_key) or use_mock)
                                else "needs_key"
                            ),
                        }
                        logger.info(
                            "Registered Google (Gemini) models directly to model_registry"
                        )
                    else:
                        logger.warning("No model_registry attribute in orchestrator")
                else:
                    logger.warning(
                        "GOOGLE_API_KEY not found and auto-register disabled, skipping Google registration."
                    )
            except Exception as e:
                logger.error(f"Failed to register Google (Gemini) models directly: {e}")

            # Register Docker Model Runner models if enabled
            use_model_runner = os.getenv("USE_MODEL_RUNNER", "false").lower() in (
                "true",
                "1",
                "yes",
            )
            enable_model_runner = os.getenv("ENABLE_MODEL_RUNNER", "false").lower() in (
                "true",
                "1",
                "yes",
            )

            if use_model_runner or enable_model_runner:
                try:
                    # Check which adapter to use (CLI or API)
                    model_runner_type = os.getenv("MODEL_RUNNER_TYPE", "cli").lower()

                    if model_runner_type == "cli":
                        # Import the CLI adapter
                        from backend.models.docker_modelrunner_cli_adapter import (
                            DockerModelRunnerCLIAdapter,
                        )

                        # Get available models
                        models = []
                        try:
                            # Use synchronous subprocess to get models
                            import subprocess

                            result = subprocess.run(
                                ["docker", "model", "list"],
                                capture_output=True,
                                text=True,
                                check=False,
                            )
                            if result.returncode == 0:
                                # Parse output - skip header line
                                lines = result.stdout.strip().split("\n")
                                if len(lines) > 1:
                                    for line in lines[1:]:  # Skip header
                                        parts = line.split()
                                        if parts:
                                            models.append(
                                                parts[0]
                                            )  # First column is model name
                                logger.info(
                                    f"Found {len(models)} Docker Model Runner models via CLI"
                                )
                        except Exception as e:
                            logger.error(
                                f"Failed to get Docker Model Runner models via CLI: {e}"
                            )

                        # Register models
                        if models and hasattr(self.orchestrator, "model_registry"):
                            for model in models:
                                model_id = f"local-{model}"
                                self.orchestrator.model_registry[model_id] = {
                                    "provider": "docker_modelrunner",
                                    "model": model,
                                    "weight": 0.8,
                                    "capabilities": {
                                        "supports_streaming": True,
                                        "max_tokens": 4096,
                                        "name": model,
                                    },
                                    "tags": ["local", "offline"],
                                    "available": True,
                                    "status": "ready",
                                }
                            logger.info(
                                f"Registered {len(models)} Docker Model Runner models via CLI"
                            )
                        else:
                            # Add default model as fallback
                            default_model = os.getenv("DEFAULT_MODEL", "ai/smollm2")
                            model_id = f"local-{default_model}"
                            if hasattr(self.orchestrator, "model_registry"):
                                self.orchestrator.model_registry[model_id] = {
                                    "provider": "docker_modelrunner",
                                    "model": default_model,
                                    "weight": 0.8,
                                    "capabilities": {
                                        "supports_streaming": True,
                                        "max_tokens": 4096,
                                        "name": default_model,
                                    },
                                    "tags": ["local", "offline"],
                                    "available": True,
                                    "status": "ready",
                                }
                                logger.info(
                                    f"Registered default Docker Model Runner model {default_model} via CLI"
                                )
                    else:
                        # Import the API adapter
                        from backend.models.docker_modelrunner_adapter import (
                            DockerModelRunnerAdapter,
                            get_available_models,
                        )

                        # Get default model from environment
                        default_model = os.getenv("DEFAULT_MODEL", "phi3:mini")

                        # Create adapter for the default model
                        modelrunner_adapter = DockerModelRunnerAdapter(
                            model=default_model
                        )

                        # Manually add to orchestrator.model_registry
                        if hasattr(self.orchestrator, "model_registry"):
                            model_id = f"local-{default_model}"
                            self.orchestrator.model_registry[model_id] = {
                                "provider": "docker_modelrunner",
                                "model": default_model,
                                "weight": 0.8,
                                "capabilities": modelrunner_adapter.get_capabilities(),
                                "tags": ["local", "offline"],
                                "available": True,
                                "status": "ready",
                            }
                            logger.info(
                                f"Registered Docker Model Runner model {default_model} directly to model_registry"
                            )

                            # Try to register additional models asynchronously
                            async def register_additional_models():
                                try:
                                    # Get available models from Docker Model Runner
                                    models = await get_available_models()
                                    for model in models:
                                        if model != default_model and hasattr(
                                            self.orchestrator, "model_registry"
                                        ):
                                            model_adapter = DockerModelRunnerAdapter(
                                                model=model
                                            )
                                            model_id = f"local-{model}"
                                            self.orchestrator.model_registry[
                                                model_id
                                            ] = {
                                                "provider": "docker_modelrunner",
                                                "model": model,
                                                "weight": 0.8,
                                                "capabilities": model_adapter.get_capabilities(),
                                                "tags": ["local", "offline"],
                                                "available": True,
                                                "status": "ready",
                                            }
                                    logger.info(
                                        f"Registered {len(models)} Docker Model Runner models"
                                    )
                                except Exception as e:
                                    logger.error(
                                        f"Failed to register additional Docker Model Runner models: {e}"
                                    )

                            # Start asynchronous task to register models
                            import asyncio

                            try:
                                loop = asyncio.get_event_loop()
                                if loop.is_running():
                                    asyncio.create_task(register_additional_models())
                                else:
                                    # If no loop is running, don't attempt to register additional models
                                    pass
                            except Exception as e:
                                logger.error(
                                    f"Failed to start async task for model registration: {e}"
                                )
                        else:
                            logger.warning(
                                "No model_registry attribute in orchestrator"
                            )
                except Exception as e:
                    logger.error(f"Failed to register Docker Model Runner models: {e}")
            else:
                logger.info(
                    "Neither USE_MODEL_RUNNER nor ENABLE_MODEL_RUNNER is set to true, skipping Docker Model Runner registration."
                )

            # REMOVED Ollama registration attempt as no adapter exists
            # # Register Ollama models
            # try:
            #     # Pass empty api_key, assuming adapter reads OLLAMA_BASE_URL from env
            #     self.orchestrator.register_model(
            #         name="llama3", provider="ollama", model="llama3:latest", api_key="" # Pass dummy key
            #     )
            #     logger.info("Registered Ollama models (adapter should read OLLAMA_BASE_URL from env)")
            # except Exception as e:
            #      logger.error(f"Failed to register Ollama models: {e}")

        except Exception as e:
            logger.error(
                f"Failed to initialize orchestrator or register models: {str(e)}"
            )
            self.orchestrator = None

    def refresh_models_if_needed(self):
        """Refresh model information if cache is stale"""
        current_time = time.time()

        # --- MODIFIED REFRESH LOGIC --- #
        # Don't overwrite if orchestrator has models; just update status/availability if needed
        # This part might need more sophisticated logic later to actually check model health
        if (
            current_time - self._last_update < self._refresh_interval
            and self._available_models
        ):
            return

        if self.orchestrator and self.orchestrator.model_registry:
            self._available_models = {}
            for name, registration in self.orchestrator.model_registry.items():
                # Check if registration is a dict or an object
                if isinstance(registration, dict):
                    # If it's a dict, use it directly
                    self._available_models[name] = {
                        "name": name,
                        "provider": registration.get("provider", "unknown"),
                        "model": registration.get("model", name),
                        "weight": registration.get("weight", 1.0),
                        "capabilities": registration.get("capabilities", {}),
                        "tags": registration.get("tags", []),
                        "available": True,  # Assume available if registered for now
                        "status": "ready",  # Assume ready if registered for now
                    }
                else:
                    # Otherwise, assume it's an object with attributes
                    self._available_models[name] = {
                        "name": name,
                        "provider": getattr(registration, "provider", "unknown"),
                        "model": getattr(registration, "model", name),
                        "weight": getattr(registration, "weight", 1.0),
                        "capabilities": getattr(registration, "capabilities", {}),
                        "tags": getattr(registration, "tags", []),
                        "available": True,  # Assume available if registered for now
                        "status": "ready",  # Assume ready if registered for now
                    }
            self._last_update = current_time
            logger.info(
                f"Refreshed model information from orchestrator registry. Found {len(self._available_models)} models."
            )
        elif not self.orchestrator:
            # Fallback to default if orchestrator failed initialization
            # (Keep existing fallback logic)
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
        # --- END MODIFIED REFRESH LOGIC --- #

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

    def get_patterns(self) -> List[str]:
        """
        Get all available analysis patterns (alias for backward compatibility)

        Returns:
            List of available pattern names
        """
        return self.get_available_analysis_patterns()

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

    def get_modes(self) -> List[Dict[str, Any]]:
        """
        Get all available analysis modes (alias for backward compatibility)

        Returns:
            List of available analysis modes with details
        """
        return self.get_available_analysis_modes()

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
