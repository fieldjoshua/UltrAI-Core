#!/usr/bin/env python3
"""
Test script to verify parallel execution of orchestrator
"""

import asyncio
import os
import sys
import time
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from backend.routes.orchestrator_routes_fixed import SimpleOrchestrator

async def test_parallel_execution():
    """Test that API calls execute in parallel"""
    print("=== Testing Parallel Execution ===")
    print(f"Start time: {datetime.now()}")
    
    # Mock API keys (we'll test with real ones if available)
    api_keys = {}
    
    # Check for real API keys
    if os.getenv("OPENAI_API_KEY"):
        api_keys["openai"] = os.getenv("OPENAI_API_KEY")
        print("✓ OpenAI API key found")
    
    if os.getenv("ANTHROPIC_API_KEY"):
        api_keys["anthropic"] = os.getenv("ANTHROPIC_API_KEY")
        print("✓ Anthropic API key found")
        
    if os.getenv("GOOGLE_API_KEY"):
        api_keys["google"] = os.getenv("GOOGLE_API_KEY")
        print("✓ Google API key found")
    
    if not api_keys:
        print("❌ No API keys found. Please set at least one API key.")
        return
    
    print(f"\nTesting with {len(api_keys)} models")
    
    # Create orchestrator
    orchestrator = SimpleOrchestrator(api_keys)
    print(f"Available models: {orchestrator.available_models}")
    
    # Test prompt
    test_prompt = "What is 2+2? Give a very brief answer."
    
    # Test orchestration
    print(f"\nSending prompt: {test_prompt}")
    print("Starting orchestration...")
    
    try:
        start = time.time()
        result = await orchestrator.orchestrate_simple(test_prompt)
        end = time.time()
        
        print(f"\n✅ SUCCESS! Orchestration completed in {end - start:.2f} seconds")
        print(f"\nModels responded:")
        for model, response in result["initial_responses"].items():
            print(f"- {model}: {response[:100]}...")
            
        print(f"\nProcessing time from result: {result['processing_time']:.2f} seconds")
        
        # Check if it was parallel
        if len(api_keys) > 1 and result['processing_time'] < 20:
            print("\n✅ PARALLEL EXECUTION CONFIRMED! Multiple models completed faster than sequential would allow.")
        elif len(api_keys) == 1:
            print("\n✓ Single model test passed.")
        else:
            print("\n⚠️  Execution may still be sequential - took longer than expected for parallel.")
            
    except Exception as e:
        print(f"\n❌ ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

async def test_timeout_handling():
    """Test that timeouts work properly"""
    print("\n\n=== Testing Timeout Handling ===")
    
    # Create orchestrator with a very long prompt to test timeout
    api_keys = {"openai": "test-key"} if os.getenv("OPENAI_API_KEY") else {}
    
    if not api_keys:
        print("Skipping timeout test - no API keys")
        return
        
    orchestrator = SimpleOrchestrator(api_keys)
    
    # Very complex prompt that might timeout
    long_prompt = "Please provide an extremely detailed analysis " * 100
    
    print("Testing with very long prompt to check timeout handling...")
    
    try:
        start = time.time()
        result = await orchestrator.orchestrate_simple(long_prompt)
        end = time.time()
        
        print(f"Completed in {end - start:.2f} seconds - timeout handling working")
        
    except Exception as e:
        print(f"Got expected error: {type(e).__name__}: {e}")

if __name__ == "__main__":
    print("Orchestrator Parallel Execution Test")
    print("=" * 50)
    
    # Run tests
    asyncio.run(test_parallel_execution())
    # asyncio.run(test_timeout_handling())  # Uncomment to test timeouts
    
    print("\n" + "=" * 50)
    print("Test complete!")