#!/usr/bin/env python3
"""
Basic usage example for Simple Core Orchestrator.

This script demonstrates the most basic usage pattern for the Simple Core
Orchestrator with real LLM providers.

Usage:
    Make sure you have the required API keys in your environment:
    - OPENAI_API_KEY for OpenAI models
    - ANTHROPIC_API_KEY for Anthropic models
    - GOOGLE_API_KEY for Google Gemini models
    - LLAMA_MODEL_PATH for local Llama models
    - LLAMA_COMMAND for Llama command (defaults to "llama")

    Then run:
    python -m src.simple_core.examples.basic_usage
"""

import asyncio
import json
import logging
import os
import sys

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
logger = logging.getLogger("simple_core.example")


async def run_example():
    """Run the basic usage example."""
    logger.info("Starting Simple Core Orchestrator example")

    # Method 1: Create from environment variables (simplest)
    orchestrator = create_from_env()

    if not orchestrator:
        logger.error(
            "No API keys found in environment. Setting up with manual configuration."
        )

        # Check for API keys and local models
        openai_key = os.environ.get("OPENAI_API_KEY")
        anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
        google_key = os.environ.get("GOOGLE_API_KEY")
        llama_model_path = os.environ.get("LLAMA_MODEL_PATH")
        llama_command = os.environ.get("LLAMA_COMMAND", "llama")

        if not any([openai_key, anthropic_key, google_key, llama_model_path]):
            logger.error(
                "No API keys or local models available. Please set environment variables."
            )
            return

        # Method 2: Manual configuration
        models = []

        if openai_key:
            models.append(
                ModelDefinition(
                    name="openai-gpt4o",
                    provider="openai",
                    priority=1,
                    api_key=openai_key,
                    options={"model_id": "gpt-4o"},
                )
            )

        if anthropic_key:
            models.append(
                ModelDefinition(
                    name="anthropic-claude",
                    provider="anthropic",
                    priority=2,
                    api_key=anthropic_key,
                    options={"model_id": "claude-3-opus-20240229"},
                )
            )

        if google_key:
            models.append(
                ModelDefinition(
                    name="google-gemini",
                    provider="gemini",
                    priority=3,
                    api_key=google_key,
                    options={"model_id": "gemini-1.5-pro-latest"},
                )
            )

        # Check for Llama
        if llama_model_path and os.path.exists(llama_model_path):
            models.append(
                ModelDefinition(
                    name="local-llama",
                    provider="llama",
                    priority=4,
                    options={
                        "model_path": llama_model_path,
                        "command": llama_command,
                        "extra_args": [],
                    },
                )
            )

        config = Config(models=models, parallel=True)
        orchestrator = create_orchestrator(config)

    # Create a simple request
    request = {
        "prompt": "Explain in 3 sentences what an LLM orchestrator does.",
        "options": {"max_tokens": 500, "temperature": 0.7},
    }

    logger.info(f"Sending request: {request['prompt']}")

    # Process the request
    response = await orchestrator.process(request)

    # Display results
    logger.info("Response received:")
    logger.info(f"Content: {response['content']}")
    logger.info(f"Processing time: {response['metadata']['time']:.2f} seconds")
    logger.info(f"Models used: {response['metadata']['models_used']}")
    logger.info(f"Successful models: {response['metadata']['successful_models']}")
    logger.info(f"Primary model: {response['metadata']['primary_model']}")

    # Save detailed response to file
    with open("orchestrator_response.json", "w") as f:
        json.dump(response, f, indent=2)

    logger.info("Detailed response saved to orchestrator_response.json")


def main():
    """Main entry point."""
    try:
        asyncio.run(run_example())
    except Exception as e:
        logger.error(f"Error running example: {str(e)}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
