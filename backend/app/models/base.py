from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class BaseDBModel(BaseModel):
    """Base model for all database models."""

    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        from_attributes = True


class BaseResponseModel(BaseModel):
    """Base model for all API responses."""

    success: bool = Field(default=True)
    message: Optional[str] = None
    data: Optional[Any] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        from_attributes = True


class BaseErrorModel(BaseModel):
    """Base model for all API error responses."""

    success: bool = Field(default=False)
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class BaseQueryModel(BaseModel):
    """Base model for all query parameters."""

    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=100)
    sort_by: Optional[str] = None
    sort_order: Optional[str] = Field(default="asc", pattern="^(asc|desc)$")
    search: Optional[str] = None
    filters: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        from_attributes = True
