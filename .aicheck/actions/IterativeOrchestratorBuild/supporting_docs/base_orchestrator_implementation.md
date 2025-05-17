# BaseOrchestrator Implementation

This document provides a reference implementation of the BaseOrchestrator class that will serve as the foundation for the iterative orchestrator system.

## Implementation

```python
"""
Base orchestration system for managing LLM requests and responses.
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Union, Tuple

# Adapter imports would be here
from src.models.llm_adapter import (
    OpenAIAdapter,
    AnthropicAdapter,
    GeminiAdapter,
    BaseLLMAdapter
)
from backend.services.mock_llm_service import MockLLMService

logger = logging.getLogger(__name__)

class BaseOrchestrator:
    """
    Core orchestration system for managing LLM requests and responses.

    Handles:
    - Sending prompts to multiple LLMs in parallel
    - Error handling and retries
    - Basic response synthesis
    - Mock mode support
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None, mock_mode: bool = False):
        """
        Initialize the BaseOrchestrator.

        Args:
            config (dict, optional): Configuration for LLMs
            mock_mode (bool): Whether to use mock responses
        """
        self.config = config or {}
        self.mock_mode = mock_mode
        self.mock_service = MockLLMService() if mock_mode else None
        self.adapters = self._initialize_adapters()

    def _initialize_adapters(self) -> Dict[str, BaseLLMAdapter]:
        """
        Initialize LLM adapters from configuration.

        Returns:
            dict: Mapping of model names to adapters
        """
        adapters = {}
        for model_name, model_config in self.config.items():
            provider = model_config.get("provider", "").lower()
            api_key = model_config.get("api_key", "")
            parameters = model_config.get("parameters", {})

            if not api_key and not self.mock_mode:
                logger.warning(f"No API key for {model_name}, skipping")
                continue

            try:
                if provider == "openai":
                    adapters[model_name] = OpenAIAdapter(
                        api_key=api_key,
                        model=model_name,
                        parameters=parameters
                    )
                elif provider == "anthropic":
                    adapters[model_name] = AnthropicAdapter(
                        api_key=api_key,
                        model=model_name,
                        parameters=parameters
                    )
                elif provider == "gemini":
                    adapters[model_name] = GeminiAdapter(
                        api_key=api_key,
                        model=model_name,
                        parameters=parameters
                    )
                else:
                    logger.warning(f"Unsupported provider {provider} for {model_name}")
            except Exception as e:
                logger.error(f"Failed to initialize adapter for {model_name}: {e}")

        return adapters

    async def check_models_availability(self) -> Dict[str, bool]:
        """
        Check which models are available and responsive.

        Returns:
            Dict[str, bool]: Mapping of model names to availability status
        """
        availability = {}
        check_tasks = []

        for model_name, adapter in self.adapters.items():
            check_tasks.append(self._check_model_availability(model_name, adapter))

        results = await asyncio.gather(*check_tasks, return_exceptions=True)

        for model_name, result in zip(self.adapters.keys(), results):
            if isinstance(result, Exception):
                logger.warning(f"Error checking availability for {model_name}: {result}")
                availability[model_name] = False
            else:
                availability[model_name] = result

        return availability

    async def _check_model_availability(self, model_name: str, adapter: BaseLLMAdapter) -> bool:
        """
        Check if a specific model is available.

        Args:
            model_name (str): Name of the model
            adapter (BaseLLMAdapter): Adapter for the model

        Returns:
            bool: True if available, False otherwise
        """
        if self.mock_mode:
            return True

        try:
            # Simple prompt to check availability
            test_prompt = "Hello, are you available? Please respond with a single word: Yes."
            response = await adapter.generate(test_prompt, max_tokens=10)
            return response is not None
        except Exception as e:
            logger.warning(f"Model {model_name} availability check failed: {e}")
            return False

    async def process(self,
                     prompt: str,
                     selected_models: Optional[List[str]] = None,
                     ultra_model: Optional[str] = None) -> Dict[str, Any]:
        """
        Process a prompt using multiple LLMs and synthesize the results.

        Args:
            prompt (str): The prompt to analyze
            selected_models (list, optional): Models to use for analysis
            ultra_model (str, optional): Model to use for synthesis

        Returns:
            dict: The orchestrated response
        """
        start_time = time.time()

        # Determine which models to use
        if selected_models:
            models_to_use = {
                model: adapter for model, adapter in self.adapters.items()
                if model in selected_models
            }
        else:
            models_to_use = self.adapters

        if not models_to_use:
            return {
                "error": "No valid models available",
                "status": "failed",
                "elapsed_time": time.time() - start_time
            }

        # Determine ultra model
        if ultra_model and ultra_model in models_to_use:
            synthesis_model = ultra_model
        else:
            # Use first available model as fallback
            synthesis_model = next(iter(models_to_use.keys()))

        # Process with all models
        llm_tasks = []
        for model_name, adapter in models_to_use.items():
            llm_tasks.append(self._send_to_llm(model_name, adapter, prompt))

        llm_results = await asyncio.gather(*llm_tasks, return_exceptions=True)

        # Organize results
        responses = {}
        errors = {}

        for model_name, result in zip(models_to_use.keys(), llm_results):
            if isinstance(result, Exception):
                logger.error(f"Error processing with {model_name}: {result}")
                errors[model_name] = str(result)
            else:
                responses[model_name] = result

        # If no successful responses, return error
        if not responses:
            return {
                "error": "All models failed to process",
                "status": "failed",
                "model_errors": errors,
                "elapsed_time": time.time() - start_time
            }

        # Synthesize responses
        synthesis_result = await self._synthesize_responses(
            prompt=prompt,
            responses=responses,
            ultra_model=synthesis_model
        )

        # Return final result
        return {
            "status": "success",
            "synthesis": synthesis_result,
            "responses": responses,
            "errors": errors,
            "ultra_model": synthesis_model,
            "elapsed_time": time.time() - start_time
        }

    async def _send_to_llm(self,
                          model_name: str,
                          adapter: BaseLLMAdapter,
                          prompt: str) -> Dict[str, Any]:
        """
        Send prompt to a specific LLM and handle errors.

        Args:
            model_name (str): Name of the model
            adapter (BaseLLMAdapter): Adapter for the model
            prompt (str): The prompt to send

        Returns:
            dict: The LLM response
        """
        if self.mock_mode and self.mock_service:
            provider = adapter.get_provider()
            return await self.mock_service.generate_mock_response(prompt, model_name, provider)

        max_retries = 3
        retry_delay = 1.0

        for retry in range(max_retries):
            try:
                start_time = time.time()
                response = await adapter.generate(prompt)
                elapsed_time = time.time() - start_time

                return {
                    "model": model_name,
                    "provider": adapter.get_provider(),
                    "response": response,
                    "elapsed_time": elapsed_time
                }
            except Exception as e:
                logger.warning(f"Error from {model_name} (attempt {retry+1}/{max_retries}): {e}")
                if retry < max_retries - 1:
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    raise

    async def _synthesize_responses(self,
                                   prompt: str,
                                   responses: Dict[str, Dict[str, Any]],
                                   ultra_model: str) -> Dict[str, Any]:
        """
        Combine multiple LLM responses into a single result.

        Args:
            prompt (str): The original prompt
            responses (dict): Responses from multiple LLMs
            ultra_model (str): Model to use for synthesis

        Returns:
            dict: Synthesized response
        """
        # If only one response, return it directly
        if len(responses) == 1:
            model_name, response = next(iter(responses.items()))
            return {
                "summary": response["response"],
                "source_model": model_name,
                "is_synthesized": False
            }

        # For multiple responses, create a synthesis prompt
        synthesis_prompt = self._create_synthesis_prompt(prompt, responses)

        # Use the ultra model to synthesize
        ultra_adapter = self.adapters.get(ultra_model)
        if not ultra_adapter:
            # Fallback to first available
            ultra_model, ultra_adapter = next(iter(self.adapters.items()))

        try:
            if self.mock_mode and self.mock_service:
                provider = ultra_adapter.get_provider()
                synthesis_response = await self.mock_service.generate_mock_response(
                    synthesis_prompt, ultra_model, provider
                )
                synthesis_text = synthesis_response["response"]
            else:
                start_time = time.time()
                synthesis_result = await ultra_adapter.generate(synthesis_prompt)
                elapsed_time = time.time() - start_time
                synthesis_text = synthesis_result

            return {
                "summary": synthesis_text,
                "source_model": ultra_model,
                "is_synthesized": True,
                "models_used": list(responses.keys())
            }
        except Exception as e:
            logger.error(f"Error during synthesis with {ultra_model}: {e}")
            # Fallback to most detailed response
            longest_response = max(
                responses.items(),
                key=lambda x: len(str(x[1].get("response", "")))
            )
            return {
                "summary": longest_response[1]["response"],
                "source_model": longest_response[0],
                "is_synthesized": False,
                "synthesis_error": str(e)
            }

    def _create_synthesis_prompt(self,
                                original_prompt: str,
                                responses: Dict[str, Dict[str, Any]]) -> str:
        """
        Create a prompt for synthesizing multiple responses.

        Args:
            original_prompt (str): The original prompt
            responses (dict): Responses from multiple LLMs

        Returns:
            str: Synthesis prompt
        """
        synthesis_prompt = f"""
        You are an expert at synthesizing responses from multiple AI models.

        The original question/prompt was:
        "{original_prompt}"

        The following AI models have provided responses:

        """

        for model_name, response_data in responses.items():
            response_text = response_data.get("response", "")
            provider = response_data.get("provider", "unknown")

            synthesis_prompt += f"""
            --- {model_name} ({provider}) response ---
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

## Usage Example

```python
async def main():
    """Example usage of BaseOrchestrator."""
    # Configuration
    config = {
        "gpt4": {
            "provider": "openai",
            "api_key": os.environ.get("OPENAI_API_KEY", ""),
            "parameters": {
                "temperature": 0.7,
                "max_tokens": 2000
            }
        },
        "claude3": {
            "provider": "anthropic",
            "api_key": os.environ.get("ANTHROPIC_API_KEY", ""),
            "parameters": {
                "temperature": 0.5,
                "max_tokens": 4000
            }
        }
    }

    # Create orchestrator
    use_mock = not (os.environ.get("OPENAI_API_KEY") and os.environ.get("ANTHROPIC_API_KEY"))
    orchestrator = BaseOrchestrator(config=config, mock_mode=use_mock)

    # Check availability
    availability = await orchestrator.check_models_availability()
    print("Model availability:")
    for model, available in availability.items():
        status = "Available" if available else "Unavailable"
        print(f"  - {model}: {status}")

    # Process a prompt
    prompt = "Explain the concept of multimodal AI in simple terms."
    result = await orchestrator.process(
        prompt=prompt,
        selected_models=["gpt4", "claude3"],
        ultra_model="claude3"
    )

    # Print results
    if result["status"] == "success":
        print("\nSynthesized Response:")
        print(result["synthesis"]["summary"])

        print("\nIndividual Responses:")
        for model, response in result["responses"].items():
            print(f"\n--- {model} ---")
            print(response["response"])
    else:
        print("\nError:")
        print(result["error"])
        if "model_errors" in result:
            for model, error in result["model_errors"].items():
                print(f"  - {model}: {error}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Notes on Implementation

1. **Error Handling**: The implementation includes comprehensive error handling with retries and fallbacks
2. **Fallback Mechanisms**: If synthesis fails, the system falls back to the longest individual response
3. **Mock Mode**: Fully supports mock mode for development without API keys
4. **Extensibility**: The design allows for easy extension with new providers or features
5. **Configuration**: Uses a simple configuration format that can be extended

## Next Steps

The BaseOrchestrator provides core functionality, but several enhancements are planned:

1. **Document Processing**: Add support for analyzing documents alongside prompts
2. **Analysis Patterns**: Implement different analysis patterns with specialized prompts
3. **Caching**: Add response caching for improved efficiency
4. **Metrics**: Enhance metrics collection for performance analysis
5. **API Integration**: Create adapters for existing API endpoints
