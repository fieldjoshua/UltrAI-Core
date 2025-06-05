#!/usr/bin/env python3
"""
Test the orchestrator endpoints using test mode to bypass API authentication
"""

import requests
import json

BASE_URL = "http://localhost:8081/api"

def test_endpoint(endpoint, method="GET", data=None):
    """Test an endpoint with test mode header"""
    headers = {
        "X-Test-Mode": "true",
        "Content-Type": "application/json"
    }
    
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data)
        
        print(f"\n✅ {method} {endpoint}")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"   Response: {json.dumps(response.json(), indent=2)}")
        else:
            print(f"   Error: {response.text}")
            
        return response
        
    except requests.exceptions.ConnectionError:
        print(f"\n❌ {method} {endpoint}")
        print(f"   Error: Connection refused. Is the server running on {BASE_URL}?")
        return None
    except Exception as e:
        print(f"\n❌ {method} {endpoint}")
        print(f"   Error: {e}")
        return None

def main():
    """Test all orchestrator endpoints"""
    print("🧪 Testing Orchestrator Endpoints in Test Mode")
    print("=" * 50)
    
    # Test 1: Get available models
    print("\n1️⃣ Testing model registry endpoint:")
    test_endpoint("/orchestrator/models")
    
    # Test 2: Get available patterns
    print("\n2️⃣ Testing pattern registry endpoint:")
    test_endpoint("/orchestrator/patterns")
    
    # Test 3: Test 4-stage feather orchestration
    print("\n3️⃣ Testing 4-stage feather orchestration:")
    test_data = {
        "prompt": "What is the meaning of life?",
        "models": ["gpt-3.5-turbo", "gpt-4"],
        "pattern": "gut"
    }
    test_endpoint("/orchestrator/feather", method="POST", data=test_data)
    
    # Test 4: Test direct process endpoint
    print("\n4️⃣ Testing direct process endpoint:")
    process_data = {
        "prompt": "Explain quantum computing in simple terms",
        "models": ["gpt-3.5-turbo"],
        "pattern": "confidence"
    }
    test_endpoint("/orchestrator/process", method="POST", data=process_data)

if __name__ == "__main__":
    main()