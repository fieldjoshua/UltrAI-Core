"""
Complete MVP validation test suite for minimal deployment.
Tests ALL MVP features (backend + frontend) to ensure nothing is missing.
"""

import json
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import pytest
import requests


@dataclass
class MVPTestResult:
    """Track test results for reporting."""

    feature: str
    endpoint: str
    status: str
    details: str
    duration: float


class CompleteMVPValidator:
    """Comprehensive MVP validation test suite."""

    def __init__(self, backend_url: str, frontend_url: str):
        self.backend_url = backend_url.rstrip("/")
        self.frontend_url = frontend_url.rstrip("/")
        self.results: List[MVPTestResult] = []
        self.auth_token: Optional[str] = None
        self.test_user_email = f"mvp_test_{int(time.time())}@example.com"
        self.test_password = "MVPTest123!@#"

    def run_all_tests(self) -> Dict[str, Any]:
        """Run complete MVP validation suite."""
        print("Starting Complete MVP Validation Test Suite")
        print("=" * 50)

        test_categories = [
            ("Backend Health", self.test_backend_health),
            ("Authentication System", self.test_authentication_system),
            ("Document Management", self.test_document_management),
            ("LLM Integration", self.test_llm_integration),
            ("Analysis & Orchestration", self.test_analysis_orchestration),
            ("Frontend Pages", self.test_frontend_pages),
            ("UI Components", self.test_ui_components),
            ("End-to-End Workflow", self.test_e2e_workflow),
            ("Performance", self.test_performance),
            ("Error Handling", self.test_error_handling),
        ]

        for category, test_func in test_categories:
            print(f"\nTesting {category}...")
            try:
                test_func()
                print(f"✓ {category} tests passed")
            except Exception as e:
                print(f"✗ {category} tests failed: {e}")
                self.results.append(
                    MVPTestResult(
                        feature=category,
                        endpoint="N/A",
                        status="FAILED",
                        details=str(e),
                        duration=0,
                    )
                )

        return self.generate_report()

    def test_backend_health(self):
        """Test backend health and dependencies."""
        features = {
            "health_check": "/api/health",
            "metrics": "/api/metrics",
            "resources": "/api/internal/resources",
        }

        for feature, endpoint in features.items():
            start_time = time.time()
            try:
                response = requests.get(f"{self.backend_url}{endpoint}")
                duration = time.time() - start_time

                if endpoint == "/api/health":
                    data = response.json()
                    assert data["status"] in [
                        "ok",
                        "warning",
                    ], f"Health status: {data['status']}"
                    assert (
                        data["app_type"] == "mvp-minimal"
                    ), "Not running minimal deployment"

                    # Check required dependencies
                    deps = data["dependencies"]
                    assert deps["sqlalchemy"]["available"], "SQLAlchemy not available"

                    self.results.append(
                        MVPTestResult(
                            feature=f"Backend {feature}",
                            endpoint=endpoint,
                            status="PASSED",
                            details=f"Dependencies: {deps}",
                            duration=duration,
                        )
                    )
                else:
                    assert response.status_code in [200, 503]
                    self.results.append(
                        MVPTestResult(
                            feature=f"Backend {feature}",
                            endpoint=endpoint,
                            status="PASSED",
                            details=f"Status: {response.status_code}",
                            duration=duration,
                        )
                    )

            except Exception as e:
                self.results.append(
                    MVPTestResult(
                        feature=f"Backend {feature}",
                        endpoint=endpoint,
                        status="FAILED",
                        details=str(e),
                        duration=time.time() - start_time,
                    )
                )
                raise

    def test_authentication_system(self):
        """Test all authentication features."""
        auth_features = {
            "register": (
                "POST",
                "/api/auth/register",
                {
                    "email": self.test_user_email,
                    "password": self.test_password,
                    "name": "MVP Test User",
                },
            ),
            "login": (
                "POST",
                "/api/auth/login",
                {"email": self.test_user_email, "password": self.test_password},
            ),
            "refresh": ("POST", "/api/auth/refresh", None),
            "password_reset": (
                "POST",
                "/api/auth/request-password-reset",
                {"email": self.test_user_email},
            ),
        }

        for feature, (method, endpoint, data) in auth_features.items():
            start_time = time.time()
            try:
                headers = {}
                if self.auth_token and feature in ["refresh"]:
                    headers["Authorization"] = f"Bearer {self.auth_token}"

                if method == "POST":
                    response = requests.post(
                        f"{self.backend_url}{endpoint}", json=data, headers=headers
                    )
                else:
                    response = requests.get(
                        f"{self.backend_url}{endpoint}", headers=headers
                    )

                duration = time.time() - start_time

                # Store token for subsequent requests
                if feature == "login" and response.status_code == 200:
                    self.auth_token = response.json().get("access_token")

                assert response.status_code in [
                    200,
                    201,
                    400,
                ], f"Auth {feature} returned {response.status_code}"

                self.results.append(
                    MVPTestResult(
                        feature=f"Auth {feature}",
                        endpoint=endpoint,
                        status="PASSED",
                        details=f"Status: {response.status_code}",
                        duration=duration,
                    )
                )

            except Exception as e:
                self.results.append(
                    MVPTestResult(
                        feature=f"Auth {feature}",
                        endpoint=endpoint,
                        status="FAILED",
                        details=str(e),
                        duration=time.time() - start_time,
                    )
                )
                if feature in ["register", "login"]:  # Critical features
                    raise

    def test_document_management(self):
        """Test document upload and management."""
        if not self.auth_token:
            self.test_authentication_system()

        headers = {"Authorization": f"Bearer {self.auth_token}"}

        # Test document upload
        start_time = time.time()
        try:
            files = {"file": ("test.txt", b"MVP test document content", "text/plain")}
            response = requests.post(
                f"{self.backend_url}/api/upload-document", files=files, headers=headers
            )
            duration = time.time() - start_time

            if response.status_code == 200:
                document_id = response.json().get("document_id")

                # Test document retrieval
                get_response = requests.get(
                    f"{self.backend_url}/api/documents/{document_id}", headers=headers
                )

                self.results.append(
                    MVPTestResult(
                        feature="Document upload",
                        endpoint="/api/upload-document",
                        status="PASSED",
                        details=f"Document ID: {document_id}",
                        duration=duration,
                    )
                )
            else:
                self.results.append(
                    MVPTestResult(
                        feature="Document upload",
                        endpoint="/api/upload-document",
                        status="WARNING",
                        details=f"Status: {response.status_code}",
                        duration=duration,
                    )
                )

        except Exception as e:
            self.results.append(
                MVPTestResult(
                    feature="Document upload",
                    endpoint="/api/upload-document",
                    status="FAILED",
                    details=str(e),
                    duration=time.time() - start_time,
                )
            )

    def test_llm_integration(self):
        """Test LLM provider integration."""
        llm_features = {
            "available_models": "/api/available-models",
            "llm_status": "/api/llm/status",
            "llm_health": "/api/llm/health-check",
            "orchestrator_models": "/api/orchestrator/models",
            "orchestrator_patterns": "/api/orchestrator/patterns",
        }

        for feature, endpoint in llm_features.items():
            start_time = time.time()
            try:
                response = requests.get(f"{self.backend_url}{endpoint}")
                duration = time.time() - start_time

                assert (
                    response.status_code == 200
                ), f"LLM {feature} returned {response.status_code}"

                data = response.json()

                # Validate response structure
                if feature == "available_models":
                    assert isinstance(data, list), "Models should be a list"
                    assert len(data) > 0, "No models available"
                elif feature == "orchestrator_patterns":
                    assert isinstance(data, list), "Patterns should be a list"
                    assert len(data) >= 5, "Should have at least 5 patterns"

                self.results.append(
                    MVPTestResult(
                        feature=f"LLM {feature}",
                        endpoint=endpoint,
                        status="PASSED",
                        details=f"Response: {len(data)} items",
                        duration=duration,
                    )
                )

            except Exception as e:
                self.results.append(
                    MVPTestResult(
                        feature=f"LLM {feature}",
                        endpoint=endpoint,
                        status="FAILED",
                        details=str(e),
                        duration=time.time() - start_time,
                    )
                )

    def test_analysis_orchestration(self):
        """Test analysis and orchestration features."""
        if not self.auth_token:
            self.test_authentication_system()

        headers = {"Authorization": f"Bearer {self.auth_token}"}

        # Test basic analysis
        analysis_data = {
            "prompt": "MVP test prompt for minimal deployment",
            "models": ["mock"],  # Use mock for testing
            "pattern": "summarize",
        }

        start_time = time.time()
        try:
            response = requests.post(
                f"{self.backend_url}/api/analyze", json=analysis_data, headers=headers
            )
            duration = time.time() - start_time

            assert response.status_code in [
                200,
                201,
            ], f"Analysis returned {response.status_code}"

            self.results.append(
                MVPTestResult(
                    feature="Analysis endpoint",
                    endpoint="/api/analyze",
                    status="PASSED",
                    details="Analysis successful",
                    duration=duration,
                )
            )

            # Test orchestrator
            orchestrator_data = {
                "prompt": "MVP orchestrator test",
                "models": ["mock"],
                "parameters": {"temperature": 0.7},
            }

            start_time = time.time()
            response = requests.post(
                f"{self.backend_url}/api/orchestrator/analyze",
                json=orchestrator_data,
                headers=headers,
            )
            duration = time.time() - start_time

            self.results.append(
                MVPTestResult(
                    feature="Orchestrator analysis",
                    endpoint="/api/orchestrator/analyze",
                    status="PASSED" if response.status_code in [200, 201] else "FAILED",
                    details=f"Status: {response.status_code}",
                    duration=duration,
                )
            )

        except Exception as e:
            self.results.append(
                MVPTestResult(
                    feature="Analysis/Orchestration",
                    endpoint="/api/analyze",
                    status="FAILED",
                    details=str(e),
                    duration=time.time() - start_time,
                )
            )

    def test_frontend_pages(self):
        """Test frontend pages are accessible."""
        pages = [
            ("/", "Home/Redirect"),
            ("/analyze", "Analysis Page"),
            ("/documents", "Documents Page"),
            ("/modelrunner", "Model Runner"),
            ("/orchestrator", "Orchestrator Page"),
        ]

        for path, name in pages:
            start_time = time.time()
            try:
                response = requests.get(f"{self.frontend_url}{path}")
                duration = time.time() - start_time

                assert (
                    response.status_code == 200
                ), f"{name} returned {response.status_code}"

                # Basic content validation
                content = response.text
                assert "<html" in content.lower(), "Not an HTML page"
                assert (
                    "error" not in content.lower() or "no error" in content.lower()
                ), "Error found in page"

                self.results.append(
                    MVPTestResult(
                        feature=f"Frontend {name}",
                        endpoint=path,
                        status="PASSED",
                        details=f"Page loaded successfully",
                        duration=duration,
                    )
                )

            except Exception as e:
                self.results.append(
                    MVPTestResult(
                        feature=f"Frontend {name}",
                        endpoint=path,
                        status="FAILED",
                        details=str(e),
                        duration=time.time() - start_time,
                    )
                )

    def test_ui_components(self):
        """Test key UI components are present."""
        # This would typically use Selenium, but for minimal testing
        # we'll check that the JavaScript bundle loads
        start_time = time.time()
        try:
            # Check main JS bundle
            response = requests.get(f"{self.frontend_url}/assets/index.js")

            if response.status_code != 200:
                # Try alternate paths
                for path in [
                    "/static/js/main.js",
                    "/dist/bundle.js",
                    "/build/static/js/main.js",
                ]:
                    response = requests.get(f"{self.frontend_url}{path}")
                    if response.status_code == 200:
                        break

            duration = time.time() - start_time

            assert response.status_code == 200, "Could not find JS bundle"
            assert len(response.content) > 1000, "JS bundle too small"

            # Check for key UI components in the bundle
            js_content = response.text
            key_components = [
                "PromptInput",
                "ModelSelector",
                "AnalysisResults",
                "DocumentUpload",
            ]

            components_found = []
            for component in key_components:
                if component in js_content:
                    components_found.append(component)

            self.results.append(
                MVPTestResult(
                    feature="UI Components",
                    endpoint="/assets/index.js",
                    status="PASSED" if len(components_found) > 2 else "WARNING",
                    details=f"Found components: {components_found}",
                    duration=duration,
                )
            )

        except Exception as e:
            self.results.append(
                MVPTestResult(
                    feature="UI Components",
                    endpoint="/assets/index.js",
                    status="FAILED",
                    details=str(e),
                    duration=time.time() - start_time,
                )
            )

    def test_e2e_workflow(self):
        """Test end-to-end workflow from UI to API."""
        # Simplified E2E test without Selenium
        workflow_steps = [
            ("Load analyze page", "GET", f"{self.frontend_url}/analyze"),
            ("Get available models", "GET", f"{self.backend_url}/api/available-models"),
            ("Get patterns", "GET", f"{self.backend_url}/api/orchestrator/patterns"),
            ("Submit analysis", "POST", f"{self.backend_url}/api/analyze"),
        ]

        for step_name, method, url in workflow_steps:
            start_time = time.time()
            try:
                if method == "GET":
                    response = requests.get(url)
                else:
                    # Analysis request
                    headers = (
                        {"Authorization": f"Bearer {self.auth_token}"}
                        if self.auth_token
                        else {}
                    )
                    data = {
                        "prompt": "E2E workflow test",
                        "models": ["mock"],
                        "pattern": "summarize",
                    }
                    response = requests.post(url, json=data, headers=headers)

                duration = time.time() - start_time

                assert response.status_code in [
                    200,
                    201,
                ], f"{step_name} returned {response.status_code}"

                self.results.append(
                    MVPTestResult(
                        feature=f"E2E {step_name}",
                        endpoint=url,
                        status="PASSED",
                        details=f"Step completed successfully",
                        duration=duration,
                    )
                )

            except Exception as e:
                self.results.append(
                    MVPTestResult(
                        feature=f"E2E {step_name}",
                        endpoint=url,
                        status="FAILED",
                        details=str(e),
                        duration=time.time() - start_time,
                    )
                )

    def test_performance(self):
        """Test performance requirements."""
        # Test concurrent requests
        endpoints = [
            f"{self.backend_url}/api/health",
            f"{self.backend_url}/api/available-models",
            f"{self.frontend_url}/analyze",
        ]

        start_time = time.time()
        try:
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = []
                for _ in range(5):  # 5 concurrent requests per endpoint
                    for endpoint in endpoints:
                        futures.append(executor.submit(requests.get, endpoint))

                results = []
                for future in futures:
                    response = future.result()
                    results.append(response.status_code)

            duration = time.time() - start_time
            success_rate = sum(1 for code in results if code == 200) / len(results)

            assert success_rate > 0.8, f"Only {success_rate*100}% requests succeeded"
            assert duration < 10, f"Concurrent requests took {duration}s"

            self.results.append(
                MVPTestResult(
                    feature="Performance",
                    endpoint="Multiple",
                    status="PASSED",
                    details=f"Success rate: {success_rate*100}%, Duration: {duration:.2f}s",
                    duration=duration,
                )
            )

        except Exception as e:
            self.results.append(
                MVPTestResult(
                    feature="Performance",
                    endpoint="Multiple",
                    status="FAILED",
                    details=str(e),
                    duration=time.time() - start_time,
                )
            )

    def test_error_handling(self):
        """Test error handling across the system."""
        error_scenarios = [
            (
                "Invalid auth",
                "POST",
                f"{self.backend_url}/api/auth/login",
                {"email": "wrong@example.com", "password": "wrong"},
                401,
            ),
            (
                "Missing data",
                "POST",
                f"{self.backend_url}/api/analyze",
                {"prompt": ""},
                422,
            ),
            ("Not found", "GET", f"{self.backend_url}/api/nonexistent", None, 404),
        ]

        for scenario, method, url, data, expected_status in error_scenarios:
            start_time = time.time()
            try:
                if method == "POST":
                    response = requests.post(url, json=data)
                else:
                    response = requests.get(url)

                duration = time.time() - start_time

                assert (
                    response.status_code == expected_status
                ), f"{scenario} returned {response.status_code}, expected {expected_status}"

                # Check error response format
                if response.status_code >= 400:
                    try:
                        error_data = response.json()
                        assert (
                            "error" in error_data or "detail" in error_data
                        ), "No error message in response"
                    except:
                        pass  # Some errors might not be JSON

                self.results.append(
                    MVPTestResult(
                        feature=f"Error handling {scenario}",
                        endpoint=url,
                        status="PASSED",
                        details=f"Correct error status: {response.status_code}",
                        duration=duration,
                    )
                )

            except Exception as e:
                self.results.append(
                    MVPTestResult(
                        feature=f"Error handling {scenario}",
                        endpoint=url,
                        status="FAILED",
                        details=str(e),
                        duration=time.time() - start_time,
                    )
                )

    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report."""
        total_tests = len(self.results)
        passed = sum(1 for r in self.results if r.status == "PASSED")
        failed = sum(1 for r in self.results if r.status == "FAILED")
        warnings = sum(1 for r in self.results if r.status == "WARNING")

        report = {
            "summary": {
                "total_tests": total_tests,
                "passed": passed,
                "failed": failed,
                "warnings": warnings,
                "success_rate": (passed / total_tests * 100) if total_tests > 0 else 0,
                "test_date": time.strftime("%Y-%m-%d %H:%M:%S"),
                "backend_url": self.backend_url,
                "frontend_url": self.frontend_url,
            },
            "results_by_feature": {},
            "failed_tests": [],
            "performance_metrics": {
                "average_response_time": 0,
                "slowest_endpoint": None,
                "fastest_endpoint": None,
            },
        }

        # Group results by feature
        for result in self.results:
            feature = result.feature.split()[0]  # First word of feature
            if feature not in report["results_by_feature"]:
                report["results_by_feature"][feature] = {
                    "passed": 0,
                    "failed": 0,
                    "warning": 0,
                    "tests": [],
                }

            report["results_by_feature"][feature]["tests"].append(
                {
                    "endpoint": result.endpoint,
                    "status": result.status,
                    "details": result.details,
                    "duration": result.duration,
                }
            )

            if result.status == "PASSED":
                report["results_by_feature"][feature]["passed"] += 1
            elif result.status == "FAILED":
                report["results_by_feature"][feature]["failed"] += 1
                report["failed_tests"].append(
                    {
                        "feature": result.feature,
                        "endpoint": result.endpoint,
                        "details": result.details,
                    }
                )
            else:
                report["results_by_feature"][feature]["warning"] += 1

        # Calculate performance metrics
        response_times = [r.duration for r in self.results if r.duration > 0]
        if response_times:
            report["performance_metrics"]["average_response_time"] = sum(
                response_times
            ) / len(response_times)

            slowest = max(self.results, key=lambda r: r.duration)
            fastest = min(
                self.results,
                key=lambda r: r.duration if r.duration > 0 else float("inf"),
            )

            report["performance_metrics"]["slowest_endpoint"] = {
                "endpoint": slowest.endpoint,
                "duration": slowest.duration,
            }
            report["performance_metrics"]["fastest_endpoint"] = {
                "endpoint": fastest.endpoint,
                "duration": fastest.duration,
            }

        return report

    def print_report(self, report: Dict[str, Any]):
        """Print formatted test report."""
        print("\n" + "=" * 60)
        print("MVP VALIDATION TEST REPORT")
        print("=" * 60)

        summary = report["summary"]
        print(f"\nTest Date: {summary['test_date']}")
        print(f"Backend URL: {summary['backend_url']}")
        print(f"Frontend URL: {summary['frontend_url']}")

        print(f"\nTOTAL TESTS: {summary['total_tests']}")
        print(
            f"PASSED: {summary['passed']} ({summary['passed']/summary['total_tests']*100:.1f}%)"
        )
        print(
            f"FAILED: {summary['failed']} ({summary['failed']/summary['total_tests']*100:.1f}%)"
        )
        print(
            f"WARNINGS: {summary['warnings']} ({summary['warnings']/summary['total_tests']*100:.1f}%)"
        )
        print(f"\nSUCCESS RATE: {summary['success_rate']:.1f}%")

        print("\n" + "-" * 40)
        print("RESULTS BY FEATURE")
        print("-" * 40)

        for feature, results in report["results_by_feature"].items():
            print(f"\n{feature}:")
            print(f"  Passed: {results['passed']}")
            print(f"  Failed: {results['failed']}")
            print(f"  Warning: {results['warning']}")

        if report["failed_tests"]:
            print("\n" + "-" * 40)
            print("FAILED TESTS")
            print("-" * 40)

            for test in report["failed_tests"]:
                print(f"\n{test['feature']} - {test['endpoint']}")
                print(f"  Details: {test['details']}")

        metrics = report["performance_metrics"]
        print("\n" + "-" * 40)
        print("PERFORMANCE METRICS")
        print("-" * 40)
        print(f"Average Response Time: {metrics['average_response_time']:.3f}s")

        if metrics["slowest_endpoint"]:
            print(
                f"Slowest Endpoint: {metrics['slowest_endpoint']['endpoint']} "
                f"({metrics['slowest_endpoint']['duration']:.3f}s)"
            )

        if metrics["fastest_endpoint"]:
            print(
                f"Fastest Endpoint: {metrics['fastest_endpoint']['endpoint']} "
                f"({metrics['fastest_endpoint']['duration']:.3f}s)"
            )

        print("\n" + "=" * 60)
        print("END OF REPORT")
        print("=" * 60)

    def save_report(self, report: Dict[str, Any], filename: str = None):
        """Save report to JSON file."""
        if not filename:
            filename = f"mvp_validation_report_{int(time.time())}.json"

        with open(filename, "w") as f:
            json.dump(report, f, indent=2)

        print(f"\nReport saved to: {filename}")


def main():
    """Run the complete MVP validation test."""
    import sys

    backend_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    frontend_url = sys.argv[2] if len(sys.argv) > 2 else "http://localhost:3000"

    print(f"Testing MVP deployment:")
    print(f"Backend: {backend_url}")
    print(f"Frontend: {frontend_url}")

    validator = CompleteMVPValidator(backend_url, frontend_url)
    report = validator.run_all_tests()

    validator.print_report(report)
    validator.save_report(report)

    # Exit with appropriate code
    if report["summary"]["failed"] > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
