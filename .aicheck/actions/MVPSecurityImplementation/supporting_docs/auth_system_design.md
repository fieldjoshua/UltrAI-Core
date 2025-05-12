# Authentication System Design

## Overview

This document outlines the design of the authentication system for the Ultra MVP. The authentication system is designed to be simple yet secure, providing the necessary functionality for user authentication without unnecessary complexity.

## Core Components

### 1. User Management

#### User Model

```python
class User(BaseModel):
    id: str
    username: str
    email: str
    password_hash: str
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    active: bool = True
```

#### Password Management

- Passwords will be hashed using bcrypt with appropriate salt
- No password strength requirements for MVP (can be added later)
- Password reset functionality not included in MVP

### 2. Authentication Flow

#### Registration
1. User submits registration form with username, email, and password
2. Server validates input (email format, username uniqueness)
3. Password is hashed with bcrypt
4. User record is created in database
5. JWT is generated and returned to client

#### Login
1. User submits login form with username/email and password
2. Server retrieves user record
3. Password is verified against stored hash
4. If valid, JWT is generated and returned to client
5. Last login timestamp is updated

#### Logout
1. Client calls logout endpoint
2. Token is added to blacklist (if implemented)
3. Client removes token from storage

### 3. JWT Implementation

#### Token Structure

```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "sub": "<user_id>",
    "iat": "<issued_at>",
    "exp": "<expiration>",
    "username": "<username>"
  },
  "signature": "..."
}
```

#### Token Handling

- Tokens will be set to expire after 24 hours for MVP
- Token blacklisting will be implemented with Redis (optional for MVP)
- Refresh tokens are not included in MVP

### 4. Middleware

#### Authentication Middleware

```python
async def auth_middleware(request: Request, call_next):
    auth_header = request.headers.get("Authorization")
    
    if not auth_header or not auth_header.startswith("Bearer "):
        return JSONResponse(
            status_code=401,
            content={"detail": "Authentication required"}
        )
    
    token = auth_header.split(" ")[1]
    
    try:
        payload = jwt.decode(
            token, 
            settings.JWT_SECRET_KEY, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        request.state.user_id = payload.get("sub")
        request.state.username = payload.get("username")
    except jwt.PyJWTError:
        return JSONResponse(
            status_code=401,
            content={"detail": "Invalid authentication token"}
        )
    
    return await call_next(request)
```

#### Protected Route Decorator

```python
def require_auth(func):
    @functools.wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
        if not hasattr(request.state, "user_id"):
            return JSONResponse(
                status_code=401,
                content={"detail": "Authentication required"}
            )
        return await func(request, *args, **kwargs)
    return wrapper
```

### 5. Frontend Integration

#### Token Storage

- JWT will be stored in localStorage for MVP
- Future enhancement: move to httpOnly cookies

#### Authentication State

- React Context will be used to manage authentication state
- Simple hook will provide authentication status and user information

```typescript
// Example usage
const { isAuthenticated, user, login, logout } = useAuth();
```

## API Endpoints

### Registration

```
POST /api/auth/register
Content-Type: application/json

{
  "username": "example_user",
  "email": "user@example.com",
  "password": "secure_password"
}
```

### Login

```
POST /api/auth/login
Content-Type: application/json

{
  "username": "example_user",
  "password": "secure_password"
}
```

### Logout

```
POST /api/auth/logout
Authorization: Bearer <token>
```

### Get Current User

```
GET /api/auth/me
Authorization: Bearer <token>
```

## Security Considerations

### For MVP

- JWTs are signed with HS256 algorithm
- Secret key is stored securely in environment variables
- Password hashing with bcrypt (10 rounds)
- Basic input validation on all endpoints

### Future Enhancements

- Move to RS256 algorithm with public/private keys
- Implement refresh tokens
- Add 2FA support
- Enhance password requirements
- Add rate limiting on auth endpoints
- Implement brute force protection

## Implementation Plan

1. Create database models for User
2. Implement authentication endpoints
3. Build authentication middleware
4. Create JWT utility functions
5. Integrate with frontend
6. Add tests for authentication flow

## Dependencies

- PyJWT for token generation and validation
- bcrypt for password hashing
- Redis for token blacklisting (optional)
- React Context API for frontend state management