#!/usr/bin/env python3
"""
Debug script to test orchestrator imports in production environment
"""

import sys
import os

print(f"Python version: {sys.version}")
print(f"Current working directory: {os.getcwd()}")
print(f"Python path: {sys.path}")

try:
    print("\n🔍 Testing orchestrator imports...")
    
    # Test basic import
    from backend.routes.orchestrator_routes import orchestrator_router
    print(f"✅ orchestrator_router imported successfully")
    print(f"📊 Number of routes: {len(orchestrator_router.routes)}")
    
    # List route details
    for i, route in enumerate(orchestrator_router.routes):
        print(f"  Route {i+1}: {route.methods} {route.path}")
    
    # Test integration import specifically
    from backend.integrations.pattern_orchestrator_integration import ORCHESTRATOR_AVAILABLE
    print(f"✅ ORCHESTRATOR_AVAILABLE: {ORCHESTRATOR_AVAILABLE}")
    
except Exception as e:
    print(f"❌ Import error: {e}")
    import traceback
    traceback.print_exc()