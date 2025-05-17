#!/usr/bin/env python3
"""
Docker Model Runner MVP Verification Script.

A simple script to verify the minimum viable functionality of Docker Model Runner.
This script provides a clear, step-by-step test to confirm Docker Model Runner
is working properly and can generate responses from a local model.

Usage:
  python3 scripts/verify_modelrunner_mvp.py
"""

import asyncio
import json
import sys
from typing import Any, Dict, List, Optional

import aiohttp


# Simple progress indicator
class ProgressIndicator:
    """Shows a simple animated progress indicator."""

    def __init__(self, message: str):
        self.message = message
        self.running = False
        self.task = None

    async def _show_progress(self):
        """Show animated progress indicator."""
        indicators = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        i = 0
        while self.running:
            print(f"\r{indicators[i % len(indicators)]} {self.message}", end="")
            await asyncio.sleep(0.1)
            i += 1

    def start(self):
        """Start showing progress."""
        self.running = True
        self.task = asyncio.create_task(self._show_progress())

    def stop(self, message: str = ""):
        """Stop showing progress and print completion message."""
        self.running = False
        if self.task:
            self.task.cancel()
        if message:
            print(f"\r✓ {message}")
        else:
            print(f"\r✓ {self.message} - Complete")


async def check_docker_desktop():
    """Check if Docker Desktop is running."""
    print("\n📦 Step 1: Checking if Docker Desktop is running...")

    try:
        # Simple docker info command
        process = await asyncio.create_subprocess_exec(
            "docker",
            "info",
            "--format",
            "{{.ServerVersion}}",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()

        if process.returncode == 0:
            version = stdout.decode().strip()
            print(f"✅ Docker Desktop is running (version {version})")
            return True
        else:
            error = stderr.decode().strip()
            print(f"❌ Docker Desktop issue: {error}")
            print("\nPlease make sure Docker Desktop is running before continuing.")
            return False

    except FileNotFoundError:
        print("❌ Docker command not found. Is Docker Desktop installed?")
        print(
            "\nPlease install Docker Desktop from https://www.docker.com/products/docker-desktop/"
        )
        return False


async def check_modelrunner_installed():
    """Check if Model Runner extension is installed."""
    print("\n🔌 Step 2: Checking if Model Runner extension is installed...")

    try:
        # List Docker extensions
        process = await asyncio.create_subprocess_exec(
            "docker",
            "extension",
            "ls",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()

        if process.returncode == 0:
            output = stdout.decode()
            if "modelrunner" in output.lower() or "model-runner" in output.lower():
                print("✅ Docker Model Runner extension is installed")
                return True
            else:
                print("❌ Docker Model Runner extension is not installed")
                print(
                    "\nPlease install it from Docker Desktop → Extensions → Marketplace → Search for 'Model Runner'"
                )
                return False
        else:
            error = stderr.decode().strip()
            print(f"❌ Could not check extensions: {error}")
            return False

    except Exception as e:
        print(f"❌ Error checking Docker extensions: {str(e)}")
        return False


async def check_modelrunner_api(url: str = "http://localhost:8080"):
    """Check if Model Runner API is responding."""
    print(f"\n🔍 Step 3: Checking if Model Runner API is responding at {url}...")

    progress = ProgressIndicator("Connecting to Model Runner API")
    progress.start()

    try:
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(f"{url}/v1/models", timeout=10) as response:
                    progress.stop()

                    if response.status == 200:
                        data = await response.json()
                        models = [model["id"] for model in data.get("data", [])]
                        model_list = (
                            ", ".join(models) if models else "No models available yet"
                        )
                        print(
                            f"✅ Model Runner API is responding. Available models: {model_list}"
                        )
                        return True, models
                    else:
                        print(f"❌ Model Runner API returned status {response.status}")
                        response_text = await response.text()
                        print(f"Response: {response_text[:200]}...")
                        return False, []
            except (aiohttp.ClientConnectorError, asyncio.TimeoutError) as e:
                progress.stop()
                print(f"❌ Cannot connect to Model Runner API: {str(e)}")
                print("\nTroubleshooting tips:")
                print(
                    "1. Open Docker Desktop → Extensions → Model Runner → Check if it's running"
                )
                print("2. Try restarting the Model Runner extension")
                print("3. Verify port 8080 is not being used by another application")
                return False, []
    except Exception as e:
        progress.stop()
        print(f"❌ Unexpected error connecting to Model Runner API: {str(e)}")
        return False, []


async def check_default_model(models: List[str]):
    """Check if a usable model is available."""
    print("\n🧠 Step 4: Checking for a usable model...")

    # Preferred models in order of preference (smallest first)
    preferred_models = [
        "phi3:mini",
        "phi3:small",
        "gemma:2b",
        "llama3:8b",
        "mistral:7b",
    ]

    # Find the first available preferred model
    for model in preferred_models:
        if model in models:
            print(f"✅ Found preferred model: {model}")
            return True, model

    # If no preferred model is found but there are other models
    if models:
        print(f"✅ Found model: {models[0]}")
        return True, models[0]

    print("❌ No models available. Need to pull a model.")
    return False, "phi3:mini"  # Default model to try pulling


async def pull_model(model: str, url: str = "http://localhost:8080"):
    """Pull a model to Docker Model Runner."""
    print(f"\n📥 Step 5: Pulling model {model}...")

    try:
        # First try using the pull API
        async with aiohttp.ClientSession() as session:
            try:
                # The endpoint might be different depending on Model Runner version
                pull_url = f"{url}/v1/internal/models/{model}"
                progress = ProgressIndicator(f"Requesting Model Runner to pull {model}")
                progress.start()

                async with session.post(pull_url, timeout=30) as response:
                    progress.stop()

                    if response.status in [200, 202, 204]:
                        print(f"✅ Pull initiated for {model}")
                        print(
                            "\nModel is being pulled. This might take several minutes for the first time."
                        )
                        print(
                            "You can check status in Docker Desktop → Extensions → Model Runner"
                        )
                        print("\nThe model will be ready to use once it's downloaded.")
                        return True
                    else:
                        print(
                            f"⚠️ Could not initiate pull via API (status: {response.status})"
                        )
                        response_text = await response.text()
                        print(f"Response: {response_text[:200]}...")

                        # Give alternative instructions
                        print("\nPlease pull the model manually:")
                        print("1. Open Docker Desktop → Extensions → Model Runner")
                        print(
                            f"2. Look for '{model}' in the model list and click 'Pull'"
                        )
                        print("3. Wait for the download to complete")
                        return False

            except (
                aiohttp.ClientConnectorError,
                asyncio.TimeoutError,
                asyncio.CancelledError,
            ) as e:
                progress.stop()
                print(f"⚠️ Could not pull model via API: {str(e)}")

                # Give alternative instructions
                print("\nPlease pull the model manually:")
                print("1. Open Docker Desktop → Extensions → Model Runner")
                print(f"2. Look for '{model}' in the model list and click 'Pull'")
                print("3. Wait for the download to complete")
                return False

    except Exception as e:
        print(f"❌ Unexpected error pulling model: {str(e)}")
        return False


async def test_generate(model: str, url: str = "http://localhost:8080"):
    """Test generating a response from the model."""
    print(f"\n💬 Step 6: Testing generation with model {model}...")

    prompt = "Explain what Docker Model Runner is in one sentence."
    messages = [{"role": "user", "content": prompt}]

    data = {"model": model, "messages": messages, "max_tokens": 100}

    progress = ProgressIndicator("Generating response")
    progress.start()

    try:
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    f"{url}/v1/chat/completions", json=data, timeout=60
                ) as response:
                    progress.stop()

                    if response.status == 200:
                        result = await response.json()
                        content = (
                            result.get("choices", [{}])[0]
                            .get("message", {})
                            .get("content", "")
                        )

                        if content:
                            print(f"✅ Successfully generated response from {model}")
                            print(
                                "\n--- Response to 'Explain what Docker Model Runner is in one sentence' ---"
                            )
                            print(content.strip())
                            print("---")
                            return True
                        else:
                            print("❌ Received empty response from model")
                            return False
                    else:
                        print(f"❌ Generation failed with status {response.status}")
                        try:
                            error_data = await response.json()
                            print(f"Error: {json.dumps(error_data, indent=2)}")
                        except:
                            response_text = await response.text()
                            print(f"Response: {response_text[:500]}")
                        return False

            except (aiohttp.ClientConnectorError, asyncio.TimeoutError) as e:
                progress.stop()
                print(f"❌ Error communicating with Model Runner: {str(e)}")
                return False

    except Exception as e:
        progress.stop()
        print(f"❌ Unexpected error generating response: {str(e)}")
        return False


async def print_summary(success: bool):
    """Print a summary of the verification results."""
    print("\n📋 Summary")
    print("------------------")

    if success:
        print("✅ Docker Model Runner MVP verification PASSED!")
        print("\nYou can now use Docker Model Runner with Ultra:")
        print("1. Start your backend with:")
        print("   export USE_MODEL_RUNNER=true")
        print("   python3 -m uvicorn backend.app:app --reload")
        print("\n2. Use the Docker Model Runner in your requests:")
        print("   - Set models to include local models in your API requests")
        print("   - Ultra will automatically use Docker Model Runner for local models")
    else:
        print("❌ Docker Model Runner MVP verification FAILED")
        print("\nPlease check the errors above and fix them before continuing.")
        print("You can re-run this script after making changes:")
        print("python3 scripts/verify_modelrunner_mvp.py")


async def main():
    """Run the MVP verification steps."""
    print("\n🚀 Docker Model Runner MVP Verification")
    print("======================================")
    print(
        "This script will verify the minimum viable functionality of Docker Model Runner"
    )

    # Step 1: Check if Docker Desktop is running
    docker_ok = await check_docker_desktop()
    if not docker_ok:
        await print_summary(False)
        return

    # Step 2: Check if Model Runner extension is installed
    extension_ok = await check_modelrunner_installed()
    if not extension_ok:
        await print_summary(False)
        return

    # Step 3: Check if Model Runner API is responding
    api_ok, models = await check_modelrunner_api()
    if not api_ok:
        await print_summary(False)
        return

    # Step 4: Check if a usable model is available
    model_ok, model = await check_default_model(models)

    # Step 5: Pull model if needed
    if not model_ok:
        pull_ok = await pull_model(model)
        if not pull_ok:
            print("\n⚠️ Automated model pull was not successful.")
            print("Please pull the model manually and run this script again.")
            await print_summary(False)
            return

        # Re-check API to see if model appears after pull request
        print("\n🔍 Checking if model is available after pull request...")
        api_ok, models = await check_modelrunner_api()
        if model in models:
            print(f"✅ Model {model} is now available")
            model_ok = True
        else:
            print(f"⚠️ Model {model} is not yet available. It may still be downloading.")
            print("Please wait for the download to complete and run this script again.")
            await print_summary(False)
            return

    # Step 6: Test generating a response
    if model_ok:
        generation_ok = await test_generate(model)
        if not generation_ok:
            await print_summary(False)
            return

    # All steps passed
    await print_summary(True)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nScript cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error: {str(e)}")
        sys.exit(1)
