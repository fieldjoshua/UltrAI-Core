#!/usr/bin/env python3
"""
Docker Model Runner CLI Test Script.

This script tests the Docker Model Runner CLI adapter.
"""

import asyncio
import os
import sys

# Add project root to path for imports
sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

# Import the adapter
from src.models.docker_modelrunner_cli_adapter import (
    DockerModelRunnerCLIAdapter,
    create_modelrunner_cli_adapter,
)


async def main():
    """Run the main script logic."""
    print("🚀 Docker Model Runner CLI Adapter Test")
    print("======================================")

    # Step 1: Check if Docker Model Runner is running
    print("\n📦 Checking Docker Model Runner status...")

    try:
        process = await asyncio.create_subprocess_exec(
            "docker",
            "model",
            "status",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            print(f"❌ Docker Model Runner is not running: {stderr.decode().strip()}")
            print("\nPlease start Docker Model Runner and try again.")
            return

        print(f"✅ Docker Model Runner is running: {stdout.decode().strip()}")

    except Exception as e:
        print(f"❌ Error checking Docker Model Runner status: {str(e)}")
        return

    # Step 2: List available models
    print("\n📋 Listing available models...")
    models = await DockerModelRunnerCLIAdapter.get_available_models()

    if not models:
        print("❌ No models available")
        print(
            "\nPlease pull a model with 'docker model pull ai/smollm2' and try again."
        )
        return

    print("✅ Available models:")
    for model in models:
        print(f"  - {model}")

    # Step 3: Test generation with first model
    model = models[0]
    print(f"\n💬 Testing generation with model '{model}'...")

    adapter = await create_modelrunner_cli_adapter(model)
    prompt = "What is Docker Model Runner in one sentence?"

    print(f"Prompt: '{prompt}'")
    print("Generating response...")

    response = await adapter.generate(prompt)

    print("\n--- Generated Response ---")
    print(response)
    print("-------------------------")

    # Step 4: Test streaming with first model
    print(f"\n🌊 Testing streaming with model '{model}'...")

    prompt = "Explain the benefits of containerization in 3 bullet points."
    print(f"Prompt: '{prompt}'")
    print("Streaming response...")

    print("\n--- Streamed Response ---")
    print("", end="", flush=True)

    async for chunk in adapter.stream_generate(prompt):
        print(chunk, end="", flush=True)
        await asyncio.sleep(0.01)

    print("\n-------------------------")

    print("\n✅ Testing complete!")
    print("\nThe Docker Model Runner CLI adapter is working correctly.")
    print(
        "You can now use this adapter with Ultra by updating the Ultra backend configuration."
    )


if __name__ == "__main__":
    asyncio.run(main())
