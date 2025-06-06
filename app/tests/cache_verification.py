#!/usr/bin/env python3
"""
Cache Verification Script for Ultra MVP

This script tests the caching mechanism for the Ultra API to ensure
responses are properly cached and retrieved from cache when appropriate.
"""

import argparse
import json
import time
from datetime import datetime
from typing import Any, Dict, List

import requests

# Configuration
API_BASE_URL = "http://localhost:8000/api"
TIMEOUT = 30  # seconds
TEST_PROMPTS = [
    "What are the major causes of climate change?",
    "Explain how blockchain technology works",
    "Compare and contrast different leadership styles",
]
TEST_MODELS = ["gpt4o", "claude37"]
TEST_PATTERN = "confidence"


class CacheVerifier:
    """Verify caching functionality of the Ultra API"""

    def __init__(self, base_url: str = API_BASE_URL):
        """Initialize the cache verifier"""
        self.base_url = base_url
        self.session = requests.Session()
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "overall_success": False,
            "tests": [],
        }

    def log(self, message: str) -> None:
        """Log a message with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {message}")

    def send_analyze_request(
        self, prompt: str, models: List[str], pattern: str, log_prefix: str = ""
    ) -> Dict[str, Any]:
        """Send an analysis request to the API"""
        payload = {
            "prompt": prompt,
            "models": models,
            "ultraModel": models[0] if models else "gpt4o",
            "pattern": pattern,
            "options": {},
        }

        start_time = time.time()
        try:
            response = self.session.post(
                f"{self.base_url}/analyze", json=payload, timeout=TIMEOUT
            )
            end_time = time.time()
            response_time = end_time - start_time

            result = {
                "success": response.status_code == 200,
                "status_code": response.status_code,
                "response_time": response_time,
                "timestamp": datetime.now().isoformat(),
            }

            if response.status_code == 200:
                response_data = response.json()
                result["cached"] = response_data.get("cached", False)
                result["data"] = response_data

                cached_status = "CACHED" if result["cached"] else "NOT CACHED"
                self.log(
                    f"{log_prefix} Response: {cached_status} ({response_time:.2f}s)"
                )
            else:
                self.log(f"{log_prefix} Error: Status code {response.status_code}")
                result["error"] = response.text

            return result
        except Exception as e:
            end_time = time.time()
            response_time = end_time - start_time
            self.log(f"{log_prefix} Exception: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "response_time": response_time,
                "timestamp": datetime.now().isoformat(),
            }

    def test_cache_functionality(
        self,
        prompt: str,
        models: List[str],
        pattern: str,
        iterations: int = 3,
        delay: float = 0.5,
    ) -> Dict[str, Any]:
        """Test cache functionality with multiple iterations of the same request"""
        self.log(f"Testing cache with prompt: '{prompt[:50]}...'")
        self.log(f"Models: {models}, Pattern: {pattern}, Iterations: {iterations}")

        test_result = {
            "prompt": prompt,
            "models": models,
            "pattern": pattern,
            "iterations": iterations,
            "success": False,
            "responses": [],
        }

        for i in range(iterations):
            log_prefix = f"[Iteration {i+1}/{iterations}]"
            response = self.send_analyze_request(prompt, models, pattern, log_prefix)
            test_result["responses"].append(response)
            time.sleep(delay)  # Small delay between requests

        # Verify cache functionality
        first_response = test_result["responses"][0]
        cached_responses = test_result["responses"][1:]

        if not first_response["success"]:
            test_result["success"] = False
            test_result["error"] = "First request failed"
            return test_result

        # Check if subsequent requests were cached
        cached_count = sum(1 for r in cached_responses if r.get("cached", False))

        # Calculate average response times
        first_time = first_response["response_time"]
        cached_times = [
            r["response_time"] for r in cached_responses if r.get("cached", False)
        ]
        non_cached_times = [
            r["response_time"] for r in cached_responses if not r.get("cached", False)
        ]

        avg_cached_time = sum(cached_times) / len(cached_times) if cached_times else 0
        avg_non_cached_time = (
            sum(non_cached_times) / len(non_cached_times) if non_cached_times else 0
        )

        # Analyze results
        test_result["first_request_time"] = first_time
        test_result["avg_cached_time"] = avg_cached_time
        test_result["avg_non_cached_time"] = avg_non_cached_time
        test_result["cached_count"] = cached_count
        test_result["non_cached_count"] = len(cached_responses) - cached_count

        # Success criteria: at least one cached response and cached responses are faster
        if cached_count > 0:
            speedup = first_time / avg_cached_time if avg_cached_time > 0 else 0
            test_result["cache_speedup"] = speedup
            test_result["success"] = (
                speedup > 1.2
            )  # Cached responses should be at least 20% faster
        else:
            test_result["success"] = False
            test_result["error"] = "No cached responses detected"

        # Log results
        if test_result["success"]:
            cache_success_msg = (
                f"✅ Cache test succeeded: {cached_count}/{len(cached_responses)} "
                f"cached responses"
            )
            self.log(cache_success_msg)
            timing_msg = (
                f"   First request: {first_time:.2f}s, "
                f"Avg cached: {avg_cached_time:.2f}s"
            )
            self.log(timing_msg)
            self.log(f"   Speedup: {test_result.get('cache_speedup', 0):.2f}x")
        else:
            cache_fail_msg = (
                f"❌ Cache test failed: {cached_count}/{len(cached_responses)} "
                f"cached responses"
            )
            self.log(cache_fail_msg)
            if "error" in test_result:
                self.log(f"   Error: {test_result['error']}")

        return test_result

    def test_cache_invalidation(
        self, prompt: str, models_sets: List[List[str]], pattern: str
    ) -> Dict[str, Any]:
        """Test that different model selections use different cache entries"""
        self.log(f"Testing cache invalidation with prompt: '{prompt[:50]}...'")
        self.log(f"Testing {len(models_sets)} different model sets")

        test_result = {
            "prompt": prompt,
            "model_sets": models_sets,
            "pattern": pattern,
            "success": False,
            "responses": {},
        }

        # First request with each model set
        for i, models in enumerate(models_sets):
            models_key = ",".join(models)
            log_prefix = f"[Models Set {i+1}/{len(models_sets)}]"
            response = self.send_analyze_request(prompt, models, pattern, log_prefix)
            test_result["responses"][models_key] = [response]
            time.sleep(0.5)  # Small delay between requests

        # Second request with each model set (should be cached)
        for i, models in enumerate(models_sets):
            models_key = ",".join(models)
            log_prefix = f"[Models Set {i+1}/{len(models_sets)} - Second request]"
            response = self.send_analyze_request(prompt, models, pattern, log_prefix)
            test_result["responses"][models_key].append(response)
            time.sleep(0.5)  # Small delay between requests

        # Analyze results - each set should have its own cache
        all_second_cached = True

        for models_key, responses in test_result["responses"].items():
            if len(responses) < 2:
                continue

            # Second request should be cached
            second_cached = responses[1].get("cached", False)
            all_second_cached = all_second_cached and second_cached

            # Log results for this model set
            if second_cached:
                speedup = responses[0]["response_time"] / responses[1]["response_time"]
                cache_msg = (
                    f"✅ Model set {models_key}: Second request cached "
                    f"(speedup: {speedup:.2f}x)"
                )
                self.log(cache_msg)
            else:
                self.log(f"❌ Model set {models_key}: Second request NOT cached")

        # Final success determination
        test_result["all_second_cached"] = all_second_cached
        test_result["success"] = all_second_cached

        return test_result

    def run_all_tests(self) -> Dict[str, Any]:
        """Run all cache verification tests"""
        self.log("Starting Ultra API cache verification tests")

        # Basic functionality tests with different prompts
        for prompt in TEST_PROMPTS:
            test_result = self.test_cache_functionality(
                prompt=prompt, models=TEST_MODELS, pattern=TEST_PATTERN, iterations=3
            )
            self.results["tests"].append(test_result)

        # Test different model combinations with the same prompt
        model_sets = [
            ["gpt4o", "claude37"],
            ["gpt4o", "gemini15"],
            ["claude37", "gemini15"],
        ]

        invalidation_test = self.test_cache_invalidation(
            prompt=TEST_PROMPTS[0], models_sets=model_sets, pattern=TEST_PATTERN
        )
        self.results["tests"].append(invalidation_test)

        # Determine overall success
        success_count = sum(
            1 for test in self.results["tests"] if test.get("success", False)
        )
        total_tests = len(self.results["tests"])
        self.results["success_count"] = success_count
        self.results["total_tests"] = total_tests
        self.results["overall_success"] = success_count == total_tests

        # Log final results
        if self.results["overall_success"]:
            self.log(f"✅ All cache tests passed: {success_count}/{total_tests}")
        else:
            self.log(
                f"❌ Some cache tests failed: {success_count}/{total_tests} passed"
            )

        return self.results

    def save_results(self, output_file: str) -> None:
        """Save test results to a file"""
        with open(output_file, "w") as f:
            json.dump(self.results, f, indent=2)
        self.log(f"Results saved to {output_file}")


def main() -> int:
    """Main function to run tests"""
    parser = argparse.ArgumentParser(description="Ultra API Cache Verification")
    parser.add_argument("--base-url", default=API_BASE_URL, help="Base URL for API")
    parser.add_argument(
        "--output", default="cache_test_results.json", help="Output file for results"
    )
    args = parser.parse_args()

    verifier = CacheVerifier(base_url=args.base_url)
    results = verifier.run_all_tests()
    verifier.save_results(args.output)

    return 0 if results["overall_success"] else 1


if __name__ == "__main__":
    exit(main())
