"""
Middleware package for the Ultra backend.

This package contains middleware components for security, authentication, and request handling.
"""

# Import only actively used middleware
from .combined_auth_middleware import setup_combined_auth_middleware
from .performance_middleware import setup_performance_middleware
from .rate_limit_middleware import RateLimitMiddleware, setup_rate_limit_middleware
from .request_id_middleware import setup_request_id_middleware
from .request_tracking_middleware import RequestTrackingMiddleware
from .security_headers_middleware import (
    SecurityHeadersMiddleware,
    setup_security_headers_middleware,
)
from .telemetry_middleware import setup_telemetry_middleware

__all__ = [
    "setup_combined_auth_middleware",
    "setup_performance_middleware",
    "setup_rate_limit_middleware",
    "setup_request_id_middleware",
    "setup_security_headers_middleware",
    "setup_telemetry_middleware",
    "RateLimitMiddleware",
    "RequestTrackingMiddleware",
    "SecurityHeadersMiddleware",
]
