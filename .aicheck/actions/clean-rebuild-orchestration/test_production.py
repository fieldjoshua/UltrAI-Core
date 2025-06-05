#!/usr/bin/env python3
"""Test production orchestrator endpoint"""
import requests
import json
import time

# Production URL
BASE_URL = "https://ultrai-core.onrender.com"

def test_orchestrator_health():
    """Test orchestrator health endpoint"""
    url = f"{BASE_URL}/api/orchestrator/health"
    print(f"Testing {url}...")
    
    try:
        response = requests.get(url, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_orchestrator_feather():
    """Test orchestrator feather endpoint"""
    url = f"{BASE_URL}/api/orchestrator/feather"
    
    payload = {
        "prompt": "What are the three most important things about artificial intelligence?",
        "models": ["gpt4o", "claude37"],
        "args": {
            "pattern": "gut",
            "ultra_model": "gpt4o",
            "output_format": "txt"
        },
        "kwargs": {}
    }
    
    print(f"\nTesting {url}...")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        start = time.time()
        response = requests.post(url, json=payload, timeout=60)
        elapsed = time.time() - start
        
        print(f"\nStatus: {response.status_code}")
        print(f"Time: {elapsed:.2f}s")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\nResponse structure:")
            print(f"- Status: {data.get('status')}")
            print(f"- Has model_responses: {'model_responses' in data}")
            print(f"- Has ultra_response: {'ultra_response' in data}")
            print(f"- Has performance: {'performance' in data}")
            
            if 'model_responses' in data:
                print(f"\nModel responses:")
                for model, resp in data['model_responses'].items():
                    print(f"- {model}: {resp[:100]}...")
            
            if 'ultra_response' in data:
                print(f"\nUltra response (first 200 chars):")
                print(data['ultra_response'][:200] + "...")
            
            if 'performance' in data:
                print(f"\nPerformance:")
                print(json.dumps(data['performance'], indent=2))
        else:
            print(f"Error response: {response.text}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    print("Testing production orchestrator at", BASE_URL)
    print("=" * 60)
    
    # Test health first
    health_ok = test_orchestrator_health()
    
    if health_ok:
        # Test main endpoint
        feather_ok = test_orchestrator_feather()
        
        if feather_ok:
            print("\n✅ Production orchestrator is working!")
        else:
            print("\n❌ Orchestrator endpoint failed")
    else:
        print("\n❌ Health check failed")

if __name__ == "__main__":
    main()