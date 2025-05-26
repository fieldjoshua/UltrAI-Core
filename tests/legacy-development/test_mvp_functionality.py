#!/usr/bin/env python3
"""
MVP Functionality Test Script
Tests core Ultra MVP features in mock mode
"""
import json
import os
import subprocess
import sys
import time
from typing import Any, Dict

import requests

# Set mock mode
os.environ["USE_MOCK"] = "true"
os.environ["MOCK_MODE"] = "true"
os.environ["ENABLE_MOCK_LLM"] = "true"


class MVPTester:
    def __init__(self, base_url: str = "http://localhost:8085"):
        self.base_url = base_url
        self.server_process = None

    def start_server(self):
        """Start the backend server in mock mode"""
        print("Starting Ultra backend in mock mode...")
        self.server_process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "uvicorn",
                "backend.app:app",
                "--host",
                "0.0.0.0",
                "--port",
                "8085",
            ],
            env=os.environ.copy(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        # Wait for server to start
        print("Waiting for server to start...")
        time.sleep(5)

    def stop_server(self):
        """Stop the backend server"""
        if self.server_process:
            print("Stopping server...")
            self.server_process.terminate()
            self.server_process.wait()

    def test_health(self) -> bool:
        """Test health endpoint"""
        try:
            print(f"\n=== Testing Health Endpoint ===")
            headers = {"X-API-Key": "test-api-key"}
            response = requests.get(f"{self.base_url}/api/health", headers=headers)
            print(f"Status: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            return response.status_code == 200
        except Exception as e:
            print(f"Health check failed: {e}")
            return False

    def test_available_models(self) -> bool:
        """Test available models endpoint"""
        try:
            print(f"\n=== Testing Available Models ===")
            headers = {"X-API-Key": "test-api-key"}
            response = requests.get(f"{self.base_url}/api/available-models", headers=headers)
            print(f"Status: {response.status_code}")
            data = response.json()
            print(f"Models found: {len(data.get('models', []))}")
            for model in data.get("models", [])[:3]:
                print(f"  - {model['id']}: {model['name']}")
            return response.status_code == 200
        except Exception as e:
            print(f"Available models test failed: {e}")
            return False

    def test_analyze(self) -> bool:
        """Test analyze endpoint"""
        try:
            print(f"\n=== Testing Analyze Endpoint ===")
            payload = {
                "prompt": "What is artificial intelligence?",
                "selected_models": ["gpt4o", "claude3opus"],
                "pattern": "gut",
                "ultra_model": "gpt4o",
                "output_format": "txt",
                "options": {},
            }

            print(f"Request payload: {json.dumps(payload, indent=2)}")
            headers = {
                "Content-Type": "application/json",
                "X-API-Key": "test-api-key"
            }
            response = requests.post(
                f"{self.base_url}/api/analyze",
                json=payload,
                headers=headers,
            )

            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"Response contains: {list(data.keys())}")
                if "results" in data:
                    print(f"Model responses: {len(data['results'])}")
                return True
            else:
                print(f"Error: {response.text}")
                return False

        except Exception as e:
            print(f"Analyze test failed: {e}")
            return False

    def run_tests(self):
        """Run all MVP tests"""
        try:
            # Run tests
            tests = {
                "Health Check": self.test_health(),
                "Available Models": self.test_available_models(),
                "Analyze Endpoint": self.test_analyze(),
            }

            # Print summary
            print("\n=== Test Summary ===")
            for test_name, result in tests.items():
                status = "✅ PASS" if result else "❌ FAIL"
                print(f"{test_name}: {status}")

            # Overall result
            all_passed = all(tests.values())
            print(
                f"\nOverall: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}"
            )

            return all_passed
        except Exception as e:
            print(f"Test error: {e}")
            return False

    def run_all_tests(self):
        """Run all MVP tests"""
        print("=== Ultra MVP Functionality Test ===")
        print("Mode: Mock")
        print(f"Base URL: {self.base_url}")

        # Start server
        self.start_server()

        try:
            return self.run_tests()
        finally:
            # Stop server
            self.stop_server()


if __name__ == "__main__":
    # Check if --no-start flag is provided
    no_start = "--no-start" in sys.argv
    
    tester = MVPTester()
    
    if no_start:
        print("=== Ultra MVP Functionality Test ===")
        print("Mode: Mock")
        print(f"Base URL: {tester.base_url}")
        print("Server start: Skipped (--no-start flag)")
        success = tester.run_tests()
    else:
        success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)
