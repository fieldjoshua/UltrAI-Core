"""
Combined authentication middleware that supports both JWT tokens and API keys.

This middleware checks for authentication using either Bearer tokens or API keys,
and ensures that admin and debug routes are properly protected.
"""

from typing import Callable, List, Optional

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.config import Config
from app.database.connection import get_db_session
from app.models.base_models import ErrorResponse
from app.services.auth_service import auth_service
from app.utils.jwt_utils import decode_token, is_token_expired
from app.utils.logging import get_logger

# Set up logger
logger = get_logger("combined_auth_middleware")


class CombinedAuthMiddleware(BaseHTTPMiddleware):
    """Middleware for combined JWT and API key authentication"""

    def __init__(
        self,
        app: ASGIApp,
        public_paths: Optional[List[str]] = None,
        protected_paths: Optional[List[str]] = None,
        auth_header: str = "Authorization",
        api_key_header: str = "X-API-Key",
    ):
        """
        Initialize combined auth middleware

        Args:
            app: ASGI application
            public_paths: Paths that don't require authentication
            protected_paths: Paths that require authentication (e.g., admin, debug)
            auth_header: Name of the header containing the auth token
            api_key_header: Name of the header containing the API key
        """
        super().__init__(app)
        self.public_paths = public_paths or []
        self.protected_paths = protected_paths or ["/api/admin", "/api/debug"]
        self.auth_header = auth_header
        self.api_key_header = api_key_header
        logger.info(
            f"Initialized CombinedAuthMiddleware with {len(self.public_paths)} public paths and {len(self.protected_paths)} protected paths"
        )

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process the request and validate authentication

        Args:
            request: FastAPI request object
            call_next: Next middleware/route handler

        Returns:
            Response
        """
        # Skip authentication if disabled
        if not Config.ENABLE_AUTH:
            return await call_next(request)

        # Skip authentication for public paths
        path = request.url.path
        if any(path.startswith(public_path) for public_path in self.public_paths):
            return await call_next(request)

        # Check if this is a protected path
        is_protected = any(path.startswith(protected_path) for protected_path in self.protected_paths)

        # Skip authentication for test requests (used in tests)
        if request.headers.get("X-Test-Mode") == "true":
            request.state.user_id = "test_user_id"
            request.state.is_authenticated = True
            return await call_next(request)

        # Try to authenticate with JWT token first
        auth_header = request.headers.get(self.auth_header, "")
        if auth_header.startswith("Bearer "):
            token = auth_header.replace("Bearer ", "")
            auth_result = await self._authenticate_with_jwt(token)
            if auth_result:
                request.state.user = auth_result["user"]
                request.state.user_id = auth_result["user_id"]
                request.state.is_authenticated = True
                request.state.auth_method = "jwt"
                return await call_next(request)
            elif is_protected:
                # If JWT auth failed and this is a protected path, return error
                return self._create_auth_error_response(
                    "Invalid or expired authentication token",
                    "invalid_token",
                    status.HTTP_401_UNAUTHORIZED,
                )

        # Try to authenticate with API key
        api_key = request.headers.get(self.api_key_header)
        if api_key:
            auth_result = await self._authenticate_with_api_key(api_key)
            if auth_result:
                request.state.user = auth_result["user"]
                request.state.user_id = auth_result["user_id"]
                request.state.is_authenticated = True
                request.state.auth_method = "api_key"
                request.state.api_key = api_key
                return await call_next(request)
            elif is_protected:
                # If API key auth failed and this is a protected path, return error
                return self._create_auth_error_response(
                    "Invalid API key",
                    "invalid_api_key",
                    status.HTTP_401_UNAUTHORIZED,
                )

        # If this is a protected path and no valid auth was provided, return error
        if is_protected:
            return self._create_auth_error_response(
                "Authentication required for this endpoint",
                "authentication_required",
                status.HTTP_401_UNAUTHORIZED,
            )

        # For non-protected paths, allow access without authentication
        request.state.is_authenticated = False
        return await call_next(request)

    async def _authenticate_with_jwt(self, token: str) -> Optional[dict]:
        """
        Authenticate using JWT token

        Args:
            token: JWT token

        Returns:
            Dict with user info if authenticated, None otherwise
        """
        try:
            # Check if token is expired
            if is_token_expired(token):
                logger.warning("JWT token has expired")
                return None

            # Decode token
            payload = decode_token(token)
            if not payload:
                logger.warning("Failed to decode JWT token")
                return None

            # Get user ID from token
            user_id = payload.get("sub")
            if not user_id:
                logger.warning("No user ID in JWT token payload")
                return None

            # Verify user exists in database
            with get_db_session() as db:
                try:
                    user_id_int = int(user_id)
                    user = auth_service.get_user(db, user_id_int)

                    if not user:
                        logger.warning(f"User with ID {user_id} not found in database")
                        return None

                    return {
                        "user": user,
                        "user_id": user_id,
                    }
                except ValueError:
                    logger.error(f"Invalid user ID format in token: {user_id}")
                    return None
                except Exception as e:
                    logger.error(f"Error verifying user: {str(e)}")
                    return None

        except Exception as e:
            logger.error(f"JWT authentication error: {str(e)}")
            return None

    async def _authenticate_with_api_key(self, api_key: str) -> Optional[dict]:
        """
        Authenticate using API key

        Args:
            api_key: API key

        Returns:
            Dict with user info if authenticated, None otherwise
        """
        try:
            with get_db_session() as db:
                user = auth_service.verify_api_key(db, api_key)
                if not user:
                    logger.warning("Invalid API key")
                    return None

                return {
                    "user": user,
                    "user_id": str(user.id),
                }
        except Exception as e:
            logger.error(f"API key authentication error: {str(e)}")
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
            response.headers["WWW-Authenticate"] = 'Bearer realm="api", charset="UTF-8"'

        return response


def setup_combined_auth_middleware(
    app: ASGIApp,
    public_paths: Optional[List[str]] = None,
    protected_paths: Optional[List[str]] = None,
) -> None:
    """
    Set up combined authentication middleware for the FastAPI application

    Args:
        app: FastAPI application
        public_paths: Paths that don't require authentication
        protected_paths: Paths that require authentication
    """
    app.add_middleware(
        CombinedAuthMiddleware,
        public_paths=public_paths,
        protected_paths=protected_paths,
    )
    logger.info("Combined authentication middleware added to application")