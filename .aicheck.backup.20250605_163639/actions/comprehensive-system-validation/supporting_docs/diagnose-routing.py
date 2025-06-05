#!/usr/bin/env python3
"""
Diagnose API Routing Issues
Comprehensive test of all possible API endpoints
"""

import subprocess
import json
from datetime import datetime

BASE_URL = "https://ultrai-core.onrender.com"

# All possible endpoint variations to test
ENDPOINTS_TO_TEST = [
    # Health checks
    {"path": "/", "method": "GET", "name": "Root"},
    {"path": "/health", "method": "GET", "name": "Health"},
    {"path": "/api/health", "method": "GET", "name": "API Health"},
    
    # Orchestrator endpoints - various path patterns
    {"path": "/api/orchestrator/models", "method": "GET", "name": "Models (api prefix)"},
    {"path": "/orchestrator/models", "method": "GET", "name": "Models (no prefix)"},
    {"path": "/api/v1/orchestrator/models", "method": "GET", "name": "Models (v1)"},
    
    {"path": "/api/orchestrator/patterns", "method": "GET", "name": "Patterns (api prefix)"},
    {"path": "/orchestrator/patterns", "method": "GET", "name": "Patterns (no prefix)"},
    
    {"path": "/api/orchestrator/feather", "method": "POST", "name": "Feather (api prefix)"},
    {"path": "/orchestrator/feather", "method": "POST", "name": "Feather (no prefix)"},
    {"path": "/api/orchestrator/process", "method": "POST", "name": "Process (api prefix)"},
    {"path": "/orchestrator/process", "method": "POST", "name": "Process (no prefix)"},
    
    # Model runner endpoints
    {"path": "/api/available-models", "method": "GET", "name": "Available Models (legacy)"},
    {"path": "/available-models", "method": "GET", "name": "Available Models (no prefix)"},
    
    # Auth endpoints
    {"path": "/api/auth/login", "method": "POST", "name": "Login"},
    {"path": "/auth/login", "method": "POST", "name": "Login (no prefix)"},
    
    # Document endpoints
    {"path": "/api/documents", "method": "GET", "name": "Documents"},
    {"path": "/documents", "method": "GET", "name": "Documents (no prefix)"},
]

def test_endpoint(endpoint):
    """Test a single endpoint"""
    url = f"{BASE_URL}{endpoint['path']}"
    cmd = ["curl", "-s", "-w", "\nHTTP_CODE:%{http_code}", "-X", endpoint['method']]
    
    # Add headers
    cmd.extend(["-H", "Content-Type: application/json"])
    
    # Add dummy data for POST requests
    if endpoint['method'] == "POST":
        if "feather" in endpoint['path'] or "process" in endpoint['path']:
            data = {"prompt": "test", "pattern": "gut"}
        elif "login" in endpoint['path']:
            data = {"email": "test@example.com", "password": "test"}
        else:
            data = {}
        cmd.extend(["-d", json.dumps(data)])
    
    cmd.append(url)
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        output = result.stdout
        
        # Extract HTTP code
        if "HTTP_CODE:" in output:
            parts = output.split("HTTP_CODE:")
            response_body = parts[0].strip()
            http_code = parts[1].strip()
            
            # Try to parse JSON response
            try:
                if response_body:
                    response_data = json.loads(response_body)
                else:
                    response_data = None
            except:
                response_data = response_body[:100] if response_body else None
            
            return {
                "http_code": http_code,
                "response": response_data,
                "success": http_code in ["200", "201", "204"]
            }
        else:
            return {
                "http_code": "???",
                "response": output[:100] if output else None,
                "success": False
            }
    except Exception as e:
        return {
            "http_code": "ERROR",
            "response": str(e),
            "success": False
        }

def run_diagnosis():
    """Run comprehensive endpoint diagnosis"""
    print("="*60)
    print("🔍 API Routing Diagnosis")
    print(f"📍 Target: {BASE_URL}")
    print(f"🕐 Started: {datetime.now().isoformat()}")
    print("="*60)
    
    results = {
        "working_endpoints": [],
        "broken_endpoints": [],
        "redirects": [],
        "auth_required": []
    }
    
    for endpoint in ENDPOINTS_TO_TEST:
        print(f"\n📍 Testing: {endpoint['name']}")
        print(f"   {endpoint['method']} {endpoint['path']}")
        
        result = test_endpoint(endpoint)
        http_code = result['http_code']
        
        # Categorize result
        if result['success']:
            print(f"   ✅ HTTP {http_code} - Success")
            if result['response']:
                print(f"   Response: {json.dumps(result['response'], indent=2) if isinstance(result['response'], dict) else result['response']}")
            results["working_endpoints"].append(endpoint)
        elif http_code == "404":
            print(f"   ❌ HTTP {http_code} - Not Found")
            results["broken_endpoints"].append(endpoint)
        elif http_code == "405":
            print(f"   ⚠️  HTTP {http_code} - Method Not Allowed")
            results["broken_endpoints"].append(endpoint)
        elif http_code in ["301", "302", "307", "308"]:
            print(f"   ↩️  HTTP {http_code} - Redirect")
            results["redirects"].append(endpoint)
        elif http_code in ["401", "403"]:
            print(f"   🔒 HTTP {http_code} - Authentication Required")
            results["auth_required"].append(endpoint)
        else:
            print(f"   ❓ HTTP {http_code}")
            if result['response']:
                print(f"   Response: {result['response']}")
            results["broken_endpoints"].append(endpoint)
    
    # Print summary
    print("\n" + "="*60)
    print("📊 DIAGNOSIS SUMMARY")
    print("="*60)
    print(f"\n✅ Working Endpoints ({len(results['working_endpoints'])}):")
    for ep in results["working_endpoints"]:
        print(f"   - {ep['method']} {ep['path']}")
    
    print(f"\n❌ Broken Endpoints ({len(results['broken_endpoints'])}):")
    for ep in results["broken_endpoints"]:
        print(f"   - {ep['method']} {ep['path']}")
    
    print(f"\n↩️  Redirects ({len(results['redirects'])}):")
    for ep in results["redirects"]:
        print(f"   - {ep['method']} {ep['path']}")
    
    print(f"\n🔒 Auth Required ({len(results['auth_required'])}):")
    for ep in results["auth_required"]:
        print(f"   - {ep['method']} {ep['path']}")
    
    print("="*60)
    
    # Save detailed results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"/Users/joshuafield/Documents/Ultra/.aicheck/actions/comprehensive-system-validation/supporting_docs/test-reports/routing_diagnosis_{timestamp}.json"
    
    with open(results_file, "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "base_url": BASE_URL,
            "results": results,
            "total_tested": len(ENDPOINTS_TO_TEST)
        }, f, indent=2)
    
    print(f"\n💾 Detailed results saved to: {results_file}")
    
    # Provide recommendations
    print("\n💡 RECOMMENDATIONS:")
    if len(results["working_endpoints"]) == 0:
        print("   ⚠️  No API endpoints are working - check if FastAPI app is properly configured")
        print("   ⚠️  Verify that routes are registered with the FastAPI app")
        print("   ⚠️  Check render.yaml for correct start command")
    elif "/api/" in str(results["working_endpoints"]) and "/api/" not in str(results["broken_endpoints"]):
        print("   ℹ️  API endpoints use /api/ prefix")
    elif "/api/" not in str(results["working_endpoints"]) and "/api/" in str(results["broken_endpoints"]):
        print("   ℹ️  API endpoints do NOT use /api/ prefix")
    
    if results["redirects"]:
        print("   ℹ️  Some endpoints are redirecting - check for trailing slashes or HTTPS redirects")

if __name__ == "__main__":
    run_diagnosis()