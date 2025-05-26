#!/usr/bin/env python3
"""
Direct Analysis Fix for UltraAI CLI

This script runs the UltraAI CLI with a direct fix for the missing analysis model.
"""

import argparse
import asyncio
import logging
import os
import sys
from typing import Any, Dict, List, Optional

# Add the current directory to the module search path
sys.path.insert(0, os.getcwd())

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("ultra_cli_fixed.log"), logging.StreamHandler()],
)

# Set lower log level for some noisy modules
logging.getLogger("httpx").setLevel(logging.WARNING)

from src.simple_core.adapter import Adapter
from src.simple_core.config import ModelDefinition, RequestConfig

# Import after configuring logging
from src.simple_core.factory import create_from_env


def print_banner():
    """Print the UltraAI CLI banner."""
    banner = r"""
  _   _ _ _            _    _____
 | | | | | |_ _ _ __ _| |  / __  |
 | | | | | __| '_/ _` | |  `' / /
 | |_| | | |_| | | (_| | |    / /
  \___/|_|\__|_|  \__,_|_|   /_/

Real-time LLM Orchestration CLI (Fixed Analysis)
------------------------------------------------
Type 'help' for commands, 'exit' to quit
    """
    print(banner)


async def get_available_models():
    """Get a list of available models."""
    # Create a temporary orchestrator to see which models are available
    orchestrator = create_from_env(modular=True)
    if not orchestrator:
        return []

    # Extract model names from the model-adapter pairs
    return [model_def.name for model_def, _ in orchestrator.models]


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="UltraAI CLI for real-time LLM orchestration (with fixed analysis)"
    )
    parser.add_argument(
        "--analysis",
        choices=["comparative", "factual"],
        default="comparative",
        help="Type of analysis to use (default: comparative)",
    )
    parser.add_argument(
        "--lead-model",
        help="Name of the model to use as lead (default: highest priority)",
    )
    parser.add_argument(
        "--models", nargs="+", help="List of models to use (default: all available)"
    )
    parser.add_argument(
        "--show-analysis", action="store_true", help="Show detailed analysis output"
    )
    parser.add_argument(
        "--show-all-responses",
        action="store_true",
        help="Show all model responses, not just the synthesis",
    )
    return parser.parse_args()


def color_text(text, color):
    """Add color to terminal text."""
    colors = {
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "magenta": "\033[95m",
        "cyan": "\033[96m",
        "white": "\033[97m",
        "reset": "\033[0m",
    }
    return f"{colors.get(color, '')}{text}{colors['reset']}"


def print_help():
    """Print help information."""
    help_text = """
Available Commands:
------------------
help                      - Show this help message
exit, quit                - Exit the program
models                    - Show available models
use <model1> <model2>...  - Specify which models to use
lead <model>              - Set the lead model for synthesis
analysis <type>           - Set analysis type (comparative or factual)
show analysis <on/off>    - Toggle showing analysis output
show responses <on/off>   - Toggle showing all responses

Examples:
---------
> use openai-gpt4o anthropic-claude     - Use only these two models
> lead anthropic-claude                  - Set Claude as the lead model
> analysis factual                       - Switch to factual analysis
> show analysis on                       - Show detailed analysis output
    """
    print(help_text)


def format_result(result, show_analysis, show_all_responses):
    """Format the result for display."""
    output = []

    # Add synthesis result (always shown)
    if "synthesis" in result and "response" in result["synthesis"]:
        model = result["synthesis"]["model"]
        provider = result["synthesis"]["provider"]
        response = result["synthesis"]["response"]

        output.append(
            color_text(f"\n=== Synthesized Response (by {model}) ===", "green")
        )
        output.append(response)

    # Add all individual responses if requested
    if show_all_responses:
        output.append(color_text("\n=== Individual Model Responses ===", "blue"))
        for i, response in enumerate(result.get("initial_responses", []), 1):
            model = response.get("model", "Unknown")
            provider = response.get("provider", "Unknown")
            quality = response.get("quality_score")

            quality_str = f", Quality: {quality:.2f}" if quality is not None else ""
            header = f"[{i}] {model} ({provider}{quality_str})"
            output.append(color_text(f"\n{header}", "yellow"))
            output.append(f"{response.get('response', '')}")

    # Add analysis if requested
    if show_analysis and "analysis_results" in result:
        output.append(color_text("\n=== Analysis Results ===", "magenta"))
        if "combined_summary" in result["analysis_results"]:
            output.append(result["analysis_results"]["combined_summary"])

    return "\n".join(output)


async def apply_direct_fix_to_orchestrator(orchestrator, lead_model_name=None):
    """Apply a direct fix to the orchestrator to ensure analysis model is set."""
    if not orchestrator or not hasattr(orchestrator, "models"):
        logging.error("Invalid orchestrator, cannot apply fix")
        return False

    # Find the appropriate model for analysis
    analysis_model = None
    lead_model_index = 0

    if lead_model_name:
        # Find the specified lead model
        for i, (model_def, adapter) in enumerate(orchestrator.models):
            if model_def.name == lead_model_name:
                analysis_model = adapter
                lead_model_index = i
                break

    # If no lead model specified or not found, use the highest priority model
    if not analysis_model and orchestrator.models:
        analysis_model = orchestrator.models[0][1]  # Use the first model's adapter

    if not analysis_model:
        logging.error("No suitable analysis model found")
        return False

    # Modify the _perform_analysis method to always use our analysis model
    original_perform_analysis = orchestrator._perform_analysis

    # Store the analysis model in the orchestrator
    orchestrator._analysis_model = analysis_model
    orchestrator._analysis_model_name = orchestrator.models[lead_model_index][0].name
    logging.info(f"Setting analysis model to: {orchestrator._analysis_model_name}")

    # Define the replacement method
    async def fixed_perform_analysis(
        self, prompt, responses, analysis_type, lead_model, request
    ):
        """Fixed version of _perform_analysis that ensures the analysis model is set."""
        # Call the original method to prepare everything
        result = await original_perform_analysis(
            self, prompt, responses, analysis_type, lead_model, request
        )

        # Ensure each module's options include the analysis model
        if "individual_results" in result and isinstance(
            result["individual_results"], dict
        ):
            model_name = getattr(self, "_analysis_model_name", lead_model[0].name)
            logging.info(f"Analysis performed using model: {model_name}")

        return result

    # Apply our custom method
    orchestrator._perform_analysis = fixed_perform_analysis.__get__(orchestrator)

    # Patch the modules directly
    if hasattr(orchestrator, "analysis_manager") and hasattr(
        orchestrator.analysis_manager, "modules"
    ):
        for module_name, module in orchestrator.analysis_manager.modules.items():
            original_analyze = module.analyze

            # Create a new analyze method that automatically adds the analysis model
            async def patched_analyze(self, prompt, responses, options=None):
                options = options or {}
                # Ensure the analysis model is set
                if not options.get("analysis_model"):
                    options["analysis_model"] = orchestrator._analysis_model
                return await original_analyze(prompt, responses, options)

            # Apply our patch to the module
            module.analyze = patched_analyze.__get__(module)
            logging.info(f"Patched {module_name} module to use fixed analysis model")

    return True


async def interactive_session(args):
    """Run an interactive CLI session."""
    print_banner()

    # Initialize settings from command line arguments
    analysis_type = args.analysis
    lead_model = args.lead_model
    model_names = args.models or []
    show_analysis = args.show_analysis
    show_all_responses = args.show_all_responses

    # Get available models
    available_models = await get_available_models()
    if not available_models:
        print("No models available. Please check your API keys and try again.")
        return

    print(f"Available models: {', '.join(available_models)}")
    print(
        f"Current settings: Analysis: {analysis_type}, Lead model: {lead_model or 'auto'}"
    )
    print(f"Using models: {', '.join(model_names) if model_names else 'all available'}")
    print("Type your prompt or enter a command (help, exit, etc.)")

    # Create the orchestrator
    orchestrator = create_from_env(modular=True, analysis_type=analysis_type)
    if not orchestrator:
        print("Failed to create orchestrator. Please check API keys and try again.")
        return

    # Apply our direct fix to ensure analysis model is set
    fix_applied = await apply_direct_fix_to_orchestrator(orchestrator, lead_model)
    if fix_applied:
        print(color_text("✓ Analysis model fix applied successfully", "green"))
    else:
        print(color_text("✗ Failed to apply analysis model fix", "red"))

    while True:
        # Get user input
        try:
            print()
            user_input = input(color_text("UltrAI> ", "cyan")).strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting...")
            break

        if not user_input:
            continue

        # Process commands
        if user_input.lower() in ["exit", "quit"]:
            break

        elif user_input.lower() == "help":
            print_help()
            continue

        elif user_input.lower() == "models":
            available_models = await get_available_models()
            print(f"Available models: {', '.join(available_models)}")
            continue

        elif user_input.lower().startswith("use "):
            parts = user_input.split()[1:]
            if not parts:
                print("Please specify at least one model name.")
                continue

            # Verify models exist
            available_models = await get_available_models()
            invalid_models = [m for m in parts if m not in available_models]
            if invalid_models:
                print(f"Invalid model(s): {', '.join(invalid_models)}")
                print(f"Available models: {', '.join(available_models)}")
                continue

            model_names = parts
            print(f"Now using models: {', '.join(model_names)}")
            continue

        elif user_input.lower().startswith("lead "):
            parts = user_input.split()[1:]
            if not parts:
                print("Please specify a lead model name.")
                continue

            lead_candidate = parts[0]
            available_models = await get_available_models()
            if lead_candidate not in available_models:
                print(f"Invalid model: {lead_candidate}")
                print(f"Available models: {', '.join(available_models)}")
                continue

            lead_model = lead_candidate
            print(f"Set lead model to: {lead_model}")

            # Update the analysis model
            fix_applied = await apply_direct_fix_to_orchestrator(
                orchestrator, lead_model
            )
            if fix_applied:
                print(color_text("✓ Analysis model updated", "green"))

            continue

        elif user_input.lower().startswith("analysis "):
            parts = user_input.split()[1:]
            if not parts:
                print("Please specify an analysis type (comparative or factual).")
                continue

            analysis_candidate = parts[0].lower()
            if analysis_candidate not in ["comparative", "factual"]:
                print(f"Invalid analysis type: {analysis_candidate}")
                print("Available types: comparative, factual")
                continue

            analysis_type = analysis_candidate

            # Recreate orchestrator with new analysis type
            orchestrator = create_from_env(modular=True, analysis_type=analysis_type)
            if not orchestrator:
                print("Failed to update orchestrator. Using previous configuration.")
                continue

            # Apply our fix to the new orchestrator
            fix_applied = await apply_direct_fix_to_orchestrator(
                orchestrator, lead_model
            )
            if fix_applied:
                print(
                    color_text(
                        "✓ Analysis model fix applied to new orchestrator", "green"
                    )
                )

            print(f"Set analysis type to: {analysis_type}")
            continue

        elif user_input.lower().startswith("show analysis "):
            parts = user_input.split()[2:]
            if not parts or parts[0].lower() not in ["on", "off"]:
                print("Please specify 'on' or 'off'.")
                continue

            show_analysis = parts[0].lower() == "on"
            print(f"Analysis display: {'on' if show_analysis else 'off'}")
            continue

        elif user_input.lower().startswith("show responses "):
            parts = user_input.split()[2:]
            if not parts or parts[0].lower() not in ["on", "off"]:
                print("Please specify 'on' or 'off'.")
                continue

            show_all_responses = parts[0].lower() == "on"
            print(f"All responses display: {'on' if show_all_responses else 'off'}")
            continue

        # Process as a prompt
        print(color_text("Processing...", "yellow"))

        try:
            # Create request config
            request = RequestConfig(
                prompt=user_input,
                model_names=model_names,
                lead_model=lead_model,
                analysis_type=analysis_type,
            )

            # Process request
            result = await orchestrator.process(request.to_dict())

            # Display result
            formatted_output = format_result(result, show_analysis, show_all_responses)
            print(formatted_output)

        except Exception as e:
            print(color_text(f"Error: {str(e)}", "red"))


if __name__ == "__main__":
    args = parse_arguments()
    asyncio.run(interactive_session(args))
