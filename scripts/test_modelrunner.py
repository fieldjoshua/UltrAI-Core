#!/usr/bin/env python3
"""
Docker Model Runner Verification Script.

This script tests the connection to Docker Model Runner and checks available models.
It can also generate a test response to verify integration with Ultra.

Usage:
  python3 scripts/test_modelrunner.py [--generate] [--model MODEL] [--prompt PROMPT]

Options:
  --generate  Generate a test response from the model
  --model     Specify model to use (default: phi3:mini)
  --prompt    Specify prompt to use (default: "Explain what Docker Model Runner is in one sentence")
"""

import argparse
import asyncio
import json
import os
import sys
from typing import Any, Dict, List, Optional

# Add project root to path
sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

# Import the adapter module
try:
    from src.models.docker_modelrunner_adapter import (
        DockerModelRunnerAdapter,
        get_available_models,
    )
except ImportError:
    print(
        "Error: Could not import Docker Model Runner adapter. Make sure you're running from the project root."
    )
    sys.exit(1)


async def check_modelrunner_connection(base_url: str = "http://localhost:8080") -> bool:
    """Check connection to Docker Model Runner."""
    try:
        print(f"Checking connection to Docker Model Runner at {base_url}...")

        # First check if the server is reachable
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{base_url}/v1/models", timeout=5) as response:
                    if response.status == 200:
                        data = await response.json()
                        models = [model["id"] for model in data.get("data", [])]
                        print("✅ Connection successful!")
                        print(
                            f"Available models: {', '.join(models) if models else 'No models available yet'}"
                        )
                        return True
                    else:
                        print(
                            f"❌ Connection failed with status code: {response.status}"
                        )
                        response_text = await response.text()
                        print(f"Response: {response_text[:200]}...")
        except aiohttp.ClientConnectorError:
            print("❌ Cannot connect to Docker Model Runner API")
        except asyncio.TimeoutError:
            print("❌ Connection timed out")

        print("\nTroubleshooting tips:")
        print("1. Make sure Docker Desktop is running")
        print("2. Check that the Model Runner extension is installed and enabled")
        print("3. Verify Docker Compose is running with the model-runner service:")
        print("   docker-compose --profile with-model-runner up -d")
        print("4. Check Docker logs for any errors:")
        print("   docker logs ultra-model-runner")
        print("5. Verify the service port is correct (default: 8080)")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False


async def test_generate_response(
    model: str = "phi3:mini",
    prompt: str = "Explain what Docker Model Runner is in one sentence",
    base_url: str = "http://localhost:8080",
) -> Optional[str]:
    """Generate a test response from Docker Model Runner."""
    try:
        print(f"Generating response from model '{model}' with prompt: '{prompt}'")
        adapter = DockerModelRunnerAdapter(
            model=model,
            base_url=base_url,
            model_mapping={model: model},  # Simple 1:1 mapping for testing
        )

        response = await adapter.generate(prompt)
        print("\n--- Generated Response ---")
        print(response)
        print("-------------------------")
        return response
    except Exception as e:
        print(f"❌ Failed to generate response: {str(e)}")
        return None


async def main():
    """Run the main script logic."""
    parser = argparse.ArgumentParser(description="Test Docker Model Runner integration")
    parser.add_argument(
        "--generate", action="store_true", help="Generate a test response"
    )
    parser.add_argument(
        "--model", default="phi3:mini", help="Model to use for generation"
    )
    parser.add_argument(
        "--prompt",
        default="Explain what Docker Model Runner is in one sentence",
        help="Prompt to use for generation",
    )
    parser.add_argument(
        "--url",
        default="http://localhost:8080",
        help="Base URL for Docker Model Runner API",
    )

    args = parser.parse_args()

    # Check connection
    connection_ok = await check_modelrunner_connection(args.url)

    if not connection_ok:
        print(
            "Could not connect to Docker Model Runner. Please check the installation."
        )
        return

    # Generate test response if requested
    if args.generate:
        await test_generate_response(args.model, args.prompt, args.url)


if __name__ == "__main__":
    asyncio.run(main())
