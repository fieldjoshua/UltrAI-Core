#!/usr/bin/env python3
"""
Test deployment progress and provide detailed diagnosis
"""

import requests
import time
import json

BASE_URL = "https://ultrai-core.onrender.com"

def test_endpoint(path, method="GET"):
    """Test an endpoint and return response info"""
    try:
        url = f"{BASE_URL}{path}"
        if method == "GET":
            response = requests.get(url, timeout=10)
        else:
            response = requests.post(url, timeout=10)
        
        return {
            "status_code": response.status_code,
            "content": response.text[:200] + "..." if len(response.text) > 200 else response.text,
            "success": response.status_code < 400
        }
    except Exception as e:
        return {
            "status_code": None,
            "content": f"Error: {str(e)}",
            "success": False
        }

def main():
    print("🔍 Testing deployment progress...")
    print(f"📡 Base URL: {BASE_URL}")
    print()
    
    endpoints_to_test = [
        ("/health", "GET"),
        ("/openapi.json", "GET"),
        ("/api/orchestrator/models", "GET"),
        ("/api/orchestrator/patterns", "GET"),
        ("/debug/env", "GET"),
    ]
    
    for path, method in endpoints_to_test:
        print(f"Testing {method} {path}...")
        result = test_endpoint(path, method)
        
        if result["success"]:
            print(f"  ✅ {result['status_code']}: {result['content'][:100]}...")
        else:
            print(f"  ❌ {result['status_code']}: {result['content']}")
        print()
    
    # Check OpenAPI for orchestrator routes
    print("🔍 Checking OpenAPI schema for orchestrator routes...")
    openapi_result = test_endpoint("/openapi.json")
    if openapi_result["success"]:
        try:
            openapi_data = json.loads(openapi_result["content"])
            orchestrator_paths = [path for path in openapi_data["paths"].keys() if "orchestrator" in path]
            print(f"📊 Found {len(orchestrator_paths)} orchestrator paths:")
            for path in orchestrator_paths:
                methods = list(openapi_data["paths"][path].keys())
                print(f"  - {' '.join(methods).upper()} {path}")
        except Exception as e:
            print(f"  ❌ Error parsing OpenAPI: {e}")
    else:
        print(f"  ❌ Could not fetch OpenAPI schema")

if __name__ == "__main__":
    main()