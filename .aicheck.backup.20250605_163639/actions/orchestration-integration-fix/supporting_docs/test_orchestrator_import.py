#!/usr/bin/env python3
"""
Test script to verify orchestrator import functionality
"""

import os
import sys

# Add project root to path
# This script is in .aicheck/actions/orchestration-integration-fix/supporting_docs/
# So we need to go up 4 levels to get to project root
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(script_dir))))
sys.path.insert(0, project_root)
backend_dir = os.path.join(project_root, "backend")

print(f"Backend dir: {backend_dir}")
print(f"Python path: {sys.path[:3]}")

# Test the integration module import
try:
    from backend.integrations.pattern_orchestrator_integration import (
        PatternOrchestrator, 
        get_pattern_mapping, 
        ORCHESTRATOR_AVAILABLE
    )
    print(f"✅ Integration module import successful")
    print(f"   ORCHESTRATOR_AVAILABLE = {ORCHESTRATOR_AVAILABLE}")
    
    if ORCHESTRATOR_AVAILABLE:
        print("✅ PatternOrchestrator is available from src")
        
        # Test creating an instance
        test_keys = {"openai": "test-key"}
        orchestrator = PatternOrchestrator(api_keys=test_keys, pattern="gut")
        print(f"✅ PatternOrchestrator instance created")
        print(f"   Available models: {orchestrator.available_models}")
        
        # Test pattern mapping
        patterns = get_pattern_mapping()
        print(f"✅ Pattern mapping retrieved")
        print(f"   Available patterns: {list(patterns.keys())}")
    else:
        print("❌ PatternOrchestrator is using fallback implementation")
        
except Exception as e:
    print(f"❌ Import failed: {e}")
    import traceback
    traceback.print_exc()

# Test direct import from src
print("\n--- Testing direct src import ---")
try:
    # Add src to path
    src_dir = os.path.join(project_root, "src")
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)
    
    from src.core.ultra_pattern_orchestrator import PatternOrchestrator as DirectOrchestrator
    print("✅ Direct import from src successful")
except Exception as e:
    print(f"❌ Direct import failed: {e}")