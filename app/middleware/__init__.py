"""
Middleware package for the Ultra backend.

This package contains middleware components for security, authentication, and request handling.
"""

from .api_key_middleware import ApiKeyMiddleware, setup_api_key_middleware
from .auth_middleware import AuthMiddleware, setup_auth_middleware
from .csrf_middleware import CSRFMiddleware, setup_csrf_middleware
from .security_headers_middleware import (
    SecurityHeadersMiddleware,
    setup_security_headers_middleware,
)
from .validation_middleware import ValidationMiddleware, setup_validation_middleware
from .rate_limit_middleware import RateLimitMiddleware, setup_rate_limit_middleware

__all__ = [
    "setup_auth_middleware",
    "setup_api_key_middleware",
    "setup_csrf_middleware",
    "setup_security_headers_middleware",
    "setup_validation_middleware",
    "setup_rate_limit_middleware",
    "AuthMiddleware",
    "ApiKeyMiddleware",
    "CSRFMiddleware",
    "SecurityHeadersMiddleware",
    "ValidationMiddleware",
    "RateLimitMiddleware",
]
