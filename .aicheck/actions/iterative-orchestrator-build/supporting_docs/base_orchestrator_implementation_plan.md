# BaseOrchestrator Implementation Plan

This document outlines the detailed implementation plan for the `BaseOrchestrator` class, which will serve as the foundation for the Iterative Orchestrator Build. The `BaseOrchestrator` will provide core functionality for handling multiple LLM requests, synthesizing responses, and managing errors.

## Implementation Steps

### 1. Set Up Directory Structure

```bash
# Create necessary directories
mkdir -p /Users/joshuafield/Documents/Ultra/src/orchestration
mkdir -p /Users/joshuafield/Documents/Ultra/src/adapters
mkdir -p /Users/joshuafield/Documents/Ultra/src/services
mkdir -p /Users/joshuafield/Documents/Ultra/src/cli
mkdir -p /Users/joshuafield/Documents/Ultra/tests/unit/orchestration
mkdir -p /Users/joshuafield/Documents/Ultra/tests/unit/adapters
```

### 2. Create Configuration Classes

File: `/Users/joshuafield/Documents/Ultra/src/orchestration/config.py`

```python
"""
Orchestrator Configuration Module

This module provides configuration classes for the orchestration system.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any


@dataclass
class ModelConfig:
    """
    Configuration for an LLM model.

    Attributes:
        provider: The provider name (openai, anthropic, etc.)
        model: The specific model name
        api_key: API key for the provider
        weight: Weight for prioritizing model responses
        parameters: Additional parameters for the model
    """

    provider: str
    model: str
    api_key: Optional[str] = None
    weight: float = 1.0
    parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OrchestratorConfig:
    """
    Configuration for the orchestrator.

    Attributes:
        models: Dictionary of model configurations
        default_models: List of default models to use
        default_primary_model: Default model for synthesis
        cache_enabled: Whether to use caching
        mock_mode: Whether to use mock mode
        max_retries: Maximum number of retries for failed requests
        retry_delay: Base delay in seconds for retry backoff
    """

    models: Dict[str, ModelConfig] = field(default_factory=dict)
    default_models: List[str] = field(default_factory=list)
    default_primary_model: Optional[str] = None
    cache_enabled: bool = True
    mock_mode: bool = False
    max_retries: int = 3
    retry_delay: float = 0.5

    def __post_init__(self):
        """Initialize default_models and default_primary_model if not provided."""
        if not self.default_models and self.models:
            # Use all models by default, sorted by weight
            self.default_models = sorted(
                self.models.keys(),
                key=lambda m: self.models[m].weight,
                reverse=True
            )

        if not self.default_primary_model and self.default_models:
            # Use highest-weighted model as primary by default
            self.default_primary_model = self.default_models[0]
```

### 3. Implement Core Adapter Factory

File: `/Users/joshuafield/Documents/Ultra/src/adapters/factory.py`

```python
"""
Adapter Factory Module

This module provides factory functions for creating LLM adapters.
"""

import logging
import os
from typing import Dict, Any, Optional

# Initially import from the existing location
# Later will be replaced with imports from the new adapter modules
from src.models.llm_adapter import (
    OpenAIAdapter,
    AnthropicAdapter,
    GeminiAdapter,
    MistralAdapter,
    CohereAdapter
)

logger = logging.getLogger(__name__)


def create_adapter(
    provider: str,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    **options
) -> Any:
    """
    Create an LLM adapter for the specified provider.

    Args:
        provider: The LLM provider ("openai", "anthropic", etc.)
        api_key: The API key
        model: Specific model to use
        **options: Additional provider-specific options

    Returns:
        An instance of the appropriate LLM adapter

    Raises:
        ValueError: If the provider is not supported
    """
    # Check for mock mode
    use_mock = os.environ.get("USE_MOCK", "false").lower() in ("true", "1", "yes")

    # Handle missing API key in mock mode
    if not api_key and use_mock:
        if provider.lower() == "openai":
            api_key = "sk-mock-key-for-openai"
        elif provider.lower() == "anthropic":
            api_key = "sk-ant-mock-key-for-anthropic"
        elif provider.lower() == "gemini":
            api_key = "AIza-mock-key-for-google"
        else:
            api_key = f"mock-key-for-{provider.lower()}"

        logger.info(f"Using mock API key for {provider} in mock mode")

    # Create the appropriate adapter
    if provider.lower() == "openai":
        return OpenAIAdapter(api_key, model=model or "gpt-4", **options)
    elif provider.lower() == "anthropic":
        return AnthropicAdapter(api_key, model=model or "claude-3-opus-20240229", **options)
    elif provider.lower() == "gemini":
        return GeminiAdapter(api_key, model=model or "gemini-pro", **options)
    elif provider.lower() == "mistral":
        return MistralAdapter(api_key, model=model or "mistral-large-latest", **options)
    elif provider.lower() == "cohere":
        return CohereAdapter(api_key, model=model or "command", **options)
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")
```

### 4. Implement BaseOrchestrator

File: `/Users/joshuafield/Documents/Ultra/src/orchestration/base.py`

```python
"""
Base Orchestrator Module

This module provides the BaseOrchestrator class for coordinating LLM requests.
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Tuple

from src.orchestration.config import OrchestratorConfig, ModelConfig
from src.adapters.factory import create_adapter

logger = logging.getLogger(__name__)


class BaseOrchestrator:
    """
    Core orchestration system for managing LLM requests and responses.

    This class provides the foundational functionality for:
    - Sending prompts to multiple LLMs in parallel
    - Error handling and retries
    - Basic response synthesis
    - Mock mode support
    """

    def __init__(self, config: Optional[OrchestratorConfig] = None):
        """
        Initialize the orchestrator with configuration.

        Args:
            config: Optional orchestrator configuration
        """
        self.config = config or OrchestratorConfig()
        self.adapters = {}
        self._initialize_adapters()

    def _initialize_adapters(self) -> None:
        """Initialize LLM adapters from configuration."""
        for model_name, model_config in self.config.models.items():
            try:
                adapter = create_adapter(
                    provider=model_config.provider,
                    api_key=model_config.api_key,
                    model=model_config.model,
                    **model_config.parameters
                )
                self.adapters[model_name] = adapter
                logger.info(f"Initialized adapter for {model_name} ({model_config.provider})")
            except Exception as e:
                logger.error(f"Failed to initialize adapter for {model_name}: {e}")

    def register_model(
        self,
        name: str,
        provider: str,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        weight: float = 1.0,
        parameters: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Register a new model with the orchestrator.

        Args:
            name: Unique identifier for the model
            provider: LLM provider (openai, anthropic, etc.)
            model: Specific model name
            api_key: API key for the provider
            weight: Weight for prioritizing model responses
            parameters: Additional parameters for the model
        """
        # Create model configuration
        model_config = ModelConfig(
            provider=provider,
            model=model or name,
            api_key=api_key,
            weight=weight,
            parameters=parameters or {}
        )

        # Add to configuration
        self.config.models[name] = model_config

        # Initialize adapter
        try:
            adapter = create_adapter(
                provider=provider,
                api_key=api_key,
                model=model or name,
                **(parameters or {})
            )
            self.adapters[name] = adapter
            logger.info(f"Registered model {name} ({provider})")
        except Exception as e:
            logger.error(f"Failed to register model {name}: {e}")

    async def check_availability(self) -> Dict[str, bool]:
        """
        Check which models are available and responsive.

        Returns:
            Dict[str, bool]: Mapping of model names to availability status
        """
        availability = {}

        for model_name, adapter in self.adapters.items():
            try:
                if hasattr(adapter, 'check_availability'):
                    # Use adapter's availability check if available
                    available = await adapter.check_availability()
                else:
                    # Simple test prompt
                    test_prompt = "Hello, are you available? Please respond with Yes or No."
                    response = await self._send_to_llm(model_name, test_prompt)
                    available = response is not None

                availability[model_name] = available
                logger.info(f"Model {model_name} availability: {available}")
            except Exception as e:
                logger.error(f"Error checking availability for {model_name}: {e}")
                availability[model_name] = False

        return availability

    async def process(
        self,
        prompt: str,
        models: Optional[List[str]] = None,
        primary_model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a prompt using multiple LLMs and synthesize results.

        Args:
            prompt: The prompt to analyze
            models: Optional list of model names to use
            primary_model: Optional model to use for synthesis

        Returns:
            Dict containing results from all models and synthesized response
        """
        start_time = time.time()

        # Determine which models to use
        models_to_use = models or self.config.default_models
        valid_models = [m for m in models_to_use if m in self.adapters]

        if not valid_models:
            return {
                "status": "error",
                "error": "No valid models available for processing",
                "elapsed_time": time.time() - start_time
            }

        # Determine primary model for synthesis
        if primary_model and primary_model in valid_models:
            synthesis_model = primary_model
        else:
            synthesis_model = self.config.default_primary_model
            if synthesis_model not in valid_models:
                synthesis_model = valid_models[0]

        # Process with all models in parallel
        tasks = []
        for model_name in valid_models:
            tasks.append(self._send_to_llm(model_name, prompt))

        # Gather results
        responses = {}
        errors = {}

        results = await asyncio.gather(*tasks, return_exceptions=True)
        for model_name, result in zip(valid_models, results):
            if isinstance(result, Exception):
                logger.error(f"Error from {model_name}: {result}")
                errors[model_name] = str(result)
            else:
                responses[model_name] = result

        # If no successful responses, return error
        if not responses:
            return {
                "status": "error",
                "error": "All models failed to process",
                "model_errors": errors,
                "elapsed_time": time.time() - start_time
            }

        # Synthesize responses
        synthesis = await self._synthesize_responses(prompt, responses, synthesis_model)

        # Return final result
        return {
            "status": "success",
            "model_responses": responses,
            "ultra_response": synthesis,
            "errors": errors,
            "ultra_model": synthesis_model,
            "models_used": list(responses.keys()),
            "elapsed_time": time.time() - start_time
        }

    async def _send_to_llm(self, model_name: str, prompt: str) -> Dict[str, Any]:
        """
        Send prompt to a specific LLM and handle errors.

        Args:
            model_name: Name of the model to use
            prompt: The prompt to send

        Returns:
            Dict containing the response and metadata

        Raises:
            Exception: If the request fails after retries
        """
        adapter = self.adapters.get(model_name)
        if not adapter:
            raise ValueError(f"Model {model_name} not found")

        max_retries = self.config.max_retries
        retry_delay = self.config.retry_delay

        for retry in range(max_retries):
            try:
                start_time = time.time()

                # Generate response
                response = await adapter.generate(prompt)

                # Calculate response time
                elapsed_time = time.time() - start_time

                return {
                    "content": response,
                    "model": model_name,
                    "tokens": len(response.split()) // 4,  # Rough estimate
                    "processing_time": elapsed_time
                }
            except Exception as e:
                logger.warning(f"Error from {model_name} (attempt {retry+1}/{max_retries}): {e}")

                # Retry with exponential backoff
                if retry < max_retries - 1:
                    delay = retry_delay * (2 ** retry)
                    logger.info(f"Retrying {model_name} in {delay:.2f}s...")
                    await asyncio.sleep(delay)
                else:
                    # Last retry failed, raise exception
                    raise

    async def _synthesize_responses(
        self,
        prompt: str,
        responses: Dict[str, Dict[str, Any]],
        primary_model: str
    ) -> str:
        """
        Combine multiple LLM responses into a single result.

        Args:
            prompt: The original prompt
            responses: Dict of model responses
            primary_model: Model to use for synthesis

        Returns:
            Synthesized response
        """
        # For single response, return it directly
        if len(responses) == 1:
            return next(iter(responses.values()))["content"]

        # Create synthesis prompt
        synthesis_prompt = self._create_synthesis_prompt(prompt, responses)

        # Use primary model for synthesis
        try:
            synthesis_response = await self._send_to_llm(primary_model, synthesis_prompt)
            return synthesis_response["content"]
        except Exception as e:
            logger.error(f"Synthesis failed with {primary_model}: {e}")

            # Fall back to the longest response
            longest_response = max(
                responses.values(),
                key=lambda r: len(r["content"])
            )
            return f"[Synthesis failed. Using response from {longest_response['model']}]\n\n{longest_response['content']}"

    def _create_synthesis_prompt(
        self,
        original_prompt: str,
        responses: Dict[str, Dict[str, Any]]
    ) -> str:
        """
        Create a prompt for synthesizing multiple responses.

        Args:
            original_prompt: The original prompt
            responses: Dict of model responses

        Returns:
            Synthesis prompt
        """
        synthesis_prompt = f"""
        You are an expert at synthesizing responses from multiple AI models.

        The original question/prompt was:
        "{original_prompt}"

        The following AI models have provided responses:

        """

        for model_name, response in responses.items():
            response_text = response.get("content", "")
            synthesis_prompt += f"""
            --- {model_name} response ---
            {response_text}
            -----------------------------
            """

        synthesis_prompt += """
        Synthesize these responses into a single, comprehensive answer.
        Focus on the most valuable insights from each model while avoiding
        repetition. Ensure the final response is well-structured and
        provides a complete answer to the original prompt.
        """

        return synthesis_prompt
```

### 5. Create Simple CLI Wrapper

File: `/Users/joshuafield/Documents/Ultra/src/cli/analyzer.py`

```python
#!/usr/bin/env python
"""
Simple Ultra Analyzer CLI

This module provides a command-line interface for the BaseOrchestrator.
"""

import argparse
import asyncio
import json
import logging
import os
import sys
from typing import Dict, List, Any, Optional

from src.orchestration.config import OrchestratorConfig, ModelConfig
from src.orchestration.base import BaseOrchestrator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("ultra_analyzer")


def load_api_keys() -> Dict[str, str]:
    """Load API keys from environment variables."""
    return {
        "openai": os.environ.get("OPENAI_API_KEY", ""),
        "anthropic": os.environ.get("ANTHROPIC_API_KEY", ""),
        "google": os.environ.get("GOOGLE_API_KEY", ""),
        "mistral": os.environ.get("MISTRAL_API_KEY", ""),
        "cohere": os.environ.get("COHERE_API_KEY", ""),
    }


def create_config_from_env(use_mock: bool = False) -> OrchestratorConfig:
    """Create orchestrator configuration from environment variables."""
    # Load API keys
    api_keys = load_api_keys()

    # Create configuration
    config = OrchestratorConfig(mock_mode=use_mock)

    # Add models based on available API keys or mock mode
    if api_keys.get("openai") or use_mock:
        config.models["gpt4o"] = ModelConfig(
            provider="openai",
            model="gpt-4o",
            api_key=api_keys.get("openai"),
            weight=1.0
        )
        config.models["gpt4turbo"] = ModelConfig(
            provider="openai",
            model="gpt-4-turbo",
            api_key=api_keys.get("openai"),
            weight=0.9
        )

    if api_keys.get("anthropic") or use_mock:
        config.models["claude3opus"] = ModelConfig(
            provider="anthropic",
            model="claude-3-opus-20240229",
            api_key=api_keys.get("anthropic"),
            weight=1.0
        )
        config.models["claude3sonnet"] = ModelConfig(
            provider="anthropic",
            model="claude-3-sonnet-20240229",
            api_key=api_keys.get("anthropic"),
            weight=0.9
        )

    if api_keys.get("google") or use_mock:
        config.models["gemini15"] = ModelConfig(
            provider="gemini",
            model="gemini-1.5-pro-latest",
            api_key=api_keys.get("google"),
            weight=0.9
        )

    if api_keys.get("mistral") or use_mock:
        config.models["mistral"] = ModelConfig(
            provider="mistral",
            model="mistral-large-latest",
            api_key=api_keys.get("mistral"),
            weight=0.8
        )

    # Update default models and primary model
    if config.models:
        config.default_models = sorted(
            config.models.keys(),
            key=lambda m: config.models[m].weight,
            reverse=True
        )
        config.default_primary_model = config.default_models[0]

    return config


async def check_models_availability(orchestrator: BaseOrchestrator) -> None:
    """
    Check which models are available and display results.

    Args:
        orchestrator: BaseOrchestrator instance
    """
    print("Checking LLM availability...")

    model_status = await orchestrator.check_availability()

    for model_name, available in model_status.items():
        model_config = orchestrator.config.models.get(model_name)
        provider = model_config.provider if model_config else "unknown"
        status = "✓" if available else "✗"
        availability = "Available" if available else "Unavailable"
        print(f"{status} {model_name} ({provider}) - {availability}")

    # Print a summary
    available_count = sum(1 for status in model_status.values() if status)
    total_count = len(model_status)

    print()
    if available_count == 0:
        print("⚠️  No LLMs are available! Running in mock mode is recommended.")
    elif available_count < total_count:
        print(f"⚠️  Some LLMs are unavailable ({available_count}/{total_count} ready)")
    else:
        print(f"✅ All LLMs are ready! ({available_count}/{total_count})")
    print()


async def analyze_prompt(
    orchestrator: BaseOrchestrator,
    prompt: str,
    selected_models: Optional[List[str]] = None,
    primary_model: Optional[str] = None
) -> Dict[str, Any]:
    """
    Analyze a prompt using the orchestrator.

    Args:
        orchestrator: BaseOrchestrator instance
        prompt: The prompt to analyze
        selected_models: Optional list of models to use
        primary_model: Optional model to use for synthesis

    Returns:
        Analysis results
    """
    print(f"Analyzing prompt: {prompt[:100]}..." + ("..." if len(prompt) > 100 else ""))

    # Process the prompt
    result = await orchestrator.process(
        prompt=prompt,
        models=selected_models,
        primary_model=primary_model
    )

    return result


async def main() -> Dict[str, Any]:
    """Main function to handle command-line arguments and run the analyzer."""
    parser = argparse.ArgumentParser(description="Ultra Analyzer CLI")
    parser.add_argument("--prompt", type=str, help="The prompt to analyze")
    parser.add_argument("--models", type=str, help="Comma-separated list of models to use")
    parser.add_argument("--primary", type=str, help="Model to use for synthesis")
    parser.add_argument("--mock", action="store_true", help="Use mock responses")
    parser.add_argument("--output", type=str, help="Output file for results (JSON format)")
    parser.add_argument("--check", action="store_true", help="Check model availability and exit")

    args = parser.parse_args()

    # Create configuration and orchestrator
    config = create_config_from_env(use_mock=args.mock)
    orchestrator = BaseOrchestrator(config)

    print("\n===== Ultra LLM Analyzer =====\n")

    # Check availability
    await check_models_availability(orchestrator)

    # Exit if only checking availability
    if args.check:
        return {"status": "success", "command": "check"}

    # If no prompt provided, get from stdin or ask the user
    if not args.prompt:
        if not sys.stdin.isatty():
            # Reading from pipe or redirected file
            args.prompt = sys.stdin.read().strip()
        else:
            print("\n" + "="*50)
            print("Enter your prompt below (type 'done' on a new line when finished)")
            print("="*50)

            prompt_lines = []
            while True:
                try:
                    line = input("> " if not prompt_lines else "  ")
                    if line.strip().lower() == 'done':
                        break
                    prompt_lines.append(line)
                except KeyboardInterrupt:
                    print("\nPrompt entry cancelled.")
                    return {"status": "cancelled"}
                except EOFError:
                    break

            if not prompt_lines:
                print("\nNo prompt entered. Exiting.")
                return {"status": "cancelled"}

            args.prompt = "\n".join(prompt_lines)
            print("\nPrompt received! Processing...\n")

    if not args.prompt:
        parser.error("No prompt provided")

    # Parse selected models from command line
    selected_models = None
    if args.models:
        selected_models = [model.strip() for model in args.models.split(",")]
    else:
        # Get available models
        available_models = list(orchestrator.config.models.keys())

        # Prompt user to select models interactively
        print("\nAvailable models:")
        for i, model_name in enumerate(available_models, 1):
            model_config = orchestrator.config.models[model_name]
            print(f"{i}. {model_name} ({model_config.provider})")

        print("\nEnter model numbers to use (comma-separated, or 'all' to use all):")
        model_selection = input("> ").strip().lower()

        if model_selection == "all" or model_selection == "":
            selected_models = available_models
        else:
            try:
                # Parse as indices
                selected_indices = [int(idx.strip()) - 1 for idx in model_selection.split(",")]
                selected_models = [available_models[idx] for idx in selected_indices if 0 <= idx < len(available_models)]

                if not selected_models:
                    print("No valid models selected. Using all available models.")
                    selected_models = available_models
            except ValueError:
                # Parse as model names
                candidate_models = [model.strip() for model in model_selection.split(",")]
                selected_models = [model for model in candidate_models if model in available_models]

                if not selected_models:
                    print("No valid models selected. Using all available models.")
                    selected_models = available_models

    # Get primary model from command line
    primary_model = args.primary

    # If no primary_model specified, prompt user to select one
    if not primary_model and selected_models:
        print("\nSelect primary model for synthesis:")
        for i, model_name in enumerate(selected_models, 1):
            print(f"{i}. {model_name}")

        print("\nEnter the number of the primary model:")
        primary_selection = input("> ").strip()

        try:
            primary_idx = int(primary_selection) - 1
            if 0 <= primary_idx < len(selected_models):
                primary_model = selected_models[primary_idx]
            else:
                print(f"Invalid selection. Using {selected_models[0]} as primary model.")
                primary_model = selected_models[0]
        except (ValueError, IndexError):
            print(f"Invalid selection. Using {selected_models[0]} as primary model.")
            primary_model = selected_models[0]

    # Run the analysis
    result = await analyze_prompt(
        orchestrator=orchestrator,
        prompt=args.prompt,
        selected_models=selected_models,
        primary_model=primary_model
    )

    # Save to file if specified
    if args.output:
        with open(args.output, "w") as f:
            json.dump(result, f, indent=2)
        print(f"Results saved to {args.output}")
    else:
        # Print the result to stdout
        print("\n\nULTRA RESPONSE:\n")
        print(result["ultra_response"])
        print("\n\nMODEL RESPONSES:\n")
        for model, response in result.get("model_responses", {}).items():
            print(f"\n--- {model} ---\n")
            content = response.get("content", "")
            print(content[:500] + "..." if len(content) > 500 else content)

    return result


if __name__ == "__main__":
    asyncio.run(main())
```

### 6. Create Unit Tests

File: `/Users/joshuafield/Documents/Ultra/tests/unit/orchestration/test_base_orchestrator.py`

```python
"""
Unit tests for the BaseOrchestrator class.
"""

import asyncio
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from src.orchestration.config import OrchestratorConfig, ModelConfig
from src.orchestration.base import BaseOrchestrator


class MockAdapter:
    """Mock adapter for testing."""

    def __init__(self, name="test", success=True):
        self.name = name
        self.success = success

    async def generate(self, prompt, **options):
        """Mock generate method."""
        if not self.success:
            raise Exception("Mock error")
        return f"Mock response from {self.name}: {prompt[:10]}..."

    async def check_availability(self):
        """Mock availability check."""
        return self.success


class TestBaseOrchestrator(unittest.IsolatedAsyncioTestCase):
    """Tests for BaseOrchestrator."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a config with mock models
        self.config = OrchestratorConfig()
        self.config.models = {
            "model1": ModelConfig(provider="test", model="model1"),
            "model2": ModelConfig(provider="test", model="model2")
        }
        self.config.default_models = ["model1", "model2"]
        self.config.default_primary_model = "model1"

        # Create an orchestrator with mock adapters
        self.orchestrator = BaseOrchestrator(self.config)
        self.orchestrator.adapters = {
            "model1": MockAdapter("model1"),
            "model2": MockAdapter("model2")
        }

    async def test_check_availability(self):
        """Test checking model availability."""
        # All models available
        availability = await self.orchestrator.check_availability()
        self.assertEqual(len(availability), 2)
        self.assertTrue(availability["model1"])
        self.assertTrue(availability["model2"])

        # One model unavailable
        self.orchestrator.adapters["model2"] = MockAdapter("model2", False)
        availability = await self.orchestrator.check_availability()
        self.assertTrue(availability["model1"])
        self.assertFalse(availability["model2"])

    async def test_process_success(self):
        """Test processing a prompt successfully."""
        result = await self.orchestrator.process("Test prompt")

        self.assertEqual(result["status"], "success")
        self.assertEqual(len(result["model_responses"]), 2)
        self.assertIn("model1", result["model_responses"])
        self.assertIn("model2", result["model_responses"])
        self.assertEqual(result["ultra_model"], "model1")
        self.assertIn("ultra_response", result)

    async def test_process_with_model_selection(self):
        """Test processing with specific models."""
        result = await self.orchestrator.process("Test prompt", models=["model1"])

        self.assertEqual(result["status"], "success")
        self.assertEqual(len(result["model_responses"]), 1)
        self.assertIn("model1", result["model_responses"])
        self.assertEqual(result["ultra_model"], "model1")

    async def test_process_with_primary_model(self):
        """Test processing with specific primary model."""
        result = await self.orchestrator.process(
            "Test prompt",
            models=["model1", "model2"],
            primary_model="model2"
        )

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["ultra_model"], "model2")

    async def test_process_with_errors(self):
        """Test processing with adapter errors."""
        # One model fails
        self.orchestrator.adapters["model2"] = MockAdapter("model2", False)

        result = await self.orchestrator.process("Test prompt")

        self.assertEqual(result["status"], "success")
        self.assertEqual(len(result["model_responses"]), 1)
        self.assertIn("model1", result["model_responses"])
        self.assertIn("model2", result["errors"])

        # All models fail
        self.orchestrator.adapters["model1"] = MockAdapter("model1", False)

        result = await self.orchestrator.process("Test prompt")

        self.assertEqual(result["status"], "error")
        self.assertIn("error", result)
        self.assertEqual(len(result["model_errors"]), 2)

    async def test_synthesize_responses(self):
        """Test response synthesis."""
        responses = {
            "model1": {"content": "Response from model1", "model": "model1"},
            "model2": {"content": "Response from model2", "model": "model2"}
        }

        synthesis = await self.orchestrator._synthesize_responses(
            "Test prompt",
            responses,
            "model1"
        )

        self.assertIsInstance(synthesis, str)
        self.assertTrue(len(synthesis) > 0)

    async def test_synthesize_single_response(self):
        """Test synthesis with a single response."""
        responses = {
            "model1": {"content": "Response from model1", "model": "model1"}
        }

        synthesis = await self.orchestrator._synthesize_responses(
            "Test prompt",
            responses,
            "model1"
        )

        self.assertEqual(synthesis, "Response from model1")

    async def test_synthesis_fallback(self):
        """Test synthesis fallback when primary model fails."""
        responses = {
            "model1": {"content": "Response from model1", "model": "model1"},
            "model2": {"content": "Response from model2", "model": "model2"}
        }

        # Make the _send_to_llm method raise an exception
        self.orchestrator._send_to_llm = AsyncMock(side_effect=Exception("Test error"))

        synthesis = await self.orchestrator._synthesize_responses(
            "Test prompt",
            responses,
            "model1"
        )

        # Should fall back to longest response
        self.assertTrue(synthesis.startswith("[Synthesis failed"))
        self.assertIn("Response from model", synthesis)


if __name__ == '__main__':
    unittest.main()
```

### 7. Create Integration Test

File: `/Users/joshuafield/Documents/Ultra/tests/integration/orchestration/test_orchestrator_integration.py`

```python
"""
Integration tests for the BaseOrchestrator.
"""

import asyncio
import os
import unittest
from unittest.mock import patch

from src.orchestration.config import OrchestratorConfig
from src.orchestration.base import BaseOrchestrator


class TestOrchestratorIntegration(unittest.IsolatedAsyncioTestCase):
    """Integration tests for BaseOrchestrator."""

    async def asyncSetUp(self):
        """Set up test fixtures."""
        # Enable mock mode for testing
        os.environ["USE_MOCK"] = "true"

        # Create a config for testing
        self.config = OrchestratorConfig(mock_mode=True)

        # Register test models
        self.orchestrator = BaseOrchestrator(self.config)
        self.orchestrator.register_model(
            name="test_model1",
            provider="openai",
            model="gpt-4",
            api_key="sk-mock-key",
            weight=1.0
        )
        self.orchestrator.register_model(
            name="test_model2",
            provider="anthropic",
            model="claude-3-opus",
            api_key="sk-ant-mock-key",
            weight=0.9
        )

    async def test_end_to_end_processing(self):
        """Test end-to-end processing in mock mode."""
        result = await self.orchestrator.process(
            prompt="What is the capital of France?",
            models=["test_model1", "test_model2"],
            primary_model="test_model1"
        )

        # Verify result structure
        self.assertEqual(result["status"], "success")
        self.assertIn("model_responses", result)
        self.assertIn("ultra_response", result)
        self.assertIn("test_model1", result["model_responses"])
        self.assertIn("test_model2", result["model_responses"])
        self.assertEqual(result["ultra_model"], "test_model1")

        # Verify model responses
        for model, response in result["model_responses"].items():
            self.assertIn("content", response)
            self.assertIn("model", response)
            self.assertIn("processing_time", response)

        # Verify ultra response
        self.assertTrue(len(result["ultra_response"]) > 0)

    async def asyncTearDown(self):
        """Clean up after tests."""
        # Disable mock mode
        if "USE_MOCK" in os.environ:
            del os.environ["USE_MOCK"]


if __name__ == '__main__':
    unittest.main()
```

## Implementation Schedule

| Day | Task                         | Description                                           |
| --- | ---------------------------- | ----------------------------------------------------- |
| 1   | Set up directory structure   | Create necessary directories and initial README files |
| 1   | Implement core configuration | Create configuration classes for orchestrator         |
| 1   | Create adapter factory       | Implement factory function for creating adapters      |
| 2   | Implement BaseOrchestrator   | Create core orchestration functionality               |
| 2   | Create CLI wrapper           | Implement simple CLI for testing                      |
| 3   | Implement unit tests         | Create comprehensive test suite                       |
| 3   | Test and debug               | Fix any issues and ensure everything works correctly  |

## Next Steps After BaseOrchestrator

1. Implement provider-specific adapter classes
2. Create EnhancedOrchestrator with advanced features
3. Implement service layer for orchestration management
4. Update API routes to use new orchestrator
5. Migrate existing code to use new components

## Risks and Mitigations

| Risk                    | Mitigation                                           |
| ----------------------- | ---------------------------------------------------- |
| Import path issues      | Use relative imports and create compatibility layers |
| Adapter incompatibility | Use adapter factory for backward compatibility       |
| Test failures           | Comprehensive test suite with mocking                |
| Performance issues      | Benchmark against existing implementation            |
