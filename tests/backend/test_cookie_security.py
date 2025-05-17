"""
Tests for cookie security middleware.

This module tests the functionality of the cookie security middleware.
"""

import pytest
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient

from backend.utils.cookie_security_middleware import (
    CookieSecurityMiddleware,
    setup_cookie_security_middleware,
)


@pytest.fixture
def app_with_default_cookie_security():
    """Create FastAPI app with default cookie security settings"""
    app = FastAPI()
    setup_cookie_security_middleware(app)

    @app.get("/cookie/basic")
    def set_basic_cookie():
        response = JSONResponse(content={"message": "test"})
        response.set_cookie(
            key="session",
            value="test-session-value",
            path="/",
        )
        return response

    @app.get("/cookie/with-attributes")
    def set_cookie_with_attributes():
        response = JSONResponse(content={"message": "test"})
        response.set_cookie(
            key="session",
            value="test-session-value",
            path="/",
            max_age=3600,
            expires=3600,
            domain="example.com",
        )
        return response

    @app.get("/cookie/multiple")
    def set_multiple_cookies():
        response = JSONResponse(content={"message": "test"})
        response.set_cookie(key="session", value="session-value", path="/")
        response.set_cookie(key="user", value="user-value", path="/user")
        response.set_cookie(key="theme", value="dark", path="/settings")
        return response

    @app.get("/cookie/already-secure")
    def set_already_secure_cookie():
        response = JSONResponse(content={"message": "test"})
        response.headers["Set-Cookie"] = (
            "secure=value; Path=/; HttpOnly; Secure; SameSite=Lax"
        )
        return response

    return app


@pytest.fixture
def app_with_custom_cookie_security():
    """Create FastAPI app with custom cookie security settings"""
    app = FastAPI()
    setup_cookie_security_middleware(app, secure=True, httponly=True, samesite="Strict")

    @app.get("/cookie/basic")
    def set_basic_cookie():
        response = JSONResponse(content={"message": "test"})
        response.set_cookie(
            key="session",
            value="test-session-value",
            path="/",
        )
        return response

    return app


@pytest.fixture
def app_with_less_secure_settings():
    """Create FastAPI app with less secure cookie settings"""
    app = FastAPI()
    setup_cookie_security_middleware(app, secure=False, httponly=False, samesite="None")

    @app.get("/cookie/basic")
    def set_basic_cookie():
        response = JSONResponse(content={"message": "test"})
        response.set_cookie(
            key="session",
            value="test-session-value",
            path="/",
        )
        return response

    return app


def test_basic_cookie_security(app_with_default_cookie_security):
    """Test that basic cookies have security attributes added"""
    client = TestClient(app_with_default_cookie_security)
    response = client.get("/cookie/basic")

    # Check that the response was successful
    assert response.status_code == 200

    # Get the Set-Cookie header
    cookies = response.headers.get_all("Set-Cookie")
    assert cookies, "No cookies found in response"
    assert len(cookies) == 1, "Expected 1 cookie in response"

    # Check that the cookie has security attributes
    cookie = cookies[0]
    assert "HttpOnly" in cookie
    assert "Secure" in cookie
    assert "SameSite=Lax" in cookie


def test_cookie_with_attributes(app_with_default_cookie_security):
    """Test that cookies with other attributes keep them after security enhancement"""
    client = TestClient(app_with_default_cookie_security)
    response = client.get("/cookie/with-attributes")

    # Get the Set-Cookie header
    cookies = response.headers.get_all("Set-Cookie")
    assert cookies, "No cookies found in response"
    cookie = cookies[0]

    # Check that the cookie has security attributes
    assert "HttpOnly" in cookie
    assert "Secure" in cookie
    assert "SameSite=Lax" in cookie

    # Check that the original attributes are preserved
    assert "Max-Age=3600" in cookie
    assert "Domain=example.com" in cookie
    assert "Path=/" in cookie


def test_multiple_cookies(app_with_default_cookie_security):
    """Test that multiple cookies all get security attributes"""
    client = TestClient(app_with_default_cookie_security)
    response = client.get("/cookie/multiple")

    # Get the Set-Cookie headers
    cookies = response.headers.get_all("Set-Cookie")
    assert cookies, "No cookies found in response"
    assert len(cookies) == 3, "Expected 3 cookies in response"

    # Check that all cookies have security attributes
    for cookie in cookies:
        assert "HttpOnly" in cookie
        assert "Secure" in cookie
        assert "SameSite=Lax" in cookie

    # Verify different paths are preserved
    assert any("Path=/" in cookie for cookie in cookies)
    assert any("Path=/user" in cookie for cookie in cookies)
    assert any("Path=/settings" in cookie for cookie in cookies)


def test_already_secure_cookie(app_with_default_cookie_security):
    """Test that already secure cookies don't get duplicate attributes"""
    client = TestClient(app_with_default_cookie_security)
    response = client.get("/cookie/already-secure")

    # Get the Set-Cookie header
    cookies = response.headers.get_all("Set-Cookie")
    assert cookies, "No cookies found in response"
    cookie = cookies[0]

    # Count occurrences of security attributes (should be only one of each)
    assert cookie.count("HttpOnly") == 1
    assert cookie.count("Secure") == 1
    assert cookie.count("SameSite=Lax") == 1


def test_custom_samesite_policy(app_with_custom_cookie_security):
    """Test that custom SameSite policy is applied"""
    client = TestClient(app_with_custom_cookie_security)
    response = client.get("/cookie/basic")

    # Get the Set-Cookie header
    cookies = response.headers.get_all("Set-Cookie")
    assert cookies, "No cookies found in response"
    cookie = cookies[0]

    # Check for Strict SameSite policy
    assert "SameSite=Strict" in cookie
    assert "SameSite=Lax" not in cookie

    # Other security attributes should be present
    assert "HttpOnly" in cookie
    assert "Secure" in cookie


def test_less_secure_settings(app_with_less_secure_settings):
    """Test middleware with less secure settings"""
    client = TestClient(app_with_less_secure_settings)
    response = client.get("/cookie/basic")

    # Get the Set-Cookie header
    cookies = response.headers.get_all("Set-Cookie")
    assert cookies, "No cookies found in response"
    cookie = cookies[0]

    # Check that Secure and HttpOnly are NOT present
    assert "Secure" not in cookie
    assert "HttpOnly" not in cookie

    # SameSite should be None
    assert "SameSite=None" in cookie


def test_direct_middleware_initialization():
    """Test direct initialization of the middleware class"""
    app = FastAPI()

    # Add middleware directly
    app.add_middleware(
        CookieSecurityMiddleware,
        secure=True,
        httponly=True,
        samesite="Lax",
    )

    # Add test endpoint
    @app.get("/test")
    def test_endpoint():
        response = JSONResponse(content={"message": "test"})
        response.set_cookie(key="test", value="value")
        return response

    client = TestClient(app)
    response = client.get("/test")

    # Check cookie security attributes
    cookies = response.headers.get_all("Set-Cookie")
    assert cookies, "No cookies found in response"

    cookie = cookies[0]
    assert "HttpOnly" in cookie
    assert "Secure" in cookie
    assert "SameSite=Lax" in cookie
