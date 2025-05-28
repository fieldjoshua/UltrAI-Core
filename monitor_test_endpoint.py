#!/usr/bin/env python3
"""
Monitor the test endpoint to see when deployment completes
"""

import requests
import time
import sys

BASE_URL = "https://ultrai-core.onrender.com"
TEST_ENDPOINT = "/api/orchestrator/test"

def check_endpoint():
    """Check if the test endpoint is available"""
    try:
        response = requests.get(f"{BASE_URL}{TEST_ENDPOINT}", timeout=10)
        return response.status_code == 200, response.status_code, response.text[:100]
    except Exception as e:
        return False, None, str(e)

def main():
    print(f"🔍 Monitoring {BASE_URL}{TEST_ENDPOINT}")
    print("⏳ Waiting for deployment to complete...")
    
    max_attempts = 20  # 10 minutes total
    attempt = 0
    
    while attempt < max_attempts:
        attempt += 1
        success, status_code, content = check_endpoint()
        
        timestamp = time.strftime("%H:%M:%S")
        if success:
            print(f"✅ {timestamp} - Endpoint available! Status: {status_code}")
            print(f"📄 Response: {content}")
            
            # Now test the main orchestrator endpoints
            print("\n🎯 Testing main orchestrator endpoints:")
            endpoints = ["/api/orchestrator/models", "/api/orchestrator/patterns"]
            for endpoint in endpoints:
                try:
                    response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
                    if response.status_code == 200:
                        print(f"  ✅ {endpoint}: Working")
                    else:
                        print(f"  ❌ {endpoint}: {response.status_code}")
                except Exception as e:
                    print(f"  ❌ {endpoint}: Error - {e}")
            
            return True
        else:
            print(f"⏳ {timestamp} - Attempt {attempt}: Status {status_code}, waiting...")
            
        time.sleep(30)  # Wait 30 seconds between attempts
    
    print("❌ Deployment did not complete within 10 minutes")
    return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)