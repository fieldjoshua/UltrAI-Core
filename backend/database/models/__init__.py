"""
Database models for the Ultra backend.

This package contains the SQLAlchemy ORM models for database entities.
"""

from sqlalchemy.orm import declarative_base

Base = declarative_base()

from .user import User  # noqa
from .document import Document  # noqa
from .analysis import Analysis  # noqa

__all__ = ["Base", "User", "Document", "Analysis"]
