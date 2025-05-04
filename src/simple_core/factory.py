"""
Factory module for Simple Core.

This module provides factory functions for creating orchestrator instances
with configured adapters.
"""

import logging
import os
import shutil
from typing import Dict, List, Optional, Tuple, Union

from src.simple_core.adapter import (
    Adapter,
    AnthropicAdapter,
    GeminiAdapter,
    LlamaAdapter,
    OpenAIAdapter,
)

# Import extended adapters if available
try:
    from src.simple_core.adapter_extensions import DeepseekAdapter, OllamaAdapter

    EXTENDED_ADAPTERS_AVAILABLE = True
except ImportError:
    DeepseekAdapter = None
    OllamaAdapter = None
    EXTENDED_ADAPTERS_AVAILABLE = False
from src.simple_core.cache_service import CacheService
from src.simple_core.config import (
    AnalysisConfig,
    Config,
    ModelDefinition,
    RequestConfig,
)
from src.simple_core.config.factory_helpers import create_analysis_registry
from src.simple_core.enhanced_orchestrator import EnhancedOrchestrator
from src.simple_core.modular_orchestrator import ModularOrchestrator
from src.simple_core.orchestrator import Orchestrator
from src.simple_core.prompt_templates import PromptTemplates
from src.simple_core.quality_metrics import QualityMetrics

logger = logging.getLogger("simple_core.factory")


def create_adapter(model_def: ModelDefinition) -> Optional[Adapter]:
    """
    Create an appropriate adapter for a model definition.

    Args:
        model_def: The model definition

    Returns:
        An adapter instance or None if provider not supported
    """
    provider = model_def.provider.lower()

    try:
        if provider == "openai":
            return OpenAIAdapter(model_def)

        elif provider == "anthropic":
            return AnthropicAdapter(model_def)

        elif provider == "gemini" or provider == "google":
            return GeminiAdapter(model_def)

        elif provider == "llama":
            return LlamaAdapter(model_def)

        # Extended adapters if available
        elif provider == "deepseek" and EXTENDED_ADAPTERS_AVAILABLE and DeepseekAdapter:
            return DeepseekAdapter(model_def)

        elif provider == "ollama" and EXTENDED_ADAPTERS_AVAILABLE and OllamaAdapter:
            return OllamaAdapter(model_def)

        else:
            logger.warning(f"Unsupported provider: {provider}")
            return None

    except Exception as e:
        logger.error(f"Failed to create adapter for {provider}: {str(e)}")
        return None


def create_orchestrator(
    config: Config,
    enhanced: bool = False,
    modular: bool = False,
    analysis_config: Optional[AnalysisConfig] = None,
) -> Union[Orchestrator, EnhancedOrchestrator, ModularOrchestrator]:
    """
    Create an orchestrator with configured adapters.

    Args:
        config: The orchestrator configuration
        enhanced: Whether to create an enhanced orchestrator with multi-stage processing
        modular: Whether to create a modular orchestrator with pluggable analysis
        analysis_config: Configuration for analysis modules (for modular orchestrator)

    Returns:
        An initialized orchestrator instance
    """
    # Create model_def to adapter mapping
    model_adapter_pairs = []

    # Create adapters for each model
    for model_def in config.models:
        adapter = create_adapter(model_def)
        if adapter:
            model_adapter_pairs.append((model_def, adapter))
            logger.info(f"Created adapter for {model_def.name} ({model_def.provider})")
        else:
            logger.warning(f"Failed to create adapter for {model_def.name}")

    if not model_adapter_pairs:
        raise ValueError(
            "No valid model adapters created, cannot initialize orchestrator"
        )

    # Sort model_adapter_pairs by priority
    model_adapter_pairs.sort(key=lambda x: x[0].priority)

    # Create support services
    prompt_templates = PromptTemplates()
    quality_metrics = QualityMetrics()
    cache_service = CacheService()

    # Create the appropriate orchestrator type
    if modular:
        # Use the analysis config or create default
        analysis_config = analysis_config or AnalysisConfig.create_default()

        # Create the modular orchestrator
        orchestrator = ModularOrchestrator(
            models=model_adapter_pairs,
            config=config,
            analysis_config=analysis_config,
            prompt_templates=prompt_templates,
            quality_metrics=quality_metrics,
            cache_service=cache_service,
        )
        logger.info(
            f"Created modular orchestrator with {len(model_adapter_pairs)} adapters"
        )

    elif enhanced:
        # Create the enhanced orchestrator
        orchestrator = EnhancedOrchestrator(
            models=model_adapter_pairs,
            config=config,
            prompt_templates=prompt_templates,
            quality_metrics=quality_metrics,
            cache_service=cache_service,
        )
        logger.info(
            f"Created enhanced orchestrator with {len(model_adapter_pairs)} adapters"
        )

    else:
        # Convert to dictionary format for basic orchestrator
        adapters = {
            model_def.name: adapter for model_def, adapter in model_adapter_pairs
        }

        # Create the basic orchestrator
        orchestrator = Orchestrator(config, adapters)
        logger.info(f"Created basic orchestrator with {len(adapters)} adapters")

    return orchestrator


def create_from_env(
    enhanced: bool = False, modular: bool = False, analysis_type: str = "comparative"
) -> Optional[Union[Orchestrator, EnhancedOrchestrator, ModularOrchestrator]]:
    """
    Create an orchestrator from environment variables.

    This is a convenience function for quickly setting up an orchestrator
    using available API keys in the environment.

    Args:
        enhanced: Whether to create an enhanced orchestrator with multi-stage processing
        modular: Whether to create a modular orchestrator with pluggable analysis
        analysis_type: Type of analysis to use with modular orchestrator

    Returns:
        An initialized orchestrator or None if no providers available
    """
    models = []

    # Check for OpenAI
    if os.environ.get("OPENAI_API_KEY"):
        models.append(
            ModelDefinition(
                name="openai-gpt4o",
                provider="openai",
                priority=1,
                options={"model_id": "gpt-4o"},
            )
        )
        logger.info("Found OpenAI API key, adding GPT-4o model")

    # Check for Anthropic
    if os.environ.get("ANTHROPIC_API_KEY"):
        models.append(
            ModelDefinition(
                name="anthropic-claude",
                provider="anthropic",
                priority=2,
                options={"model_id": "claude-3-opus-20240229"},
            )
        )
        logger.info("Found Anthropic API key, adding Claude model")

    # Check for Google/Gemini
    if os.environ.get("GOOGLE_API_KEY"):
        models.append(
            ModelDefinition(
                name="google-gemini",
                provider="gemini",
                priority=3,
                options={"model_id": "gemini-1.5-pro-latest"},
            )
        )
        logger.info("Found Google API key, adding Gemini model")

    # Check for Deepseek if adapter available
    if (
        EXTENDED_ADAPTERS_AVAILABLE
        and DeepseekAdapter
        and os.environ.get("DEEPSEEK_API_KEY")
    ):
        models.append(
            ModelDefinition(
                name="deepseek-chat",
                provider="deepseek",
                priority=4,
                options={"model_id": "deepseek-chat"},
            )
        )
        logger.info("Found Deepseek API key, adding Deepseek Chat model")

    # Check for Ollama if adapter available and service running
    if EXTENDED_ADAPTERS_AVAILABLE and OllamaAdapter and os.environ.get("OLLAMA_MODEL"):
        # We don't need to check if Ollama is running here; the adapter will do that
        ollama_model = os.environ.get("OLLAMA_MODEL", "llama3")
        models.append(
            ModelDefinition(
                name=f"ollama-{ollama_model}",
                provider="ollama",
                priority=5,
                options={"model_id": ollama_model},
            )
        )
        logger.info(f"Found Ollama configuration, adding model {ollama_model}")

    # Check for Llama local models
    llama_model_path = os.environ.get("LLAMA_MODEL_PATH")
    llama_command = os.environ.get("LLAMA_COMMAND", "llama")

    # Check if the llama command is available
    if llama_model_path and shutil.which(llama_command):
        models.append(
            ModelDefinition(
                name="local-llama",
                provider="llama",
                priority=6,
                options={
                    "model_path": llama_model_path,
                    "command": llama_command,
                    "extra_args": [],
                },
            )
        )
        logger.info(f"Found Llama model at {llama_model_path}, adding Llama model")

    if not models:
        logger.warning(
            "No API keys or local models found in environment, cannot create orchestrator"
        )
        return None

    # Create config and orchestrator
    config = Config(models=models, parallel=True)

    # Create analysis config if needed
    analysis_config = None
    if modular:
        analysis_config = AnalysisConfig(analysis_type=analysis_type, enabled=True)

    # Create the appropriate type of orchestrator
    if modular:
        log_type = "modular"
    elif enhanced:
        log_type = "enhanced"
    else:
        log_type = "basic"

    logger.info(f"Creating {log_type} orchestrator from environment")

    return create_orchestrator(
        config, enhanced=enhanced, modular=modular, analysis_config=analysis_config
    )
