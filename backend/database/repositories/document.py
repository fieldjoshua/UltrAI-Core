"""
Document repository for the Ultra backend.

This module provides repositories for document-related database operations.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any

from sqlalchemy import desc
from sqlalchemy.orm import Session

from backend.database.models.document import Document, DocumentChunk, DocumentStatus
from backend.database.repositories.base import BaseRepository
from backend.utils.logging import get_logger

logger = get_logger("database.document_repository", "logs/database.log")


class DocumentRepository(BaseRepository[Document]):
    """Repository for document operations"""

    def __init__(self):
        super().__init__(Document)

    def get_by_uuid(self, db: Session, uuid: str) -> Optional[Document]:
        """
        Get a document by its UUID

        Args:
            db: Database session
            uuid: Document UUID

        Returns:
            The document if found, None otherwise
        """
        try:
            return db.query(Document).filter(Document.uuid == uuid).first()
        except Exception as e:
            logger.error(f"Error getting document with UUID {uuid}: {str(e)}")
            return None

    def get_user_documents(
        self, db: Session, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[Document]:
        """
        Get documents for a specific user

        Args:
            db: Database session
            user_id: User ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of user documents
        """
        return (
            db.query(Document)
            .filter(Document.user_id == user_id)
            .order_by(desc(Document.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def update_status(
        self,
        db: Session,
        document_id: int,
        status: DocumentStatus,
        error_message: Optional[str] = None
    ) -> Document:
        """
        Update document status

        Args:
            db: Database session
            document_id: Document ID
            status: New status
            error_message: Optional error message

        Returns:
            The updated document
        """
        document = self.get_by_id(db, document_id, raise_if_not_found=True)

        update_data = {"status": status}
        if error_message is not None:
            update_data["error_message"] = error_message

        if status == DocumentStatus.PROCESSED:
            update_data["processed_at"] = datetime.utcnow()

        return self.update(db, db_obj=document, obj_in=update_data)

    def update_processing_metadata(
        self,
        db: Session,
        document_id: int,
        word_count: Optional[int] = None,
        chunk_count: Optional[int] = None,
        embedding_model: Optional[str] = None
    ) -> Document:
        """
        Update document processing metadata

        Args:
            db: Database session
            document_id: Document ID
            word_count: Total word count
            chunk_count: Number of chunks
            embedding_model: Name of embedding model used

        Returns:
            The updated document
        """
        document = self.get_by_id(db, document_id, raise_if_not_found=True)

        update_data = {}
        if word_count is not None:
            update_data["word_count"] = word_count
        if chunk_count is not None:
            update_data["chunk_count"] = chunk_count
        if embedding_model is not None:
            update_data["embedding_model"] = embedding_model

        return self.update(db, db_obj=document, obj_in=update_data)


class DocumentChunkRepository(BaseRepository[DocumentChunk]):
    """Repository for document chunk operations"""

    def __init__(self):
        super().__init__(DocumentChunk)

    def get_document_chunks(
        self, db: Session, document_id: int, skip: int = 0, limit: int = 100
    ) -> List[DocumentChunk]:
        """
        Get chunks for a specific document

        Args:
            db: Database session
            document_id: Document ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of document chunks
        """
        return (
            db.query(DocumentChunk)
            .filter(DocumentChunk.document_id == document_id)
            .order_by(DocumentChunk.chunk_index)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def add_chunk(
        self,
        db: Session,
        document_id: int,
        chunk_index: int,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        page_number: Optional[int] = None,
        embedding: Optional[Dict[str, Any]] = None,
        embedding_model: Optional[str] = None
    ) -> DocumentChunk:
        """
        Add a new document chunk

        Args:
            db: Database session
            document_id: Document ID
            chunk_index: Chunk index
            content: Text content
            metadata: Optional chunk metadata
            page_number: Optional page number
            embedding: Optional embedding vector
            embedding_model: Optional embedding model name

        Returns:
            The created document chunk
        """
        chunk_data = {
            "document_id": document_id,
            "chunk_index": chunk_index,
            "content": content,
        }

        if metadata is not None:
            chunk_data["metadata"] = metadata
        if page_number is not None:
            chunk_data["page_number"] = page_number
        if embedding is not None:
            chunk_data["embedding"] = embedding
        if embedding_model is not None:
            chunk_data["embedding_model"] = embedding_model

        return self.create(db, chunk_data)

    def update_embedding(
        self,
        db: Session,
        chunk_id: int,
        embedding: Dict[str, Any],
        embedding_model: str
    ) -> DocumentChunk:
        """
        Update embedding for a document chunk

        Args:
            db: Database session
            chunk_id: Chunk ID
            embedding: Embedding vector
            embedding_model: Embedding model name

        Returns:
            The updated document chunk
        """
        chunk = self.get_by_id(db, chunk_id, raise_if_not_found=True)

        update_data = {
            "embedding": embedding,
            "embedding_model": embedding_model
        }

        return self.update(db, db_obj=chunk, obj_in=update_data)