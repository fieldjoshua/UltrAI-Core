#!/usr/bin/env python3
# pylint: disable=invalid-name,subprocess-run-check
"""
Test script for Docker Model Runner integration.

This script tests the Docker Model Runner integration by:
1. Checking if the Docker Model Runner CLI is available
2. Listing available models in Docker Model Runner
3. Testing a simple prompt with a selected model
4. Running the same prompt through the Ultra API with Docker Model Runner

Usage:
    python3 test_docker_modelrunner.py [--base-url URL] [--model MODEL_NAME]
"""

import argparse
import asyncio
import json
import os
import subprocess
import sys
import time
from typing import Any, Dict, List, Optional

import aiohttp


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Test Docker Model Runner integration")
    parser.add_argument(
        "--base-url",
        default="http://localhost:8085",
        help="Base URL for the Ultra API (default: http://localhost:8085)",
    )
    parser.add_argument(
        "--model",
        default=None,
        help="Docker Model Runner model to test (default: first available model)",
    )
    parser.add_argument(
        "--prompt",
        default="Explain the concept of Docker Model Runner in one paragraph.",
        help="Prompt to use for testing (default: explanation of Docker Model Runner)",
    )
    return parser.parse_args()


def print_header(text: str):
    """Print a nicely formatted header."""
    print("\n" + "=" * 80)
    print(f" {text}")
    print("=" * 80)


def check_docker_model_runner_cli():
    """Check if Docker Model Runner CLI is available."""
    print_header("Checking Docker Model Runner CLI")
    try:
        result = subprocess.run(
            ["docker", "model", "list"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            print("✅ Docker Model Runner CLI is available")
            return True
        else:
            print(f"❌ Docker Model Runner CLI not available: {result.stderr.strip()}")
            return False
    except FileNotFoundError:
        print("❌ Docker command not found. Make sure Docker is installed.")
        return False
    except Exception as e:
        print(f"❌ Error checking Docker Model Runner CLI: {e}")
        return False


def list_available_models():
    """List available models in Docker Model Runner."""
    print_header("Listing Available Models")
    try:
        result = subprocess.run(
            ["docker", "model", "list"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            # Parse output to extract model names
            lines = result.stdout.strip().split("\n")
            models = []

            # Skip header line
            if len(lines) > 1:
                for line in lines[1:]:
                    columns = line.split()
                    if columns:
                        models.append(columns[0])  # First column is model name

            if models:
                print(f"✅ Found {len(models)} models:")
                for model in models:
                    print(f"  - {model}")
                return models
            else:
                print(
                    "⚠️ No models found. You can pull a model using 'docker model pull [model]'"
                )
                return []
        else:
            print(f"❌ Failed to list models: {result.stderr.strip()}")
            return []
    except Exception as e:
        print(f"❌ Error listing models: {e}")
        return []


def test_model_directly(model: str, prompt: str):
    """Test a model directly using Docker Model Runner CLI."""
    print_header(f"Testing Model {model} Directly")
    print(f"Prompt: '{prompt}'")

    try:
        start_time = time.time()
        result = subprocess.run(
            ["docker", "model", "run", model, prompt],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        elapsed = time.time() - start_time

        if result.returncode == 0:
            print(f"✅ Model responded in {elapsed:.2f} seconds")
            response = result.stdout.strip()

            # Print preview of response
            preview_length = min(len(response), 500)
            print(
                f"\nResponse preview ({preview_length} chars of {len(response)} total):"
            )
            print("-" * 80)
            print(response[:preview_length])
            if len(response) > preview_length:
                print("...")
            print("-" * 80)

            return response
        else:
            print(f"❌ Model run failed: {result.stderr.strip()}")
            return None
    except Exception as e:
        print(f"❌ Error running model: {e}")
        return None


async def test_model_through_api(base_url: str, model: str, prompt: str):
    """Test a model through the Ultra API."""
    print_header(f"Testing Model {model} Through Ultra API")
    print(f"Base URL: {base_url}")
    print(f"Prompt: '{prompt}'")

    # Test endpoint - make sure it has /api prefix
    if not base_url.endswith("/api"):
        analyze_endpoint = f"{base_url}/api/analyze"
    else:
        analyze_endpoint = f"{base_url}/analyze"

    # Prepare request payload
    payload = {
        "prompt": prompt,
        "selected_models": [model],
        "ultra_model": model,
        "pattern": "gut",
        "options": {},
    }

    try:
        async with aiohttp.ClientSession() as session:
            start_time = time.time()
            print(f"Sending request to {analyze_endpoint}")

            async with session.post(analyze_endpoint, json=payload) as response:
                elapsed = time.time() - start_time
                print(f"Response status: {response.status} (took {elapsed:.2f}s)")

                if response.status == 200:
                    response_data = await response.json()

                    # Check for model responses in either format
                    if "model_responses" in response_data:
                        model_responses = response_data.get("model_responses", {})
                    else:
                        results = response_data.get("results", {})
                        model_responses = results.get("model_responses", {})

                    # Check if we got a response for the requested model
                    if model in model_responses:
                        model_response = model_responses[model]

                        # Handle string or object response format
                        if isinstance(model_response, str):
                            response_text = model_response
                        elif (
                            isinstance(model_response, dict)
                            and "content" in model_response
                        ):
                            response_text = model_response["content"]
                        elif (
                            isinstance(model_response, dict)
                            and "response" in model_response
                        ):
                            response_text = model_response["response"]
                        else:
                            response_text = str(model_response)

                        print(f"✅ Model {model} responded through API")

                        # Print preview of response
                        preview_length = min(len(response_text), 500)
                        print(
                            f"\nResponse preview ({preview_length} chars of {len(response_text)} total):"
                        )
                        print("-" * 80)
                        print(response_text[:preview_length])
                        if len(response_text) > preview_length:
                            print("...")
                        print("-" * 80)

                        return response_text
                    else:
                        print(f"❌ No response found for model {model}")
                        print(
                            f"Available model responses: {list(model_responses.keys())}"
                        )
                        return None
                else:
                    print(f"❌ API request failed with status {response.status}")
                    error_text = await response.text()
                    print(f"Error: {error_text}")
                    return None
    except aiohttp.ClientConnectorError as e:
        print(f"❌ Connection error: {e}")
        print(f"Is the Ultra API running at {base_url}?")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None


async def main():
    """Main function to run tests."""
    args = parse_args()
    base_url = args.base_url
    selected_model = args.model
    prompt = args.prompt

    print_header("Docker Model Runner Integration Test")
    print(f"Ultra API URL: {base_url}")

    # Check if Docker Model Runner CLI is available
    if not check_docker_model_runner_cli():
        print("Aborting tests because Docker Model Runner CLI is not available.")
        sys.exit(1)

    # List available models
    available_models = list_available_models()
    if not available_models:
        print("Aborting tests because no models are available.")
        sys.exit(1)

    # Choose a model to test
    model_to_test = selected_model
    if not model_to_test:
        model_to_test = available_models[0]
        print(f"No model specified, using first available model: {model_to_test}")
    elif model_to_test not in available_models:
        print(f"⚠️ Specified model {model_to_test} not found in available models.")
        model_to_test = available_models[0]
        print(f"Using first available model instead: {model_to_test}")

    # Test the model directly
    direct_response = test_model_directly(model_to_test, prompt)

    # Test the model through the API
    api_response = await test_model_through_api(base_url, model_to_test, prompt)

    # Final summary
    print_header("Test Summary")
    print(f"Model tested: {model_to_test}")
    print(f"Ultra API URL: {base_url}")

    if direct_response:
        print("✅ Direct model test successful")
    else:
        print("❌ Direct model test failed")

    if api_response:
        print("✅ API integration test successful")
    else:
        print("❌ API integration test failed")

    if direct_response and api_response:
        print("\n🎉 Docker Model Runner integration is working correctly!")
    else:
        print("\n⚠️ Docker Model Runner integration test completed with issues.")
        print("Please check the logs above for details.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n❌ Test interrupted by user.")
        sys.exit(1)
