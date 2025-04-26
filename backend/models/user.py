from typing import Any, Dict, Optional

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    """Base model for user information"""

    email: EmailStr
    name: Optional[str] = None


class UserCreate(UserBase):
    """Request model for creating a new user"""

    user_id: Optional[str] = None
    username: Optional[str] = None
    password: str
    tier: str = "basic"
    initial_balance: float = 0.0


class UserLogin(BaseModel):
    """Request model for user login"""

    email: EmailStr
    password: str


class OAuthUserLogin(BaseModel):
    """Request model for OAuth login"""

    provider: str


class UserUpdate(BaseModel):
    """Request model for updating user information"""

    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    tier: Optional[str] = None


class UserResponse(BaseModel):
    """Response model for user information"""

    user_id: str
    email: EmailStr
    username: Optional[str] = None
    name: Optional[str] = None
    tier: str
    created_at: str
    last_login: Optional[str] = None
    balance: Optional[float] = None
    settings: Optional[Dict[str, Any]] = None
    is_verified: Optional[bool] = None
    oauth_provider: Optional[str] = None


class TokenResponse(BaseModel):
    """Response model for authentication token"""

    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user_id: str
