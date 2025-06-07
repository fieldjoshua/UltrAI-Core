#!/usr/bin/env python3
"""
Test production orchestration endpoint after fixes
"""

import requests
import json
import time
from datetime import datetime

def test_production_orchestration():
    """Test the production orchestration endpoint"""
    print("=== Testing Production Orchestration ===")
    print(f"Time: {datetime.now()}")
    
    # Production URL
    url = "https://ultrai-core.onrender.com/api/orchestrator/feather"
    
    # Test data
    test_data = {
        "prompt": "What is 2+2? Give a brief answer.",
        "pattern": "gut"
    }
    
    print(f"\nTesting endpoint: {url}")
    print(f"Prompt: {test_data['prompt']}")
    
    try:
        # Send request
        print("\nSending request...")
        start_time = time.time()
        
        response = requests.post(
            url,
            json=test_data,
            timeout=330  # 5.5 minutes to be safe
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\nResponse received in {duration:.2f} seconds")
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("\n✅ SUCCESS! Orchestration completed")
            print(f"\nProcessing time: {result.get('processing_time', 'N/A')} seconds")
            print(f"Pattern used: {result.get('pattern_used', 'N/A')}")
            print(f"Models used: {result.get('models_used', [])}")
            
            # Show responses
            if 'initial_responses' in result:
                print("\nInitial responses:")
                for model, resp in result['initial_responses'].items():
                    print(f"- {model}: {resp[:100]}...")
                    
            print(f"\nUltra response: {result.get('ultra_response', 'N/A')[:200]}...")
            
            # Check if it was parallel
            if len(result.get('models_used', [])) > 1 and duration < 30:
                print("\n✅ PARALLEL EXECUTION CONFIRMED in production!")
            
        else:
            print(f"\n❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("\n❌ Request timed out after 5.5 minutes")
    except Exception as e:
        print(f"\n❌ Error: {type(e).__name__}: {e}")

def check_deployment_status():
    """Check if new code is deployed"""
    print("\n=== Checking Deployment Status ===")
    
    # Test endpoint to see if router is working
    test_url = "https://ultrai-core.onrender.com/api/orchestrator/test"
    
    try:
        response = requests.get(test_url, timeout=10)
        if response.status_code == 200:
            print("✅ Orchestrator router is accessible")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ Router test failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error checking router: {e}")

if __name__ == "__main__":
    print("Production Orchestration Test")
    print("=" * 50)
    
    # Check deployment
    check_deployment_status()
    
    # Test orchestration
    test_production_orchestration()
    
    print("\n" + "=" * 50)
    print("Test complete!")