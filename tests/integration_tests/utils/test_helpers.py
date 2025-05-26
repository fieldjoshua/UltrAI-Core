"""Test Helper Utilities for Integration Testing"""

import asyncio
import json
import os
import time
from contextlib import contextmanager
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import jwt
import pytest
import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class TestConfig:
    """Test configuration"""

    BASE_URL = os.getenv("TEST_BASE_URL", "http://localhost:8087")
    API_BASE = f"{BASE_URL}/api"

    # Database
    DATABASE_URL = os.getenv(
        "TEST_DATABASE_URL",
        "postgresql://ultra_test:test_password@localhost:5433/ultra_test",
    )

    # Redis
    REDIS_URL = os.getenv("TEST_REDIS_URL", "redis://localhost:6380")

    # Auth
    JWT_SECRET = os.getenv("JWT_SECRET", "test-secret-key")
    JWT_ALGORITHM = "HS256"

    # Timeouts
    DEFAULT_TIMEOUT = 30
    HEALTH_CHECK_TIMEOUT = 60


class APIClient:
    """API client for integration testing"""

    def __init__(self, base_url: str = TestConfig.API_BASE):
        self.base_url = base_url
        self.session = requests.Session()
        self.token = None

    def set_auth_token(self, token: str):
        """Set authentication token"""
        self.token = token
        self.session.headers.update({"Authorization": f"Bearer {token}"})

    def clear_auth(self):
        """Clear authentication"""
        self.token = None
        self.session.headers.pop("Authorization", None)

    def request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make an API request"""
        url = f"{self.base_url}{endpoint}"
        return self.session.request(method, url, **kwargs)

    def get(self, endpoint: str, **kwargs) -> requests.Response:
        """GET request"""
        return self.request("GET", endpoint, **kwargs)

    def post(self, endpoint: str, **kwargs) -> requests.Response:
        """POST request"""
        return self.request("POST", endpoint, **kwargs)

    def put(self, endpoint: str, **kwargs) -> requests.Response:
        """PUT request"""
        return self.request("PUT", endpoint, **kwargs)

    def delete(self, endpoint: str, **kwargs) -> requests.Response:
        """DELETE request"""
        return self.request("DELETE", endpoint, **kwargs)


class TestUser:
    """Test user management"""

    def __init__(self, api_client: APIClient):
        self.api_client = api_client
        self.created_users = []

    def create_user(self, email: str = None, password: str = None) -> Dict[str, Any]:
        """Create a test user"""
        if not email:
            email = f"test_{int(time.time())}@example.com"
        if not password:
            password = "Test123!@#"

        response = self.api_client.post(
            "/auth/register", json={"email": email, "password": password}
        )
        response.raise_for_status()

        user_data = response.json()
        self.created_users.append(user_data["user"]["id"])
        return user_data

    def login_user(self, email: str, password: str) -> str:
        """Login a user and return token"""
        response = self.api_client.post(
            "/auth/login", json={"email": email, "password": password}
        )
        response.raise_for_status()

        data = response.json()
        return data["access_token"]

    def cleanup(self):
        """Clean up created users"""
        for user_id in self.created_users:
            try:
                self.api_client.delete(f"/admin/users/{user_id}")
            except Exception:
                pass
        self.created_users.clear()


class DatabaseHelper:
    """Database helper for testing"""

    def __init__(self, database_url: str = TestConfig.DATABASE_URL):
        self.engine = create_engine(database_url)
        self.SessionLocal = sessionmaker(bind=self.engine)

    @contextmanager
    def get_session(self):
        """Get database session"""
        session = self.SessionLocal()
        try:
            yield session
        finally:
            session.close()

    def reset_database(self):
        """Reset database to clean state"""
        with self.get_session() as session:
            # Clear test data
            session.execute("TRUNCATE TABLE users CASCADE")
            session.execute("TRUNCATE TABLE documents CASCADE")
            session.execute("TRUNCATE TABLE analysis_results CASCADE")
            session.commit()


class MockService:
    """Mock service management"""

    @staticmethod
    def simulate_llm_failure(model: str, duration: int = 60):
        """Simulate LLM provider failure"""
        response = requests.post(
            "http://localhost:8086/admin/failures",
            json={"model": model, "duration": duration},
        )
        response.raise_for_status()

    @staticmethod
    def reset_mocks():
        """Reset all mock services"""
        response = requests.post("http://localhost:8086/admin/reset")
        response.raise_for_status()


def wait_for_service(url: str, timeout: int = TestConfig.HEALTH_CHECK_TIMEOUT):
    """Wait for service to be healthy"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(f"{url}/health", timeout=5)
            if response.status_code == 200:
                return True
        except requests.exceptions.RequestException:
            pass
        time.sleep(1)
    raise TimeoutError(
        f"Service at {url} did not become healthy within {timeout} seconds"
    )


def generate_test_jwt(user_id: str, expires_in: int = 3600) -> str:
    """Generate test JWT token"""
    payload = {
        "sub": user_id,
        "exp": datetime.utcnow() + timedelta(seconds=expires_in),
        "iat": datetime.utcnow(),
    }
    return jwt.encode(
        payload, TestConfig.JWT_SECRET, algorithm=TestConfig.JWT_ALGORITHM
    )


def upload_test_document(api_client: APIClient, file_path: str) -> Dict[str, Any]:
    """Upload a test document"""
    with open(file_path, "rb") as f:
        files = {"file": (os.path.basename(file_path), f, "application/pdf")}
        response = api_client.post("/documents/upload", files=files)
        response.raise_for_status()
        return response.json()


class PerformanceTracker:
    """Track performance metrics during tests"""

    def __init__(self):
        self.metrics = []

    @contextmanager
    def track(self, operation: str):
        """Track operation performance"""
        start_time = time.time()
        try:
            yield
        finally:
            duration = time.time() - start_time
            self.metrics.append(
                {
                    "operation": operation,
                    "duration": duration,
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )

    def get_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        if not self.metrics:
            return {}

        durations = [m["duration"] for m in self.metrics]
        return {
            "total_operations": len(self.metrics),
            "total_duration": sum(durations),
            "avg_duration": sum(durations) / len(durations),
            "min_duration": min(durations),
            "max_duration": max(durations),
            "operations": self.metrics,
        }


# Pytest fixtures
@pytest.fixture
def api_client():
    """API client fixture"""
    client = APIClient()
    yield client


@pytest.fixture
def test_user(api_client):
    """Test user fixture"""
    user_helper = TestUser(api_client)
    yield user_helper
    user_helper.cleanup()


@pytest.fixture
def db_helper():
    """Database helper fixture"""
    helper = DatabaseHelper()
    yield helper


@pytest.fixture
def performance_tracker():
    """Performance tracker fixture"""
    tracker = PerformanceTracker()
    yield tracker


@pytest.fixture(scope="session")
def wait_for_services():
    """Wait for all services to be healthy"""
    services = [
        TestConfig.BASE_URL,
        "http://localhost:5433",  # Test DB
        "http://localhost:6380",  # Test Redis
        "http://localhost:8086",  # Mock LLM
    ]

    for service in services:
        wait_for_service(service)
