"""
Deployment validation tests for MVP minimal configuration.
Tests to run on actual Render deployment to verify functionality.
"""

import os
import time
from typing import Any, Dict, Optional

import pytest
import requests

# Configuration for deployment testing
DEPLOYMENT_URL = os.getenv("DEPLOYMENT_URL", "https://ultra-mvp.onrender.com")
TEST_TIMEOUT = 30
MAX_RETRIES = 3


class DeploymentValidator:
    """Validator for production deployment testing."""

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.auth_token: Optional[str] = None

    def test_endpoint(
        self,
        endpoint: str,
        method: str = "GET",
        json_data: Optional[Dict] = None,
        headers: Optional[Dict] = None,
    ) -> requests.Response:
        """Test an endpoint with retries."""
        url = f"{self.base_url}{endpoint}"

        for attempt in range(MAX_RETRIES):
            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    json=json_data,
                    headers=headers or {},
                    timeout=TEST_TIMEOUT,
                )
                return response
            except requests.exceptions.RequestException as e:
                if attempt == MAX_RETRIES - 1:
                    raise
                time.sleep(2**attempt)  # Exponential backoff

        raise Exception(f"Failed to reach {url} after {MAX_RETRIES} attempts")

    def authenticate(
        self, email: str = "test@example.com", password: str = "TestPass123!"
    ) -> str:
        """Authenticate and get token."""
        # First try to register (in case user doesn't exist)
        register_data = {"email": email, "password": password, "name": "Test User"}
        self.test_endpoint("/api/auth/register", "POST", register_data)

        # Now login
        login_data = {"email": email, "password": password}
        response = self.test_endpoint("/api/auth/login", "POST", login_data)

        if response.status_code == 200:
            self.auth_token = response.json().get("access_token")
            return self.auth_token

        raise Exception(f"Authentication failed: {response.text}")

    def get_auth_headers(self) -> Dict[str, str]:
        """Get authenticated headers."""
        if not self.auth_token:
            self.authenticate()
        return {"Authorization": f"Bearer {self.auth_token}"}


@pytest.fixture
def validator():
    """Create deployment validator."""
    return DeploymentValidator(DEPLOYMENT_URL)


class TestDeploymentHealth:
    """Test deployment health and availability."""

    def test_deployment_reachable(self, validator):
        """Test that deployment is reachable."""
        response = validator.test_endpoint("/api/health")
        assert (
            response.status_code == 200
        ), f"Deployment not reachable: {response.status_code} {response.text}"

    def test_health_check_response(self, validator):
        """Test health check returns expected data."""
        response = validator.test_endpoint("/api/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] in [
            "ok",
            "warning",
        ], f"Unexpected health status: {data['status']}"
        assert data["service"] == "ultra-api"
        assert data["app_type"] == "minimal"
        assert "dependencies" in data

    def test_dependency_status(self, validator):
        """Test that critical dependencies are available."""
        response = validator.test_endpoint("/api/health")
        data = response.json()

        # SQLAlchemy is required
        assert (
            data["dependencies"]["sqlalchemy"]["available"] is True
        ), "SQLAlchemy not available in deployment"

        # Check optional dependencies
        deps = data["dependencies"]
        print(f"Deployment dependencies: {deps}")


class TestAuthenticationFlow:
    """Test authentication functionality in deployment."""

    def test_user_registration(self, validator):
        """Test user registration works."""
        register_data = {
            "email": f"test_{int(time.time())}@example.com",
            "password": "SecurePass123!",
            "name": "Test User",
        }

        response = validator.test_endpoint("/api/auth/register", "POST", register_data)
        assert response.status_code in [
            200,
            201,
        ], f"Registration failed: {response.text}"

    def test_user_login(self, validator):
        """Test user login works."""
        # Create test user
        email = f"test_{int(time.time())}@example.com"
        password = "SecurePass123!"

        register_data = {"email": email, "password": password, "name": "Test User"}
        validator.test_endpoint("/api/auth/register", "POST", register_data)

        # Test login
        login_data = {"email": email, "password": password}
        response = validator.test_endpoint("/api/auth/login", "POST", login_data)

        assert response.status_code == 200, f"Login failed: {response.text}"
        assert "access_token" in response.json()

    def test_token_refresh(self, validator):
        """Test token refresh functionality."""
        validator.authenticate()
        headers = validator.get_auth_headers()

        response = validator.test_endpoint("/api/auth/refresh", "POST", headers=headers)
        assert response.status_code == 200, f"Token refresh failed: {response.text}"
        assert "access_token" in response.json()


class TestLLMEndpoints:
    """Test LLM-related endpoints in deployment."""

    def test_available_models(self, validator):
        """Test available models endpoint."""
        response = validator.test_endpoint("/api/available-models")
        assert response.status_code == 200

        models = response.json()
        assert isinstance(models, list), "Expected list of models"
        assert len(models) > 0, "No models available"

        # Check model structure
        for model in models:
            assert "id" in model
            assert "name" in model
            assert "provider" in model

    def test_llm_status(self, validator):
        """Test LLM status endpoint."""
        response = validator.test_endpoint("/api/llm/status")
        assert response.status_code == 200

        status = response.json()
        assert "providers" in status
        assert isinstance(status["providers"], dict)

    def test_orchestrator_patterns(self, validator):
        """Test orchestrator patterns endpoint."""
        response = validator.test_endpoint("/api/orchestrator/patterns")
        assert response.status_code == 200

        patterns = response.json()
        assert isinstance(patterns, list), "Expected list of patterns"
        assert len(patterns) > 0, "No patterns available"


class TestDocumentOperations:
    """Test document operations in deployment."""

    def test_document_upload(self, validator):
        """Test document upload functionality."""
        validator.authenticate()
        headers = validator.get_auth_headers()

        # Create test file
        files = {"file": ("test.txt", "Test content for deployment", "text/plain")}

        response = validator.session.post(
            f"{validator.base_url}/api/upload-document",
            files=files,
            headers=headers,
            timeout=TEST_TIMEOUT,
        )

        assert response.status_code in [
            200,
            201,
        ], f"Document upload failed: {response.text}"
        assert "document_id" in response.json()


class TestAnalysisFlow:
    """Test analysis functionality in deployment."""

    def test_simple_analysis(self, validator):
        """Test simple analysis request."""
        validator.authenticate()
        headers = validator.get_auth_headers()

        analysis_data = {
            "prompt": "Test analysis for deployment validation",
            "models": ["mock"],  # Use mock for deployment test
            "pattern": "summarize",
        }

        response = validator.test_endpoint("/analyze", "POST", analysis_data, headers)

        assert response.status_code in [200, 201], f"Analysis failed: {response.text}"

    def test_orchestrator_analysis(self, validator):
        """Test orchestrator analysis."""
        validator.authenticate()
        headers = validator.get_auth_headers()

        orchestrate_data = {
            "prompt": "Test orchestration",
            "models": ["mock"],
            "parameters": {"temperature": 0.7},
        }

        response = validator.test_endpoint(
            "/api/orchestrator/analyze", "POST", orchestrate_data, headers
        )

        assert response.status_code in [
            200,
            201,
        ], f"Orchestration failed: {response.text}"


class TestPerformanceMetrics:
    """Test performance metrics in deployment."""

    def test_response_times(self, validator):
        """Test response times for various endpoints."""
        endpoints = [
            "/api/health",
            "/api/available-models",
            "/api/orchestrator/patterns",
        ]

        response_times = {}

        for endpoint in endpoints:
            start_time = time.time()
            response = validator.test_endpoint(endpoint)
            end_time = time.time()

            response_times[endpoint] = end_time - start_time
            assert response.status_code == 200

        # Check response times
        for endpoint, response_time in response_times.items():
            assert (
                response_time < 5.0
            ), f"Response time for {endpoint} is {response_time}s (>5s)"
            print(f"{endpoint}: {response_time:.3f}s")

    def test_cold_start(self, validator):
        """Test cold start performance."""
        # Wait a bit to ensure cold start
        time.sleep(60)

        start_time = time.time()
        response = validator.test_endpoint("/api/health")
        cold_start_time = time.time() - start_time

        assert response.status_code == 200
        assert cold_start_time < 30, f"Cold start took {cold_start_time}s (>30s)"
        print(f"Cold start time: {cold_start_time:.3f}s")


class TestErrorHandling:
    """Test error handling in deployment."""

    def test_404_handling(self, validator):
        """Test 404 error handling."""
        response = validator.test_endpoint("/nonexistent", method="GET")
        assert response.status_code == 404

    def test_authentication_error(self, validator):
        """Test authentication error handling."""
        response = validator.test_endpoint(
            "/api/auth/login",
            "POST",
            {"email": "wrong@example.com", "password": "wrongpass"},
        )

        assert response.status_code in [401, 403]
        error_data = response.json()
        assert "error_code" in error_data or "detail" in error_data

    def test_validation_error(self, validator):
        """Test validation error handling."""
        response = validator.test_endpoint(
            "/api/auth/register",
            "POST",
            {"email": "invalid-email"},  # Missing required fields
        )

        assert response.status_code in [400, 422]
        error_data = response.json()
        assert "detail" in error_data or "message" in error_data


class TestResourceLimits:
    """Test resource limits in deployment."""

    def test_concurrent_load(self, validator):
        """Test deployment under concurrent load."""
        import concurrent.futures

        def make_request():
            return validator.test_endpoint("/api/health")

        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(make_request) for _ in range(50)]
            results = [f.result() for f in futures]

        success_count = sum(1 for r in results if r.status_code == 200)
        assert (
            success_count >= 40
        ), f"Only {success_count}/50 requests succeeded under load"

    def test_large_request_handling(self, validator):
        """Test handling of large requests."""
        validator.authenticate()
        headers = validator.get_auth_headers()

        # Create large prompt
        large_prompt = "Test " * 10000  # ~50KB

        analysis_data = {
            "prompt": large_prompt,
            "models": ["mock"],
            "pattern": "summarize",
        }

        response = validator.test_endpoint("/analyze", "POST", analysis_data, headers)

        # Should either succeed or return appropriate error
        assert response.status_code in [200, 201, 413]


# Deployment validation summary
def run_deployment_validation():
    """Run all deployment validation tests and generate report."""
    validator = DeploymentValidator(DEPLOYMENT_URL)

    report = {
        "deployment_url": DEPLOYMENT_URL,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "tests": {},
        "summary": {"total": 0, "passed": 0, "failed": 0},
    }

    # Run tests
    test_classes = [
        TestDeploymentHealth,
        TestAuthenticationFlow,
        TestLLMEndpoints,
        TestDocumentOperations,
        TestAnalysisFlow,
        TestPerformanceMetrics,
        TestErrorHandling,
        TestResourceLimits,
    ]

    for test_class in test_classes:
        test_instance = test_class()
        class_name = test_class.__name__
        report["tests"][class_name] = {}

        for method_name in dir(test_instance):
            if method_name.startswith("test_"):
                report["summary"]["total"] += 1

                try:
                    method = getattr(test_instance, method_name)
                    method(validator)
                    report["tests"][class_name][method_name] = "PASSED"
                    report["summary"]["passed"] += 1
                except Exception as e:
                    report["tests"][class_name][method_name] = f"FAILED: {str(e)}"
                    report["summary"]["failed"] += 1

    # Generate report
    print("\n=== Deployment Validation Report ===")
    print(f"URL: {report['deployment_url']}")
    print(f"Time: {report['timestamp']}")
    print(f"\nSummary:")
    print(f"  Total tests: {report['summary']['total']}")
    print(f"  Passed: {report['summary']['passed']}")
    print(f"  Failed: {report['summary']['failed']}")

    print("\nDetailed Results:")
    for class_name, tests in report["tests"].items():
        print(f"\n{class_name}:")
        for test_name, result in tests.items():
            print(f"  {test_name}: {result}")

    return report


if __name__ == "__main__":
    if len(sys.argv) > 1:
        DEPLOYMENT_URL = sys.argv[1]

    run_deployment_validation()
