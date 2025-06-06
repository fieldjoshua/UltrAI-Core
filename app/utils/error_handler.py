"""Centralized error handling for the application."""

import logging
import traceback
from datetime import datetime
from typing import Any, Dict, Optional, Tuple

from fastapi import HTTPException, Request, Response
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from .errors import (
    BaseError,
    ErrorCategory,
    ErrorSeverity,
    InternalServerError,
    ValidationError,
)

logger = logging.getLogger(__name__)


class ErrorHandler:
    """Centralized error handler for consistent error responses."""

    def __init__(self, debug: bool = False):
        self.debug = debug
        self.error_mappings = self._load_error_mappings()

    def _load_error_mappings(self) -> Dict[str, str]:
        """Load error code mappings."""
        return {
            # Add any custom error mappings here
        }

    def handle_error(
        self,
        error: Exception,
        request: Optional[Request] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> JSONResponse:
        """Handle error and return appropriate response."""
        # Add request context
        if request:
            context = context or {}
            context.update(
                {
                    "method": request.method,
                    "path": request.url.path,
                    "client": request.client.host if request.client else None,
                    "headers": dict(request.headers) if self.debug else None,
                    "locale": getattr(request.state, "locale", None),
                }
            )

        # Handle different error types
        if isinstance(error, BaseError):
            return self._handle_base_error(error, context)
        elif isinstance(error, HTTPException):
            return self._handle_http_exception(error, context)
        elif isinstance(error, StarletteHTTPException):
            return self._handle_starlette_exception(error, context)
        else:
            return self._handle_unknown_error(error, context)

    def _handle_base_error(
        self, error: BaseError, context: Optional[Dict[str, Any]] = None
    ) -> JSONResponse:
        """Handle custom BaseError instances."""
        # Update error context
        if context:
            error.context.update(context)

        # Get user-friendly message
        user_message = self._get_user_message(error)

        response_data = {
            "error": {
                "code": error.code,
                "message": user_message,
                "details": error.details if self.debug else {},
                "timestamp": error.timestamp,
                "request_id": context.get("request_id") if context else None,
            }
        }

        # Add debug information in development
        if self.debug:
            response_data["error"]["debug"] = {
                "category": error.category.value,
                "severity": error.severity.value,
                "context": error.context,
                "traceback": traceback.format_exc(),
            }

        return JSONResponse(status_code=error.status_code, content=response_data)

    def _handle_http_exception(
        self, error: HTTPException, context: Optional[Dict[str, Any]] = None
    ) -> JSONResponse:
        """Handle FastAPI HTTPException."""
        response_data = {
            "error": {
                "code": f"HTTP_{error.status_code}",
                "message": error.detail,
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": context.get("request_id") if context else None,
            }
        }

        logger.warning(f"HTTP Exception: {error.status_code} - {error.detail}")

        return JSONResponse(status_code=error.status_code, content=response_data)

    def _handle_starlette_exception(
        self, error: StarletteHTTPException, context: Optional[Dict[str, Any]] = None
    ) -> JSONResponse:
        """Handle Starlette HTTPException."""
        return self._handle_http_exception(
            HTTPException(status_code=error.status_code, detail=error.detail), context
        )

    def _handle_unknown_error(
        self, error: Exception, context: Optional[Dict[str, Any]] = None
    ) -> JSONResponse:
        """Handle unknown/unexpected errors."""
        # Create InternalServerError
        internal_error = InternalServerError(
            message="An unexpected error occurred",
            details={"original_error": str(error)} if self.debug else {},
            context=context,
        )

        # Log the full error
        logger.error(
            f"Unexpected error: {type(error).__name__}: {str(error)}",
            exc_info=True,
            extra={"context": context},
        )

        return self._handle_base_error(internal_error, context)

    def _get_user_message(self, error: BaseError) -> str:
        """Get user-friendly error message."""
        from .user_messages import get_user_message

        # Get locale from request context if available
        locale = None
        if error.context and "locale" in error.context:
            locale = error.context["locale"]

        # Get user-friendly message
        return get_user_message(
            error_code=error.code, locale=locale, fallback_message=error.message
        )

    def create_error_response(
        self,
        error_code: str,
        message: Optional[str] = None,
        status_code: int = 400,
        details: Optional[Dict[str, Any]] = None,
    ) -> JSONResponse:
        """Create error response with standard format."""
        from .errors import ERROR_REGISTRY

        # Get error class
        error_class = ERROR_REGISTRY.get(error_code, BaseError)

        # Create error instance
        error = error_class(message=message, details=details)

        return self._handle_base_error(error)


# Get debug mode from config
import os

DEBUG_MODE = os.environ.get("DEBUG", "false").lower() == "true"

# Global error handler instance
error_handler = ErrorHandler(debug=DEBUG_MODE)


# Error response model for type hints
def error_response_model():
    """Return error response model for documentation."""
    return {
        "error": {
            "code": "string",
            "message": "string",
            "details": {},
            "timestamp": "string",
            "request_id": "string",
        }
    }


# Exception handlers for FastAPI
async def base_error_handler(request: Request, exc: BaseError) -> JSONResponse:
    """Handle BaseError exceptions."""
    return error_handler.handle_error(exc, request)


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTPException."""
    return error_handler.handle_error(exc, request)


async def validation_exception_handler(
    request: Request, exc: ValidationError
) -> JSONResponse:
    """Handle validation exceptions."""
    return error_handler.handle_error(exc, request)


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle all other exceptions."""
    return error_handler.handle_error(exc, request)


async def validation_exception_handler(request: Request, exc) -> JSONResponse:
    """Handle validation exceptions from FastAPI/Pydantic."""
    from fastapi.exceptions import RequestValidationError

    if isinstance(exc, RequestValidationError):
        # Extract validation errors
        errors = exc.errors()
        details = {
            "validation_errors": errors,
            "body": exc.body if hasattr(exc, "body") else None,
        }

        validation_error = ValidationError(
            message="Request validation failed", details=details
        )
        return error_handler.handle_error(validation_error, request)

    # For other validation errors, convert to ValidationError
    validation_error = ValidationError(
        message=str(exc), details={"error": type(exc).__name__}
    )
    return error_handler.handle_error(validation_error, request)


# Utility functions
def wrap_error_detail(field: str, message: str) -> Dict[str, Any]:
    """Wrap field-specific error details."""
    return {"field": field, "message": message}


def create_validation_error(field_errors: Dict[str, str]) -> ValidationError:
    """Create validation error from field errors."""
    from .errors import InvalidFormatError, RequiredFieldMissingError

    # Determine primary error type
    if any("required" in msg.lower() for msg in field_errors.values()):
        error_class = RequiredFieldMissingError
    else:
        error_class = InvalidFormatError

    # Create detailed error
    return error_class(message="Validation failed", details={"fields": field_errors})


# Missing functions for app.py compatibility
async def error_handling_middleware(request: Request, call_next):
    """
    Middleware for handling errors consistently across the application.
    """
    try:
        response = await call_next(request)
        return response
    except BaseError as e:
        return error_handler.handle_error(e, request)
    except HTTPException as e:
        return error_handler.handle_error(e, request)
    except Exception as e:
        return error_handler.handle_error(e, request)


def register_exception_handlers(app):
    """
    Register all custom exception handlers with the FastAPI app.
    """
    from fastapi.exceptions import RequestValidationError

    from .errors import BaseError

    # Register handler for BaseError and subclasses
    app.add_exception_handler(BaseError, base_error_handler)

    # Register handler for HTTPException
    app.add_exception_handler(HTTPException, http_exception_handler)

    # Register handler for Starlette HTTPException
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)

    # Register handler for validation errors
    app.add_exception_handler(RequestValidationError, validation_exception_handler)

    # Register catch-all handler
    app.add_exception_handler(Exception, generic_exception_handler)
