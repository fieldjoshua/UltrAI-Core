"""
Authentication middleware for the Ultra backend.

This module provides middleware for JWT-based authentication of API requests.
"""

import logging
import os
from typing import Any, Callable, Dict, List, Optional

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.config import Config
from app.utils.jwt import decode_token, is_token_expired
from app.utils.logging import get_logger

# Configure logging
logger = get_logger("auth_middleware")


class AuthMiddleware(BaseHTTPMiddleware):
    """Middleware for JWT-based authentication"""

    def __init__(
        self,
        app: ASGIApp,
        public_paths: Optional[List[str]] = None,
    ):
        """
        Initialize the middleware

        Args:
            app: The ASGI application
            public_paths: Paths that don't require authentication
        """
        super().__init__(app)
        self.public_paths = public_paths or Config.PUBLIC_PATHS
        logger.info(
            f"Initialized AuthMiddleware with {len(self.public_paths)} public paths"
        )

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process the request and apply authentication

        Args:
            request: The request to process
            call_next: The next middleware or route handler

        Returns:
            The response from the next handler or an error response
        """
        # Skip authentication for public paths
        if not Config.ENABLE_AUTH:
            return await call_next(request)

        path = request.url.path
        if any(path.startswith(public_path) for public_path in self.public_paths):
            return await call_next(request)

        # Check for token in Authorization header
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "status": "error",
                    "message": "Missing or invalid authentication token",
                    "code": "auth_error",
                },
            )

        token = auth_header.replace("Bearer ", "")

        # For test tokens in test environment
        if Config.TESTING and token.startswith("test_token_"):
            # Set test user in request state
            request.state.user = {
                "id": "test_user_id",
                "email": "test@example.com",
                "name": "Test User",
                "is_active": True,
            }
            return await call_next(request)

        # Check if token is expired
        if is_token_expired(token):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "status": "error",
                    "message": "Authentication token has expired",
                    "code": "token_expired",
                },
            )

        try:
            # Decode token
            payload = decode_token(token)

            # Check token type
            if payload.get("type") != "access":
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={
                        "status": "error",
                        "message": "Invalid token type",
                        "code": "invalid_token_type",
                    },
                )

            # Get user_id from token
            user_id = payload.get("sub")
            if not user_id:
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={
                        "status": "error",
                        "message": "Invalid token payload",
                        "code": "invalid_token_payload",
                    },
                )

            # Set user in request state
            request.state.user = {
                "id": user_id,
                "email": payload.get("email", "unknown@example.com"),
                "name": payload.get("name", "Unknown User"),
                "is_active": True,
            }

            # Continue with the request
            return await call_next(request)

        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "status": "error",
                    "message": "Authentication failed",
                    "code": "auth_error",
                },
            )


def setup_auth_middleware(
    app: ASGIApp, public_paths: Optional[List[str]] = None
) -> None:
    """
    Set up authentication middleware for the application

    Args:
        app: The ASGI application
        public_paths: Paths that don't require authentication
    """
    # Use configured public paths if not provided
    paths = public_paths or Config.PUBLIC_PATHS

    # Add middleware
    app.add_middleware(AuthMiddleware, public_paths=paths)

    logger.info("Authentication middleware added to application")
