"""
Error handling module for the Ultra backend.

This module provides standardized error handling, custom exceptions,
and error response formatting for the application.
"""

from typing import Any, Dict, Optional
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
import logging

# Set up logging
logger = logging.getLogger(__name__)


# Standard error response format
class ErrorResponse:
    def __init__(
        self,
        status: str = "error",
        message: str = "An error occurred",
        code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.status = status
        self.message = message
        self.code = code
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "message": self.message,
            "code": self.code,
            "details": self.details,
        }


# Custom exceptions
class UltraException(Exception):
    """Base exception for Ultra application errors."""

    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.code = code
        self.details = details or {}
        super().__init__(message)


class AuthenticationError(UltraException):
    """Raised when authentication fails."""

    def __init__(
        self,
        message: str = "Authentication failed",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            code="AUTH_ERROR",
            details=details,
        )


class AuthorizationError(UltraException):
    """Raised when authorization fails."""

    def __init__(
        self, message: str = "Not authorized", details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            code="FORBIDDEN",
            details=details,
        )


class ResourceNotFoundError(UltraException):
    """Raised when a requested resource is not found."""

    def __init__(
        self,
        message: str = "Resource not found",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            code="NOT_FOUND",
            details=details,
        )


class ValidationError(UltraException):
    """Raised when input validation fails."""

    def __init__(
        self,
        message: str = "Validation error",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            code="VALIDATION_ERROR",
            details=details,
        )


class ProcessingError(UltraException):
    """Raised when there is an error processing a request."""

    def __init__(
        self,
        message: str = "Processing error",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            code="PROCESSING_ERROR",
            details=details,
        )


class InternalServerError(UltraException):
    """Raised when there is an unexpected internal server error."""

    def __init__(
        self,
        message: str = "Internal server error",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            code="INTERNAL_ERROR",
            details=details,
        )


class ServiceError(UltraException):
    """Raised when a service operation fails."""

    def __init__(
        self, message: str = "Service error", details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            code="SERVICE_ERROR",
            details=details,
        )


# Error response handler
def handle_error(error: Exception) -> JSONResponse:
    """
    Handle exceptions and return appropriate JSONResponse.

    Args:
        error: The exception to handle

    Returns:
        JSONResponse: Formatted error response
    """
    if isinstance(error, UltraException):
        # Handle custom Ultra exceptions
        error_response = ErrorResponse(
            message=error.message,
            code=error.code,
            details=error.details,
        )
        return JSONResponse(
            status_code=error.status_code,
            content=error_response.to_dict(),
        )
    elif isinstance(error, HTTPException):
        # Handle FastAPI HTTP exceptions
        error_response = ErrorResponse(
            message=str(error.detail),
            code="HTTP_ERROR",
            details={"status_code": error.status_code},
        )
        return JSONResponse(
            status_code=error.status_code,
            content=error_response.to_dict(),
        )
    else:
        # Handle unexpected errors
        logger.error(f"Unexpected error: {str(error)}", exc_info=True)
        error_response = ErrorResponse(
            message="An unexpected error occurred",
            code="INTERNAL_ERROR",
            details={"error": str(error)},
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response.to_dict(),
        )
