"""
Security Headers Middleware for the UltraAI backend.

This module provides middleware that adds security headers to all API responses to
enhance the security posture of the application.
"""

from typing import Callable, Dict, List, Optional

from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from starlette.types import ASGIApp

from app.utils.logging import get_logger

# Set up logger
logger = get_logger("security_headers", "logs/security.log")

# Default security headers based on OWASP recommendations
DEFAULT_SECURITY_HEADERS = {
    # Prevent MIME type sniffing
    "X-Content-Type-Options": "nosniff",
    # Control how the page can be framed
    "X-Frame-Options": "DENY",
    # Browser XSS protection (although CSP is better, this is for older browsers)
    "X-XSS-Protection": "1; mode=block",
    # Force HTTPS connections
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
    # Content Security Policy - restricts resources that can be loaded
    "Content-Security-Policy": (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://unpkg.com; "
        "object-src 'none'; "
        "img-src 'self' data: https://cdn.jsdelivr.net; "
        "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://unpkg.com; "
        "font-src 'self' https://cdn.jsdelivr.net; "
        "frame-src 'none'; "
        "frame-ancestors 'none'; "
        "base-uri 'self'; "
        "form-action 'self'; "
        "worker-src 'self' blob:; "
        "connect-src 'self' https://api.ultrai.app "
        "wss://api.ultrai.app https://app.ultrai.app;"
    ),
    # Control referrer information
    "Referrer-Policy": "strict-origin-when-cross-origin",
    # Control browser features/permissions
    "Permissions-Policy": (
        "accelerometer=(), autoplay=(), camera=(), "
        "clipboard-read=(), clipboard-write=(), "
        "display-capture=(), document-domain=(), "
        "encrypted-media=(), fullscreen=(), "
        "geolocation=(), gyroscope=(), hid=(), "
        "identity-credentials-get=(), idle-detection=(), "
        "local-fonts=(), magnetometer=(), "
        "microphone=(), midi=(), payment=(), "
        "picture-in-picture=(), "
        "publickey-credentials-get=(), "
        "screen-wake-lock=(), serial=(), "
        "sync-xhr=(), usb=(), web-share=(), "
        "xr-spatial-tracking=()"
    ),
    # Prevent server fingerprinting
    "Server": "UltraAI",
    # Cross-Origin Resource Sharing protection
    "Cross-Origin-Opener-Policy": "same-origin",
    "Cross-Origin-Embedder-Policy": "require-corp",
    "Cross-Origin-Resource-Policy": "same-origin",
    # Cache control - no caching for API responses
    "Cache-Control": "no-store, max-age=0",
    "Pragma": "no-cache",
}

# Paths that need special CSP settings (e.g., documentation)
SPECIAL_CSP_PATHS = {
    "/api/docs": {
        "Content-Security-Policy": (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "object-src 'none'; "
            "img-src 'self' data:; "
            "style-src 'self' 'unsafe-inline'; "
            "font-src 'self'; "
            "frame-src 'self'; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self'"
        ),
    },
    "/api/redoc": {
        "Content-Security-Policy": (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "object-src 'none'; "
            "img-src 'self' data: https:; "
            "style-src 'self' 'unsafe-inline'; "
            "font-src 'self' https:; "
            "frame-src 'self'; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self'"
        ),
    },
}


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware for adding security headers to API responses"""

    def __init__(
        self,
        app: ASGIApp,
        security_headers: Optional[Dict[str, str]] = None,
        special_paths: Optional[Dict[str, Dict[str, str]]] = None,
        skip_paths: Optional[List[str]] = None,
    ):
        """
        Initialize security headers middleware

        Args:
            app: ASGI application
            security_headers: Dictionary of security headers to add to responses
                (overrides default headers)
            special_paths: Dictionary of paths with special header configurations
            skip_paths: List of paths to skip security headers entirely
        """
        super().__init__(app)
        self.security_headers = security_headers or DEFAULT_SECURITY_HEADERS
        self.special_paths = special_paths or SPECIAL_CSP_PATHS
        self.skip_paths = set(skip_paths or ["/health", "/metrics"])

        logger.info(
            f"Initialized SecurityHeadersMiddleware with "
            f"{len(self.security_headers)} headers, "
            f"{len(self.special_paths)} special paths, and "
            f"{len(self.skip_paths)} skipped paths"
        )

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process the request and add security headers to the response

        Args:
            request: FastAPI request object
            call_next: Next middleware/route handler

        Returns:
            Response with security headers added
        """
        # Process the request
        response = await call_next(request)

        # Check if this path should be skipped
        if request.url.path in self.skip_paths:
            return response

        # Determine which headers to use based on path
        headers_to_use = self.security_headers.copy()

        # Check if this path has special header configurations
        for path_prefix, special_headers in self.special_paths.items():
            if request.url.path.startswith(path_prefix):
                # Override the default headers with special headers
                for header_name, header_value in special_headers.items():
                    headers_to_use[header_name] = header_value

        # Add security headers to the response
        for header_name, header_value in headers_to_use.items():
            response.headers[header_name] = header_value

        # Add appropriate Vary header to prevent caching issues
        if "Vary" in response.headers:
            if "Origin" not in response.headers["Vary"]:
                response.headers["Vary"] = response.headers["Vary"] + ", Origin"
        else:
            response.headers["Vary"] = "Origin"

        return response


def setup_security_headers_middleware(
    app: FastAPI,
    custom_headers: Optional[Dict[str, str]] = None,
    special_paths: Optional[Dict[str, Dict[str, str]]] = None,
    skip_paths: Optional[List[str]] = None,
) -> None:
    """
    Set up security headers middleware for a FastAPI application

    Args:
        app: FastAPI application
        custom_headers: Custom security headers to use (overrides default headers)
        special_paths: Dictionary of paths with special header configurations
        skip_paths: List of paths to skip security headers entirely
    """
    # Create merged headers if custom headers are provided
    security_headers = DEFAULT_SECURITY_HEADERS.copy()
    if custom_headers:
        security_headers.update(custom_headers)

    # Add middleware to the application
    app.add_middleware(
        SecurityHeadersMiddleware,
        security_headers=security_headers,
        special_paths=special_paths or SPECIAL_CSP_PATHS,
        skip_paths=skip_paths,
    )

    logger.info("Security headers middleware added to application")
