"""
Alembic environment module for database migrations.

This module configures the Alembic environment and defines how migrations are run.
"""

import os
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

# Add the parent directory to the path so we can import backend.models as models
sys.path.insert(
    0,
    os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ),
)

# Import database connection settings
from backend.database.connection import (
    DATABASE_URL,
    DB_HOST,
    DB_NAME,
    DB_PASSWORD,
    DB_PORT,
    DB_USER,
)

# Import the SQLAlchemy base
from backend.database.models.base import Base

# Alembic Config object, which provides access to values in the .ini file
config = context.config

# Override the sqlalchemy.url from the alembic.ini file with our actual connection URL
config.set_main_option("sqlalchemy.url", DATABASE_URL)

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

from backend.database.models.analysis import Analysis, AnalysisResult
from backend.database.models.document import Document, DocumentChunk

# Import all models to ensure they're included in the migration
from backend.database.models.user import ApiKey, User

# Set target metadata to Base.metadata
target_metadata = Base.metadata


def get_url():
    """Get database URL from environment variables or default to the one in alembic.ini."""
    return DATABASE_URL


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.
    """
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    # Use connection string from the config
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_url()

    # Create the engine
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            # Use transaction per migration to ensure atomic upgrades
            transaction_per_migration=True,
            # Compare types to catch subtle schema changes
            compare_type=True,
            # Compare server default values
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
