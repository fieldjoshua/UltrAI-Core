"""
Global Error Handling System for the UltraAI backend.

This module provides a comprehensive and unified error handling system with:
- Consistent error response formatting
- Detailed error logging with context
- Error classification and codes
- Automatic error recovery mechanisms
- Circuit breakers for external services
"""

import asyncio
import inspect
import json
import sys
import time
import traceback
from enum import Enum
from functools import wraps
from http import HTTPStatus
from typing import Any, Callable, Dict, List, Optional, Type, Union

import sentry_sdk
from fastapi import FastAPI, Request, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.models.base_models import ErrorDetail, ErrorResponse
from app.utils.logging import CorrelationContext, get_logger

# Configure logger
logger = get_logger("error_handler", "logs/error.log")


class ErrorCode:
    """Centralized error code constants for consistent error handling"""

    # General errors
    INTERNAL_ERROR = "internal_error"
    NOT_FOUND = "not_found"
    VALIDATION_ERROR = "validation_error"
    BAD_REQUEST = "bad_request"

    # Authentication errors
    UNAUTHORIZED = "unauthorized"
    FORBIDDEN = "forbidden"
    INVALID_AUTH = "invalid_auth"
    EXPIRED_AUTH = "expired_auth"
    AUTH_REVOKED = "auth_revoked"

    # Input errors
    INVALID_INPUT = "invalid_input"
    MISSING_FIELD = "missing_field"
    INVALID_FORMAT = "invalid_format"
    INVALID_TYPE = "invalid_type"
    VALUE_ERROR = "value_error"

    # Resource errors
    RESOURCE_EXISTS = "resource_exists"
    RESOURCE_NOT_FOUND = "resource_not_found"
    RESOURCE_CONFLICT = "resource_conflict"
    INSUFFICIENT_RESOURCES = "insufficient_resources"

    # Rate limiting errors
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    QUOTA_EXCEEDED = "quota_exceeded"

    # Service errors
    SERVICE_UNAVAILABLE = "service_unavailable"
    EXTERNAL_SERVICE_ERROR = "external_service_error"
    TIMEOUT = "timeout"
    CIRCUIT_OPEN = "circuit_open"
    DEPENDENCY_FAILURE = "dependency_failure"

    # Business logic errors
    BUSINESS_LOGIC_ERROR = "business_logic_error"
    PERMISSION_DENIED = "permission_denied"
    OPERATION_NOT_SUPPORTED = "operation_not_supported"
    INVALID_STATE = "invalid_state"
    PRECONDITION_FAILED = "precondition_failed"


class ErrorSeverity(str, Enum):
    """Error severity levels for proper handling and logging"""

    CRITICAL = "critical"  # System is unusable, immediate attention required
    ERROR = "error"  # Error that prevents operation from completing
    WARNING = "warning"  # Potentially harmful situation, operation can continue
    INFO = "info"  # Informational message about an error
    DEBUG = "debug"  # Debugging information about an error


class ErrorCategory(str, Enum):
    """Error categories for grouping similar errors"""

    SECURITY = "security"  # Security-related errors
    VALIDATION = "validation"  # Input validation errors
    AUTHORIZATION = "authorization"  # Authentication/authorization errors
    RESOURCE = "resource"  # Resource access/manipulation errors
    SERVICE = "service"  # Service availability/external service errors
    SYSTEM = "system"  # System/infrastructure errors
    BUSINESS = "business"  # Business logic errors
    RATE_LIMIT = "rate_limit"  # Rate limiting/quota errors
    CLIENT = "client"  # Client-side errors
    UNKNOWN = "unknown"  # Uncategorized errors


class ErrorClassification:
    """
    Error classification system for consistent error handling.

    Maps error types to appropriate error codes, HTTP status codes, and severity levels.
    """

    # Mapping of exception types to error codes
    ERROR_CODE_MAPPING = {
        ValidationError: ErrorCode.VALIDATION_ERROR,
        RequestValidationError: ErrorCode.VALIDATION_ERROR,
        ValueError: ErrorCode.INVALID_INPUT,
        TypeError: ErrorCode.INVALID_TYPE,
        KeyError: ErrorCode.MISSING_FIELD,
        IndexError: ErrorCode.INVALID_INPUT,
        LookupError: ErrorCode.RESOURCE_NOT_FOUND,
        TimeoutError: ErrorCode.TIMEOUT,
        ConnectionError: ErrorCode.EXTERNAL_SERVICE_ERROR,
        PermissionError: ErrorCode.PERMISSION_DENIED,
        FileNotFoundError: ErrorCode.RESOURCE_NOT_FOUND,
        NotImplementedError: ErrorCode.OPERATION_NOT_SUPPORTED,
        # Add more exception types as needed
    }

    # Mapping of error codes to HTTP status codes
    STATUS_CODE_MAPPING = {
        # General errors
        ErrorCode.INTERNAL_ERROR: status.HTTP_500_INTERNAL_SERVER_ERROR,
        ErrorCode.BAD_REQUEST: status.HTTP_400_BAD_REQUEST,
        ErrorCode.NOT_FOUND: status.HTTP_404_NOT_FOUND,
        ErrorCode.VALIDATION_ERROR: status.HTTP_422_UNPROCESSABLE_ENTITY,
        # Authentication errors
        ErrorCode.UNAUTHORIZED: status.HTTP_401_UNAUTHORIZED,
        ErrorCode.FORBIDDEN: status.HTTP_403_FORBIDDEN,
        ErrorCode.INVALID_AUTH: status.HTTP_401_UNAUTHORIZED,
        ErrorCode.EXPIRED_AUTH: status.HTTP_401_UNAUTHORIZED,
        ErrorCode.AUTH_REVOKED: status.HTTP_401_UNAUTHORIZED,
        # Input errors
        ErrorCode.INVALID_INPUT: status.HTTP_400_BAD_REQUEST,
        ErrorCode.MISSING_FIELD: status.HTTP_400_BAD_REQUEST,
        ErrorCode.INVALID_FORMAT: status.HTTP_400_BAD_REQUEST,
        ErrorCode.INVALID_TYPE: status.HTTP_400_BAD_REQUEST,
        ErrorCode.VALUE_ERROR: status.HTTP_400_BAD_REQUEST,
        # Resource errors
        ErrorCode.RESOURCE_EXISTS: status.HTTP_409_CONFLICT,
        ErrorCode.RESOURCE_NOT_FOUND: status.HTTP_404_NOT_FOUND,
        ErrorCode.RESOURCE_CONFLICT: status.HTTP_409_CONFLICT,
        ErrorCode.INSUFFICIENT_RESOURCES: status.HTTP_507_INSUFFICIENT_STORAGE,
        # Rate limiting errors
        ErrorCode.RATE_LIMIT_EXCEEDED: status.HTTP_429_TOO_MANY_REQUESTS,
        ErrorCode.QUOTA_EXCEEDED: status.HTTP_429_TOO_MANY_REQUESTS,
        # Service errors
        ErrorCode.SERVICE_UNAVAILABLE: status.HTTP_503_SERVICE_UNAVAILABLE,
        ErrorCode.EXTERNAL_SERVICE_ERROR: status.HTTP_502_BAD_GATEWAY,
        ErrorCode.TIMEOUT: status.HTTP_504_GATEWAY_TIMEOUT,
        ErrorCode.CIRCUIT_OPEN: status.HTTP_503_SERVICE_UNAVAILABLE,
        ErrorCode.DEPENDENCY_FAILURE: status.HTTP_502_BAD_GATEWAY,
        # Business logic errors
        ErrorCode.BUSINESS_LOGIC_ERROR: status.HTTP_422_UNPROCESSABLE_ENTITY,
        ErrorCode.PERMISSION_DENIED: status.HTTP_403_FORBIDDEN,
        ErrorCode.OPERATION_NOT_SUPPORTED: status.HTTP_405_METHOD_NOT_ALLOWED,
        ErrorCode.INVALID_STATE: status.HTTP_409_CONFLICT,
        ErrorCode.PRECONDITION_FAILED: status.HTTP_412_PRECONDITION_FAILED,
    }

    # Mapping of error codes to severity levels
    SEVERITY_MAPPING = {
        # General errors
        ErrorCode.INTERNAL_ERROR: ErrorSeverity.ERROR,
        ErrorCode.BAD_REQUEST: ErrorSeverity.WARNING,
        ErrorCode.NOT_FOUND: ErrorSeverity.WARNING,
        ErrorCode.VALIDATION_ERROR: ErrorSeverity.WARNING,
        # Authentication errors - usually warnings since they're client errors
        ErrorCode.UNAUTHORIZED: ErrorSeverity.WARNING,
        ErrorCode.FORBIDDEN: ErrorSeverity.WARNING,
        ErrorCode.INVALID_AUTH: ErrorSeverity.WARNING,
        ErrorCode.EXPIRED_AUTH: ErrorSeverity.INFO,
        ErrorCode.AUTH_REVOKED: ErrorSeverity.INFO,
        # Input errors
        ErrorCode.INVALID_INPUT: ErrorSeverity.WARNING,
        ErrorCode.MISSING_FIELD: ErrorSeverity.WARNING,
        ErrorCode.INVALID_FORMAT: ErrorSeverity.WARNING,
        ErrorCode.INVALID_TYPE: ErrorSeverity.WARNING,
        ErrorCode.VALUE_ERROR: ErrorSeverity.WARNING,
        # Resource errors
        ErrorCode.RESOURCE_EXISTS: ErrorSeverity.WARNING,
        ErrorCode.RESOURCE_NOT_FOUND: ErrorSeverity.WARNING,
        ErrorCode.RESOURCE_CONFLICT: ErrorSeverity.WARNING,
        ErrorCode.INSUFFICIENT_RESOURCES: ErrorSeverity.ERROR,
        # Rate limiting errors
        ErrorCode.RATE_LIMIT_EXCEEDED: ErrorSeverity.INFO,
        ErrorCode.QUOTA_EXCEEDED: ErrorSeverity.INFO,
        # Service errors - high severity since they affect functionality
        ErrorCode.SERVICE_UNAVAILABLE: ErrorSeverity.ERROR,
        ErrorCode.EXTERNAL_SERVICE_ERROR: ErrorSeverity.ERROR,
        ErrorCode.TIMEOUT: ErrorSeverity.ERROR,
        ErrorCode.CIRCUIT_OPEN: ErrorSeverity.WARNING,
        ErrorCode.DEPENDENCY_FAILURE: ErrorSeverity.ERROR,
        # Business logic errors
        ErrorCode.BUSINESS_LOGIC_ERROR: ErrorSeverity.WARNING,
        ErrorCode.PERMISSION_DENIED: ErrorSeverity.WARNING,
        ErrorCode.OPERATION_NOT_SUPPORTED: ErrorSeverity.WARNING,
        ErrorCode.INVALID_STATE: ErrorSeverity.WARNING,
        ErrorCode.PRECONDITION_FAILED: ErrorSeverity.WARNING,
    }

    # Mapping of error codes to categories
    CATEGORY_MAPPING = {
        # General errors
        ErrorCode.INTERNAL_ERROR: ErrorCategory.SYSTEM,
        ErrorCode.BAD_REQUEST: ErrorCategory.CLIENT,
        ErrorCode.NOT_FOUND: ErrorCategory.RESOURCE,
        ErrorCode.VALIDATION_ERROR: ErrorCategory.VALIDATION,
        # Authentication errors
        ErrorCode.UNAUTHORIZED: ErrorCategory.AUTHORIZATION,
        ErrorCode.FORBIDDEN: ErrorCategory.AUTHORIZATION,
        ErrorCode.INVALID_AUTH: ErrorCategory.SECURITY,
        ErrorCode.EXPIRED_AUTH: ErrorCategory.SECURITY,
        ErrorCode.AUTH_REVOKED: ErrorCategory.SECURITY,
        # Input errors
        ErrorCode.INVALID_INPUT: ErrorCategory.VALIDATION,
        ErrorCode.MISSING_FIELD: ErrorCategory.VALIDATION,
        ErrorCode.INVALID_FORMAT: ErrorCategory.VALIDATION,
        ErrorCode.INVALID_TYPE: ErrorCategory.VALIDATION,
        ErrorCode.VALUE_ERROR: ErrorCategory.VALIDATION,
        # Resource errors
        ErrorCode.RESOURCE_EXISTS: ErrorCategory.RESOURCE,
        ErrorCode.RESOURCE_NOT_FOUND: ErrorCategory.RESOURCE,
        ErrorCode.RESOURCE_CONFLICT: ErrorCategory.RESOURCE,
        ErrorCode.INSUFFICIENT_RESOURCES: ErrorCategory.SYSTEM,
        # Rate limiting errors
        ErrorCode.RATE_LIMIT_EXCEEDED: ErrorCategory.RATE_LIMIT,
        ErrorCode.QUOTA_EXCEEDED: ErrorCategory.RATE_LIMIT,
        # Service errors
        ErrorCode.SERVICE_UNAVAILABLE: ErrorCategory.SERVICE,
        ErrorCode.EXTERNAL_SERVICE_ERROR: ErrorCategory.SERVICE,
        ErrorCode.TIMEOUT: ErrorCategory.SERVICE,
        ErrorCode.CIRCUIT_OPEN: ErrorCategory.SERVICE,
        ErrorCode.DEPENDENCY_FAILURE: ErrorCategory.SERVICE,
        # Business logic errors
        ErrorCode.BUSINESS_LOGIC_ERROR: ErrorCategory.BUSINESS,
        ErrorCode.PERMISSION_DENIED: ErrorCategory.AUTHORIZATION,
        ErrorCode.OPERATION_NOT_SUPPORTED: ErrorCategory.BUSINESS,
        ErrorCode.INVALID_STATE: ErrorCategory.BUSINESS,
        ErrorCode.PRECONDITION_FAILED: ErrorCategory.BUSINESS,
    }

    @classmethod
    def get_error_code(cls, exception: Exception) -> str:
        """Get the appropriate error code for the given exception"""
        # Find the most specific exception type in the mapping
        for exc_type, code in cls.ERROR_CODE_MAPPING.items():
            if isinstance(exception, exc_type):
                return code

        # If it's an HTTP exception, use the status code
        if isinstance(exception, StarletteHTTPException):
            return f"http_{exception.status_code}"

        # If we don't have a specific mapping, use a generic error code
        return ErrorCode.INTERNAL_ERROR

    @classmethod
    def get_status_code(cls, error_code: str) -> int:
        """Get the appropriate HTTP status code for the given error code"""
        return cls.STATUS_CODE_MAPPING.get(
            error_code, status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    @classmethod
    def get_severity(cls, error_code: str) -> ErrorSeverity:
        """Get the severity level for the given error code"""
        return cls.SEVERITY_MAPPING.get(error_code, ErrorSeverity.ERROR)

    @classmethod
    def get_category(cls, error_code: str) -> ErrorCategory:
        """Get the error category for the given error code"""
        return cls.CATEGORY_MAPPING.get(error_code, ErrorCategory.UNKNOWN)


class UltraBaseException(Exception):
    """Base exception for all Ultra API exceptions"""

    def __init__(
        self,
        message: str,
        code: str = ErrorCode.INTERNAL_ERROR,
        status_code: Optional[int] = None,
        details: Optional[List[ErrorDetail]] = None,
    ):
        """
        Initialize the base exception

        Args:
            message: Human-readable error message
            code: Error code for programmatic handling
            status_code: HTTP status code to return
            details: Detailed error information
        """
        self.message = message
        self.code = code
        self.status_code = status_code or ErrorClassification.get_status_code(code)
        self.details = details
        super().__init__(message)


def create_error_response(
    error_code: str,
    message: str,
    details: Optional[Union[List[ErrorDetail], Dict[str, Any], str]] = None,
    request_id: Optional[str] = None,
) -> ErrorResponse:
    """
    Create a standardized error response

    Args:
        error_code: Error code for programmatic handling
        message: Human-readable error message
        details: Detailed error information
        request_id: Request ID for tracking

    Returns:
        Standardized error response
    """
    # If details is a string, convert it to an error detail
    if isinstance(details, str):
        details = [ErrorDetail(type=error_code, msg=details)]

    # If details is a dict, convert it to an error detail
    elif isinstance(details, dict):
        details = [ErrorDetail(type=error_code, msg=message, ctx=details)]

    # Create the error response
    return ErrorResponse(
        status="error",
        message=message,
        code=error_code,
        details=details,
        request_id=request_id or CorrelationContext.get_correlation_id(),
    )


def format_exception(exc: Exception) -> List[ErrorDetail]:
    """
    Format an exception into a list of error details

    Args:
        exc: Exception to format

    Returns:
        List of error details
    """
    # Get exception details
    exc_type = type(exc).__name__
    exc_msg = str(exc)
    exc_traceback = traceback.format_exc()

    # Create an error detail
    error_detail = ErrorDetail(
        type=exc_type,
        msg=exc_msg,
        ctx={"traceback": exc_traceback},
    )

    return [error_detail]


def log_exception(
    request: Request,
    exc: Exception,
    level: str = "error",
) -> None:
    """
    Log an exception with request context

    Args:
        request: FastAPI request
        exc: Exception to log
        level: Log level
    """
    # Get request details
    method = request.method
    url = str(request.url)
    client_host = getattr(request.client, "host", "unknown")
    request_id = getattr(request.state, "request_id", None)

    # Get exception details
    exc_type = type(exc).__name__
    exc_msg = str(exc)
    exc_traceback = traceback.format_exc()

    # Prepare log data
    log_data = {
        "method": method,
        "url": url,
        "client_host": client_host,
        "request_id": request_id,
        "exception_type": exc_type,
        "exception_message": exc_msg,
    }

    # Log at the appropriate level
    if level == "critical":
        logger.critical(f"Critical error processing request: {exc_msg}", extra=log_data)
    elif level == "error":
        logger.error(f"Error processing request: {exc_msg}", extra=log_data)
    elif level == "warning":
        logger.warning(f"Warning processing request: {exc_msg}", extra=log_data)
    elif level == "info":
        logger.info(f"Info about request error: {exc_msg}", extra=log_data)
    else:
        logger.debug(f"Debug info about request error: {exc_msg}", extra=log_data)

    # Log traceback at debug level
    logger.debug(f"Exception traceback: {exc_traceback}")


class CircuitBreaker:
    """
    Circuit breaker for protecting against failing external services.

    When a service fails repeatedly, the circuit breaker opens and
    fails fast, preventing cascading failures.
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        reset_timeout: int = 30,
        half_open_success_threshold: int = 2,
    ):
        """
        Initialize the circuit breaker

        Args:
            failure_threshold: Number of consecutive failures before opening the circuit
            reset_timeout: Time in seconds before trying to close the circuit again
            half_open_success_threshold: Number of successful requests needed to close the circuit
        """
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.half_open_success_threshold = half_open_success_threshold

        self.failure_count = 0
        self.last_failure_time = 0
        self.state = "closed"  # closed, open, half-open
        self.success_count = 0

    def register_failure(self) -> None:
        """Register a failure and potentially open the circuit"""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.state == "closed" and self.failure_count >= self.failure_threshold:
            self.state = "open"
            logger.warning(
                f"Circuit opened after {self.failure_count} consecutive failures"
            )

        elif self.state == "half-open":
            self.state = "open"
            self.failure_count = self.failure_threshold
            logger.warning("Circuit reopened after a failure in half-open state")

    def register_success(self) -> None:
        """Register a success and potentially close the circuit"""
        if self.state == "half-open":
            self.success_count += 1

            if self.success_count >= self.half_open_success_threshold:
                self.state = "closed"
                self.failure_count = 0
                self.success_count = 0
                logger.info(
                    "Circuit closed after successful requests in half-open state"
                )

        elif self.state == "closed":
            self.failure_count = 0

    def allow_request(self) -> bool:
        """Check if a request should be allowed to proceed"""
        # If circuit is closed, allow request
        if self.state == "closed":
            return True

        # If circuit is open, check if reset timeout has elapsed
        if self.state == "open":
            elapsed = time.time() - self.last_failure_time

            if elapsed >= self.reset_timeout:
                # Allow one request to go through
                self.state = "half-open"
                self.success_count = 0
                logger.info("Circuit half-opened, allowing trial request")
                return True

            return False

        # If circuit is half-open, allow request
        return self.state == "half-open"

    def __call__(self, func):
        """Decorator to apply circuit breaker to a function"""

        @wraps(func)
        async def wrapper(*args, **kwargs):
            if not self.allow_request():
                raise UltraBaseException(
                    message="Service temporarily unavailable due to recent failures",
                    code=ErrorCode.CIRCUIT_OPEN,
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                )

            try:
                result = await func(*args, **kwargs)
                self.register_success()
                return result

            except Exception as e:
                self.register_failure()
                raise e

        return wrapper


class GlobalErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Middleware for global error handling with consistent responses"""

    def __init__(
        self,
        app: ASGIApp,
        include_debug_details: bool = False,
        exclude_paths: List[str] = None,
    ):
        """
        Initialize the middleware

        Args:
            app: ASGI application
            include_debug_details: Whether to include debug details in error responses
            exclude_paths: Paths to exclude from detailed error reporting
        """
        super().__init__(app)
        self.include_debug_details = include_debug_details
        self.exclude_paths = exclude_paths or ["/health", "/metrics"]

        logger.info(
            f"Initialized GlobalErrorHandlingMiddleware with "
            f"debug_details={include_debug_details}, "
            f"exclude_paths={exclude_paths}"
        )

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process the request and handle any exceptions

        Args:
            request: FastAPI request
            call_next: Next middleware or route handler

        Returns:
            Response object
        """
        # Set correlation ID for request tracking
        correlation_id = request.headers.get("X-Correlation-ID", f"ultra-{time.time()}")
        CorrelationContext.set_correlation_id(correlation_id)

        # Add correlation ID to request state
        request.state.correlation_id = correlation_id

        try:
            # Process the request
            response = await call_next(request)

            # Add correlation ID to response headers
            response.headers["X-Correlation-ID"] = correlation_id

            return response

        except UltraBaseException as e:
            # Log structured exception
            severity = ErrorClassification.get_severity(e.code)
            log_exception(request, e, level=severity)

            # Create error response
            error_response = create_error_response(
                error_code=e.code,
                message=e.message,
                details=e.details,
                request_id=correlation_id,
            )

            # Create JSON response
            response = JSONResponse(
                status_code=e.status_code,
                content=error_response.dict(exclude_none=True),
            )

            # Add correlation ID to response headers
            response.headers["X-Correlation-ID"] = correlation_id

            return response

        except Exception as e:
            # Get error code and status code
            error_code = ErrorClassification.get_error_code(e)
            status_code = ErrorClassification.get_status_code(error_code)
            severity = ErrorClassification.get_severity(error_code)
            category = ErrorClassification.get_category(error_code)

            # Log structured exception
            log_exception(request, e, level=severity)

            # Only include detailed error information if allowed
            include_details = self.include_debug_details
            if request.url.path in self.exclude_paths:
                include_details = False

            # Prepare error details
            details = None
            if include_details:
                details = format_exception(e)

            # Create error response with appropriate message
            if status_code >= 500:
                message = "An unexpected server error occurred"
                # Capture in Sentry if it's a server error
                sentry_sdk.capture_exception(e)
            else:
                # For client errors, provide a more specific message if available
                message = (
                    str(e) if str(e) else "An error occurred processing your request"
                )

            # Create error response
            error_response = create_error_response(
                error_code=error_code,
                message=message,
                details=details,
                request_id=correlation_id,
            )

            # Create JSON response
            response = JSONResponse(
                status_code=status_code,
                content=error_response.dict(exclude_none=True),
            )

            # Add correlation ID to response headers
            response.headers["X-Correlation-ID"] = correlation_id

            return response


def setup_error_handling(
    app: FastAPI,
    include_debug_details: bool = False,
    exclude_paths: List[str] = None,
) -> None:
    """
    Set up the global error handling system for a FastAPI application

    Args:
        app: FastAPI application
        include_debug_details: Whether to include debug details in error responses
        exclude_paths: Paths to exclude from detailed error reporting
    """
    # Register exception handlers
    register_exception_handlers(app)

    # Add global error handling middleware
    app.add_middleware(
        GlobalErrorHandlingMiddleware,
        include_debug_details=include_debug_details,
        exclude_paths=exclude_paths,
    )

    logger.info("Global error handling system configured")


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
            field = ".".join(
                str(part) for part in location if not isinstance(part, int)
            )

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
            request_id=getattr(request.state, "correlation_id", None),
        )

        # Return JSON response
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_response.dict(exclude_none=True),
        )

    # Handle HTTP exceptions
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        """Handle HTTP exceptions"""
        # Log the error
        level = "error" if exc.status_code >= 500 else "warning"
        log_exception(request, exc, level=level)

        # Create error response
        error_response = create_error_response(
            error_code=f"http_{exc.status_code}",
            message=exc.detail,
            request_id=getattr(request.state, "correlation_id", None),
        )

        # Return JSON response
        return JSONResponse(
            status_code=exc.status_code,
            content=error_response.dict(exclude_none=True),
        )

    # Handle UltraBaseException
    @app.exception_handler(UltraBaseException)
    async def ultra_exception_handler(
        request: Request, exc: UltraBaseException
    ) -> JSONResponse:
        """Handle Ultra base exceptions"""
        # Log the error
        severity = ErrorClassification.get_severity(exc.code)
        log_exception(request, exc, level=severity)

        # Create error response
        error_response = create_error_response(
            error_code=exc.code,
            message=exc.message,
            details=exc.details,
            request_id=getattr(request.state, "correlation_id", None),
        )

        # Return JSON response
        return JSONResponse(
            status_code=exc.status_code,
            content=error_response.dict(exclude_none=True),
        )

    # Handle general exceptions
    @app.exception_handler(Exception)
    async def general_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        """Handle general exceptions"""
        # Get error code and status code
        error_code = ErrorClassification.get_error_code(exc)
        status_code = ErrorClassification.get_status_code(error_code)

        # Log the error
        level = "error" if status_code >= 500 else "warning"
        log_exception(request, exc, level=level)

        # Capture in Sentry if it's a server error
        if status_code >= 500:
            sentry_sdk.capture_exception(exc)

        # Create error response
        error_response = create_error_response(
            error_code=error_code,
            message="An unexpected error occurred",
            request_id=getattr(request.state, "correlation_id", None),
        )

        # Return JSON response
        return JSONResponse(
            status_code=status_code,
            content=error_response.dict(exclude_none=True),
        )

    logger.info("Exception handlers registered")


# Decorator for automatic retries with backoff
def with_retry(
    max_retries: int = 3,
    initial_backoff: float = 0.1,
    max_backoff: float = 10.0,
    backoff_factor: float = 2.0,
    retryable_exceptions: List[Type[Exception]] = None,
):
    """
    Decorator for automatic retries with exponential backoff

    Args:
        max_retries: Maximum number of retry attempts
        initial_backoff: Initial backoff time in seconds
        max_backoff: Maximum backoff time in seconds
        backoff_factor: Factor to increase backoff time by after each retry
        retryable_exceptions: List of exception types to retry on

    Returns:
        Decorated function
    """
    # Default retryable exceptions
    if retryable_exceptions is None:
        retryable_exceptions = [
            ConnectionError,
            TimeoutError,
        ]

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            retries = 0
            current_backoff = initial_backoff

            while True:
                try:
                    return await func(*args, **kwargs)

                except Exception as e:
                    # Only retry on specified exceptions
                    if not any(isinstance(e, exc) for exc in retryable_exceptions):
                        raise e

                    # Check if we've reached the maximum retries
                    retries += 1
                    if retries > max_retries:
                        logger.warning(
                            f"Max retries ({max_retries}) exceeded for "
                            f"{func.__name__}, raising exception"
                        )
                        raise e

                    # Calculate backoff time
                    backoff_time = min(current_backoff, max_backoff)
                    current_backoff *= backoff_factor

                    # Log retry attempt
                    logger.info(
                        f"Retrying {func.__name__} after exception: {str(e)}, "
                        f"retry {retries}/{max_retries}, backoff {backoff_time:.2f}s"
                    )

                    # Wait for backoff time
                    await asyncio.sleep(backoff_time)

        return wrapper

    return decorator
