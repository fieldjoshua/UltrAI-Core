# Authentication Testing Guidelines

## Overview

This document provides guidelines for implementing comprehensive authentication tests for the Ultra MVP. Authentication is a critical component of the application, as it forms the foundation for user identity and access control throughout the system.

## Authentication Components to Test

The authentication system in Ultra consists of several components that should be tested individually and together:

1. User registration
2. Login/logout
3. JWT token generation and validation
4. Token refresh mechanism
5. Password hashing and validation
6. Permission management
7. Session handling
8. Authentication middleware

## Test Cases

### 1. User Registration Tests

#### Basic Functionality

- **test_register_new_user**: Test that a new user can register with valid credentials
- **test_register_duplicate_email**: Test that registration fails with an existing email
- **test_register_with_invalid_email**: Test that registration fails with an invalid email format
- **test_register_with_weak_password**: Test that registration fails with a password that doesn't meet strength requirements

#### Security Tests

- **test_register_password_hashing**: Verify that passwords are properly hashed in the database
- **test_register_email_case_insensitivity**: Verify that emails are treated as case insensitive
- **test_register_password_normalization**: Verify that passwords undergo proper normalization

#### Implementation Example

```python
def test_register_new_user(client):
    """Test that a new user can register with valid credentials"""
    response = client.post("/api/auth/register", json={
        "email": "new_user@example.com",
        "password": "StrongPassword123!",
        "name": "New User"
    })

    assert response.status_code == 201
    assert "user_id" in response.json()
    assert response.json()["message"] == "User registered successfully"

    # Verify user exists in database
    from backend.models.user import User
    user = User.get_by_email("new_user@example.com")
    assert user is not None
    assert user.name == "New User"
    assert user.password != "StrongPassword123!"  # Password should be hashed
```

### 2. Login Tests

#### Basic Functionality

- **test_login_valid_credentials**: Test successful login with valid credentials
- **test_login_invalid_email**: Test login with non-existent email
- **test_login_invalid_password**: Test login with incorrect password
- **test_login_disabled_account**: Test login with a disabled account

#### Security Tests

- **test_login_brute_force_protection**: Test rate limiting for failed login attempts
- **test_login_case_sensitivity**: Test email case insensitivity during login
- **test_login_session_creation**: Verify that a session is created upon successful login

#### Implementation Example

```python
def test_login_valid_credentials(client, test_user):
    """Test successful login with valid credentials"""
    response = client.post("/api/auth/login", json={
        "email": test_user.email,
        "password": "password123"  # Match test_user fixture password
    })

    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "refresh_token" in response.json()
    assert "token_type" in response.json()
    assert response.json()["token_type"] == "bearer"

    # Verify token can be used to access protected endpoints
    auth_header = {"Authorization": f"Bearer {response.json()['access_token']}"}
    profile_response = client.get("/api/users/me", headers=auth_header)
    assert profile_response.status_code == 200
    assert profile_response.json()["email"] == test_user.email
```

### 3. Token Validation Tests

#### Basic Functionality

- **test_valid_token_access**: Test that a valid token grants access to protected endpoints
- **test_expired_token**: Test that expired tokens are rejected
- **test_invalid_token_signature**: Test that tokens with invalid signatures are rejected
- **test_malformed_token**: Test that malformed tokens are rejected

#### Security Tests

- **test_token_without_required_claims**: Test tokens missing required claims
- **test_token_with_wrong_audience**: Test tokens with incorrect audience
- **test_token_with_future_issuance**: Test tokens with future issuance times

#### Implementation Example

```python
def test_valid_token_access(client, test_user, auth_token):
    """Test that a valid token grants access to protected endpoints"""
    headers = {"Authorization": f"Bearer {auth_token}"}

    response = client.get("/api/users/me", headers=headers)

    assert response.status_code == 200
    assert response.json()["email"] == test_user.email
    assert response.json()["user_id"] == test_user.id

def test_expired_token(client):
    """Test that expired tokens are rejected"""
    # Create a token that's already expired
    from backend.utils.jwt import create_token
    import time

    expired_token = create_token(
        data={"sub": "test_user_id", "exp": int(time.time()) - 3600}
    )

    headers = {"Authorization": f"Bearer {expired_token}"}
    response = client.get("/api/users/me", headers=headers)

    assert response.status_code == 401
    assert response.json()["status"] == "error"
    assert "expired" in response.json()["message"].lower()
```

### 4. Token Refresh Tests

#### Basic Functionality

- **test_refresh_valid_token**: Test that a valid refresh token can be used to obtain a new access token
- **test_refresh_expired_token**: Test that an expired refresh token is rejected
- **test_refresh_revoked_token**: Test that a revoked refresh token is rejected
- **test_refresh_preserves_claims**: Test that refreshed tokens preserve necessary claims

#### Security Tests

- **test_refresh_token_reuse**: Test that refresh tokens cannot be reused
- **test_access_token_as_refresh**: Test that access tokens cannot be used as refresh tokens
- **test_refresh_after_password_change**: Test that refresh tokens are invalidated after password changes

#### Implementation Example

```python
def test_refresh_valid_token(client, refresh_token):
    """Test that a valid refresh token can be used to obtain a new access token"""
    response = client.post("/api/auth/refresh", json={
        "refresh_token": refresh_token
    })

    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "refresh_token" in response.json()  # Should get a new refresh token too

    # Verify new token works
    headers = {"Authorization": f"Bearer {response.json()['access_token']}"}
    protected_response = client.get("/api/users/me", headers=headers)
    assert protected_response.status_code == 200
```

### 5. Logout Tests

#### Basic Functionality

- **test_logout_valid_token**: Test that logout succeeds with a valid token
- **test_logout_already_logged_out**: Test behavior when trying to logout with an already logged out token
- **test_logout_invalid_token**: Test logout with an invalid token

#### Security Tests

- **test_token_invalidation_after_logout**: Verify that tokens are invalidated after logout
- **test_refresh_token_invalidation**: Verify that refresh tokens are invalidated after logout

#### Implementation Example

```python
def test_logout_valid_token(client, auth_token):
    """Test that logout succeeds with a valid token"""
    headers = {"Authorization": f"Bearer {auth_token}"}

    # First verify token works
    pre_response = client.get("/api/users/me", headers=headers)
    assert pre_response.status_code == 200

    # Logout
    logout_response = client.post("/api/auth/logout", headers=headers)
    assert logout_response.status_code == 200
    assert logout_response.json()["message"] == "Successfully logged out"

    # Verify token no longer works
    post_response = client.get("/api/users/me", headers=headers)
    assert post_response.status_code == 401
```

### 6. Middleware Tests

#### Basic Functionality

- **test_middleware_extracts_token**: Test that the auth middleware correctly extracts tokens from headers
- **test_middleware_validates_token**: Test that the middleware properly validates tokens
- **test_middleware_handles_missing_auth_header**: Test behavior when auth header is missing
- **test_middleware_handles_invalid_auth_header**: Test behavior with malformed auth header

#### Implementation Example

```python
def test_middleware_extracts_token(client, auth_token):
    """Test that the auth middleware correctly extracts tokens from headers"""
    # Test various valid header formats
    valid_headers = [
        {"Authorization": f"Bearer {auth_token}"},
        {"authorization": f"bearer {auth_token}"},  # Test case insensitivity
        {"Authorization": f"Bearer  {auth_token}"}  # Test extra spaces
    ]

    for headers in valid_headers:
        response = client.get("/api/users/me", headers=headers)
        assert response.status_code == 200, f"Failed with headers: {headers}"
```

## Test Fixtures

To efficiently test authentication, create these test fixtures:

```python
@pytest.fixture
def test_user():
    """Create a test user in the database"""
    from backend.models.user import User
    from backend.utils.password import hash_password

    user = User(
        email="test@example.com",
        password=hash_password("password123"),  # Always hash passwords
        name="Test User",
        is_active=True
    )
    user.save()

    yield user

    # Cleanup
    user.delete()

@pytest.fixture
def auth_token(test_user):
    """Create a valid authentication token for the test user"""
    from backend.utils.jwt import create_token

    token = create_token(
        data={"sub": str(test_user.id), "email": test_user.email}
    )

    return token

@pytest.fixture
def refresh_token(test_user):
    """Create a valid refresh token for the test user"""
    from backend.utils.jwt import create_refresh_token

    token = create_refresh_token(
        data={"sub": str(test_user.id)}
    )

    return token
```

## Integration with Authentication Flows

### Frontend-Backend Integration Testing

Test the complete authentication flows including frontend and backend integration:

```python
def test_frontend_login_flow(client, mock_frontend):
    """Test the complete login flow from frontend to backend"""
    # Register a new user
    register_response = client.post("/api/auth/register", json={
        "email": "frontend_test@example.com",
        "password": "SecurePassword123!",
        "name": "Frontend Test User"
    })
    assert register_response.status_code == 201

    # Simulate frontend login
    login_result = mock_frontend.login(
        email="frontend_test@example.com",
        password="SecurePassword123!"
    )

    assert login_result.status == "success"
    assert login_result.isAuthenticated == True
    assert login_result.userData["email"] == "frontend_test@example.com"

    # Verify token storage
    assert mock_frontend.hasStoredToken()

    # Test accessing protected resource
    profile_result = mock_frontend.fetchProfile()
    assert profile_result.status == "success"
    assert profile_result.userData["email"] == "frontend_test@example.com"

    # Test logout
    logout_result = mock_frontend.logout()
    assert logout_result.status == "success"
    assert not mock_frontend.hasStoredToken()
```

## Additional Security Testing

### Password Security Tests

Test password hashing and verification functionality:

```python
def test_password_hashing():
    """Test that passwords are properly hashed and can be verified"""
    from backend.utils.password import hash_password, verify_password

    original_password = "SecurePassword123!"
    hashed_password = hash_password(original_password)

    # Verify hashing produces different results each time (salting)
    assert hashed_password != hash_password(original_password)

    # Verify password verification works
    assert verify_password(original_password, hashed_password)
    assert not verify_password("WrongPassword", hashed_password)
```

### JWT Security Tests

Test JWT token generation and verification:

```python
def test_jwt_claims():
    """Test that JWT tokens contain all required claims"""
    from backend.utils.jwt import create_token, decode_token

    user_id = "test_user_id"
    token = create_token(data={"sub": user_id})
    decoded = decode_token(token)

    assert decoded["sub"] == user_id
    assert "exp" in decoded  # Expiration time
    assert "iat" in decoded  # Issued at time
    assert "jti" in decoded  # JWT ID for uniqueness
```

## Mocking Authentication for Other Tests

For tests where authentication is not the focus, create a helper to mock authentication:

```python
def authenticate_client(client, user_id="test_user_id", scopes=None):
    """Helper to authenticate a test client"""
    from backend.utils.jwt import create_token

    token_data = {"sub": user_id}
    if scopes:
        token_data["scopes"] = scopes

    token = create_token(data=token_data)
    client.headers = {"Authorization": f"Bearer {token}"}
    return client

# Usage example
def test_protected_endpoint(client):
    """Test that requires authentication"""
    client = authenticate_client(client)
    response = client.get("/api/protected-resource")
    assert response.status_code == 200
```

## Conclusion

Authentication testing is crucial for ensuring the security and reliability of the Ultra platform. By implementing these tests, we can verify that:

1. Users can register and log in securely
2. Access tokens are properly validated and protected resources are secure
3. Invalid authentication attempts are properly rejected
4. Sessions are managed correctly
5. User credentials are stored securely
6. Token refresh and logout functionality works as expected

Implementing these tests will significantly enhance the security posture of the application and reduce the risk of authentication-related vulnerabilities.
