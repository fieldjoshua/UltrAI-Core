"""
Authentication models for the Ultra backend.

This module defines Pydantic models for authentication-related data structures.
"""

from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Base user model with common fields"""

    email: EmailStr = Field(..., description="User email address")
    name: Optional[str] = Field(None, description="User's full name")


class UserCreate(UserBase):
    """User registration model"""

    password: str = Field(..., min_length=8, description="User password")


class UserLogin(BaseModel):
    """User login model"""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class UserDB(UserBase):
    """User database model"""

    id: str = Field(..., description="User ID")
    hashed_password: str = Field(..., description="Hashed password")
    is_active: bool = Field(True, description="Whether the user account is active")
    is_verified: bool = Field(False, description="Whether the user's email is verified")


class User(UserBase):
    """User model returned to clients"""

    id: str = Field(..., description="User ID")
    is_active: bool = Field(..., description="Whether the user account is active")


class TokenData(BaseModel):
    """Token data model"""

    sub: Optional[str] = Field(None, description="Subject (user ID)")
    exp: Optional[int] = Field(None, description="Expiration time")
    type: Optional[str] = Field(None, description="Token type")


class TokenResponse(BaseModel):
    """Token response model"""

    status: str = Field("success", description="Response status")
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field("bearer", description="Token type")
    expires_in: Optional[int] = Field(
        None, description="Token expiration time in seconds"
    )


class RefreshTokenRequest(BaseModel):
    """Refresh token request model"""

    refresh_token: str = Field(..., description="JWT refresh token")


class PasswordResetRequest(BaseModel):
    """Password reset request model"""

    email: EmailStr = Field(..., description="User email address")


class PasswordReset(BaseModel):
    """Password reset model"""

    token: str = Field(..., description="Password reset token")
    new_password: str = Field(..., min_length=8, description="New user password")


class MessageResponse(BaseModel):
    """Generic message response model"""

    status: str = Field(..., description="Response status")
    message: str = Field(..., description="Response message")
    user_id: Optional[str] = Field(None, description="User ID (if applicable)")
