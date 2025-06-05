#!/usr/bin/env python3
"""
Production Deployment Verification Script
For orchestration-integration-fix action Phase 4

This script verifies that the orchestration endpoints are properly deployed
and functioning in the production environment.
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Tuple

# Production URL
BASE_URL = "https://ultrai-core.onrender.com"

# Test configuration
TEST_PATTERNS = [
    "gut", "confidence", "critique", "fact_check", "perspective",
    "scenario", "stakeholder", "systems", "time", "innovation"
]

TEST_PROMPTS = {
    "gut": "What's your intuitive sense about the future of AI?",
    "confidence": "How confident are you that renewable energy will replace fossil fuels?",
    "critique": "Critique the current state of social media platforms",
    "fact_check": "Fact check: The Earth is approximately 4.5 billion years old",
    "perspective": "What are different perspectives on universal basic income?",
    "scenario": "What scenarios could unfold from widespread automation?",
    "stakeholder": "Who are the stakeholders in climate change policy?",
    "systems": "Analyze the education system from a systems perspective",
    "time": "How has transportation evolved over time?",
    "innovation": "What innovations might emerge in healthcare?"
}


class DeploymentVerifier:
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "base_url": BASE_URL,
            "endpoints": {},
            "patterns": {},
            "performance": {},
            "errors": [],
            "summary": {}
        }
    
    def test_endpoint(self, path: str, method: str = "GET", 
                     headers: Dict = None, data: Dict = None) -> Tuple[bool, Dict]:
        """Test a single endpoint"""
        try:
            url = f"{BASE_URL}{path}"
            start_time = time.time()
            
            if method == "GET":
                response = requests.get(url, headers=headers, timeout=30)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=data, timeout=30)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            elapsed_time = time.time() - start_time
            
            result = {
                "status_code": response.status_code,
                "response_time": elapsed_time,
                "success": response.status_code < 400,
                "headers": dict(response.headers)
            }
            
            try:
                result["data"] = response.json()
            except:
                result["data"] = response.text
            
            return result["success"], result
            
        except Exception as e:
            return False, {
                "status_code": None,
                "response_time": None,
                "success": False,
                "error": str(e)
            }
    
    def test_health_endpoints(self):
        """Test health check endpoints"""
        print("🏥 Testing health endpoints...")
        
        # Basic health
        success, result = self.test_endpoint("/health")
        self.results["endpoints"]["health_basic"] = result
        print(f"  /health: {'✅' if success else '❌'} {result.get('status_code', 'Error')}")
        
        # Detailed health
        success, result = self.test_endpoint("/health?detail=true")
        self.results["endpoints"]["health_detailed"] = result
        print(f"  /health?detail=true: {'✅' if success else '❌'} {result.get('status_code', 'Error')}")
        
        # LLM providers health
        success, result = self.test_endpoint("/health/llm/providers")
        self.results["endpoints"]["health_llm_providers"] = result
        print(f"  /health/llm/providers: {'✅' if success else '❌'} {result.get('status_code', 'Error')}")
    
    def test_orchestrator_endpoints(self, auth_token: str = None):
        """Test orchestrator endpoints"""
        print("\n🎼 Testing orchestrator endpoints...")
        
        headers = {}
        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"
        
        # Models endpoint
        success, result = self.test_endpoint("/api/orchestrator/models", headers=headers)
        self.results["endpoints"]["orchestrator_models"] = result
        print(f"  /api/orchestrator/models: {'✅' if success else '❌'} {result.get('status_code', 'Error')}")
        
        if success and "data" in result:
            models = result["data"].get("models", [])
            print(f"    Available models: {len(models)}")
            for model in models[:3]:  # Show first 3
                print(f"      - {model}")
        
        # Patterns endpoint
        success, result = self.test_endpoint("/api/orchestrator/patterns", headers=headers)
        self.results["endpoints"]["orchestrator_patterns"] = result
        print(f"  /api/orchestrator/patterns: {'✅' if success else '❌'} {result.get('status_code', 'Error')}")
        
        if success and "data" in result:
            patterns = result["data"].get("patterns", [])
            print(f"    Available patterns: {len(patterns)}")
            for pattern in patterns[:3]:  # Show first 3
                print(f"      - {pattern.get('id', 'unknown')}: {pattern.get('name', 'unknown')}")
    
    def test_pattern_analysis(self, pattern: str, auth_token: str = None):
        """Test a specific pattern analysis"""
        headers = {}
        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"
        
        data = {
            "prompt": TEST_PROMPTS.get(pattern, "Test prompt"),
            "pattern": pattern,
            "models": ["openai/gpt-3.5-turbo", "anthropic/claude-3-haiku-20240307"]
        }
        
        start_time = time.time()
        success, result = self.test_endpoint(
            "/api/orchestrator/feather",
            method="POST",
            headers=headers,
            data=data
        )
        elapsed_time = time.time() - start_time
        
        self.results["patterns"][pattern] = {
            "success": success,
            "response_time": elapsed_time,
            "status_code": result.get("status_code"),
            "stages_completed": 0
        }
        
        if success and "data" in result:
            stages = result["data"].get("stages", {})
            self.results["patterns"][pattern]["stages_completed"] = len(stages)
        
        return success
    
    def test_all_patterns(self, auth_token: str = None):
        """Test all analysis patterns"""
        print("\n🧪 Testing analysis patterns...")
        
        successful = 0
        for pattern in TEST_PATTERNS:
            print(f"  Testing {pattern} pattern...", end="", flush=True)
            success = self.test_pattern_analysis(pattern, auth_token)
            if success:
                successful += 1
                print(f" ✅ ({self.results['patterns'][pattern]['response_time']:.2f}s)")
            else:
                print(f" ❌ ({self.results['patterns'][pattern].get('status_code', 'Error')})")
        
        print(f"\n  Summary: {successful}/{len(TEST_PATTERNS)} patterns working")
    
    def analyze_performance(self):
        """Analyze performance metrics"""
        print("\n📊 Performance Analysis...")
        
        # Calculate average response times
        endpoint_times = []
        for endpoint, data in self.results["endpoints"].items():
            if data.get("response_time"):
                endpoint_times.append(data["response_time"])
        
        pattern_times = []
        for pattern, data in self.results["patterns"].items():
            if data.get("response_time"):
                pattern_times.append(data["response_time"])
        
        self.results["performance"]["avg_endpoint_response"] = (
            sum(endpoint_times) / len(endpoint_times) if endpoint_times else 0
        )
        self.results["performance"]["avg_pattern_response"] = (
            sum(pattern_times) / len(pattern_times) if pattern_times else 0
        )
        
        print(f"  Average endpoint response: {self.results['performance']['avg_endpoint_response']:.3f}s")
        print(f"  Average pattern analysis: {self.results['performance']['avg_pattern_response']:.3f}s")
    
    def generate_summary(self):
        """Generate deployment summary"""
        # Count successes
        endpoint_success = sum(
            1 for data in self.results["endpoints"].values() 
            if data.get("success", False)
        )
        pattern_success = sum(
            1 for data in self.results["patterns"].values()
            if data.get("success", False)
        )
        
        self.results["summary"] = {
            "endpoints_tested": len(self.results["endpoints"]),
            "endpoints_successful": endpoint_success,
            "patterns_tested": len(self.results["patterns"]),
            "patterns_successful": pattern_success,
            "overall_status": "healthy" if endpoint_success > 0 else "unhealthy"
        }
        
        print("\n📋 Deployment Summary")
        print(f"  Endpoints: {endpoint_success}/{len(self.results['endpoints'])} working")
        print(f"  Patterns: {pattern_success}/{len(self.results['patterns'])} working")
        print(f"  Overall Status: {self.results['summary']['overall_status']}")
    
    def save_report(self):
        """Save verification report"""
        filename = f"deployment_verification_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = f"/Users/joshuafield/Documents/Ultra/.aicheck/actions/orchestration-integration-fix/supporting_docs/{filename}"
        
        with open(filepath, "w") as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n💾 Report saved to: {filename}")
        return filepath


def main():
    """Run deployment verification"""
    print("🚀 UltraAI Production Deployment Verification")
    print(f"📍 Target: {BASE_URL}")
    print(f"🕐 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    verifier = DeploymentVerifier()
    
    # Test health endpoints (no auth required)
    verifier.test_health_endpoints()
    
    # Test orchestrator endpoints (may require auth)
    # TODO: Add authentication token if required
    auth_token = None  # Set this if authentication is required
    verifier.test_orchestrator_endpoints(auth_token)
    
    # Test patterns if endpoints are accessible
    if verifier.results["endpoints"].get("orchestrator_patterns", {}).get("success"):
        verifier.test_all_patterns(auth_token)
    else:
        print("\n⚠️  Skipping pattern tests - orchestrator endpoints not accessible")
    
    # Analyze and summarize
    verifier.analyze_performance()
    verifier.generate_summary()
    
    # Save report
    report_path = verifier.save_report()
    
    print("\n✅ Verification complete!")
    
    return verifier.results["summary"]["overall_status"] == "healthy"


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)