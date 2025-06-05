#!/usr/bin/env python3
"""
Test Deployed Service: UltraAI Core on Render
Tests the deployed service endpoints
"""

import json
import subprocess
import sys
import time
from datetime import datetime

BASE_URL = "https://ultrai-core.onrender.com"

def curl_request(url, method="GET", data=None):
    """Make request using curl command"""
    cmd = ["curl", "-s", "-X", method]
    
    if data:
        cmd.extend(["-H", "Content-Type: application/json"])
        cmd.extend(["-d", json.dumps(data)])
    
    cmd.append(url)
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            try:
                return {"status": "success", "data": json.loads(result.stdout)}
            except json.JSONDecodeError:
                return {"status": "success", "data": result.stdout}
        else:
            return {"status": "error", "error": result.stderr}
    except Exception as e:
        return {"status": "error", "error": str(e)}

def test_health_endpoint():
    """Test health check endpoint"""
    print("\n🏥 Testing Health Endpoint...")
    
    # Try different possible health endpoints
    endpoints = ["/", "/health", "/api/health"]
    
    for endpoint in endpoints:
        result = curl_request(f"{BASE_URL}{endpoint}")
        if result["status"] == "success":
            print(f"✅ {endpoint} is accessible")
            if isinstance(result["data"], dict):
                print(f"   Response: {json.dumps(result['data'], indent=2)}")
            else:
                print(f"   Response: HTML page received (service is running)")
            return True
    
    print("❌ No health endpoint found")
    return False

def test_orchestrator_models():
    """Test available models endpoint"""
    print("\n🤖 Testing Available Models Endpoint...")
    
    result = curl_request(f"{BASE_URL}/api/orchestrator/models")
    
    if result["status"] == "success" and isinstance(result["data"], dict):
        if result["data"].get("status") == "success":
            models = result["data"].get("models", [])
            print(f"✅ Found {len(models)} models: {models}")
            return True, models
        else:
            print(f"❌ Models endpoint returned error: {result['data']}")
            return False, []
    else:
        print(f"❌ Failed to access models endpoint: {result.get('error', 'Unknown error')}")
        return False, []

def test_orchestrator_patterns():
    """Test available patterns endpoint"""
    print("\n🎨 Testing Available Patterns Endpoint...")
    
    result = curl_request(f"{BASE_URL}/api/orchestrator/patterns")
    
    if result["status"] == "success" and isinstance(result["data"], dict):
        if result["data"].get("status") == "success":
            patterns = result["data"].get("patterns", [])
            print(f"✅ Found {len(patterns)} patterns:")
            for pattern in patterns:
                print(f"   - {pattern['name']}: {pattern['description']}")
            return True, patterns
        else:
            print(f"❌ Patterns endpoint returned error: {result['data']}")
            return False, []
    else:
        print(f"❌ Failed to access patterns endpoint: {result.get('error', 'Unknown error')}")
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
    result = curl_request(f"{BASE_URL}/api/orchestrator/feather", method="POST", data=data)
    elapsed = time.time() - start_time
    
    if result["status"] == "success" and isinstance(result["data"], dict):
        if result["data"].get("status") == "success":
            # Validate 4-stage structure
            required_fields = ["initial_responses", "meta_responses", "hyper_responses", "ultra_response"]
            missing = [f for f in required_fields if f not in result["data"]]
            
            if not missing:
                print(f"✅ Orchestration completed in {elapsed:.2f}s")
                print(f"   Models used: {result['data'].get('models_used', [])}")
                
                # Show response preview
                ultra_response = result["data"]["ultra_response"]
                preview = ultra_response[:200] + "..." if len(ultra_response) > 200 else ultra_response
                print(f"   Ultra response: {preview}")
                
                # Show stage sizes
                print("\n   📊 Stage Analysis:")
                print(f"   - Initial: {len(result['data']['initial_responses'])} models")
                print(f"   - Meta: {len(result['data']['meta_responses'])} analyses")
                print(f"   - Hyper: {len(result['data']['hyper_responses'])} syntheses")
                print(f"   - Ultra: Final orchestrated response")
                
                return True
            else:
                print(f"❌ Missing stages: {missing}")
                return False
        else:
            print(f"❌ Orchestration returned error: {result['data']}")
            return False
    else:
        print(f"❌ Failed to access orchestration endpoint: {result.get('error', 'Unknown error')}")
        return False

def run_all_tests():
    """Run all validation tests"""
    print("="*60)
    print("🚀 UltraAI Deployed Service Validation")
    print(f"📍 Target: {BASE_URL}")
    print(f"🕐 Started: {datetime.now().isoformat()}")
    print("="*60)
    
    results = {
        "passed": 0,
        "failed": 0,
        "tests": []
    }
    
    # Test 1: Health check
    success = test_health_endpoint()
    results["tests"].append(("Health Check", success))
    if success:
        results["passed"] += 1
    else:
        results["failed"] += 1
        print("\n⚠️  Service may not be accessible. Stopping tests.")
        return results
    
    # Test 2: Available models
    success, models = test_orchestrator_models()
    results["tests"].append(("Available Models", success))
    if success:
        results["passed"] += 1
    else:
        results["failed"] += 1
    
    # Test 3: Available patterns
    success, patterns = test_orchestrator_patterns()
    results["tests"].append(("Available Patterns", success))
    if success:
        results["passed"] += 1
    else:
        results["failed"] += 1
    
    # Test 4: Feather orchestration tests
    test_cases = [
        {
            "name": "Basic Gut Analysis",
            "prompt": "What is the capital of France?",
            "pattern": "gut"
        },
        {
            "name": "Confidence Analysis",
            "prompt": "Explain the benefits of renewable energy",
            "pattern": "confidence"
        },
        {
            "name": "Critique Analysis",
            "prompt": "What are the limitations of current AI technology?",
            "pattern": "critique"
        }
    ]
    
    for test_case in test_cases:
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
    results_file = f"/Users/joshuafield/Documents/Ultra/.aicheck/actions/comprehensive-system-validation/supporting_docs/test-reports/deployed_test_{timestamp}.json"
    
    with open(results_file, "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "base_url": BASE_URL,
            "results": results
        }, f, indent=2)
    
    print(f"\n💾 Results saved to: {results_file}")
    
    return results

if __name__ == "__main__":
    try:
        results = run_all_tests()
        
        # Update todo based on results
        if results["passed"] > 0:
            print("\n✅ Some tests passed! The deployed service is partially functional.")
        
        if results["failed"] > 0:
            print("\n⚠️  Some tests failed. Review the results for details.")
            sys.exit(1)
        else:
            sys.exit(0)
            
    except KeyboardInterrupt:
        print("\n\n⚠️ Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {str(e)}")
        sys.exit(1)