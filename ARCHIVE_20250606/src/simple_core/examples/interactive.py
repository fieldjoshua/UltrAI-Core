#!/usr/bin/env python3
"""
Interactive example for Simple Core Orchestrator.

This script provides an interactive interface to test the Simple Core
Orchestrator with your own prompts.

Usage:
    Make sure you have the required API keys in your environment:
    - OPENAI_API_KEY for OpenAI models
    - ANTHROPIC_API_KEY for Anthropic models
    - GOOGLE_API_KEY for Google Gemini models
    - LLAMA_MODEL_PATH for local Llama models

    Then run:
    python -m src.simple_core.examples.interactive
"""

import asyncio
import json
import logging
import os
import sys
from typing import Any, Dict, List

# Add the project root to the Python path
sys.path.insert(
    0,
    os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ),
)

from src.simple_core.config import Config, ModelDefinition
from src.simple_core.factory import create_from_env, create_orchestrator

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("simple_core.interactive")


async def initialize_orchestrator():
    """Initialize the orchestrator from environment variables."""
    logger.info("Initializing orchestrator from environment variables...")

    # Create orchestrator from environment
    orchestrator = create_from_env()

    if not orchestrator:
        logger.error("No API keys found in environment. Exiting.")
        return None

    return orchestrator


async def process_prompt(orchestrator, prompt: str, specific_models: List[str] = None):
    """
    Process a prompt using the orchestrator.

    Args:
        orchestrator: The orchestrator instance
        prompt: The prompt to process
        specific_models: Optional list of specific model names to use
    """
    # Create request
    request = {
        "prompt": prompt,
        "options": {
            "max_tokens": 1000,
            "temperature": 0.7,
            "system_message": "You are a helpful assistant.",
        },
    }

    # Add specific models if provided
    if specific_models:
        request["models"] = specific_models

    logger.info("Processing prompt...")
    start_time = asyncio.get_event_loop().time()

    # Process request
    response = await orchestrator.process(request)

    elapsed = asyncio.get_event_loop().time() - start_time
    logger.info(f"Processing completed in {elapsed:.2f} seconds.")

    return response


def display_response(response: Dict[str, Any], show_all: bool = False):
    """
    Display the response in a user-friendly format.

    Args:
        response: The response from the orchestrator
        show_all: Whether to show all model responses
    """
    print("\n=" * 40)
    print("PRIMARY RESPONSE:")
    print("-" * 80)
    print(response["content"])
    print("-" * 80)

    if show_all:
        print("\nALL MODEL RESPONSES:")
        for model_name, model_response in response["model_responses"].items():
            print(f"\n{model_name.upper()}:")
            print("-" * 40)
            if "error" in model_response:
                print(f"ERROR: {model_response['error']}")
            else:
                print(model_response["content"])

    print("\nMETADATA:")
    print(f"Processing time: {response['metadata']['time']:.2f} seconds")
    print(f"Models used: {', '.join(response['metadata']['models_used'])}")
    print(f"Successful models: {', '.join(response['metadata']['successful_models'])}")
    print(f"Primary model: {response['metadata']['primary_model']}")
    print("=" * 80)


async def interactive_session():
    """Run an interactive session with the orchestrator."""
    print("\nSimple Core Orchestrator - Interactive Mode")
    print("==========================================")
    print("Type 'exit' or 'quit' to exit the session.")
    print("Type 'show all' to toggle showing all model responses.")
    print("Type 'use model1,model2,...' to specify which models to use.")
    print("Type 'models' to see available models.")
    print("Type 'help' for help.")

    # Initialize orchestrator
    orchestrator = await initialize_orchestrator()
    if not orchestrator:
        return

    # Get available models
    available_models = [name for name in orchestrator.adapters.keys()]
    print(f"\nAvailable models: {', '.join(available_models)}")

    # Interactive loop
    show_all_responses = False
    specific_models = None

    while True:
        try:
            # Get user input
            user_input = input("\nEnter prompt (or command): ").strip()

            # Check for commands
            if user_input.lower() in ["exit", "quit"]:
                print("Exiting...")
                break

            elif user_input.lower() == "help":
                print("\nCommands:")
                print("  exit, quit - Exit the session")
                print("  show all - Toggle showing all model responses")
                print("  use model1,model2,... - Use specific models")
                print("  models - Show available models")
                print("  help - Show this help message")
                continue

            elif user_input.lower() == "show all":
                show_all_responses = not show_all_responses
                print(f"Show all responses: {show_all_responses}")
                continue

            elif user_input.lower().startswith("use "):
                models_str = user_input[4:].strip()
                if models_str.lower() == "all":
                    specific_models = None
                    print("Using all available models")
                else:
                    specific_models = [m.strip() for m in models_str.split(",")]
                    # Validate models
                    valid_models = [m for m in specific_models if m in available_models]
                    if not valid_models:
                        print(
                            f"No valid models specified. Available models: {', '.join(available_models)}"
                        )
                        specific_models = None
                    else:
                        specific_models = valid_models
                        print(f"Using models: {', '.join(specific_models)}")
                continue

            elif user_input.lower() == "models":
                print(f"\nAvailable models: {', '.join(available_models)}")
                continue

            # Process prompt
            response = await process_prompt(orchestrator, user_input, specific_models)

            # Display response
            display_response(response, show_all_responses)

        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"\nError processing prompt: {str(e)}")


def main():
    """Main entry point."""
    try:
        asyncio.run(interactive_session())
    except Exception as e:
        logger.error(f"Error running interactive session: {str(e)}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
