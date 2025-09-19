"""
Unified Error Handling System for the UltraAI backend.

This module consolidates error handling functionality from multiple sources into a single,
comprehensive error handling system with:
- Standardized error codes and classifications
- Consistent error response formatting
- Detailed error logging with context
- Automatic recovery mechanisms (circuit breakers and retries)
- Domain-specific exception classes
"""

import asyncio
import inspect
import json
import os
import sys
import time
import traceback
import uuid
from enum import Enum
from functools import wraps
from http import HTTPStatus
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Type, Union

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
    """
    Comprehensive error code constants for consistent error handling across the application.
    These codes uniquely identify different error scenarios for programmatic handling.
    """

    # General errors (1xx)
    INTERNAL_ERROR = "internal_error"
    NOT_FOUND = "not_found"
    BAD_REQUEST = "bad_request"

    # Validation errors (2xx)
    VALIDATION_ERROR = "validation_error"
    INVALID_INPUT = "invalid_input"
    MISSING_FIELD = "missing_field"
    INVALID_FORMAT = "invalid_format"
    INVALID_TYPE = "invalid_type"
    VALUE_ERROR = "value_error"
    SCHEMA_ERROR = "schema_error"

    # Authentication errors (3xx)
    UNAUTHORIZED = "unauthorized"
    FORBIDDEN = "forbidden"
    INVALID_AUTH = "invalid_auth"
    EXPIRED_AUTH = "expired_auth"
    AUTH_REVOKED = "auth_revoked"
    INVALID_TOKEN = "invalid_token"
    EXPIRED_TOKEN = "expired_token"
    MISSING_TOKEN = "missing_token"

    # Resource errors (4xx)
    RESOURCE_EXISTS = "resource_exists"
    RESOURCE_NOT_FOUND = "resource_not_found"
    RESOURCE_CONFLICT = "resource_conflict"
    INSUFFICIENT_RESOURCES = "insufficient_resources"
    RESOURCE_EXHAUSTED = "resource_exhausted"

    # Rate limiting errors (5xx)
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    QUOTA_EXCEEDED = "quota_exceeded"
    THROTTLED = "throttled"

    # Service errors (6xx)
    SERVICE_UNAVAILABLE = "service_unavailable"
    EXTERNAL_SERVICE_ERROR = "external_service_error"
    TIMEOUT = "timeout"
    CIRCUIT_OPEN = "circuit_open"
    DEPENDENCY_FAILURE = "dependency_failure"
    CONNECTION_ERROR = "connection_error"

    # Business logic errors (7xx)
    BUSINESS_LOGIC_ERROR = "business_logic_error"
    PERMISSION_DENIED = "permission_denied"
    OPERATION_NOT_SUPPORTED = "operation_not_supported"
    INVALID_STATE = "invalid_state"
    PRECONDITION_FAILED = "precondition_failed"

    # Data errors (8xx)
    DATABASE_ERROR = "database_error"
    DATA_INTEGRITY_ERROR = "data_integrity_error"
    DATA_NOT_FOUND = "data_not_found"
    DATA_ALREADY_EXISTS = "data_already_exists"
    DATA_VALIDATION_ERROR = "data_validation_error"

    # LLM and model errors (9xx)
    MODEL_ERROR = "model_error"
    MODEL_UNAVAILABLE = "model_unavailable"
    MODEL_TIMEOUT = "model_timeout"
    MODEL_CONTENT_FILTER = "model_content_filter"
    MODEL_CONTEXT_LENGTH = "model_context_length"
    MODEL_BAD_RESPONSE = "model_bad_response"

    # Document errors (10xx)
    DOCUMENT_ERROR = "document_error"
    DOCUMENT_NOT_FOUND = "document_not_found"
    DOCUMENT_FORMAT_ERROR = "document_format_error"
    DOCUMENT_TOO_LARGE = "document_too_large"
    DOCUMENT_PROCESSING_ERROR = "document_processing_error"

    # Payment and pricing errors (11xx)
    PAYMENT_REQUIRED = "payment_required"
    PAYMENT_FAILED = "payment_failed"
    INSUFFICIENT_FUNDS = "insufficient_funds"
    SUBSCRIPTION_EXPIRED = "subscription_expired"
    SUBSCRIPTION_REQUIRED = "subscription_required"


class ErrorSeverity(str, Enum):
    """Error severity levels to guide logging and monitoring behavior"""

    CRITICAL = "critical"  # System is unusable, immediate attention required
    ERROR = "error"  # Error that prevents operation from completing
    WARNING = "warning"  # Potentially harmful situation, operation can continue
    INFO = "info"  # Informational message about an error
    DEBUG = "debug"  # Debugging information about an error


class ErrorCategory(str, Enum):
    """Error categories for grouping similar error types"""

    SECURITY = "security"  # Security-related errors
    VALIDATION = "validation"  # Input validation errors
    AUTHORIZATION = "authorization"  # Authentication/authorization errors
    RESOURCE = "resource"  # Resource access/manipulation errors
    SERVICE = "service"  # Service availability/external service errors
    SYSTEM = "system"  # System/infrastructure errors
    BUSINESS = "business"  # Business logic errors
    RATE_LIMIT = "rate_limit"  # Rate limiting/quota errors
    CLIENT = "client"  # Client-side errors
    DATA = "data"  # Data/database errors
    MODEL = "model"  # LLM/model errors
    DOCUMENT = "document"  # Document processing errors
    PAYMENT = "payment"  # Payment/pricing errors
    UNKNOWN = "unknown"  # Uncategorized errors


class ErrorClassification:
    """
    Comprehensive error classification system that maps error codes to HTTP status codes,
    severity levels, and categories for consistent handling across the application.
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
        ConnectionError: ErrorCode.CONNECTION_ERROR,
        PermissionError: ErrorCode.PERMISSION_DENIED,
        FileNotFoundError: ErrorCode.RESOURCE_NOT_FOUND,
        NotImplementedError: ErrorCode.OPERATION_NOT_SUPPORTED,
        json.JSONDecodeError: ErrorCode.INVALID_FORMAT,
        AssertionError: ErrorCode.PRECONDITION_FAILED,
    }

    # Mapping of error codes to HTTP status codes
    STATUS_CODE_MAPPING = {
        # General errors
        ErrorCode.INTERNAL_ERROR: status.HTTP_500_INTERNAL_SERVER_ERROR,
        ErrorCode.BAD_REQUEST: status.HTTP_400_BAD_REQUEST,
        ErrorCode.NOT_FOUND: status.HTTP_404_NOT_FOUND,
        # Validation errors
        ErrorCode.VALIDATION_ERROR: status.HTTP_422_UNPROCESSABLE_ENTITY,
        ErrorCode.INVALID_INPUT: status.HTTP_400_BAD_REQUEST,
        ErrorCode.MISSING_FIELD: status.HTTP_400_BAD_REQUEST,
        ErrorCode.INVALID_FORMAT: status.HTTP_400_BAD_REQUEST,
        ErrorCode.INVALID_TYPE: status.HTTP_400_BAD_REQUEST,
        ErrorCode.VALUE_ERROR: status.HTTP_400_BAD_REQUEST,
        ErrorCode.SCHEMA_ERROR: status.HTTP_422_UNPROCESSABLE_ENTITY,
        # Authentication errors
        ErrorCode.UNAUTHORIZED: status.HTTP_401_UNAUTHORIZED,
        ErrorCode.FORBIDDEN: status.HTTP_403_FORBIDDEN,
        ErrorCode.INVALID_AUTH: status.HTTP_401_UNAUTHORIZED,
        ErrorCode.EXPIRED_AUTH: status.HTTP_401_UNAUTHORIZED,
        ErrorCode.AUTH_REVOKED: status.HTTP_401_UNAUTHORIZED,
        ErrorCode.INVALID_TOKEN: status.HTTP_401_UNAUTHORIZED,
        ErrorCode.EXPIRED_TOKEN: status.HTTP_401_UNAUTHORIZED,
        ErrorCode.MISSING_TOKEN: status.HTTP_401_UNAUTHORIZED,
        # Resource errors
        ErrorCode.RESOURCE_EXISTS: status.HTTP_409_CONFLICT,
        ErrorCode.RESOURCE_NOT_FOUND: status.HTTP_404_NOT_FOUND,
        ErrorCode.RESOURCE_CONFLICT: status.HTTP_409_CONFLICT,
        ErrorCode.INSUFFICIENT_RESOURCES: status.HTTP_507_INSUFFICIENT_STORAGE,
        ErrorCode.RESOURCE_EXHAUSTED: status.HTTP_429_TOO_MANY_REQUESTS,
        # Rate limiting errors
        ErrorCode.RATE_LIMIT_EXCEEDED: status.HTTP_429_TOO_MANY_REQUESTS,
        ErrorCode.QUOTA_EXCEEDED: status.HTTP_429_TOO_MANY_REQUESTS,
        ErrorCode.THROTTLED: status.HTTP_429_TOO_MANY_REQUESTS,
        # Service errors
        ErrorCode.SERVICE_UNAVAILABLE: status.HTTP_503_SERVICE_UNAVAILABLE,
        ErrorCode.EXTERNAL_SERVICE_ERROR: status.HTTP_502_BAD_GATEWAY,
        ErrorCode.TIMEOUT: status.HTTP_504_GATEWAY_TIMEOUT,
        ErrorCode.CIRCUIT_OPEN: status.HTTP_503_SERVICE_UNAVAILABLE,
        ErrorCode.DEPENDENCY_FAILURE: status.HTTP_502_BAD_GATEWAY,
        ErrorCode.CONNECTION_ERROR: status.HTTP_502_BAD_GATEWAY,
        # Business logic errors
        ErrorCode.BUSINESS_LOGIC_ERROR: status.HTTP_422_UNPROCESSABLE_ENTITY,
        ErrorCode.PERMISSION_DENIED: status.HTTP_403_FORBIDDEN,
        ErrorCode.OPERATION_NOT_SUPPORTED: status.HTTP_405_METHOD_NOT_ALLOWED,
        ErrorCode.INVALID_STATE: status.HTTP_409_CONFLICT,
        ErrorCode.PRECONDITION_FAILED: status.HTTP_412_PRECONDITION_FAILED,
        # Data errors
        ErrorCode.DATABASE_ERROR: status.HTTP_500_INTERNAL_SERVER_ERROR,
        ErrorCode.DATA_INTEGRITY_ERROR: status.HTTP_409_CONFLICT,
        ErrorCode.DATA_NOT_FOUND: status.HTTP_404_NOT_FOUND,
        ErrorCode.DATA_ALREADY_EXISTS: status.HTTP_409_CONFLICT,
        ErrorCode.DATA_VALIDATION_ERROR: status.HTTP_422_UNPROCESSABLE_ENTITY,
        # LLM and model errors
        ErrorCode.MODEL_ERROR: status.HTTP_500_INTERNAL_SERVER_ERROR,
        ErrorCode.MODEL_UNAVAILABLE: status.HTTP_503_SERVICE_UNAVAILABLE,
        ErrorCode.MODEL_TIMEOUT: status.HTTP_504_GATEWAY_TIMEOUT,
        ErrorCode.MODEL_CONTENT_FILTER: status.HTTP_422_UNPROCESSABLE_ENTITY,
        ErrorCode.MODEL_CONTEXT_LENGTH: status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
        ErrorCode.MODEL_BAD_RESPONSE: status.HTTP_502_BAD_GATEWAY,
        # Document errors
        ErrorCode.DOCUMENT_ERROR: status.HTTP_500_INTERNAL_SERVER_ERROR,
        ErrorCode.DOCUMENT_NOT_FOUND: status.HTTP_404_NOT_FOUND,
        ErrorCode.DOCUMENT_FORMAT_ERROR: status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        ErrorCode.DOCUMENT_TOO_LARGE: status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
        ErrorCode.DOCUMENT_PROCESSING_ERROR: status.HTTP_500_INTERNAL_SERVER_ERROR,
        # Payment and pricing errors
        ErrorCode.PAYMENT_REQUIRED: status.HTTP_402_PAYMENT_REQUIRED,
        ErrorCode.PAYMENT_FAILED: status.HTTP_402_PAYMENT_REQUIRED,
        ErrorCode.INSUFFICIENT_FUNDS: status.HTTP_402_PAYMENT_REQUIRED,
        ErrorCode.SUBSCRIPTION_EXPIRED: status.HTTP_402_PAYMENT_REQUIRED,
        ErrorCode.SUBSCRIPTION_REQUIRED: status.HTTP_402_PAYMENT_REQUIRED,
    }

    # Mapping of error codes to severity levels
    SEVERITY_MAPPING = {
        # General errors
        ErrorCode.INTERNAL_ERROR: ErrorSeverity.ERROR,
        ErrorCode.BAD_REQUEST: ErrorSeverity.WARNING,
        ErrorCode.NOT_FOUND: ErrorSeverity.WARNING,
        # Validation errors - typically warnings as they're client errors
        ErrorCode.VALIDATION_ERROR: ErrorSeverity.WARNING,
        ErrorCode.INVALID_INPUT: ErrorSeverity.WARNING,
        ErrorCode.MISSING_FIELD: ErrorSeverity.WARNING,
        ErrorCode.INVALID_FORMAT: ErrorSeverity.WARNING,
        ErrorCode.INVALID_TYPE: ErrorSeverity.WARNING,
        ErrorCode.VALUE_ERROR: ErrorSeverity.WARNING,
        ErrorCode.SCHEMA_ERROR: ErrorSeverity.WARNING,
        # Authentication errors - usually warnings as they're client errors
        ErrorCode.UNAUTHORIZED: ErrorSeverity.WARNING,
        ErrorCode.FORBIDDEN: ErrorSeverity.WARNING,
        ErrorCode.INVALID_AUTH: ErrorSeverity.WARNING,
        ErrorCode.EXPIRED_AUTH: ErrorSeverity.INFO,
        ErrorCode.AUTH_REVOKED: ErrorSeverity.INFO,
        ErrorCode.INVALID_TOKEN: ErrorSeverity.WARNING,
        ErrorCode.EXPIRED_TOKEN: ErrorSeverity.INFO,
        ErrorCode.MISSING_TOKEN: ErrorSeverity.WARNING,
        # Resource errors
        ErrorCode.RESOURCE_EXISTS: ErrorSeverity.WARNING,
        ErrorCode.RESOURCE_NOT_FOUND: ErrorSeverity.WARNING,
        ErrorCode.RESOURCE_CONFLICT: ErrorSeverity.WARNING,
        ErrorCode.INSUFFICIENT_RESOURCES: ErrorSeverity.ERROR,
        ErrorCode.RESOURCE_EXHAUSTED: ErrorSeverity.ERROR,
        # Rate limiting errors
        ErrorCode.RATE_LIMIT_EXCEEDED: ErrorSeverity.INFO,
        ErrorCode.QUOTA_EXCEEDED: ErrorSeverity.INFO,
        ErrorCode.THROTTLED: ErrorSeverity.INFO,
        # Service errors - high severity since they affect functionality
        ErrorCode.SERVICE_UNAVAILABLE: ErrorSeverity.ERROR,
        ErrorCode.EXTERNAL_SERVICE_ERROR: ErrorSeverity.ERROR,
        ErrorCode.TIMEOUT: ErrorSeverity.ERROR,
        ErrorCode.CIRCUIT_OPEN: ErrorSeverity.WARNING,
        ErrorCode.DEPENDENCY_FAILURE: ErrorSeverity.ERROR,
        ErrorCode.CONNECTION_ERROR: ErrorSeverity.ERROR,
        # Business logic errors
        ErrorCode.BUSINESS_LOGIC_ERROR: ErrorSeverity.WARNING,
        ErrorCode.PERMISSION_DENIED: ErrorSeverity.WARNING,
        ErrorCode.OPERATION_NOT_SUPPORTED: ErrorSeverity.WARNING,
        ErrorCode.INVALID_STATE: ErrorSeverity.WARNING,
        ErrorCode.PRECONDITION_FAILED: ErrorSeverity.WARNING,
        # Data errors
        ErrorCode.DATABASE_ERROR: ErrorSeverity.ERROR,
        ErrorCode.DATA_INTEGRITY_ERROR: ErrorSeverity.ERROR,
        ErrorCode.DATA_NOT_FOUND: ErrorSeverity.WARNING,
        ErrorCode.DATA_ALREADY_EXISTS: ErrorSeverity.WARNING,
        ErrorCode.DATA_VALIDATION_ERROR: ErrorSeverity.WARNING,
        # LLM and model errors
        ErrorCode.MODEL_ERROR: ErrorSeverity.ERROR,
        ErrorCode.MODEL_UNAVAILABLE: ErrorSeverity.ERROR,
        ErrorCode.MODEL_TIMEOUT: ErrorSeverity.ERROR,
        ErrorCode.MODEL_CONTENT_FILTER: ErrorSeverity.WARNING,
        ErrorCode.MODEL_CONTEXT_LENGTH: ErrorSeverity.WARNING,
        ErrorCode.MODEL_BAD_RESPONSE: ErrorSeverity.ERROR,
        # Document errors
        ErrorCode.DOCUMENT_ERROR: ErrorSeverity.ERROR,
        ErrorCode.DOCUMENT_NOT_FOUND: ErrorSeverity.WARNING,
        ErrorCode.DOCUMENT_FORMAT_ERROR: ErrorSeverity.WARNING,
        ErrorCode.DOCUMENT_TOO_LARGE: ErrorSeverity.WARNING,
        ErrorCode.DOCUMENT_PROCESSING_ERROR: ErrorSeverity.ERROR,
        # Payment and pricing errors
        ErrorCode.PAYMENT_REQUIRED: ErrorSeverity.WARNING,
        ErrorCode.PAYMENT_FAILED: ErrorSeverity.WARNING,
        ErrorCode.INSUFFICIENT_FUNDS: ErrorSeverity.WARNING,
        ErrorCode.SUBSCRIPTION_EXPIRED: ErrorSeverity.WARNING,
        ErrorCode.SUBSCRIPTION_REQUIRED: ErrorSeverity.WARNING,
    }

    # Mapping of error codes to categories
    CATEGORY_MAPPING = {
        # General errors
        ErrorCode.INTERNAL_ERROR: ErrorCategory.SYSTEM,
        ErrorCode.BAD_REQUEST: ErrorCategory.CLIENT,
        ErrorCode.NOT_FOUND: ErrorCategory.RESOURCE,
        # Validation errors
        ErrorCode.VALIDATION_ERROR: ErrorCategory.VALIDATION,
        ErrorCode.INVALID_INPUT: ErrorCategory.VALIDATION,
        ErrorCode.MISSING_FIELD: ErrorCategory.VALIDATION,
        ErrorCode.INVALID_FORMAT: ErrorCategory.VALIDATION,
        ErrorCode.INVALID_TYPE: ErrorCategory.VALIDATION,
        ErrorCode.VALUE_ERROR: ErrorCategory.VALIDATION,
        ErrorCode.SCHEMA_ERROR: ErrorCategory.VALIDATION,
        # Authentication errors
        ErrorCode.UNAUTHORIZED: ErrorCategory.AUTHORIZATION,
        ErrorCode.FORBIDDEN: ErrorCategory.AUTHORIZATION,
        ErrorCode.INVALID_AUTH: ErrorCategory.SECURITY,
        ErrorCode.EXPIRED_AUTH: ErrorCategory.SECURITY,
        ErrorCode.AUTH_REVOKED: ErrorCategory.SECURITY,
        ErrorCode.INVALID_TOKEN: ErrorCategory.SECURITY,
        ErrorCode.EXPIRED_TOKEN: ErrorCategory.SECURITY,
        ErrorCode.MISSING_TOKEN: ErrorCategory.SECURITY,
        # Resource errors
        ErrorCode.RESOURCE_EXISTS: ErrorCategory.RESOURCE,
        ErrorCode.RESOURCE_NOT_FOUND: ErrorCategory.RESOURCE,
        ErrorCode.RESOURCE_CONFLICT: ErrorCategory.RESOURCE,
        ErrorCode.INSUFFICIENT_RESOURCES: ErrorCategory.SYSTEM,
        ErrorCode.RESOURCE_EXHAUSTED: ErrorCategory.SYSTEM,
        # Rate limiting errors
        ErrorCode.RATE_LIMIT_EXCEEDED: ErrorCategory.RATE_LIMIT,
        ErrorCode.QUOTA_EXCEEDED: ErrorCategory.RATE_LIMIT,
        ErrorCode.THROTTLED: ErrorCategory.RATE_LIMIT,
        # Service errors
        ErrorCode.SERVICE_UNAVAILABLE: ErrorCategory.SERVICE,
        ErrorCode.EXTERNAL_SERVICE_ERROR: ErrorCategory.SERVICE,
        ErrorCode.TIMEOUT: ErrorCategory.SERVICE,
        ErrorCode.CIRCUIT_OPEN: ErrorCategory.SERVICE,
        ErrorCode.DEPENDENCY_FAILURE: ErrorCategory.SERVICE,
        ErrorCode.CONNECTION_ERROR: ErrorCategory.SERVICE,
        # Business logic errors
        ErrorCode.BUSINESS_LOGIC_ERROR: ErrorCategory.BUSINESS,
        ErrorCode.PERMISSION_DENIED: ErrorCategory.AUTHORIZATION,
        ErrorCode.OPERATION_NOT_SUPPORTED: ErrorCategory.BUSINESS,
        ErrorCode.INVALID_STATE: ErrorCategory.BUSINESS,
        ErrorCode.PRECONDITION_FAILED: ErrorCategory.BUSINESS,
        # Data errors
        ErrorCode.DATABASE_ERROR: ErrorCategory.DATA,
        ErrorCode.DATA_INTEGRITY_ERROR: ErrorCategory.DATA,
        ErrorCode.DATA_NOT_FOUND: ErrorCategory.DATA,
        ErrorCode.DATA_ALREADY_EXISTS: ErrorCategory.DATA,
        ErrorCode.DATA_VALIDATION_ERROR: ErrorCategory.DATA,
        # LLM and model errors
        ErrorCode.MODEL_ERROR: ErrorCategory.MODEL,
        ErrorCode.MODEL_UNAVAILABLE: ErrorCategory.MODEL,
        ErrorCode.MODEL_TIMEOUT: ErrorCategory.MODEL,
        ErrorCode.MODEL_CONTENT_FILTER: ErrorCategory.MODEL,
        ErrorCode.MODEL_CONTEXT_LENGTH: ErrorCategory.MODEL,
        ErrorCode.MODEL_BAD_RESPONSE: ErrorCategory.MODEL,
        # Document errors
        ErrorCode.DOCUMENT_ERROR: ErrorCategory.DOCUMENT,
        ErrorCode.DOCUMENT_NOT_FOUND: ErrorCategory.DOCUMENT,
        ErrorCode.DOCUMENT_FORMAT_ERROR: ErrorCategory.DOCUMENT,
        ErrorCode.DOCUMENT_TOO_LARGE: ErrorCategory.DOCUMENT,
        ErrorCode.DOCUMENT_PROCESSING_ERROR: ErrorCategory.DOCUMENT,
        # Payment and pricing errors
        ErrorCode.PAYMENT_REQUIRED: ErrorCategory.PAYMENT,
        ErrorCode.PAYMENT_FAILED: ErrorCategory.PAYMENT,
        ErrorCode.INSUFFICIENT_FUNDS: ErrorCategory.PAYMENT,
        ErrorCode.SUBSCRIPTION_EXPIRED: ErrorCategory.PAYMENT,
        ErrorCode.SUBSCRIPTION_REQUIRED: ErrorCategory.PAYMENT,
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
    """Base exception for all Ultra custom exceptions with enhanced metadata"""

    def __init__(
        self,
        message: str,
        code: str = ErrorCode.INTERNAL_ERROR,
        status_code: Optional[int] = None,
        details: Optional[Union[List[ErrorDetail], Dict[str, Any], str]] = None,
        correlation_id: Optional[str] = None,
        original_exception: Optional[Exception] = None,
    ):
        """
        Initialize a new UltraBaseException

        Args:
            message: Human-readable error message
            code: Error code for programmatic handling
            status_code: HTTP status code to return (derived from code if not provided)
            details: Additional details about the error
            correlation_id: Unique identifier for tracking this error across systems
            original_exception: The original exception that caused this one
        """
        self.message = message
        self.code = code
        self.status_code = status_code or ErrorClassification.get_status_code(code)
        self.details = details
        self.correlation_id = correlation_id or CorrelationContext.get_correlation_id()
        self.original_exception = original_exception
        self.severity = ErrorClassification.get_severity(code)
        self.category = ErrorClassification.get_category(code)
        self.timestamp = time.time()

        # Capture the current stack trace
        self.stack_trace = traceback.format_exc() if sys.exc_info()[0] else None

        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        """Convert the exception to a dictionary for logging or serialization"""
        result = {
            "message": self.message,
            "code": self.code,
            "status_code": self.status_code,
            "severity": str(self.severity),
            "category": str(self.category),
            "timestamp": self.timestamp,
            "correlation_id": self.correlation_id,
        }

        if self.details:
            result["details"] = self.details

        if self.stack_trace:
            result["stack_trace"] = self.stack_trace

        if self.original_exception:
            result["original_exception"] = {
                "type": type(self.original_exception).__name__,
                "message": str(self.original_exception),
            }

        return result

    def to_error_response(self) -> ErrorResponse:
        """Convert the exception to an ErrorResponse model"""
        return create_error_response(
            error_code=self.code,
            message=self.message,
            details=self.details,
            request_id=self.correlation_id,
        )


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
    correlation_id = getattr(request.state, "correlation_id", None) or request_id

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
        "correlation_id": correlation_id,
        "exception_type": exc_type,
        "exception_message": exc_msg,
    }

    # Add more details for Ultra exceptions
    if isinstance(exc, UltraBaseException):
        log_data.update(
            {
                "error_code": exc.code,
                "error_category": str(exc.category),
                "error_severity": str(exc.severity),
                "status_code": exc.status_code,
            }
        )

        if exc.details:
            log_data["error_details"] = exc.details

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

    # Send to Sentry if it's a server error
    if isinstance(exc, UltraBaseException) and exc.status_code >= 500:
        sentry_sdk.capture_exception(exc)


class CircuitBreaker:
    """
    Circuit breaker pattern implementation for protecting against failing external services.

    When a service fails repeatedly, the circuit breaker opens and fails fast, preventing
    cascading failures and allowing the service time to recover.
    """

    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        reset_timeout: int = 30,
        half_open_success_threshold: int = 2,
    ):
        """
        Initialize the circuit breaker

        Args:
            name: Name of the circuit breaker (typically the service name)
            failure_threshold: Number of consecutive failures before opening the circuit
            reset_timeout: Time in seconds before trying to close the circuit again
            half_open_success_threshold: Number of successful requests needed to close the circuit
        """
        self.name = name
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.half_open_success_threshold = half_open_success_threshold

        self.failure_count = 0
        self.last_failure_time = 0
        self.state = "closed"  # closed, open, half-open
        self.success_count = 0

        logger.info(
            f"Initialized circuit breaker {name} with "
            f"failure_threshold={failure_threshold}, "
            f"reset_timeout={reset_timeout}s, "
            f"half_open_success_threshold={half_open_success_threshold}"
        )

    def register_failure(self) -> None:
        """Register a failure and potentially open the circuit"""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.state == "closed" and self.failure_count >= self.failure_threshold:
            self.state = "open"
            logger.warning(
                f"Circuit {self.name} opened after {self.failure_count} consecutive failures"
            )

        elif self.state == "half-open":
            self.state = "open"
            self.failure_count = self.failure_threshold
            logger.warning(
                f"Circuit {self.name} reopened after a failure in half-open state"
            )

    def register_success(self) -> None:
        """Register a success and potentially close the circuit"""
        if self.state == "half-open":
            self.success_count += 1

            if self.success_count >= self.half_open_success_threshold:
                self.state = "closed"
                self.failure_count = 0
                self.success_count = 0
                logger.info(
                    f"Circuit {self.name} closed after {self.success_count} successful requests in half-open state"
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
                logger.info(f"Circuit {self.name} half-opened, allowing trial request")
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
                    message=f"Service {self.name} temporarily unavailable due to recent failures",
                    code=ErrorCode.CIRCUIT_OPEN,
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    details={"service": self.name, "circuit_state": self.state},
                )

            try:
                if inspect.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)

                self.register_success()
                return result

            except UltraBaseException as e:
                # Only register failure for service errors
                if e.category == ErrorCategory.SERVICE:
                    self.register_failure()
                raise e

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
        self.exclude_paths = exclude_paths or ["/health", "/metrics", "/docs", "/redoc"]

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
        correlation_id = request.headers.get(
            "X-Correlation-ID", f"ultra-{uuid.uuid4()}"
        )
        CorrelationContext.set_correlation_id(correlation_id)

        # Add correlation ID to request state
        request.state.correlation_id = correlation_id
        request.state.request_id = correlation_id  # For backward compatibility

        try:
            # Process the request
            response = await call_next(request)

            # Add correlation ID to response headers
            response.headers["X-Correlation-ID"] = correlation_id

            return response

        except UltraBaseException as e:
            # Log structured exception
            log_exception(request, e, level=str(e.severity))

            # Create error response
            error_response = e.to_error_response()

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
            log_exception(request, e, level=str(severity))

            # Only include detailed error information if allowed
            include_details = self.include_debug_details
            if request.url.path in self.exclude_paths:
                include_details = False

            # Environment-aware error details
            is_production = os.environ.get("ENVIRONMENT", "development") == "production"
            if is_production:
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


def with_retry(
    max_retries: int = 3,
    initial_backoff: float = 0.1,
    max_backoff: float = 10.0,
    backoff_factor: float = 2.0,
    retryable_exceptions: List[Type[Exception]] = None,
    retryable_status_codes: List[int] = None,
):
    """
    Decorator for automatic retries with exponential backoff

    Args:
        max_retries: Maximum number of retry attempts
        initial_backoff: Initial backoff time in seconds
        max_backoff: Maximum backoff time in seconds
        backoff_factor: Factor to increase backoff time by after each retry
        retryable_exceptions: List of exception types to retry on
        retryable_status_codes: List of HTTP status codes to retry on

    Returns:
        Decorated function
    """
    # Default retryable exceptions
    if retryable_exceptions is None:
        retryable_exceptions = [
            ConnectionError,
            TimeoutError,
        ]

    # Default retryable status codes (5xx)
    if retryable_status_codes is None:
        retryable_status_codes = [500, 502, 503, 504]

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            retries = 0
            current_backoff = initial_backoff

            while True:
                try:
                    if inspect.iscoroutinefunction(func):
                        return await func(*args, **kwargs)
                    else:
                        return func(*args, **kwargs)

                except UltraBaseException as e:
                    # Only retry on specific status codes
                    if e.status_code not in retryable_status_codes:
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
        # Ensure message is always a string
        message = exc.detail if isinstance(exc.detail, str) else str(exc.detail)
        error_response = create_error_response(
            error_code=f"http_{exc.status_code}",
            message=message,
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
        log_exception(request, exc, level=str(exc.severity))

        # Create error response
        error_response = exc.to_error_response()

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

        # Don't expose internal error details in production
        is_production = os.environ.get("ENVIRONMENT", "development") == "production"
        details = None if is_production else format_exception(exc)

        # Create error response
        error_response = create_error_response(
            error_code=error_code,
            message="An unexpected error occurred",
            details=details,
            request_id=getattr(request.state, "correlation_id", None),
        )

        # Return JSON response
        return JSONResponse(
            status_code=status_code,
            content=error_response.dict(exclude_none=True),
        )

    logger.info("Exception handlers registered")


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
