#!/usr/bin/env python3
"""
Test the basic orchestrator locally
Focus: Verify it actually works with real LLMs
"""
import asyncio
import os
import sys
import time

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../../'))

from backend.services.basic_orchestrator import BasicOrchestrator


async def test_basic_orchestrator():
    """Test basic orchestrator functionality"""
    print("=== Testing Basic Orchestrator ===")
    print("Focus: Reliability, Speed, Simplicity\n")
    
    # Initialize
    orchestrator = BasicOrchestrator()
    
    # Check available models
    available = orchestrator.get_available_models()
    print(f"Available models: {len(available)}")
    for model in available:
        print(f"  - {model['id']} ({model['provider']})")
    print()
    
    if not available:
        print("❌ No models available. Check API keys.")
        return
    
    # Test 1: Basic parallel call
    print("Test 1: Basic parallel call")
    start = time.time()
    
    result = await orchestrator.orchestrate_basic(
        prompt="What is 2+2? Answer in one sentence.",
        models=["gpt4o", "claude37"]
    )
    
    elapsed = time.time() - start
    print(f"✓ Completed in {elapsed:.1f}s")
    print(f"Status: {result['status']}")
    print(f"Successful models: {result['performance']['successful_models']}")
    print(f"Failed models: {result['performance']['failed_models']}")
    print()
    
    # Show responses
    for model, response in result['model_responses'].items():
        print(f"{model}:")
        print(f"  {response[:100]}...")
        print()
    
    # Test 2: Single model call
    print("\nTest 2: Single model call")
    start = time.time()
    
    result = await orchestrator.orchestrate_basic(
        prompt="Say 'hello' in Spanish.",
        models=["gpt4o"]
    )
    
    elapsed = time.time() - start
    print(f"✓ Completed in {elapsed:.1f}s")
    print(f"Response: {result['model_responses']['gpt4o']}")
    print()
    
    # Test 3: Error handling
    print("\nTest 3: Error handling (invalid model)")
    result = await orchestrator.orchestrate_basic(
        prompt="Test",
        models=["invalid-model", "gpt4o"]
    )
    
    print(f"Status: {result['status']}")
    print(f"Invalid model response: {result['model_responses']['invalid-model']}")
    print(f"Valid model response: {result['model_responses']['gpt4o'][:50]}...")
    
    print("\n✅ All tests completed!")


if __name__ == "__main__":
    # Check for API keys
    if not any([
        os.getenv("OPENAI_API_KEY"),
        os.getenv("ANTHROPIC_API_KEY"),
        os.getenv("GOOGLE_API_KEY")
    ]):
        print("❌ No API keys found. Set at least one of:")
        print("   - OPENAI_API_KEY")
        print("   - ANTHROPIC_API_KEY")
        print("   - GOOGLE_API_KEY")
        sys.exit(1)
    
    asyncio.run(test_basic_orchestrator())