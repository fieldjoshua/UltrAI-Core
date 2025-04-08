"""
Database module for the Ultra backend.

This module provides database connectivity and models for the Ultra backend.
"""

from backend.database.connection import init_db, get_db, check_database_connection
from backend.database.repositories import (
    UserRepository,
    DocumentRepository,
    DocumentChunkRepository,
    AnalysisRepository
)

__all__ = [
    "init_db",
    "get_db",
    "check_database_connection",
    "UserRepository",
    "DocumentRepository",
    "DocumentChunkRepository",
    "AnalysisRepository"
]