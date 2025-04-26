from typing import Any, ClassVar
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy import Column, DateTime, Boolean, JSON, String
from sqlalchemy.sql import func
from uuid import uuid4


@as_declarative()
class Base:
    """Base class for all database models."""

    id: Any
    __name__: str

    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(cls) -> ClassVar[str]:
        return cls.__name__.lower()

    # Common columns for all models
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    is_active = Column(Boolean, default=True, nullable=False)
    metadata = Column(JSON, default=dict, nullable=False)
