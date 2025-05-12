#!/usr/bin/env python3
"""
Custom prompt runner for the Ultra orchestration system.
"""

import asyncio
import logging
import sys
import os
from typing import Any, Dict

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

async def run_custom_prompt(prompt: str):
    """Run a custom prompt through the orchestrator."""
    print("\n" + "=" * 80)
    print("Ultra Orchestrator - Custom Prompt")
    print("=" * 80)

    # Import here to avoid immediate import errors
    try:
        from src.simple_core.config import RequestConfig
        from src.simple_core.factory import create_from_env
    except ImportError as e:
        print(f"Failed to import required modules: {e}")
        return

    # Set environment to only use OpenAI
    os.environ["ANTHROPIC_API_KEY"] = ""
    os.environ["GOOGLE_API_KEY"] = ""
    os.environ["DEEPSEEK_API_KEY"] = ""
    
    # Create the orchestrator with only OpenAI
    orchestrator = create_from_env(modular=True, analysis_type="factual")

    if not orchestrator:
        print("Failed to create orchestrator. Please check API keys in environment.")
        return

    # Create a request with specific configuration
    request = RequestConfig(
        prompt=prompt,
        model_names=["openai-gpt4o"],  # Only use OpenAI's GPT-4o
        lead_model="openai-gpt4o",
        analysis_type="factual",
    )

    print(f"\nProcessing prompt: {prompt}")
    print("\nThis will generate a response using OpenAI's GPT-4o model.")
    print("Working...\n")

    try:
        # Process the request
        result = await orchestrator.process(request.to_dict())

        # Display initial responses
        print("\n--- Response ---")
        for response in result.get("initial_responses", []):
            model = response.get("model", "Unknown")
            provider = response.get("provider", "Unknown")
            response_text = response.get("response", "")

            print(f"\n{model} ({provider}):")
            print("-" * 40)
            print(response_text)

        # Display synthesis if available
        if result.get("synthesis"):
            print("\n\n" + "=" * 80)
            print("--- Synthesized Response ---")
            synthesis = result.get("synthesis", {})
            model = synthesis.get("model", "Unknown")
            provider = synthesis.get("provider", "Unknown")

            print(f"Synthesized by {model} ({provider}):")
            print("-" * 40)
            print(synthesis.get("response", ""))

    except Exception as e:
        print(f"Error processing prompt: {e}")

    print("\n" + "=" * 80)
    print("Done!")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_custom_prompt.py \"Your prompt here\"")
        sys.exit(1)

    prompt = sys.argv[1]
    asyncio.run(run_custom_prompt(prompt))