"""
Database module for the Ultra backend.

This module provides database models, repositories, and connection management
for the PostgreSQL database.
"""

from backend.database.connection import (
    Base,
    init_db,
    get_db,
    get_db_session,
    check_database_connection,
    create_tables,
)

# For convenience, import models here
# This makes it possible to import models directly from backend.database
from backend.database.models.user import User
from backend.database.models.document import Document, DocumentChunk
from backend.database.models.analysis import Analysis

__all__ = [
    # Connection
    "Base",
    "init_db",
    "get_db",
    "get_db_session",
    "check_database_connection",
    "create_tables",

    # Models
    "User",
    "Document",
    "DocumentChunk",
    "Analysis",
]