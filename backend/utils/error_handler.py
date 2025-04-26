"""
Error handling middleware and exception handlers for the UltraAI backend.

This module provides a centralized error handling solution with:
- Standardized error response format
- Exception registration with FastAPI
- Middleware for capturing unhandled exceptions
- Integration with logging and monitoring systems
"""

import traceback
from typing import Any, Dict, List, Optional, Union

import sentry_sdk
from fastapi import FastAPI, Request, Response, status, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.exc import SQLAlchemyError

from backend.utils.exceptions import UltraBaseException
from backend.utils.logging import CorrelationContext, log_error, get_logger


# Define standard error response models
class ErrorDetail(BaseModel):
    """Details about a specific error"""

    type: str
    msg: str
    loc: Optional[List[str]] = None
    code: Optional[str] = None
    ctx: Optional[Dict[str, Any]] = None


class ErrorResponse(BaseModel):
    """Standard error response format"""

    status: str = "error"
    message: str
    code: str
    details: Optional[Union[List[Any], Dict[str, Any]]] = None
    request_id: Optional[str] = None


# Exception handler for FastAPI
def register_exception_handlers(app: FastAPI) -> None:
    """Register all exception handlers with the FastAPI app."""

    @app.exception_handler(UltraBaseException)
    async def handle_ultra_exception(request: Request, exc: UltraBaseException):
        """Handle custom Ultra exceptions"""
        # Log the error
        log_error(
            f"Ultra API error: {exc.code} - {exc.message}",
            extra={
                "status_code": exc.status_code,
                "error_code": exc.code,
                "endpoint": request.url.path,
                "method": request.method,
            },
        )

        # Capture in Sentry if it's a server error (5xx)
        if exc.status_code >= 500:
            sentry_sdk.capture_exception(exc)

        # Create standardized error response
        error_response = ErrorResponse(
            status="error",
            message=exc.message,
            code=exc.code,
            details=exc.details,
            request_id=CorrelationContext.get_correlation_id(),
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
        log_error(
            f"Validation error: {error_details}",
            extra={
                "endpoint": request.url.path,
                "method": request.method,
                "validation_errors": exc.errors(),
            },
        )

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
            request_id=CorrelationContext.get_correlation_id(),
        )

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_response.dict(exclude_none=True),
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        """Handle Starlette HTTP exceptions"""
        # Log the error
        log_error(
            f"HTTP error {exc.status_code}: {exc.detail}",
            extra={
                "status_code": exc.status_code,
                "endpoint": request.url.path,
                "method": request.method,
            },
        )

        # Create standardized error response
        error_response = ErrorResponse(
            status="error",
            message=exc.detail,
            code=f"http_{exc.status_code}",
            request_id=CorrelationContext.get_correlation_id(),
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
        log_error(
            f"Unhandled exception: {str(exc)}",
            error=exc,
            extra={
                "traceback": tb,
                "endpoint": request.url.path,
                "method": request.method,
            },
        )

        # Capture in Sentry
        sentry_sdk.capture_exception(exc)

        # Create standardized error response (with limited info for security)
        error_response = ErrorResponse(
            status="error",
            message="An unexpected error occurred",
            code="internal_server_error",
            request_id=CorrelationContext.get_correlation_id(),
        )

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response.dict(exclude_none=True),
        )


# Middleware to add request ID and handle errors consistently
async def error_handling_middleware(request: Request, call_next):
    """Middleware to add request_id to every request and handle errors consistently."""
    # Generate a unique request ID using the CorrelationContext
    correlation_id = CorrelationContext.get_correlation_id()

    # Add the correlation ID to request state for potential use in handlers
    request.state.correlation_id = correlation_id

    try:
        # Process the request
        response = await call_next(request)

        # Add correlation ID header to response
        if isinstance(response, Response):
            response.headers["X-Correlation-ID"] = correlation_id

        return response

    except Exception as exc:
        # This handles any errors not caught by the exception handlers
        log_error(
            f"Unhandled error in middleware: {str(exc)}",
            error=exc,
            extra={
                "endpoint": request.url.path,
                "method": request.method,
            },
        )

        sentry_sdk.capture_exception(exc)

        # Create standardized error response
        error_response = ErrorResponse(
            status="error",
            message="An unexpected error occurred",
            code="internal_server_error",
            request_id=correlation_id,
        )

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response.dict(exclude_none=True),
            headers={"X-Correlation-ID": correlation_id},
        )


logger = get_logger("error_handler", "logs/error.log")


def handle_error(error: Exception) -> None:
    """Handle errors consistently across the application."""
    if isinstance(error, HTTPException):
        raise error

    if isinstance(error, SQLAlchemyError):
        logger.error(f"Database error: {str(error)}")
        raise HTTPException(
            status_code=500,
            detail="Database error occurred. Please try again later.",
        )

    logger.error(f"Unexpected error: {str(error)}")
    raise HTTPException(
        status_code=500,
        detail="An unexpected error occurred. Please try again later.",
    )
