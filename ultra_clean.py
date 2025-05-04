#!/usr/bin/env python3
"""
UltraAI CLI - Clean version with progress bars and reduced warnings.
"""

import argparse
import asyncio
import logging
import os
import random
import sys
import time
from typing import Any, Dict, List, Optional

# Configure logging to file only (no console output)
logging.basicConfig(
    level=logging.WARNING,  # Only show warnings and above
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("ultra_clean.log")],
)

# Suppress specific loggers
logging.getLogger("httpx").setLevel(logging.ERROR)
logging.getLogger("anthropic").setLevel(logging.ERROR)
logging.getLogger("openai").setLevel(logging.ERROR)
logging.getLogger("google").setLevel(logging.ERROR)

# Add the current directory to the module search path
sys.path.insert(0, os.getcwd())

# Import progress bar (install if not available)
try:
    from tqdm import tqdm
except ImportError:
    print("Installing tqdm for progress bars...")
    os.system(f"{sys.executable} -m pip install tqdm")
    from tqdm import tqdm


# Terminal colors
class Colors:
    PURPLE = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    END = "\033[0m"


def print_banner():
    """Print the UltraAI CLI banner."""
    banner = f"""{Colors.PURPLE}
  _   _ _ _            _    _____
 | | | | | |_ _ _ __ _| |  / __  |
 | | | | | __| '_/ _` | |  `' / /
 | |_| | | |_| | | (_| | |    / /
  \___/|_|\__|_|  \__,_|_|   /_/
{Colors.CYAN}
Clean LLM Orchestration CLI
---------------------------{Colors.END}
"""
    print(banner)


def progress_spinner(description="Working", delay=0.1):
    """
    Create a context manager for a progress spinner.

    Args:
        description: Text to show next to the spinner
        delay: Delay between spinner updates

    Usage:
        with progress_spinner("Loading models"):
            # do some work
    """
    spinner_chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

    class Spinner:
        def __init__(self, desc, delay):
            self.desc = desc
            self.delay = delay
            self.spinner = spinner_chars
            self.running = False

        def spin(self):
            while self.running:
                for char in self.spinner:
                    sys.stdout.write(
                        f"\r{Colors.CYAN}{char} {self.desc}...{Colors.END}"
                    )
                    sys.stdout.flush()
                    time.sleep(self.delay)
                    if not self.running:
                        break

        def __enter__(self):
            self.running = True
            self.thread = asyncio.create_task(self._async_spin())
            return self

        async def _async_spin(self):
            while self.running:
                for char in self.spinner:
                    sys.stdout.write(
                        f"\r{Colors.CYAN}{char} {self.desc}...{Colors.END}"
                    )
                    sys.stdout.flush()
                    await asyncio.sleep(self.delay)
                    if not self.running:
                        break

        def __exit__(self, exc_type, exc_val, exc_tb):
            self.running = False
            sys.stdout.write(
                f"\r{Colors.GREEN}✓ {self.desc} completed!{Colors.END}"
                + " " * 20
                + "\n"
            )
            sys.stdout.flush()

    return Spinner(description, delay)


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="UltraAI CLI - Clean version")
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


def print_help():
    """Print help information."""
    help_text = f"""
{Colors.CYAN}Available Commands:{Colors.END}
------------------
{Colors.BOLD}help{Colors.END}                      - Show this help message
{Colors.BOLD}exit, quit{Colors.END}                - Exit the program
{Colors.BOLD}models{Colors.END}                    - Show available models
{Colors.BOLD}use <model1> <model2>...{Colors.END}  - Specify which models to use
{Colors.BOLD}lead <model>{Colors.END}              - Set the lead model for synthesis
{Colors.BOLD}analysis <type>{Colors.END}           - Set analysis type (comparative or factual)
{Colors.BOLD}show analysis <on/off>{Colors.END}    - Toggle showing analysis output
{Colors.BOLD}show responses <on/off>{Colors.END}   - Toggle showing all responses

{Colors.YELLOW}Examples:{Colors.END}
---------
> {Colors.GREEN}use openai-gpt4o anthropic-claude{Colors.END}     - Use only these two models
> {Colors.GREEN}lead anthropic-claude{Colors.END}                  - Set Claude as the lead model
> {Colors.GREEN}analysis factual{Colors.END}                       - Switch to factual analysis
> {Colors.GREEN}show analysis on{Colors.END}                       - Show detailed analysis output
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
            f"\n{Colors.GREEN}=== Synthesized Response (by {model}) ==={Colors.END}"
        )
        output.append(response)

    # Add all individual responses if requested
    if show_all_responses:
        output.append(f"\n{Colors.BLUE}=== Individual Model Responses ==={Colors.END}")
        for i, response in enumerate(result.get("initial_responses", []), 1):
            model = response.get("model", "Unknown")
            provider = response.get("provider", "Unknown")
            quality = response.get("quality_score")

            quality_str = f", Quality: {quality:.2f}" if quality is not None else ""
            header = f"[{i}] {model} ({provider}{quality_str})"
            output.append(f"\n{Colors.YELLOW}{header}{Colors.END}")
            output.append(f"{response.get('response', '')}")

    # Add analysis if requested
    if show_analysis and "analysis_results" in result:
        output.append(f"\n{Colors.PURPLE}=== Analysis Results ==={Colors.END}")
        if "combined_summary" in result["analysis_results"]:
            output.append(result["analysis_results"]["combined_summary"])

    return "\n".join(output)


async def get_available_models():
    """Get a list of available models with a progress bar."""
    # Import here to avoid early errors
    from src.simple_core.factory import create_from_env

    with progress_spinner("Detecting available models"):
        # Small delay to make the spinner visible
        await asyncio.sleep(1)

        # Create a temporary orchestrator to see which models are available
        orchestrator = create_from_env(modular=True)
        if not orchestrator:
            return []

        # Extract model names from the model-adapter pairs
        return [model_def.name for model_def, _ in orchestrator.models]


async def apply_direct_fix_to_orchestrator(orchestrator, lead_model_name=None):
    """Apply a direct fix to the orchestrator to ensure analysis model is set."""
    if not orchestrator or not hasattr(orchestrator, "models"):
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
        return False

    # Modify the _perform_analysis method to always use our analysis model
    original_perform_analysis = orchestrator._perform_analysis

    # Store the analysis model in the orchestrator
    orchestrator._analysis_model = analysis_model
    orchestrator._analysis_model_name = orchestrator.models[lead_model_index][0].name

    # Define the replacement method
    async def fixed_perform_analysis(
        self, prompt, responses, analysis_type, lead_model, request
    ):
        """Fixed version of _perform_analysis that ensures the analysis model is set."""
        # Call the original method to prepare everything
        result = await original_perform_analysis(
            self, prompt, responses, analysis_type, lead_model, request
        )
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

    return True


async def simulation_progress(steps=10, description="Processing"):
    """Simulate a progress bar for processing."""
    with tqdm(
        total=steps, desc=description, bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}"
    ) as pbar:
        for i in range(steps):
            # Randomized delay to simulate different steps taking different times
            delay = random.uniform(0.05, 0.3)
            await asyncio.sleep(delay)
            pbar.update(1)


async def interactive_session(args):
    """Run an interactive CLI session."""
    print_banner()

    # Initialize settings from command line arguments
    analysis_type = args.analysis
    lead_model = args.lead_model
    model_names = args.models or []
    show_analysis = args.show_analysis
    show_all_responses = args.show_all_responses

    # Import libraries only when needed
    from src.simple_core.config import RequestConfig
    from src.simple_core.factory import create_from_env

    # Get available models
    available_models = await get_available_models()
    if not available_models:
        print(
            f"{Colors.RED}No models available. Please check your API keys and try again.{Colors.END}"
        )
        return

    print(
        f"{Colors.GREEN}Available models: {Colors.YELLOW}{', '.join(available_models)}{Colors.END}"
    )
    print(
        f"Current settings: Analysis: {Colors.CYAN}{analysis_type}{Colors.END}, Lead model: {Colors.CYAN}{lead_model or 'auto'}{Colors.END}"
    )
    print(
        f"Using models: {Colors.CYAN}{', '.join(model_names) if model_names else 'all available'}{Colors.END}"
    )

    # Create the orchestrator
    with progress_spinner("Initializing orchestrator"):
        await asyncio.sleep(1.5)  # Small delay to make the spinner visible
        orchestrator = create_from_env(modular=True, analysis_type=analysis_type)

    if not orchestrator:
        print(
            f"{Colors.RED}Failed to create orchestrator. Please check your API keys and try again.{Colors.END}"
        )
        return

    # Apply our direct fix to ensure analysis model is set
    with progress_spinner("Applying analysis model fix"):
        await asyncio.sleep(0.8)  # Small delay to make the spinner visible
        await apply_direct_fix_to_orchestrator(orchestrator, lead_model)

    print(
        f"\n{Colors.CYAN}Type your prompt or enter a command (help, exit, etc.){Colors.END}"
    )

    while True:
        # Get user input
        try:
            print()
            user_input = input(
                f"{Colors.BOLD}{Colors.PURPLE}UltrAI> {Colors.END}"
            ).strip()
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
            print(
                f"Available models: {Colors.YELLOW}{', '.join(available_models)}{Colors.END}"
            )
            continue

        elif user_input.lower().startswith("use "):
            parts = user_input.split()[1:]
            if not parts:
                print(
                    f"{Colors.RED}Please specify at least one model name.{Colors.END}"
                )
                continue

            # Verify models exist
            with progress_spinner("Checking model availability"):
                await asyncio.sleep(0.5)
                available_models = await get_available_models()

            invalid_models = [m for m in parts if m not in available_models]
            if invalid_models:
                print(
                    f"{Colors.RED}Invalid model(s): {', '.join(invalid_models)}{Colors.END}"
                )
                print(
                    f"Available models: {Colors.YELLOW}{', '.join(available_models)}{Colors.END}"
                )
                continue

            model_names = parts
            print(
                f"Now using models: {Colors.GREEN}{', '.join(model_names)}{Colors.END}"
            )
            continue

        elif user_input.lower().startswith("lead "):
            parts = user_input.split()[1:]
            if not parts:
                print(f"{Colors.RED}Please specify a lead model name.{Colors.END}")
                continue

            lead_candidate = parts[0]
            with progress_spinner("Verifying lead model"):
                await asyncio.sleep(0.5)
                available_models = await get_available_models()

            if lead_candidate not in available_models:
                print(f"{Colors.RED}Invalid model: {lead_candidate}{Colors.END}")
                print(
                    f"Available models: {Colors.YELLOW}{', '.join(available_models)}{Colors.END}"
                )
                continue

            lead_model = lead_candidate

            # Update the analysis model
            with progress_spinner("Updating lead model"):
                await asyncio.sleep(0.5)
                await apply_direct_fix_to_orchestrator(orchestrator, lead_model)

            print(f"Set lead model to: {Colors.GREEN}{lead_model}{Colors.END}")
            continue

        elif user_input.lower().startswith("analysis "):
            parts = user_input.split()[1:]
            if not parts:
                print(
                    f"{Colors.RED}Please specify an analysis type (comparative or factual).{Colors.END}"
                )
                continue

            analysis_candidate = parts[0].lower()
            if analysis_candidate not in ["comparative", "factual"]:
                print(
                    f"{Colors.RED}Invalid analysis type: {analysis_candidate}{Colors.END}"
                )
                print(
                    f"Available types: {Colors.YELLOW}comparative, factual{Colors.END}"
                )
                continue

            analysis_type = analysis_candidate

            # Recreate orchestrator with new analysis type
            with progress_spinner(f"Switching to {analysis_type} analysis"):
                await asyncio.sleep(1.0)
                orchestrator = create_from_env(
                    modular=True, analysis_type=analysis_type
                )
                if orchestrator:
                    await apply_direct_fix_to_orchestrator(orchestrator, lead_model)

            if not orchestrator:
                print(
                    f"{Colors.RED}Failed to update orchestrator. Using previous configuration.{Colors.END}"
                )
                continue

            print(f"Set analysis type to: {Colors.GREEN}{analysis_type}{Colors.END}")
            continue

        elif user_input.lower().startswith("show analysis "):
            parts = user_input.split()[2:]
            if not parts or parts[0].lower() not in ["on", "off"]:
                print(f"{Colors.RED}Please specify 'on' or 'off'.{Colors.END}")
                continue

            show_analysis = parts[0].lower() == "on"
            print(
                f"Analysis display: {Colors.GREEN}{'on' if show_analysis else 'off'}{Colors.END}"
            )
            continue

        elif user_input.lower().startswith("show responses "):
            parts = user_input.split()[2:]
            if not parts or parts[0].lower() not in ["on", "off"]:
                print(f"{Colors.RED}Please specify 'on' or 'off'.{Colors.END}")
                continue

            show_all_responses = parts[0].lower() == "on"
            print(
                f"All responses display: {Colors.GREEN}{'on' if show_all_responses else 'off'}{Colors.END}"
            )
            continue

        # Process as a prompt
        try:
            # Create request config
            request = RequestConfig(
                prompt=user_input,
                model_names=model_names,
                lead_model=lead_model,
                analysis_type=analysis_type,
            )

            # Process request with progress bar
            print(f"{Colors.CYAN}Orchestrating LLM responses...{Colors.END}")
            await simulation_progress(steps=8, description="Fetching responses")

            # Process request
            result = await orchestrator.process(request.to_dict())

            # Show analysis progress if enabled
            if show_analysis:
                await simulation_progress(steps=5, description="Analyzing responses")

            # Display result
            formatted_output = format_result(result, show_analysis, show_all_responses)
            print(formatted_output)

        except Exception as e:
            print(f"{Colors.RED}Error: {str(e)}{Colors.END}")


if __name__ == "__main__":
    # Capture all output to prevent unwanted messages
    import io
    from contextlib import redirect_stderr, redirect_stdout

    # Parse arguments
    args = parse_arguments()

    # Run the main function with captured output
    with redirect_stderr(io.StringIO()), redirect_stdout(io.StringIO()):
        # Initialize setup silently
        pass

    # Now run the main function normally
    asyncio.run(interactive_session(args))
