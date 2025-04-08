import json
import logging
import traceback
from typing import Any, Dict, List, Optional

import sentry_sdk
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from starlette.exceptions import HTTPException as StarletteHTTPException

# Configure logging
logger = logging.getLogger("ultra_error_handler")


# Define standard error response models
class ErrorDetail(BaseModel):
    type: str
    msg: str
    loc: Optional[List[str]] = None
    code: Optional[str] = None
    ctx: Optional[Dict[str, Any]] = None


class ErrorResponse(BaseModel):
    status: str = "error"
    message: str
    code: str
    details: Optional[List[ErrorDetail]] = None
    request_id: Optional[str] = None


# Custom exceptions
class UltraBaseException(Exception):
    """Base exception for all Ultra API exceptions"""

    def __init__(
        self,
        message: str,
        code: str = "internal_error",
        status_code: int = 500,
        details: list = None,
    ):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details
        super().__init__(self.message)


class ValidationError(UltraBaseException):
    """Exception for validation errors"""

    def __init__(self, message: str, details: list = None):
        super().__init__(message, "validation_error", 422, details)


class ResourceNotFoundError(UltraBaseException):
    """Exception for 404 not found errors"""

    def __init__(self, resource_type: str, resource_id: str):
        message = f"{resource_type} with ID {resource_id} not found"
        super().__init__(message, "not_found", 404)


class ApiResponseError(UltraBaseException):
    """Exception for errors in API responses"""

    def __init__(self, message: str, response_status: int = None, details: list = None):
        super().__init__(message, "api_response_error", 500, details)
        self.response_status = response_status


class ServiceUnavailableError(UltraBaseException):
    """Exception for service unavailable errors"""

    def __init__(self, service: str, message: str = None):
        message = message or f"Service {service} is currently unavailable"
        super().__init__(message, "service_unavailable", 503)


class RateLimitExceededError(UltraBaseException):
    """Exception for rate limit exceeded errors"""

    def __init__(self, message: str = "Rate limit exceeded. Please try again later."):
        super().__init__(message, "rate_limit_exceeded", 429)


class AuthenticationError(UltraBaseException):
    """Exception for authentication errors"""

    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, "authentication_error", 401)


class AuthorizationError(UltraBaseException):
    """Exception for authorization errors"""

    def __init__(
        self, message: str = "You do not have permission to perform this action"
    ):
        super().__init__(message, "authorization_error", 403)


# Exception handler for FastAPI
def register_exception_handlers(app: FastAPI):
    """Register all exception handlers with the FastAPI app."""

    @app.exception_handler(UltraBaseException)
    async def handle_ultra_exception(request: Request, exc: UltraBaseException):
        """Handle custom Ultra exceptions"""
        # Log the error
        logger.error(f"Ultra API error: {exc.code} - {exc.message}")

        # Capture in Sentry if it's a server error (5xx)
        if exc.status_code >= 500:
            sentry_sdk.capture_exception(exc)

        # Create standardized error response
        error_response = ErrorResponse(
            status="error",
            message=exc.message,
            code=exc.code,
            details=exc.details,
            request_id=(
                request.state.request_id
                if hasattr(request.state, "request_id")
                else None
            ),
        )

        return JSONResponse(
            status_code=exc.status_code, content=error_response.dict(exclude_none=True)
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ):
        """Handle FastAPI validation errors"""
        # Log the error
        error_details = str(exc.errors())
        logger.error(f"Validation error: {error_details}")

        # Format validation errors
        details = []
        for error in exc.errors():
            details.append(
                ErrorDetail(
                    type=error.get("type", "validation_error"),
                    msg=error.get("msg", "Validation error"),
                    loc=error.get("loc", []),
                    ctx=error.get("ctx"),
                )
            )

        # Create standardized error response
        error_response = ErrorResponse(
            status="error",
            message="Validation error",
            code="validation_error",
            details=details,
            request_id=(
                request.state.request_id
                if hasattr(request.state, "request_id")
                else None
            ),
        )

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_response.dict(exclude_none=True),
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        """Handle Starlette HTTP exceptions"""
        # Log the error
        logger.error(f"HTTP error {exc.status_code}: {exc.detail}")

        # Create standardized error response
        error_response = ErrorResponse(
            status="error",
            message=exc.detail,
            code=f"http_{exc.status_code}",
            request_id=(
                request.state.request_id
                if hasattr(request.state, "request_id")
                else None
            ),
        )

        return JSONResponse(
            status_code=exc.status_code, content=error_response.dict(exclude_none=True)
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle all other exceptions"""
        # Get the traceback
        tb = traceback.format_exc()

        # Log the error with traceback
        logger.error(f"Unhandled exception: {str(exc)}\n{tb}")

        # Capture in Sentry
        sentry_sdk.capture_exception(exc)

        # Create standardized error response (with limited info for security)
        error_response = ErrorResponse(
            status="error",
            message="An unexpected error occurred",
            code="internal_server_error",
            request_id=(
                request.state.request_id
                if hasattr(request.state, "request_id")
                else None
            ),
        )

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response.dict(exclude_none=True),
        )


# Middleware to add request ID and handle errors consistently
async def error_handling_middleware(request: Request, call_next):
    """Middleware to add request_id to every request and handle errors consistently."""
    import uuid

    # Generate a unique request ID
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id

    try:
        # Process the request
        response = await call_next(request)
        return response

    except Exception as exc:
        # This handles any errors not caught by the exception handlers
        logger.error(f"Unhandled error in middleware: {str(exc)}")
        sentry_sdk.capture_exception(exc)

        # Create standardized error response
        error_response = ErrorResponse(
            status="error",
            message="An unexpected error occurred",
            code="internal_server_error",
            request_id=request_id,
        )

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response.dict(exclude_none=True),
        )
