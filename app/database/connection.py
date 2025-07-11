"""
Database connection module for PostgreSQL integration with SQLAlchemy.

This module manages the database connection pool and provides session management
for interacting with the PostgreSQL database. It handles graceful degradation
when the database is not available by using an in-memory fallback.
"""

import os
from contextlib import contextmanager
from typing import Any, Generator

from app.utils.dependency_manager import sqlalchemy_dependency
from app.utils.logging import get_logger

# Set up logger
logger = get_logger("database", "logs/database.log")

def get_database_url():
    """
    Get database URL from environment variables at runtime.
    This ensures we read the environment variables when they're actually available.
    """
    # Render might use different variable names for managed databases
    possible_db_url_vars = [
        "DATABASE_URL",          # Standard PostgreSQL URL
        "POSTGRES_URL",          # Alternative naming
        "POSTGRESQL_URL",        # Another alternative
        "DATABASE_CONNECTION_STRING",  # Descriptive naming
        "DB_URL"                 # Short form
    ]

    database_url = None
    found_var_name = None

    for var_name in possible_db_url_vars:
        database_url = os.environ.get(var_name)
        if database_url:
            found_var_name = var_name
            break

    # Debug logging to understand what's happening
    logger.info(f"Database environment variables checked: {possible_db_url_vars}")
    if database_url:
        logger.info(f"Found database URL in variable: {found_var_name}")
        # Don't log the full URL for security, just confirm it's not localhost
        is_localhost = "localhost" in database_url.lower() or "127.0.0.1" in database_url
        logger.info(f"Database URL points to localhost: {is_localhost}")
        return database_url
    else:
        logger.warning("No database URL found in any environment variables, using individual DB_* variables")
        # Log available environment variables that might be database-related
        db_related_vars = [k for k in os.environ.keys() if any(keyword in k.upper() for keyword in ["DB", "DATABASE", "POSTGRES"])]
        logger.info(f"Available database-related environment variables: {db_related_vars}")
        
        # Fallback to individual environment variables for local development
        db_host = os.environ.get("DB_HOST", "localhost")
        db_port = os.environ.get("DB_PORT", "5432")
        db_name = os.environ.get("DB_NAME", "ultra")
        db_user = os.environ.get("DB_USER", "ultrauser")
        db_password = os.environ.get("DB_PASSWORD", "ultrapassword")
        
        # Create database URL from individual components
        return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

# Configuration for fallback
ENABLE_DB_FALLBACK = os.getenv("ENABLE_DB_FALLBACK", "true").lower() in (
    "true",
    "1",
    "yes",
)
DB_CONNECTION_TIMEOUT = int(os.getenv("DB_CONNECTION_TIMEOUT", "5"))  # Seconds

# Global engine instance
_engine = None

# Session factory
SessionLocal = None

# Fallback flag
_use_fallback = False


def get_engine():
    """
    Get or create SQLAlchemy engine instance.

    Returns:
        SQLAlchemy engine instance
    """
    global _engine, _use_fallback

    # Check if SQLAlchemy is available
    if not sqlalchemy_dependency.is_available():
        logger.warning("SQLAlchemy not available, using in-memory database fallback")
        _use_fallback = True
        return None

    # If fallback is already active, don't try to create an engine
    if _use_fallback:
        return None

    # If engine exists, return it
    if _engine is not None:
        return _engine

    try:
        # Get database URL at runtime
        database_url = get_database_url()
        logger.info(f"Creating database engine with runtime URL (first 20 chars): {database_url[:20]}...")

        # Import SQLAlchemy dynamically
        sqlalchemy = sqlalchemy_dependency.get_module()

        # Create engine with connection pooling
        _engine = sqlalchemy.create_engine(
            database_url,
            pool_size=5,
            max_overflow=10,
            pool_timeout=30,  # seconds
            pool_recycle=1800,  # 30 minutes
            connect_args={"connect_timeout": DB_CONNECTION_TIMEOUT},
            echo=False,  # Set to True for SQL logging (development only)
        )

        # Try to connect to verify connection works
        with _engine.connect() as conn:
            conn.execute(sqlalchemy.text("SELECT 1"))

        logger.info("Database engine created successfully")

        return _engine
    except Exception as e:
        logger.error(f"Error creating database engine: {str(e)}")

        if ENABLE_DB_FALLBACK:
            logger.warning("Using in-memory database fallback due to connection error")
            _use_fallback = True
            return None
        else:
            logger.critical(
                "Database fallback is disabled, cannot continue without database"
            )
            raise


def init_db() -> None:
    """
    Initialize the database connection and session factory.

    This should be called at application startup.
    """
    global SessionLocal, _use_fallback

    # Check if SQLAlchemy is available
    if not sqlalchemy_dependency.is_available():
        logger.warning("SQLAlchemy not available, using in-memory database fallback")
        _use_fallback = True

        try:
            # Import fallback dynamically
            from app.database.fallback import fallback_session

            SessionLocal = fallback_session
        except ImportError as e:
            logger.error(f"Error importing fallback database module: {str(e)}")
            raise

        return

    try:
        # Get or create engine
        engine = get_engine()

        if engine is None:
            # Using fallback
            from app.database.fallback import fallback_session

            SessionLocal = fallback_session
            return

        # Import SQLAlchemy dynamically
        sqlalchemy = sqlalchemy_dependency.get_module()

        # Create session factory
        SessionLocal = sqlalchemy.orm.sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=engine,
        )

        logger.info("Database session factory initialized with PostgreSQL")
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")

        if ENABLE_DB_FALLBACK:
            logger.warning(
                "Using in-memory database fallback due to initialization error"
            )
            _use_fallback = True

            try:
                # Import fallback dynamically
                from app.database.fallback import fallback_session

                SessionLocal = fallback_session
            except ImportError as e2:
                logger.error(f"Error importing fallback database module: {str(e2)}")
                raise e2
        else:
            logger.critical(
                "Database fallback is disabled, cannot continue without database"
            )
            raise


def create_tables() -> None:
    """
    Create all tables defined in models.

    This should only be used for development or testing.
    For production, use Alembic migrations.
    """
    if _use_fallback:
        logger.warning("Using in-memory database, tables are created on-demand")
        return

    if not sqlalchemy_dependency.is_available():
        logger.warning("SQLAlchemy not available, cannot create tables")
        return

    engine = get_engine()
    if engine is None:
        logger.warning("Database engine not available, cannot create tables")
        return

    try:
        # Import Base and create tables
        from app.database.models.base import Base

        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created")
    except Exception as e:
        logger.error(f"Error creating database tables: {str(e)}")

        if not ENABLE_DB_FALLBACK:
            raise


@contextmanager
def get_db_session() -> Generator[Any, None, None]:
    """
    Get a database session as a context manager.

    Yields:
        SQLAlchemy session or fallback session

    Example:
        ```
        with get_db_session() as session:
            users = session.query(User).all()
        ```
    """
    if SessionLocal is None:
        raise RuntimeError(
            "Database session factory not initialized. Call init_db() first."
        )

    if _use_fallback:
        # Using fallback session
        with SessionLocal() as session:
            yield session
    else:
        # Using SQLAlchemy session
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


def get_db() -> Generator[Any, None, None]:
    """
    Dependency for FastAPI to get a database session.

    Yields:
        SQLAlchemy session or fallback session

    Example:
        ```
        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            return db.query(User).all()
        ```
    """
    if SessionLocal is None:
        msg = "Database session factory not initialized. Call init_db() first."
        raise RuntimeError(msg)

    if _use_fallback:
        # Using fallback session
        with SessionLocal() as session:
            yield session
    else:
        # Using SQLAlchemy session
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
    if _use_fallback:
        # We're using fallback, so connection is "working" in fallback mode
        logger.info("Using in-memory database fallback, connection check passed")
        return True

    if not sqlalchemy_dependency.is_available():
        logger.warning("SQLAlchemy not available, cannot check database connection")
        return False

    try:
        engine = get_engine()
        if engine is None:
            return False

        sqlalchemy = sqlalchemy_dependency.get_module()

        with engine.connect() as conn:
            conn.execute(sqlalchemy.text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Database connection error: {str(e)}")
        return False


def is_using_fallback() -> bool:
    """
    Check if we're using the fallback database.

    Returns:
        True if using fallback, False if using PostgreSQL
    """
    return _use_fallback


def get_database_status() -> dict:
    """
    Get database connection status.

    Returns:
        Dictionary with database status information
    """
    status = {
        "connected": check_database_connection(),
        "using_fallback": _use_fallback,
        "fallback_enabled": ENABLE_DB_FALLBACK,
        "sqlalchemy_available": sqlalchemy_dependency.is_available(),
    }

    if not _use_fallback:
        # Add PostgreSQL-specific status
        status.update(
            {
                "host": DB_HOST,
                "port": DB_PORT,
                "database": DB_NAME,
                "user": DB_USER,
            }
        )
    else:
        # Add fallback-specific status
        try:
            from app.database.memory_db import memory_db

            status.update(
                {
                    "memory_db_status": memory_db.get_status(),
                }
            )
        except ImportError:
            status.update(
                {
                    "memory_db_status": "Not available",
                }
            )

    return status
