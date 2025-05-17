"""
Enhanced validation error handling for Ultra backend.

This module provides improved validation error handling for FastAPI applications,
with better error messages, logging, and response formatting.
"""

from typing import Any, Dict, List, Optional, Type, Union

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationError, create_model, validator

from backend.utils.logging import get_logger

# Configure logger
logger = get_logger("validation", "logs/validation.log")


class ValidationErrorDetail(BaseModel):
    """Model for a single validation error detail"""

    field: str
    message: str
    code: str
    location: List[str]
    input_value: Optional[Any] = None
    context: Optional[Dict[str, Any]] = None


class ValidationErrorResponse(BaseModel):
    """Model for the validation error response"""

    status: str = "error"
    message: str = "Validation error"
    code: str = "validation_error"
    errors: List[ValidationErrorDetail]

    @validator("errors")
    def sort_errors(cls, errors):
        """Sort errors by field name for consistency"""
        return sorted(errors, key=lambda x: x.field)


def format_validation_errors(exc: RequestValidationError) -> ValidationErrorResponse:
    """
    Format validation errors into a standardized response

    Args:
        exc: RequestValidationError exception

    Returns:
        Formatted ValidationErrorResponse
    """
    error_details = []

    # Process each error
    for error in exc.errors():
        # Extract location
        location = error.get("loc", [])
        field = ".".join(str(part) for part in location if not isinstance(part, int))

        # Skip body parameter itself (usually means the whole body is invalid)
        if field == "body":
            field = ""

        # Create error detail
        error_detail = ValidationErrorDetail(
            field=field,
            message=error.get("msg", "Invalid value"),
            code=error.get("type", "validation_error"),
            location=[str(loc) for loc in location],
            input_value=error.get("input"),
            context=error.get("ctx"),
        )

        error_details.append(error_detail)

    # Create response
    return ValidationErrorResponse(errors=error_details)


def log_validation_error(request: Request, exc: RequestValidationError) -> None:
    """
    Log validation error details

    Args:
        request: FastAPI request
        exc: Validation error exception
    """
    # Get formatted errors
    formatted = format_validation_errors(exc)

    # Log the error
    logger.warning(
        "Request validation failed",
        extra={
            "method": request.method,
            "path": request.url.path,
            "client_host": getattr(request.client, "host", "unknown"),
            "errors": [error.dict() for error in formatted.errors],
        },
    )


def create_error_handler(app: FastAPI) -> None:
    """
    Create and register enhanced validation error handler

    Args:
        app: FastAPI application
    """

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """
        Handle validation errors with enhanced error response

        Args:
            request: FastAPI request
            exc: Validation error exception

        Returns:
            JSON response with validation error details
        """
        # Log the error
        log_validation_error(request, exc)

        # Format the error response
        error_response = format_validation_errors(exc)

        # Return JSON response
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_response.dict(),
        )

    logger.info("Enhanced validation error handler registered")


def create_validated_model(name: str, **fields: Any) -> Type[BaseModel]:
    """
    Create a validated model with enhanced error messages

    Args:
        name: Model name
        **fields: Field definitions

    Returns:
        Pydantic model class
    """
    return create_model(name, **fields)


def setup_enhanced_validation(app: FastAPI) -> None:
    """
    Set up enhanced validation for a FastAPI application

    Args:
        app: FastAPI application
    """
    # Register error handler
    create_error_handler(app)

    logger.info("Enhanced validation system configured")
