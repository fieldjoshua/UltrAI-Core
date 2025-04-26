from typing import Any, Dict, Optional
from pydantic import BaseModel


class ErrorResponse(BaseModel):
    """Standard error response model for the API."""

    code: str
    message: str
    details: Optional[Dict[str, Any]] = None


class UltraAIException(Exception):
    """Base exception for all UltraAI errors."""

    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = 400,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__()
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details

    def to_response(self) -> ErrorResponse:
        """Convert exception to standard error response."""
        return ErrorResponse(code=self.code, message=self.message, details=self.details)


class ValidationError(UltraAIException):
    """Raised when input validation fails."""

    def __init__(
        self,
        message: str = "Validation error",
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            code="VALIDATION_ERROR", message=message, status_code=422, details=details
        )


class AuthenticationError(UltraAIException):
    """Raised when authentication fails."""

    def __init__(
        self,
        message: str = "Authentication failed",
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            code="AUTHENTICATION_ERROR",
            message=message,
            status_code=401,
            details=details,
        )


class AuthorizationError(UltraAIException):
    """Raised when authorization fails."""

    def __init__(
        self,
        message: str = "Not authorized",
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            code="AUTHORIZATION_ERROR",
            message=message,
            status_code=403,
            details=details,
        )


class NotFoundError(UltraAIException):
    """Raised when a resource is not found."""

    def __init__(
        self,
        message: str = "Resource not found",
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            code="NOT_FOUND", message=message, status_code=404, details=details
        )


class ConflictError(UltraAIException):
    """Raised when there's a conflict with existing resources."""

    def __init__(
        self,
        message: str = "Resource conflict",
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            code="CONFLICT", message=message, status_code=409, details=details
        )


class InternalServerError(UltraAIException):
    """Raised when an unexpected error occurs."""

    def __init__(
        self,
        message: str = "Internal server error",
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            code="INTERNAL_ERROR", message=message, status_code=500, details=details
        )
