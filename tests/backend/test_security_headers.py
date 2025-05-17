"""
Tests for security headers middleware.

This module tests the functionality of the security headers middleware.
"""

import pytest
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient

from backend.utils.cookie_security_middleware import setup_cookie_security_middleware
from backend.utils.security_headers_middleware import (
    DEFAULT_SECURITY_HEADERS,
    setup_security_headers_middleware,
)


@pytest.fixture
def app_with_security_headers():
    """Create a FastAPI application with security headers middleware"""
    app = FastAPI()
    setup_security_headers_middleware(app)

    @app.get("/test")
    def test_endpoint():
        return {"message": "test"}

    @app.get("/health")
    def health_endpoint():
        return {"status": "healthy"}

    @app.get("/docs")
    def docs_endpoint():
        return {"message": "documentation"}

    return app


@pytest.fixture
def app_with_custom_headers():
    """Create FastAPI app with custom security headers"""
    app = FastAPI()

    custom_headers = {
        "X-Custom-Security-Header": "test-value",
        "Content-Security-Policy": "default-src 'self'; script-src 'self'",
    }

    setup_security_headers_middleware(
        app,
        custom_headers=custom_headers,
        special_paths={"/api/special": {"Content-Security-Policy": "default-src *"}},
        skip_paths=["/skip", "/health"],
    )

    @app.get("/test")
    def test_endpoint():
        return {"message": "test"}

    @app.get("/skip")
    def skip_endpoint():
        return {"message": "skipped"}

    @app.get("/api/special")
    def special_endpoint():
        return {"message": "special"}

    @app.get("/health")
    def health_endpoint():
        return {"status": "healthy"}

    return app


@pytest.fixture
def app_with_cookie_security():
    """Create a FastAPI application with cookie security middleware"""
    app = FastAPI()
    setup_cookie_security_middleware(app)

    @app.get("/test-cookie")
    def test_cookie_endpoint():
        response = JSONResponse(content={"message": "test"})
        response.set_cookie(key="test", value="value", path="/")
        return response

    @app.get("/test-multiple-cookies")
    def test_multiple_cookies_endpoint():
        response = JSONResponse(content={"message": "test"})
        response.set_cookie(key="test1", value="value1", path="/")
        response.set_cookie(key="test2", value="value2", path="/api")
        response.set_cookie(key="test3", value="value3", path="/docs")
        return response

    return app


def test_security_headers_present(app_with_security_headers):
    """Test that security headers are present in responses"""
    client = TestClient(app_with_security_headers)
    response = client.get("/test")

    # Check that the response was successful
    assert response.status_code == 200

    # Check that all expected security headers are present
    for header_name, expected_value in DEFAULT_SECURITY_HEADERS.items():
        assert response.headers.get(header_name) == expected_value

    # Verify specific important headers
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "DENY"
    assert "Content-Security-Policy" in response.headers
    assert "X-XSS-Protection" in response.headers
    assert "Strict-Transport-Security" in response.headers
    assert "Referrer-Policy" in response.headers
    assert "Permissions-Policy" in response.headers


def test_security_headers_excluded_paths(app_with_security_headers):
    """Test that security headers are not added to excluded paths"""
    client = TestClient(app_with_security_headers)
    response = client.get("/health")

    # Check excluded paths don't have security headers
    assert "X-Content-Type-Options" not in response.headers
    assert "X-Frame-Options" not in response.headers


def test_custom_security_headers(app_with_custom_headers):
    """Test custom security header configuration"""
    client = TestClient(app_with_custom_headers)

    # Test regular endpoint with custom headers
    response = client.get("/test")
    assert response.headers.get("X-Custom-Security-Header") == "test-value"
    assert (
        response.headers.get("Content-Security-Policy")
        == "default-src 'self'; script-src 'self'"
    )

    # Test skipped endpoint
    skip_response = client.get("/skip")
    assert "X-Custom-Security-Header" not in skip_response.headers
    assert "Content-Security-Policy" not in skip_response.headers

    # Test special path with custom CSP
    special_response = client.get("/api/special")
    assert special_response.headers.get("Content-Security-Policy") == "default-src *"
    assert special_response.headers.get("X-Custom-Security-Header") == "test-value"


def test_cookie_security(app_with_cookie_security):
    """Test that cookies have security attributes"""
    client = TestClient(app_with_cookie_security)
    response = client.get("/test-cookie")

    # Check that the response was successful
    assert response.status_code == 200

    # Get the Set-Cookie header
    cookies = response.headers.get_all("Set-Cookie")
    assert cookies, "No cookies found in response"

    # Check that all cookies have security attributes
    for cookie in cookies:
        assert "HttpOnly" in cookie
        assert "Secure" in cookie
        assert "SameSite=Lax" in cookie


def test_multiple_cookies_security(app_with_cookie_security):
    """Test that multiple cookies all have security attributes"""
    client = TestClient(app_with_cookie_security)
    response = client.get("/test-multiple-cookies")

    # Check that the response was successful
    assert response.status_code == 200

    # Get all cookies
    cookies = response.headers.get_all("Set-Cookie")
    assert len(cookies) == 3, "Expected 3 cookies in response"

    # Check each cookie has proper security attributes
    for cookie in cookies:
        assert "HttpOnly" in cookie
        assert "Secure" in cookie
        assert "SameSite=Lax" in cookie

    # Verify cookie values are preserved
    assert "test1=value1" in cookies[0]
    assert "test2=value2" in cookies[1]
    assert "test3=value3" in cookies[2]
