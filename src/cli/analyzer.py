#!/usr/bin/env python3
"""
Command-line interface for the BaseOrchestrator.

This module provides a simple CLI for interacting with the BaseOrchestrator,
allowing users to send prompts to LLMs and configure models via command line.
"""

import argparse
import asyncio
import json
import logging
import os
import sys
from typing import List, Dict, Any

# Add src to path to enable imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.orchestration.config import OrchestratorConfig, ModelConfig, RequestConfig, LLMProvider
from src.orchestration.base_orchestrator import BaseOrchestrator


logger = logging.getLogger(__name__)


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Ultra LLM Analyzer CLI")
    
    parser.add_argument(
        "--prompt", "-p",
        type=str,
        help="Prompt to send to the LLM(s)"
    )
    
    parser.add_argument(
        "--models", "-m",
        type=str,
        default="mock:gpt-3.5-turbo",
        help="Comma-separated list of models to use in provider:model format"
    )
    
    parser.add_argument(
        "--primary", "-P",
        type=str,
        help="Primary model to use in provider:model format"
    )
    
    parser.add_argument(
        "--temperature", "-t",
        type=float,
        default=0.7,
        help="Temperature for generation (0.0 to 1.0)"
    )
    
    parser.add_argument(
        "--max-tokens", "-M",
        type=int,
        default=1000,
        help="Maximum tokens to generate"
    )
    
    parser.add_argument(
        "--parallel", "-x",
        action="store_true",
        help="Execute requests in parallel"
    )
    
    parser.add_argument(
        "--cache", "-c",
        action="store_true",
        help="Enable response caching"
    )
    
    parser.add_argument(
        "--output", "-o",
        type=str,
        help="Output file to write results to (JSON format)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Run in interactive mode"
    )
    
    return parser.parse_args()


def create_model_config(model_str: str, is_primary: bool = False, temperature: float = 0.7, max_tokens: int = 1000) -> ModelConfig:
    """
    Create a ModelConfig from a model string in provider:model format.
    
    Args:
        model_str: String in format "provider:model"
        is_primary: Whether this is the primary model
        temperature: Temperature for generation
        max_tokens: Maximum tokens to generate
        
    Returns:
        ModelConfig instance
    """
    parts = model_str.split(":")
    if len(parts) != 2:
        raise ValueError(f"Invalid model format: {model_str}. Expected format: provider:model")
    
    provider_str, model_id = parts
    
    try:
        provider = LLMProvider(provider_str.lower())
    except ValueError:
        logger.warning(f"Unknown provider: {provider_str}. Using CUSTOM instead.")
        provider = LLMProvider.CUSTOM
    
    # Get API keys from environment if available
    api_key = None
    if provider == LLMProvider.OPENAI:
        api_key = os.environ.get("OPENAI_API_KEY")
    elif provider == LLMProvider.ANTHROPIC:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
    elif provider == LLMProvider.GOOGLE:
        api_key = os.environ.get("GOOGLE_API_KEY")
    elif provider == LLMProvider.COHERE:
        api_key = os.environ.get("COHERE_API_KEY")
    elif provider == LLMProvider.MISTRAL:
        api_key = os.environ.get("MISTRAL_API_KEY")
    
    return ModelConfig(
        provider=provider,
        model_id=model_id,
        api_key=api_key,
        temperature=temperature,
        max_tokens=max_tokens,
        is_primary=is_primary
    )


def create_orchestrator_config(args) -> OrchestratorConfig:
    """
    Create an OrchestratorConfig from command line arguments.
    
    Args:
        args: Command line arguments
        
    Returns:
        OrchestratorConfig instance
    """
    models = []
    
    # Parse model list
    model_strs = args.models.split(",")
    for model_str in model_strs:
        models.append(create_model_config(
            model_str,
            is_primary=False,
            temperature=args.temperature,
            max_tokens=args.max_tokens
        ))
    
    # Set primary model if specified
    if args.primary:
        primary_found = False
        for model in models:
            model_str = f"{model.provider.value}:{model.model_id}"
            if model_str == args.primary:
                model.is_primary = True
                primary_found = True
                break
        
        if not primary_found:
            primary_model = create_model_config(
                args.primary,
                is_primary=True,
                temperature=args.temperature,
                max_tokens=args.max_tokens
            )
            models.append(primary_model)
    elif models:
        # Make the first model primary if none specified
        models[0].is_primary = True
    
    return OrchestratorConfig(
        models=models,
        cache_enabled=args.cache,
        parallel_execution=args.parallel,
        log_level="DEBUG" if args.verbose else "INFO"
    )


async def process_single_prompt(orchestrator: BaseOrchestrator, prompt: str) -> Dict[str, Any]:
    """
    Process a single prompt with the orchestrator.
    
    Args:
        orchestrator: BaseOrchestrator instance
        prompt: Prompt to process
        
    Returns:
        Dictionary with results
    """
    request = RequestConfig(prompt=prompt)
    response = await orchestrator.execute_request(request)
    return response.to_dict()


def print_response(response: Dict[str, Any], verbose: bool = False):
    """
    Print a response from the orchestrator.
    
    Args:
        response: Response dictionary
        verbose: Whether to print verbose output
    """
    print("\n" + "=" * 80)
    print("RESPONSE:")
    print("-" * 80)
    print(response["content"])
    print("-" * 80)
    
    if verbose:
        print("\nMETADATA:")
        print(f"Execution time: {response['metadata']['execution_time']:.2f} seconds")
        print(f"Models used: {', '.join(response['metadata']['models_used'])}")
        print(f"Successful models: {', '.join(response['metadata']['successful_models'])}")
        
        print("\nMODEL RESPONSES:")
        for model_key, model_response in response["model_responses"].items():
            print(f"\n{model_key}:")
            if "error" in model_response:
                print(f"ERROR: {model_response['error']}")
            else:
                print(f"Content: {model_response['content'][:100]}...")
    
    print("=" * 80 + "\n")


async def interactive_mode(orchestrator: BaseOrchestrator, args):
    """
    Run the CLI in interactive mode.
    
    Args:
        orchestrator: BaseOrchestrator instance
        args: Command line arguments
    """
    print("\nUltra LLM Analyzer Interactive Mode")
    print("Type 'exit' or 'quit' to exit, 'help' for help.")
    print(f"Using models: {', '.join(m.provider.value + ':' + m.model_id for m in orchestrator.config.models)}")
    
    while True:
        try:
            prompt = input("\nEnter prompt: ")
            if prompt.lower() in ["exit", "quit"]:
                break
            elif prompt.lower() == "help":
                print("\nCommands:")
                print("  help - Show this help message")
                print("  exit, quit - Exit the interactive mode")
                print("  models - Show available models")
                print("  use <provider:model> - Switch to a different model")
                print("  Any other input will be sent as a prompt to the LLM(s)")
                continue
            elif prompt.lower() == "models":
                print("\nAvailable models:")
                for model in orchestrator.get_available_models():
                    primary = " (PRIMARY)" if model["is_primary"] else ""
                    print(f"  {model['provider']}:{model['model_id']}{primary}")
                continue
            elif prompt.lower().startswith("use "):
                model_str = prompt[4:].strip()
                try:
                    model_config = create_model_config(
                        model_str,
                        is_primary=True,
                        temperature=args.temperature,
                        max_tokens=args.max_tokens
                    )
                    
                    # Reset primary flag on all existing models
                    for model in orchestrator.config.models:
                        model.is_primary = False
                    
                    # Add new model or update existing
                    found = False
                    for model in orchestrator.config.models:
                        if model.provider == model_config.provider and model.model_id == model_config.model_id:
                            model.is_primary = True
                            found = True
                            break
                    
                    if not found:
                        orchestrator.add_model(model_config)
                    
                    print(f"Set {model_str} as primary model")
                except Exception as e:
                    print(f"Error: {str(e)}")
                continue
            
            response = await process_single_prompt(orchestrator, prompt)
            print_response(response, args.verbose)
            
            # Save to output file if specified
            if args.output:
                try:
                    with open(args.output, "w") as f:
                        json.dump(response, f, indent=2)
                    print(f"Results saved to {args.output}")
                except Exception as e:
                    print(f"Error saving results: {str(e)}")
                    
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {str(e)}")


async def main_async():
    """Main async function for the CLI."""
    args = parse_args()
    
    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Create orchestrator config and instance
    config = create_orchestrator_config(args)
    orchestrator = BaseOrchestrator(config)
    
    # Display available models
    available_models = orchestrator.get_available_models()
    logger.info(f"Available models: {available_models}")
    
    if args.interactive:
        await interactive_mode(orchestrator, args)
    elif args.prompt:
        response = await process_single_prompt(orchestrator, args.prompt)
        print_response(response, args.verbose)
        
        # Save to output file if specified
        if args.output:
            try:
                with open(args.output, "w") as f:
                    json.dump(response, f, indent=2)
                logger.info(f"Results saved to {args.output}")
            except Exception as e:
                logger.error(f"Error saving results: {str(e)}")
    else:
        logger.error("No prompt provided. Use --prompt or --interactive")
        sys.exit(1)


def main():
    """Main entry point for the CLI."""
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()