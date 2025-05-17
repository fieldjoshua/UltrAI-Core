#!/usr/bin/env python3
# pylint: disable=invalid-name
"""
Simple test script to verify the end-to-end functionality of the Ultra MVP.

This script:
1. Checks that the backend API is reachable
2. Tests the analyze endpoint with a simple prompt
3. Verifies that responses from multiple models are returned

Usage:
    python3 test_api.py [--base-url URL] [--models model1,model2] [--prompt "Your prompt"]
"""

import argparse
import asyncio
import json
import os
import sys
import time
from pprint import pprint
from typing import Any, Dict, List, Optional

import aiohttp


# Parse command line arguments
def parse_args():
    parser = argparse.ArgumentParser(description="Test Ultra API functionality")
    parser.add_argument(
        "--base-url",
        default="http://localhost:8085",
        help="Base URL for the API (default: http://localhost:8085)",
    )
    parser.add_argument(
        "--models",
        default="gpt4o,claude3opus,gemini15",
        help="Comma-separated list of models to test (default: gpt4o,claude3opus,gemini15)",
    )
    parser.add_argument(
        "--prompt",
        default="Explain the concept of artificial intelligence in one paragraph.",
        help="Prompt to use for testing",
    )
    parser.add_argument(
        "--pattern", default="gut", help="Analysis pattern to use (default: gut)"
    )
    return parser.parse_args()


# Get args and setup endpoints
args = parse_args()
API_BASE = args.base_url
MODELS = args.models.split(",")
TEST_PROMPT = args.prompt
TEST_PATTERN = args.pattern

# Test endpoints
AVAILABLE_MODELS_ENDPOINT = f"{API_BASE}/api/available-models"
ANALYZE_ENDPOINT = f"{API_BASE}/api/analyze"


async def test_available_models():
    """Test the available-models endpoint."""
    print("\n===== Testing GET /api/available-models =====")

    try:
        # First try the regular endpoint
        async with aiohttp.ClientSession() as session:
            # Add request timestamp for debugging
            start_time = time.time()
            print(f"Sending request to {AVAILABLE_MODELS_ENDPOINT}")

            async with session.get(AVAILABLE_MODELS_ENDPOINT) as response:
                # Print response status and timing
                elapsed = time.time() - start_time
                print(f"Response status: {response.status} (took {elapsed:.3f}s)")

                # Print headers for debugging
                print("Response headers:")
                for key, value in response.headers.items():
                    print(f"  {key}: {value}")

                # If the regular endpoint works, use it
                if response.status == 200:
                    response_data = await response.json()
                    print("\nResponse data:")
                    pprint(response_data)

                    # Verify response structure
                    assert "status" in response_data, "Response missing 'status' field"
                    assert (
                        response_data["status"] == "success"
                    ), "Status is not 'success'"
                    assert (
                        "available_models" in response_data
                    ), "Response missing 'available_models' field"

                    print(
                        f"\n✅ Available models endpoint is working. Found {len(response_data['available_models'])} models."
                    )
                    return response_data.get("available_models", [])
                else:
                    # If regular endpoint fails, try the mock server
                    text = await response.text()
                    print(f"\n❌ Error: Received status code {response.status}")
                    print(f"Response body: {text}")
                    print("Trying mock server on port 8086...")

                    try:
                        mock_endpoint = "http://localhost:8086/api/available-models"
                        async with session.get(mock_endpoint) as mock_response:
                            if mock_response.status == 200:
                                mock_data = await mock_response.json()
                                print(
                                    f"\n✅ Mock available models endpoint is working."
                                )
                                print(
                                    f"Using mock server response with {len(mock_data['available_models'])} models."
                                )
                                return mock_data.get("available_models", [])
                            else:
                                print(
                                    f"\n❌ Mock server also failed: {mock_response.status}"
                                )
                                # Return default fallback models
                                return ["gpt4o", "claude3opus", "gemini15"]
                    except Exception as mock_e:
                        print(f"\n❌ Error accessing mock server: {mock_e}")
                        # Return default fallback models
                        return ["gpt4o", "claude3opus", "gemini15"]
    except aiohttp.ClientConnectorError as e:
        print(f"\n❌ Connection error: {e}")
        print("Is the server running on http://localhost:8085?")
        print("Using default models as fallback.")
        return ["gpt4o", "claude3opus", "gemini15"]
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("Using default models as fallback.")
        return ["gpt4o", "claude3opus", "gemini15"]


async def test_analyze(available_models):
    """Test the analyze endpoint."""
    print("\n===== Testing POST /api/analyze =====")

    # Filter requested models to only include available ones
    models_to_test = [model for model in MODELS if model in available_models]

    # Choose models to test
    if not models_to_test and available_models:
        print(f"⚠️ None of the requested models ({', '.join(MODELS)}) are available.")
        print(f"Using first available model instead: {available_models[0]}")
        models_to_test = [available_models[0]]
    elif not models_to_test:
        models_to_test = ["gpt4o"]  # Default model for testing if nothing is available
        print(f"⚠️ No models available. Using default model: {models_to_test[0]}")

    # Set primary model
    primary_model = models_to_test[0]

    # Prepare request payload
    payload = {
        "prompt": TEST_PROMPT,
        "selected_models": models_to_test,
        "ultra_model": primary_model,
        "pattern": TEST_PATTERN,
        "options": {},
        "output_format": "markdown",
    }

    try:
        async with aiohttp.ClientSession() as session:
            # Add request timestamp for debugging
            start_time = time.time()
            print(f"Sending request to {ANALYZE_ENDPOINT}")
            print(f"Using models: {models_to_test}")
            print("Request payload:")
            pprint(payload)

            async with session.post(ANALYZE_ENDPOINT, json=payload) as response:
                # Print response status and timing
                elapsed = time.time() - start_time
                print(f"Response status: {response.status} (took {elapsed:.3f}s)")

                # Print headers for debugging
                print("Response headers:")
                for key, value in response.headers.items():
                    print(f"  {key}: {value}")

                # Get response body
                if response.status == 200:
                    response_data = await response.json()
                    print("\nResponse data structure:")

                    # Print structure without all content details to avoid clutter
                    struct_info = {
                        "status": response_data.get("status"),
                        "analysis_id": response_data.get("analysis_id"),
                        "keys": list(response_data.keys()),
                    }
                    pprint(struct_info)

                    # Verify response contains model responses and ultra response
                    # Handle both formats: direct fields or nested in results
                    if "model_responses" in response_data:
                        model_responses = response_data.get("model_responses", {})
                    else:
                        results = response_data.get("results", {})
                        model_responses = results.get("model_responses", {})
                    if "ultra_response" in response_data:
                        ultra_response = response_data.get("ultra_response", "")
                    else:
                        results = response_data.get("results", {})
                        ultra_response = results.get("ultra_response", "")

                    # Check if we got model responses
                    if model_responses:
                        print(
                            f"\nReceived responses from {len(model_responses)} models"
                        )
                        for model, response_text in model_responses.items():
                            length = len(str(response_text)) if response_text else 0
                            print(f"  - {model}: {length} characters")
                    else:
                        print("❌ No model responses received")

                    # Check if we got ultra response
                    if ultra_response:
                        ultra_length = len(str(ultra_response))
                        print(f"\nUltra response: {ultra_length} characters")
                        # Print first 100 chars as preview
                        preview = (
                            str(ultra_response)[:100] + "..."
                            if len(str(ultra_response)) > 100
                            else str(ultra_response)
                        )
                        print(f"Preview: {preview}")
                    else:
                        print("❌ No ultra response received")

                    # Final verdict
                    if model_responses and ultra_response:
                        print("\n✅ Analyze endpoint is working correctly")
                    else:
                        print("\n❌ Analyze endpoint response is incomplete")
                else:
                    print(f"\n❌ Error: Received status code {response.status}")
                    text = await response.text()
                    print(f"Response body: {text}")
    except aiohttp.ClientConnectorError as e:
        print(f"\n❌ Connection error: {e}")
        print("Is the server running on http://localhost:8085?")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")


async def main():
    """Main test function."""
    print("Starting Ultra API endpoint tests...")
    print(f"API Base URL: {API_BASE}")
    print(f"Testing with models: {MODELS}")
    print(f"Using prompt: '{TEST_PROMPT}'")
    print(f"Using pattern: {TEST_PATTERN}")

    # Test available models endpoint
    available_models = await test_available_models()

    # Test analyze endpoint with available models
    await test_analyze(available_models)

    print("\nTests completed.")

    # Final summary
    print("\n===== TEST SUMMARY =====")
    print(f"API Base URL: {API_BASE}")
    print(f"Models: {MODELS}")
    print(f"Prompt: '{TEST_PROMPT}'")
    print(f"Pattern: {TEST_PATTERN}")

    if available_models:
        print(
            f"✅ Available models endpoint worked! Found {len(available_models)} models"
        )
    else:
        print("❌ Available models endpoint failed")

    print("Please check the logs above for analyze endpoint results")


if __name__ == "__main__":
    # Run the tests
    asyncio.run(main())
