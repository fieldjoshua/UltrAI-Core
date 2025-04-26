"""
Base class for SQLAlchemy models.

This module provides the SQLAlchemy declarative base class for ORM models.
"""

from sqlalchemy.ext.declarative import declarative_base

# Create a base class for models
Base = declarative_base()
