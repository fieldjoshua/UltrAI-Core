#!/usr/bin/env python3
"""
End-to-End Testing for Ultra MVP

This script performs comprehensive end-to-end testing of the Ultra MVP,
validating the full request flow from UI to API to LLMs and back.
"""

import sys
import time
import json
import asyncio
import requests
import argparse
from typing import Dict, List, Any, Optional
from datetime import datetime

# Configure test parameters
API_BASE_URL = "http://localhost:8000/api"
TIMEOUT = 30  # seconds
MAX_RETRIES = 3
TEST_PATTERNS = ["gut", "confidence", "critique", "fact_check"]
TEST_MODELS = ["gpt4o", "claude37", "gemini15"]

# Test prompts with varying complexity
TEST_PROMPTS = [
    "What are the pros and cons of renewable energy?",
    "Explain quantum computing in simple terms.",
    "What are some effective strategies for addressing climate change?",
    "Compare and contrast different approaches to artificial intelligence development.",
]

# Error test cases
ERROR_TEST_CASES = [
    {"prompt": "", "expected_error": "Prompt cannot be empty"},
    {"prompt": "Test prompt", "models": [], "expected_error": "No models selected"},
    {
        "prompt": "Test prompt with timeout",
        "timeout": 0.001,
        "expected_error": "timeout",
    },
]


class UltraE2ETester:
    """End-to-End tester for Ultra MVP"""

    def __init__(self, base_url: str = API_BASE_URL, use_mock: bool = True):
        """Initialize the tester"""
        self.base_url = base_url
        self.use_mock = use_mock
        self.session = requests.Session()
        self.results = {
            "overall": {
                "success": False,
                "timestamp": datetime.now().isoformat(),
                "tests_run": 0,
                "tests_passed": 0,
                "tests_failed": 0,
            },
            "service_check": {},
            "available_models": {},
            "analysis_tests": [],
            "error_handling": [],
            "performance": {},
        }

    def log(self, message: str, level: str = "INFO"):
        """Log a message"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")

    def check_service_up(self) -> bool:
        """Check if the API service is up and running"""
        try:
            response = self.session.get(f"{self.base_url}/status", timeout=TIMEOUT)
            self.results["service_check"] = {
                "success": response.status_code == 200,
                "status_code": response.status_code,
                "response": response.json() if response.status_code == 200 else None,
            }
            return self.results["service_check"]["success"]
        except Exception as e:
            self.log(f"Service check failed: {str(e)}", "ERROR")
            self.results["service_check"] = {"success": False, "error": str(e)}
            return False

    def get_available_models(self) -> List[str]:
        """Get list of available models from the API"""
        try:
            response = self.session.get(
                f"{self.base_url}/available-models", timeout=TIMEOUT
            )
            if response.status_code == 200:
                models = response.json().get("available_models", [])
                self.results["available_models"] = {
                    "success": True,
                    "models": models,
                    "count": len(models),
                }
                return models
            else:
                self.results["available_models"] = {
                    "success": False,
                    "status_code": response.status_code,
                    "response": response.text,
                }
                return []
        except Exception as e:
            self.log(f"Failed to get available models: {str(e)}", "ERROR")
            self.results["available_models"] = {"success": False, "error": str(e)}
            return []

    def test_analysis(
        self,
        prompt: str,
        models: Optional[List[str]] = None,
        pattern: str = "confidence",
        timeout: int = TIMEOUT,
    ) -> Dict[str, Any]:
        """Test the analysis endpoint with given parameters"""
        if models is None:
            models = TEST_MODELS[:2]  # Use first two models by default

        self.log(f"Testing analysis with prompt: '{prompt[:30]}...'")
        self.log(f"Models: {models}, Pattern: {pattern}")

        test_result = {
            "prompt": prompt,
            "models": models,
            "pattern": pattern,
            "success": False,
            "timestamp": datetime.now().isoformat(),
        }

        payload = {
            "prompt": prompt,
            "models": models,
            "ultraModel": models[0] if models else "gpt4o",
            "pattern": pattern,
            "options": {},
        }

        try:
            start_time = time.time()
            response = self.session.post(
                f"{self.base_url}/analyze", json=payload, timeout=timeout
            )
            end_time = time.time()
            response_time = end_time - start_time

            test_result["response_time"] = response_time

            if response.status_code == 200:
                response_data = response.json()
                test_result["success"] = True
                test_result["status_code"] = response.status_code

                # Validate response structure
                test_result["validation"] = {
                    "has_ultra_response": "ultra_response" in response_data,
                    "has_model_responses": "model_responses" in response_data,
                    "models_match": set(response_data.get("model_responses", {}).keys())
                    == set(models),
                }

                # Basic validation of response content
                if (
                    "ultra_response" in response_data
                    and response_data["ultra_response"]
                ):
                    test_result["ultra_response_length"] = len(
                        response_data["ultra_response"]
                    )

                # Check performance metrics
                if "performance" in response_data:
                    test_result["performance"] = response_data["performance"]
            else:
                test_result["success"] = False
                test_result["status_code"] = response.status_code
                test_result["error"] = response.text
                self.log(
                    f"Analysis failed with status code: {response.status_code}", "ERROR"
                )
        except Exception as e:
            test_result["success"] = False
            test_result["error"] = str(e)
            self.log(f"Analysis request failed: {str(e)}", "ERROR")

        self.results["tests_run"] = self.results.get("tests_run", 0) + 1
        if test_result["success"]:
            self.results["tests_passed"] = self.results.get("tests_passed", 0) + 1
        else:
            self.results["tests_failed"] = self.results.get("tests_failed", 0) + 1

        self.results["analysis_tests"].append(test_result)
        return test_result

    def test_error_handling(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Test error handling for specific error cases"""
        prompt = test_case.get("prompt", "Test prompt")
        models = test_case.get("models", ["gpt4o"])
        pattern = test_case.get("pattern", "confidence")
        timeout = test_case.get("timeout", TIMEOUT)
        expected_error = test_case.get("expected_error", "")

        self.log(f"Testing error handling for: {expected_error}")

        test_result = {
            "test_case": test_case,
            "success": False,
            "expected_error": expected_error,
            "timestamp": datetime.now().isoformat(),
        }

        payload = {
            "prompt": prompt,
            "models": models,
            "ultraModel": models[0] if models and len(models) > 0 else "gpt4o",
            "pattern": pattern,
            "options": {},
        }

        try:
            start_time = time.time()
            response = self.session.post(
                f"{self.base_url}/analyze", json=payload, timeout=timeout
            )
            end_time = time.time()
            response_time = end_time - start_time

            test_result["response_time"] = response_time
            test_result["status_code"] = response.status_code

            if response.status_code >= 400 or "error" in response.text.lower():
                # This should be an error response - check if expected error is present
                response_text = response.text.lower()
                error_present = expected_error.lower() in response_text
                test_result["success"] = error_present
                test_result["error_present"] = error_present
                test_result["actual_response"] = response.text

                if not error_present:
                    self.log(
                        f"Expected error '{expected_error}' not found in response",
                        "WARNING",
                    )
            else:
                # We received a successful response when we expected an error
                test_result["success"] = False
                test_result["unexpected_success"] = True
                test_result["response"] = response.text
                self.log("Expected error but got success response", "WARNING")
        except requests.Timeout:
            # If we expected a timeout, this is a success
            if "timeout" in expected_error.lower():
                test_result["success"] = True
                test_result["error"] = "Request timed out as expected"
            else:
                test_result["success"] = False
                test_result["error"] = "Request timed out unexpectedly"
        except Exception as e:
            test_result["error"] = str(e)
            test_result["success"] = "expected exception" in expected_error.lower()
            self.log(f"Error test case failed: {str(e)}", "ERROR")

        self.results["tests_run"] = self.results.get("tests_run", 0) + 1
        if test_result["success"]:
            self.results["tests_passed"] = self.results.get("tests_passed", 0) + 1
        else:
            self.results["tests_failed"] = self.results.get("tests_failed", 0) + 1

        self.results["error_handling"].append(test_result)
        return test_result

    def test_caching(
        self, prompt: str, models: List[str], pattern: str = "confidence"
    ) -> Dict[str, Any]:
        """Test caching functionality by making the same request twice"""
        self.log("Testing caching functionality")

        test_result = {
            "prompt": prompt,
            "models": models,
            "pattern": pattern,
            "success": False,
        }

        # First request
        first_start = time.time()
        # Store response but we don't use it directly - it gets stored in results
        _ = self.test_analysis(prompt, models, pattern)
        first_time = time.time() - first_start

        # Short delay
        time.sleep(1)

        # Second request (should be cached)
        second_start = time.time()
        # Store response but we don't use it directly - it gets stored in results
        _ = self.test_analysis(prompt, models, pattern)
        second_time = time.time() - second_start

        # Check if second request was faster (indicating cache hit)
        speedup_factor = first_time / max(second_time, 0.001)  # Avoid division by zero
        cache_hit = speedup_factor > 1.5  # If second request is significantly faster

        test_result["success"] = cache_hit
        test_result["first_request_time"] = first_time
        test_result["second_request_time"] = second_time
        test_result["speedup_factor"] = speedup_factor
        test_result["cache_hit_detected"] = cache_hit

        self.results["performance"]["caching"] = test_result
        return test_result

    def test_concurrent_requests(self, count: int = 5) -> Dict[str, Any]:
        """Test handling of multiple concurrent requests"""
        self.log(f"Testing {count} concurrent requests")

        test_result = {
            "count": count,
            "success": False,
            "start_time": datetime.now().isoformat(),
        }

        # Prepare different prompts for each request
        prompts = [
            f"Concurrent test {i}: {TEST_PROMPTS[i % len(TEST_PROMPTS)]}"
            for i in range(count)
        ]
        results = []

        async def make_requests():
            async def single_request(prompt, index):
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    None,
                    lambda: self.test_analysis(
                        prompt, TEST_MODELS, TEST_PATTERNS[index % len(TEST_PATTERNS)]
                    ),
                )
                return result

            tasks = [single_request(prompts[i], i) for i in range(count)]
            return await asyncio.gather(*tasks, return_exceptions=True)

        # Run concurrent requests
        start_time = time.time()
        if sys.version_info >= (3, 7):
            results = asyncio.run(make_requests())
        else:
            loop = asyncio.get_event_loop()
            results = loop.run_until_complete(make_requests())
        end_time = time.time()

        # Analyze results
        successes = sum(
            1 for r in results if isinstance(r, dict) and r.get("success", False)
        )
        failures = count - successes

        test_result["total_time"] = end_time - start_time
        test_result["average_time_per_request"] = (end_time - start_time) / count
        test_result["success_count"] = successes
        test_result["failure_count"] = failures
        test_result["success_rate"] = successes / count if count > 0 else 0
        test_result["success"] = successes == count  # All requests succeeded

        self.results["performance"]["concurrent_requests"] = test_result
        return test_result

    def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests and return results"""
        self.log("Starting Ultra MVP end-to-end tests")

        # Check if service is up
        if not self.check_service_up():
            self.log("Service is not responding, aborting tests", "ERROR")
            return self.results

        # Get available models
        models = self.get_available_models()
        if not models:
            self.log("No models available, using default test models", "WARNING")
            models = TEST_MODELS

        # Basic analysis tests with different prompts and patterns
        for i, prompt in enumerate(TEST_PROMPTS):
            pattern = TEST_PATTERNS[i % len(TEST_PATTERNS)]
            test_models = models[: min(3, len(models))]  # Use up to 3 models
            self.test_analysis(prompt, test_models, pattern)

        # Error handling tests
        for test_case in ERROR_TEST_CASES:
            self.test_error_handling(test_case)

        # Caching test
        self.test_caching(TEST_PROMPTS[0], models[:2], "confidence")

        # Concurrent requests test (light load)
        self.test_concurrent_requests(3)

        # Update overall result
        self.results["overall"]["success"] = (
            self.results["tests_passed"] > 0 and self.results["tests_failed"] == 0
        )
        self.results["overall"]["tests_run"] = self.results["tests_run"]
        self.results["overall"]["tests_passed"] = self.results["tests_passed"]
        self.results["overall"]["tests_failed"] = self.results["tests_failed"]
        self.results["overall"]["end_timestamp"] = datetime.now().isoformat()

        test_stats = (
            f"Tests completed: {self.results['tests_passed']} passed, "
            f"{self.results['tests_failed']} failed"
        )
        self.log(test_stats)
        return self.results

    def save_results(self, output_file: str):
        """Save test results to a file"""
        with open(output_file, "w") as f:
            json.dump(self.results, f, indent=2)
        self.log(f"Results saved to {output_file}")


def main():
    """Main function to run tests"""
    parser = argparse.ArgumentParser(description="Ultra MVP End-to-End Testing")
    parser.add_argument("--base-url", default=API_BASE_URL, help="Base URL for API")
    parser.add_argument(
        "--output", default="e2e_test_results.json", help="Output file for results"
    )
    parser.add_argument("--mock", action="store_true", help="Use mock LLM service")
    args = parser.parse_args()

    tester = UltraE2ETester(base_url=args.base_url, use_mock=args.mock)
    results = tester.run_all_tests()
    tester.save_results(args.output)

    if results["overall"]["success"]:
        print("\n✅ All tests passed successfully!")
        return 0
    else:
        test_results = f"\n❌ Tests failed: {results['tests_failed']} of {results['tests_run']} failed"
        print(test_results)
        return 1


if __name__ == "__main__":
    sys.exit(main())
