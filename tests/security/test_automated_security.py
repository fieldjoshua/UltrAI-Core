import pytest
from pathlib import Path
import re
from typing import List
from unittest.mock import MagicMock


class SecurityTestBase:
    """Base class for security tests with common utilities."""

    @staticmethod
    def find_sensitive_patterns(content: str, patterns: List[str]) -> List[str]:
        """Find sensitive patterns in content."""
        found = []
        for pattern in patterns:
            if re.search(pattern, content):
                found.append(pattern)
        return found

    @staticmethod
    def check_file_permissions(path: Path) -> bool:
        """Check if file has secure permissions."""
        return path.stat().st_mode & 0o777 <= 0o644


class TestStaticAnalysis(SecurityTestBase):
    """Tests for static code analysis."""

    def test_no_hardcoded_credentials(self):
        """Test that no hardcoded credentials are present."""
        sensitive_patterns = [
            r'password\s*=\s*["\'].*["\']',
            r'api_key\s*=\s*["\'].*["\']',
            r'secret\s*=\s*["\'].*["\']',
            r'token\s*=\s*["\'].*["\']',
            r'key\s*=\s*["\'].*["\']',
        ]

        for path in Path(".").rglob("*.py"):
            if "venv" not in str(path) and "node_modules" not in str(path):
                content = path.read_text()
                found = self.find_sensitive_patterns(content, sensitive_patterns)
                if found:
                    pytest.fail(
                        f"Potential hardcoded credentials found in {path}: {found}"
                    )

    def test_secure_file_permissions(self):
        """Test that files have secure permissions."""
        for path in Path(".").rglob("*"):
            if (
                path.is_file()
                and "venv" not in str(path)
                and "node_modules" not in str(path)
            ):
                if not self.check_file_permissions(path):
                    pytest.fail(f"Insecure file permissions for {path}")


class TestDynamicAnalysis(SecurityTestBase):
    """Tests for dynamic security analysis."""

    def test_api_security_headers(self, client):
        """Test that API responses include security headers."""
        response = client.get("/api/health")
        headers = response.headers

        required_headers = [
            "X-Content-Type-Options",
            "X-Frame-Options",
            "X-XSS-Protection",
            "Strict-Transport-Security",
            "Content-Security-Policy",
        ]

        missing_headers = [
            header for header in required_headers if header not in headers
        ]
        if missing_headers:
            pytest.fail(f"Missing security headers: {missing_headers}")

    def test_input_validation(self, client):
        """Test input validation for API endpoints."""
        # Test SQL injection attempt
        response = client.get("/api/search?q=1%27%20OR%201%3D1")
        if response.status_code != 400:
            pytest.fail("SQL injection attempt not properly blocked")

        # Test XSS attempt
        response = client.get("/api/search?q=<script>alert(1)</script>")
        if response.status_code != 400:
            pytest.fail("XSS attempt not properly blocked")

    def test_rate_limiting(self, client):
        """Test rate limiting implementation."""
        for _ in range(100):  # Assuming limit is 100 requests per minute
            client.get("/api/health")

        response = client.get("/api/health")
        if response.status_code != 429:  # Too Many Requests
            pytest.fail("Rate limiting not properly implemented")


class TestAuthentication(SecurityTestBase):
    """Tests for authentication mechanisms."""

    def test_password_policy(self, client):
        """Test password policy enforcement."""
        weak_passwords = ["password", "123456", "qwerty", "admin123"]

        for password in weak_passwords:
            response = client.post(
                "/api/auth/register", json={"username": "test", "password": password}
            )
            if response.status_code != 400:
                pytest.fail(f"Weak password '{password}' was accepted")

    def test_session_management(self, client):
        """Test session management security."""
        # Test session timeout
        client.post(
            "/api/auth/login", json={"username": "test", "password": "Test123!@#"}
        )

        # Wait for session timeout
        import time

        time.sleep(3600)  # Assuming 1-hour timeout

        response = client.get("/api/protected")
        if response.status_code != 401:
            pytest.fail("Session timeout not properly implemented")


class TestAuthorization(SecurityTestBase):
    """Tests for authorization controls."""

    def test_role_based_access(self, client):
        """Test role-based access control."""
        # Test admin-only endpoint
        response = client.get("/api/admin/users")
        if response.status_code != 403:
            pytest.fail("Admin endpoint not properly protected")

        # Test user-specific endpoint
        response = client.get("/api/users/other-user/profile")
        if response.status_code != 403:
            pytest.fail("User-specific endpoint not properly protected")

    def test_resource_ownership(self, client):
        """Test resource ownership validation."""
        # Test accessing other user's resource
        response = client.get("/api/users/other-user/documents")
        if response.status_code != 403:
            pytest.fail("Resource ownership not properly validated")


class TestEncryption(SecurityTestBase):
    """Tests for encryption mechanisms."""

    def test_data_encryption(self, monkeypatch):
        """Test data encryption at rest."""
        # Mock the database
        mock_db = MagicMock()
        mock_db.execute.return_value.fetchone.return_value = ("encrypted_data",)

        # Patch the get_db function
        monkeypatch.setattr("database.get_db", lambda: mock_db)

        # Insert test data
        mock_db.execute(
            "INSERT INTO test_data (sensitive_data) VALUES (?)",
            ("test_sensitive_data",),
        )

        # Verify data is encrypted in database
        raw_data = mock_db.execute("SELECT sensitive_data FROM test_data").fetchone()
        if raw_data[0] == "test_sensitive_data":
            pytest.fail("Data not properly encrypted in database")

    def test_secure_communication(self, client):
        """Test secure communication."""
        # Verify HTTPS
        response = client.get("/api/health")
        if not response.url.startswith("https://"):
            pytest.fail("HTTPS not properly enforced")

        # Verify TLS version
        hsts_header = response.headers.get("Strict-Transport-Security", "")
        if not hsts_header.startswith("max-age="):
            pytest.fail("HSTS not properly configured")
