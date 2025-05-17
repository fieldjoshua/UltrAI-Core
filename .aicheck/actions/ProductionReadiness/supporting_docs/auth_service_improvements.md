# Authentication Service Improvements

This document outlines the necessary improvements to the authentication service for production readiness.

## Current Authentication Issues

Based on our testing, several authentication issues were identified when running in real mode:

1. Public endpoints like health checks return 401 Unauthorized
2. Test authentication tokens aren't properly handled
3. Auth middleware doesn't properly identify public routes in real mode

## Required Changes

### 1. Public Routes Configuration

```python
# Current implementation
public_paths = [
    "/docs",
    "/openapi.json",
    # Other paths...
]

# Improved implementation
public_paths = [
    "/api/health",
    "/api/docs",
    "/api/openapi.json",
    "/api/auth/login",
    "/api/auth/register",
    "/api/auth/refresh",
    "/api/auth/password-reset",
    # Other public paths...
]
```

The public paths list should be consistent across all environments and properly include all endpoints that should be accessible without authentication.

### 2. Authentication Middleware

```python
async def auth_middleware(request: Request, call_next: Callable) -> Response:
    """
    Authentication middleware that verifies JWT tokens

    Args:
        request: The incoming request
        call_next: The next middleware or route handler

    Returns:
        The response from the next handler
    """
    # Check if the path should bypass authentication
    if any(request.url.path.startswith(path) for path in public_paths):
        return await call_next(request)

    # Get token from Authorization header
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Missing or invalid authentication token"}
        )

    token = auth_header.replace("Bearer ", "")

    # In test mode, accept test tokens
    if os.getenv("TESTING", "false").lower() == "true":
        if token.startswith("test_token_"):
            # Set a test user in request state
            request.state.user = {"id": "test_user_id", "email": "test@example.com"}
            return await call_next(request)

    # Verify token
    try:
        user = await auth_service.get_user_from_token(token)
        if not user:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Invalid authentication token"}
            )

        # Add user to request state
        request.state.user = user
        return await call_next(request)
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Authentication failed"}
        )
```

### 3. Auth Service Implementation

```python
class AuthService:
    """Service for handling authentication operations"""

    def __init__(self):
        """Initialize the authentication service"""
        self.db = database_service
        self.jwt_secret = os.getenv("JWT_SECRET", "default-secret-key")
        self.jwt_algorithm = os.getenv("JWT_ALGORITHM", "HS256")
        self.access_token_expire_minutes = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
        self.refresh_token_expire_days = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "7"))
        self.enable_auth = os.getenv("ENABLE_AUTH", "true").lower() == "true"

        # Set a warning if using default secret key
        if self.jwt_secret == "default-secret-key":
            logger.warning("Using default JWT secret key, this is insecure for production")

    async def get_user_from_token(self, token: str) -> Optional[dict]:
        """
        Get a user from a JWT token

        Args:
            token: The JWT token

        Returns:
            The user object if the token is valid, None otherwise
        """
        # Skip auth if disabled
        if not self.enable_auth:
            return {"id": "anonymous", "email": "anonymous@example.com"}

        try:
            # Handle test tokens in test environment
            if os.getenv("TESTING", "false").lower() == "true":
                if token.startswith("test_token_"):
                    return {"id": "test_user_id", "email": "test@example.com"}

            # Decode token
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])

            # Verify token type
            if payload.get("type") != "access":
                return None

            # Get user from database
            user_id = payload.get("sub")
            if not user_id:
                return None

            # If database is unavailable, return the user from the token
            if not self.db or not self.db.is_connected():
                logger.warning("Database unavailable, using token data for user")
                return {
                    "id": user_id,
                    "email": payload.get("email", "unknown@example.com"),
                    "name": payload.get("name", "Unknown User"),
                    "is_active": True
                }

            # Get user from database
            user = await self.db.get_user(user_id)
            return user
        except jwt.PyJWTError as e:
            logger.error(f"JWT token error: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error getting user from token: {str(e)}")
            return None
```

### 4. Token Generation and Validation

```python
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a new JWT access token

    Args:
        data: The data to encode in the token
        expires_delta: Custom expiration time

    Returns:
        The encoded JWT token
    """
    to_encode = data.copy()

    # Set expiration
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
        )

    # Add standard claims
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })

    # Encode token
    jwt_secret = os.getenv("JWT_SECRET", "default-secret-key")
    jwt_algorithm = os.getenv("JWT_ALGORITHM", "HS256")
    encoded_jwt = jwt.encode(to_encode, jwt_secret, algorithm=jwt_algorithm)

    return encoded_jwt

def validate_token(token: str, token_type: str = "access") -> Tuple[bool, Optional[dict]]:
    """
    Validate a JWT token

    Args:
        token: The token to validate
        token_type: The expected token type

    Returns:
        A tuple of (is_valid, payload)
    """
    try:
        # Decode token
        jwt_secret = os.getenv("JWT_SECRET", "default-secret-key")
        jwt_algorithm = os.getenv("JWT_ALGORITHM", "HS256")
        payload = jwt.decode(token, jwt_secret, algorithms=[jwt_algorithm])

        # Verify token type
        if payload.get("type") != token_type:
            return False, None

        return True, payload
    except jwt.ExpiredSignatureError:
        return False, {"error": "Token has expired"}
    except jwt.InvalidTokenError:
        return False, {"error": "Invalid token"}
    except Exception as e:
        return False, {"error": f"Validation error: {str(e)}"}
```

## Test Environment Configuration

For testing, we need to ensure that test tokens are properly handled:

```python
# Set test environment variables
os.environ["TESTING"] = "true"
os.environ["JWT_SECRET"] = "test-secret-key"
os.environ["ENABLE_AUTH"] = "true"  # Enable auth but accept test tokens

# Generate a test token for test client
test_token = create_access_token({"sub": "test-user-id", "email": "test@example.com"})

# Configure test client
@pytest.fixture
def client():
    """Test client with authentication"""
    with TestClient(app) as client:
        client.headers["Authorization"] = f"Bearer {test_token}"
        yield client
```

## Production Authentication Flow

In production, the authentication flow should be:

1. User registers or logs in to receive access and refresh tokens
2. Access token is used for API requests (expires after 30 minutes)
3. When access token expires, refresh token is used to get a new access token
4. If refresh token expires, user must log in again

This flow should be properly implemented in the frontend and backend.

## Security Considerations

1. JWT tokens should be stored securely (HTTP-only cookies or secure local storage)
2. CSRF protection should be implemented for cookie-based authentication
3. Token expiration should be relatively short for access tokens
4. JWT secrets should be strong and unique per environment
5. Token validation should check issuer, audience, and other claims

## Testing Authentication

All authentication flows should be thoroughly tested:

1. Login with valid credentials
2. Login with invalid credentials
3. Token validation and expiration
4. Token refresh
5. Access to protected endpoints
6. Access to public endpoints
7. Error handling for invalid tokens

These tests should be run in both mock and real modes to ensure consistent behavior.
