"""
CSRF (Cross-Site Request Forgery) protection middleware for the Ultra backend.

This module provides a FastAPI middleware that adds CSRF protection to
state-changing requests (POST, PUT, DELETE, PATCH) by requiring a CSRF token.
"""

import secrets
import time
from typing import Callable, Dict, List, Optional, Set

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from backend.models.base_models import ErrorResponse
from backend.utils.logging import get_logger

# Set up logger
logger = get_logger("csrf_middleware", "logs/security.log")

# Methods that require CSRF protection
UNSAFE_METHODS = {"POST", "PUT", "DELETE", "PATCH"}

# Store for CSRF tokens (in a production environment, use Redis)
csrf_tokens: Dict[str, Dict[str, float]] = {}  # token -> {user_id, expiry}


class CSRFMiddleware(BaseHTTPMiddleware):
    """Middleware for CSRF protection"""

    def __init__(
        self,
        app: ASGIApp,
        token_header: str = "X-CSRF-Token",
        cookie_name: str = "csrf_token",
        token_expiry: int = 86400,  # 24 hours
        safe_origins: Optional[List[str]] = None,
        exempt_paths: Optional[List[str]] = None,
        exempt_methods: Optional[Set[str]] = None,
    ):
        """
        Initialize CSRF middleware

        Args:
            app: ASGI application
            token_header: Name of the header containing the CSRF token
            cookie_name: Name of the cookie containing the CSRF token
            token_expiry: Token expiry time in seconds
            safe_origins: List of origins that are considered safe
            exempt_paths: Paths exempt from CSRF protection
            exempt_methods: Methods exempt from CSRF protection
        """
        super().__init__(app)
        self.token_header = token_header
        self.cookie_name = cookie_name
        self.token_expiry = token_expiry
        self.safe_origins = safe_origins or []
        self.exempt_paths = exempt_paths or [
            "/api/auth/login",
            "/api/auth/register",
            "/api/auth/refresh",
            "/api/auth/reset-password-request",
            "/api/auth/reset-password",
        ]
        self.exempt_methods = exempt_methods or {"GET", "HEAD", "OPTIONS"}
        logger.info(
            f"Initialized CSRFMiddleware with {len(self.exempt_paths)} exempt paths"
        )

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process the request and validate CSRF token

        Args:
            request: FastAPI request object
            call_next: Next middleware/route handler

        Returns:
            Response
        """
        # Skip CSRF protection if auth is disabled
        from backend.config import Config
        if not Config.ENABLE_AUTH:
            return await call_next(request)
            
        # Skip CSRF protection for safe methods
        if request.method in self.exempt_methods:
            response = await call_next(request)
            return self._set_csrf_cookie(request, response)

        # Skip CSRF protection for exempt paths
        if any(request.url.path.startswith(path) for path in self.exempt_paths):
            response = await call_next(request)
            return self._set_csrf_cookie(request, response)

        # Check if the request is from a safe origin
        origin = request.headers.get("Origin", "")
        referer = request.headers.get("Referer", "")

        # If request is from a safe origin, skip CSRF check
        if origin and any(origin.startswith(safe) for safe in self.safe_origins):
            response = await call_next(request)
            return self._set_csrf_cookie(request, response)

        if referer and any(referer.startswith(safe) for safe in self.safe_origins):
            response = await call_next(request)
            return self._set_csrf_cookie(request, response)

        # For unsafe methods, validate CSRF token
        if request.method in UNSAFE_METHODS:
            # Get CSRF token from header
            csrf_token = request.headers.get(self.token_header)

            # If no token in header, check cookie
            if not csrf_token:
                csrf_token = request.cookies.get(self.cookie_name)

            # Validate CSRF token
            if not self._validate_csrf_token(csrf_token, request):
                return self._create_csrf_error_response(
                    "Invalid or missing CSRF token", "invalid_csrf_token"
                )

        # Process the request
        response = await call_next(request)

        # Set CSRF cookie for next request
        return self._set_csrf_cookie(request, response)

    def _validate_csrf_token(self, token: Optional[str], request: Request) -> bool:
        """
        Validate CSRF token

        Args:
            token: CSRF token
            request: FastAPI request object

        Returns:
            True if token is valid, False otherwise
        """
        if not token:
            return False

        # Check if token exists and is not expired
        token_info = csrf_tokens.get(token)
        if not token_info:
            return False

        expiry = token_info.get("expiry", 0)
        if expiry < time.time():
            # Token expired, remove it
            del csrf_tokens[token]
            return False

        # If the token is associated with a user, check if it matches the current user
        user_id = token_info.get("user_id")
        current_user_id = getattr(request.state, "user_id", None)

        if user_id and current_user_id and user_id != current_user_id:
            return False

        return True

    def _generate_csrf_token(self, request: Request) -> str:
        """
        Generate a new CSRF token

        Args:
            request: FastAPI request object

        Returns:
            CSRF token
        """
        token = secrets.token_hex(32)
        user_id = getattr(request.state, "user_id", None)

        # Store token with expiry
        csrf_tokens[token] = {
            "user_id": user_id,
            "expiry": time.time() + self.token_expiry,
        }

        # Clean up expired tokens (periodically)
        self._cleanup_expired_tokens()

        return token

    def _cleanup_expired_tokens(self) -> None:
        """Clean up expired CSRF tokens"""
        # Only clean up tokens occasionally (1% chance per request)
        if secrets.randbelow(100) != 0:
            return

        current_time = time.time()
        expired_tokens = [
            token
            for token, info in csrf_tokens.items()
            if info.get("expiry", 0) < current_time
        ]

        for token in expired_tokens:
            del csrf_tokens[token]

        if expired_tokens:
            logger.info(f"Cleaned up {len(expired_tokens)} expired CSRF tokens")

    def _set_csrf_cookie(self, request: Request, response: Response) -> Response:
        """
        Set CSRF token cookie in response

        Args:
            request: FastAPI request object
            response: FastAPI response object

        Returns:
            Response with CSRF token cookie
        """
        # Check if response already has CSRF cookie
        # Handle streaming responses that don't have cookies attribute
        if hasattr(response, 'cookies') and self.cookie_name in response.cookies:
            return response

        # Generate new CSRF token
        token = self._generate_csrf_token(request)

        # Set cookie with appropriate security flags
        # Only set cookie if response supports it (not streaming responses)
        if hasattr(response, 'set_cookie'):
            response.set_cookie(
                key=self.cookie_name,
                value=token,
                max_age=self.token_expiry,
                httponly=False,  # JS needs to access this token
                secure=True,
                samesite="lax",
                path="/",
            )

        # Also set the token in a header for single-page applications
        response.headers[self.token_header] = token

        return response

    def _create_csrf_error_response(self, message: str, code: str) -> JSONResponse:
        """
        Create CSRF error response

        Args:
            message: Error message
            code: Error code

        Returns:
            JSONResponse with error details
        """
        error_response = ErrorResponse(
            status="error",
            message=message,
            code=code,
        )

        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content=error_response.dict(exclude_none=True),
        )


def setup_csrf_middleware(
    app: ASGIApp,
    token_header: str = "X-CSRF-Token",
    cookie_name: str = "csrf_token",
    token_expiry: int = 86400,
    safe_origins: Optional[List[str]] = None,
    exempt_paths: Optional[List[str]] = None,
) -> None:
    """
    Set up CSRF middleware for the FastAPI application

    Args:
        app: FastAPI application
        token_header: Name of the header containing the CSRF token
        cookie_name: Name of the cookie containing the CSRF token
        token_expiry: Token expiry time in seconds
        safe_origins: List of origins that are considered safe
        exempt_paths: Paths exempt from CSRF protection
    """
    app.add_middleware(
        CSRFMiddleware,
        token_header=token_header,
        cookie_name=cookie_name,
        token_expiry=token_expiry,
        safe_origins=safe_origins,
        exempt_paths=exempt_paths,
    )
    logger.info("CSRF middleware added to application")
