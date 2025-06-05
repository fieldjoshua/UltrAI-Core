#!/usr/bin/env python3
"""
Test production orchestrator endpoints
This can be run on the server or locally
"""
import requests
import json
import time
import sys

# Production URL
BASE_URL = "https://ultrai-core.onrender.com"

def test_health():
    """Test basic health endpoint"""
    print("1. Testing health endpoint...")
    resp = requests.get(f"{BASE_URL}/health")
    if resp.status_code == 200:
        data = resp.json()
        print(f"   ✓ Health: {data['status']}")
        print(f"   ✓ Uptime: {data['uptime']}")
        return True
    else:
        print(f"   ✗ Health check failed: {resp.status_code}")
        return False

def test_orchestrator_health():
    """Test orchestrator health"""
    print("\n2. Testing orchestrator health...")
    resp = requests.get(f"{BASE_URL}/api/orchestrator/health")
    if resp.status_code == 200:
        data = resp.json()
        print(f"   ✓ Status: {data['status']}")
        print(f"   ✓ Adapters: {data['adapters_initialized']}")
        print(f"   ✓ Providers: {data['available_providers']}")
        return True
    else:
        print(f"   ✗ Orchestrator health failed: {resp.status_code}")
        return False

def test_models():
    """Test available models"""
    print("\n3. Testing available models...")
    resp = requests.get(f"{BASE_URL}/api/orchestrator/models")
    if resp.status_code == 200:
        data = resp.json()
        print(f"   ✓ Model count: {data['count']}")
        for model in data['models']:
            print(f"   ✓ {model['id']} ({model['provider']})")
        return True
    else:
        print(f"   ✗ Models endpoint failed: {resp.status_code}")
        return False

def test_orchestration_with_csrf():
    """Test orchestration with CSRF token"""
    print("\n4. Testing orchestration (with CSRF)...")
    
    # First, get a CSRF token by making a GET request
    session = requests.Session()
    resp = session.get(f"{BASE_URL}/api/orchestrator/health")
    
    # Extract CSRF token from headers or cookies
    csrf_token = resp.headers.get('X-CSRF-Token')
    if not csrf_token and 'csrf_token' in session.cookies:
        csrf_token = session.cookies['csrf_token']
    
    if csrf_token:
        print(f"   ✓ Got CSRF token: {csrf_token[:10]}...")
    else:
        print("   ✗ No CSRF token received")
        return False
    
    # Now make the orchestration request
    headers = {
        'Content-Type': 'application/json',
        'X-CSRF-Token': csrf_token
    }
    
    payload = {
        "prompt": "What is 2+2? Answer in exactly one word.",
        "models": ["gpt4o"],
        "args": {},
        "kwargs": {}
    }
    
    start_time = time.time()
    resp = session.post(
        f"{BASE_URL}/api/orchestrator/feather",
        headers=headers,
        json=payload
    )
    elapsed = time.time() - start_time
    
    if resp.status_code == 200:
        data = resp.json()
        print(f"   ✓ Status: {data['status']}")
        print(f"   ✓ Response time: {elapsed:.2f}s")
        
        if 'model_responses' in data:
            for model, response in data['model_responses'].items():
                print(f"   ✓ {model}: {response[:50]}...")
        
        if 'ultra_response' in data and data['ultra_response']:
            print(f"   ✓ Combined: {data['ultra_response'][:50]}...")
            
        return True
    else:
        print(f"   ✗ Orchestration failed: {resp.status_code}")
        print(f"   ✗ Response: {resp.text}")
        return False

def test_orchestration_direct():
    """Test orchestration directly (for servers with auth disabled)"""
    print("\n5. Testing direct orchestration (no CSRF)...")
    
    headers = {'Content-Type': 'application/json'}
    payload = {
        "prompt": "Say hello in Spanish. One word only.",
        "models": ["gpt4o", "claude37"],
        "args": {},
        "kwargs": {}
    }
    
    start_time = time.time()
    resp = requests.post(
        f"{BASE_URL}/api/orchestrator/feather",
        headers=headers,
        json=payload
    )
    elapsed = time.time() - start_time
    
    if resp.status_code == 200:
        data = resp.json()
        print(f"   ✓ Status: {data['status']}")
        print(f"   ✓ Response time: {elapsed:.2f}s")
        
        if elapsed < 10:
            print(f"   ✓ Performance: Under 10 seconds!")
        else:
            print(f"   ⚠ Performance: Over 10 seconds ({elapsed:.2f}s)")
            
        return True
    elif resp.status_code == 403 and "CSRF" in resp.text:
        print("   ⚠ CSRF protection is enabled")
        return None  # Not a failure, just informational
    else:
        print(f"   ✗ Request failed: {resp.status_code}")
        print(f"   ✗ Response: {resp.text[:200]}")
        return False

def main():
    """Run all tests"""
    print("=== Production Orchestrator Tests ===")
    print(f"Target: {BASE_URL}\n")
    
    results = []
    
    # Basic tests
    results.append(("Health", test_health()))
    results.append(("Orchestrator Health", test_orchestrator_health()))
    results.append(("Available Models", test_models()))
    
    # Try direct orchestration first
    direct_result = test_orchestration_direct()
    if direct_result is None:
        # CSRF is enabled, try with token
        results.append(("Orchestration", test_orchestration_with_csrf()))
    else:
        results.append(("Orchestration", direct_result))
    
    # Summary
    print("\n=== Test Summary ===")
    passed = sum(1 for _, result in results if result is True)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} - {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())