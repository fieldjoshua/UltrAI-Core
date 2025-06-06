"""
API key authentication middleware for the Ultra backend.

This module provides a FastAPI middleware that authenticates requests using API keys
and enforces access control based on key scope, permissions, and rate limits.
"""

from typing import Callable, Dict, List, Optional, Set

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from backend.models.base_models import ErrorResponse
from backend.utils.api_key_manager import ApiKeyScope, api_key_manager
from backend.utils.logging import get_logger, log_audit

# Set up logger
logger = get_logger("api_key_middleware", "logs/security.log")


class ApiKeyMiddleware(BaseHTTPMiddleware):
    """Middleware for API key authentication"""

    def __init__(
        self,
        app: ASGIApp,
        api_key_header: str = "X-API-Key",
        public_paths: Optional[List[str]] = None,
        scopes_required: Optional[Dict[str, ApiKeyScope]] = None,
        write_methods: Optional[Set[str]] = None,
        admin_paths: Optional[List[str]] = None,
    ):
        """
        Initialize API key middleware

        Args:
            app: ASGI application
            api_key_header: Name of the header containing the API key
            public_paths: Paths that don't require API key authentication
            scopes_required: Mapping of path prefixes to required scopes
            write_methods: HTTP methods that require write scope
            admin_paths: Paths that require admin scope
        """
        super().__init__(app)
        self.api_key_header = api_key_header
        self.public_paths = public_paths or [
            "/api/auth/",
            "/health",
            "/metrics",
            "/api/docs",
            "/api/redoc",
            "/api/openapi.json",
            "/favicon.ico",
        ]
        self.scopes_required = scopes_required or {
            "/api/admin/": ApiKeyScope.ADMIN,
            "/api/v1/write/": ApiKeyScope.READ_WRITE,
        }
        self.write_methods = write_methods or {"POST", "PUT", "PATCH", "DELETE"}
        self.admin_paths = admin_paths or ["/api/admin/"]
        logger.info(
            f"Initialized ApiKeyMiddleware with {len(self.public_paths)} public paths"
        )

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process the request and authenticate with API key

        Args:
            request: FastAPI request object
            call_next: Next middleware/route handler

        Returns:
            Response
        """
        # Skip API key authentication for public paths
        if any(request.url.path.startswith(path) for path in self.public_paths):
            return await call_next(request)

        # Skip API key authentication for test requests (used in production tests)
        if request.headers.get("X-Test-Mode") == "true":
            # Add dummy API key info to request state for downstream handlers
            request.state.api_key = "test-api-key"
            request.state.user_id = "test-user-id"
            return await call_next(request)

        # Get API key from header
        api_key = request.headers.get(self.api_key_header)
        if not api_key:
            # If authentication is required but no API key is provided, return error
            return self._create_api_key_error_response(
                "API key is required",
                "missing_api_key",
                status.HTTP_401_UNAUTHORIZED,
            )

        # Validate API key
        api_key_obj = api_key_manager.validate_api_key(
            api_key=api_key,
            path=request.url.path,
            ip_address=request.client.host if request.client else None,
        )

        if not api_key_obj:
            return self._create_api_key_error_response(
                "Invalid API key",
                "invalid_api_key",
                status.HTTP_401_UNAUTHORIZED,
            )

        # Check if the key is expired (redundant, but for clarity)
        if api_key_obj.is_expired():
            return self._create_api_key_error_response(
                "API key has expired",
                "expired_api_key",
                status.HTTP_401_UNAUTHORIZED,
            )

        # Check if the key has sufficient scope for the path
        required_scope = self._get_required_scope(request.url.path, request.method)
        if (
            required_scope == ApiKeyScope.ADMIN
            and api_key_obj.scope != ApiKeyScope.ADMIN
        ):
            # For admin paths, require admin scope
            return self._create_api_key_error_response(
                "API key does not have admin privileges",
                "insufficient_privileges",
                status.HTTP_403_FORBIDDEN,
            )
        elif (
            required_scope == ApiKeyScope.READ_WRITE
            and api_key_obj.scope == ApiKeyScope.READ_ONLY
        ):
            # For write operations, require read-write scope
            return self._create_api_key_error_response(
                "API key does not have write privileges",
                "insufficient_privileges",
                status.HTTP_403_FORBIDDEN,
            )

        # Store API key info in request state
        request.state.api_key = api_key_obj
        request.state.user_id = api_key_obj.user_id

        # Log API key usage
        log_audit(
            action="api_key_usage",
            user_id=api_key_obj.user_id,
            resource=f"path:{request.url.path}",
            details={
                "method": request.method,
                "key_id": api_key_obj.key_id,
                "scope": api_key_obj.scope,
            },
        )

        # Process the request
        return await call_next(request)

    def _get_required_scope(self, path: str, method: str) -> ApiKeyScope:
        """
        Determine the required scope for a path and method

        Args:
            path: Request path
            method: HTTP method

        Returns:
            Required API key scope
        """
        # Admin paths require admin scope
        if any(path.startswith(admin_path) for admin_path in self.admin_paths):
            return ApiKeyScope.ADMIN

        # Check path-specific scope requirements
        for path_prefix, scope in self.scopes_required.items():
            if path.startswith(path_prefix):
                return scope

        # Write methods require write scope
        if method in self.write_methods:
            return ApiKeyScope.READ_WRITE

        # Default to read-only
        return ApiKeyScope.READ_ONLY

    def _create_api_key_error_response(
        self, message: str, code: str, status_code: int
    ) -> JSONResponse:
        """
        Create API key error response

        Args:
            message: Error message
            code: Error code
            status_code: HTTP status code

        Returns:
            JSONResponse with error details
        """
        error_response = ErrorResponse(
            status="error",
            message=message,
            code=code,
        )

        return JSONResponse(
            status_code=status_code,
            content=error_response.dict(exclude_none=True),
        )


def setup_api_key_middleware(
    app: ASGIApp,
    api_key_header: str = "X-API-Key",
    public_paths: Optional[List[str]] = None,
    admin_paths: Optional[List[str]] = None,
) -> None:
    """
    Set up API key middleware for the FastAPI application

    Args:
        app: FastAPI application
        api_key_header: Name of the header containing the API key
        public_paths: Paths that don't require API key authentication
        admin_paths: Paths that require admin scope
    """
    app.add_middleware(
        ApiKeyMiddleware,
        api_key_header=api_key_header,
        public_paths=public_paths,
        admin_paths=admin_paths,
    )
    logger.info("API key middleware added to application")
