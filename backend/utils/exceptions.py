"""
Custom exception classes for the UltraAI backend.

This module defines a hierarchy of exception classes that provide consistent
error handling and error responses throughout the application.
"""

from http import HTTPStatus
from typing import Any, Dict, List, Optional, Union


class UltraBaseException(Exception):
    """Base exception class for all Ultra custom exceptions"""

    def __init__(
        self,
        message: str,
        status_code: int = HTTPStatus.INTERNAL_SERVER_ERROR,
        code: str = "internal_error",
        details: Optional[Union[List[Dict[str, Any]], Dict[str, Any]]] = None,
    ):
        """
        Initialize a new UltraBaseException

        Args:
            message: Human-readable error message
            status_code: HTTP status code to return
            code: Error code for programmatic handling
            details: Additional details about the error
        """
        self.message = message
        self.status_code = status_code
        self.code = code
        self.details = details
        super().__init__(self.message)


# Authentication and Authorization Exceptions
class AuthenticationException(UltraBaseException):
    """Exception raised when authentication fails"""

    def __init__(
        self,
        message: str = "Authentication failed",
        code: str = "authentication_error",
        details: Optional[Union[List[Dict[str, Any]], Dict[str, Any]]] = None,
    ):
        super().__init__(
            message=message,
            status_code=HTTPStatus.UNAUTHORIZED,
            code=code,
            details=details,
        )


class AuthorizationException(UltraBaseException):
    """Exception raised when a user is not authorized to perform an action"""

    def __init__(
        self,
        message: str = "You are not authorized to perform this action",
        code: str = "authorization_error",
        details: Optional[Union[List[Dict[str, Any]], Dict[str, Any]]] = None,
    ):
        super().__init__(
            message=message,
            status_code=HTTPStatus.FORBIDDEN,
            code=code,
            details=details,
        )


class RateLimitException(UltraBaseException):
    """Exception raised when a rate limit is exceeded"""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        code: str = "rate_limit_exceeded",
        retry_after: Optional[int] = None,
        details: Optional[Union[List[Dict[str, Any]], Dict[str, Any]]] = None,
    ):
        if retry_after:
            details = details or {}
            if isinstance(details, list):
                details.append({"retry_after": retry_after})
            else:
                details["retry_after"] = retry_after

        super().__init__(
            message=message,
            status_code=HTTPStatus.TOO_MANY_REQUESTS,
            code=code,
            details=details,
        )
        self.retry_after = retry_after


# Resource Exceptions
class ResourceNotFoundException(UltraBaseException):
    """Exception raised when a requested resource is not found"""

    def __init__(
        self,
        resource_type: str,
        resource_id: str,
        message: Optional[str] = None,
        code: str = "resource_not_found",
        details: Optional[Union[List[Dict[str, Any]], Dict[str, Any]]] = None,
    ):
        message = message or f"{resource_type} with ID {resource_id} not found"
        resource_details = {
            "resource_type": resource_type,
            "resource_id": resource_id,
        }

        if details:
            if isinstance(details, list):
                details.append(resource_details)
            else:
                details.update(resource_details)
        else:
            details = resource_details

        super().__init__(
            message=message,
            status_code=HTTPStatus.NOT_FOUND,
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
        code: str = "resource_already_exists",
        details: Optional[Union[List[Dict[str, Any]], Dict[str, Any]]] = None,
    ):
        message = message or f"{resource_type} with identifier {identifier} already exists"
        resource_details = {
            "resource_type": resource_type,
            "identifier": identifier,
        }

        if details:
            if isinstance(details, list):
                details.append(resource_details)
            else:
                details.update(resource_details)
        else:
            details = resource_details

        super().__init__(
            message=message,
            status_code=HTTPStatus.CONFLICT,
            code=code,
            details=details,
        )


# Validation Exceptions
class ValidationException(UltraBaseException):
    """Exception raised when validation fails"""

    def __init__(
        self,
        message: str = "Validation error",
        code: str = "validation_error",
        field_errors: Optional[Dict[str, str]] = None,
        details: Optional[Union[List[Dict[str, Any]], Dict[str, Any]]] = None,
    ):
        if field_errors:
            validation_details = {"field_errors": field_errors}
            if details:
                if isinstance(details, list):
                    details.append(validation_details)
                else:
                    details.update(validation_details)
            else:
                details = validation_details

        super().__init__(
            message=message,
            status_code=HTTPStatus.BAD_REQUEST,
            code=code,
            details=details,
        )


# Service Exceptions
class ServiceUnavailableException(UltraBaseException):
    """Exception raised when a required service is unavailable"""

    def __init__(
        self,
        service_name: str,
        message: Optional[str] = None,
        code: str = "service_unavailable",
        retry_after: Optional[int] = None,
        details: Optional[Union[List[Dict[str, Any]], Dict[str, Any]]] = None,
    ):
        message = message or f"Service {service_name} is currently unavailable"
        service_details = {"service_name": service_name}

        if retry_after:
            service_details["retry_after"] = retry_after

        if details:
            if isinstance(details, list):
                details.append(service_details)
            else:
                details.update(service_details)
        else:
            details = service_details

        super().__init__(
            message=message,
            status_code=HTTPStatus.SERVICE_UNAVAILABLE,
            code=code,
            details=details,
        )
        self.retry_after = retry_after


class ThirdPartyServiceException(UltraBaseException):
    """Exception raised when there is an error from a third-party service"""

    def __init__(
        self,
        service_name: str,
        message: Optional[str] = None,
        original_error: Optional[Exception] = None,
        code: str = "third_party_service_error",
        status_code: int = HTTPStatus.BAD_GATEWAY,
        details: Optional[Union[List[Dict[str, Any]], Dict[str, Any]]] = None,
    ):
        message = message or f"Error from third-party service: {service_name}"
        service_details = {"service_name": service_name}

        if original_error:
            service_details["original_error"] = str(original_error)

        if details:
            if isinstance(details, list):
                details.append(service_details)
            else:
                details.update(service_details)
        else:
            details = service_details

        super().__init__(
            message=message,
            status_code=status_code,
            code=code,
            details=details,
        )


# Database Exceptions
class DatabaseException(UltraBaseException):
    """Exception raised when there is a database error"""

    def __init__(
        self,
        message: str = "Database error",
        code: str = "database_error",
        operation: Optional[str] = None,
        details: Optional[Union[List[Dict[str, Any]], Dict[str, Any]]] = None,
    ):
        if operation:
            db_details = {"operation": operation}
            if details:
                if isinstance(details, list):
                    details.append(db_details)
                else:
                    details.update(db_details)
            else:
                details = db_details

        super().__init__(
            message=message,
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            code=code,
            details=details,
        )


class DatabaseConnectionException(DatabaseException):
    """Exception raised when there is a database connection error"""

    def __init__(
        self,
        message: str = "Database connection error",
        code: str = "database_connection_error",
        details: Optional[Union[List[Dict[str, Any]], Dict[str, Any]]] = None,
    ):
        super().__init__(
            message=message,
            code=code,
            details=details,
        )


# Model/LLM Exceptions
class ModelException(UltraBaseException):
    """Exception raised when there is an error with a model"""

    def __init__(
        self,
        model_name: str,
        message: Optional[str] = None,
        code: str = "model_error",
        status_code: int = HTTPStatus.INTERNAL_SERVER_ERROR,
        details: Optional[Union[List[Dict[str, Any]], Dict[str, Any]]] = None,
    ):
        message = message or f"Error with model: {model_name}"
        model_details = {"model_name": model_name}

        if details:
            if isinstance(details, list):
                details.append(model_details)
            else:
                details.update(model_details)
        else:
            details = model_details

        super().__init__(
            message=message,
            status_code=status_code,
            code=code,
            details=details,
        )


class ModelUnavailableException(ModelException):
    """Exception raised when a model is unavailable"""

    def __init__(
        self,
        model_name: str,
        message: Optional[str] = None,
        code: str = "model_unavailable",
        details: Optional[Union[List[Dict[str, Any]], Dict[str, Any]]] = None,
    ):
        message = message or f"Model {model_name} is currently unavailable"
        super().__init__(
            model_name=model_name,
            message=message,
            code=code,
            status_code=HTTPStatus.SERVICE_UNAVAILABLE,
            details=details,
        )


# Document processing exceptions
class DocumentProcessingException(UltraBaseException):
    """Exception raised when there is an error processing a document"""

    def __init__(
        self,
        document_id: str,
        message: Optional[str] = None,
        code: str = "document_processing_error",
        details: Optional[Union[List[Dict[str, Any]], Dict[str, Any]]] = None,
    ):
        message = message or f"Error processing document: {document_id}"
        document_details = {"document_id": document_id}

        if details:
            if isinstance(details, list):
                details.append(document_details)
            else:
                details.update(document_details)
        else:
            details = document_details

        super().__init__(
            message=message,
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            code=code,
            details=details,
        )


class DocumentFormatException(DocumentProcessingException):
    """Exception raised when a document has an invalid format"""

    def __init__(
        self,
        document_id: str,
        format: str,
        message: Optional[str] = None,
        code: str = "invalid_document_format",
        details: Optional[Union[List[Dict[str, Any]], Dict[str, Any]]] = None,
    ):
        message = message or f"Invalid document format: {format}"
        format_details = {"format": format}

        if details:
            if isinstance(details, list):
                details.append(format_details)
            else:
                details.update(format_details)
        else:
            details = format_details

        super().__init__(
            document_id=document_id,
            message=message,
            code=code,
            details=details,
        )


# Payment and pricing exceptions
class PaymentRequiredException(UltraBaseException):
    """Exception raised when payment is required"""

    def __init__(
        self,
        message: str = "Payment required",
        code: str = "payment_required",
        required_amount: Optional[float] = None,
        details: Optional[Union[List[Dict[str, Any]], Dict[str, Any]]] = None,
    ):
        if required_amount is not None:
            payment_details = {"required_amount": required_amount}
            if details:
                if isinstance(details, list):
                    details.append(payment_details)
                else:
                    details.update(payment_details)
            else:
                details = payment_details

        super().__init__(
            message=message,
            status_code=HTTPStatus.PAYMENT_REQUIRED,
            code=code,
            details=details,
        )


class QuotaExceededException(UltraBaseException):
    """Exception raised when a user's quota is exceeded"""

    def __init__(
        self,
        message: str = "Quota exceeded",
        code: str = "quota_exceeded",
        quota_type: Optional[str] = None,
        details: Optional[Union[List[Dict[str, Any]], Dict[str, Any]]] = None,
    ):
        if quota_type:
            quota_details = {"quota_type": quota_type}
            if details:
                if isinstance(details, list):
                    details.append(quota_details)
                else:
                    details.update(quota_details)
            else:
                details = quota_details

        super().__init__(
            message=message,
            status_code=HTTPStatus.FORBIDDEN,
            code=code,
            details=details,
        )