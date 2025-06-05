#!/usr/bin/env python3
"""
Quick test script to verify orchestrator works locally
Run with: python test_local_orchestrator.py
"""
import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

from backend.services.minimal_orchestrator import MinimalOrchestrator


async def test_orchestrator():
    """Test the orchestrator locally"""
    print("Testing Minimal Orchestrator with Ultra Synthesis™\n")
    
    orchestrator = MinimalOrchestrator()
    
    # Test prompt
    prompt = "What are the benefits of exercise?"
    models = ["gpt4o", "claude37"]
    
    print(f"Prompt: {prompt}")
    print(f"Models: {models}")
    print("\nRunning Ultra Synthesis (Initial → Meta → Ultra)...\n")
    
    try:
        result = await orchestrator.orchestrate(prompt, models)
        
        print("=== INITIAL RESPONSES ===")
        for model, response in result["initial_responses"].items():
            print(f"\n{model}:")
            print(response[:200] + "..." if len(response) > 200 else response)
        
        print("\n=== META RESPONSES ===")
        for model, response in result["meta_responses"].items():
            print(f"\n{model}:")
            print(response[:200] + "..." if len(response) > 200 else response)
        
        print("\n=== ULTRA SYNTHESIS ===")
        print(result["ultra_response"][:500] + "..." if len(result["ultra_response"]) > 500 else result["ultra_response"])
        
        print("\n=== PERFORMANCE ===")
        print(f"Total time: {result['performance']['total_time_seconds']:.2f}s")
        print("Model times:")
        for stage, time in result['performance']['model_times'].items():
            print(f"  {stage}: {time:.2f}s")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Check for API keys
    if not os.getenv("OPENAI_API_KEY"):
        print("Warning: OPENAI_API_KEY not set")
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("Warning: ANTHROPIC_API_KEY not set")
    if not os.getenv("GOOGLE_API_KEY"):
        print("Warning: GOOGLE_API_KEY not set")
    
    asyncio.run(test_orchestrator())