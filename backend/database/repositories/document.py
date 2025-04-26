"""Document repository for the Ultra backend.

This module provides data access operations for document-related models.
"""

import logging
from typing import List, Optional

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.database.models.document import Document, DocumentChunk
from backend.database.repositories.base import BaseRepository
from backend.utils.exceptions import DatabaseException

logger = logging.getLogger(__name__)


class DocumentRepository(BaseRepository[Document]):
    """Repository for document operations."""

    def __init__(self):
        """Initialize the document repository."""
        super().__init__(Document)

    def get_by_filename(
        self, db: Session, filename: str, user_id: str
    ) -> Optional[Document]:
        """Get a document by its filename and user ID.

        Args:
            db: Database session
            filename: The name of the file
            user_id: The ID of the user who owns the document

        Returns:
            The document if found, None otherwise
        """
        try:
            return (
                db.query(Document)
                .filter(Document.filename == filename, Document.user_id == user_id)
                .first()
            )
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving document by filename: {e}")
            raise DatabaseException(f"Failed to retrieve document: {str(e)}")

    def get_user_documents(
        self, db: Session, user_id: str, skip: int = 0, limit: int = 100
    ) -> List[Document]:
        """Get all documents for a specific user.

        Args:
            db: Database session
            user_id: The ID of the user
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return

        Returns:
            List of documents owned by the user
        """
        try:
            return (
                db.query(Document)
                .filter(Document.user_id == user_id)
                .offset(skip)
                .limit(limit)
                .all()
            )
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving user documents: {e}")
            raise DatabaseException(f"Failed to retrieve user documents: {str(e)}")

    def count_user_documents(self, db: Session, user_id: str) -> int:
        """Count the number of documents for a specific user.

        Args:
            db: Database session
            user_id: The ID of the user

        Returns:
            The count of documents
        """
        try:
            return db.query(Document).filter(Document.user_id == user_id).count()
        except SQLAlchemyError as e:
            logger.error(f"Error counting user documents: {e}")
            raise DatabaseException(f"Failed to count user documents: {str(e)}")

    def delete_user_documents(self, db: Session, user_id: str) -> int:
        """Delete all documents for a specific user.

        Args:
            db: Database session
            user_id: The ID of the user

        Returns:
            The number of documents deleted
        """
        try:
            documents = db.query(Document).filter(Document.user_id == user_id).all()
            count = len(documents)

            for doc in documents:
                db.delete(doc)

            db.commit()
            return count
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Error deleting user documents: {e}")
            raise DatabaseException(f"Failed to delete user documents: {str(e)}")


class DocumentChunkRepository(BaseRepository[DocumentChunk]):
    """Repository for document chunk operations."""

    def __init__(self):
        """Initialize the document chunk repository."""
        super().__init__(DocumentChunk)

    def get_chunks_by_document_id(
        self, db: Session, document_id: str, skip: int = 0, limit: int = 100
    ) -> List[DocumentChunk]:
        """Get all chunks for a specific document.

        Args:
            db: Database session
            document_id: The ID of the document
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return

        Returns:
            List of document chunks
        """
        try:
            return (
                db.query(DocumentChunk)
                .filter(DocumentChunk.document_id == document_id)
                .offset(skip)
                .limit(limit)
                .all()
            )
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving document chunks: {e}")
            raise DatabaseException(f"Failed to retrieve document chunks: {str(e)}")

    def count_chunks_by_document_id(self, db: Session, document_id: str) -> int:
        """Count the number of chunks for a specific document.

        Args:
            db: Database session
            document_id: The ID of the document

        Returns:
            The count of document chunks
        """
        try:
            return (
                db.query(DocumentChunk)
                .filter(DocumentChunk.document_id == document_id)
                .count()
            )
        except SQLAlchemyError as e:
            logger.error(f"Error counting document chunks: {e}")
            raise DatabaseException(f"Failed to count document chunks: {str(e)}")

    def delete_document_chunks(self, db: Session, document_id: str) -> int:
        """Delete all chunks for a specific document.

        Args:
            db: Database session
            document_id: The ID of the document

        Returns:
            The number of chunks deleted
        """
        try:
            chunks = (
                db.query(DocumentChunk)
                .filter(DocumentChunk.document_id == document_id)
                .all()
            )
            count = len(chunks)

            for chunk in chunks:
                db.delete(chunk)

            db.commit()
            return count
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Error deleting document chunks: {e}")
            raise DatabaseException(f"Failed to delete document chunks: {str(e)}")
