#!/usr/bin/env python3
"""
Test script to verify orchestrator endpoints are working
"""

import requests
import json

# Base URL for API
BASE_URL = "http://localhost:8000/api"

def test_models_endpoint():
    """Test the models endpoint"""
    print("\n=== Testing /api/orchestrator/models ===")
    try:
        response = requests.get(f"{BASE_URL}/orchestrator/models")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Failed to connect: {e}")

def test_patterns_endpoint():
    """Test the patterns endpoint"""
    print("\n=== Testing /api/orchestrator/patterns ===")
    try:
        response = requests.get(f"{BASE_URL}/orchestrator/patterns")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Failed to connect: {e}")

def test_feather_endpoint():
    """Test the Feather orchestration endpoint"""
    print("\n=== Testing /api/orchestrator/feather ===")
    
    payload = {
        "prompt": "What is the capital of France?",
        "pattern": "gut",
        "output_format": "plain"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/orchestrator/feather",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Pattern used: {data.get('pattern_used')}")
            print(f"Models used: {data.get('models_used')}")
            print(f"Processing time: {data.get('processing_time')}s")
            print(f"Ultra response preview: {data.get('ultra_response', '')[:200]}...")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Failed to connect: {e}")

if __name__ == "__main__":
    print("Testing UltraAI Orchestrator Endpoints")
    print("Make sure the backend is running on http://localhost:8000")
    
    test_models_endpoint()
    test_patterns_endpoint()
    test_feather_endpoint()