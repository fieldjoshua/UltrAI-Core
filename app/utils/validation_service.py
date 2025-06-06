"""
Validation service for the Ultra backend.

This module provides utilities for comprehensive request validation, schema validation,
and custom validation rules.
"""

import inspect
import re
from enum import Enum
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Set, Type, Union, get_type_hints

from fastapi import Depends, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field, ValidationError, root_validator, validator

from backend.utils.logging import get_logger

# Configure logger
logger = get_logger("validation", "logs/validation.log")

# Common validation patterns
VALIDATION_PATTERNS = {
    "email": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
    "url": r"^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$",
    "username": r"^[a-zA-Z0-9_-]{3,16}$",
    "password": r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@$!%*#?&]{8,}$",
    "alpha": r"^[a-zA-Z]+$",
    "alphanumeric": r"^[a-zA-Z0-9]+$",
    "numeric": r"^[0-9]+$",
    "phone": r"^\+?[0-9]{10,15}$",
    "date": r"^\d{4}-\d{2}-\d{2}$",
    "time": r"^\d{2}:\d{2}(:\d{2})?$",
    "datetime": r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(:\d{2})?(\.\d+)?(Z|[+-]\d{2}:\d{2})?$",
    "uuid": r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    "ipv4": r"^(\d{1,3}\.){3}\d{1,3}$",
    "ipv6": r"^([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$",
    "mac": r"^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$",
}


class ValidatedModel(BaseModel):
    """Base model with enhanced validation capabilities"""

    class Config:
        """Configuration for ValidatedModel"""

        # Validate all assignments
        validate_assignment = True
        # Extra fields are forbidden
        extra = "forbid"
        # Automatically exclude None fields in serialize
        exclude_none = True


def create_validated_model(
    model_name: str,
    fields: Dict[str, Any],
    validators: Optional[Dict[str, Callable]] = None,
) -> Type[ValidatedModel]:
    """
    Dynamically create a validated model class

    Args:
        model_name: Name of the model class
        fields: Dictionary of field definitions
        validators: Dictionary of validator methods

    Returns:
        A ValidatedModel subclass
    """
    # Create field annotations
    annotations = {}
    field_defaults = {}

    for field_name, field_def in fields.items():
        if isinstance(field_def, tuple):
            if len(field_def) >= 1:
                annotations[field_name] = field_def[0]
            if len(field_def) >= 2:
                field_defaults[field_name] = field_def[1]
        else:
            annotations[field_name] = field_def

    # Create class attributes
    attrs = {
        "__annotations__": annotations,
        **field_defaults,
    }

    # Add validators if provided
    if validators:
        for validator_name, validator_func in validators.items():
            attrs[validator_name] = validator_func

    # Create the model class
    model_class = type(model_name, (ValidatedModel,), attrs)

    return model_class


def validate_with_pattern(value: str, pattern_name: str) -> bool:
    """
    Validate a string against a named pattern

    Args:
        value: String to validate
        pattern_name: Name of the pattern to use

    Returns:
        True if the value matches the pattern, False otherwise
    """
    if pattern_name not in VALIDATION_PATTERNS:
        raise ValueError(f"Unknown pattern: {pattern_name}")

    pattern = VALIDATION_PATTERNS[pattern_name]
    return bool(re.match(pattern, value))


def pattern_validator(pattern_name: str, error_msg: Optional[str] = None):
    """
    Create a pydantic validator that validates against a named pattern

    Args:
        pattern_name: Name of the pattern to use
        error_msg: Custom error message

    Returns:
        A validator function
    """

    def validate(cls, value, field):
        if not validate_with_pattern(value, pattern_name):
            msg = error_msg or f"Value does not match {pattern_name} pattern"
            raise ValueError(msg)
        return value

    return validator(validate)


def validate_request(
    model: Type[BaseModel],
    request: Request,
    strict: bool = True,
    custom_error_messages: Optional[Dict[str, str]] = None,
) -> BaseModel:
    """
    Validate a request against a model

    Args:
        model: Pydantic model to validate against
        request: FastAPI request object
        strict: Whether to raise an exception on validation failure
        custom_error_messages: Custom error messages for validation errors

    Returns:
        Validated model instance

    Raises:
        RequestValidationError: If validation fails and strict=True
    """
    try:
        # Get request body
        body = await request.json()

        # Create model instance
        instance = model(**body)

        # Log successful validation
        logger.info(
            f"Request validation successful",
            extra={
                "model": model.__name__,
                "path": request.url.path,
                "method": request.method,
            },
        )

        return instance
    except ValidationError as e:
        # Prepare error details
        errors = e.errors()

        # Add custom error messages if provided
        if custom_error_messages:
            for error in errors:
                field = ".".join(str(loc) for loc in error["loc"])
                if field in custom_error_messages:
                    error["msg"] = custom_error_messages[field]

        # Log validation error
        logger.warning(
            f"Request validation failed: {str(e)}",
            extra={
                "model": model.__name__,
                "path": request.url.path,
                "method": request.method,
                "errors": errors,
            },
        )

        if strict:
            raise RequestValidationError(errors)

        return None


def validate_input(
    model: Type[BaseModel],
    error_status_code: int = status.HTTP_422_UNPROCESSABLE_ENTITY,
    custom_error_messages: Optional[Dict[str, str]] = None,
):
    """
    Decorator to validate function input against a model

    Args:
        model: Pydantic model to validate against
        error_status_code: HTTP status code to use for validation errors
        custom_error_messages: Custom error messages for validation errors

    Returns:
        Decorator function
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Find the request object
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break

            if not request:
                for _, value in kwargs.items():
                    if isinstance(value, Request):
                        request = value
                        break

            if not request:
                raise ValueError("No request object found")

            # Validate the request
            validated = await validate_request(
                model,
                request,
                strict=False,
                custom_error_messages=custom_error_messages,
            )

            if not validated:
                raise HTTPException(
                    status_code=error_status_code,
                    detail="Request validation failed",
                )

            # Call the original function with the validated model
            kwargs["validated_data"] = validated
            return await func(*args, **kwargs)

        return wrapper

    return decorator


def validate_output(
    model: Type[BaseModel],
    exclude_none: bool = True,
    custom_serializer: Optional[Callable] = None,
):
    """
    Decorator to validate function output against a model

    Args:
        model: Pydantic model to validate against
        exclude_none: Whether to exclude None fields in serialization
        custom_serializer: Custom serializer function

    Returns:
        Decorator function
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Call the original function
            result = await func(*args, **kwargs)

            try:
                # Use a custom serializer if provided
                if custom_serializer:
                    return custom_serializer(result)

                # If result is already a model instance, just validate
                if isinstance(result, BaseModel):
                    result.validate(result)
                    return result.dict(exclude_none=exclude_none)

                # Create model instance
                instance = model(**result)

                # Return serialized result
                return instance.dict(exclude_none=exclude_none)
            except ValidationError as e:
                logger.error(
                    f"Output validation failed: {str(e)}",
                    extra={
                        "func": func.__name__,
                        "model": model.__name__,
                        "errors": e.errors(),
                    },
                )

                # Re-raise the validation error
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Output validation failed",
                )

        return wrapper

    return decorator


class ValidationException(HTTPException):
    """Custom exception for validation errors"""

    def __init__(
        self,
        message: str = "Validation error",
        status_code: int = status.HTTP_422_UNPROCESSABLE_ENTITY,
        field_errors: Optional[Dict[str, str]] = None,
    ):
        detail = {"message": message}
        if field_errors:
            detail["field_errors"] = field_errors

        super().__init__(status_code=status_code, detail=detail)


# Type alias for validation functions
ValidationFunc = Callable[[Any], Any]


def field_validator(
    field_name: str,
    validator_func: ValidationFunc,
    error_message: str = "Invalid value",
):
    """
    Create a validator function for a specific field

    Args:
        field_name: Name of the field to validate
        validator_func: Function that takes a value and returns True/False or raises ValueError
        error_message: Error message to use if validation fails

    Returns:
        Validator function
    """

    def validate(cls, values):
        value = values.get(field_name)
        if value is not None:
            try:
                result = validator_func(value)
                if result is False:
                    raise ValueError(error_message)
            except ValueError as e:
                raise ValueError(f"{field_name}: {str(e)}")
        return values

    return root_validator(pre=True)(validate)


def dependency_validator(depends_on: List[Depends], model: Type[BaseModel]):
    """
    Validator that combines FastAPI dependencies with Pydantic validation

    Args:
        depends_on: List of FastAPI dependencies
        model: Pydantic model to validate against

    Returns:
        Callable that can be used as a FastAPI dependency
    """

    def validate_with_dependencies(request: Request, *args, **kwargs):
        # The dependencies will be passed as args/kwargs
        # Now we can validate the request against the model
        return validate_request(model, request)

    # Add dependencies to the function
    for dependency in depends_on:
        validate_with_dependencies = Depends(dependency)(validate_with_dependencies)

    return Depends(validate_with_dependencies)
