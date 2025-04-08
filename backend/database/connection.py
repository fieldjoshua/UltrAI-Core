"""
Database connection module for PostgreSQL integration with SQLAlchemy.

This module manages the database connection pool and provides session management
for interacting with the PostgreSQL database.
"""

import os
from contextlib import contextmanager
from typing import Any, Generator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

from backend.utils.logging import get_logger

# Set up logger
logger = get_logger("database", "logs/database.log")

# Create declarative base for models
Base = declarative_base()

# Database connection configuration
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = os.environ.get("DB_PORT", "5432")
DB_NAME = os.environ.get("DB_NAME", "ultra")
DB_USER = os.environ.get("DB_USER", "ultrauser")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "ultrapassword")

# Create database URL
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Global engine instance
_engine: Engine = None

# Session factory
SessionLocal = None


def get_engine() -> Engine:
    """
    Get or create SQLAlchemy engine instance.

    Returns:
        SQLAlchemy engine instance
    """
    global _engine

    if _engine is None:
        logger.info(f"Creating database engine for {DB_HOST}:{DB_PORT}/{DB_NAME}")

        # Create engine with connection pooling
        _engine = create_engine(
            DATABASE_URL,
            pool_size=5,
            max_overflow=10,
            pool_timeout=30,  # seconds
            pool_recycle=1800,  # 30 minutes
            echo=False,  # Set to True for SQL logging (development only)
        )

    return _engine


def init_db() -> None:
    """
    Initialize the database connection and session factory.

    This should be called at application startup.
    """
    global SessionLocal

    # Get or create engine
    engine = get_engine()

    # Create session factory
    SessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )

    logger.info("Database session factory initialized")


def create_tables() -> None:
    """
    Create all tables defined in models.

    This should only be used for development or testing.
    For production, use Alembic migrations.
    """
    engine = get_engine()
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created")


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """
    Get a database session as a context manager.

    Yields:
        SQLAlchemy session

    Example:
        ```
        with get_db_session() as session:
            users = session.query(User).all()
        ```
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Database session error: {str(e)}")
        raise
    finally:
        session.close()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency for FastAPI to get a database session.

    Yields:
        SQLAlchemy session

    Example:
        ```
        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            return db.query(User).all()
        ```
    """
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def check_database_connection() -> bool:
    """
    Check if database connection is working.

    Returns:
        True if connection is successful, False otherwise
    """
    try:
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        return True
    except Exception as e:
        logger.error(f"Database connection error: {str(e)}")
        return False