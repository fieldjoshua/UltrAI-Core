"""Custom error classes and error handling utilities."""

import logging
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class ErrorCategory(Enum):
    """Error categories for classification."""

    AUTHENTICATION = "AUTH"
    AUTHORIZATION = "AUTHZ"
    VALIDATION = "VAL"
    LLM_PROVIDER = "LLM"
    SYSTEM = "SYS"
    NETWORK = "NET"


class ErrorSeverity(Enum):
    """Error severity levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class BaseError(Exception):
    """Base error class for all custom exceptions."""

    category: ErrorCategory = ErrorCategory.SYSTEM
    default_message: str = "An error occurred"
    default_status_code: int = 500
    severity: ErrorSeverity = ErrorSeverity.MEDIUM

    def __init__(
        self,
        message: Optional[str] = None,
        code: Optional[str] = None,
        status_code: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
    ):
        self.message = message or self.default_message
        self.code = code or self._generate_code()
        self.status_code = status_code or self.default_status_code
        self.details = details or {}
        self.context = context or {}
        self.timestamp = datetime.utcnow().isoformat()

        super().__init__(self.message)

        # Log error with context
        self._log_error()

    def _generate_code(self) -> str:
        """Generate error code based on category."""
        base_code = f"{self.category.value}_001"
        return base_code

    def _log_error(self):
        """Log error with appropriate level."""
        log_data = {
            "error_code": self.code,
            "error_category": self.category.value,
            "error_message": self.message,
            "severity": self.severity.value,
            "status_code": self.status_code,
            "details": self.details,
            "context": self.context,
            "timestamp": self.timestamp,
        }

        if self.severity == ErrorSeverity.CRITICAL:
            logger.critical(log_data)
        elif self.severity == ErrorSeverity.HIGH:
            logger.error(log_data)
        elif self.severity == ErrorSeverity.MEDIUM:
            logger.warning(log_data)
        else:
            logger.info(log_data)

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for API responses."""
        return {
            "error": {
                "code": self.code,
                "message": self.message,
                "category": self.category.value,
                "details": self.details,
                "timestamp": self.timestamp,
            }
        }


# Authentication Errors
class AuthenticationError(BaseError):
    """Base class for authentication errors."""

    category = ErrorCategory.AUTHENTICATION
    default_message = "Authentication failed"
    default_status_code = 401
    severity = ErrorSeverity.MEDIUM


class InvalidCredentialsError(AuthenticationError):
    """Invalid username or password."""

    default_message = "Invalid credentials provided"

    def _generate_code(self) -> str:
        return "AUTH_001"


class TokenExpiredError(AuthenticationError):
    """JWT token has expired."""

    default_message = "Authentication token has expired"

    def _generate_code(self) -> str:
        return "AUTH_002"


class TokenInvalidError(AuthenticationError):
    """JWT token is invalid."""

    default_message = "Invalid authentication token"

    def _generate_code(self) -> str:
        return "AUTH_003"


class AccountLockedError(AuthenticationError):
    """User account is locked."""

    default_message = "Account has been locked"
    default_status_code = 423
    severity = ErrorSeverity.HIGH

    def _generate_code(self) -> str:
        return "AUTH_004"


# Authorization Errors
class AuthorizationError(BaseError):
    """Base class for authorization errors."""

    category = ErrorCategory.AUTHORIZATION
    default_message = "Access denied"
    default_status_code = 403
    severity = ErrorSeverity.MEDIUM


class InsufficientPermissionsError(AuthorizationError):
    """User lacks required permissions."""

    default_message = "Insufficient permissions for this action"

    def _generate_code(self) -> str:
        return "AUTHZ_001"


class ResourceAccessDeniedError(AuthorizationError):
    """Access to specific resource denied."""

    default_message = "Access to this resource is denied"

    def _generate_code(self) -> str:
        return "AUTHZ_002"


class ActionNotAllowedError(AuthorizationError):
    """Specific action not allowed."""

    default_message = "This action is not allowed"

    def _generate_code(self) -> str:
        return "AUTHZ_003"


# Validation Errors
class ValidationError(BaseError):
    """Base class for validation errors."""

    category = ErrorCategory.VALIDATION
    default_message = "Validation failed"
    default_status_code = 400
    severity = ErrorSeverity.LOW


class RequiredFieldMissingError(ValidationError):
    """Required field is missing."""

    default_message = "Required field is missing"

    def _generate_code(self) -> str:
        return "VAL_001"


class InvalidFormatError(ValidationError):
    """Invalid data format."""

    default_message = "Invalid format provided"

    def _generate_code(self) -> str:
        return "VAL_002"


class ValueOutOfRangeError(ValidationError):
    """Value is outside acceptable range."""

    default_message = "Value is out of acceptable range"

    def _generate_code(self) -> str:
        return "VAL_003"


class FileTypeNotSupportedError(ValidationError):
    """File type not supported."""

    default_message = "File type is not supported"

    def _generate_code(self) -> str:
        return "VAL_004"


# LLM Provider Errors
class LLMProviderError(BaseError):
    """Base class for LLM provider errors."""

    category = ErrorCategory.LLM_PROVIDER
    default_message = "LLM provider error"
    default_status_code = 503
    severity = ErrorSeverity.HIGH


class ProviderUnavailableError(LLMProviderError):
    """LLM provider is unavailable."""

    default_message = "LLM provider is currently unavailable"

    def _generate_code(self) -> str:
        return "LLM_001"


class RateLimitExceededError(LLMProviderError):
    """Rate limit exceeded."""

    default_message = "Rate limit exceeded for LLM provider"
    default_status_code = 429

    def _generate_code(self) -> str:
        return "LLM_002"


class TokenLimitExceededError(LLMProviderError):
    """Token limit exceeded."""

    default_message = "Token limit exceeded for this request"
    default_status_code = 400
    severity = ErrorSeverity.MEDIUM

    def _generate_code(self) -> str:
        return "LLM_003"


class InvalidModelError(LLMProviderError):
    """Invalid model specified."""

    default_message = "Invalid model specified"
    default_status_code = 400
    severity = ErrorSeverity.MEDIUM

    def _generate_code(self) -> str:
        return "LLM_004"


class ProviderTimeoutError(LLMProviderError):
    """Provider request timeout."""

    default_message = "Request to LLM provider timed out"
    default_status_code = 504

    def _generate_code(self) -> str:
        return "LLM_005"


# System Errors
class SystemError(BaseError):
    """Base class for system errors."""

    category = ErrorCategory.SYSTEM
    default_message = "Internal system error"
    default_status_code = 500
    severity = ErrorSeverity.HIGH


class RecoveryError(SystemError):
    """Error during recovery process."""
    
    default_message = "Recovery process failed"
    severity = ErrorSeverity.HIGH
    
    def _generate_code(self) -> str:
        return "SYS_005"


class InternalServerError(SystemError):
    """Generic internal server error."""

    default_message = "An internal server error occurred"
    severity = ErrorSeverity.CRITICAL

    def _generate_code(self) -> str:
        return "SYS_001"


class DatabaseUnavailableError(SystemError):
    """Database is unavailable."""

    default_message = "Database service is unavailable"
    default_status_code = 503
    severity = ErrorSeverity.CRITICAL

    def _generate_code(self) -> str:
        return "SYS_002"


class ServiceOverloadedError(SystemError):
    """Service is overloaded."""

    default_message = "Service is currently overloaded"
    default_status_code = 503

    def _generate_code(self) -> str:
        return "SYS_003"


class ConfigurationError(SystemError):
    """Configuration error."""

    default_message = "System configuration error"
    severity = ErrorSeverity.CRITICAL

    def _generate_code(self) -> str:
        return "SYS_004"


# Network Errors
class NetworkError(BaseError):
    """Base class for network errors."""

    category = ErrorCategory.NETWORK
    default_message = "Network error occurred"
    default_status_code = 502
    severity = ErrorSeverity.MEDIUM


class ConnectionTimeoutError(NetworkError):
    """Connection timeout."""

    default_message = "Connection timed out"
    default_status_code = 504

    def _generate_code(self) -> str:
        return "NET_001"


class DNSResolutionError(NetworkError):
    """DNS resolution failed."""

    default_message = "Failed to resolve domain"

    def _generate_code(self) -> str:
        return "NET_002"


class SSLCertificateError(NetworkError):
    """SSL certificate error."""

    default_message = "SSL certificate verification failed"
    default_status_code = 495
    severity = ErrorSeverity.HIGH

    def _generate_code(self) -> str:
        return "NET_003"


# Error Registry
ERROR_REGISTRY = {
    # Authentication
    "AUTH_001": InvalidCredentialsError,
    "AUTH_002": TokenExpiredError,
    "AUTH_003": TokenInvalidError,
    "AUTH_004": AccountLockedError,
    # Authorization
    "AUTHZ_001": InsufficientPermissionsError,
    "AUTHZ_002": ResourceAccessDeniedError,
    "AUTHZ_003": ActionNotAllowedError,
    # Validation
    "VAL_001": RequiredFieldMissingError,
    "VAL_002": InvalidFormatError,
    "VAL_003": ValueOutOfRangeError,
    "VAL_004": FileTypeNotSupportedError,
    # LLM Provider
    "LLM_001": ProviderUnavailableError,
    "LLM_002": RateLimitExceededError,
    "LLM_003": TokenLimitExceededError,
    "LLM_004": InvalidModelError,
    "LLM_005": ProviderTimeoutError,
    # System
    "SYS_001": InternalServerError,
    "SYS_002": DatabaseUnavailableError,
    "SYS_003": ServiceOverloadedError,
    "SYS_004": ConfigurationError,
    "SYS_005": RecoveryError,
    # Network
    "NET_001": ConnectionTimeoutError,
    "NET_002": DNSResolutionError,
    "NET_003": SSLCertificateError,
}


def get_error_by_code(error_code: str) -> type:
    """Get error class by error code."""
    return ERROR_REGISTRY.get(error_code, BaseError)
