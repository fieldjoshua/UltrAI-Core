"""
Tests for the error handling system.

This module tests the error handling components, including error classification,
exception handling, and error response formatting.
"""

import pytest
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.testclient import TestClient

from backend.utils.error_handler import (
    UltraBaseException,
    ValidationException,
    ResourceNotFoundException,
    AuthenticationException,
    BusinessLogicException,
    ServiceException,
    ErrorCode,
    ErrorCategory,
    ErrorClassification,
    register_exception_handlers,
)


@pytest.fixture
def app_with_error_handlers():
    """Create a FastAPI app with error handlers"""
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/test/validation-error")
    async def validation_error():
        raise ValidationException(
            message="Custom validation error",
            field_errors={"field1": "Invalid field1", "field2": "Invalid field2"},
        )

    @app.get("/test/not-found")
    async def not_found():
        raise ResourceNotFoundException(resource_type="User", resource_id="123")

    @app.get("/test/auth-error")
    async def auth_error():
        raise AuthenticationException(
            message="Authentication required", code=ErrorCode.UNAUTHORIZED
        )

    @app.get("/test/business-error")
    async def business_error():
        raise BusinessLogicException(
            message="Business rule violation",
            details={"rule": "maximum_attempts_exceeded"},
        )

    @app.get("/test/service-error")
    async def service_error():
        raise ServiceException(
            message="External service unavailable",
            service_name="payment_gateway",
            code=ErrorCode.SERVICE_UNAVAILABLE,
        )

    @app.get("/test/generic-error")
    async def generic_error():
        raise UltraBaseException(
            message="Something went wrong", code=ErrorCode.INTERNAL_ERROR
        )

    @app.get("/test/unexpected-error")
    async def unexpected_error():
        # This will raise a standard Python exception
        raise ValueError("This is an unexpected error")

    return app


def test_error_classification():
    """Test error classification mappings"""
    # Check status code mapping
    assert (
        ErrorClassification.get_status_code(ErrorCode.INTERNAL_ERROR)
        == status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    assert (
        ErrorClassification.get_status_code(ErrorCode.NOT_FOUND)
        == status.HTTP_404_NOT_FOUND
    )
    assert (
        ErrorClassification.get_status_code(ErrorCode.VALIDATION_ERROR)
        == status.HTTP_422_UNPROCESSABLE_ENTITY
    )

    # Check category mapping
    assert (
        ErrorClassification.get_category(ErrorCode.INTERNAL_ERROR)
        == ErrorCategory.SYSTEM
    )
    assert (
        ErrorClassification.get_category(ErrorCode.UNAUTHORIZED)
        == ErrorCategory.AUTHENTICATION
    )
    assert (
        ErrorClassification.get_category(ErrorCode.VALIDATION_ERROR)
        == ErrorCategory.VALIDATION
    )


def test_validation_exception(app_with_error_handlers):
    """Test validation exception handling"""
    client = TestClient(app_with_error_handlers)
    response = client.get("/test/validation-error")

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    data = response.json()

    assert data["status"] == "error"
    assert data["message"] == "Custom validation error"
    assert data["code"] == ErrorCode.VALIDATION_ERROR

    # Check for field errors in details
    assert "details" in data
    assert isinstance(data["details"], list)
    assert len(data["details"]) > 0

    # Check individual field errors
    field_errors = {error["loc"][0]: error["msg"] for error in data["details"]}
    assert "field1" in field_errors
    assert "field2" in field_errors
    assert field_errors["field1"] == "Invalid field1"
    assert field_errors["field2"] == "Invalid field2"


def test_resource_not_found_exception(app_with_error_handlers):
    """Test resource not found exception handling"""
    client = TestClient(app_with_error_handlers)
    response = client.get("/test/not-found")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()

    assert data["status"] == "error"
    assert "User with ID 123 not found" in data["message"]
    assert data["code"] == ErrorCode.RESOURCE_NOT_FOUND

    # Check details
    assert "details" in data
    assert data["details"]["resource_type"] == "User"
    assert data["details"]["resource_id"] == "123"


def test_authentication_exception(app_with_error_handlers):
    """Test authentication exception handling"""
    client = TestClient(app_with_error_handlers)
    response = client.get("/test/auth-error")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    data = response.json()

    assert data["status"] == "error"
    assert data["message"] == "Authentication required"
    assert data["code"] == ErrorCode.UNAUTHORIZED


def test_business_logic_exception(app_with_error_handlers):
    """Test business logic exception handling"""
    client = TestClient(app_with_error_handlers)
    response = client.get("/test/business-error")

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    data = response.json()

    assert data["status"] == "error"
    assert data["message"] == "Business rule violation"
    assert data["code"] == ErrorCode.BUSINESS_LOGIC_ERROR

    # Check details
    assert "details" in data
    assert data["details"]["rule"] == "maximum_attempts_exceeded"


def test_service_exception(app_with_error_handlers):
    """Test service exception handling"""
    client = TestClient(app_with_error_handlers)
    response = client.get("/test/service-error")

    assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    data = response.json()

    assert data["status"] == "error"
    assert data["message"] == "External service unavailable"
    assert data["code"] == ErrorCode.SERVICE_UNAVAILABLE

    # Check service name in details
    assert "details" in data
    assert data["details"]["service_name"] == "payment_gateway"


def test_generic_exception(app_with_error_handlers):
    """Test generic exception handling"""
    client = TestClient(app_with_error_handlers)
    response = client.get("/test/generic-error")

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    data = response.json()

    assert data["status"] == "error"
    assert data["message"] == "Something went wrong"
    assert data["code"] == ErrorCode.INTERNAL_ERROR


def test_unexpected_exception(app_with_error_handlers):
    """Test unexpected exception handling"""
    client = TestClient(app_with_error_handlers)
    response = client.get("/test/unexpected-error")

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    data = response.json()

    assert data["status"] == "error"
    assert "An unexpected error occurred" in data["message"]
    assert data["code"] == ErrorCode.INTERNAL_ERROR
