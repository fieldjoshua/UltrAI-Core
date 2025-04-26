"""
Database module for the Ultra backend.

This module provides database connectivity and models for the Ultra backend.
"""

import os
from typing import Optional

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from backend.config import Config
from backend.database.models import Base
from backend.database.repositories import (
    AnalysisRepository,
    DocumentChunkRepository,
    DocumentRepository,
    UserRepository,
)

# Create database engine
engine = create_engine(
    Config.DATABASE_URL,
    echo=Config.DEBUG,
    pool_pre_ping=True,
    pool_recycle=3600,
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

__all__ = [
    "init_db",
    "get_db",
    "check_database_connection",
    "UserRepository",
    "DocumentRepository",
    "DocumentChunkRepository",
    "AnalysisRepository",
]


def init_db():
    """Initialize the database by creating all tables."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Get a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_database_connection() -> bool:
    """Check if the database connection is working."""
    try:
        # Try to create a session and execute a simple query
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        return True
    except Exception:
        return False
