"""
Domain-specific exception classes for the UltraAI backend.

This module defines specialized exception classes for different domains of the application,
providing consistent error handling with domain-specific context and metadata.
"""

from typing import Any, Dict, List, Optional, Union

from backend.models.base_models import ErrorDetail
from backend.utils.unified_error_handler import (
    ErrorCategory,
    ErrorCode,
    UltraBaseException,
)

#
# Authentication and Authorization Exceptions
#


class AuthenticationException(UltraBaseException):
    """Exception raised when authentication fails"""

    def __init__(
        self,
        message: str = "Authentication failed",
        code: str = ErrorCode.UNAUTHORIZED,
        details: Optional[Union[List[ErrorDetail], Dict[str, Any], str]] = None,
        auth_type: Optional[str] = None,
    ):
        """
        Initialize a new AuthenticationException

        Args:
            message: Human-readable error message
            code: Error code for programmatic handling
            details: Additional details about the error
            auth_type: The type of authentication that failed (e.g., "jwt", "api_key")
        """
        if auth_type:
            if details is None:
                details = {"auth_type": auth_type}
            elif isinstance(details, dict):
                details["auth_type"] = auth_type

        super().__init__(
            message=message,
            code=code,
            details=details,
        )


class AuthorizationException(UltraBaseException):
    """Exception raised when a user is not authorized to perform an action"""

    def __init__(
        self,
        message: str = "You are not authorized to perform this action",
        code: str = ErrorCode.FORBIDDEN,
        details: Optional[Union[List[ErrorDetail], Dict[str, Any], str]] = None,
        required_permission: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
    ):
        """
        Initialize a new AuthorizationException

        Args:
            message: Human-readable error message
            code: Error code for programmatic handling
            details: Additional details about the error
            required_permission: The permission that was required
            resource_type: The type of resource being accessed
            resource_id: The ID of the resource being accessed
        """
        auth_details = {}

        if required_permission:
            auth_details["required_permission"] = required_permission

        if resource_type:
            auth_details["resource_type"] = resource_type

        if resource_id:
            auth_details["resource_id"] = resource_id

        if auth_details:
            if details is None:
                details = auth_details
            elif isinstance(details, dict):
                details.update(auth_details)

        super().__init__(
            message=message,
            code=code,
            details=details,
        )


class InvalidTokenException(AuthenticationException):
    """Exception raised when a token is invalid"""

    def __init__(
        self,
        message: str = "Invalid token",
        details: Optional[Union[List[ErrorDetail], Dict[str, Any], str]] = None,
        token_type: str = "access",
    ):
        super().__init__(
            message=message,
            code=ErrorCode.INVALID_TOKEN,
            details=details,
            auth_type=f"{token_type}_token",
        )


class ExpiredTokenException(AuthenticationException):
    """Exception raised when a token has expired"""

    def __init__(
        self,
        message: str = "Token has expired",
        details: Optional[Union[List[ErrorDetail], Dict[str, Any], str]] = None,
        token_type: str = "access",
        expiry_time: Optional[str] = None,
    ):
        token_details = {"token_type": token_type}

        if expiry_time:
            token_details["expiry_time"] = expiry_time

        if details is None:
            details = token_details
        elif isinstance(details, dict):
            details.update(token_details)

        super().__init__(
            message=message,
            code=ErrorCode.EXPIRED_TOKEN,
            details=details,
            auth_type=f"{token_type}_token",
        )


class MissingTokenException(AuthenticationException):
    """Exception raised when a token is missing"""

    def __init__(
        self,
        message: str = "Authorization token is missing",
        token_type: str = "access",
    ):
        super().__init__(
            message=message,
            code=ErrorCode.MISSING_TOKEN,
            details={"token_type": token_type},
            auth_type=f"{token_type}_token",
        )


#
# Rate Limiting Exceptions
#


class RateLimitException(UltraBaseException):
    """Exception raised when a rate limit is exceeded"""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        code: str = ErrorCode.RATE_LIMIT_EXCEEDED,
        details: Optional[Union[List[ErrorDetail], Dict[str, Any], str]] = None,
        limit: Optional[int] = None,
        period: Optional[str] = None,
        retry_after: Optional[int] = None,
    ):
        """
        Initialize a new RateLimitException

        Args:
            message: Human-readable error message
            code: Error code for programmatic handling
            details: Additional details about the error
            limit: The rate limit that was exceeded
            period: The time period for the rate limit (e.g., "1m", "1h")
            retry_after: The number of seconds after which the client can retry
        """
        rate_limit_details = {}

        if limit:
            rate_limit_details["limit"] = limit

        if period:
            rate_limit_details["period"] = period

        if retry_after:
            rate_limit_details["retry_after"] = retry_after

        if rate_limit_details:
            if details is None:
                details = rate_limit_details
            elif isinstance(details, dict):
                details.update(rate_limit_details)

        super().__init__(
            message=message,
            code=code,
            details=details,
        )


class QuotaExceededException(UltraBaseException):
    """Exception raised when a quota is exceeded"""

    def __init__(
        self,
        message: str = "Quota exceeded",
        details: Optional[Union[List[ErrorDetail], Dict[str, Any], str]] = None,
        quota_type: Optional[str] = None,
        current_usage: Optional[int] = None,
        quota_limit: Optional[int] = None,
        reset_time: Optional[str] = None,
    ):
        """
        Initialize a new QuotaExceededException

        Args:
            message: Human-readable error message
            details: Additional details about the error
            quota_type: The type of quota that was exceeded
            current_usage: The current usage count
            quota_limit: The quota limit
            reset_time: When the quota will reset
        """
        quota_details = {}

        if quota_type:
            quota_details["quota_type"] = quota_type

        if current_usage is not None:
            quota_details["current_usage"] = current_usage

        if quota_limit is not None:
            quota_details["quota_limit"] = quota_limit

        if reset_time:
            quota_details["reset_time"] = reset_time

        if quota_details:
            if details is None:
                details = quota_details
            elif isinstance(details, dict):
                details.update(quota_details)

        super().__init__(
            message=message,
            code=ErrorCode.QUOTA_EXCEEDED,
            details=details,
        )


#
# Validation Exceptions
#


class ValidationException(UltraBaseException):
    """Exception raised when validation fails"""

    def __init__(
        self,
        message: str = "Validation error",
        code: str = ErrorCode.VALIDATION_ERROR,
        details: Optional[Union[List[ErrorDetail], Dict[str, Any], str]] = None,
        field_errors: Optional[Dict[str, str]] = None,
    ):
        """
        Initialize a new ValidationException

        Args:
            message: Human-readable error message
            code: Error code for programmatic handling
            details: Additional details about the error
            field_errors: Dictionary mapping field names to error messages
        """
        if field_errors:
            validation_details = {"field_errors": field_errors}

            if details is None:
                details = validation_details
            elif isinstance(details, dict):
                details.update(validation_details)

        super().__init__(
            message=message,
            code=code,
            details=details,
        )


class InvalidInputException(ValidationException):
    """Exception raised when input is invalid"""

    def __init__(
        self,
        message: str = "Invalid input",
        details: Optional[Union[List[ErrorDetail], Dict[str, Any], str]] = None,
        field: Optional[str] = None,
        value: Optional[Any] = None,
        reason: Optional[str] = None,
    ):
        """
        Initialize a new InvalidInputException

        Args:
            message: Human-readable error message
            details: Additional details about the error
            field: The field that is invalid
            value: The invalid value
            reason: The reason the value is invalid
        """
        input_details = {}
        field_errors = {}

        if field:
            input_details["field"] = field

        if value is not None:
            input_details["value"] = str(value)

        if reason:
            input_details["reason"] = reason

            if field:
                field_errors[field] = reason

        if input_details:
            if details is None:
                details = input_details
            elif isinstance(details, dict):
                details.update(input_details)

        super().__init__(
            message=message,
            code=ErrorCode.INVALID_INPUT,
            details=details,
            field_errors=field_errors,
        )


class MissingFieldException(ValidationException):
    """Exception raised when a required field is missing"""

    def __init__(
        self,
        field: str,
        message: Optional[str] = None,
    ):
        """
        Initialize a new MissingFieldException

        Args:
            field: The field that is missing
            message: Human-readable error message
        """
        message = message or f"Required field '{field}' is missing"
        field_errors = {field: "This field is required"}

        super().__init__(
            message=message,
            code=ErrorCode.MISSING_FIELD,
            details={"field": field},
            field_errors=field_errors,
        )


#
# Resource Exceptions
#


class ResourceNotFoundException(UltraBaseException):
    """Exception raised when a requested resource is not found"""

    def __init__(
        self,
        resource_type: str,
        resource_id: str,
        message: Optional[str] = None,
        code: str = ErrorCode.RESOURCE_NOT_FOUND,
        details: Optional[Union[List[ErrorDetail], Dict[str, Any], str]] = None,
    ):
        """
        Initialize a new ResourceNotFoundException

        Args:
            resource_type: The type of resource that was not found
            resource_id: The ID of the resource that was not found
            message: Human-readable error message
            code: Error code for programmatic handling
            details: Additional details about the error
        """
        message = message or f"{resource_type} with ID {resource_id} not found"
        resource_details = {
            "resource_type": resource_type,
            "resource_id": resource_id,
        }

        if details is None:
            details = resource_details
        elif isinstance(details, dict):
            details.update(resource_details)

        super().__init__(
            message=message,
            code=code,
            details=details,
        )


class ResourceAlreadyExistsException(UltraBaseException):
    """Exception raised when a resource already exists"""

    def __init__(
        self,
        resource_type: str,
        identifier: str,
        message: Optional[str] = None,
        details: Optional[Union[List[ErrorDetail], Dict[str, Any], str]] = None,
    ):
        """
        Initialize a new ResourceAlreadyExistsException

        Args:
            resource_type: The type of resource that already exists
            identifier: The identifier of the resource that already exists
            message: Human-readable error message
            details: Additional details about the error
        """
        message = (
            message or f"{resource_type} with identifier '{identifier}' already exists"
        )
        resource_details = {
            "resource_type": resource_type,
            "identifier": identifier,
        }

        if details is None:
            details = resource_details
        elif isinstance(details, dict):
            details.update(resource_details)

        super().__init__(
            message=message,
            code=ErrorCode.RESOURCE_EXISTS,
            details=details,
        )


class ResourceConflictException(UltraBaseException):
    """Exception raised when there is a conflict with a resource"""

    def __init__(
        self,
        resource_type: str,
        resource_id: str,
        message: Optional[str] = None,
        details: Optional[Union[List[ErrorDetail], Dict[str, Any], str]] = None,
        conflict_reason: Optional[str] = None,
    ):
        """
        Initialize a new ResourceConflictException

        Args:
            resource_type: The type of resource with the conflict
            resource_id: The ID of the resource with the conflict
            message: Human-readable error message
            details: Additional details about the error
            conflict_reason: The reason for the conflict
        """
        message = message or f"Conflict with {resource_type} {resource_id}"
        resource_details = {
            "resource_type": resource_type,
            "resource_id": resource_id,
        }

        if conflict_reason:
            resource_details["conflict_reason"] = conflict_reason

        if details is None:
            details = resource_details
        elif isinstance(details, dict):
            details.update(resource_details)

        super().__init__(
            message=message,
            code=ErrorCode.RESOURCE_CONFLICT,
            details=details,
        )


#
# Service Exceptions
#


class ServiceException(UltraBaseException):
    """Exception raised when there is an error with a service"""

    def __init__(
        self,
        service_name: str,
        message: Optional[str] = None,
        code: str = ErrorCode.SERVICE_UNAVAILABLE,
        details: Optional[Union[List[ErrorDetail], Dict[str, Any], str]] = None,
        original_exception: Optional[Exception] = None,
    ):
        """
        Initialize a new ServiceException

        Args:
            service_name: The name of the service
            message: Human-readable error message
            code: Error code for programmatic handling
            details: Additional details about the error
            original_exception: The original exception that caused this one
        """
        message = message or f"Error with service: {service_name}"
        service_details = {"service_name": service_name}

        if details is None:
            details = service_details
        elif isinstance(details, dict):
            details.update(service_details)

        super().__init__(
            message=message,
            code=code,
            details=details,
            original_exception=original_exception,
        )


class ServiceUnavailableException(ServiceException):
    """Exception raised when a service is unavailable"""

    def __init__(
        self,
        service_name: str,
        message: Optional[str] = None,
        details: Optional[Union[List[ErrorDetail], Dict[str, Any], str]] = None,
        retry_after: Optional[int] = None,
    ):
        """
        Initialize a new ServiceUnavailableException

        Args:
            service_name: The name of the service
            message: Human-readable error message
            details: Additional details about the error
            retry_after: The number of seconds after which the client can retry
        """
        message = message or f"Service {service_name} is currently unavailable"
        service_details = {}

        if retry_after:
            service_details["retry_after"] = retry_after

        super().__init__(
            service_name=service_name,
            message=message,
            code=ErrorCode.SERVICE_UNAVAILABLE,
            details=details,
        )


class ExternalServiceException(ServiceException):
    """Exception raised when there is an error with an external service"""

    def __init__(
        self,
        service_name: str,
        message: Optional[str] = None,
        details: Optional[Union[List[ErrorDetail], Dict[str, Any], str]] = None,
        status_code: Optional[int] = None,
        original_error: Optional[Exception] = None,
    ):
        """
        Initialize a new ExternalServiceException

        Args:
            service_name: The name of the external service
            message: Human-readable error message
            details: Additional details about the error
            status_code: The HTTP status code returned by the external service
            original_error: The original error from the external service
        """
        message = message or f"Error from external service: {service_name}"
        service_details = {}

        if status_code:
            service_details["status_code"] = status_code

        if original_error:
            service_details["original_error"] = str(original_error)

        if service_details:
            if details is None:
                details = service_details
            elif isinstance(details, dict):
                details.update(service_details)

        super().__init__(
            service_name=service_name,
            message=message,
            code=ErrorCode.EXTERNAL_SERVICE_ERROR,
            details=details,
            original_exception=original_error,
        )


class TimeoutException(ServiceException):
    """Exception raised when a request times out"""

    def __init__(
        self,
        service_name: str,
        message: Optional[str] = None,
        details: Optional[Union[List[ErrorDetail], Dict[str, Any], str]] = None,
        timeout_seconds: Optional[float] = None,
    ):
        """
        Initialize a new TimeoutException

        Args:
            service_name: The name of the service that timed out
            message: Human-readable error message
            details: Additional details about the error
            timeout_seconds: The timeout in seconds
        """
        message = message or f"Request to {service_name} timed out"
        timeout_details = {}

        if timeout_seconds:
            timeout_details["timeout_seconds"] = timeout_seconds

        if timeout_details:
            if details is None:
                details = timeout_details
            elif isinstance(details, dict):
                details.update(timeout_details)

        super().__init__(
            service_name=service_name,
            message=message,
            code=ErrorCode.TIMEOUT,
            details=details,
        )


class CircuitOpenException(ServiceException):
    """Exception raised when a circuit breaker is open"""

    def __init__(
        self,
        service_name: str,
        message: Optional[str] = None,
        details: Optional[Union[List[ErrorDetail], Dict[str, Any], str]] = None,
        retry_after: Optional[int] = None,
    ):
        """
        Initialize a new CircuitOpenException

        Args:
            service_name: The name of the service with the open circuit
            message: Human-readable error message
            details: Additional details about the error
            retry_after: The number of seconds after which the client can retry
        """
        message = (
            message
            or f"Service {service_name} is temporarily unavailable due to circuit breaker"
        )
        circuit_details = {}

        if retry_after:
            circuit_details["retry_after"] = retry_after

        if circuit_details:
            if details is None:
                details = circuit_details
            elif isinstance(details, dict):
                details.update(circuit_details)

        super().__init__(
            service_name=service_name,
            message=message,
            code=ErrorCode.CIRCUIT_OPEN,
            details=details,
        )


#
# Database Exceptions
#


class DatabaseException(UltraBaseException):
    """Exception raised when there is a database error"""

    def __init__(
        self,
        message: str = "Database error",
        code: str = ErrorCode.DATABASE_ERROR,
        details: Optional[Union[List[ErrorDetail], Dict[str, Any], str]] = None,
        operation: Optional[str] = None,
        table: Optional[str] = None,
        original_exception: Optional[Exception] = None,
    ):
        """
        Initialize a new DatabaseException

        Args:
            message: Human-readable error message
            code: Error code for programmatic handling
            details: Additional details about the error
            operation: The database operation that failed
            table: The database table involved
            original_exception: The original exception that caused this one
        """
        db_details = {}

        if operation:
            db_details["operation"] = operation

        if table:
            db_details["table"] = table

        if db_details:
            if details is None:
                details = db_details
            elif isinstance(details, dict):
                details.update(db_details)

        super().__init__(
            message=message,
            code=code,
            details=details,
            original_exception=original_exception,
        )


class DataIntegrityException(DatabaseException):
    """Exception raised when there is a data integrity error"""

    def __init__(
        self,
        message: str = "Data integrity error",
        details: Optional[Union[List[ErrorDetail], Dict[str, Any], str]] = None,
        constraint: Optional[str] = None,
    ):
        """
        Initialize a new DataIntegrityException

        Args:
            message: Human-readable error message
            details: Additional details about the error
            constraint: The constraint that was violated
        """
        integrity_details = {}

        if constraint:
            integrity_details["constraint"] = constraint

        if integrity_details:
            if details is None:
                details = integrity_details
            elif isinstance(details, dict):
                details.update(integrity_details)

        super().__init__(
            message=message,
            code=ErrorCode.DATA_INTEGRITY_ERROR,
            details=details,
        )


#
# LLM/Model Exceptions
#


class ModelException(UltraBaseException):
    """Exception raised when there is an error with a model"""

    def __init__(
        self,
        model_name: str,
        message: Optional[str] = None,
        code: str = ErrorCode.MODEL_ERROR,
        details: Optional[Union[List[ErrorDetail], Dict[str, Any], str]] = None,
        provider: Optional[str] = None,
        original_exception: Optional[Exception] = None,
    ):
        """
        Initialize a new ModelException

        Args:
            model_name: The name of the model
            message: Human-readable error message
            code: Error code for programmatic handling
            details: Additional details about the error
            provider: The provider of the model
            original_exception: The original exception that caused this one
        """
        message = message or f"Error with model: {model_name}"
        model_details = {"model_name": model_name}

        if provider:
            model_details["provider"] = provider

        if model_details:
            if details is None:
                details = model_details
            elif isinstance(details, dict):
                details.update(model_details)

        super().__init__(
            message=message,
            code=code,
            details=details,
            original_exception=original_exception,
        )


class ModelUnavailableException(ModelException):
    """Exception raised when a model is unavailable"""

    def __init__(
        self,
        model_name: str,
        message: Optional[str] = None,
        details: Optional[Union[List[ErrorDetail], Dict[str, Any], str]] = None,
        provider: Optional[str] = None,
    ):
        """
        Initialize a new ModelUnavailableException

        Args:
            model_name: The name of the model
            message: Human-readable error message
            details: Additional details about the error
            provider: The provider of the model
        """
        message = message or f"Model {model_name} is currently unavailable"

        super().__init__(
            model_name=model_name,
            message=message,
            code=ErrorCode.MODEL_UNAVAILABLE,
            details=details,
            provider=provider,
        )


class ModelTimeoutException(ModelException):
    """Exception raised when a model request times out"""

    def __init__(
        self,
        model_name: str,
        message: Optional[str] = None,
        details: Optional[Union[List[ErrorDetail], Dict[str, Any], str]] = None,
        provider: Optional[str] = None,
        timeout_seconds: Optional[float] = None,
    ):
        """
        Initialize a new ModelTimeoutException

        Args:
            model_name: The name of the model
            message: Human-readable error message
            details: Additional details about the error
            provider: The provider of the model
            timeout_seconds: The timeout in seconds
        """
        message = message or f"Request to model {model_name} timed out"
        timeout_details = {}

        if timeout_seconds:
            timeout_details["timeout_seconds"] = timeout_seconds

        if timeout_details:
            if details is None:
                details = timeout_details
            elif isinstance(details, dict):
                details.update(timeout_details)

        super().__init__(
            model_name=model_name,
            message=message,
            code=ErrorCode.MODEL_TIMEOUT,
            details=details,
            provider=provider,
        )


class ModelContentFilterException(ModelException):
    """Exception raised when content is filtered by a model's content filter"""

    def __init__(
        self,
        model_name: str,
        message: Optional[str] = None,
        details: Optional[Union[List[ErrorDetail], Dict[str, Any], str]] = None,
        provider: Optional[str] = None,
        filter_type: Optional[str] = None,
    ):
        """
        Initialize a new ModelContentFilterException

        Args:
            model_name: The name of the model
            message: Human-readable error message
            details: Additional details about the error
            provider: The provider of the model
            filter_type: The type of content filter that was triggered
        """
        message = message or f"Content filtered by model {model_name}"
        filter_details = {}

        if filter_type:
            filter_details["filter_type"] = filter_type

        if filter_details:
            if details is None:
                details = filter_details
            elif isinstance(details, dict):
                details.update(filter_details)

        super().__init__(
            model_name=model_name,
            message=message,
            code=ErrorCode.MODEL_CONTENT_FILTER,
            details=details,
            provider=provider,
        )


class ModelContextLengthException(ModelException):
    """Exception raised when a model's context length is exceeded"""

    def __init__(
        self,
        model_name: str,
        message: Optional[str] = None,
        details: Optional[Union[List[ErrorDetail], Dict[str, Any], str]] = None,
        provider: Optional[str] = None,
        context_length: Optional[int] = None,
        token_count: Optional[int] = None,
    ):
        """
        Initialize a new ModelContextLengthException

        Args:
            model_name: The name of the model
            message: Human-readable error message
            details: Additional details about the error
            provider: The provider of the model
            context_length: The maximum context length of the model
            token_count: The token count of the request
        """
        message = message or f"Context length exceeded for model {model_name}"
        context_details = {}

        if context_length:
            context_details["context_length"] = context_length

        if token_count:
            context_details["token_count"] = token_count

        if context_details:
            if details is None:
                details = context_details
            elif isinstance(details, dict):
                details.update(context_details)

        super().__init__(
            model_name=model_name,
            message=message,
            code=ErrorCode.MODEL_CONTEXT_LENGTH,
            details=details,
            provider=provider,
        )


#
# Document Exceptions
#


class DocumentException(UltraBaseException):
    """Exception raised when there is an error with a document"""

    def __init__(
        self,
        document_id: Optional[str] = None,
        message: str = "Document error",
        code: str = ErrorCode.DOCUMENT_ERROR,
        details: Optional[Union[List[ErrorDetail], Dict[str, Any], str]] = None,
    ):
        """
        Initialize a new DocumentException

        Args:
            document_id: The ID of the document
            message: Human-readable error message
            code: Error code for programmatic handling
            details: Additional details about the error
        """
        document_details = {}

        if document_id:
            document_details["document_id"] = document_id

        if document_details:
            if details is None:
                details = document_details
            elif isinstance(details, dict):
                details.update(document_details)

        super().__init__(
            message=message,
            code=code,
            details=details,
        )


class DocumentNotFoundException(DocumentException):
    """Exception raised when a document is not found"""

    def __init__(
        self,
        document_id: str,
        message: Optional[str] = None,
        details: Optional[Union[List[ErrorDetail], Dict[str, Any], str]] = None,
    ):
        """
        Initialize a new DocumentNotFoundException

        Args:
            document_id: The ID of the document
            message: Human-readable error message
            details: Additional details about the error
        """
        message = message or f"Document with ID {document_id} not found"

        super().__init__(
            document_id=document_id,
            message=message,
            code=ErrorCode.DOCUMENT_NOT_FOUND,
            details=details,
        )


class DocumentFormatException(DocumentException):
    """Exception raised when a document has an invalid format"""

    def __init__(
        self,
        document_id: Optional[str] = None,
        format: Optional[str] = None,
        message: Optional[str] = None,
        details: Optional[Union[List[ErrorDetail], Dict[str, Any], str]] = None,
    ):
        """
        Initialize a new DocumentFormatException

        Args:
            document_id: The ID of the document
            format: The invalid format
            message: Human-readable error message
            details: Additional details about the error
        """
        if format:
            message = message or f"Invalid document format: {format}"
            format_details = {"format": format}

            if details is None:
                details = format_details
            elif isinstance(details, dict):
                details.update(format_details)
        else:
            message = message or "Invalid document format"

        super().__init__(
            document_id=document_id,
            message=message,
            code=ErrorCode.DOCUMENT_FORMAT_ERROR,
            details=details,
        )


class DocumentTooLargeException(DocumentException):
    """Exception raised when a document is too large"""

    def __init__(
        self,
        size: Optional[int] = None,
        max_size: Optional[int] = None,
        document_id: Optional[str] = None,
        message: Optional[str] = None,
        details: Optional[Union[List[ErrorDetail], Dict[str, Any], str]] = None,
    ):
        """
        Initialize a new DocumentTooLargeException

        Args:
            size: The size of the document
            max_size: The maximum allowed size
            document_id: The ID of the document
            message: Human-readable error message
            details: Additional details about the error
        """
        size_details = {}

        if size:
            size_details["size"] = size

        if max_size:
            size_details["max_size"] = max_size
            message = (
                message
                or f"Document size ({size} bytes) exceeds maximum allowed size ({max_size} bytes)"
            )
        else:
            message = message or "Document is too large"

        if size_details:
            if details is None:
                details = size_details
            elif isinstance(details, dict):
                details.update(size_details)

        super().__init__(
            document_id=document_id,
            message=message,
            code=ErrorCode.DOCUMENT_TOO_LARGE,
            details=details,
        )


class DocumentProcessingException(DocumentException):
    """Exception raised when there is an error processing a document"""

    def __init__(
        self,
        document_id: str,
        message: Optional[str] = None,
        details: Optional[Union[List[ErrorDetail], Dict[str, Any], str]] = None,
        processing_stage: Optional[str] = None,
    ):
        """
        Initialize a new DocumentProcessingException

        Args:
            document_id: The ID of the document
            message: Human-readable error message
            details: Additional details about the error
            processing_stage: The stage of processing where the error occurred
        """
        message = message or f"Error processing document {document_id}"
        processing_details = {}

        if processing_stage:
            processing_details["processing_stage"] = processing_stage

        if processing_details:
            if details is None:
                details = processing_details
            elif isinstance(details, dict):
                details.update(processing_details)

        super().__init__(
            document_id=document_id,
            message=message,
            code=ErrorCode.DOCUMENT_PROCESSING_ERROR,
            details=details,
        )


#
# Payment and Pricing Exceptions
#


class PaymentException(UltraBaseException):
    """Exception raised when there is a payment error"""

    def __init__(
        self,
        message: str = "Payment error",
        code: str = ErrorCode.PAYMENT_REQUIRED,
        details: Optional[Union[List[ErrorDetail], Dict[str, Any], str]] = None,
    ):
        """
        Initialize a new PaymentException

        Args:
            message: Human-readable error message
            code: Error code for programmatic handling
            details: Additional details about the error
        """
        super().__init__(
            message=message,
            code=code,
            details=details,
        )


class PaymentRequiredException(PaymentException):
    """Exception raised when payment is required"""

    def __init__(
        self,
        message: str = "Payment required",
        details: Optional[Union[List[ErrorDetail], Dict[str, Any], str]] = None,
        required_amount: Optional[float] = None,
        currency: Optional[str] = None,
    ):
        """
        Initialize a new PaymentRequiredException

        Args:
            message: Human-readable error message
            details: Additional details about the error
            required_amount: The amount required
            currency: The currency of the amount
        """
        payment_details = {}

        if required_amount is not None:
            payment_details["required_amount"] = required_amount

        if currency:
            payment_details["currency"] = currency

        if payment_details:
            if details is None:
                details = payment_details
            elif isinstance(details, dict):
                details.update(payment_details)

        super().__init__(
            message=message,
            code=ErrorCode.PAYMENT_REQUIRED,
            details=details,
        )


class InsufficientFundsException(PaymentException):
    """Exception raised when there are insufficient funds"""

    def __init__(
        self,
        message: str = "Insufficient funds",
        details: Optional[Union[List[ErrorDetail], Dict[str, Any], str]] = None,
        available_funds: Optional[float] = None,
        required_amount: Optional[float] = None,
        currency: Optional[str] = None,
    ):
        """
        Initialize a new InsufficientFundsException

        Args:
            message: Human-readable error message
            details: Additional details about the error
            available_funds: The available funds
            required_amount: The amount required
            currency: The currency of the amounts
        """
        funds_details = {}

        if available_funds is not None:
            funds_details["available_funds"] = available_funds

        if required_amount is not None:
            funds_details["required_amount"] = required_amount

        if currency:
            funds_details["currency"] = currency

        if (
            funds_details
            and available_funds is not None
            and required_amount is not None
        ):
            message = (
                message
                or f"Insufficient funds. Available: {available_funds} {currency or 'units'}, "
                f"Required: {required_amount} {currency or 'units'}"
            )

        if funds_details:
            if details is None:
                details = funds_details
            elif isinstance(details, dict):
                details.update(funds_details)

        super().__init__(
            message=message,
            code=ErrorCode.INSUFFICIENT_FUNDS,
            details=details,
        )


class SubscriptionRequiredException(PaymentException):
    """Exception raised when a subscription is required"""

    def __init__(
        self,
        message: str = "Subscription required",
        details: Optional[Union[List[ErrorDetail], Dict[str, Any], str]] = None,
        feature: Optional[str] = None,
        subscription_level: Optional[str] = None,
    ):
        """
        Initialize a new SubscriptionRequiredException

        Args:
            message: Human-readable error message
            details: Additional details about the error
            feature: The feature that requires a subscription
            subscription_level: The required subscription level
        """
        subscription_details = {}

        if feature:
            subscription_details["feature"] = feature
            message = message or f"Subscription required to access {feature}"

        if subscription_level:
            subscription_details["subscription_level"] = subscription_level
            if feature:
                message = (
                    message
                    or f"Subscription level {subscription_level} required to access {feature}"
                )
            else:
                message = message or f"Subscription level {subscription_level} required"

        if subscription_details:
            if details is None:
                details = subscription_details
            elif isinstance(details, dict):
                details.update(subscription_details)

        super().__init__(
            message=message,
            code=ErrorCode.SUBSCRIPTION_REQUIRED,
            details=details,
        )


class SubscriptionExpiredException(PaymentException):
    """Exception raised when a subscription has expired"""

    def __init__(
        self,
        message: str = "Subscription has expired",
        details: Optional[Union[List[ErrorDetail], Dict[str, Any], str]] = None,
        expiry_date: Optional[str] = None,
        subscription_level: Optional[str] = None,
    ):
        """
        Initialize a new SubscriptionExpiredException

        Args:
            message: Human-readable error message
            details: Additional details about the error
            expiry_date: The date the subscription expired
            subscription_level: The subscription level that expired
        """
        subscription_details = {}

        if expiry_date:
            subscription_details["expiry_date"] = expiry_date

        if subscription_level:
            subscription_details["subscription_level"] = subscription_level
            message = message or f"{subscription_level} subscription has expired"

        if subscription_details:
            if details is None:
                details = subscription_details
            elif isinstance(details, dict):
                details.update(subscription_details)

        super().__init__(
            message=message,
            code=ErrorCode.SUBSCRIPTION_EXPIRED,
            details=details,
        )
