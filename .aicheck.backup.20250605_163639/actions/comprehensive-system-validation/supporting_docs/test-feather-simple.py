#!/usr/bin/env python3
"""
Simple Test Script: 4-Stage Feather Orchestration Validation
Uses only standard library modules for portability
"""

import json
import urllib.request
import urllib.error
import time
from datetime import datetime
import sys
import os

# Test configuration
BASE_URL = os.getenv("ULTRAI_BASE_URL", "http://localhost:8000")
if len(sys.argv) > 1 and sys.argv[1] == "--deployed":
    BASE_URL = "https://ultrai-core.onrender.com"

# Test cases
TEST_CASES = [
    {
        "name": "Basic Gut Analysis",
        "prompt": "What is the capital of France?",
        "pattern": "gut"
    },
    {
        "name": "Confidence Analysis",
        "prompt": "Is artificial intelligence beneficial for humanity?",
        "pattern": "confidence"
    },
    {
        "name": "Critique Analysis", 
        "prompt": "Analyze the pros and cons of remote work",
        "pattern": "critique"
    },
    {
        "name": "Fact Check Analysis",
        "prompt": "What are the main causes of climate change?",
        "pattern": "fact_check"
    }
]

def make_request(url, method="GET", data=None, timeout=30):
    """Make HTTP request with error handling"""
    try:
        headers = {"Content-Type": "application/json"}
        
        if data:
            data = json.dumps(data).encode('utf-8')
            
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return {
                "status": response.status,
                "data": json.loads(response.read().decode('utf-8'))
            }
    except urllib.error.HTTPError as e:
        return {
            "status": e.code,
            "error": e.reason,
            "data": json.loads(e.read().decode('utf-8')) if e.read() else None
        }
    except Exception as e:
        return {
            "status": 0,
            "error": str(e)
        }

def test_available_models():
    """Test available models endpoint"""
    print("\n🔍 Testing Available Models...")
    
    result = make_request(f"{BASE_URL}/api/orchestrator/models")
    
    if result["status"] == 200:
        models = result["data"].get("models", [])
        print(f"✅ Found {len(models)} models: {models}")
        return True, models
    else:
        print(f"❌ Failed to get models: {result.get('error', 'Unknown error')}")
        return False, []

def test_available_patterns():
    """Test available patterns endpoint"""
    print("\n🔍 Testing Available Patterns...")
    
    result = make_request(f"{BASE_URL}/api/orchestrator/patterns")
    
    if result["status"] == 200:
        patterns = result["data"].get("patterns", [])
        print(f"✅ Found {len(patterns)} patterns:")
        for pattern in patterns:
            print(f"   - {pattern['name']}: {pattern['description']}")
        return True, patterns
    else:
        print(f"❌ Failed to get patterns: {result.get('error', 'Unknown error')}")
        return False, []

def test_feather_orchestration(prompt, pattern="gut"):
    """Test Feather orchestration endpoint"""
    print(f"\n🚀 Testing Feather Orchestration (pattern: {pattern})...")
    print(f"   Prompt: {prompt[:80]}...")
    
    data = {
        "prompt": prompt,
        "pattern": pattern,
        "output_format": "plain"
    }
    
    start_time = time.time()
    result = make_request(
        f"{BASE_URL}/api/orchestrator/feather",
        method="POST",
        data=data,
        timeout=120
    )
    elapsed = time.time() - start_time
    
    if result["status"] == 200:
        response_data = result["data"]
        
        # Validate 4-stage structure
        required_fields = ["initial_responses", "meta_responses", "hyper_responses", "ultra_response"]
        missing = [f for f in required_fields if f not in response_data]
        
        if not missing:
            print(f"✅ Orchestration completed in {elapsed:.2f}s")
            print(f"   Models used: {response_data.get('models_used', [])}")
            print(f"   Ultra response preview: {response_data['ultra_response'][:150]}...")
            
            # Show stage progression
            print("\n   Stage Progression:")
            print(f"   1. Initial: {len(response_data['initial_responses'])} model responses")
            print(f"   2. Meta: {len(response_data['meta_responses'])} analyses")
            print(f"   3. Hyper: {len(response_data['hyper_responses'])} syntheses")
            print(f"   4. Ultra: Final orchestrated response")
            
            return True
        else:
            print(f"❌ Missing stages: {missing}")
            return False
    else:
        print(f"❌ Orchestration failed: {result.get('error', 'Unknown error')}")
        if result.get("data"):
            print(f"   Details: {result['data']}")
        return False

def run_all_tests():
    """Run all validation tests"""
    print("="*60)
    print("🚀 4-Stage Feather Orchestration Validation")
    print(f"📍 Target: {BASE_URL}")
    print(f"🕐 Started: {datetime.now().isoformat()}")
    print("="*60)
    
    results = {
        "passed": 0,
        "failed": 0,
        "tests": []
    }
    
    # Test 1: Available models
    success, models = test_available_models()
    results["tests"].append(("Available Models", success))
    if success:
        results["passed"] += 1
    else:
        results["failed"] += 1
    
    # Test 2: Available patterns
    success, patterns = test_available_patterns()
    results["tests"].append(("Available Patterns", success))
    if success:
        results["passed"] += 1
    else:
        results["failed"] += 1
    
    # Test 3: Feather orchestration tests
    for test_case in TEST_CASES:
        print(f"\n{'='*60}")
        print(f"📝 Test Case: {test_case['name']}")
        print(f"{'='*60}")
        
        success = test_feather_orchestration(
            test_case["prompt"],
            test_case["pattern"]
        )
        
        results["tests"].append((test_case["name"], success))
        if success:
            results["passed"] += 1
        else:
            results["failed"] += 1
        
        # Small delay between tests
        time.sleep(2)
    
    # Print summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    print(f"Total Tests: {len(results['tests'])}")
    print(f"Passed: {results['passed']}")
    print(f"Failed: {results['failed']}")
    print(f"Success Rate: {(results['passed'] / len(results['tests']) * 100):.1f}%")
    print("\nDetailed Results:")
    for test_name, success in results["tests"]:
        icon = "✅" if success else "❌"
        print(f"  {icon} {test_name}")
    print("="*60)
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"/Users/joshuafield/Documents/Ultra/.aicheck/actions/comprehensive-system-validation/supporting_docs/test-reports/simple_test_{timestamp}.json"
    
    os.makedirs(os.path.dirname(results_file), exist_ok=True)
    
    with open(results_file, "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "base_url": BASE_URL,
            "results": results
        }, f, indent=2)
    
    print(f"\n💾 Results saved to: {results_file}")
    
    return results["failed"] == 0

if __name__ == "__main__":
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {str(e)}")
        sys.exit(1)