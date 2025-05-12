"""
Global error handling for the Ultra backend.

This module provides comprehensive error handling capabilities with
consistent error responses, detailed logging, and error classification.
"""

import os
import sys
import traceback
from http import HTTPStatus
from typing import Any, Dict, List, Optional, Type, Union

import sentry_sdk
from fastapi import FastAPI, Request, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from backend.models.base_models import ErrorDetail, ErrorResponse
from backend.utils.logging import get_logger

# Configure logger
logger = get_logger("error_handler", "logs/error.log")


class ErrorCode:
    """Error code constants"""

    # General errors
    INTERNAL_ERROR = "internal_error"
    NOT_FOUND = "not_found"
    VALIDATION_ERROR = "validation_error"

    # Authentication errors
    UNAUTHORIZED = "unauthorized"
    FORBIDDEN = "forbidden"
    INVALID_TOKEN = "invalid_token"
    EXPIRED_TOKEN = "expired_token"

    # Input errors
    INVALID_INPUT = "invalid_input"
    MISSING_FIELD = "missing_field"
    INVALID_FORMAT = "invalid_format"

    # Resource errors
    RESOURCE_EXISTS = "resource_exists"
    RESOURCE_NOT_FOUND = "resource_not_found"
    RESOURCE_CONFLICT = "resource_conflict"

    # Rate limiting errors
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"

    # Service errors
    SERVICE_UNAVAILABLE = "service_unavailable"
    EXTERNAL_SERVICE_ERROR = "external_service_error"
    TIMEOUT = "timeout"

    # Business logic errors
    BUSINESS_LOGIC_ERROR = "business_logic_error"
    PERMISSION_DENIED = "permission_denied"


class ErrorCategory:
    """Error category constants"""

    SYSTEM = "system"          # System-level errors
    AUTHENTICATION = "auth"     # Authentication/authorization errors
    VALIDATION = "validation"   # Input validation errors
    RESOURCE = "resource"       # Resource-related errors
    RATE_LIMIT = "rate_limit"   # Rate limiting errors
    SERVICE = "service"         # Service-related errors
    BUSINESS = "business"       # Business logic errors


class ErrorClassification:
    """Classification of errors by code, HTTP status, and category"""

    # Map error codes to HTTP status codes and categories
    ERROR_MAP = {
        # General errors
        ErrorCode.INTERNAL_ERROR: (status.HTTP_500_INTERNAL_SERVER_ERROR, ErrorCategory.SYSTEM),
        ErrorCode.NOT_FOUND: (status.HTTP_404_NOT_FOUND, ErrorCategory.RESOURCE),
        ErrorCode.VALIDATION_ERROR: (status.HTTP_422_UNPROCESSABLE_ENTITY, ErrorCategory.VALIDATION),

        # Authentication errors
        ErrorCode.UNAUTHORIZED: (status.HTTP_401_UNAUTHORIZED, ErrorCategory.AUTHENTICATION),
        ErrorCode.FORBIDDEN: (status.HTTP_403_FORBIDDEN, ErrorCategory.AUTHENTICATION),
        ErrorCode.INVALID_TOKEN: (status.HTTP_401_UNAUTHORIZED, ErrorCategory.AUTHENTICATION),
        ErrorCode.EXPIRED_TOKEN: (status.HTTP_401_UNAUTHORIZED, ErrorCategory.AUTHENTICATION),

        # Input errors
        ErrorCode.INVALID_INPUT: (status.HTTP_400_BAD_REQUEST, ErrorCategory.VALIDATION),
        ErrorCode.MISSING_FIELD: (status.HTTP_400_BAD_REQUEST, ErrorCategory.VALIDATION),
        ErrorCode.INVALID_FORMAT: (status.HTTP_400_BAD_REQUEST, ErrorCategory.VALIDATION),

        # Resource errors
        ErrorCode.RESOURCE_EXISTS: (status.HTTP_409_CONFLICT, ErrorCategory.RESOURCE),
        ErrorCode.RESOURCE_NOT_FOUND: (status.HTTP_404_NOT_FOUND, ErrorCategory.RESOURCE),
        ErrorCode.RESOURCE_CONFLICT: (status.HTTP_409_CONFLICT, ErrorCategory.RESOURCE),

        # Rate limiting errors
        ErrorCode.RATE_LIMIT_EXCEEDED: (status.HTTP_429_TOO_MANY_REQUESTS, ErrorCategory.RATE_LIMIT),

        # Service errors
        ErrorCode.SERVICE_UNAVAILABLE: (status.HTTP_503_SERVICE_UNAVAILABLE, ErrorCategory.SERVICE),
        ErrorCode.EXTERNAL_SERVICE_ERROR: (status.HTTP_502_BAD_GATEWAY, ErrorCategory.SERVICE),
        ErrorCode.TIMEOUT: (status.HTTP_504_GATEWAY_TIMEOUT, ErrorCategory.SERVICE),

        # Business logic errors
        ErrorCode.BUSINESS_LOGIC_ERROR: (status.HTTP_422_UNPROCESSABLE_ENTITY, ErrorCategory.BUSINESS),
        ErrorCode.PERMISSION_DENIED: (status.HTTP_403_FORBIDDEN, ErrorCategory.BUSINESS),
    }

    @classmethod
    def get_status_code(cls, error_code: str) -> int:
        """Get HTTP status code for an error code"""
        return cls.ERROR_MAP.get(error_code, (status.HTTP_500_INTERNAL_SERVER_ERROR, None))[0]

    @classmethod
    def get_category(cls, error_code: str) -> str:
        """Get category for an error code"""
        return cls.ERROR_MAP.get(error_code, (None, ErrorCategory.SYSTEM))[1]

    @classmethod
    def get_error_code(cls, exception: Exception) -> str:
        """Get error code for an exception"""
        # Handle known exception types
        if isinstance(exception, RequestValidationError):
            return ErrorCode.VALIDATION_ERROR

        # Default to internal error
        return ErrorCode.INTERNAL_ERROR


class UltraBaseException(Exception):
    """Base class for all Ultra exceptions"""

    def __init__(
        self,
        message: str,
        code: str = ErrorCode.INTERNAL_ERROR,
        status_code: Optional[int] = None,
        details: Optional[Any] = None,
    ):
        self.message = message
        self.code = code
        self.status_code = status_code or ErrorClassification.get_status_code(code)
        self.details = details
        super().__init__(message)


class ValidationException(UltraBaseException):
    """Exception for validation errors"""

    def __init__(
        self,
        message: str = "Validation error",
        code: str = ErrorCode.VALIDATION_ERROR,
        field_errors: Optional[Dict[str, str]] = None,
        details: Optional[Any] = None,
    ):
        # Convert field errors to details if provided
        if field_errors:
            error_details = []
            for field, msg in field_errors.items():
                error_details.append(
                    ErrorDetail(
                        type=ErrorCode.INVALID_INPUT,
                        msg=msg,
                        loc=[field],
                    )
                )
            details = {"field_errors": error_details}

        super().__init__(
            message=message,
            code=code,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details,
        )


class ResourceNotFoundException(UltraBaseException):
    """Exception for resource not found errors"""

    def __init__(
        self,
        resource_type: str,
        resource_id: str,
        message: Optional[str] = None,
    ):
        message = message or f"{resource_type} with ID {resource_id} not found"
        details = {
            "resource_type": resource_type,
            "resource_id": resource_id,
        }

        super().__init__(
            message=message,
            code=ErrorCode.RESOURCE_NOT_FOUND,
            status_code=status.HTTP_404_NOT_FOUND,
            details=details,
        )


class AuthenticationException(UltraBaseException):
    """Exception for authentication errors"""

    def __init__(
        self,
        message: str = "Authentication failed",
        code: str = ErrorCode.UNAUTHORIZED,
    ):
        super().__init__(
            message=message,
            code=code,
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


class BusinessLogicException(UltraBaseException):
    """Exception for business logic errors"""

    def __init__(
        self,
        message: str,
        code: str = ErrorCode.BUSINESS_LOGIC_ERROR,
        details: Optional[Any] = None,
    ):
        super().__init__(
            message=message,
            code=code,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details,
        )


class ServiceException(UltraBaseException):
    """Exception for service-related errors"""

    def __init__(
        self,
        message: str,
        service_name: str,
        code: str = ErrorCode.SERVICE_UNAVAILABLE,
        details: Optional[Any] = None,
    ):
        if details is None:
            details = {}

        details["service_name"] = service_name

        super().__init__(
            message=message,
            code=code,
            details=details,
        )


def create_error_response(
    error_code: str,
    message: str,
    details: Optional[Any] = None,
    request_id: Optional[str] = None,
) -> ErrorResponse:
    """
    Create a standardized error response

    Args:
        error_code: Error code
        message: Error message
        details: Additional error details
        request_id: Request ID for tracking

    Returns:
        ErrorResponse object
    """
    return ErrorResponse(
        status="error",
        message=message,
        code=error_code,
        details=details,
        request_id=request_id,
    )


def format_exception(
    exception: Exception,
    include_traceback: bool = False,
) -> Dict[str, Any]:
    """
    Format an exception into a standardized dictionary

    Args:
        exception: Exception to format
        include_traceback: Whether to include traceback

    Returns:
        Formatted exception as a dictionary
    """
    result = {
        "type": type(exception).__name__,
        "message": str(exception),
    }

    # Add traceback if requested
    if include_traceback:
        result["traceback"] = traceback.format_exception(
            type(exception),
            exception,
            exception.__traceback__,
        )

    # Add extra details for Ultra exceptions
    if isinstance(exception, UltraBaseException):
        result["code"] = exception.code
        result["status_code"] = exception.status_code

        if exception.details:
            result["details"] = exception.details

    return result


def log_exception(
    request: Request,
    exception: Exception,
    level: str = "error",
) -> None:
    """
    Log an exception with standardized format

    Args:
        request: FastAPI request
        exception: Exception to log
        level: Log level
    """
    # Format the exception
    formatted_exception = format_exception(
        exception,
        include_traceback=True,  # Always include traceback in logs
    )

    # Add request information
    log_data = {
        "exception": formatted_exception,
        "request": {
            "method": request.method,
            "url": str(request.url),
            "client_host": getattr(request.client, "host", "unknown"),
            "headers": dict(request.headers),
        },
    }

    # Get log function based on level
    log_func = getattr(logger, level, logger.error)

    # Log the error
    log_func(
        f"Exception occurred: {type(exception).__name__}: {str(exception)}",
        extra=log_data,
    )


async def error_handling_middleware(request: Request, call_next: Any) -> Response:
    """
    Middleware for handling exceptions in request processing

    Args:
        request: FastAPI request
        call_next: Next middleware or route handler

    Returns:
        Response object
    """
    try:
        # Process the request
        return await call_next(request)
    except UltraBaseException as e:
        # Log Ultra exceptions
        log_exception(request, e, level="warning")

        # Create error response
        error_response = create_error_response(
            error_code=e.code,
            message=e.message,
            details=e.details,
            request_id=getattr(request.state, "request_id", None),
        )

        # Return JSON response
        return JSONResponse(
            content=error_response.dict(exclude_none=True),
            status_code=e.status_code,
        )
    except Exception as e:
        # Log unexpected exceptions
        log_exception(request, e, level="error")

        # Get error code
        error_code = ErrorClassification.get_error_code(e)
        status_code = ErrorClassification.get_status_code(error_code)

        # Don't expose internal error details in production
        is_production = os.environ.get("ENVIRONMENT", "development") == "production"
        details = None if is_production else format_exception(e)

        # Create error response
        error_response = create_error_response(
            error_code=error_code,
            message="An unexpected error occurred",
            details=details,
            request_id=getattr(request.state, "request_id", None),
        )

        # Return JSON response
        return JSONResponse(
            content=error_response.dict(exclude_none=True),
            status_code=status_code,
        )


def register_exception_handlers(app: FastAPI) -> None:
    """
    Register exception handlers for a FastAPI application

    Args:
        app: FastAPI application
    """
    # Handle validation errors
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """Handle FastAPI validation errors"""
        # Log the error
        log_exception(request, exc, level="warning")

        # Format validation errors
        error_details = []
        for error in exc.errors():
            # Extract location
            location = error.get("loc", [])
            field = ".".join(str(part) for part in location if not isinstance(part, int))

            # Skip body parameter itself (usually means the whole body is invalid)
            if field == "body":
                field = ""

            # Create error detail
            error_detail = ErrorDetail(
                type=error.get("type", "validation_error"),
                msg=error.get("msg", "Invalid value"),
                loc=[str(loc) for loc in location],
                ctx=error.get("ctx"),
            )

            error_details.append(error_detail)

        # Create error response
        error_response = create_error_response(
            error_code=ErrorCode.VALIDATION_ERROR,
            message="Validation error",
            details=error_details,
            request_id=getattr(request.state, "request_id", None),
        )

        # Return JSON response
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_response.dict(exclude_none=True),
        )

    # Handle Ultra base exceptions
    @app.exception_handler(UltraBaseException)
    async def ultra_exception_handler(
        request: Request, exc: UltraBaseException
    ) -> JSONResponse:
        """Handle Ultra base exceptions"""
        # Log the error
        log_exception(request, exc, level="warning")

        # Create error response
        error_response = create_error_response(
            error_code=exc.code,
            message=exc.message,
            details=exc.details,
            request_id=getattr(request.state, "request_id", None),
        )

        # Return JSON response
        return JSONResponse(
            status_code=exc.status_code,
            content=error_response.dict(exclude_none=True),
        )

    logger.info("Exception handlers registered successfully")
