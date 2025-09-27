"""
Database session management for UltraAI Core.

This module provides SQLAlchemy session factory and dependency injection.
"""

import os
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import NullPool, QueuePool

from app.utils.logging import get_logger

logger = get_logger(__name__)


def get_database_url() -> str:
    """Get database URL from environment or use default."""
    database_url = os.getenv("DATABASE_URL", "sqlite:///./ultrai_dev.db")

    # Handle Render.com PostgreSQL URL format
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    return database_url


def create_session_factory() -> sessionmaker:
    """Create SQLAlchemy session factory."""
    database_url = get_database_url()

    # Handle empty or invalid database URL for tests
    if not database_url or database_url == "":
        raise ValueError("Invalid or empty DATABASE_URL")

    # Configure engine based on database type
    if "sqlite" in database_url:
        # SQLite configuration
        engine = create_engine(
            database_url,
            connect_args={"check_same_thread": False},
            poolclass=NullPool,  # Disable pooling for SQLite
            echo=os.getenv("SQL_ECHO", "false").lower() == "true",
        )
    else:
        # PostgreSQL/MySQL configuration
        engine = create_engine(
            database_url,
            poolclass=QueuePool,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,  # Verify connections before using
            echo=os.getenv("SQL_ECHO", "false").lower() == "true",
        )

    # Create session factory
    session_factory = sessionmaker(
        bind=engine,
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
    )

    return session_factory


# Global session factory
try:
    SessionLocal = create_session_factory()
except Exception as e:
    logger.warning(f"Failed to create database session factory: {e}")
    # Create a dummy session factory for tests
    SessionLocal = sessionmaker()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency to get database session.

    Yields:
        Database session that auto-closes after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """
    Context manager for database sessions.

    Usage:
        with get_db_session() as db:
            # Use db session
            pass
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Initialize database tables."""
    from app.database.models import Base

    database_url = get_database_url()

    # Create engine
    if "sqlite" in database_url:
        engine = create_engine(
            database_url,
            connect_args={"check_same_thread": False},
        )
    else:
        engine = create_engine(database_url)

    # Create all tables
    Base.metadata.create_all(bind=engine)
    logger.info(f"Database tables created at {database_url}")


def check_db_connection() -> bool:
    """
    Check if database connection is working.
    
    Returns:
        True if connection successful, False otherwise.
    """
    try:
        with get_db_session() as db:
            # Execute simple query
            db.execute("SELECT 1")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {str(e)}")
        return False
