#!/usr/bin/env python3
"""
Minimal test to verify orchestration works
"""

import asyncio
import os
import sys
sys.path.insert(0, 'backend')

from routes.orchestrator_routes_fixed import SimpleOrchestrator

async def test_local():
    """Test orchestration locally to ensure code works"""
    print("Testing orchestration locally...")
    
    # Use real API keys if available
    api_keys = {}
    if os.getenv("OPENAI_API_KEY"):
        api_keys["openai"] = os.getenv("OPENAI_API_KEY")
    if os.getenv("ANTHROPIC_API_KEY"):
        api_keys["anthropic"] = os.getenv("ANTHROPIC_API_KEY")
    if os.getenv("GOOGLE_API_KEY"):
        api_keys["google"] = os.getenv("GOOGLE_API_KEY")
    
    if not api_keys:
        print("No API keys found")
        return
    
    orchestrator = SimpleOrchestrator(api_keys)
    print(f"Initialized with models: {orchestrator.available_models}")
    print(f"Clients: {list(orchestrator.clients.keys())}")
    
    # Check if google client is properly stored
    if "google" in api_keys:
        print(f"Google client stored: {'google' in orchestrator.clients}")
    
    try:
        result = await orchestrator.orchestrate_simple("What is 1+1?")
        print(f"\nSUCCESS! Got response in {result['processing_time']:.2f}s")
        print(f"Models responded: {list(result['initial_responses'].keys())}")
    except Exception as e:
        print(f"\nERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_local())