#!/usr/bin/env python3
"""
Test script for API endpoints.

This script tests the following endpoints:
1. GET /api/available-models - Returns a list of available LLM models
2. POST /api/analyze - Analyzes a prompt using a model and returns results
"""

import json
import os
import sys
import time
from pprint import pprint
from typing import Any, Dict

import requests

# Add the project root to the Python path to allow imports from backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the config to set mock mode
from backend.config import Config

# Set the base URL for the API
BASE_URL = "http://localhost:8000"


# Colors for console output
class Colors:
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    END = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def print_section(title: str):
    """Print a section header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD} {title} {Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.END}\n")


def print_request(method: str, url: str, data: Dict[str, Any] = None):
    """Print request details"""
    print(f"{Colors.BLUE}{Colors.BOLD}REQUEST:{Colors.END}")
    print(f"{Colors.BLUE}Method: {method}{Colors.END}")
    print(f"{Colors.BLUE}URL: {url}{Colors.END}")
    if data:
        print(f"{Colors.BLUE}Data:{Colors.END}")
        print(json.dumps(data, indent=2))
    print()


def print_response(response, detailed=True):
    """Print response details"""
    print(f"{Colors.CYAN}{Colors.BOLD}RESPONSE:{Colors.END}")
    print(f"{Colors.CYAN}Status Code: {response.status_code}{Colors.END}")

    if response.status_code >= 200 and response.status_code < 300:
        status_color = Colors.GREEN
    else:
        status_color = Colors.FAIL

    print(
        f"{status_color}Status: {'Success' if 200 <= response.status_code < 300 else 'Error'}{Colors.END}"
    )

    if detailed:
        try:
            json_response = response.json()
            print(f"{Colors.CYAN}Response Body:{Colors.END}")
            print(json.dumps(json_response, indent=2))
        except ValueError:
            print(f"{Colors.CYAN}Response Body (non-JSON):{Colors.END}")
            print(response.text[:500])  # Limit to 500 chars
    print()


def test_available_models_endpoint():
    """Test the GET /api/available-models endpoint"""
    print_section("Testing GET /api/available-models Endpoint")

    url = f"{BASE_URL}/api/available-models"
    print_request("GET", url)

    try:
        start_time = time.time()
        response = requests.get(url)
        end_time = time.time()

        print_response(response)

        if response.status_code == 200:
            print(f"{Colors.GREEN}✓ Endpoint is working!{Colors.END}")
            print(
                f"{Colors.GREEN}  Response time: {end_time - start_time:.2f} seconds{Colors.END}"
            )

            # Check if response contains expected fields
            json_response = response.json()
            if "status" in json_response and "available_models" in json_response:
                print(f"{Colors.GREEN}✓ Response contains expected fields{Colors.END}")
                print(
                    f"{Colors.GREEN}✓ Available models: {len(json_response['available_models'])}{Colors.END}"
                )
            else:
                print(f"{Colors.FAIL}✗ Response is missing expected fields{Colors.END}")
        else:
            print(f"{Colors.FAIL}✗ Endpoint returned an error{Colors.END}")
    except requests.exceptions.RequestException as e:
        print(f"{Colors.FAIL}✗ Error connecting to endpoint: {str(e)}{Colors.END}")


def test_analyze_endpoint():
    """Test the POST /api/analyze endpoint"""
    print_section("Testing POST /api/analyze Endpoint")

    url = f"{BASE_URL}/api/analyze"

    # Prepare test data
    data = {
        "prompt": "Explain the differences between Python and JavaScript for web development.",
        "selected_models": ["gpt4o", "claude37"],
        "ultra_model": "claude3opus",
        "pattern": "comparison",
        "output_format": "txt",
        "options": {},
    }

    print_request("POST", url, data)

    try:
        start_time = time.time()
        response = requests.post(url, json=data)
        end_time = time.time()

        print_response(response)

        if response.status_code == 200:
            print(f"{Colors.GREEN}✓ Endpoint is working!{Colors.END}")
            print(
                f"{Colors.GREEN}  Response time: {end_time - start_time:.2f} seconds{Colors.END}"
            )

            # Check if response contains expected fields
            json_response = response.json()
            if "status" in json_response and "results" in json_response:
                print(f"{Colors.GREEN}✓ Response contains expected fields{Colors.END}")

                # Check model responses
                if "model_responses" in json_response["results"]:
                    model_responses = json_response["results"]["model_responses"]
                    print(
                        f"{Colors.GREEN}✓ Model responses received: {len(model_responses)}{Colors.END}"
                    )
                    for model, response_text in model_responses.items():
                        print(
                            f"{Colors.GREEN}  - {model}: {len(response_text)} characters{Colors.END}"
                        )
                else:
                    print(
                        f"{Colors.FAIL}✗ No model responses in the result{Colors.END}"
                    )

                # Check Ultra response
                if "ultra_response" in json_response["results"]:
                    ultra_response = json_response["results"]["ultra_response"]
                    print(
                        f"{Colors.GREEN}✓ Ultra response received: {len(ultra_response)} characters{Colors.END}"
                    )
                else:
                    print(f"{Colors.FAIL}✗ No Ultra response in the result{Colors.END}")

                # Check performance metrics
                if "performance" in json_response["results"]:
                    performance = json_response["results"]["performance"]
                    print(f"{Colors.GREEN}✓ Performance metrics received{Colors.END}")
                    print(
                        f"{Colors.GREEN}  - Total time: {performance.get('total_time_seconds', 'N/A')} seconds{Colors.END}"
                    )
                else:
                    print(
                        f"{Colors.FAIL}✗ No performance metrics in the result{Colors.END}"
                    )
            else:
                print(f"{Colors.FAIL}✗ Response is missing expected fields{Colors.END}")
        else:
            print(f"{Colors.FAIL}✗ Endpoint returned an error{Colors.END}")
    except requests.exceptions.RequestException as e:
        print(f"{Colors.FAIL}✗ Error connecting to endpoint: {str(e)}{Colors.END}")


def main():
    """Main function to run the tests"""
    print_section("API Endpoint Testing")

    # Check if we should use mock mode
    use_mock = Config.use_mock
    print(f"Current mock mode setting: {Colors.BOLD}{use_mock}{Colors.END}")

    # Ask if we should enable mock mode if it's not already enabled
    if not use_mock:
        response = input(
            f"{Colors.WARNING}Do you want to enable mock mode for testing? (y/n): {Colors.END}"
        )
        if response.lower() == "y":
            Config.use_mock = True
            print(f"{Colors.GREEN}Mock mode enabled for this test run.{Colors.END}")
        else:
            print(
                f"{Colors.WARNING}Running tests against real LLM services. This may incur costs.{Colors.END}"
            )

    # Run the tests
    test_available_models_endpoint()
    test_analyze_endpoint()

    print_section("Testing Complete")


if __name__ == "__main__":
    main()
