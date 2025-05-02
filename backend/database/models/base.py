"""
Base SQLAlchemy model for database models.

This module provides the Base declarative base class for all SQLAlchemy models.
"""

from typing import Any, Dict
import uuid

from backend.utils.dependency_manager import sqlalchemy_dependency

# Check if SQLAlchemy is available
if sqlalchemy_dependency.is_available():
    sqlalchemy = sqlalchemy_dependency.get_module()
    declarative_base = sqlalchemy.orm.declarative_base
    Column = sqlalchemy.Column
    String = sqlalchemy.String
    DateTime = sqlalchemy.DateTime
    func = sqlalchemy.func
    
    class Base(declarative_base()):
        """Base class for all SQLAlchemy models."""
        
        __abstract__ = True
        
        def as_dict(self) -> Dict[str, Any]:
            """
            Convert model to dictionary.
            
            Returns:
                Dictionary representation of model
            """
            return {c.name: getattr(self, c.name) for c in self.__table__.columns}
            
        def update_from_dict(self, data: Dict[str, Any]) -> None:
            """
            Update model from dictionary.
            
            Args:
                data: Dictionary with model data
            """
            for key, value in data.items():
                if hasattr(self, key):
                    setattr(self, key, value)
else:
    # Provide dummy classes when SQLAlchemy is not available
    Base = object
    Column = lambda *args, **kwargs: None  # noqa: E731
    String = lambda *args, **kwargs: None  # noqa: E731
    DateTime = lambda *args, **kwargs: None  # noqa: E731
    func = type('func', (), {'now': lambda: None})