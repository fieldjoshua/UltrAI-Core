"""
Test script for the modular orchestrator with factual analysis.
"""

import asyncio
import logging
from typing import Any, Dict

from src.simple_core.config import RequestConfig
from src.simple_core.factory import create_from_env

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# A prompt that requires factual accuracy
TEST_PROMPT = "Explain the key events that led to World War I."


async def run_factual_test():
    print("\n" + "=" * 80)
    print("Modular Orchestrator Test - Factual Analysis")
    print("=" * 80)

    # Create the modular orchestrator
    orchestrator = create_from_env(modular=True, analysis_type="factual")

    if not orchestrator:
        print("Failed to create orchestrator. Please check API keys in environment.")
        return

    # Create a request with specific configuration
    request = RequestConfig(
        prompt=TEST_PROMPT,
        model_names=[],  # Empty list means use all available models
        lead_model=None,  # None means use highest priority model
        analysis_type="factual",  # Use factual analysis
    )

    print(f"\nProcessing prompt: {TEST_PROMPT}")
    print("\nThis will demonstrate the modular orchestrator with factual analysis.")
    print("Working...\n")

    # Process the request
    result = await orchestrator.process(request.to_dict())

    # Display initial responses
    print("\n--- Initial Responses ---")
    for i, response in enumerate(result.get("initial_responses", []), 1):
        model = response.get("model", "Unknown")
        provider = response.get("provider", "Unknown")
        response_text = response.get("response", "")

        print(f"\n[{i}] {model} ({provider}):")
        print("-" * 40)
        print(response_text[:500] + ("..." if len(response_text) > 500 else ""))

    # Display analysis results
    if result.get("analysis_results"):
        print("\n\n" + "=" * 80)
        print("--- Analysis Results ---")
        print("Analysis type: factual")

        if "combined_summary" in result.get("analysis_results", {}):
            print("\nAnalysis Summary:")
            print("-" * 40)
            print(result["analysis_results"]["combined_summary"][:1000] + "...")
        else:
            print("No analysis summary available.")

    # Display synthesis
    if result.get("synthesis"):
        print("\n\n" + "=" * 80)
        print("--- Synthesized Response ---")
        synthesis = result.get("synthesis", {})
        model = synthesis.get("model", "Unknown")
        provider = synthesis.get("provider", "Unknown")

        print(f"Synthesized by {model} ({provider}):")
        print("-" * 40)
        print(synthesis.get("response", ""))

    print("\n" + "=" * 80)
    print("Test completed!")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    asyncio.run(run_factual_test())
