"""
Example of using the modular orchestrator.

This script demonstrates how to use the modular orchestrator with
different analysis types and configuration options.
"""

import asyncio
import logging
import os
import sys
from typing import Any, Dict, List

# Add the parent directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from src.simple_core.config.request_config import RequestConfig
from src.simple_core.factory import create_from_env

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


async def run_modular_example():
    """Run an example with the modular orchestrator."""
    print("\n" + "=" * 80)
    print("Modular Orchestrator Example")
    print("=" * 80)

    # Create a modular orchestrator using environment variables
    # By default, it will use comparative analysis
    orchestrator = create_from_env(modular=True)

    if not orchestrator:
        print("Failed to create orchestrator. Please check API keys in environment.")
        return

    print("\nCreated modular orchestrator with default comparative analysis.")

    # Example 1: Basic request with default settings
    prompt = "Explain how blockchain technology works in simple terms."
    print(f"\nProcessing prompt: {prompt}")

    # Create a request config
    request = RequestConfig(
        prompt=prompt,
        # Leave model_names empty to use all available models
        model_names=[],
        # Leave lead_model as None to use highest priority model
        lead_model=None,
        # Use comparative analysis (default)
        analysis_type="comparative",
    )

    # Process the request
    print("Processing with default settings...")
    result = await orchestrator.process(request)

    # Display the synthesis result
    print("\n--- Synthesized Response ---")
    if "synthesis" in result and "response" in result["synthesis"]:
        print(f"Lead model: {result['synthesis']['model']}")
        print(f"Response:\n{result['synthesis']['response']}")
    else:
        print("No synthesis available.")

    # Example 2: Request with specific models and lead
    print("\n" + "=" * 80)
    print("Example with specific model selection")
    print("=" * 80)

    # Get available model names from the previous result
    available_models = [resp["model"] for resp in result["initial_responses"]]
    print(f"Available models: {', '.join(available_models)}")

    if len(available_models) >= 2:
        # Select first two models and make the second one the lead
        selected_models = available_models[:2]
        lead_model = selected_models[1]

        print(f"Selected models: {', '.join(selected_models)}")
        print(f"Lead model: {lead_model}")

        # Create a request with specific models and lead
        prompt = "What are the key considerations for implementing AI in healthcare?"
        request = RequestConfig(
            prompt=prompt,
            model_names=selected_models,
            lead_model=lead_model,
            analysis_type="comparative",
        )

        # Process the request
        print(f"\nProcessing prompt: {prompt}")
        result = await orchestrator.process(request)

        # Display the synthesis result
        print("\n--- Synthesized Response ---")
        if "synthesis" in result and "response" in result["synthesis"]:
            print(f"Lead model: {result['synthesis']['model']}")
            print(f"Response:\n{result['synthesis']['response']}")
        else:
            print("No synthesis available.")
    else:
        print("Not enough models available for this example.")

    print("\n" + "=" * 80 + "\n")


if __name__ == "__main__":
    asyncio.run(run_modular_example())
