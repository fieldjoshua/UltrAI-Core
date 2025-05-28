#!/usr/bin/env python3
"""
Monitor script to check when orchestrator endpoints become available
"""

import requests
import time
from datetime import datetime

PROD_URL = "https://ultrai-core.onrender.com"

def check_endpoints():
    """Check if new orchestrator endpoints are available"""
    endpoints = [
        "/api/orchestrator/models",
        "/api/orchestrator/patterns", 
        "/api/orchestrator/feather"
    ]
    
    results = {}
    for endpoint in endpoints:
        try:
            response = requests.get(f"{PROD_URL}{endpoint}", timeout=5)
            results[endpoint] = response.status_code
        except Exception as e:
            results[endpoint] = f"Error: {e}"
    
    return results

def check_openapi():
    """Check OpenAPI spec for new endpoints"""
    try:
        response = requests.get(f"{PROD_URL}/openapi.json", timeout=5)
        if response.status_code == 200:
            data = response.json()
            paths = list(data.get('paths', {}).keys())
            orchestrator_paths = [p for p in paths if 'orchestrator' in p]
            return orchestrator_paths
        return []
    except:
        return []

def main():
    print(f"🔍 Monitoring deployment status...")
    print(f"Started at: {datetime.now().isoformat()}")
    print(f"Checking: {PROD_URL}")
    print("-" * 50)
    
    for attempt in range(1, 13):  # Check for 12 attempts (6 minutes)
        print(f"\n⏰ Attempt {attempt}/12 - {datetime.now().strftime('%H:%M:%S')}")
        
        # Check OpenAPI spec
        orchestrator_paths = check_openapi()
        print(f"OpenAPI orchestrator paths: {orchestrator_paths}")
        
        # Check specific endpoints
        results = check_endpoints()
        for endpoint, status in results.items():
            print(f"  {endpoint}: {status}")
        
        # Check if we have the new endpoints
        has_models = any('models' in path for path in orchestrator_paths)
        has_patterns = any('patterns' in path for path in orchestrator_paths) 
        has_feather = any('feather' in path for path in orchestrator_paths)
        
        if has_models and has_patterns and has_feather:
            print(f"\n🎉 SUCCESS! New orchestrator endpoints are live!")
            print(f"Deployment completed at: {datetime.now().isoformat()}")
            return True
            
        print(f"⏳ Still waiting... (next check in 30s)")
        time.sleep(30)
    
    print(f"\n⚠️ Timeout reached. Endpoints may need manual investigation.")
    return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🚀 Ready to test sophisticated orchestration!")
    else:
        print("\n🔧 May need to check Render dashboard or trigger manual redeploy")