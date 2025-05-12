"""
Authentication middleware for the Ultra backend.

This module provides a FastAPI middleware that validates authentication tokens
and adds the authenticated user to the request state for further processing.
"""

import logging
from typing import Callable, Optional, List, Dict, Any

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from backend.utils.jwt import decode_token, is_token_expired
from backend.utils.logging import get_logger
from backend.models.base_models import ErrorResponse

# Set up logger
logger = get_logger("auth_middleware", "logs/auth.log")

# Token blacklist for logout (in a production environment, use Redis)
token_blacklist = set()


class AuthMiddleware(BaseHTTPMiddleware):
    """Middleware for authenticating requests using JWT tokens"""

    def __init__(
        self,
        app: ASGIApp,
        public_paths: Optional[List[str]] = None,
        auth_header: str = "Authorization",
        cookie_name: Optional[str] = "auth_token",
    ):
        """
        Initialize auth middleware

        Args:
            app: ASGI application
            public_paths: Paths that don't require authentication
            auth_header: Name of the header containing the auth token
            cookie_name: Name of the cookie containing the auth token (optional)
        """
        super().__init__(app)
        self.public_paths = public_paths or [
            "/api/auth/login",
            "/api/auth/register",
            "/api/auth/refresh",
            "/api/auth/reset-password-request",
            "/api/auth/reset-password",
            "/health",
            "/metrics",
            "/api/docs",
            "/api/redoc",
            "/api/openapi.json",
            "/favicon.ico",
        ]
        self.auth_header = auth_header
        self.cookie_name = cookie_name
        logger.info(f"Initialized AuthMiddleware with {len(self.public_paths)} public paths")

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process the request and validate authentication

        Args:
            request: FastAPI request object
            call_next: Next middleware/route handler

        Returns:
            Response
        """
        # Skip authentication for public paths
        if any(request.url.path.startswith(path) for path in self.public_paths):
            return await call_next(request)

        # Get token from header or cookie
        token = self._get_token_from_request(request)

        if not token:
            return self._create_auth_error_response(
                "Missing authentication token", 
                "missing_token",
                status.HTTP_401_UNAUTHORIZED
            )

        # Check if token is blacklisted (logout)
        if token in token_blacklist:
            return self._create_auth_error_response(
                "Token has been invalidated", 
                "invalid_token",
                status.HTTP_401_UNAUTHORIZED
            )

        # Validate token
        try:
            # Check if token is expired
            if is_token_expired(token):
                return self._create_auth_error_response(
                    "Token has expired", 
                    "expired_token",
                    status.HTTP_401_UNAUTHORIZED
                )

            # Decode token
            payload = decode_token(token)
            
            # Get user ID from token
            user_id = payload.get("sub")
            if not user_id:
                return self._create_auth_error_response(
                    "Invalid token payload", 
                    "invalid_payload",
                    status.HTTP_401_UNAUTHORIZED
                )

            # Store user information in request state
            request.state.user_id = user_id
            request.state.token_payload = payload
            request.state.is_authenticated = True

            # Process the request
            return await call_next(request)

        except Exception as e:
            # Log the error
            logger.error(f"Authentication error: {str(e)}")
            
            # Return authentication error
            return self._create_auth_error_response(
                f"Authentication error: {str(e)}", 
                "auth_error",
                status.HTTP_401_UNAUTHORIZED
            )

    def _get_token_from_request(self, request: Request) -> Optional[str]:
        """
        Extract authentication token from request

        Args:
            request: FastAPI request object

        Returns:
            Authentication token if found, None otherwise
        """
        # Try to get token from header
        auth_header = request.headers.get(self.auth_header, "")
        if auth_header.startswith("Bearer "):
            return auth_header.replace("Bearer ", "")

        # Try to get token from cookie if header not found
        if self.cookie_name and request.cookies.get(self.cookie_name):
            return request.cookies.get(self.cookie_name)

        return None

    def _create_auth_error_response(
        self, message: str, code: str, status_code: int
    ) -> JSONResponse:
        """
        Create an authentication error response

        Args:
            message: Error message
            code: Error code
            status_code: HTTP status code

        Returns:
            JSON response with error details
        """
        error_response = ErrorResponse(
            status="error",
            message=message,
            code=code,
        )

        response = JSONResponse(
            status_code=status_code,
            content=error_response.dict(exclude_none=True),
        )

        # Add WWW-Authenticate header for 401 responses
        if status_code == status.HTTP_401_UNAUTHORIZED:
            response.headers["WWW-Authenticate"] = "Bearer"

        return response


def add_token_to_blacklist(token: str) -> None:
    """
    Add a token to the blacklist (for logout)

    Args:
        token: The token to blacklist
    """
    token_blacklist.add(token)
    logger.info(f"Added token to blacklist (current size: {len(token_blacklist)})")


def setup_auth_middleware(
    app: ASGIApp,
    public_paths: Optional[List[str]] = None,
    auth_header: str = "Authorization",
    cookie_name: Optional[str] = "auth_token",
) -> None:
    """
    Set up authentication middleware for the FastAPI application

    Args:
        app: FastAPI application
        public_paths: Paths that don't require authentication
        auth_header: Name of the header containing the auth token
        cookie_name: Name of the cookie containing the auth token (optional)
    """
    app.add_middleware(
        AuthMiddleware,
        public_paths=public_paths,
        auth_header=auth_header,
        cookie_name=cookie_name,
    )
    logger.info("Authentication middleware added to application")