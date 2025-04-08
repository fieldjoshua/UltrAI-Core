from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any


class UserBase(BaseModel):
    """Base model for user information"""
    user_id: str
    email: EmailStr
    name: Optional[str] = None


class UserCreate(UserBase):
    """Request model for creating a new user"""
    password: str
    tier: str = "basic"
    initial_balance: float = 0.0


class UserLogin(BaseModel):
    """Request model for user login"""
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    """Request model for updating user information"""
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    tier: Optional[str] = None


class UserResponse(UserBase):
    """Response model for user information"""
    tier: str
    created_at: str
    last_login: Optional[str] = None
    balance: Optional[float] = None
    settings: Optional[Dict[str, Any]] = None


class TokenResponse(BaseModel):
    """Response model for authentication token"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user_id: str