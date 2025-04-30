#!/usr/bin/env python3
"""
Test script to validate the full analysis flow.

This script tests the end-to-end flow from the API to LLMs and back:
1. Checks if the server is running
2. Gets available models
3. Sends an analysis request
4. Retrieves and displays the results
"""

import asyncio
import json
import sys
import time
import requests
from typing import Dict, Any

# Configuration
API_BASE_URL = "http://localhost:8000"
TEST_PROMPT = "Explain the concept of artificial general intelligence in simple terms."
TEST_MODELS = ["gpt4o", "claude3opus", "gemini15"]
TEST_ULTRA_MODEL = "gpt4o"
TEST_PATTERN = "comprehensive"


async def test_full_flow():
    """Test the full analysis flow"""
    print("\n==== Ultra MVP Full Flow Test ====\n")

    # 1. Check if server is running
    print("1. Checking if server is running...")
    try:
        server_response = requests.get(f"{API_BASE_URL}/api/health", timeout=5)
        if server_response.status_code == 200:
            data = server_response.json()
            print(f"✅ Server is running (status: {data.get('status', 'unknown')})")
        else:
            print(
                f"❌ Server returned unexpected status code: {server_response.status_code}"
            )
            print("Response:", server_response.text)
            return
    except requests.RequestException as e:
        print(f"❌ Failed to connect to server: {e}")
        print("Make sure the server is running (use ./scripts/run.sh)")
        return

    # 2. Get available models
    print("\n2. Getting available models...")
    try:
        models_response = requests.get(f"{API_BASE_URL}/api/llms", timeout=5)
        if models_response.status_code == 200:
            models_data = models_response.json()
            available_models = [m["id"] for m in models_data.get("models", [])]
            print(f"✅ Available models: {', '.join(available_models)}")

            # Check if our test models are available
            missing_models = [
                model for model in TEST_MODELS if model not in available_models
            ]
            if missing_models:
                print(
                    f"⚠️ Warning: Some test models are not available: {', '.join(missing_models)}"
                )
                TEST_MODELS = [
                    model for model in TEST_MODELS if model in available_models
                ]
                if not TEST_MODELS:
                    print("❌ No test models available. Cannot proceed.")
                    return
                print(f"Proceeding with available models: {', '.join(TEST_MODELS)}")

                # Adjust ultra model if needed
                if TEST_ULTRA_MODEL not in available_models:
                    TEST_ULTRA_MODEL = TEST_MODELS[0]
                    print(f"Setting ultra model to {TEST_ULTRA_MODEL}")
        else:
            print(f"❌ Failed to get models: {models_response.status_code}")
            print("Response:", models_response.text)
            return
    except requests.RequestException as e:
        print(f"❌ Failed to get models: {e}")
        return

    # 3. Get available patterns
    print("\n3. Getting available patterns...")
    try:
        patterns_response = requests.get(f"{API_BASE_URL}/api/patterns", timeout=5)
        if patterns_response.status_code == 200:
            patterns_data = patterns_response.json()
            available_patterns = patterns_data.get("patterns", [])
            print(f"✅ Available patterns: {', '.join(available_patterns)}")

            # Check if our test pattern is available
            if TEST_PATTERN not in available_patterns and available_patterns:
                TEST_PATTERN = available_patterns[0]
                print(
                    f"⚠️ Selected pattern not available. Using {TEST_PATTERN} instead."
                )
        else:
            print(f"⚠️ Failed to get patterns: {patterns_response.status_code}")
            print("Continuing with default pattern.")
    except requests.RequestException as e:
        print(f"⚠️ Failed to get patterns: {e}")
        print("Continuing with default pattern.")

    # 4. Run analysis
    print("\n4. Sending analysis request...")
    try:
        analysis_request = {
            "prompt": TEST_PROMPT,
            "selected_models": TEST_MODELS,
            "ultra_model": TEST_ULTRA_MODEL,
            "pattern": TEST_PATTERN,
        }

        print(f"Request details:")
        print(f'  Prompt: "{TEST_PROMPT}"')
        print(f"  Models: {', '.join(TEST_MODELS)}")
        print(f"  Ultra model: {TEST_ULTRA_MODEL}")
        print(f"  Pattern: {TEST_PATTERN}")

        print("\nSending request...")
        analysis_response = requests.post(
            f"{API_BASE_URL}/api/analyze",
            json=analysis_request,
            timeout=30,  # Longer timeout for LLM processing
        )

        if analysis_response.status_code != 200:
            print(
                f"❌ Analysis request failed with status {analysis_response.status_code}"
            )
            print("Response:", analysis_response.text)
            return

        analysis_data = analysis_response.json()

        if analysis_data.get("status") == "success":
            print("✅ Analysis successful!")

            # Get the results
            results = analysis_data.get("results", {})
            model_responses = results.get("model_responses", {})
            ultra_response = results.get("ultra_response")
            total_time = results.get("total_time", 0)

            print(f"\nModels used: {', '.join(model_responses.keys())}")
            print(f"Total processing time: {total_time:.2f} seconds")

            # Print a sample of each response
            print("\n=== Model Responses ===")
            for model, response in model_responses.items():
                content = response.get("content", "")
                if content:
                    # Format the response for better readability
                    print(f"\n[{model.upper()}]")
                    print("-" * (len(model) + 2))
                    print(content)
                else:
                    print(f"\n[{model.upper()}]")
                    print("-" * (len(model) + 2))
                    print(f"Error: {response.get('error', 'Unknown error')}")

            # Print the Ultra response if available
            if ultra_response:
                print("\n=== Ultra Synthesis ===")
                print("-" * 18)
                ultra_content = ultra_response.get("content", "")
                if ultra_content:
                    print(ultra_content)
                else:
                    print(f"Error: {ultra_response.get('error', 'Unknown error')}")

            # Test complete
            print("\n✅ Full flow test completed successfully!")
        else:
            print(
                f"❌ Analysis failed with error: {analysis_data.get('message', 'Unknown error')}"
            )

    except requests.RequestException as e:
        print(f"❌ Analysis request failed: {e}")


if __name__ == "__main__":
    try:
        asyncio.run(test_full_flow())
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
        sys.exit(0)
