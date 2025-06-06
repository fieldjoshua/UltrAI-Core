"""Database configuration for production environment."""

import os
from typing import Dict
from urllib.parse import urlparse

from sqlalchemy.engine.url import URL

from backend.utils.logging import get_logger

logger = get_logger("database_config")


def parse_database_url(url: str) -> Dict[str, any]:
    """Parse database URL into components."""
    parsed = urlparse(url)
    
    # Extract components
    components = {
        "drivername": "postgresql",
        "username": parsed.username,
        "password": parsed.password,
        "host": parsed.hostname,
        "port": parsed.port or 5432,
        "database": parsed.path.lstrip("/") if parsed.path else None,
    }
    
    # Parse query parameters for additional options
    if parsed.query:
        import urllib.parse
        query_params = urllib.parse.parse_qs(parsed.query)
        components["query"] = {k: v[0] for k, v in query_params.items()}
    
    return components


def get_database_config() -> Dict[str, any]:
    """Get database configuration from environment variables."""
    db_url = os.environ.get("DATABASE_URL", "")
    
    if not db_url:
        logger.warning("DATABASE_URL not configured, using default SQLite database")
        return {
            "url": "sqlite:///./test.db",
            "pool_size": 5,
            "max_overflow": 10,
            "pool_timeout": 30,
            "pool_recycle": 3600,
        }
    
    # Parse the database URL
    components = parse_database_url(db_url)
    
    # Get pool configuration from environment
    pool_size = int(os.environ.get("DATABASE_POOL_SIZE", "20"))
    max_overflow = int(os.environ.get("DATABASE_MAX_OVERFLOW", "10"))
    pool_timeout = int(os.environ.get("DATABASE_POOL_TIMEOUT", "30"))
    pool_recycle = int(os.environ.get("CONNECTION_POOL_RECYCLE", "3600"))
    
    # Additional production settings
    config = {
        "url": URL.create(**components),
        "pool_size": pool_size,
        "max_overflow": max_overflow,
        "pool_timeout": pool_timeout,
        "pool_recycle": pool_recycle,
        "pool_pre_ping": True,  # Test connections before using them
        "echo": False,  # Disable SQL logging in production
    }
    
    # SSL configuration for production
    if os.environ.get("DATABASE_SSL_MODE", "require") == "require":
        config["connect_args"] = {
            "sslmode": "require",
            "sslcert": os.environ.get("DATABASE_SSL_CERT"),
            "sslkey": os.environ.get("DATABASE_SSL_KEY"),
            "sslrootcert": os.environ.get("DATABASE_SSL_ROOT_CERT"),
        }
    
    return config


def get_alembic_config() -> Dict[str, str]:
    """Get Alembic migration configuration."""
    db_url = os.environ.get("DATABASE_URL", "sqlite:///./test.db")
    
    return {
        "script_location": "backend/database/migrations",
        "prepend_sys_path": ".",
        "version_path_separator": os.pathsep,
        "sqlalchemy.url": db_url,
    }


def test_database_connection(config: Dict[str, any]) -> bool:
    """Test database connection with given configuration."""
    from sqlalchemy import create_engine, text
    
    try:
        # Create engine with the configuration
        engine = create_engine(
            config["url"],
            pool_size=config.get("pool_size", 5),
            max_overflow=config.get("max_overflow", 10),
            pool_timeout=config.get("pool_timeout", 30),
            pool_recycle=config.get("pool_recycle", 3600),
            pool_pre_ping=config.get("pool_pre_ping", True),
            echo=config.get("echo", False),
            connect_args=config.get("connect_args", {}),
        )
        
        # Test the connection
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            result.fetchone()
        
        logger.info("Database connection test successful")
        return True
    except Exception as e:
        logger.error(f"Database connection test failed: {str(e)}")
        return False