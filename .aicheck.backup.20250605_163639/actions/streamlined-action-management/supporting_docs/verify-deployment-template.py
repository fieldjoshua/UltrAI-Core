#!/usr/bin/env python3
"""
Deployment Verification Script Template
This script is run by 'aicheck deploy verify' to ensure production deployment is working

Customize this template for your specific action's deployment verification needs.
"""

import sys
import json
import requests
from datetime import datetime
from typing import Dict, List, Any, Tuple

# Configuration - Update these for your action
PRODUCTION_URL = "https://your-app.com"
EXPECTED_ENDPOINTS = [
    "/health",
    "/api/status",
    # Add your specific endpoints
]

# Test functions - Add your specific tests

def test_health_check() -> Tuple[bool, str]:
    """Test that the health check endpoint is responding"""
    try:
        response = requests.get(f"{PRODUCTION_URL}/health", timeout=10)
        if response.status_code == 200:
            return True, f"Health check passed (status: {response.status_code})"
        else:
            return False, f"Health check failed (status: {response.status_code})"
    except Exception as e:
        return False, f"Health check error: {str(e)}"

def test_api_endpoints() -> Tuple[bool, str]:
    """Test that API endpoints are accessible"""
    failed_endpoints = []
    
    for endpoint in EXPECTED_ENDPOINTS:
        try:
            response = requests.get(f"{PRODUCTION_URL}{endpoint}", timeout=10)
            if response.status_code >= 500:
                failed_endpoints.append(f"{endpoint} (status: {response.status_code})")
        except Exception as e:
            failed_endpoints.append(f"{endpoint} (error: {str(e)})")
    
    if failed_endpoints:
        return False, f"Failed endpoints: {', '.join(failed_endpoints)}"
    else:
        return True, f"All {len(EXPECTED_ENDPOINTS)} endpoints accessible"

def test_specific_functionality() -> Tuple[bool, str]:
    """Test specific functionality for this action"""
    # TODO: Implement your specific tests here
    # Example: Test that a new feature is working
    
    try:
        # Replace with your actual test
        response = requests.post(
            f"{PRODUCTION_URL}/api/your-feature",
            json={"test": "data"},
            timeout=10
        )
        
        if response.status_code == 200:
            # Verify response content
            data = response.json()
            if "expected_field" in data:
                return True, "Feature test passed"
            else:
                return False, "Feature response missing expected fields"
        else:
            return False, f"Feature test failed (status: {response.status_code})"
    except Exception as e:
        return False, f"Feature test error: {str(e)}"

def test_data_integrity() -> Tuple[bool, str]:
    """Verify that data/database changes are correct"""
    # TODO: Add tests to verify data integrity
    # Example: Check that migrations ran successfully
    return True, "Data integrity check skipped (not implemented)"

def verify_deployment() -> int:
    """
    Main verification function
    Returns: 0 if all tests pass, 1 if any test fails
    """
    results = {
        "timestamp": datetime.now().isoformat(),
        "production_url": PRODUCTION_URL,
        "tests": [],
        "passed": False,
        "summary": ""
    }
    
    # Define all tests to run
    tests = [
        ("health_check", test_health_check),
        ("api_endpoints", test_api_endpoints),
        ("specific_functionality", test_specific_functionality),
        ("data_integrity", test_data_integrity),
    ]
    
    # Run all tests
    failed_count = 0
    for test_name, test_func in tests:
        try:
            passed, details = test_func()
            results["tests"].append({
                "name": test_name,
                "passed": passed,
                "details": details
            })
            if not passed:
                failed_count += 1
        except Exception as e:
            results["tests"].append({
                "name": test_name,
                "passed": False,
                "details": f"Test crashed: {str(e)}"
            })
            failed_count += 1
    
    # Determine overall result
    results["passed"] = failed_count == 0
    results["summary"] = f"{len(tests) - failed_count}/{len(tests)} tests passed"
    
    # Output results as JSON for aicheck to parse
    print(json.dumps(results, indent=2))
    
    # Also print human-readable summary to stderr
    print(f"\n{'='*60}", file=sys.stderr)
    print(f"Deployment Verification: {results['summary']}", file=sys.stderr)
    print(f"{'='*60}", file=sys.stderr)
    
    for test in results["tests"]:
        status = "✅ PASS" if test["passed"] else "❌ FAIL"
        print(f"{status} {test['name']}: {test['details']}", file=sys.stderr)
    
    return 0 if results["passed"] else 1

if __name__ == "__main__":
    sys.exit(verify_deployment())