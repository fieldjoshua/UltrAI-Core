"""
Test runner for MVP minimal deployment
Tests all functionality with resource monitoring
"""

import os
import subprocess
import sys
import time
from typing import Any, Dict

import psutil
import requests

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))


class MinimalDeploymentTester:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.app_process = None
        self.auth_token = None
        self.test_results = {"passed": 0, "failed": 0, "errors": []}

    def start_app(self):
        """Start the minimal app"""
        print("Starting minimal app...")

        # Set minimal environment
        env = os.environ.copy()
        env.update(
            {
                "ENV": "development",
                "USE_MOCK": "true",
                "DATABASE_URL": "sqlite:///./test_ultra.db",
                "SECRET_KEY": "test-secret-key",
                "JWT_SECRET_KEY": "test-jwt-secret",
                "LOG_LEVEL": "INFO",
            }
        )

        # Start app
        self.app_process = subprocess.Popen(
            [sys.executable, "-m", "backend.app_minimal"], env=env
        )

        # Wait for startup
        time.sleep(5)

        # Verify app is running
        try:
            response = requests.get(f"{self.base_url}/api/health")
            if response.status_code == 200:
                print("✓ App started successfully")
            else:
                print("✗ App failed to start")
                raise Exception("App failed to start")
        except Exception as e:
            print(f"✗ Could not connect to app: {e}")
            self.stop_app()
            raise

    def stop_app(self):
        """Stop the app"""
        if self.app_process:
            print("Stopping app...")
            self.app_process.terminate()
            self.app_process.wait()

    def test_endpoint(
        self,
        method: str,
        endpoint: str,
        data: Dict = None,
        headers: Dict = None,
        expected_status: int = 200,
    ) -> Dict[str, Any]:
        """Test an endpoint"""
        url = f"{self.base_url}{endpoint}"

        try:
            response = requests.request(
                method=method, url=url, json=data, headers=headers or {}, timeout=10
            )

            if response.status_code == expected_status:
                print(f"✓ {method} {endpoint} returned {response.status_code}")
                self.test_results["passed"] += 1
                return response.json() if response.content else {}
            else:
                error = f"✗ {method} {endpoint} returned {response.status_code} (expected {expected_status})"
                print(error)
                print(f"  Response: {response.text}")
                self.test_results["failed"] += 1
                self.test_results["errors"].append(error)
                return {}

        except Exception as e:
            error = f"✗ {method} {endpoint} failed: {e}"
            print(error)
            self.test_results["failed"] += 1
            self.test_results["errors"].append(error)
            return {}

    def run_tests(self):
        """Run all tests"""
        print("\n=== MVP Minimal Deployment Test Suite ===\n")

        # Start app
        self.start_app()

        try:
            # Health check
            print("\n--- Health Check ---")
            health = self.test_endpoint("GET", "/api/health")
            if health:
                print(f"  Environment: {health.get('environment')}")
                print(f"  App Type: {health.get('app_type')}")
                print(f"  Dependencies: {health.get('dependencies', {})}")

            # Root endpoint
            print("\n--- Root Endpoint ---")
            root = self.test_endpoint("GET", "/")
            if root:
                print(f"  Features: {root.get('features', {})}")

            # Authentication
            print("\n--- Authentication Tests ---")

            # Register
            register_data = {
                "email": f"test_{int(time.time())}@example.com",
                "password": "SecurePass123!",
                "name": "Test User",
            }
            self.test_endpoint(
                "POST", "/api/auth/register", register_data, expected_status=200
            )

            # Login
            login_data = {
                "email": register_data["email"],
                "password": register_data["password"],
            }
            login_response = self.test_endpoint("POST", "/api/auth/login", login_data)

            if login_response and "access_token" in login_response:
                self.auth_token = login_response["access_token"]
                print("  ✓ Got authentication token")

            # LLM Endpoints
            print("\n--- LLM Endpoints ---")
            self.test_endpoint("GET", "/api/available-models")
            self.test_endpoint("GET", "/api/llm/status")
            self.test_endpoint("GET", "/api/orchestrator/patterns")

            # Analysis
            print("\n--- Analysis Tests ---")
            analysis_data = {
                "prompt": "Test analysis for minimal deployment",
                "models": ["mock"],
                "pattern": "summarize",
            }

            headers = (
                {"Authorization": f"Bearer {self.auth_token}"}
                if self.auth_token
                else {}
            )
            self.test_endpoint("POST", "/analyze", analysis_data, headers=headers)

            # Document Upload
            print("\n--- Document Upload Test ---")
            # Note: This would need multipart form data, simplified for now
            self.test_endpoint(
                "POST", "/api/upload-document", headers=headers, expected_status=503
            )

            # Error Handling
            print("\n--- Error Handling Tests ---")
            self.test_endpoint("GET", "/nonexistent", expected_status=404)
            self.test_endpoint(
                "POST",
                "/api/auth/login",
                {"email": "wrong@example.com", "password": "wrong"},
                expected_status=401,
            )

            # Resource Usage
            print("\n--- Resource Usage ---")
            resources = self.test_endpoint("GET", "/api/internal/resources")
            if resources:
                print(f"  Memory: {resources.get('memory_mb', 0):.2f} MB")
                print(f"  CPU: {resources.get('cpu_percent', 0):.1f}%")
                print(f"  Threads: {resources.get('threads', 0)}")

            # Check process resources
            if self.app_process:
                try:
                    process = psutil.Process(self.app_process.pid)
                    memory_mb = process.memory_info().rss / 1024 / 1024
                    cpu_percent = process.cpu_percent(interval=1)

                    print(f"\n--- Process Metrics ---")
                    print(f"  Memory Usage: {memory_mb:.2f} MB")
                    print(f"  CPU Usage: {cpu_percent:.1f}%")

                    if memory_mb > 512:
                        print(f"  ⚠️  Memory usage exceeds 512MB limit")
                    else:
                        print(f"  ✓ Memory usage within limits")
                except Exception as e:
                    print(f"  Could not get process metrics: {e}")

        finally:
            self.stop_app()

        # Print summary
        print(f"\n=== Test Summary ===")
        print(f"Passed: {self.test_results['passed']}")
        print(f"Failed: {self.test_results['failed']}")

        if self.test_results["errors"]:
            print("\nErrors:")
            for error in self.test_results["errors"]:
                print(f"  - {error}")

        return self.test_results["failed"] == 0


def main():
    """Run the test suite"""
    tester = MinimalDeploymentTester()

    try:
        success = tester.run_tests()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Test suite failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
