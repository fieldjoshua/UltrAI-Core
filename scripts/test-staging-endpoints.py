#!/usr/bin/env python3
"""Test staging endpoints to verify deployment and functionality."""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, Any

# Configuration
STAGING_URL = "https://ultrai-staging-api.onrender.com"
TIMEOUT = 30

def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{'=' * 60}")
    print(f"{title}")
    print(f"{'=' * 60}")

def test_endpoint(method: str, path: str, data: Dict[str, Any] = None, headers: Dict[str, str] = None) -> Dict[str, Any]:
    """Test an endpoint and return results."""
    url = f"{STAGING_URL}{path}"
    result = {
        "url": url,
        "method": method,
        "timestamp": datetime.now().isoformat(),
        "success": False,
        "status_code": None,
        "response": None,
        "error": None
    }
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=TIMEOUT, headers=headers)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=TIMEOUT, headers=headers)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        result["status_code"] = response.status_code
        result["success"] = 200 <= response.status_code < 300
        
        try:
            result["response"] = response.json()
        except:
            result["response"] = response.text
            
    except Exception as e:
        result["error"] = str(e)
    
    return result

def main():
    """Run all staging endpoint tests."""
    print(f"🧪 Testing Staging Endpoints: {STAGING_URL}")
    print(f"📅 Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test results storage
    results = {}
    
    # 1. Health Check
    print_section("1. Health Check")
    health_result = test_endpoint("GET", "/api/health")
    results["health"] = health_result
    print(f"Status: {health_result['status_code']}")
    print(f"Response: {json.dumps(health_result['response'], indent=2)}")
    
    # 2. Models Endpoint
    print_section("2. Available Models")
    models_result = test_endpoint("GET", "/api/models")
    results["models"] = models_result
    print(f"Status: {models_result['status_code']}")
    if models_result['success'] and isinstance(models_result['response'], dict):
        models = models_result['response'].get('models', [])
        print(f"Total models: {len(models)}")
        if models:
            print("Sample models:")
            for model in models[:5]:
                print(f"  - {model.get('id')} ({model.get('provider')})")
    else:
        print(f"Response: {models_result['response']}")
    
    # 3. Model Health
    print_section("3. Model Health Check")
    health_check_result = test_endpoint("GET", "/api/model-health")
    results["model_health"] = health_check_result
    print(f"Status: {health_check_result['status_code']}")
    if health_check_result['success'] and isinstance(health_check_result['response'], dict):
        available = health_check_result['response'].get('available_models', {})
        total = health_check_result['response'].get('total_models', 0)
        print(f"Available models: {len(available)} / {total}")
        for provider, models in available.items():
            print(f"  {provider}: {len(models)} models")
    else:
        print(f"Response: {health_check_result['response']}")
    
    # 4. API Keys Status
    print_section("4. API Keys Status")
    keys_result = test_endpoint("GET", "/api/models/api-keys-status")
    results["api_keys"] = keys_result
    print(f"Status: {keys_result['status_code']}")
    if keys_result['success']:
        print(f"Response: {json.dumps(keys_result['response'], indent=2)}")
    
    # 5. Test Orchestration (Simple)
    print_section("5. Orchestration Test (Simple)")
    orchestrate_data = {
        "prompt": "What is 2+2?",
        "analysis_type": "quick"
    }
    orchestrate_result = test_endpoint("POST", "/api/orchestrate", data=orchestrate_data)
    results["orchestration_simple"] = orchestrate_result
    print(f"Status: {orchestrate_result['status_code']}")
    if orchestrate_result['success']:
        response = orchestrate_result['response']
        if isinstance(response, dict):
            print(f"Success: {response.get('success', False)}")
            if 'error' in response:
                print(f"Error: {response['error']}")
            elif 'result' in response:
                result_preview = str(response['result'])[:200] + "..." if len(str(response['result'])) > 200 else str(response['result'])
                print(f"Result preview: {result_preview}")
    else:
        print(f"Response: {orchestrate_result['response']}")
    
    # 6. Metrics Endpoint
    print_section("6. Metrics")
    metrics_result = test_endpoint("GET", "/api/metrics")
    results["metrics"] = metrics_result
    print(f"Status: {metrics_result['status_code']}")
    if metrics_result['success'] and isinstance(metrics_result['response'], str):
        lines = metrics_result['response'].split('\n')
        print("Sample metrics:")
        for line in lines[:10]:
            if line and not line.startswith('#'):
                print(f"  {line}")
    
    # Summary
    print_section("Test Summary")
    successful = sum(1 for r in results.values() if r['success'])
    total = len(results)
    print(f"✅ Successful: {successful}/{total}")
    print(f"❌ Failed: {total - successful}/{total}")
    
    print("\nEndpoint Status:")
    for name, result in results.items():
        status = "✅" if result['success'] else "❌"
        print(f"  {status} {name}: {result['status_code'] or 'Error'}")
    
    # Save results
    with open("staging_test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n📄 Full results saved to: staging_test_results.json")
    
    return 0 if successful == total else 1

if __name__ == "__main__":
    sys.exit(main())