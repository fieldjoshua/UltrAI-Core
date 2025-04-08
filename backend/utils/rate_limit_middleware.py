"""
Rate limiting middleware for the Ultra backend.

This module provides a FastAPI middleware that applies rate limits to API requests
based on user subscription tier.
"""

from typing import Callable, Optional

from fastapi import FastAPI, Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from backend.database.models.user import User
from backend.services.auth_service import auth_service
from backend.services.rate_limit_service import rate_limit_service
from backend.utils.logging import get_logger

# Set up logger
logger = get_logger("rate_limit_middleware", "logs/rate_limit.log")


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware for enforcing rate limits on API requests"""

    def __init__(self, app: ASGIApp):
        """
        Initialize rate limit middleware

        Args:
            app: ASGI application
        """
        super().__init__(app)

    async def get_user_from_request(self, request: Request) -> Optional[User]:
        """
        Get the authenticated user from a request, if any

        Args:
            request: FastAPI request object

        Returns:
            User object if authenticated, None otherwise
        """
        # Extract token from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return None

        try:
            # Parse Bearer token
            scheme, token = auth_header.split()
            if scheme.lower() != "bearer":
                return None

            # Verify token and get user ID
            user_id = auth_service.verify_token(token)
            if not user_id:
                return None

            # Get user from database
            # For simplicity, we'll create a fake session here
            # In a real application, you'd use a proper database session
            db = request.state.db if hasattr(request.state, "db") else None
            if not db:
                return None

            # Convert user_id to int
            try:
                user_id_int = int(user_id)
            except ValueError:
                return None

            # Get user from database
            return auth_service.get_user(db, user_id_int)

        except Exception as e:
            logger.error(f"Error getting user from request: {str(e)}")
            return None

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process the request and apply rate limiting

        Args:
            request: FastAPI request object
            call_next: Next middleware/route handler

        Returns:
            Response
        """
        # Skip rate limiting for non-API routes
        if not request.url.path.startswith("/api"):
            return await call_next(request)

        # Get authenticated user, if any
        user = await self.get_user_from_request(request)

        # Check rate limit
        result = rate_limit_service.check_rate_limit(request, user)

        # Add rate limit headers to the response
        response_headers = {
            "X-RateLimit-Limit": str(result.limit),
            "X-RateLimit-Remaining": str(result.remaining),
            "X-RateLimit-Reset": str(result.reset_at)
        }

        # If rate limited, return 429 Too Many Requests
        if not result.is_allowed:
            if result.retry_after:
                response_headers["Retry-After"] = str(result.retry_after)

            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": "Rate limit exceeded",
                    "limit": result.limit,
                    "reset_at": result.reset_at
                },
                headers=response_headers
            )

        # If allowed, proceed with the request
        response = await call_next(request)

        # Add rate limit headers to the response
        for key, value in response_headers.items():
            response.headers[key] = value

        return response


def setup_rate_limit_middleware(app: FastAPI) -> None:
    """
    Set up rate limiting middleware for the FastAPI application

    Args:
        app: FastAPI application
    """
    app.add_middleware(RateLimitMiddleware)