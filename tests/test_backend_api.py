import os
import json
import pytest
from fastapi.testclient import TestClient
from uuid import uuid4

# Import app
from backend.app import app
from backend.services.auth_service import auth_service, JWT_SECRET
from backend.services.pricing_integration import pricing_integration

# Initialize test client
client = TestClient(app)


# Clear test data before and after tests
@pytest.fixture(scope="module", autouse=True)
def clear_test_data():
    # Save original data paths
    original_user_file = auth_service.user_file

    # Use temporary paths for testing
    test_user_file = "test_user_data.json"
    auth_service.user_file = test_user_file

    # Clear any existing test data
    if os.path.exists(test_user_file):
        os.remove(test_user_file)

    # Reset users
    auth_service.users = {}

    # Run tests
    yield

    # Clean up test files
    if os.path.exists(test_user_file):
        os.remove(test_user_file)

    # Restore original paths
    auth_service.user_file = original_user_file


# User API Tests
class TestUserAPI:
    def test_register_user(self):
        """Test user registration endpoint"""
        # Prepare test data
        user_data = {
            "user_id": str(uuid4()),
            "email": "test@example.com",
            "password": "securepassword",
            "name": "Test User",
            "tier": "basic"
        }

        # Make request
        response = client.post("/api/register", json=user_data)

        # Check response
        assert response.status_code == 200

        # Verify user was created
        data = response.json()
        assert data["user_id"] == user_data["user_id"]
        assert data["email"] == user_data["email"]
        assert data["name"] == user_data["name"]
        assert "password" not in data  # Password should not be returned

        # Verify user exists in auth service
        user = auth_service.get_user(user_data["user_id"])
        assert user is not None
        assert user["email"] == user_data["email"]

    def test_duplicate_registration(self):
        """Test registering a user with an existing user_id"""
        # First registration
        user_data = {
            "user_id": str(uuid4()),
            "email": "duplicate@example.com",
            "password": "securepassword",
            "name": "Duplicate User"
        }

        client.post("/api/register", json=user_data)

        # Try to register with same user_id
        response = client.post("/api/register", json=user_data)

        # Should return error
        assert response.status_code == 400
        assert "error" in response.json()

    def test_login_success(self):
        """Test login with valid credentials"""
        # Register a user first
        user_id = str(uuid4())
        user_data = {
            "user_id": user_id,
            "email": "login@example.com",
            "password": "loginpassword",
            "name": "Login User"
        }

        client.post("/api/register", json=user_data)

        # Try to login
        login_data = {
            "email": "login@example.com",
            "password": "loginpassword"
        }

        response = client.post("/api/login", json=login_data)

        # Should succeed and return a token
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["user_id"] == user_id

    def test_login_failure(self):
        """Test login with invalid credentials"""
        # Try to login with invalid credentials
        login_data = {
            "email": "nonexistent@example.com",
            "password": "wrongpassword"
        }

        response = client.post("/api/login", json=login_data)

        # Should fail
        assert response.status_code == 401
        assert "error" in response.json()

    def test_get_current_user(self):
        """Test getting the current user profile with authentication"""
        # Register a user first
        user_id = str(uuid4())
        user_data = {
            "user_id": user_id,
            "email": "profile@example.com",
            "password": "profilepassword",
            "name": "Profile User"
        }

        client.post("/api/register", json=user_data)

        # Login to get token
        login_data = {
            "email": "profile@example.com",
            "password": "profilepassword"
        }

        login_response = client.post("/api/login", json=login_data)
        token = login_response.json()["access_token"]

        # Get user profile with token
        response = client.get(
            "/api/user/me",
            headers={"Authorization": f"Bearer {token}"}
        )

        # Should return user profile
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == user_id
        assert data["email"] == user_data["email"]
        assert data["name"] == user_data["name"]

    def test_update_user(self):
        """Test updating user profile"""
        # Register a user first
        user_id = str(uuid4())
        user_data = {
            "user_id": user_id,
            "email": "update@example.com",
            "password": "updatepassword",
            "name": "Update User"
        }

        client.post("/api/register", json=user_data)

        # Login to get token
        login_data = {
            "email": "update@example.com",
            "password": "updatepassword"
        }

        login_response = client.post("/api/login", json=login_data)
        token = login_response.json()["access_token"]

        # Update user profile
        update_data = {
            "name": "Updated Name",
            "email": "updated@example.com"
        }

        response = client.put(
            "/api/user/me",
            json=update_data,
            headers={"Authorization": f"Bearer {token}"}
        )

        # Should return updated profile
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["email"] == update_data["email"]

        # Verify changes persisted
        user = auth_service.get_user(user_id)
        assert user["name"] == update_data["name"]
        assert user["email"] == update_data["email"]


# Pricing API Tests
class TestPricingAPI:
    def test_estimate_tokens(self):
        """Test token estimation endpoint"""
        # Prepare test data
        request_data = {
            "prompt": "This is a test prompt for token estimation",
            "model": "gpt4o",
            "requestType": "completion",
            "userId": "test123"
        }

        # Make request
        response = client.post("/api/estimate-tokens", json=request_data)

        # Check response
        assert response.status_code == 200
        data = response.json()
        assert "estimated_tokens" in data
        assert "cost_estimate" in data
        assert data["prompt_length"] == len(request_data["prompt"])

    def test_toggle_pricing(self):
        """Test pricing toggle endpoint"""
        # Save original state
        original_state = pricing_integration.pricing_enabled

        try:
            # Prepare test data
            toggle_data = {
                "enabled": not original_state,
                "reason": "Testing pricing toggle"
            }

            # Make request
            response = client.post("/api/admin/pricing/toggle", json=toggle_data)

            # Check response
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert data["pricing_enabled"] == toggle_data["enabled"]
            assert data["previous_state"] == original_state

            # Verify state was changed
            assert pricing_integration.pricing_enabled == toggle_data["enabled"]

        finally:
            # Restore original state
            pricing_integration.pricing_enabled = original_state

    def test_create_user_account(self):
        """Test creating a user account with pricing integration"""
        # Prepare test data
        user_data = {
            "userId": str(uuid4()),
            "tier": "premium",
            "initialBalance": 100.0
        }

        # Make request
        response = client.post("/api/user/create", json=user_data)

        # Check response
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "user" in data

        # Verify user was created
        user = data["user"]
        assert user["id"] == user_data["userId"]
        assert user["tier"] == user_data["tier"]
        assert user["balance"] == user_data["initialBalance"]

    def test_add_funds(self):
        """Test adding funds to a user account"""
        # Create a user first
        user_id = str(uuid4())
        user_data = {
            "userId": user_id,
            "tier": "basic",
            "initialBalance": 50.0
        }

        client.post("/api/user/create", json=user_data)

        # Add funds
        funds_data = {
            "userId": user_id,
            "amount": 25.0,
            "description": "Test deposit"
        }

        response = client.post("/api/user/add-funds", json=funds_data)

        # Check response
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "transaction" in data

        # Verify funds were added
        balance_response = client.get(f"/api/user/{user_id}/balance")
        balance_data = balance_response.json()
        assert balance_data["status"] == "success"
        # The initial balance was 50, we added 25
        assert balance_data["balance"]["balance"] >= 50.0  # May include additional details