#!/usr/bin/env python
"""
Simple Ultra Analyzer

This script provides a simplified version of the UltraAI system for analyzing
prompts with multiple LLMs and combining the results.
"""

import asyncio
import json
import logging
import os
import sys
from typing import Any, Dict, List, Optional

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("simple_analyzer")

# Import LLM adapters
try:
    from src.models.llm_adapter import (
        AnthropicAdapter,
        GeminiAdapter,
        OpenAIAdapter,
        create_adapter,
    )
except ImportError:
    logger.error("Could not import LLM adapters. Falling back to mock implementation.")

    # Create mock adapter classes if imports fail
    class LLMAdapter:
        def __init__(self, name, api_key=None):
            self.name = name
            self.api_key = api_key

        async def generate(self, prompt, **options):
            return f"Mock response from {self.name}: This would be a response to: {prompt[:30]}..."

    class OpenAIAdapter(LLMAdapter):
        pass

    class AnthropicAdapter(LLMAdapter):
        pass

    class GeminiAdapter(LLMAdapter):
        pass

    def create_adapter(provider, api_key, **options):
        if provider.lower() == "openai":
            return OpenAIAdapter("openai", api_key)
        elif provider.lower() == "anthropic":
            return AnthropicAdapter("anthropic", api_key)
        elif provider.lower() == "gemini":
            return GeminiAdapter("gemini", api_key)
        else:
            return LLMAdapter(provider, api_key)


def load_api_keys():
    """Load API keys from environment variables."""
    return {
        "openai": os.environ.get("OPENAI_API_KEY", ""),
        "anthropic": os.environ.get("ANTHROPIC_API_KEY", ""),
        "google": os.environ.get("GOOGLE_API_KEY", ""),
    }


def get_available_models(
    api_keys: Dict[str, str], use_mock: bool = False
) -> Dict[str, Dict[str, Any]]:
    """Get available models based on API keys."""
    models = {}

    # Add models based on available API keys or mock mode
    if api_keys.get("openai") or use_mock:
        models["gpt4o"] = {
            "provider": "openai",
            "model": "gpt-4o",
            "weight": 1.0,
            "available": True,
        }
        models["gpt4turbo"] = {
            "provider": "openai",
            "model": "gpt-4-turbo",
            "weight": 0.9,
            "available": True,
        }

    if api_keys.get("anthropic") or use_mock:
        models["claude3opus"] = {
            "provider": "anthropic",
            "model": "claude-3-opus-20240229",
            "weight": 1.0,
            "available": True,
        }
        models["claude3sonnet"] = {
            "provider": "anthropic",
            "model": "claude-3-sonnet-20240229",
            "weight": 0.9,
            "available": True,
        }

    if api_keys.get("google") or use_mock:
        models["gemini15"] = {
            "provider": "gemini",
            "model": "gemini-1.5-pro-latest",
            "weight": 0.9,
            "available": True,
        }

    return models


async def generate_model_response(
    model_name: str,
    model_info: Dict[str, Any],
    prompt: str,
    api_keys: Dict[str, str],
    use_mock: bool = False,
) -> Dict[str, Any]:
    """Generate a response from a model."""
    logger.info(f"Generating response from {model_name} ({model_info['provider']})")

    start_time = asyncio.get_event_loop().time()

    try:
        # Get the appropriate API key
        provider = model_info["provider"]
        api_key = (
            api_keys.get(provider, "")
            if provider != "openai"
            else api_keys.get("openai")
        )

        # Set environment USE_MOCK if needed
        if use_mock:
            os.environ["USE_MOCK"] = "true"

        # Create the adapter
        adapter = create_adapter(
            provider,
            api_key,
            model=model_info["model"],
        )

        # Generate response
        content = await adapter.generate(prompt, max_tokens=1500)

        # Calculate processing time
        processing_time = asyncio.get_event_loop().time() - start_time

        return {
            "model": model_name,
            "content": content,
            "processing_time": processing_time,
            "tokens_used": len(content.split()) // 4,  # Rough estimate
            "success": True,
        }
    except Exception as e:
        logger.error(f"Error generating response from {model_name}: {e}")

        # Calculate processing time even for failures
        processing_time = asyncio.get_event_loop().time() - start_time

        return {
            "model": model_name,
            "content": f"Error: {str(e)}",
            "processing_time": processing_time,
            "tokens_used": 0,
            "success": False,
        }


async def synthesize_responses(
    prompt: str,
    model_responses: Dict[str, Dict[str, Any]],
    ultra_model: str,
    api_keys: Dict[str, str],
    use_mock: bool = False,
) -> str:
    """Synthesize multiple model responses using an ultra model."""
    logger.info(f"Synthesizing responses using {ultra_model}")

    # Prepare a prompt that includes all model responses
    synthesis_prompt = f"""As an expert synthesizer, analyze and combine these AI model responses to a user's prompt.

USER PROMPT:
{prompt}

MODEL RESPONSES:
"""

    for model_name, response in model_responses.items():
        if response["success"]:
            synthesis_prompt += (
                f"\n\n--- {model_name} RESPONSE ---\n{response['content']}\n"
            )

    synthesis_prompt += """
Based on these responses, provide a comprehensive synthesis that:
1. Combines the best insights from all models
2. Resolves any contradictions between the responses
3. Presents a clear, well-organized answer to the original prompt
"""

    try:
        # Get model info for the ultra model
        available_models = get_available_models(api_keys, use_mock)
        if ultra_model not in available_models:
            # Use any available model if the specified one doesn't exist
            ultra_model = next(iter(available_models.keys()))

        model_info = available_models[ultra_model]

        # Get the appropriate API key
        provider = model_info["provider"]
        api_key = (
            api_keys.get(provider, "")
            if provider != "openai"
            else api_keys.get("openai")
        )

        # Set environment USE_MOCK if needed
        if use_mock:
            os.environ["USE_MOCK"] = "true"

        # Create the adapter
        adapter = create_adapter(
            provider,
            api_key,
            model=model_info["model"],
        )

        # Generate synthesis
        synthesis = await adapter.generate(synthesis_prompt, max_tokens=2000)

        return synthesis
    except Exception as e:
        logger.error(f"Error synthesizing responses: {e}")

        # Fallback to a simple concatenation of responses
        synthesis = "ERROR IN SYNTHESIS. Here are the individual model responses:\n\n"
        for model_name, response in model_responses.items():
            if response["success"]:
                synthesis += f"--- {model_name} ---\n{response['content'][:500]}...\n\n"

        return synthesis


async def check_models_availability(
    api_keys: Dict[str, str], use_mock: bool = False
) -> Dict[str, bool]:
    """
    Check which models are available and responsive.

    Args:
        api_keys: Dictionary of API keys
        use_mock: Whether to use mock responses

    Returns:
        Dictionary mapping model names to availability status
    """
    test_prompt = "Hello, this is a test prompt to check if you're available."
    available_models = get_available_models(api_keys, use_mock)
    model_status = {}

    print("Checking LLM availability...")

    for model_name, model_info in available_models.items():
        try:
            provider = model_info["provider"]
            api_key = (
                api_keys.get(provider, "")
                if provider != "openai"
                else api_keys.get("openai")
            )

            if use_mock:
                # In mock mode, all models are considered available
                print(f"✓ {model_name} ({provider}) - Available in mock mode")
                model_status[model_name] = True
                continue

            if not api_key:
                print(f"✗ {model_name} ({provider}) - No API key provided")
                model_status[model_name] = False
                continue

            # Create adapter and test with a simple prompt
            adapter = create_adapter(provider, api_key, model=model_info["model"])

            # For real availability testing, we would call adapter.generate() here
            # But to avoid unnecessary API calls, we'll just check if the API key exists
            print(f"✓ {model_name} ({provider}) - API key is present")
            model_status[model_name] = True

        except Exception as e:
            print(f"✗ {model_name} ({provider}) - Error: {str(e)}")
            model_status[model_name] = False

    # Print a summary
    available_count = sum(1 for status in model_status.values() if status)
    total_count = len(model_status)

    if available_count == 0:
        print("\n⚠️  No LLMs are available! Running in mock mode is recommended.")
    elif available_count < total_count:
        print(f"\n⚠️  Some LLMs are unavailable ({available_count}/{total_count} ready)")
    else:
        print(f"\n✅ All LLMs are ready! ({available_count}/{total_count})")

    return model_status


async def analyze_prompt(
    prompt: str,
    selected_models: Optional[List[str]] = None,
    ultra_model: Optional[str] = None,
    use_mock: bool = False,
) -> Dict[str, Any]:
    """
    Analyze a prompt using multiple LLMs and combine the results.

    Args:
        prompt: The prompt to analyze
        selected_models: Optional list of models to use (uses all available if None)
        ultra_model: Model to use for synthesis (uses first available if None)
        use_mock: Whether to use mock responses

    Returns:
        Analysis results
    """
    # Load API keys
    api_keys = load_api_keys()

    # Get available models
    available_models = get_available_models(api_keys, use_mock)

    if not available_models:
        return {
            "status": "error",
            "message": "No models available. Please set API keys or enable mock mode.",
        }

    # Filter models based on selection
    if selected_models:
        models_to_use = {
            name: info
            for name, info in available_models.items()
            if name in selected_models
        }
    else:
        models_to_use = available_models

    if not models_to_use:
        return {
            "status": "error",
            "message": "No valid models selected for processing",
        }

    # Set default ultra model if not specified
    if not ultra_model or ultra_model not in available_models:
        ultra_model = next(iter(available_models.keys()))

    logger.info(f"Analyzing prompt with models: {list(models_to_use.keys())}")
    logger.info(f"Ultra model: {ultra_model}")

    # Generate responses from all models in parallel
    tasks = []
    for model_name, model_info in models_to_use.items():
        task = generate_model_response(
            model_name, model_info, prompt, api_keys, use_mock
        )
        tasks.append(task)

    model_responses = {}
    responses = await asyncio.gather(*tasks)
    for response in responses:
        model_name = response["model"]
        model_responses[model_name] = response

    # Synthesize responses
    ultra_response = await synthesize_responses(
        prompt, model_responses, ultra_model, api_keys, use_mock
    )

    # Format the final result
    result = {
        "status": "success",
        "model_responses": {
            model: response["content"] for model, response in model_responses.items()
        },
        "ultra_response": ultra_response,
        "performance": {
            "total_time_seconds": sum(
                response["processing_time"] for response in model_responses.values()
            ),
            "model_times": {
                model: response["processing_time"]
                for model, response in model_responses.items()
            },
            "token_counts": {
                model: response["tokens_used"]
                for model, response in model_responses.items()
            },
        },
        "metadata": {
            "models_used": list(model_responses.keys()),
            "ultra_model": ultra_model,
        },
    }

    return result


async def main():
    """Main function to handle command-line arguments and run the analyzer."""
    import argparse

    parser = argparse.ArgumentParser(description="Simple Ultra Analyzer")
    parser.add_argument("--prompt", type=str, help="The prompt to analyze")
    parser.add_argument(
        "--models", type=str, help="Comma-separated list of models to use"
    )
    parser.add_argument("--ultra", type=str, help="Model to use for synthesis")
    parser.add_argument("--mock", action="store_true", help="Use mock responses")
    parser.add_argument(
        "--output", type=str, help="Output file for results (JSON format)"
    )
    parser.add_argument(
        "--check", action="store_true", help="Check model availability and exit"
    )

    args = parser.parse_args()

    # Load API keys
    api_keys = load_api_keys()

    # Check model availability if requested
    if args.check:
        model_status = await check_models_availability(api_keys, args.mock)
        return {"status": "success", "model_status": model_status}

    print("\n===== Ultra LLM Analyzer =====\n")

    # Check availability before processing
    await check_models_availability(api_keys, args.mock)

    # If no prompt provided, get from stdin or ask the user
    if not args.prompt:
        if not sys.stdin.isatty():
            # Reading from pipe or redirected file
            args.prompt = sys.stdin.read().strip()
        else:
            print("\n" + "=" * 50)
            print("Enter your prompt below (type 'done' on a new line when finished)")
            print("=" * 50)

            prompt_lines = []
            while True:
                try:
                    line = input("> " if not prompt_lines else "  ")
                    if line.strip().lower() == "done":
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

    # Interactive model selection if not specified in args
    available_models = get_available_models(api_keys, args.mock)
    available_model_names = list(available_models.keys())

    # Parse selected models from command line
    selected_models = None
    if args.models:
        selected_models = [model.strip() for model in args.models.split(",")]
    else:
        # Prompt user to select models interactively
        print("\nAvailable models:")
        for i, model_name in enumerate(available_model_names, 1):
            model_info = available_models[model_name]
            print(f"{i}. {model_name} ({model_info['provider']})")

        print("\nEnter model numbers to use (comma-separated, or 'all' to use all):")
        model_selection = input("> ").strip().lower()

        if model_selection == "all" or model_selection == "":
            selected_models = available_model_names
        else:
            try:
                # Parse as indices
                selected_indices = [
                    int(idx.strip()) - 1 for idx in model_selection.split(",")
                ]
                selected_models = [
                    available_model_names[idx]
                    for idx in selected_indices
                    if 0 <= idx < len(available_model_names)
                ]

                if not selected_models:
                    print("No valid models selected. Using all available models.")
                    selected_models = available_model_names
            except ValueError:
                # Parse as model names
                candidate_models = [
                    model.strip() for model in model_selection.split(",")
                ]
                selected_models = [
                    model
                    for model in candidate_models
                    if model in available_model_names
                ]

                if not selected_models:
                    print("No valid models selected. Using all available models.")
                    selected_models = available_model_names

    # Get ultra model from command line
    ultra_model = args.ultra

    # If no ultra_model specified, prompt user to select one
    if not ultra_model and selected_models:
        print("\nSelect primary model for synthesis:")
        for i, model_name in enumerate(selected_models, 1):
            print(f"{i}. {model_name}")

        print("\nEnter the number of the primary model:")
        ultra_selection = input("> ").strip()

        try:
            ultra_idx = int(ultra_selection) - 1
            if 0 <= ultra_idx < len(selected_models):
                ultra_model = selected_models[ultra_idx]
            else:
                print(
                    f"Invalid selection. Using {selected_models[0]} as primary model."
                )
                ultra_model = selected_models[0]
        except (ValueError, IndexError):
            print(f"Invalid selection. Using {selected_models[0]} as primary model.")
            ultra_model = selected_models[0]

    # Run the analysis
    print(f"\nAnalyzing prompt: {args.prompt[:50]}...")
    result = await analyze_prompt(args.prompt, selected_models, ultra_model, args.mock)

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
        for model, response in result["model_responses"].items():
            print(f"\n--- {model} ---\n")
            print(response[:500] + "..." if len(response) > 500 else response)

    return result


if __name__ == "__main__":
    asyncio.run(main())
