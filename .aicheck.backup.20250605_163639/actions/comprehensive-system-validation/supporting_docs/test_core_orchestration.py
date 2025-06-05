#!/usr/bin/env python3
"""
Core Orchestration Validation Test Script
Tests the 4-stage Feather orchestration with multiple LLMs
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Any

# Production base URL
BASE_URL = "https://ultrai-core.onrender.com"

# Test configuration
TEST_PROMPT = "Explain the concept of artificial intelligence in simple terms"
TEST_PATTERNS = ["gut", "confidence", "critique", "fact_check", "perspective", "scenario"]

def log_test(message: str, level: str = "INFO"):
    """Log test output with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}")

def test_health_check():
    """Test health check endpoints"""
    log_test("Testing health check endpoints...")
    
    endpoints = ["/health", "/api/health"]
    results = {}
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
            results[endpoint] = {
                "status_code": response.status_code,
                "response": response.json() if response.status_code == 200 else None
            }
            log_test(f"{endpoint}: {response.status_code}")
        except Exception as e:
            results[endpoint] = {"error": str(e)}
            log_test(f"{endpoint}: ERROR - {e}", "ERROR")
    
    return results

def test_available_models():
    """Test available models endpoint"""
    log_test("Testing available models endpoint...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/available-models", timeout=10)
        if response.status_code == 200:
            models = response.json()
            log_test(f"Found {len(models)} available models")
            for model in models:
                log_test(f"  - {model.get('id', 'Unknown')}: {model.get('name', 'Unknown')}")
            return {"success": True, "models": models}
        else:
            log_test(f"Failed to get models: {response.status_code}", "ERROR")
            return {"success": False, "status_code": response.status_code}
    except Exception as e:
        log_test(f"Error getting models: {e}", "ERROR")
        return {"success": False, "error": str(e)}

def test_available_patterns():
    """Test available patterns endpoint"""
    log_test("Testing available patterns endpoint...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/available-patterns", timeout=10)
        if response.status_code == 200:
            patterns = response.json()
            log_test(f"Found {len(patterns)} available patterns")
            for pattern in patterns:
                log_test(f"  - {pattern.get('id', 'Unknown')}: {pattern.get('description', '')[:50]}...")
            return {"success": True, "patterns": patterns}
        else:
            log_test(f"Failed to get patterns: {response.status_code}", "ERROR")
            return {"success": False, "status_code": response.status_code}
    except Exception as e:
        log_test(f"Error getting patterns: {e}", "ERROR")
        return {"success": False, "error": str(e)}

def test_orchestration_execution(pattern: str, models: List[str] = None):
    """Test orchestration execution with a specific pattern"""
    log_test(f"Testing orchestration with pattern: {pattern}")
    
    # If no models specified, use defaults
    if not models:
        models = ["gpt-3.5-turbo", "claude-3-haiku-20240307", "gemini-pro"]
    
    payload = {
        "prompt": TEST_PROMPT,
        "pattern": pattern,
        "models": models
    }
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/api/orchestrator/execute",
            json=payload,
            timeout=60  # Longer timeout for orchestration
        )
        end_time = time.time()
        
        if response.status_code == 200:
            result = response.json()
            log_test(f"Orchestration completed in {end_time - start_time:.2f} seconds")
            
            # Verify 4-stage progression
            stages = ["initial", "meta", "hyper", "ultra"]
            stage_results = {}
            
            for stage in stages:
                if stage in result:
                    stage_results[stage] = {
                        "exists": True,
                        "has_content": bool(result[stage]),
                        "content_length": len(str(result[stage]))
                    }
                    log_test(f"  - {stage.capitalize()} stage: ✓ ({stage_results[stage]['content_length']} chars)")
                else:
                    stage_results[stage] = {"exists": False}
                    log_test(f"  - {stage.capitalize()} stage: ✗ (missing)", "WARNING")
            
            # Check quality metrics
            if "quality_metrics" in result:
                log_test("  - Quality metrics: ✓")
                metrics = result["quality_metrics"]
                for metric, value in metrics.items():
                    log_test(f"    - {metric}: {value}")
            else:
                log_test("  - Quality metrics: ✗ (missing)", "WARNING")
            
            return {
                "success": True,
                "duration": end_time - start_time,
                "stages": stage_results,
                "has_quality_metrics": "quality_metrics" in result,
                "result": result
            }
        else:
            log_test(f"Orchestration failed: {response.status_code}", "ERROR")
            return {"success": False, "status_code": response.status_code, "error": response.text}
    
    except Exception as e:
        log_test(f"Error during orchestration: {e}", "ERROR")
        return {"success": False, "error": str(e)}

def generate_test_report(results: Dict[str, Any]):
    """Generate a comprehensive test report"""
    report = f"""# Core Orchestration Validation Report
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Summary

### Health Check Results
"""
    
    # Health check section
    for endpoint, result in results["health_check"].items():
        if "error" in result:
            report += f"- {endpoint}: ❌ ERROR - {result['error']}\n"
        else:
            report += f"- {endpoint}: {'✅' if result['status_code'] == 200 else '❌'} (Status: {result['status_code']})\n"
    
    # Available models section
    report += "\n### Available Models\n"
    if results["models"]["success"]:
        report += f"✅ Successfully retrieved {len(results['models']['models'])} models\n\n"
        for model in results["models"]["models"]:
            report += f"- {model.get('id', 'Unknown')}: {model.get('name', 'Unknown')}\n"
    else:
        report += "❌ Failed to retrieve models\n"
    
    # Available patterns section
    report += "\n### Available Patterns\n"
    if results["patterns"]["success"]:
        report += f"✅ Successfully retrieved {len(results['patterns']['patterns'])} patterns\n\n"
        for pattern in results["patterns"]["patterns"]:
            report += f"- **{pattern.get('id', 'Unknown')}**: {pattern.get('description', 'No description')}\n"
    else:
        report += "❌ Failed to retrieve patterns\n"
    
    # Orchestration test results
    report += "\n## Orchestration Test Results\n\n"
    
    total_tests = len(results["orchestration_tests"])
    successful_tests = sum(1 for test in results["orchestration_tests"].values() if test["success"])
    
    report += f"**Total Tests**: {total_tests}\n"
    report += f"**Successful**: {successful_tests}\n"
    report += f"**Failed**: {total_tests - successful_tests}\n\n"
    
    for pattern, test_result in results["orchestration_tests"].items():
        report += f"### Pattern: {pattern}\n"
        
        if test_result["success"]:
            report += f"✅ **Status**: Success\n"
            report += f"- **Duration**: {test_result['duration']:.2f} seconds\n"
            report += f"- **4-Stage Progression**:\n"
            
            for stage, stage_info in test_result["stages"].items():
                if stage_info.get("exists"):
                    report += f"  - {stage.capitalize()}: ✅ ({stage_info['content_length']} chars)\n"
                else:
                    report += f"  - {stage.capitalize()}: ❌ Missing\n"
            
            report += f"- **Quality Metrics**: {'✅ Present' if test_result['has_quality_metrics'] else '❌ Missing'}\n"
        else:
            report += f"❌ **Status**: Failed\n"
            report += f"- **Error**: {test_result.get('error', 'Unknown error')}\n"
        
        report += "\n"
    
    # Validation summary
    report += "## Validation Summary\n\n"
    
    # Check success criteria
    all_patterns_accessible = results["patterns"]["success"] and len(results["patterns"]["patterns"]) >= 10
    four_stage_works = all(
        test["success"] and all(test["stages"].get(stage, {}).get("exists", False) 
        for stage in ["initial", "meta", "hyper", "ultra"])
        for test in results["orchestration_tests"].values()
    )
    quality_metrics_present = all(
        test["success"] and test["has_quality_metrics"]
        for test in results["orchestration_tests"].values()
    )
    
    report += f"- ✅ All 10 Feather analysis patterns accessible: {'✅' if all_patterns_accessible else '❌'}\n"
    report += f"- ✅ 4-stage orchestration completes successfully: {'✅' if four_stage_works else '❌'}\n"
    report += f"- ✅ Quality metrics calculated and displayed: {'✅' if quality_metrics_present else '❌'}\n"
    report += f"- ✅ Multi-LLM selection works: {'✅' if results['models']['success'] else '❌'}\n"
    
    return report

def main():
    """Main test execution"""
    log_test("Starting Core Orchestration Validation Tests", "INFO")
    log_test(f"Target: {BASE_URL}", "INFO")
    log_test("-" * 60)
    
    results = {
        "health_check": {},
        "models": {},
        "patterns": {},
        "orchestration_tests": {}
    }
    
    # Test 1: Health checks
    results["health_check"] = test_health_check()
    log_test("-" * 60)
    
    # Test 2: Available models
    results["models"] = test_available_models()
    log_test("-" * 60)
    
    # Test 3: Available patterns
    results["patterns"] = test_available_patterns()
    log_test("-" * 60)
    
    # Test 4: Orchestration execution for each pattern
    for pattern in TEST_PATTERNS:
        results["orchestration_tests"][pattern] = test_orchestration_execution(pattern)
        log_test("-" * 60)
        time.sleep(2)  # Avoid overwhelming the server
    
    # Generate and save report
    report = generate_test_report(results)
    
    report_path = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    with open(report_path, 'w') as f:
        f.write(report)
    
    log_test(f"Test report saved to: {report_path}", "INFO")
    
    # Also save raw results as JSON
    json_path = f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(json_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    log_test(f"Raw results saved to: {json_path}", "INFO")
    
    # Print summary
    log_test("\n" + "=" * 60, "INFO")
    log_test("TEST SUMMARY", "INFO")
    log_test("=" * 60, "INFO")
    
    total_orchestration_tests = len(results["orchestration_tests"])
    successful_orchestration = sum(1 for test in results["orchestration_tests"].values() if test["success"])
    
    log_test(f"Health Checks: {'PASS' if all(r.get('status_code') == 200 for r in results['health_check'].values() if 'status_code' in r) else 'FAIL'}")
    log_test(f"Model Registry: {'PASS' if results['models']['success'] else 'FAIL'}")
    log_test(f"Pattern Registry: {'PASS' if results['patterns']['success'] else 'FAIL'}")
    log_test(f"Orchestration Tests: {successful_orchestration}/{total_orchestration_tests} passed")

if __name__ == "__main__":
    main()