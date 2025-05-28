"""
Cookie Security Middleware for the UltraAI backend.

This module provides middleware that ensures cookies set by the application
follow security best practices.
"""

from typing import Callable

from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from starlette.types import ASGIApp

from backend.utils.logging import get_logger

# Set up logger
logger = get_logger("cookie_security", "logs/security.log")


class CookieSecurityMiddleware(BaseHTTPMiddleware):
    """Middleware for ensuring cookie security"""

    def __init__(
        self,
        app: ASGIApp,
        secure: bool = True,
        httponly: bool = True,
        samesite: str = "Lax",
    ):
        """
        Initialize cookie security middleware

        Args:
            app: ASGI application
            secure: Whether to set the Secure flag on cookies
            httponly: Whether to set the HttpOnly flag on cookies
            samesite: SameSite attribute (None, Lax, or Strict)
        """
        super().__init__(app)
        self.secure = secure
        self.httponly = httponly
        self.samesite = samesite
        logger.info(
            f"Initialized CookieSecurityMiddleware with "
            f"secure={secure}, httponly={httponly}, samesite={samesite}"
        )

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process the request and enhance security of cookies in the response

        Args:
            request: FastAPI request object
            call_next: Next middleware/route handler

        Returns:
            Response with security-enhanced cookies
        """
        # Process the request
        response = await call_next(request)

        # Get all cookies from the response
        cookies = response.headers.getlist("set-cookie")
        if not cookies:
            return response

        # Create new list of cookies with security attributes
        secure_cookies = []
        for cookie in cookies:
            # Skip if cookie already has desired security attributes
            if all(
                attr in cookie
                for attr in [
                    "SameSite=" + self.samesite,
                    "HttpOnly" if self.httponly else "",
                    "Secure" if self.secure else "",
                ]
                if attr
            ):
                secure_cookies.append(cookie)
                continue

            # Otherwise, add security attributes
            # Parse cookie to preserve its existing attributes
            parts = cookie.split(";")
            base = parts[0]
            attribs = [p.strip() for p in parts[1:]]

            # Add security attributes if not already present
            if self.secure and "Secure" not in attribs:
                attribs.append("Secure")
            if self.httponly and "HttpOnly" not in attribs:
                attribs.append("HttpOnly")

            # Add SameSite if not already present
            if not any(a.lower().startswith("samesite=") for a in attribs):
                attribs.append(f"SameSite={self.samesite}")

            # Combine all parts back into a cookie string
            secure_cookie = f"{base}; {'; '.join(attribs)}"
            secure_cookies.append(secure_cookie)

        # Replace cookies in response
        # Remove existing set-cookie headers
        if "set-cookie" in response.headers:
            del response.headers["set-cookie"]
        for cookie in secure_cookies:
            response.headers.append("set-cookie", cookie)

        return response


def setup_cookie_security_middleware(
    app: FastAPI,
    secure: bool = True,
    httponly: bool = True,
    samesite: str = "Lax",
) -> None:
    """
    Set up cookie security middleware for a FastAPI application

    Args:
        app: FastAPI application
        secure: Whether to set the Secure flag on cookies
        httponly: Whether to set the HttpOnly flag on cookies
        samesite: SameSite attribute (None, Lax, or Strict)
    """
    # Add middleware to the application
    app.add_middleware(
        CookieSecurityMiddleware,
        secure=secure,
        httponly=httponly,
        samesite=samesite,
    )

    logger.info(
        f"Cookie security middleware added to application with "
        f"secure={secure}, httponly={httponly}, samesite={samesite}"
    )
