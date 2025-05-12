#!/usr/bin/env python3
"""
Cloud LLM Provider Test Script.

This script tests connectivity and functionality of cloud LLM providers
(OpenAI/GPT, Anthropic/Claude, Google/Gemini) with Ultra.

Usage:
  python3 scripts/test_cloud_llms.py [--provider PROVIDER] [--model MODEL]

Options:
  --provider  Provider to test (openai, anthropic, gemini, all)
  --model     Specific model to test
"""

import os
import sys
import asyncio
import argparse
from typing import Dict, Any, List, Optional

# Add project root to path for imports
sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

# Import the adapter module
from src.models.llm_adapter import (
    create_adapter,
    OpenAIAdapter, 
    AnthropicAdapter,
    GeminiAdapter
)


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


async def test_openai(api_key: Optional[str] = None, model: str = "gpt-4") -> bool:
    """Test OpenAI/GPT models."""
    print("\n📝 Testing OpenAI/GPT Integration")
    print("--------------------------------")
    
    # Get API key from environment if not provided
    if not api_key:
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            print("❌ OPENAI_API_KEY environment variable not set")
            return False
    
    try:
        # Create adapter
        print(f"Creating OpenAI adapter for model: {model}")
        adapter = OpenAIAdapter(api_key=api_key, model=model)
        
        # Test simple generation
        print("\nTesting simple generation...")
        progress = ProgressIndicator("Generating response")
        progress.start()
        
        response = await adapter.generate(
            "What are the three laws of robotics? Answer briefly."
        )
        
        progress.stop()
        print("\n--- Generated Response ---")
        print(response)
        print("-------------------------")
        
        # Test streaming
        print("\nTesting streaming generation...")
        print("--- Streamed Response ---")
        print("", end="", flush=True)
        
        async for chunk in adapter.stream_generate(
            "Explain what an LLM is in one sentence."
        ):
            print(chunk, end="", flush=True)
        
        print("\n-------------------------")
        
        # Get capabilities
        capabilities = adapter.get_capabilities()
        print(f"\nModel capabilities: {capabilities}")
        
        print("\n✅ OpenAI integration test completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ OpenAI test failed: {str(e)}")
        return False


async def test_anthropic(api_key: Optional[str] = None, model: str = "claude-3-opus-20240229") -> bool:
    """Test Anthropic/Claude models."""
    print("\n🧠 Testing Anthropic/Claude Integration")
    print("------------------------------------")
    
    # Get API key from environment if not provided
    if not api_key:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            print("❌ ANTHROPIC_API_KEY environment variable not set")
            return False
    
    try:
        # Create adapter
        print(f"Creating Anthropic adapter for model: {model}")
        adapter = AnthropicAdapter(api_key=api_key, model=model)
        
        # Test simple generation
        print("\nTesting simple generation...")
        progress = ProgressIndicator("Generating response")
        progress.start()
        
        response = await adapter.generate(
            "What is the Fermi Paradox? Answer briefly."
        )
        
        progress.stop()
        print("\n--- Generated Response ---")
        print(response)
        print("-------------------------")
        
        # Test streaming
        print("\nTesting streaming generation...")
        print("--- Streamed Response ---")
        print("", end="", flush=True)
        
        async for chunk in adapter.stream_generate(
            "Explain what quantum computing is in one sentence."
        ):
            print(chunk, end="", flush=True)
        
        print("\n-------------------------")
        
        # Get capabilities
        capabilities = adapter.get_capabilities()
        print(f"\nModel capabilities: {capabilities}")
        
        print("\n✅ Anthropic integration test completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Anthropic test failed: {str(e)}")
        return False


async def test_gemini(api_key: Optional[str] = None, model: str = "gemini-1.5-flash-latest") -> bool:
    """Test Google/Gemini models."""
    print("\n🌟 Testing Google/Gemini Integration")
    print("----------------------------------")
    
    # Get API key from environment if not provided
    if not api_key:
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            print("❌ GOOGLE_API_KEY environment variable not set")
            return False
    
    try:
        # Create adapter
        print(f"Creating Gemini adapter for model: {model}")
        adapter = GeminiAdapter(api_key=api_key, model=model)
        
        # Test simple generation
        print("\nTesting simple generation...")
        progress = ProgressIndicator("Generating response")
        progress.start()
        
        response = await adapter.generate(
            "What is the importance of renewable energy? Answer briefly."
        )
        
        progress.stop()
        print("\n--- Generated Response ---")
        print(response)
        print("-------------------------")
        
        # Get capabilities
        capabilities = adapter.get_capabilities()
        print(f"\nModel capabilities: {capabilities}")
        
        print("\n✅ Gemini integration test completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Gemini test failed: {str(e)}")
        return False


async def test_provider_with_create_adapter(provider: str, model: Optional[str] = None) -> bool:
    """Test a provider using the create_adapter factory function."""
    print(f"\n🔧 Testing {provider.upper()} with create_adapter Factory")
    print("-" * (len(provider) + 39))
    
    # Get appropriate API key from environment
    env_var = f"{provider.upper()}_API_KEY"
    api_key = os.environ.get(env_var)
    if not api_key:
        print(f"❌ {env_var} environment variable not set")
        return False
    
    try:
        # Create adapter using factory function
        options = {}
        if model:
            options["model"] = model
            
        print(f"Creating adapter for {provider} with model: {model or 'default'}")
        adapter = create_adapter(provider=provider, api_key=api_key, **options)
        
        # Test simple generation
        print("\nTesting simple generation...")
        progress = ProgressIndicator("Generating response")
        progress.start()
        
        response = await adapter.generate(
            "What is the capital of France and why is it historically significant? Answer briefly."
        )
        
        progress.stop()
        print("\n--- Generated Response ---")
        print(response)
        print("-------------------------")
        
        # Get capabilities
        capabilities = adapter.get_capabilities()
        print(f"\nModel capabilities: {capabilities}")
        
        print(f"\n✅ {provider.upper()} adapter factory test completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ {provider.upper()} adapter factory test failed: {str(e)}")
        return False


async def main():
    """Run the main script."""
    parser = argparse.ArgumentParser(description="Test cloud LLM providers")
    parser.add_argument(
        "--provider", 
        choices=["openai", "anthropic", "gemini", "all"], 
        default="all",
        help="Provider to test"
    )
    parser.add_argument(
        "--model", 
        help="Specific model to test"
    )
    
    args = parser.parse_args()
    provider = args.provider.lower()
    model = args.model
    
    print("🚀 Cloud LLM Provider Test")
    print("========================")
    
    results = {}
    
    # Test specified provider(s)
    if provider == "openai" or provider == "all":
        if provider == "openai" and model:
            results["openai"] = await test_openai(model=model)
            results["openai_factory"] = await test_provider_with_create_adapter("openai", model)
        else:
            results["openai"] = await test_openai()
            results["openai_factory"] = await test_provider_with_create_adapter("openai")
            
    if provider == "anthropic" or provider == "all":
        if provider == "anthropic" and model:
            results["anthropic"] = await test_anthropic(model=model)
            results["anthropic_factory"] = await test_provider_with_create_adapter("anthropic", model)
        else:
            results["anthropic"] = await test_anthropic()
            results["anthropic_factory"] = await test_provider_with_create_adapter("anthropic")
            
    if provider == "gemini" or provider == "all":
        if provider == "gemini" and model:
            results["gemini"] = await test_gemini(model=model)
            results["gemini_factory"] = await test_provider_with_create_adapter("gemini", model)
        else:
            results["gemini"] = await test_gemini()
            results["gemini_factory"] = await test_provider_with_create_adapter("gemini")
    
    # Print summary
    print("\n📋 Test Summary")
    print("=============")
    for name, success in results.items():
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{name}: {status}")
    
    # Check if all tests passed
    all_passed = all(results.values())
    if all_passed:
        print("\n🎉 All tests passed! Cloud LLM providers are integrated and working correctly.")
    else:
        print("\n⚠️ Some tests failed. Check the logs above for details.")
        
    print("\nTo use these LLM providers with Ultra, make sure the appropriate environment variables are set:")
    print("- OPENAI_API_KEY for OpenAI/GPT models")
    print("- ANTHROPIC_API_KEY for Anthropic/Claude models")
    print("- GOOGLE_API_KEY for Google/Gemini models")
    
    return all_passed


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nTest cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error: {str(e)}")
        sys.exit(1)