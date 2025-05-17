#!/usr/bin/env python3
"""
Test script to verify connections to all supported LLM APIs.
Run this script to check if your API keys are correctly configured and the LLM APIs are accessible.
"""

import asyncio
import os
import sys
import time
from pathlib import Path

# Add the project root to the Python path for imports
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))

try:
    from dotenv import load_dotenv

    from src.core.ultra_llm import UltraLLM
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print(
        "Make sure you've installed all requirements with: pip install -r requirements.txt"
    )
    sys.exit(1)


async def test_connections():
    """Test connections to all configured LLM APIs"""
    print("\n=== Ultra LLM Connection Test ===\n")

    # Load environment variables from .env file
    load_dotenv()
    print("Loaded environment variables")

    # Get API keys from environment
    api_keys = {
        "openai": os.getenv("OPENAI_API_KEY"),
        "anthropic": os.getenv("ANTHROPIC_API_KEY"),
        "google": os.getenv("GOOGLE_API_KEY"),
        "mistral": os.getenv("MISTRAL_API_KEY"),
        "llama": os.getenv("LLAMA_API_KEY"),
    }

    # Check which API keys are configured
    configured_apis = [api for api, key in api_keys.items() if key]
    missing_apis = [api for api, key in api_keys.items() if not key]

    print(
        f"Configured APIs: {', '.join(configured_apis) if configured_apis else 'None'}"
    )
    if missing_apis:
        print(f"Missing API keys: {', '.join(missing_apis)}")

    # Create UltraLLM instance with all features enabled
    llm = UltraLLM(
        api_keys=api_keys,
        enabled_features=[
            "openai",
            "anthropic",
            "gemini",
            "mistral",
            "ollama",
            "llama",
        ],
    )

    # Initialize clients
    print("\nInitializing LLM clients...")
    llm._initialize_clients()

    # Print available models
    print(
        f"\nAvailable models: {', '.join(llm.available_models) if llm.available_models else 'None'}"
    )

    if not llm.available_models:
        print(
            "\nNo models available. Please check your API keys and internet connection."
        )
        return

    # Test a simple prompt with each available model
    test_prompt = "What is the capital of France? Please answer in one sentence."

    print("\n=== Testing each LLM with a simple prompt ===")
    print(f'Prompt: "{test_prompt}"\n')

    for model in llm.available_models:
        print(f"\n--- Testing {model} ---")
        try:
            start_time = time.time()

            if model == "openai":
                response = await llm.get_chatgpt_response(test_prompt)
            elif model == "anthropic":
                response = await llm.get_claude_response(test_prompt)
            elif model == "gemini":
                response = await llm.get_gemini_response(test_prompt)
            elif model == "mistral":
                response = await llm.get_mistral_response(test_prompt)
            elif model == "ollama":
                response = await llm.call_ollama(test_prompt)
            elif model == "llama":
                response = await llm.call_llama(test_prompt)
            else:
                print(f"No test method available for {model}")
                continue

            end_time = time.time()

            print(f"Response: {response}")
            print(f"Time taken: {end_time - start_time:.2f} seconds")
            print("✅ Connection successful!")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            print("Connection failed. Check API key and internet connection.")


if __name__ == "__main__":
    asyncio.run(test_connections())
