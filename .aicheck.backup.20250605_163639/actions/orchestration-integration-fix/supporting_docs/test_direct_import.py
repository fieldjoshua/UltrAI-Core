#!/usr/bin/env python3
"""
Test direct import of orchestrator routes to debug the 500 error
"""

import os
import sys

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../..'))

try:
    # Test the integration module import
    print("1. Testing pattern_orchestrator_integration import...")
    from backend.integrations.pattern_orchestrator_integration import (
        PatternOrchestrator, 
        get_pattern_mapping, 
        ORCHESTRATOR_AVAILABLE
    )
    print(f"   ✅ ORCHESTRATOR_AVAILABLE = {ORCHESTRATOR_AVAILABLE}")
    
    # Test orchestrator initialization
    print("\n2. Testing PatternOrchestrator initialization...")
    api_keys = {
        "openai": os.getenv("OPENAI_API_KEY", "test-key"),
    }
    orchestrator = PatternOrchestrator(api_keys=api_keys, pattern="gut")
    print(f"   ✅ Orchestrator created")
    print(f"   Available models: {orchestrator.available_models}")
    
    # Test pattern mapping
    print("\n3. Testing pattern mapping...")
    patterns = get_pattern_mapping()
    print(f"   ✅ Pattern mapping: {list(patterns.keys())}")
    
    # Test the route handler directly
    print("\n4. Testing route handler...")
    from backend.routes.orchestrator_routes import get_available_orchestrator_models
    import asyncio
    
    async def test_endpoint():
        result = await get_available_orchestrator_models()
        return result
    
    result = asyncio.run(test_endpoint())
    print(f"   ✅ Route result: {result}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()