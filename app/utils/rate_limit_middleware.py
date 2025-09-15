"""
Rate limiting middleware for the Ultra backend.

This module provides a FastAPI middleware that applies rate limits to API requests
based on user subscription tier, path, and method.
"""

import time
import uuid
from typing import Any, Callable, Dict, List, Optional

from fastapi import FastAPI, Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.database.models.user import User
from app.models.base_models import ErrorResponse
from app.services.auth_service import auth_service
from app.utils.logging import get_logger
from app.utils.rate_limit_service import rate_limit_service

# Set up logger
logger = get_logger("rate_limit_middleware", "logs/rate_limit.log")

# Internal service token header
INTERNAL_SERVICE_HEADER = "X-Internal-Service-Token"
# Header for bypass keys
BYPASS_KEY_HEADER = "X-Rate-Limit-Bypass"


class RateLimitMiddleware(BaseHTTPMiddleware):
    """[Deprecated] Use app.middleware.rate_limit_middleware.RateLimitMiddleware instead."""

    def __init__(
        self,
        app: ASGIApp,
        exclude_paths: Optional[List[str]] = None,
        quota_paths: Optional[Dict[str, Dict[str, int]]] = None,
    ):
        """
        Initialize rate limit middleware

        Args:
            app: ASGI application
            exclude_paths: Paths to exclude from rate limiting
            quota_paths: Path-specific quota configurations by subscription tier
        """
        super().__init__(app)
        self.exclude_paths = exclude_paths or [
            "/health",
            "/metrics",
            "/api/docs",
            "/api/redoc",
            "/api/openapi.json",
        ]
        self.quota_paths = quota_paths or {}
        logger.info(
            f"[Deprecated utils middleware] Initialized with {len(self.exclude_paths)} excluded paths and {len(self.quota_paths)} path-specific quotas."
        )

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process the request and apply rate limiting

        Args:
            request: FastAPI request object
            call_next: Next middleware/route handler

        Returns:
            Response with rate limit headers added
        """
        start_time = time.time()

        # Skip rate limiting for excluded paths
        if any(request.url.path.startswith(path) for path in self.exclude_paths):
            return await call_next(request)

        # Generate a unique request ID for tracking
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        # Get client IP address
        client_host = request.client.host if request.client else "unknown"

        # Get user ID from authentication if available
        user_id = None
        user = None
        subscription_tier = "anonymous"

        try:
            token = request.headers.get("Authorization", "").replace("Bearer ", "")
            if token:
                user = await auth_service.get_user_from_token(token)
                if user:
                    user_id = str(user.id)
                    subscription_tier = getattr(user, "subscription_tier", "free")
        except Exception as e:
            logger.warning(f"Error getting user from token: {str(e)}")

        # Get request method and path
        method = request.method
        path = request.url.path

        # Check for internal service token
        internal_token = request.headers.get(INTERNAL_SERVICE_HEADER)

        # Check for bypass key
        bypass_key = request.headers.get(BYPASS_KEY_HEADER)
        if bypass_key:
            # Validate bypass key (you might want to implement a proper validation mechanism)
            is_valid_bypass = (
                bypass_key.startswith("ultra_bypass_") and len(bypass_key) > 20
            )
            if is_valid_bypass:
                logger.info(f"Rate limit bypass key used for request to {path}")
                response = await call_next(request)
                response.headers["X-Rate-Limit-Bypassed"] = "true"
                return response

        # Check rate limit
        try:
            # Check if there are path-specific quotas
            path_quota = None
            for pattern, quotas in self.quota_paths.items():
                if path.startswith(pattern):
                    path_quota = quotas.get(subscription_tier)
                    break

            is_limited, rate_limit_info = rate_limit_service.check_rate_limit(
                ip_address=client_host,
                user_id=user_id,
                path=path,
                method=method,
                internal_token=internal_token,
                path_quota=path_quota,
            )

            # Add request tracking
            rate_limit_service.track_request(
                user_id=user_id,
                ip_address=client_host,
                path=path,
                method=method,
                subscription_tier=subscription_tier,
            )

            if is_limited:
                # Calculate retry after seconds
                retry_after = max(
                    1, int(rate_limit_info.get("reset", time.time() + 60) - time.time())
                )

                logger.warning(
                    f"Rate limit exceeded for {client_host} (user: {user_id}, tier: {subscription_tier}) "
                    f"path: {request.url.path}, method: {method}, count: {rate_limit_info.get('count', 0)}/{rate_limit_info.get('limit', 0)}"
                )

                error_response = ErrorResponse(
                    status="error",
                    message="Rate limit exceeded. Please try again later.",
                    code="rate_limit_exceeded",
                    details={
                        "limit": rate_limit_info.get("limit", 0),
                        "reset": rate_limit_info.get("reset", 0),
                        "retry_after": retry_after,
                        "tier": subscription_tier,
                        "request_id": request_id,
                    },
                )

                response = JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content=error_response.dict(exclude_none=True),
                )

                # Add rate limit headers
                response.headers["X-RateLimit-Limit"] = str(
                    rate_limit_info.get("limit", 0)
                )
                response.headers["X-RateLimit-Remaining"] = "0"
                response.headers["X-RateLimit-Reset"] = str(
                    rate_limit_info.get("reset", 0)
                )
                response.headers["Retry-After"] = str(retry_after)
                response.headers["X-Request-ID"] = request_id

                # Log response time for monitoring
                duration = time.time() - start_time
                logger.info(f"Rate limit response time: {duration:.4f}s for {path}")

                return response

            # Process the request
            response = await call_next(request)

            # Add rate limit headers to the response
            try:
                if hasattr(response, "headers"):
                    response.headers["X-RateLimit-Limit"] = str(
                        rate_limit_info.get("limit", 0)
                    )
                    response.headers["X-RateLimit-Remaining"] = str(
                        rate_limit_info.get("remaining", 0)
                    )
                    response.headers["X-RateLimit-Reset"] = str(
                        rate_limit_info.get("reset", 0)
                    )
                    response.headers["X-Request-ID"] = request_id
            except Exception as e:
                logger.error(f"Error adding rate limit headers: {str(e)}")

            return response

        except Exception as e:
            logger.error(f"Error applying rate limiting: {str(e)}")

            # Continue processing even if rate limiting fails
            return await call_next(request)


def setup_rate_limit_middleware(
    app: FastAPI,
    exclude_paths: Optional[List[str]] = None,
    quota_paths: Optional[Dict[str, Dict[str, int]]] = None,
) -> None:
    """
    Set up rate limiting middleware for the FastAPI application

    Args:
        app: FastAPI application
        exclude_paths: Paths to exclude from rate limiting
        quota_paths: Path-specific quota configurations by subscription tier
    """
    # Default path-specific quotas if not provided
    if quota_paths is None:
        quota_paths = {
            "/api/llm/": {
                "anonymous": 10,
                "free": 30,
                "basic": 100,
                "premium": 300,
                "enterprise": 1000,
            },
            "/api/document/": {
                "anonymous": 5,
                "free": 20,
                "basic": 50,
                "premium": 200,
                "enterprise": 500,
            },
            "/api/analyze/": {
                "anonymous": 5,
                "free": 15,
                "basic": 80,
                "premium": 250,
                "enterprise": 800,
            },
        }

    app.add_middleware(
        RateLimitMiddleware,
        exclude_paths=exclude_paths,
        quota_paths=quota_paths,
    )
    logger.info("Rate limiting middleware added to application")


# Standalone middleware function for backward compatibility
async def rate_limit_middleware(request: Request, call_next):
    """
    Rate limiting middleware function (backward compatibility)

    Args:
        request: FastAPI request
        call_next: Next middleware or route handler

    Returns:
        Response from next middleware or route handler
    """
    try:
        # Check if this is a health check or a path that should be excluded
        if request.url.path.startswith("/health") or request.url.path.startswith(
            "/api/docs"
        ):
            return await call_next(request)

        # Use the same middleware implementation with default settings
        middleware = RateLimitMiddleware(app=None)

        # Call the dispatch method directly
        return await middleware.dispatch(request, call_next)
    except Exception as e:
        logger.error(f"Error in standalone rate limit middleware: {str(e)}")
        # Continue with the request even if rate limiting fails
        return await call_next(request)
