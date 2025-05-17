#!/usr/bin/env python3
"""
Menu-based CLI for the Ultra orchestration system.
This provides a simple terminal interface for interacting with the LLM orchestration functionality.
"""

import os
import sys
import time
from typing import Any, Dict, List, Optional

# Add the parent directory to the path if needed
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.adapters.adapter_factory import create_adapter, get_adapter_names
from src.orchestration.simple_orchestrator import Orchestrator


def clear_screen():
    """Clear the terminal screen."""
    os.system("cls" if os.name == "nt" else "clear")


def print_header():
    """Print the application header."""
    print("\n")
    print("=" * 80)
    print(" " * 25 + "ULTRA ORCHESTRATION SYSTEM" + " " * 25)
    print("=" * 80)
    print("\n")


def print_menu():
    """Print the main menu options."""
    print("\nMAIN MENU:")
    print("1. Run Comparative Analysis")
    print("2. Run Factual Analysis")
    print("3. Configure Settings")
    print("4. View Available Models")
    print("5. Exit")
    print()


def get_available_models() -> List[str]:
    """Get a list of available LLM models."""
    return get_adapter_names()


def display_models():
    """Display the available models."""
    models = get_available_models()

    print("\nAvailable Models:")
    print("-" * 50)

    for i, model in enumerate(models, 1):
        print(f"{i}. {model}")

    print("\nPress Enter to continue...")
    input()


def select_models() -> List[str]:
    """Let the user select which models to use."""
    available_models = get_available_models()
    selected_models = []

    print("\nSelect Models to Use:")
    print("-" * 50)

    for i, model in enumerate(available_models, 1):
        print(f"{i}. {model}")

    print(
        "\nEnter model numbers separated by commas (e.g., 1,3,4) or 'all' for all models:"
    )

    selection = input("> ").strip().lower()

    if selection == "all":
        return available_models

    try:
        indices = [int(idx.strip()) - 1 for idx in selection.split(",")]
        for idx in indices:
            if 0 <= idx < len(available_models):
                selected_models.append(available_models[idx])
    except ValueError:
        print("Invalid input. Using default model.")
        # Use the first model as default
        if available_models:
            selected_models = [available_models[0]]

    if not selected_models and available_models:
        print("No valid models selected. Using default model.")
        selected_models = [available_models[0]]

    return selected_models


def run_analysis(analysis_type: str):
    """Run the specified type of analysis with user input."""
    clear_screen()
    print_header()
    print(f"\nRunning {analysis_type.title()} Analysis")
    print("-" * 50)

    # Get models
    models = select_models()

    # Get prompt
    print("\nEnter your prompt:")
    prompt = input("> ").strip()

    if not prompt:
        print("Empty prompt. Returning to main menu...")
        time.sleep(2)
        return

    # Get lead model
    lead_model = None
    if len(models) > 1:
        print("\nSelect lead model:")
        for i, model in enumerate(models, 1):
            print(f"{i}. {model}")

        try:
            lead_idx = int(input("> ").strip()) - 1
            if 0 <= lead_idx < len(models):
                lead_model = models[lead_idx]
        except ValueError:
            lead_model = models[0]
            print(f"Invalid input. Using {lead_model} as lead model.")
    else:
        lead_model = models[0]

    print("\nProcessing request...\n")

    # Initialize orchestrator
    try:
        orchestrator = Orchestrator(
            models=models, lead_model=lead_model, analysis_type=analysis_type
        )

        # Process the request
        result = orchestrator.process(prompt)

        # Display results
        print("\nResults:")
        print("-" * 50)

        # Initial responses
        print("\nInitial Responses:")
        for model_name, response in result.get("initial_responses", {}).items():
            model_display = model_name
            if model_name == lead_model:
                model_display += " (Lead)"

            print(f"\n{model_display}:")
            print("-" * len(model_display))
            print(response.get("response", "No response available"))

        # Analysis results
        print("\nAnalysis Results:")
        print("-" * 50)
        analysis = result.get("analysis_results", {})
        if analysis:
            print(analysis.get("summary", "No analysis available"))

        # Synthesis
        synthesis = result.get("synthesis", {})
        if synthesis:
            print("\nSynthesized Response:")
            print("-" * 50)
            print(synthesis.get("response", "No synthesis available"))

    except Exception as e:
        print(f"\nError: {str(e)}")

    print("\nPress Enter to continue...")
    input()


def configure_settings():
    """Configure application settings."""
    clear_screen()
    print_header()
    print("\nConfigure Settings")
    print("-" * 50)

    print("\nCurrent Settings:")
    print(f"1. Mock Mode: {os.environ.get('USE_MOCK', 'true')}")
    print(f"2. Log Level: {os.environ.get('LOG_LEVEL', 'info')}")

    print("\nSelect a setting to change (or 0 to return):")

    try:
        choice = int(input("> ").strip())

        if choice == 1:
            current = os.environ.get("USE_MOCK", "true").lower()
            new_value = "false" if current == "true" else "true"
            os.environ["USE_MOCK"] = new_value
            print(f"Mock Mode set to: {new_value}")

        elif choice == 2:
            print("\nSelect Log Level:")
            print("1. debug")
            print("2. info")
            print("3. warning")
            print("4. error")

            log_choice = int(input("> ").strip())
            levels = ["debug", "info", "warning", "error"]

            if 1 <= log_choice <= 4:
                os.environ["LOG_LEVEL"] = levels[log_choice - 1]
                print(f"Log Level set to: {levels[log_choice - 1]}")

    except ValueError:
        print("Invalid input.")

    print("\nPress Enter to continue...")
    input()


def main():
    """Main application loop."""
    while True:
        clear_screen()
        print_header()
        print_menu()

        try:
            choice = input("Enter your choice (1-5): ").strip()

            if choice == "1":
                run_analysis("comparative")
            elif choice == "2":
                run_analysis("factual")
            elif choice == "3":
                configure_settings()
            elif choice == "4":
                display_models()
            elif choice == "5":
                print("\nExiting Ultra Orchestration System. Goodbye!")
                break
            else:
                print("\nInvalid choice. Please try again.")
                time.sleep(1)

        except Exception as e:
            print(f"\nAn error occurred: {str(e)}")
            print("Press Enter to continue...")
            input()


if __name__ == "__main__":
    main()
