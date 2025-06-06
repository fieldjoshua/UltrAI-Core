#!/usr/bin/env python3
"""
Simple test runner for orchestration tests
Runs specific tests to verify orchestration is working
"""

import subprocess
import sys
import os


def run_tests():
    """Run orchestration tests"""
    print("🧪 Running Orchestration Tests")
    print("=" * 50)
    
    # Install test requirements if needed
    print("\n📦 Installing test requirements...")
    subprocess.run([
        sys.executable, "-m", "pip", "install", "-q",
        "pytest", "pytest-asyncio", "pytest-timeout", "httpx"
    ])
    
    # Run specific tests
    test_commands = [
        # Quick health check
        [sys.executable, "-m", "pytest", "-xvs", "test_orchestration_production.py::TestOrchestrationProduction::test_health_endpoint"],
        
        # Models and patterns
        [sys.executable, "-m", "pytest", "-xvs", "test_orchestration_production.py::TestOrchestrationProduction::test_models_endpoint"],
        [sys.executable, "-m", "pytest", "-xvs", "test_orchestration_production.py::TestOrchestrationProduction::test_patterns_endpoint"],
        
        # The critical test - does orchestration actually work?
        [sys.executable, "-m", "pytest", "-xvs", "--timeout=60", "test_orchestration_production.py::TestOrchestrationProduction::test_feather_orchestration_simple"],
    ]
    
    results = []
    for cmd in test_commands:
        test_name = cmd[-1].split("::")[-1]
        print(f"\n🔍 Running: {test_name}")
        print("-" * 40)
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ PASSED: {test_name}")
            results.append((test_name, "PASSED"))
        else:
            print(f"❌ FAILED: {test_name}")
            print("STDOUT:", result.stdout[-500:])  # Last 500 chars
            print("STDERR:", result.stderr[-500:])
            results.append((test_name, "FAILED"))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    for test, status in results:
        emoji = "✅" if status == "PASSED" else "❌"
        print(f"  {emoji} {test}: {status}")
    
    # Overall result
    failed = sum(1 for _, status in results if status == "FAILED")
    if failed == 0:
        print(f"\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n❌ {failed} tests failed!")
        return 1


if __name__ == "__main__":
    # Change to tests directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    sys.exit(run_tests())