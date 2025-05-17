# Authentication System Technical Documentation

## Overview

The Ultra authentication system provides secure user authentication, API key management, and session handling for the application. It uses a combination of JWT (JSON Web Tokens) for stateless authentication and database-backed user management.

## Architecture

The authentication system follows a layered architecture:

1. **Repository Layer**: Handles database operations for user data
2. **Service Layer**: Implements authentication business logic
3. **API Layer**: Provides authentication endpoints
4. **Middleware Layer**: Validates authentication for protected routes

### Components

#### Database Models

- `User`: Represents a user account with authentication information
- `ApiKey`: Represents an API key for programmatic access

#### Repositories

- `UserRepository`: Handles user-related database operations
- `BaseRepository`: Provides common database functionality

#### Service

- `AuthService`: Core authentication service with comprehensive functionality

#### API Routes

- `/api/auth/register`: User registration
- `/api/auth/login`: User login
- `/api/auth/refresh`: Token refresh
- `/api/auth/logout`: User logout
- `/api/auth/reset-password-request`: Password reset request
- `/api/auth/reset-password`: Password reset
- `/api/users/me`: User profile management
- `/api/users/me/change-password`: Password change
- `/api/users/me/api-keys`: API key management

#### Middleware

- `AuthMiddleware`: Authentication validation for protected routes

## Authentication Flow

1. **Registration**:
   - User provides email, password, and profile information
   - Password is hashed securely
   - User record is created in the database
   - Authentication tokens are generated

2. **Login**:
   - User provides email and password
   - Credentials are verified against the database
   - Authentication tokens (access and refresh) are generated
   - User information is returned

3. **Token Validation**:
   - Access token is included in API requests
   - Middleware validates the token
   - User information is added to request context
   - Request is processed if token is valid

4. **Token Refresh**:
   - Refresh token is used to obtain new access token
   - Old tokens are invalidated
   - New tokens are generated and returned

5. **Logout**:
   - Tokens are added to blacklist
   - Sessions are invalidated

## Token Management

The authentication system uses two types of tokens:

1. **Access Token**: Short-lived token for API access (15 minutes)
2. **Refresh Token**: Longer-lived token for obtaining new access tokens (7 days)

Tokens are implemented as JWTs with the following fields:

- `sub`: User ID
- `exp`: Expiration time
- `iat`: Issued at time
- `type`: Token type (access or refresh)
- `jti`: Unique token ID

## API Key Management

The authentication system supports API key management for programmatic access:

1. **API Key Creation**: Users can create named API keys
2. **API Key Listing**: Users can view their API keys
3. **API Key Revocation**: Users can revoke API keys

API keys are securely generated and associated with a specific user account.

## Security Considerations

The authentication system implements several security measures:

1. **Password Security**:
   - Passwords are hashed using bcrypt
   - Password strength validation is enforced
   - Password change requires current password verification

2. **Token Security**:
   - Short-lived access tokens
   - Token rotation with refresh
   - Token blacklisting for logout

3. **API Security**:
   - Protected routes require authentication
   - User verification in database
   - Proper error handling to prevent information leakage

## Error Handling

Authentication errors are handled consistently with appropriate HTTP status codes:

- `400 Bad Request`: Invalid input (e.g., weak password)
- `401 Unauthorized`: Authentication failure (e.g., invalid credentials)
- `403 Forbidden`: Authorization failure (e.g., insufficient permissions)
- `404 Not Found`: Resource not found (e.g., user not found)
- `500 Internal Server Error`: Server-side error

## Database Schema

### User Table

```
users (
    id INTEGER PRIMARY KEY,
    email VARCHAR NOT NULL UNIQUE,
    username VARCHAR UNIQUE,
    full_name VARCHAR,
    hashed_password VARCHAR NOT NULL,
    role ENUM NOT NULL,
    subscription_tier ENUM NOT NULL,
    subscription_expiry TIMESTAMP,
    account_balance FLOAT,
    oauth_provider VARCHAR,
    oauth_id VARCHAR,
    is_verified BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    last_login TIMESTAMP
)
```

### API Key Table

```
api_keys (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    name VARCHAR NOT NULL,
    key VARCHAR NOT NULL UNIQUE,
    created_at TIMESTAMP NOT NULL,
    last_used_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
)
```

## Implementation Details

### AuthService

The `AuthService` class provides the following functionality:

- User registration and authentication
- Token generation and validation
- API key management
- User profile management
- Password change
- Token refresh

### AuthMiddleware

The `AuthMiddleware` class provides:

- Token validation for protected routes
- User verification in database
- Token blacklisting check

## Usage Examples

### User Registration

```python
result = auth_service.create_user(
    db,
    "user@example.com",
    "SecurePassword123!",
    name="Example User"
)
```

### User Authentication

```python
user, token_response = auth_service.authenticate_user(
    db, "user@example.com", "SecurePassword123!"
)
```

### API Key Creation

```python
api_key = auth_service.create_api_key(db, user.id, "My API Key")
```

### Token Validation

```python
user = await auth_service.get_current_user(token, db)
```

## Integration Points

### Frontend Integration

The authentication system integrates with the frontend through:

- Authentication API endpoints
- Token storage in the client
- Authentication state management

### API Integration

The authentication system protects API endpoints through:

- Authentication middleware
- User context in requests
- API key validation

## Future Enhancements

Planned enhancements for the authentication system include:

1. Email verification for new users
2. OAuth integration (Google, GitHub, etc.)
3. Two-factor authentication
4. Rate limiting for authentication endpoints
5. Admin user management interface

## Troubleshooting

Common authentication issues and solutions:

### Token Expiration

If a token has expired, use the refresh token to obtain a new access token.

### Invalid Credentials

Check that the email and password are correct.

### API Key Issues

Ensure the API key is active and associated with the correct user.

### Database Connection Issues

Check the database connection and ensure the user repository is properly configured.

## Conclusion

The authentication system provides a secure and comprehensive solution for user authentication, API key management, and session handling in the Ultra application. It follows best practices for security and provides a solid foundation for future enhancements.
