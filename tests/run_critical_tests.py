#!/usr/bin/env python3
"""
Run the most critical tests for UltrAI system verification.
"""

import subprocess
import sys
from pathlib import Path

def run_test_file(test_file: str, test_name: str = None):
    """Run a specific test file or test within a file."""
    cmd = ["python", "-m", "pytest", test_file, "-v", "--tb=short"]
    
    if test_name:
        cmd.extend(["-k", test_name])
    
    print(f"\n{'='*60}")
    print(f"Running: {' '.join(cmd)}")
    print(f"{'='*60}")
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    return result.returncode == 0

def main():
    """Run the critical tests in order of importance."""
    
    test_root = Path(__file__).parent
    all_passed = True
    
    critical_tests = [
        # Test 1: Original prompt preservation (the fix we made)
        {
            "file": "test_ultrai_synthesis_implementation.py",
            "test": "test_synthesis_preserves_original_prompt",
            "description": "Verify synthesis correctly shows user's original query"
        },
        
        # Test 2: Three-stage pipeline execution
        {
            "file": "test_ultrai_synthesis_implementation.py", 
            "test": "test_three_stage_pipeline_execution",
            "description": "Verify Initial → Peer Review → Synthesis pipeline"
        },
        
        # Test 3: Model availability requirements
        {
            "file": "test_ultrai_universal_flow.py",
            "test": "test_initialization_sufficient_models",
            "description": "Verify 2-model minimum, 3-model target requirement"
        },
        
        # Test 4: Peer review skipping logic
        {
            "file": "test_ultrai_synthesis_implementation.py",
            "test": "test_peer_review_skipped_with_insufficient_models",
            "description": "Verify peer review skips when < 3 models"
        },
        
        # Test 5: Synthesis combines all outputs
        {
            "file": "test_ultrai_synthesis_implementation.py",
            "test": "test_synthesis_combines_all_model_outputs", 
            "description": "Verify synthesis integrates all model responses"
        }
    ]
    
    print("\n" + "="*60)
    print("ULTRAI CRITICAL TEST SUITE")
    print("="*60)
    
    for i, test in enumerate(critical_tests, 1):
        print(f"\n[{i}/{len(critical_tests)}] {test['description']}")
        
        test_file = test_root / test["file"]
        if not test_file.exists():
            print(f"❌ Test file not found: {test_file}")
            all_passed = False
            continue
        
        passed = run_test_file(str(test_file), test["test"])
        
        if passed:
            print(f"✅ PASSED: {test['description']}")
        else:
            print(f"❌ FAILED: {test['description']}")
            all_passed = False
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    if all_passed:
        print("✅ All critical tests passed!")
        return 0
    else:
        print("❌ Some tests failed. Review output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())