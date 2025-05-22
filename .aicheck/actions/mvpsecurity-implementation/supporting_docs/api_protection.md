# API Protection Implementation

This document outlines the implementation details for protecting API endpoints in the Ultra MVP.

## Overview

API protection involves several key components:

1. Input validation and sanitization
2. Rate limiting
3. API key management
4. Request/response security

## Input Validation

### Validation Middleware

We'll implement a validation middleware using Pydantic models:

```python
from fastapi import Request, HTTPException
from fastapi.routing import APIRoute
from pydantic import ValidationError
from typing import Callable, Type, Dict, Any

class ValidatedRoute(APIRoute):
    def __init__(
        self,
        *args,
        request_model: Type = None,
        **kwargs
    ):
        self.request_model = request_model
        super().__init__(*args, **kwargs)

    async def handle(self, request: Request) -> Any:
        if self.request_model is not None:
            body = await request.json()
            try:
                # Validate request body against model
                validated_data = self.request_model(**body)
                # Add validated data to request state
                request.state.validated_data = validated_data
            except ValidationError as e:
                raise HTTPException(
                    status_code=422,
                    detail=e.errors()
                )

        return await super().handle(request)
```

### Schema Validation

Define Pydantic models for all request types:

```python
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)

class AnalysisRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=4000)
    models: List[str] = Field(..., min_items=1)
    analysis_pattern: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
```

### Implementation in Routes

Apply validation to routes:

```python
from fastapi import APIRouter, Depends
from .models import UserCreate, AnalysisRequest
from .middleware import ValidatedRoute

router = APIRouter(route_class=ValidatedRoute)

@router.post("/users")
async def create_user(request: Request):
    # Validated data is available in request.state.validated_data
    user_data = request.state.validated_data
    # Process user creation
    return {"status": "success"}

@router.post("/analysis")
async def create_analysis(request: Request):
    # Validated data is available in request.state.validated_data
    analysis_data = request.state.validated_data
    # Process analysis request
    return {"status": "success"}
```

## Rate Limiting

### Rate Limit Middleware

Implement rate limiting using a Redis-based solution:

```python
import time
import redis
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        redis_url: str,
        requests_per_minute: int = 60,
        window_seconds: int = 60
    ):
        super().__init__(app)
        self.redis = redis.from_url(redis_url)
        self.requests_per_minute = requests_per_minute
        self.window_seconds = window_seconds

    async def dispatch(self, request: Request, call_next):
        # Determine client identifier (IP or user_id)
        identifier = request.state.user_id if hasattr(request.state, "user_id") else request.client.host

        # Rate limit key includes endpoint and identifier
        endpoint = f"{request.method}:{request.url.path}"
        key = f"ratelimit:{endpoint}:{identifier}"

        # Get current request count
        current = self.redis.get(key)
        current = int(current) if current else 0

        # Check if rate limit exceeded
        if current >= self.requests_per_minute:
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Try again later."
            )

        # Increment counter and set expiry
        pipe = self.redis.pipeline()
        pipe.incr(key)
        pipe.expire(key, self.window_seconds)
        pipe.execute()

        # Add rate limit headers
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(max(0, self.requests_per_minute - current - 1))
        response.headers["X-RateLimit-Reset"] = str(int(time.time() + self.window_seconds))

        return response
```

### Endpoint-Specific Rate Limits

Configure different rate limits for different endpoints:

```python
# In application startup code
app.add_middleware(
    RateLimitMiddleware,
    redis_url=settings.REDIS_URL,
    requests_per_minute=60,  # Default rate limit
    window_seconds=60
)

# For specific routes with different limits
auth_router = APIRouter()
app.include_router(
    auth_router,
    prefix="/auth",
    dependencies=[
        Depends(
            RateLimitMiddleware(
                app=None,
                redis_url=settings.REDIS_URL,
                requests_per_minute=10,  # Stricter limit for auth endpoints
                window_seconds=60
            ).dispatch
        )
    ]
)
```

## API Key Management

### Secure Storage

Store API keys securely using environment variables:

```python
# settings.py
import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    OPENAI_API_KEY: str
    CLAUDE_API_KEY: str
    COHERE_API_KEY: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
```

### Key Encryption

For keys stored in the database, implement encryption:

```python
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os

class KeyEncryption:
    def __init__(self, master_key: str):
        # Derive key from master key
        salt = os.environ.get("KEY_SALT", "default_salt").encode()
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(master_key.encode()))
        self.fernet = Fernet(key)

    def encrypt_key(self, api_key: str) -> str:
        """Encrypt an API key"""
        return self.fernet.encrypt(api_key.encode()).decode()

    def decrypt_key(self, encrypted_key: str) -> str:
        """Decrypt an API key"""
        return self.fernet.decrypt(encrypted_key.encode()).decode()

# Usage
key_encryption = KeyEncryption(os.environ.get("MASTER_KEY"))
encrypted_key = key_encryption.encrypt_key(settings.OPENAI_API_KEY)
# Store encrypted_key in database
```

### Key Rotation

Implement key rotation capabilities:

```python
from datetime import datetime, timedelta
from typing import Dict, Optional
import uuid

class APIKeyManager:
    def __init__(self, db_connection, key_encryption):
        self.db = db_connection
        self.key_encryption = key_encryption

    async def create_key(self, service: str, api_key: str, user_id: Optional[str] = None) -> Dict:
        """Create a new API key entry"""
        key_id = str(uuid.uuid4())
        encrypted_key = self.key_encryption.encrypt_key(api_key)

        expiry = datetime.utcnow() + timedelta(days=90)  # 90-day rotation

        key_record = {
            "id": key_id,
            "service": service,
            "key": encrypted_key,
            "user_id": user_id,
            "created_at": datetime.utcnow(),
            "expires_at": expiry,
            "active": True
        }

        await self.db.api_keys.insert_one(key_record)
        return key_record

    async def rotate_key(self, key_id: str, new_api_key: str) -> Dict:
        """Rotate an API key"""
        old_key = await self.db.api_keys.find_one({"id": key_id})
        if not old_key:
            raise ValueError(f"Key with ID {key_id} not found")

        # Deactivate old key
        await self.db.api_keys.update_one(
            {"id": key_id},
            {"$set": {"active": False}}
        )

        # Create new key
        return await self.create_key(
            service=old_key["service"],
            api_key=new_api_key,
            user_id=old_key.get("user_id")
        )

    async def get_active_key(self, service: str, user_id: Optional[str] = None) -> str:
        """Get the active API key for a service"""
        query = {"service": service, "active": True}
        if user_id:
            query["user_id"] = user_id

        key_record = await self.db.api_keys.find_one(query)
        if not key_record:
            raise ValueError(f"No active key found for service {service}")

        return self.key_encryption.decrypt_key(key_record["key"])
```

## Request/Response Security

### HTTPS Enforcement

```python
from fastapi import FastAPI
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware

app = FastAPI()

# Only enable in production
if not settings.DEBUG:
    app.add_middleware(HTTPSRedirectMiddleware)
```

### Content Security Policy

```python
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)

        # Set security headers
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Only set HSTS in production
        if not settings.DEBUG:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        return response

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS
)
```

## Implementation Timeline

1. **Week 1**: Input validation and API key management
2. **Week 2**: Rate limiting and security headers
3. **Week 3**: Testing and refinement

## Dependencies

- FastAPI for API framework
- Pydantic for validation
- Redis for rate limiting
- Cryptography for key encryption
