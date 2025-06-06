"""
Interactive example for the Enhanced Orchestrator

This script demonstrates the enhanced orchestrator with meta-analysis and synthesis.
It allows you to enter prompts and see results from different stages of processing.
"""

import asyncio
import json
import logging
import os
import sys
from typing import Any, Dict

# Add the parent directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from src.simple_core.config import Config, ModelDefinition
from src.simple_core.factory import create_from_env

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


async def enhanced_interactive_session():
    """Run an interactive session with the enhanced orchestrator"""
    # Create the enhanced orchestrator from environment variables
    orchestrator = create_from_env(enhanced=True)

    if not orchestrator:
        print("Failed to create orchestrator. Please check API keys in environment.")
        print("Required environment variables:")
        print("  - OPENAI_API_KEY (for OpenAI models)")
        print("  - ANTHROPIC_API_KEY (for Anthropic models)")
        print("  - GOOGLE_API_KEY (for Google/Gemini models)")
        print("  - LLAMA_MODEL_PATH and LLAMA_COMMAND (for local Llama models)")
        return

    print("\n" + "=" * 80)
    print("Enhanced Orchestrator Interactive Session")
    print("=" * 80)
    print("Enter prompts to process with the enhanced orchestrator.")
    print("The orchestrator will perform multi-stage processing:")
    print("1. Initial responses from all configured models")
    print("2. Meta-analysis of the responses")
    print("3. Synthesis of results into a final response")
    print("\nType 'exit', 'quit', or use Ctrl+C to end the session.")
    print("=" * 80 + "\n")

    try:
        while True:
            # Get user input
            prompt = input("\nEnter your prompt (or 'exit' to quit): ")
            if prompt.lower() in ["exit", "quit"]:
                break

            if not prompt.strip():
                continue

            # Process the prompt
            print("\nProcessing with enhanced orchestrator...")
            try:
                result = await orchestrator.process({"prompt": prompt})

                # Display initial responses
                print("\n--- Initial Responses ---")
                for i, response in enumerate(result.get("initial_responses", []), 1):
                    model = response.get("model", "Unknown")
                    provider = response.get("provider", "Unknown")
                    response_text = response.get("response", "")
                    time = response.get("response_time", 0)
                    quality = response.get("quality_score", None)

                    quality_str = (
                        f", Quality: {quality:.2f}" if quality is not None else ""
                    )
                    print(f"\n[{i}] {model} ({provider}, {time:.2f}s{quality_str}):")
                    print("-" * 40)
                    print(
                        response_text[:300]
                        + ("..." if len(response_text) > 300 else "")
                    )

                # Display meta-analyses
                if result.get("meta_analyses"):
                    print("\n--- Meta-Analyses ---")
                    for i, analysis in enumerate(result.get("meta_analyses", []), 1):
                        model = analysis.get("model", "Unknown")
                        provider = analysis.get("provider", "Unknown")
                        analysis_text = analysis.get("analysis", "")

                        print(f"\n[{i}] Analysis by {model} ({provider}):")
                        print("-" * 40)
                        print(
                            analysis_text[:300]
                            + ("..." if len(analysis_text) > 300 else "")
                        )

                # Display synthesis
                if result.get("synthesis"):
                    synthesis = result.get("synthesis", {})
                    model = synthesis.get("model", "Unknown")
                    provider = synthesis.get("provider", "Unknown")
                    response_text = synthesis.get("response", "")

                    print("\n--- Synthesized Response ---")
                    print(f"Synthesized by {model} ({provider}):")
                    print("-" * 40)
                    print(response_text)

                # Display selected response
                if result.get("selected_response"):
                    selected = result.get("selected_response", {})
                    model = selected.get("model", "Unknown")
                    provider = selected.get("provider", "Unknown")
                    quality = selected.get("quality_score", None)

                    quality_str = (
                        f", Quality: {quality:.2f}" if quality is not None else ""
                    )
                    print(
                        f"\n--- Selected Best Response: {model} ({provider}{quality_str}) ---"
                    )

                print("\n" + "=" * 80)

            except Exception as e:
                print(f"Error processing prompt: {str(e)}")

    except KeyboardInterrupt:
        print("\nExiting session...")

    print("Session ended.")


if __name__ == "__main__":
    asyncio.run(enhanced_interactive_session())
