#!/usr/bin/env python3
"""
Test script to verify orchestrator endpoints in production
"""

import requests
import json
import time
from datetime import datetime

# Production URL
PROD_URL = "https://ultrai-core.onrender.com"

def test_health():
    """Test basic health endpoint"""
    print("\n=== Testing Health Endpoint ===")
    try:
        response = requests.get(f"{PROD_URL}/health", timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
            return True
        else:
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"Failed to connect: {e}")
        return False

def test_models_endpoint():
    """Test the models endpoint"""
    print("\n=== Testing /api/orchestrator/models ===")
    try:
        response = requests.get(f"{PROD_URL}/api/orchestrator/models", timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Available models: {data.get('models', [])}")
            return True, data.get('models', [])
        else:
            print(f"Error: {response.text}")
            return False, []
    except Exception as e:
        print(f"Failed to connect: {e}")
        return False, []

def test_patterns_endpoint():
    """Test the patterns endpoint"""
    print("\n=== Testing /api/orchestrator/patterns ===")
    try:
        response = requests.get(f"{PROD_URL}/api/orchestrator/patterns", timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            patterns = data.get('patterns', [])
            print(f"Available patterns ({len(patterns)}):")
            for pattern in patterns:
                print(f"  - {pattern.get('name')}: {pattern.get('description')}")
            return True, patterns
        else:
            print(f"Error: {response.text}")
            return False, []
    except Exception as e:
        print(f"Failed to connect: {e}")
        return False, []

def test_feather_endpoint(prompt="What is the meaning of life?", pattern="gut"):
    """Test the Feather orchestration endpoint"""
    print(f"\n=== Testing /api/orchestrator/feather with pattern '{pattern}' ===")
    
    payload = {
        "prompt": prompt,
        "pattern": pattern,
        "output_format": "plain"
    }
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{PROD_URL}/api/orchestrator/feather",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=60  # Longer timeout for orchestration
        )
        end_time = time.time()
        
        print(f"Status: {response.status_code}")
        print(f"Response time: {end_time - start_time:.2f}s")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Pattern used: {data.get('pattern_used')}")
            print(f"Models used: {data.get('models_used')}")
            print(f"Processing time: {data.get('processing_time')}s")
            
            # Check for 4-stage responses
            has_initial = bool(data.get('initial_responses'))
            has_meta = bool(data.get('meta_responses'))
            has_hyper = bool(data.get('hyper_responses'))
            has_ultra = bool(data.get('ultra_response'))
            
            print(f"\n4-Stage Feather Analysis:")
            print(f"  ✓ Initial responses: {'Yes' if has_initial else 'No'}")
            print(f"  ✓ Meta responses: {'Yes' if has_meta else 'No'}")
            print(f"  ✓ Hyper responses: {'Yes' if has_hyper else 'No'}")
            print(f"  ✓ Ultra response: {'Yes' if has_ultra else 'No'}")
            
            if has_ultra:
                print(f"\nUltra response preview: {data.get('ultra_response', '')[:200]}...")
            
            return True
        else:
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"Failed to connect: {e}")
        return False

def main():
    print("=" * 60)
    print("UltraAI Production Orchestrator Verification")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"Production URL: {PROD_URL}")
    print("=" * 60)
    
    results = {
        "health": False,
        "models": False,
        "patterns": False,
        "feather": False,
        "models_list": [],
        "patterns_list": []
    }
    
    # Test health first
    results["health"] = test_health()
    
    if not results["health"]:
        print("\n❌ Health check failed - server may be down or deploying")
        return results
    
    # Test models endpoint
    success, models = test_models_endpoint()
    results["models"] = success
    results["models_list"] = models
    
    # Test patterns endpoint
    success, patterns = test_patterns_endpoint()
    results["patterns"] = success
    results["patterns_list"] = patterns
    
    # Test feather orchestration with a simple prompt
    if results["models"] and results["patterns"]:
        results["feather"] = test_feather_endpoint()
    else:
        print("\n⚠️ Skipping Feather test - models or patterns endpoint failed")
    
    # Summary
    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)
    print(f"✓ Health Check: {'PASS' if results['health'] else 'FAIL'}")
    print(f"✓ Models Endpoint: {'PASS' if results['models'] else 'FAIL'}")
    print(f"✓ Patterns Endpoint: {'PASS' if results['patterns'] else 'FAIL'}")
    print(f"✓ Feather Orchestration: {'PASS' if results['feather'] else 'FAIL'}")
    
    if results["models"]:
        print(f"\nModels available: {len(results['models_list'])}")
    if results["patterns"]:
        print(f"Patterns available: {len(results['patterns_list'])}")
    
    overall_pass = all([results["health"], results["models"], results["patterns"]])
    print(f"\nOverall Status: {'✅ PASS' if overall_pass else '❌ FAIL'}")
    
    return results

if __name__ == "__main__":
    main()