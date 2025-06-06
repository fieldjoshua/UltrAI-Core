#!/usr/bin/env python3
"""
Command-line test runner for the Ultra orchestration system.
This script allows running the orchestrator from the command line with specific parameters.
"""

import argparse
import json
import os
import sys
from typing import Any, Dict, List, Optional

# Add the parent directory to the path if needed
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.adapters.adapter_factory import get_adapter_names
from src.orchestration.simple_orchestrator import Orchestrator


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Test the Ultra orchestration system")

    parser.add_argument(
        "--prompt", type=str, required=True, help="The prompt to send to the LLMs"
    )

    parser.add_argument(
        "--models", type=str, default=None, help="Comma-separated list of models to use"
    )

    parser.add_argument(
        "--lead",
        type=str,
        default=None,
        help="Lead model for synthesis (must be in the models list)",
    )

    parser.add_argument(
        "--analysis",
        type=str,
        default="comparative",
        choices=["comparative", "factual"],
        help="Type of analysis to perform",
    )

    parser.add_argument(
        "--output",
        type=str,
        default="text",
        choices=["text", "json"],
        help="Output format",
    )

    parser.add_argument(
        "--mock",
        action="store_true",
        help="Force mock mode regardless of environment setting",
    )

    return parser.parse_args()


def print_json_result(result: Dict[str, Any]):
    """Print the result in JSON format."""
    print(json.dumps(result, indent=2))


def print_text_result(result: Dict[str, Any], lead_model: str):
    """Print the result in human-readable text format."""
    # Initial responses
    print("\n" + "=" * 80)
    print(" " * 30 + "INITIAL RESPONSES" + " " * 30)
    print("=" * 80)

    for model_response in result.get("initial_responses", []):
        model_name = model_response.get("model", "Unknown")
        provider = model_response.get("provider", "Unknown")
        response_text = model_response.get("response", "No response available")

        leader_mark = " (LEAD)" if model_name == lead_model else ""
        print(f"\n{model_name}{leader_mark} ({provider}):")
        print("-" * 80)
        print(response_text)

    # Analysis results
    analysis = result.get("analysis_results", {})
    if analysis:
        print("\n" + "=" * 80)
        print(
            " " * 30
            + f"ANALYSIS ({analysis.get('type', 'Unknown').upper()})"
            + " " * 30
        )
        print("=" * 80)

        if "combined_summary" in analysis:
            print(analysis["combined_summary"])

    # Synthesis
    synthesis = result.get("synthesis", {})
    if synthesis:
        print("\n" + "=" * 80)
        print(" " * 32 + "SYNTHESIS" + " " * 32)
        print("=" * 80)

        model = synthesis.get("model", "Unknown")
        provider = synthesis.get("provider", "Unknown")
        print(f"Synthesized by: {model} ({provider})\n")
        print(synthesis.get("response", "No synthesis available"))


def main():
    """Main function to run the test."""
    args = parse_arguments()

    # Override mock mode if specified
    if args.mock:
        os.environ["USE_MOCK"] = "true"
        print("Mock mode enabled via command line")

    # Parse models
    models = []
    if args.models:
        models = [model.strip() for model in args.models.split(",")]

    # If no models specified, use all available
    if not models:
        models = get_adapter_names()
        print(f"No models specified, using all available: {', '.join(models)}")

    # Set lead model
    lead_model = args.lead
    if not lead_model and models:
        lead_model = models[0]
        print(f"No lead model specified, using: {lead_model}")

    if lead_model and lead_model not in models:
        print(f"Warning: Lead model {lead_model} not in models list. Adding it.")
        models.append(lead_model)

    # Print run information
    print(f"Running {args.analysis} analysis with prompt: '{args.prompt}'")
    print(f"Using models: {', '.join(models)}")
    print(f"Lead model: {lead_model}")

    try:
        # Initialize orchestrator
        orchestrator = Orchestrator(
            models=models, lead_model=lead_model, analysis_type=args.analysis
        )

        # Process the request
        result = orchestrator.process(args.prompt)

        # Display results in the requested format
        if args.output == "json":
            print_json_result(result)
        else:
            print_text_result(result, lead_model)

    except Exception as e:
        print(f"Error: {str(e)}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
