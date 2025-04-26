from typing import Optional
from pydantic import EmailStr, Field

from app.models.base import BaseDBModel, BaseResponseModel


class UserBase(BaseDBModel):
    """Base user model with common fields."""

    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = None
    is_superuser: bool = Field(default=False)
    is_verified: bool = Field(default=False)


class UserCreate(UserBase):
    """Model for creating a new user."""

    password: str = Field(..., min_length=8)


class UserUpdate(BaseDBModel):
    """Model for updating a user."""

    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    full_name: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8)
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None
    is_verified: Optional[bool] = None


class UserInDB(UserBase):
    """Model for user data in database."""

    hashed_password: str


class UserResponse(BaseResponseModel):
    """Model for user API responses."""

    data: UserBase
