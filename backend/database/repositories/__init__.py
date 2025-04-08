"""
Database repositories for the Ultra backend.

This module contains repository classes for interacting with the database models.
Repositories provide an abstraction layer over the database operations and implement
the Repository pattern, allowing for cleaner code and easier testing.

Available repositories:
- BaseRepository: Generic base class with common CRUD operations
- UserRepository: Operations for user management
- DocumentRepository: Operations for document metadata
- DocumentChunkRepository: Operations for document chunks and embeddings
- AnalysisRepository: Operations for analysis results
"""

from backend.database.repositories.base import BaseRepository
from backend.database.repositories.user import UserRepository
from backend.database.repositories.document import DocumentRepository, DocumentChunkRepository
from backend.database.repositories.analysis import AnalysisRepository

__all__ = [
    "BaseRepository",
    "UserRepository",
    "DocumentRepository",
    "DocumentChunkRepository",
    "AnalysisRepository",
]