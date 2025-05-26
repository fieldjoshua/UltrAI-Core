#!/usr/bin/env python3
"""
Test Script: 4-Stage Feather Orchestration Validation
This script validates the sophisticated patent-protected 4-stage orchestration system
"""

import asyncio
import json
import os
import sys
import time
from datetime import datetime
from typing import Dict, List, Any

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

import aiohttp

# Test configuration
BASE_URL = os.getenv("ULTRAI_BASE_URL", "http://localhost:8000")
API_TIMEOUT = 120  # 2 minutes for orchestration requests

# Test prompts for different scenarios
TEST_PROMPTS = {
    "simple": "What is the capital of France?",
    "complex": "Analyze the impact of artificial intelligence on employment in the next decade, considering both opportunities and challenges.",
    "creative": "Write a haiku about quantum computing that captures both its complexity and potential.",
    "analytical": "Compare and contrast the approaches of supervised and unsupervised machine learning, with real-world examples.",
    "factual": "What are the main causes of climate change and their relative contributions?"
}

# Expected patterns
ANALYSIS_PATTERNS = ["gut", "confidence", "critique", "fact_check", "perspective", "scenario"]

class FeatherOrchestrationTester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.results = {
            "test_time": datetime.now().isoformat(),
            "base_url": base_url,
            "tests": {},
            "summary": {}
        }
        
    async def test_available_models(self, session: aiohttp.ClientSession) -> Dict[str, Any]:
        """Test the available models endpoint"""
        print("\n🔍 Testing Available Models Endpoint...")
        
        try:
            async with session.get(
                f"{self.base_url}/api/orchestrator/models",
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                data = await response.json()
                
                if response.status == 200 and data.get("status") == "success":
                    models = data.get("models", [])
                    print(f"✅ Found {len(models)} available models: {models}")
                    return {
                        "status": "passed",
                        "models": models,
                        "count": len(models)
                    }
                else:
                    print(f"❌ Failed to get models: {response.status}")
                    return {
                        "status": "failed",
                        "error": f"HTTP {response.status}",
                        "data": data
                    }
        except Exception as e:
            print(f"❌ Error testing models endpoint: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def test_available_patterns(self, session: aiohttp.ClientSession) -> Dict[str, Any]:
        """Test the available patterns endpoint"""
        print("\n🔍 Testing Available Patterns Endpoint...")
        
        try:
            async with session.get(
                f"{self.base_url}/api/orchestrator/patterns",
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                data = await response.json()
                
                if response.status == 200 and data.get("status") == "success":
                    patterns = data.get("patterns", [])
                    print(f"✅ Found {len(patterns)} available patterns:")
                    for pattern in patterns:
                        print(f"   - {pattern['name']}: {pattern['description']}")
                    
                    # Verify all expected patterns are present
                    pattern_names = [p["name"] for p in patterns]
                    missing_patterns = [p for p in ANALYSIS_PATTERNS if p not in pattern_names]
                    
                    return {
                        "status": "passed" if not missing_patterns else "partial",
                        "patterns": patterns,
                        "count": len(patterns),
                        "missing_patterns": missing_patterns
                    }
                else:
                    print(f"❌ Failed to get patterns: {response.status}")
                    return {
                        "status": "failed",
                        "error": f"HTTP {response.status}",
                        "data": data
                    }
        except Exception as e:
            print(f"❌ Error testing patterns endpoint: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def test_feather_orchestration(
        self, 
        session: aiohttp.ClientSession,
        prompt: str,
        pattern: str = "gut",
        models: List[str] = None
    ) -> Dict[str, Any]:
        """Test a single Feather orchestration request"""
        print(f"\n🚀 Testing Feather Orchestration (pattern: {pattern})...")
        print(f"   Prompt: {prompt[:100]}...")
        
        request_data = {
            "prompt": prompt,
            "pattern": pattern,
            "output_format": "plain"
        }
        
        if models:
            request_data["models"] = models
            
        start_time = time.time()
        
        try:
            async with session.post(
                f"{self.base_url}/api/orchestrator/feather",
                json=request_data,
                timeout=aiohttp.ClientTimeout(total=API_TIMEOUT)
            ) as response:
                data = await response.json()
                elapsed_time = time.time() - start_time
                
                if response.status == 200 and data.get("status") == "success":
                    # Validate 4-stage structure
                    stages = ["initial_responses", "meta_responses", "hyper_responses", "ultra_response"]
                    missing_stages = [s for s in stages if s not in data]
                    
                    if not missing_stages:
                        print(f"✅ Orchestration completed in {elapsed_time:.2f}s")
                        print(f"   Models used: {data.get('models_used', [])}")
                        print(f"   Ultra response preview: {data['ultra_response'][:200]}...")
                        
                        # Validate quality metrics if present
                        quality_metrics = self._extract_quality_metrics(data)
                        
                        return {
                            "status": "passed",
                            "elapsed_time": elapsed_time,
                            "models_used": data.get("models_used", []),
                            "stages_present": stages,
                            "response_lengths": {
                                "initial": sum(len(r) for r in data["initial_responses"].values()),
                                "meta": sum(len(r) for r in data["meta_responses"].values()),
                                "hyper": sum(len(r) for r in data["hyper_responses"].values()),
                                "ultra": len(data["ultra_response"])
                            },
                            "quality_metrics": quality_metrics
                        }
                    else:
                        print(f"❌ Missing orchestration stages: {missing_stages}")
                        return {
                            "status": "failed",
                            "error": "Missing stages",
                            "missing_stages": missing_stages,
                            "data": data
                        }
                else:
                    print(f"❌ Orchestration failed: {response.status}")
                    return {
                        "status": "failed",
                        "error": f"HTTP {response.status}",
                        "data": data
                    }
        except asyncio.TimeoutError:
            print(f"⏱️ Orchestration timed out after {API_TIMEOUT}s")
            return {
                "status": "timeout",
                "error": f"Timeout after {API_TIMEOUT}s",
                "elapsed_time": API_TIMEOUT
            }
        except Exception as e:
            print(f"❌ Error during orchestration: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "elapsed_time": time.time() - start_time
            }
    
    def _extract_quality_metrics(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract quality evaluation metrics from orchestration response"""
        metrics = {}
        
        # Look for metrics in the ultra response
        ultra_response = data.get("ultra_response", "")
        
        # Simple heuristic metrics for now
        metrics["response_coherence"] = len(ultra_response) > 100
        metrics["multi_stage_progression"] = all([
            data.get("initial_responses"),
            data.get("meta_responses"), 
            data.get("hyper_responses"),
            data.get("ultra_response")
        ])
        
        return metrics
    
    async def run_pattern_tests(self, session: aiohttp.ClientSession, available_models: List[str]):
        """Run tests for each analysis pattern"""
        print("\n🔄 Testing All Analysis Patterns...")
        
        pattern_results = {}
        
        for pattern in ANALYSIS_PATTERNS:
            print(f"\n--- Testing Pattern: {pattern} ---")
            
            # Test with a relevant prompt for each pattern
            prompt = TEST_PROMPTS.get(
                "factual" if pattern == "fact_check" else 
                "analytical" if pattern in ["critique", "perspective"] else
                "complex"
            )
            
            result = await self.test_feather_orchestration(
                session,
                prompt=prompt,
                pattern=pattern,
                models=available_models[:3]  # Use up to 3 models for testing
            )
            
            pattern_results[pattern] = result
            
            # Add a small delay between tests
            await asyncio.sleep(2)
        
        return pattern_results
    
    async def run_multi_llm_test(self, session: aiohttp.ClientSession, available_models: List[str]):
        """Test orchestration with multiple LLMs"""
        print("\n🤖 Testing Multi-LLM Orchestration...")
        
        if len(available_models) < 2:
            print("⚠️  Need at least 2 models for multi-LLM test")
            return {"status": "skipped", "reason": "Insufficient models"}
        
        # Test with different model combinations
        test_cases = [
            {
                "name": "All Available Models",
                "models": available_models,
                "prompt": TEST_PROMPTS["complex"]
            },
            {
                "name": "Top 3 Models",
                "models": available_models[:3],
                "prompt": TEST_PROMPTS["analytical"]
            },
            {
                "name": "Model Pairs",
                "models": available_models[:2],
                "prompt": TEST_PROMPTS["simple"]
            }
        ]
        
        results = {}
        
        for test_case in test_cases:
            print(f"\n   Testing: {test_case['name']} - {test_case['models']}")
            
            result = await self.test_feather_orchestration(
                session,
                prompt=test_case["prompt"],
                models=test_case["models"]
            )
            
            results[test_case["name"]] = result
            await asyncio.sleep(2)
        
        return results
    
    async def run_all_tests(self):
        """Run comprehensive validation tests"""
        print("🚀 Starting Comprehensive Feather Orchestration Validation")
        print(f"📍 Target: {self.base_url}")
        print(f"🕐 Started at: {datetime.now().isoformat()}")
        
        async with aiohttp.ClientSession() as session:
            # Test 1: Check available models
            models_result = await self.test_available_models(session)
            self.results["tests"]["available_models"] = models_result
            
            if models_result["status"] != "passed":
                print("\n⚠️  Cannot proceed without available models")
                return self.results
            
            available_models = models_result["models"]
            
            # Test 2: Check available patterns
            patterns_result = await self.test_available_patterns(session)
            self.results["tests"]["available_patterns"] = patterns_result
            
            # Test 3: Basic orchestration test
            print("\n📝 Running Basic Orchestration Test...")
            basic_result = await self.test_feather_orchestration(
                session,
                prompt=TEST_PROMPTS["simple"],
                pattern="gut"
            )
            self.results["tests"]["basic_orchestration"] = basic_result
            
            # Test 4: Pattern-specific tests
            pattern_results = await self.run_pattern_tests(session, available_models)
            self.results["tests"]["pattern_tests"] = pattern_results
            
            # Test 5: Multi-LLM tests
            multi_llm_results = await self.run_multi_llm_test(session, available_models)
            self.results["tests"]["multi_llm_tests"] = multi_llm_results
            
            # Generate summary
            self._generate_summary()
            
        return self.results
    
    def _generate_summary(self):
        """Generate test summary"""
        total_tests = 0
        passed_tests = 0
        failed_tests = 0
        
        # Count basic tests
        for test_name, result in self.results["tests"].items():
            if isinstance(result, dict) and "status" in result:
                total_tests += 1
                if result["status"] == "passed":
                    passed_tests += 1
                elif result["status"] in ["failed", "error", "timeout"]:
                    failed_tests += 1
        
        # Count pattern tests
        if "pattern_tests" in self.results["tests"]:
            for pattern, result in self.results["tests"]["pattern_tests"].items():
                total_tests += 1
                if result["status"] == "passed":
                    passed_tests += 1
                elif result["status"] in ["failed", "error", "timeout"]:
                    failed_tests += 1
        
        self.results["summary"] = {
            "total_tests": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            "test_duration": (datetime.now() - datetime.fromisoformat(self.results["test_time"])).total_seconds()
        }
    
    def save_results(self, filename: str = None):
        """Save test results to file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"feather_orchestration_test_results_{timestamp}.json"
        
        filepath = os.path.join(
            os.path.dirname(__file__),
            "test-reports",
            filename
        )
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, "w") as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n💾 Results saved to: {filepath}")
        return filepath
    
    def print_summary(self):
        """Print test summary"""
        summary = self.results.get("summary", {})
        
        print("\n" + "="*60)
        print("📊 TEST SUMMARY")
        print("="*60)
        print(f"Total Tests: {summary.get('total_tests', 0)}")
        print(f"Passed: {summary.get('passed', 0)}")
        print(f"Failed: {summary.get('failed', 0)}")
        print(f"Success Rate: {summary.get('success_rate', 0):.1f}%")
        print(f"Duration: {summary.get('test_duration', 0):.2f}s")
        
        # Print pattern test summary
        if "pattern_tests" in self.results["tests"]:
            print("\n📋 Pattern Test Results:")
            for pattern, result in self.results["tests"]["pattern_tests"].items():
                status_icon = "✅" if result["status"] == "passed" else "❌"
                print(f"   {status_icon} {pattern}: {result['status']}")
        
        print("="*60)


async def main():
    """Main test execution"""
    # Check if we're testing locally or against deployed service
    if len(sys.argv) > 1 and sys.argv[1] == "--deployed":
        base_url = "https://ultrai-core.onrender.com"
        print("🌐 Testing against deployed service")
    else:
        base_url = BASE_URL
        print("🏠 Testing against local service")
    
    tester = FeatherOrchestrationTester(base_url)
    
    try:
        await tester.run_all_tests()
        tester.print_summary()
        tester.save_results()
        
        # Return exit code based on test results
        summary = tester.results.get("summary", {})
        if summary.get("failed", 0) > 0:
            sys.exit(1)
        else:
            sys.exit(0)
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())