"""
Rate limiting middleware for the Ultra backend.

This middleware applies rate limits based on user subscription tier or IP address.
"""

from typing import Callable, List, Optional

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.config import Config
from app.services.rate_limit_service import rate_limit_service
from app.utils.logging import get_logger

# Set up logger
logger = get_logger("rate_limit_middleware")


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware for rate limiting API requests"""

    def __init__(
        self,
        app: ASGIApp,
        excluded_paths: Optional[List[str]] = None,
    ):
        """
        Initialize rate limit middleware

        Args:
            app: ASGI application
            excluded_paths: Paths to exclude from rate limiting
        """
        super().__init__(app)
        self.excluded_paths = excluded_paths or [
            "/health",
            "/api/health",
            "/metrics",
            "/api/metrics",
            "/api/docs",
            "/api/redoc",
            "/api/openapi.json",
            "/favicon.ico",
        ]
        logger.info(
            f"Initialized RateLimitMiddleware with {len(self.excluded_paths)} excluded paths"
        )

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process the request and apply rate limiting

        Args:
            request: FastAPI request object
            call_next: Next middleware/route handler

        Returns:
            Response
        """
        # Skip rate limiting if disabled
        if not Config.ENABLE_RATE_LIMIT:
            return await call_next(request)

        # Skip rate limiting for excluded paths
        if any(request.url.path.startswith(path) for path in self.excluded_paths):
            return await call_next(request)

        # Skip rate limiting for test requests
        if request.headers.get("X-Test-Mode") == "true":
            return await call_next(request)

        # Get user from request state (set by auth middleware)
        user = getattr(request.state, "user", None)

        # Check rate limit
        result = rate_limit_service.check_rate_limit(request, user)

        # If rate limited, return 429 response
        if not result.is_allowed:
            logger.warning(
                f"Rate limit exceeded for {rate_limit_service.get_client_identifier(request, user)}"
            )
            
            response = JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "status": "error",
                    "message": "Rate limit exceeded",
                    "code": "rate_limit_exceeded",
                    "retry_after": result.retry_after,
                },
            )
            
            # Add rate limit headers
            response.headers["X-RateLimit-Limit"] = str(result.limit)
            response.headers["X-RateLimit-Remaining"] = str(result.remaining)
            response.headers["X-RateLimit-Reset"] = str(result.reset_at)
            if result.retry_after:
                response.headers["Retry-After"] = str(result.retry_after)
            
            return response

        # Process the request
        response = await call_next(request)

        # Add rate limit headers to successful responses
        response.headers["X-RateLimit-Limit"] = str(result.limit)
        response.headers["X-RateLimit-Remaining"] = str(result.remaining)
        response.headers["X-RateLimit-Reset"] = str(result.reset_at)

        return response


def setup_rate_limit_middleware(
    app: ASGIApp,
    excluded_paths: Optional[List[str]] = None,
) -> None:
    """
    Set up rate limiting middleware for the FastAPI application

    Args:
        app: FastAPI application
        excluded_paths: Paths to exclude from rate limiting
    """
    app.add_middleware(
        RateLimitMiddleware,
        excluded_paths=excluded_paths,
    )
    logger.info("Rate limiting middleware added to application")