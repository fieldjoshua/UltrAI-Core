#!/usr/bin/env python3
"""Verify basic production orchestrator functionality with stub adapters"""
import requests
import json
import time

# Production URL
BASE_URL = "https://ultrai-core.onrender.com"

def test_basic_functionality():
    """Test with a simple prompt that should work even with stubs"""
    url = f"{BASE_URL}/api/orchestrator/feather"
    
    # Use a very simple prompt
    payload = {
        "prompt": "Hello",
        "models": ["gpt4o"],
        "args": {
            "pattern": "gut",
            "ultra_model": "gpt4o",
            "output_format": "txt"
        },
        "kwargs": {}
    }
    
    print(f"Testing {url}...")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        start = time.time()
        response = requests.post(url, json=payload, timeout=30)
        elapsed = time.time() - start
        
        print(f"\nStatus: {response.status_code}")
        print(f"Time: {elapsed:.2f}s")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\nResponse structure:")
            print(f"- Status: {data.get('status')}")
            print(f"- Model responses count: {len(data.get('model_responses', {}))}")
            print(f"- Has ultra_response: {'ultra_response' in data}")
            
            if 'model_responses' in data:
                print(f"\nModel responses:")
                for model, resp in data['model_responses'].items():
                    print(f"- {model}: {resp[:100]}...")
            
            if 'ultra_response' in data:
                print(f"\nUltra response:")
                print(data['ultra_response'][:200] + "...")
            
            return True
        else:
            print(f"Error response: {response.text}")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_available_models():
    """Test listing available models"""
    url = f"{BASE_URL}/api/orchestrator/models"
    print(f"\nTesting {url}...")
    
    try:
        response = requests.get(url, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\nAvailable models: {data.get('count', 0)}")
            for model in data.get('models', []):
                print(f"- {model['name']} ({model['provider']})")
            return True
        else:
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    print("Testing production orchestrator (with stub adapters)")
    print("=" * 60)
    
    # Test health
    health_url = f"{BASE_URL}/api/orchestrator/health"
    print(f"Testing {health_url}...")
    
    try:
        response = requests.get(health_url, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test available models
    test_available_models()
    
    # Test basic functionality
    print("\n" + "=" * 60)
    basic_ok = test_basic_functionality()
    
    if basic_ok:
        print("\n✅ Basic production orchestrator is working!")
        print("Note: Using stub adapters - real LLM responses require API keys")
    else:
        print("\n❌ Orchestrator test failed")

if __name__ == "__main__":
    main()