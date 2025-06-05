#!/usr/bin/env python3
"""Test a minimal endpoint to debug the timeout"""
import requests
import json
import time

BASE_URL = "https://ultrai-core.onrender.com"

def test_root():
    """Test root endpoint"""
    url = BASE_URL
    print(f"Testing {url}...")
    
    try:
        response = requests.get(url, timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.text[:200]}...")
        else:
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

def test_health():
    """Test general health endpoint"""
    url = f"{BASE_URL}/health"
    print(f"\nTesting {url}...")
    
    try:
        response = requests.get(url, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

def test_llm_health():
    """Test LLM health check"""
    url = f"{BASE_URL}/api/health/llm"
    print(f"\nTesting {url}...")
    
    try:
        response = requests.get(url, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

def test_minimal_feather():
    """Test with minimal payload"""
    url = f"{BASE_URL}/api/orchestrator/feather"
    
    # Absolute minimal payload
    payload = {
        "prompt": "Hi",
        "models": ["gpt4o"]
    }
    
    print(f"\nTesting {url} with minimal payload...")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        start = time.time()
        response = requests.post(url, json=payload, timeout=15)
        elapsed = time.time() - start
        
        print(f"Status: {response.status_code}")
        print(f"Time: {elapsed:.2f}s")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response keys: {list(data.keys())}")
            print(f"Status: {data.get('status')}")
        else:
            print(f"Error: {response.text[:500]}")
    except requests.exceptions.Timeout:
        elapsed = time.time() - start
        print(f"Timeout after {elapsed:.2f}s")
    except Exception as e:
        print(f"Error: {e}")

def main():
    print("Testing production endpoints")
    print("=" * 60)
    
    test_root()
    test_health()
    test_llm_health()
    test_minimal_feather()

if __name__ == "__main__":
    main()