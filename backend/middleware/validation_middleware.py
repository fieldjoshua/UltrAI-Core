"""
Input validation middleware for the Ultra backend.

This module provides a FastAPI middleware that performs additional validation
on request data beyond the standard Pydantic validation, including sanitization
of input data and protection against various injection attacks.
"""

import json
import re
from typing import Any, Callable, Dict, List, Optional, Set, Union

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from backend.models.base_models import ErrorResponse
from backend.utils.logging import get_logger, log_error

# Set up logger
logger = get_logger("validation_middleware", "logs/security.log")

# Common patterns for validation
SQL_INJECTION_PATTERN = re.compile(
    r"(?i)(\bselect\s+|insert\s+into|update\s+|delete\s+from|drop\s+|alter\s+|create\s+|union\s+|exec\s+|execute\s+|--|\\\*\/)"
)
XSS_PATTERN = re.compile(r"(?i)(<script|javascript:|on\w+\s*=|<iframe|<object|alert\()")
PATH_TRAVERSAL_PATTERN = re.compile(r"(?i)(\.\.\/|\.\.\\|~\/|~\\)")
COMMAND_INJECTION_PATTERN = re.compile(r"(?i)(;|\||&&|\$\(|\`)")


class ValidationMiddleware(BaseHTTPMiddleware):
    """Middleware for additional input validation and sanitization"""

    def __init__(
        self,
        app: ASGIApp,
        max_content_length: int = 10 * 1024 * 1024,  # 10MB
        max_path_length: int = 2000,
        max_query_params: int = 50,
        max_header_length: int = 8192,
        max_json_items: int = 1000,
        content_types: Optional[Set[str]] = None,
        exempt_paths: Optional[List[str]] = None,
    ):
        """
        Initialize validation middleware

        Args:
            app: ASGI application
            max_content_length: Maximum content length in bytes
            max_path_length: Maximum URL path length
            max_query_params: Maximum number of query parameters
            max_header_length: Maximum header length
            max_json_items: Maximum number of items in JSON object
            content_types: Allowed content types
            exempt_paths: Paths exempt from validation
        """
        super().__init__(app)
        self.max_content_length = max_content_length
        self.max_path_length = max_path_length
        self.max_query_params = max_query_params
        self.max_header_length = max_header_length
        self.max_json_items = max_json_items
        self.content_types = content_types or {
            "application/json",
            "application/x-www-form-urlencoded",
            "multipart/form-data",
        }
        self.exempt_paths = exempt_paths or [
            "/api/docs",
            "/api/redoc",
            "/api/openapi.json",
            "/health",
            "/metrics",
        ]
        logger.info(
            f"Initialized ValidationMiddleware with {len(self.exempt_paths)} exempt paths"
        )

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process the request and validate input data

        Args:
            request: FastAPI request object
            call_next: Next middleware/route handler

        Returns:
            Response
        """
        # Skip validation for exempt paths
        if any(request.url.path.startswith(path) for path in self.exempt_paths):
            return await call_next(request)

        # Validate URL path length
        if len(request.url.path) > self.max_path_length:
            return self._create_validation_error_response(
                "URL path exceeds maximum length",
                "path_too_long",
                status.HTTP_414_URI_TOO_LONG,
            )

        # Validate number of query parameters
        if len(request.query_params) > self.max_query_params:
            return self._create_validation_error_response(
                "Too many query parameters",
                "too_many_params",
                status.HTTP_400_BAD_REQUEST,
            )

        # Skip content validation for GET, HEAD, and OPTIONS requests
        if request.method in {"GET", "HEAD", "OPTIONS"}:
            # Still validate query parameters for injection patterns
            for param, value in request.query_params.items():
                validation_result = self._validate_string_input(param, value)
                if validation_result:
                    return self._create_validation_error_response(
                        f"Invalid query parameter: {validation_result}",
                        "invalid_query_param",
                        status.HTTP_400_BAD_REQUEST,
                    )
            return await call_next(request)

        # For other methods, validate content type
        content_type = request.headers.get("content-type", "")
        if content_type and not any(ct in content_type for ct in self.content_types):
            return self._create_validation_error_response(
                f"Unsupported content type: {content_type}",
                "unsupported_content_type",
                status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            )

        # Validate content length
        content_length = request.headers.get("content-length", "0")
        try:
            if int(content_length) > self.max_content_length:
                return self._create_validation_error_response(
                    "Request entity too large",
                    "content_too_large",
                    status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                )
        except ValueError:
            # If content-length is not a valid integer, continue
            pass

        # For JSON content, validate the JSON body
        if "application/json" in content_type:
            try:
                # Read and validate JSON body
                body = await request.body()
                if body:
                    json_data = json.loads(body)
                    validation_result = self._validate_json_content(json_data)
                    if validation_result:
                        return self._create_validation_error_response(
                            validation_result,
                            "invalid_json_content",
                            status.HTTP_400_BAD_REQUEST,
                        )
            except json.JSONDecodeError:
                return self._create_validation_error_response(
                    "Invalid JSON format",
                    "invalid_json",
                    status.HTTP_400_BAD_REQUEST,
                )
            except Exception as e:
                log_error("JSON validation error", e)
                return self._create_validation_error_response(
                    "Error validating request body",
                    "validation_error",
                    status.HTTP_400_BAD_REQUEST,
                )

        # Process the request
        return await call_next(request)

    def _validate_string_input(self, param_name: str, value: str) -> Optional[str]:
        """
        Validate a string input for security issues

        Args:
            param_name: Name of the parameter
            value: Value to validate

        Returns:
            Error message if validation fails, None otherwise
        """
        # Skip validation for empty strings
        if not value:
            return None

        # Check for SQL injection patterns
        if SQL_INJECTION_PATTERN.search(value):
            return f"Potential SQL injection detected in {param_name}"

        # Check for XSS patterns
        if XSS_PATTERN.search(value):
            return f"Potential XSS detected in {param_name}"

        # Check for path traversal patterns
        if PATH_TRAVERSAL_PATTERN.search(value):
            return f"Potential path traversal detected in {param_name}"

        # Check for command injection patterns
        if COMMAND_INJECTION_PATTERN.search(value):
            return f"Potential command injection detected in {param_name}"

        return None

    def _validate_json_content(self, data: Any, path: str = "") -> Optional[str]:
        """
        Recursively validate JSON content

        Args:
            data: JSON data to validate
            path: Current path in the JSON structure

        Returns:
            Error message if validation fails, None otherwise
        """
        # Check for object size limits
        if isinstance(data, dict):
            if len(data) > self.max_json_items:
                return f"JSON object at {path or 'root'} exceeds maximum size"

            # Validate each key and value in the dictionary
            for key, value in data.items():
                # Validate key for injection patterns
                key_validation = self._validate_string_input(
                    f"key at {path}/{key}", key
                )
                if key_validation:
                    return key_validation

                # Recursively validate value
                if isinstance(value, (dict, list)):
                    nested_validation = self._validate_json_content(
                        value, f"{path}/{key}"
                    )
                    if nested_validation:
                        return nested_validation
                elif isinstance(value, str):
                    string_validation = self._validate_string_input(
                        f"value at {path}/{key}", value
                    )
                    if string_validation:
                        return string_validation

        # Check for array size limits
        elif isinstance(data, list):
            if len(data) > self.max_json_items:
                return f"JSON array at {path or 'root'} exceeds maximum size"

            # Recursively validate each item in the array
            for i, item in enumerate(data):
                if isinstance(item, (dict, list)):
                    nested_validation = self._validate_json_content(
                        item, f"{path}[{i}]"
                    )
                    if nested_validation:
                        return nested_validation
                elif isinstance(item, str):
                    string_validation = self._validate_string_input(
                        f"item at {path}[{i}]", item
                    )
                    if string_validation:
                        return string_validation

        # If we reached here, validation passed
        return None

    def _create_validation_error_response(
        self, message: str, code: str, status_code: int
    ) -> JSONResponse:
        """
        Create validation error response

        Args:
            message: Error message
            code: Error code
            status_code: HTTP status code

        Returns:
            JSONResponse with error details
        """
        error_response = ErrorResponse(
            status="error",
            message=message,
            code=code,
        )

        return JSONResponse(
            status_code=status_code,
            content=error_response.dict(exclude_none=True),
        )


def setup_validation_middleware(
    app: ASGIApp,
    max_content_length: int = 10 * 1024 * 1024,
    max_path_length: int = 2000,
    max_query_params: int = 50,
    exempt_paths: Optional[List[str]] = None,
) -> None:
    """
    Set up validation middleware for the FastAPI application

    Args:
        app: FastAPI application
        max_content_length: Maximum content length in bytes
        max_path_length: Maximum URL path length
        max_query_params: Maximum number of query parameters
        exempt_paths: Paths exempt from validation
    """
    app.add_middleware(
        ValidationMiddleware,
        max_content_length=max_content_length,
        max_path_length=max_path_length,
        max_query_params=max_query_params,
        exempt_paths=exempt_paths,
    )
    logger.info("Validation middleware added to application")
