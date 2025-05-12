#!/usr/bin/env python3
"""
Docker Model Runner Model Puller.

This script pulls models for Docker Model Runner to use in local development.
It helps automate the process of setting up the models needed for running
UltraLLM with local model inference capabilities.

Usage:
  python3 scripts/pull_modelrunner_models.py [--models MODEL1,MODEL2,...] [--force]

Options:
  --models    Comma-separated list of models to pull (default: phi3:mini,llama3:8b)
  --force     Force pull even if models are already available
"""

import os
import sys
import asyncio
import argparse
from typing import List, Optional

# Add parent directory to path for imports
sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

# Try to import aiohttp
try:
    import aiohttp
except ImportError:
    print("Error: aiohttp not found. Please install with:")
    print("pip install aiohttp")
    sys.exit(1)

# Default models to pull
DEFAULT_MODELS = ["phi3:mini", "llama3:8b"]


async def check_model_availability(model_id: str, base_url: str = "http://localhost:8080") -> bool:
    """
    Check if a model is already available in Docker Model Runner.
    
    Args:
        model_id: The model identifier
        base_url: The base URL for the Model Runner API
        
    Returns:
        True if the model is available, False otherwise
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{base_url}/v1/models", timeout=5) as response:
                if response.status == 200:
                    data = await response.json()
                    available_models = [model["id"] for model in data.get("data", [])]
                    return model_id in available_models
                return False
    except Exception:
        return False


async def pull_model(model_id: str, base_url: str = "http://localhost:8080") -> bool:
    """
    Pull a model using Docker Model Runner API.
    
    Args:
        model_id: The model identifier
        base_url: The base URL for the Model Runner API
        
    Returns:
        True if successful, False otherwise
    """
    try:
        print(f"Pulling model {model_id}...")
        
        # Check if model already exists
        if await check_model_availability(model_id, base_url):
            print(f"Model {model_id} is already available")
            return True
            
        # Use the API to pull the model
        async with aiohttp.ClientSession() as session:
            # In Model Runner, we can create a model to pull it
            create_payload = {
                "id": model_id,
                "name": model_id,
                "object": "model"
            }
            
            async with session.post(
                f"{base_url}/v1/models", 
                json=create_payload,
                timeout=600  # 10 minute timeout for large model downloads
            ) as response:
                if response.status in (200, 201, 202):
                    print(f"✅ Successfully pulled model {model_id}")
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ Failed to pull model {model_id}: {response.status} - {error_text[:200]}")
                    return False
    except Exception as e:
        print(f"❌ Error pulling model {model_id}: {str(e)}")
        return False


async def check_docker_model_runner(base_url: str = "http://localhost:8080") -> bool:
    """
    Check if Docker Model Runner is available.
    
    Args:
        base_url: The base URL for the Model Runner API
        
    Returns:
        True if available, False otherwise
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{base_url}/v1/models", timeout=5) as response:
                return response.status == 200
    except Exception:
        return False


async def main():
    """Run the main script logic."""
    parser = argparse.ArgumentParser(description="Pull models for Docker Model Runner")
    parser.add_argument(
        "--models", 
        default=",".join(DEFAULT_MODELS),
        help=f"Comma-separated list of models to pull (default: {','.join(DEFAULT_MODELS)})"
    )
    parser.add_argument(
        "--force", 
        action="store_true",
        help="Force pull even if models are already available"
    )
    parser.add_argument(
        "--url", 
        default="http://localhost:8080",
        help="Base URL for Docker Model Runner API"
    )
    
    args = parser.parse_args()
    models_to_pull = args.models.split(",")
    
    # Check if Docker Model Runner is available
    if not await check_docker_model_runner(args.url):
        print("❌ Docker Model Runner is not available at the specified URL")
        print(f"Attempted to connect to: {args.url}")
        print("\nTroubleshooting tips:")
        print("1. Make sure Docker Desktop is running")
        print("2. Check that the Model Runner extension is installed and enabled")
        print("3. Try running 'docker model list' to verify the command line works")
        print("4. Check if the Model Runner API is available at the correct port")
        print("5. Try manually pulling a model with 'docker model run phi3:mini \"Hello\"'")
        return
    
    # Pull each model
    print(f"Pulling {len(models_to_pull)} models: {', '.join(models_to_pull)}")
    
    for model_id in models_to_pull:
        # Check if we should skip existing models
        if not args.force and await check_model_availability(model_id, args.url):
            print(f"Skipping {model_id} as it's already available (use --force to override)")
            continue
            
        success = await pull_model(model_id, args.url)
        if not success:
            print(f"Warning: Failed to pull model {model_id}")
    
    # Final status check
    print("\nChecking final model availability...")
    available = []
    missing = []
    
    for model_id in models_to_pull:
        if await check_model_availability(model_id, args.url):
            available.append(model_id)
        else:
            missing.append(model_id)
    
    if available:
        print(f"\n✅ Available models: {', '.join(available)}")
    
    if missing:
        print(f"\n❌ Missing models: {', '.join(missing)}")
        print("Some models failed to pull. Check the Docker Model Runner logs for details.")
    else:
        print("\n✅ All requested models are available!")
        print("You can now use the Docker Model Runner with Ultra!")


if __name__ == "__main__":
    asyncio.run(main())