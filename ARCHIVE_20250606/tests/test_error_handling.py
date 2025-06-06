"""Test the new error handling system."""

import pytest

from backend.utils.error_handler import ErrorHandler, error_handler
from backend.utils.errors import (
    AuthenticationError,
    AuthorizationError,
    ErrorCategory,
    ErrorSeverity,
    InsufficientPermissionsError,
    InternalServerError,
    InvalidCredentialsError,
    ValidationError,
)


def test_error_categories():
    """Test that error categories are properly assigned."""
    auth_error = AuthenticationError()
    assert auth_error.category == ErrorCategory.AUTHENTICATION

    authz_error = AuthorizationError()
    assert authz_error.category == ErrorCategory.AUTHORIZATION

    val_error = ValidationError()
    assert val_error.category == ErrorCategory.VALIDATION

    sys_error = InternalServerError()
    assert sys_error.category == ErrorCategory.SYSTEM


def test_error_status_codes():
    """Test that proper status codes are assigned."""
    auth_error = AuthenticationError()
    assert auth_error.status_code == 401

    authz_error = AuthorizationError()
    assert authz_error.status_code == 403

    val_error = ValidationError()
    assert val_error.status_code == 400

    sys_error = InternalServerError()
    assert sys_error.status_code == 500


def test_error_severity_levels():
    """Test that severity levels are properly assigned."""
    auth_error = AuthenticationError()
    assert auth_error.severity == ErrorSeverity.MEDIUM

    val_error = ValidationError()
    assert val_error.severity == ErrorSeverity.LOW

    sys_error = InternalServerError()
    assert sys_error.severity == ErrorSeverity.CRITICAL


def test_error_handler_base_error():
    """Test handling of custom base errors."""
    handler = ErrorHandler(debug=True)

    error = InvalidCredentialsError()
    response = handler.handle_error(error)

    assert response.status_code == 401
    assert response.body is not None


def test_error_handler_user_messages():
    """Test user-friendly error messages."""
    handler = ErrorHandler(debug=False)

    error = InvalidCredentialsError()
    response = handler.handle_error(error)

    # Should contain user-friendly message
    content = response.body.decode("utf-8")
    assert "The email or password you entered is incorrect" in content


def test_error_context_preservation():
    """Test that error context is preserved."""
    error = ValidationError(
        message="Custom validation error",
        details={"field": "email", "reason": "invalid format"},
        context={"user_id": 123},
    )

    assert error.details == {"field": "email", "reason": "invalid format"}
    assert error.context == {"user_id": 123}


def test_error_code_generation():
    """Test that error codes are generated correctly."""
    error = InvalidCredentialsError()
    assert error.code == "AUTH_001"

    error = InsufficientPermissionsError()
    assert error.code == "AUTHZ_001"

    error = ValidationError()
    assert error.code == "VAL_001"


if __name__ == "__main__":
    # Run basic tests
    print("Testing error categories...")
    test_error_categories()
    print("✓ Error categories test passed")

    print("\nTesting status codes...")
    test_error_status_codes()
    print("✓ Status codes test passed")

    print("\nTesting severity levels...")
    test_error_severity_levels()
    print("✓ Severity levels test passed")

    print("\nTesting error codes...")
    test_error_code_generation()
    print("✓ Error codes test passed")

    print("\nAll tests passed!")
