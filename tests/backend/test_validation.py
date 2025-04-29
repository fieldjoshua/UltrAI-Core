"""
Tests for request validation middleware and service.

This module tests the functionality of the request validation middleware
and validation service.
"""

import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from pydantic import Field

from backend.utils.middleware import RequestValidationMiddleware
from backend.utils.validation_service import validate_input, ValidatedModel


class TestUser(ValidatedModel):
    """Test user model for validation testing"""

    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(...)  # Email validation through ValidatedModel
    age: int = Field(..., ge=18, le=120)


@pytest.fixture
def app_with_validation_middleware():
    """Create a FastAPI application with validation middleware"""
    app = FastAPI()

    app.add_middleware(
        RequestValidationMiddleware,
        allowed_content_types={"application/json"},
        max_content_length=1024 * 1024,  # 1MB
        required_headers=["content-type"],
    )

    @app.post("/api/users")
    @validate_input(TestUser)
    async def create_user(request: Request, validated_data: TestUser):
        """Create a new user with validated data"""
        return {
            "status": "success",
            "message": "User created successfully",
            "data": validated_data.dict(),
        }

    @app.post("/api/test/content-type")
    async def test_content_type(request: Request):
        """Test content type validation"""
        return {"status": "success"}

    @app.post("/api/test/size")
    async def test_size(request: Request):
        """Test request size validation"""
        return {"status": "success"}

    return app


def test_valid_request(app_with_validation_middleware):
    """Test that valid requests pass validation"""
    client = TestClient(app_with_validation_middleware)

    valid_data = {"username": "testuser", "email": "test@example.com", "age": 30}

    response = client.post(
        "/api/users", json=valid_data, headers={"Content-Type": "application/json"}
    )

    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert response.json()["data"]["username"] == "testuser"
    assert response.json()["data"]["email"] == "test@example.com"
    assert response.json()["data"]["age"] == 30


def test_invalid_data(app_with_validation_middleware):
    """Test that invalid data fails validation"""
    client = TestClient(app_with_validation_middleware)

    # Username too short
    invalid_data = {"username": "te", "email": "test@example.com", "age": 30}

    response = client.post(
        "/api/users", json=invalid_data, headers={"Content-Type": "application/json"}
    )

    assert response.status_code == 422

    # Invalid email
    invalid_data = {"username": "testuser", "email": "not-an-email", "age": 30}

    response = client.post(
        "/api/users", json=invalid_data, headers={"Content-Type": "application/json"}
    )

    assert response.status_code == 422

    # Age too low
    invalid_data = {"username": "testuser", "email": "test@example.com", "age": 17}

    response = client.post(
        "/api/users", json=invalid_data, headers={"Content-Type": "application/json"}
    )

    assert response.status_code == 422


def test_missing_required_field(app_with_validation_middleware):
    """Test that missing required fields fail validation"""
    client = TestClient(app_with_validation_middleware)

    # Missing email
    invalid_data = {"username": "testuser", "age": 30}

    response = client.post(
        "/api/users", json=invalid_data, headers={"Content-Type": "application/json"}
    )

    assert response.status_code == 422


def test_unsupported_content_type(app_with_validation_middleware):
    """Test that unsupported content types are rejected"""
    client = TestClient(app_with_validation_middleware)

    response = client.post(
        "/api/test/content-type",
        content="Plain text data",
        headers={"Content-Type": "text/plain"},
    )

    assert response.status_code == 415  # Unsupported Media Type


def test_missing_content_type(app_with_validation_middleware):
    """Test that missing required header is rejected"""
    client = TestClient(app_with_validation_middleware)

    response = client.post(
        "/api/test/content-type",
        json={"test": "data"},
        # No Content-Type header
    )

    assert response.status_code == 400  # Bad Request


def test_request_too_large(app_with_validation_middleware):
    """Test that requests exceeding size limit are rejected"""
    client = TestClient(app_with_validation_middleware)

    # Generate large payload (just over 1MB)
    large_data = {"data": "x" * (1024 * 1024 + 100)}

    response = client.post(
        "/api/test/size",
        json=large_data,
        headers={
            "Content-Type": "application/json",
            "Content-Length": str(len(str(large_data))),
        },
    )

    assert response.status_code == 413  # Request Entity Too Large
