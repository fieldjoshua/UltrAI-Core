#!/usr/bin/env python3
"""Test script to verify UltraAI deployment is working"""

import requests
import json
from datetime import datetime

# Configuration
BACKEND_URL = "https://ultrai-core-4lut.onrender.com"
FRONTEND_URL = "https://ultr-ai-core.vercel.app"

def test_backend_health():
    """Test if backend is responding"""
    print("\n=== Testing Backend Health ===")
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=10)
        print(f"✅ Health endpoint: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Backend health check failed: {e}")
        return False

def test_orchestrator_access():
    """Test if orchestrator endpoints are accessible"""
    print("\n=== Testing Orchestrator Access ===")
    endpoints = [
        "/api/orchestrator/models",
        "/api/orchestrator/patterns",
    ]
    
    results = {}
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BACKEND_URL}{endpoint}", timeout=10)
            results[endpoint] = response.status_code
            print(f"{'✅' if response.status_code == 200 else '❌'} {endpoint}: {response.status_code}")
            if response.status_code == 401:
                print(f"   ⚠️  Auth blocking despite public paths!")
        except Exception as e:
            results[endpoint] = str(e)
            print(f"❌ {endpoint}: {e}")
    
    return results

def test_frontend_deployment():
    """Test if frontend is deployed and loading"""
    print("\n=== Testing Frontend Deployment ===")
    try:
        response = requests.get(FRONTEND_URL, timeout=10)
        print(f"✅ Frontend loads: {response.status_code}")
        
        # Check if it contains React app markers
        if "root" in response.text and ("vite" in response.text or "react" in response.text):
            print("   ✅ React app detected")
        else:
            print("   ❌ React app not detected in response")
            
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Frontend check failed: {e}")
        return False

def test_cors_headers():
    """Test CORS configuration"""
    print("\n=== Testing CORS Headers ===")
    try:
        response = requests.options(
            f"{BACKEND_URL}/api/orchestrator/models",
            headers={"Origin": FRONTEND_URL}
        )
        
        cors_headers = {
            "Access-Control-Allow-Origin": response.headers.get("Access-Control-Allow-Origin"),
            "Access-Control-Allow-Methods": response.headers.get("Access-Control-Allow-Methods"),
            "Access-Control-Allow-Headers": response.headers.get("Access-Control-Allow-Headers"),
        }
        
        for header, value in cors_headers.items():
            if value:
                print(f"✅ {header}: {value}")
            else:
                print(f"❌ {header}: Not set")
                
        return cors_headers["Access-Control-Allow-Origin"] is not None
    except Exception as e:
        print(f"❌ CORS test failed: {e}")
        return False

def main():
    """Run all deployment tests"""
    print(f"\n🚀 UltraAI Deployment Test - {datetime.now()}")
    print(f"Backend: {BACKEND_URL}")
    print(f"Frontend: {FRONTEND_URL}")
    
    results = {
        "backend_health": test_backend_health(),
        "orchestrator_access": test_orchestrator_access(),
        "frontend_deployment": test_frontend_deployment(),
        "cors_configured": test_cors_headers(),
    }
    
    print("\n=== Summary ===")
    all_passed = True
    for test, result in results.items():
        if isinstance(result, bool):
            status = "✅ PASS" if result else "❌ FAIL"
            if not result:
                all_passed = False
        else:
            status = "⚠️  MIXED"
            all_passed = False
        print(f"{status}: {test}")
    
    if all_passed:
        print("\n🎉 All tests passed! Deployment is working.")
    else:
        print("\n❌ Some tests failed. Check the output above for details.")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    exit(main())