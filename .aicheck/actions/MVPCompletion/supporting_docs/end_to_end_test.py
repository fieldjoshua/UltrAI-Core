#!/usr/bin/env python3
"""
End-to-End Test Script for Ultra MVP

This script tests the full flow of the Ultra MVP:
1. Connecting to the API
2. Sending a prompt to multiple LLMs
3. Receiving and validating responses

Usage:
    python end_to_end_test.py
"""

import os
import sys
import time
import logging
import argparse
import requests
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("e2e-test")

# Load environment variables
load_dotenv()


class UltraAPITester:
    """Test the Ultra API end-to-end functionality."""

    def __init__(self, base_url=None):
        """Initialize the API tester with optional custom base URL."""
        self.base_url = base_url or os.getenv(
            "REACT_APP_API_URL", "http://localhost:8000/api"
        )
        self.test_results = {
            "available_models": {"status": "not_run", "details": None},
            "analyze_basic": {"status": "not_run", "details": None},
            "analyze_multi_model": {"status": "not_run", "details": None},
            "analyze_error_handling": {"status": "not_run", "details": None},
            "cache_performance": {"status": "not_run", "details": None},
        }
        self.test_session = requests.Session()

    def run_all_tests(self):
        """Run all API tests and collect results."""
        self.test_available_models()
        self.test_basic_analysis()
        self.test_multi_model_analysis()
        self.test_error_handling()
        self.test_cache_performance()
        return self.print_summary()

    def test_available_models(self):
        """Test the /available-models endpoint."""
        logger.info("Testing available models endpoint...")

        try:
            response = self.test_session.get(f"{self.base_url}/available-models")
            response.raise_for_status()
            data = response.json()

            if "available_models" not in data:
                raise ValueError("Response missing 'available_models' field")

            if not isinstance(data["available_models"], list):
                raise ValueError("'available_models' is not a list")

            if len(data["available_models"]) == 0:
                logger.warning("No models available")

            self.test_results["available_models"] = {
                "status": "success",
                "details": {
                    "models": data["available_models"],
                    "count": len(data["available_models"]),
                    "response_time_ms": response.elapsed.total_seconds() * 1000,
                },
            }
            logger.info(f"Available models: {', '.join(data['available_models'])}")

        except requests.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            self.test_results["available_models"] = {
                "status": "failed",
                "details": {"error": str(e)},
            }
        except ValueError as e:
            logger.error(f"Invalid response: {str(e)}")
            self.test_results["available_models"] = {
                "status": "failed",
                "details": {"error": str(e)},
            }

    def test_basic_analysis(self):
        """Test a basic prompt analysis with a single model."""
        logger.info("Testing basic analysis with one model...")

        # Skip if we don't have available models
        if (
            self.test_results["available_models"]["status"] != "success"
            or len(self.test_results["available_models"]["details"]["models"]) == 0
        ):
            logger.warning(
                "Skipping test_basic_analysis because available_models test failed"
            )
            self.test_results["analyze_basic"] = {
                "status": "skipped",
                "details": {"reason": "No available models"},
            }
            return

        # Choose the first available model
        model = self.test_results["available_models"]["details"]["models"][0]

        try:
            prompt = "What is the capital of France?"
            start_time = time.time()

            response = self.test_session.post(
                f"{self.base_url}/analyze",
                json={
                    "prompt": prompt,
                    "selected_models": [model],
                    "pattern": "standard",
                },
            )
            response.raise_for_status()
            data = response.json()
            end_time = time.time()

            if "results" not in data:
                raise ValueError("Response missing 'results' field")

            if "model_responses" not in data["results"]:
                raise ValueError("Response missing 'model_responses' field")

            if model not in data["results"]["model_responses"]:
                raise ValueError(f"Response missing results for model {model}")

            response_content = data["results"]["model_responses"][model]

            # Check if the response contains "Paris" (case insensitive)
            if "paris" not in response_content.lower():
                logger.warning(
                    f"Response may not be accurate: {response_content[:100]}..."
                )

            self.test_results["analyze_basic"] = {
                "status": "success",
                "details": {
                    "model": model,
                    "prompt": prompt,
                    "response_excerpt": response_content[:100] + "...",
                    "response_time_ms": (end_time - start_time) * 1000,
                },
            }
            logger.info(f"Basic analysis successful with model {model}")

        except requests.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            self.test_results["analyze_basic"] = {
                "status": "failed",
                "details": {"error": str(e)},
            }
        except ValueError as e:
            logger.error(f"Invalid response: {str(e)}")
            self.test_results["analyze_basic"] = {
                "status": "failed",
                "details": {"error": str(e)},
            }

    def test_multi_model_analysis(self):
        """Test analysis with multiple models."""
        logger.info("Testing analysis with multiple models...")

        # Skip if we don't have enough available models
        if (
            self.test_results["available_models"]["status"] != "success"
            or len(self.test_results["available_models"]["details"]["models"]) < 2
        ):
            logger.warning(
                "Skipping test_multi_model_analysis because not enough models are available"
            )
            self.test_results["analyze_multi_model"] = {
                "status": "skipped",
                "details": {"reason": "Not enough available models"},
            }
            return

        # Choose the first two available models
        models = self.test_results["available_models"]["details"]["models"][:2]

        try:
            prompt = "Explain the difference between machine learning and artificial intelligence."
            start_time = time.time()

            response = self.test_session.post(
                f"{self.base_url}/analyze",
                json={
                    "prompt": prompt,
                    "selected_models": models,
                    "pattern": "critique",  # Use critique pattern to test more complex flow
                },
            )
            response.raise_for_status()
            data = response.json()
            end_time = time.time()

            if "results" not in data:
                raise ValueError("Response missing 'results' field")

            if "model_responses" not in data["results"]:
                raise ValueError("Response missing 'model_responses' field")

            # Check that all models responded
            for model in models:
                if model not in data["results"]["model_responses"]:
                    raise ValueError(f"Response missing results for model {model}")

            # Check if ultra response exists
            if "ultra_response" not in data["results"]:
                logger.warning("Response missing 'ultra_response' field")

            self.test_results["analyze_multi_model"] = {
                "status": "success",
                "details": {
                    "models": models,
                    "prompt": prompt,
                    "response_count": len(data["results"]["model_responses"]),
                    "has_ultra_response": "ultra_response" in data["results"],
                    "response_time_ms": (end_time - start_time) * 1000,
                },
            }
            logger.info(
                f"Multi-model analysis successful with models {', '.join(models)}"
            )

        except requests.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            self.test_results["analyze_multi_model"] = {
                "status": "failed",
                "details": {"error": str(e)},
            }
        except ValueError as e:
            logger.error(f"Invalid response: {str(e)}")
            self.test_results["analyze_multi_model"] = {
                "status": "failed",
                "details": {"error": str(e)},
            }

    def test_error_handling(self):
        """Test API error handling with invalid requests."""
        logger.info("Testing error handling...")

        error_scenarios = [
            {
                "name": "empty_prompt",
                "request": {"prompt": "", "selected_models": ["gpt4o"]},
                "expected_status": 400,
            },
            {
                "name": "invalid_model",
                "request": {
                    "prompt": "Test",
                    "selected_models": ["invalid_model_name"],
                },
                "expected_status": [
                    400,
                    404,
                    500,
                ],  # Any of these statuses is acceptable
            },
            {
                "name": "missing_models",
                "request": {"prompt": "Test"},
                "expected_status": 400,
            },
        ]

        results = []

        for scenario in error_scenarios:
            try:
                response = self.test_session.post(
                    f"{self.base_url}/analyze", json=scenario["request"]
                )

                expected_status = scenario["expected_status"]
                if isinstance(expected_status, list):
                    status_matched = response.status_code in expected_status
                else:
                    status_matched = response.status_code == expected_status

                if status_matched:
                    result = {
                        "name": scenario["name"],
                        "status": "success",
                        "details": {
                            "status_code": response.status_code,
                            "response": (
                                response.json()
                                if response.headers.get("content-type")
                                == "application/json"
                                else None
                            ),
                        },
                    }
                else:
                    result = {
                        "name": scenario["name"],
                        "status": "failed",
                        "details": {
                            "expected_status": expected_status,
                            "actual_status": response.status_code,
                            "response": (
                                response.json()
                                if response.headers.get("content-type")
                                == "application/json"
                                else response.text
                            ),
                        },
                    }

            except requests.RequestException as e:
                result = {
                    "name": scenario["name"],
                    "status": "error",
                    "details": {"error": str(e)},
                }

            results.append(result)
            logger.info(f"Error scenario '{scenario['name']}': {result['status']}")

        success_count = sum(1 for r in results if r["status"] == "success")

        self.test_results["analyze_error_handling"] = {
            "status": "success" if success_count == len(error_scenarios) else "partial",
            "details": {
                "scenarios": results,
                "success_rate": f"{success_count}/{len(error_scenarios)}",
            },
        }

    def test_cache_performance(self):
        """Test caching by sending the same request twice."""
        logger.info("Testing cache performance...")

        # Skip if basic analysis failed
        if self.test_results["analyze_basic"]["status"] != "success":
            logger.warning(
                "Skipping test_cache_performance because analyze_basic test failed"
            )
            self.test_results["cache_performance"] = {
                "status": "skipped",
                "details": {"reason": "Basic analysis test failed"},
            }
            return

        # Use the same model as in basic analysis
        model = self.test_results["analyze_basic"]["details"]["model"]
        prompt = "What is the capital of France?"

        try:
            # First request
            start_time1 = time.time()
            response1 = self.test_session.post(
                f"{self.base_url}/analyze",
                json={
                    "prompt": prompt,
                    "selected_models": [model],
                    "pattern": "standard",
                },
            )
            response1.raise_for_status()
            end_time1 = time.time()
            time_first = (end_time1 - start_time1) * 1000

            # Wait a moment
            time.sleep(1)

            # Second request (should be cached)
            start_time2 = time.time()
            response2 = self.test_session.post(
                f"{self.base_url}/analyze",
                json={
                    "prompt": prompt,
                    "selected_models": [model],
                    "pattern": "standard",
                },
            )
            response2.raise_for_status()
            end_time2 = time.time()
            time_second = (end_time2 - start_time2) * 1000

            # Compare times
            time_diff = time_first - time_second
            cache_speedup = (time_diff / time_first) * 100 if time_first > 0 else 0

            # Check if responses match
            data1 = response1.json()
            data2 = response2.json()

            responses_match = data1.get("results", {}).get("model_responses", {}).get(
                model, ""
            ) == data2.get("results", {}).get("model_responses", {}).get(model, "")

            # Determine if caching is working
            is_cached = time_second < time_first and responses_match

            self.test_results["cache_performance"] = {
                "status": "success" if is_cached else "warning",
                "details": {
                    "first_request_ms": time_first,
                    "second_request_ms": time_second,
                    "time_difference_ms": time_diff,
                    "cache_speedup_percent": cache_speedup,
                    "responses_match": responses_match,
                    "caching_appears_enabled": is_cached,
                },
            }

            if is_cached:
                logger.info(
                    f"Cache performance test successful: {cache_speedup:.1f}% speedup"
                )
            else:
                logger.warning("Cache may not be working properly")

        except requests.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            self.test_results["cache_performance"] = {
                "status": "failed",
                "details": {"error": str(e)},
            }

    def print_summary(self):
        """Print a summary of all test results."""
        print("\n" + "=" * 60)
        print("ULTRA MVP END-TO-END TEST RESULTS")
        print("=" * 60)

        for test_name, result in self.test_results.items():
            status_symbol = {
                "success": "✅",
                "partial": "⚠️",
                "warning": "⚠️",
                "failed": "❌",
                "skipped": "⏩",
                "not_run": "⏸️",
            }.get(result["status"], "?")

            print(
                f"\n{status_symbol} {test_name.replace('_', ' ').title()}: {result['status'].upper()}"
            )

            if result["status"] == "success":
                details = result.get("details", {})
                if test_name == "available_models":
                    print(
                        f"  Found {details.get('count', 0)} models: {', '.join(details.get('models', []))[:60]}..."
                    )
                    print(
                        f"  Response time: {details.get('response_time_ms', 0):.1f}ms"
                    )
                elif test_name == "analyze_basic":
                    print(f"  Model: {details.get('model', 'unknown')}")
                    print(
                        f"  Response time: {details.get('response_time_ms', 0):.1f}ms"
                    )
                    print(
                        f"  Response excerpt: {details.get('response_excerpt', 'N/A')}"
                    )
                elif test_name == "analyze_multi_model":
                    print(f"  Models: {', '.join(details.get('models', []))}")
                    print(
                        f"  Response time: {details.get('response_time_ms', 0):.1f}ms"
                    )
                    print(
                        f"  Received {details.get('response_count', 0)} model responses"
                    )
                elif test_name == "analyze_error_handling":
                    print(f"  Success rate: {details.get('success_rate', 'N/A')}")
                elif test_name == "cache_performance":
                    print(
                        f"  First request: {details.get('first_request_ms', 0):.1f}ms"
                    )
                    print(
                        f"  Second request: {details.get('second_request_ms', 0):.1f}ms"
                    )
                    print(
                        f"  Cache speedup: {details.get('cache_speedup_percent', 0):.1f}%"
                    )
            elif result["status"] == "failed" or result["status"] == "warning":
                if "error" in result.get("details", {}):
                    print(f"  Error: {result['details']['error']}")
            elif result["status"] == "skipped":
                print(f"  Reason: {result.get('details', {}).get('reason', 'Unknown')}")

        print("\n" + "=" * 60)

        # Overall summary
        success_count = sum(
            1 for r in self.test_results.values() if r["status"] == "success"
        )
        total_count = len(self.test_results)
        partial_count = sum(
            1
            for r in self.test_results.values()
            if r["status"] in ["partial", "warning"]
        )
        failed_count = sum(
            1 for r in self.test_results.values() if r["status"] == "failed"
        )
        skipped_count = sum(
            1 for r in self.test_results.values() if r["status"] == "skipped"
        )

        print(f"\nSummary: {success_count}/{total_count} tests successful")
        if partial_count > 0:
            print(f"         {partial_count} tests partially successful/warnings")
        if failed_count > 0:
            print(f"         {failed_count} tests failed")
        if skipped_count > 0:
            print(f"         {skipped_count} tests skipped")

        overall_status = (
            "PASSED"
            if success_count + partial_count == total_count - skipped_count
            else "FAILED"
        )
        print(f"\nOverall status: {overall_status}")
        print("=" * 60 + "\n")

        return overall_status == "PASSED"


def main():
    """Run the end-to-end tests."""
    parser = argparse.ArgumentParser(description="Ultra MVP End-to-End Test")
    parser.add_argument("--url", help="Base URL for the API")
    args = parser.parse_args()

    tester = UltraAPITester(base_url=args.url)
    success = tester.run_all_tests()

    # Exit with appropriate status code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
