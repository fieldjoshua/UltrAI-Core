"""
Security headers middleware for the Ultra backend.

This module provides a FastAPI middleware that adds security headers to responses
to help protect against common web vulnerabilities like XSS, clickjacking, and more.
"""

from typing import Callable, Dict, List, Optional

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.utils.logging import get_logger

# Set up logger
logger = get_logger("security_headers_middleware", "logs/security.log")


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware for adding security headers to responses"""

    def __init__(
        self,
        app: ASGIApp,
        csp_directives: Optional[Dict[str, str]] = None,
        hsts_max_age: int = 31536000,  # 1 year
        hsts_include_subdomains: bool = True,
        hsts_preload: bool = False,
        frame_options: str = "DENY",
        content_type_options: str = "nosniff",
        xss_protection: str = "1; mode=block",
        referrer_policy: str = "strict-origin-when-cross-origin",
        permissions_policy: Optional[str] = None,
        exclude_paths: Optional[List[str]] = None,
    ):
        """
        Initialize security headers middleware

        Args:
            app: ASGI application
            csp_directives: Content Security Policy directives
            hsts_max_age: Strict-Transport-Security max-age in seconds
            hsts_include_subdomains: Whether to include subdomains in HSTS
            hsts_preload: Whether to include preload directive in HSTS
            frame_options: X-Frame-Options value
            content_type_options: X-Content-Type-Options value
            xss_protection: X-XSS-Protection value
            referrer_policy: Referrer-Policy value
            permissions_policy: Permissions-Policy value
            exclude_paths: Paths to exclude from security headers
        """
        super().__init__(app)
        self.csp_directives = csp_directives or {
            "default-src": "'self'",
            "script-src": "'self'",
            "style-src": "'self'",
            "img-src": "'self' data:",
            "font-src": "'self'",
            "connect-src": "'self'",
            "frame-src": "'none'",
            "object-src": "'none'",
            "base-uri": "'self'",
            "form-action": "'self'",
        }
        self.hsts_max_age = hsts_max_age
        self.hsts_include_subdomains = hsts_include_subdomains
        self.hsts_preload = hsts_preload
        self.frame_options = frame_options
        self.content_type_options = content_type_options
        self.xss_protection = xss_protection
        self.referrer_policy = referrer_policy
        self.permissions_policy = permissions_policy
        self.exclude_paths = exclude_paths or [
            "/api/docs",
            "/api/redoc",
            "/api/openapi.json",
            "/swagger-ui",
        ]
        logger.info(
            f"Initialized SecurityHeadersMiddleware with {len(self.csp_directives)} CSP directives"
        )

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process the request and add security headers to the response

        Args:
            request: FastAPI request objec
            call_next: Next middleware/route handler

        Returns:
            Response with security headers
        """
        # Process the reques
        response = await call_next(request)

        # Skip adding headers for excluded paths
        if any(request.url.path.startswith(path) for path in self.exclude_paths):
            return response

        # Add security headers
        self._add_content_security_policy(response)
        self._add_hsts_header(response)
        self._add_basic_security_headers(response)

        return response

    def _add_content_security_policy(self, response: Response) -> None:
        """
        Add Content-Security-Policy header to response

        Args:
            response: FastAPI response object
        """
        if self.csp_directives:
            # Ensure critical domains are always included
            directives = dict(self.csp_directives)

            # Always include Google Fonts in style-src
            if "style-src" in directives:
                if "fonts.googleapis.com" not in directives["style-src"]:
                    directives["style-src"] += " https://fonts.googleapis.com"

            # Always include Google Fonts in font-src
            if "font-src" in directives:
                if "fonts.gstatic.com" not in directives["font-src"]:
                    directives["font-src"] += " https://fonts.gstatic.com"

            # Always include production domains in connect-src (https/wss)
            if "connect-src" in directives:
                connect = directives["connect-src"]
                domains = [
                    "https://ultrai-core.onrender.com",
                    "wss://ultrai-core.onrender.com",
                    "https://ultr-ai-core.vercel.app",
                    "wss://ultr-ai-core.vercel.app",
                    "https://ultrai-core-4lut.onrender.com",
                    "wss://ultrai-core-4lut.onrender.com",
                ]
                for d in domains:
                    if d not in connect:
                        connect += f" {d}"
                directives["connect-src"] = connect

            csp_value = "; ".join(
                f"{key} {value}" for key, value in directives.items()
            )
            response.headers["Content-Security-Policy"] = csp_value

    def _add_hsts_header(self, response: Response) -> None:
        """
        Add Strict-Transport-Security header to response

        Args:
            response: FastAPI response objec
        """
        hsts_value = f"max-age={self.hsts_max_age}"
        if self.hsts_include_subdomains:
            hsts_value += "; includeSubDomains"
        if self.hsts_preload:
            hsts_value += "; preload"
        response.headers["Strict-Transport-Security"] = hsts_value

    def _add_basic_security_headers(self, response: Response) -> None:
        """
        Add basic security headers to response

        Args:
            response: FastAPI response objec
        """
        response.headers["X-Frame-Options"] = self.frame_options
        response.headers["X-Content-Type-Options"] = self.content_type_options
        response.headers["X-XSS-Protection"] = self.xss_protection
        response.headers["Referrer-Policy"] = self.referrer_policy

        if self.permissions_policy:
            response.headers["Permissions-Policy"] = self.permissions_policy


def setup_security_headers_middleware(
    app: ASGIApp,
    csp_directives: Optional[Dict[str, str]] = None,
    hsts_max_age: int = 31536000,
    hsts_include_subdomains: bool = True,
    hsts_preload: bool = False,
    exclude_paths: Optional[List[str]] = None,
) -> None:
    """
    Set up security headers middleware for the FastAPI application

    Args:
        app: FastAPI application
        csp_directives: Content Security Policy directives
        hsts_max_age: Strict-Transport-Security max-age in seconds
        hsts_include_subdomains: Whether to include subdomains in HSTS
        hsts_preload: Whether to include preload directive in HSTS
        exclude_paths: Paths to exclude from security headers
    """
    app.add_middleware(
        SecurityHeadersMiddleware,
        csp_directives=csp_directives,
        hsts_max_age=hsts_max_age,
        hsts_include_subdomains=hsts_include_subdomains,
        hsts_preload=hsts_preload,
        exclude_paths=exclude_paths,
    )
    logger.info("Security headers middleware added to application")
