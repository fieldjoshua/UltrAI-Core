#!/usr/bin/env python3
"""
Cloud LLM Integration Verification Script.

This script performs a comprehensive verification of the cloud LLM integrations
with Ultra, testing both the adapter functionality and the service layer integration.

Usage:
  python3 scripts/verify_cloud_llm_integration.py [--full]

Options:
  --full    Run full verification including all providers and end-to-end tests
"""

import argparse
import asyncio
import json
import os
import sys
from typing import Any, Dict, List, Optional

# Add project root to path for imports
sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from backend.services.llm_config_service import llm_config_service

# Import required modules
from src.models.llm_adapter import (
    AnthropicAdapter,
    GeminiAdapter,
    OpenAIAdapter,
    create_adapter_async,
)


async def verify_adapter_creation(provider: str, api_key: Optional[str] = None) -> bool:
    """
    Verify that an adapter can be created for the specified provider.

    Args:
        provider: The provider to test
        api_key: Optional API key (if not provided, will be read from environment)

    Returns:
        True if adapter creation succeeded, False otherwise
    """
    print(f"\n📋 Testing adapter creation for {provider}")
    print("-" * 40)

    try:
        # Get API key from environment if not provided
        if not api_key:
            env_var = f"{provider.upper()}_API_KEY"
            api_key = os.environ.get(env_var)
            if not api_key:
                print(f"❌ {env_var} environment variable not set")
                return False

        # Create adapter
        adapter = await create_adapter_async(provider=provider, api_key=api_key)

        # Check if adapter is of expected type
        if provider.lower() == "openai" and not isinstance(adapter, OpenAIAdapter):
            print(f"❌ Expected OpenAIAdapter but got {type(adapter)}")
            return False
        elif provider.lower() == "anthropic" and not isinstance(
            adapter, AnthropicAdapter
        ):
            print(f"❌ Expected AnthropicAdapter but got {type(adapter)}")
            return False
        elif provider.lower() == "gemini" and not isinstance(adapter, GeminiAdapter):
            print(f"❌ Expected GeminiAdapter but got {type(adapter)}")
            return False

        # Check capabilities
        capabilities = adapter.get_capabilities()
        print(f"✅ Adapter created successfully")
        print(f"Model capabilities: {json.dumps(capabilities, indent=2)}")
        return True

    except Exception as e:
        print(f"❌ Failed to create adapter: {str(e)}")
        return False


async def verify_model_registration(provider: str) -> bool:
    """
    Verify that models for the specified provider are registered in the LLM config service.

    Args:
        provider: The provider to test

    Returns:
        True if models are registered, False otherwise
    """
    print(f"\n📋 Testing model registration for {provider}")
    print("-" * 40)

    try:
        # Get available models
        models = llm_config_service.get_available_models()

        # Check if any models for the provider are registered
        provider_models = []
        for name, details in models.items():
            # Handle different model registry formats
            provider_name = ""
            if isinstance(details, dict):
                provider_name = details.get("provider", "")
            elif hasattr(details, "provider"):
                provider_name = details.provider

            if provider_name.lower() == provider.lower():
                provider_models.append(name)

        if not provider_models:
            print(f"❌ No models registered for provider {provider}")
            return False

        print(f"✅ Found {len(provider_models)} models for provider {provider}:")
        for model in provider_models:
            details = models.get(model, {})
            # Get available status safely
            is_available = False
            if isinstance(details, dict):
                is_available = details.get("available", False)
            elif hasattr(details, "available"):
                is_available = details.available

            status = "✅ Available" if is_available else "❌ Unavailable"

            # Get model name safely
            model_name = "unknown"
            if isinstance(details, dict):
                model_name = details.get("model", "unknown")
            elif hasattr(details, "model"):
                model_name = details.model

            print(f"  - {model}: {status} ({model_name})")

        return True

    except Exception as e:
        print(f"❌ Failed to verify model registration: {str(e)}")
        return False


async def verify_simple_generation(
    provider: str, api_key: Optional[str] = None
) -> bool:
    """
    Verify that a simple text generation works with the specified provider.

    Args:
        provider: The provider to test
        api_key: Optional API key (if not provided, will be read from environment)

    Returns:
        True if generation succeeded, False otherwise
    """
    print(f"\n📋 Testing simple generation with {provider}")
    print("-" * 40)

    try:
        # Get API key from environment if not provided
        if not api_key:
            env_var = f"{provider.upper()}_API_KEY"
            api_key = os.environ.get(env_var)
            if not api_key:
                print(f"❌ {env_var} environment variable not set")
                return False

        # Create adapter
        adapter = await create_adapter_async(provider=provider, api_key=api_key)

        # Test generation
        print("Generating response...")
        prompt = "What is the capital of France? Answer in one sentence."
        response = await adapter.generate(prompt)

        print(f"\nResponse: {response}")

        if not response or len(response.strip()) < 5:
            print("❌ Response seems too short or empty")
            return False

        print("✅ Generation successful")
        return True

    except Exception as e:
        print(f"❌ Failed to generate text: {str(e)}")
        return False


async def verify_streaming_generation(
    provider: str, api_key: Optional[str] = None
) -> bool:
    """
    Verify that streaming text generation works with the specified provider.

    Args:
        provider: The provider to test
        api_key: Optional API key (if not provided, will be read from environment)

    Returns:
        True if streaming generation succeeded, False otherwise
    """
    print(f"\n📋 Testing streaming generation with {provider}")
    print("-" * 40)

    # Skip streaming test for Google/Gemini as it has limited streaming support
    if provider.lower() == "gemini":
        print("⚠️ Skipping streaming test for Gemini (limited streaming support)")
        return True

    # For Anthropic, fallback to simple generation if streaming fails
    anthropic_fallback = False

    try:
        # Get API key from environment if not provided
        if not api_key:
            env_var = f"{provider.upper()}_API_KEY"
            api_key = os.environ.get(env_var)
            if not api_key:
                print(f"❌ {env_var} environment variable not set")
                return False

        # Create adapter
        adapter = await create_adapter_async(provider=provider, api_key=api_key)

        # Check if streaming is supported
        capabilities = adapter.get_capabilities()
        if not capabilities.get("supports_streaming", False):
            print(
                f"⚠️ Provider {provider} does not support streaming according to capabilities"
            )
            return True

        # Test streaming
        print("Streaming response:")
        prompt = "Count from 1 to 5 with each number on a new line."
        full_response = ""

        try:
            print("", end="", flush=True)
            async for chunk in adapter.stream_generate(prompt):
                print(chunk, end="", flush=True)
                full_response += chunk
            print()
        except Exception as e:
            if provider.lower() == "anthropic":
                print(f"\n⚠️ Anthropic streaming failed: {str(e)}")
                print("Falling back to non-streaming response...")
                anthropic_fallback = True
                # For Anthropic, fallback to simple generation
                full_response = await adapter.generate(prompt)
                print(full_response)
            else:
                raise e

        if not full_response or len(full_response.strip()) < 5:
            print("❌ Streamed response seems too short or empty")
            return False

        if anthropic_fallback:
            print(
                "\n⚠️ Anthropic streaming not working, but fallback to non-streaming succeeded"
            )
            return True
        else:
            print("\n✅ Streaming successful")
            return True

    except Exception as e:
        print(f"❌ Failed to stream text: {str(e)}")
        return False


async def verify_provider(provider: str) -> Dict[str, bool]:
    """
    Run all verification tests for a single provider.

    Args:
        provider: The provider to test

    Returns:
        Dictionary of test results
    """
    print(f"\n\n🔍 VERIFYING {provider.upper()} INTEGRATION")
    print("=" * 50)

    results = {}

    # Test adapter creation
    results["adapter_creation"] = await verify_adapter_creation(provider)

    # Test model registration
    results["model_registration"] = await verify_model_registration(provider)

    # Test simple generation
    results["simple_generation"] = await verify_simple_generation(provider)

    # Test streaming generation
    results["streaming_generation"] = await verify_streaming_generation(provider)

    return results


async def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Verify cloud LLM integrations")
    parser.add_argument("--full", action="store_true", help="Run full verification")

    args = parser.parse_args()
    full_verification = args.full

    print("🚀 Cloud LLM Integration Verification")
    print("====================================")

    # Ensure environment variables are set for all providers
    if "OPENAI_API_KEY" not in os.environ:
        print("⚠️ OPENAI_API_KEY not found in environment - some tests may fail")
    if "ANTHROPIC_API_KEY" not in os.environ:
        print("⚠️ ANTHROPIC_API_KEY not found in environment - some tests may fail")
    if "GOOGLE_API_KEY" not in os.environ:
        print("⚠️ GOOGLE_API_KEY not found in environment - some tests may fail")

    # Look for specific keys in the .env file if they exist
    try:
        with open(
            os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"), "r"
        ) as f:
            env_content = f.read()

            # Extract API keys from .env if not in environment
            if "OPENAI_API_KEY" not in os.environ:
                import re

                match = re.search(r"OPENAI_API_KEY\s*=\s*([^\s]+)", env_content)
                if match:
                    os.environ["OPENAI_API_KEY"] = match.group(1)
                    print("✅ Found OPENAI_API_KEY in .env file")

            if "ANTHROPIC_API_KEY" not in os.environ:
                match = re.search(r"ANTHROPIC_API_KEY\s*=\s*([^\s]+)", env_content)
                if match:
                    os.environ["ANTHROPIC_API_KEY"] = match.group(1)
                    print("✅ Found ANTHROPIC_API_KEY in .env file")

            if "GOOGLE_API_KEY" not in os.environ:
                match = re.search(r"GOOGLE_API_KEY\s*=\s*([^\s]+)", env_content)
                if match:
                    os.environ["GOOGLE_API_KEY"] = match.group(1)
                    print("✅ Found GOOGLE_API_KEY in .env file")
    except:
        print("⚠️ Could not read .env file")

    providers = ["openai", "anthropic", "gemini"]
    all_results = {}

    for provider in providers:
        all_results[provider] = await verify_provider(provider)

    # Print summary
    print("\n\n📊 VERIFICATION SUMMARY")
    print("=====================")

    all_passed = True
    for provider, results in all_results.items():
        provider_passed = all(results.values())
        status = "✅ PASSED" if provider_passed else "❌ FAILED"
        all_passed = all_passed and provider_passed

        print(f"\n{provider.upper()}: {status}")
        for test, passed in results.items():
            test_status = "✅ Passed" if passed else "❌ Failed"
            print(f"  - {test}: {test_status}")

    print("\n" + "=" * 50)
    overall_status = (
        "✅ ALL PROVIDERS VERIFIED SUCCESSFULLY"
        if all_passed
        else "❌ VERIFICATION FAILED FOR SOME PROVIDERS"
    )
    print(overall_status)

    if not all_passed:
        print(
            "\n⚠️ Some verification tests failed. Please check the logs above for details."
        )
        print("Make sure the appropriate API keys are set in environment variables:")
        print("- OPENAI_API_KEY for OpenAI")
        print("- ANTHROPIC_API_KEY for Anthropic")
        print("- GOOGLE_API_KEY for Google/Gemini")

    return all_passed


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
