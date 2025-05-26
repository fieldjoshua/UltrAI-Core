"""Test Render endpoints with multiple attempts"""
import requests
import time
import json

def test_endpoints():
    base_url = "https://ultra-backend.onrender.com"
    endpoints = ["/", "/health", "/docs", "/openapi.json"]
    
    print("Testing Render endpoints with multiple attempts...")
    
    for endpoint in endpoints:
        print(f"\nTesting {endpoint}:")
        for i in range(5):
            try:
                response = requests.get(f"{base_url}{endpoint}", timeout=5)
                print(f"  Attempt {i+1}: Status {response.status_code}")
                
                # If we get a 200, show the response
                if response.status_code == 200:
                    if response.headers.get('content-type', '').startswith('application/json'):
                        print(f"  Response: {response.json()}")
                    else:
                        print(f"  Response: {response.text[:100]}...")
                    break
                else:
                    print(f"  Response: {response.text[:100]}...")
                    
            except Exception as e:
                print(f"  Attempt {i+1}: Error - {e}")
            
            time.sleep(1)

if __name__ == "__main__":
    test_endpoints()