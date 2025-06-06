"""Document service for the Ultra backend.

This module provides services for document-related operations, including
document upload, processing, and retrieval.
"""

import logging
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.database.repositories import DocumentChunkRepository, DocumentRepository
from app.utils.exceptions import ResourceNotFoundException

logger = logging.getLogger(__name__)


class DocumentService:
    """Service for document operations."""

    def __init__(self):
        """Initialize the document service."""
        self.document_repo = DocumentRepository()
        self.chunk_repo = DocumentChunkRepository()

    def get_user_documents(
        self, db: Session, user_id: str, skip: int = 0, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get documents for a specific user.

        Args:
            db: Database session
            user_id: The ID of the user
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of user documents with metadata
        """
        documents = self.document_repo.get_user_documents(db, user_id, skip, limit)

        # Convert to dictionary and add additional metadata
        result = []
        for doc in documents:
            doc_dict = {
                "id": doc.id,
                "filename": doc.filename,
                "content_type": doc.content_type,
                "size_bytes": doc.size_bytes,
                "created_at": doc.created_at.isoformat() if doc.created_at else None,
                "status": doc.status,
                "word_count": doc.word_count,
                "chunk_count": doc.chunk_count,
            }
            result.append(doc_dict)

        return result

    def get_document_by_id(
        self, db: Session, document_id: str, user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get a document by its ID.

        Args:
            db: Database session
            document_id: The ID of the document
            user_id: Optional user ID for access control

        Returns:
            Document with metadata

        Raises:
            ResourceNotFoundException: If the document doesn't exist
            PermissionError: If the user doesn't have access to the document
        """
        document = self.document_repo.get_by_id(
            db, document_id, raise_if_not_found=True
        )

        # Check if the user has access to this document
        if user_id and document.user_id != user_id:
            logger.warning(
                f"User {user_id} attempted to access document {document_id} owned by {document.user_id}"
            )
            raise PermissionError("User does not have access to this document")

        # Convert to dictionary and add additional metadata
        doc_dict = {
            "id": document.id,
            "user_id": document.user_id,
            "filename": document.filename,
            "content_type": document.content_type,
            "size_bytes": document.size_bytes,
            "created_at": (
                document.created_at.isoformat() if document.created_at else None
            ),
            "processed_at": (
                document.processed_at.isoformat() if document.processed_at else None
            ),
            "status": document.status,
            "word_count": document.word_count,
            "chunk_count": document.chunk_count,
            "embedding_model": document.embedding_model,
        }

        # Count chunks
        chunk_count = self.chunk_repo.count_chunks_by_document_id(db, document_id)
        doc_dict["actual_chunk_count"] = chunk_count

        return doc_dict

    def delete_document(
        self, db: Session, document_id: str, user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Delete a document and its chunks.

        Args:
            db: Database session
            document_id: The ID of the document
            user_id: Optional user ID for access control

        Returns:
            Metadata about the deleted document

        Raises:
            ResourceNotFoundException: If the document doesn't exist
            PermissionError: If the user doesn't have access to the document
        """
        document = self.document_repo.get_by_id(
            db, document_id, raise_if_not_found=True
        )

        # Check if the user has access to this document
        if user_id and document.user_id != user_id:
            logger.warning(
                f"User {user_id} attempted to delete document {document_id} owned by {document.user_id}"
            )
            raise PermissionError("User does not have access to this document")

        # First delete all chunks
        chunks_deleted = self.chunk_repo.delete_document_chunks(db, document_id)

        # Then delete the document
        self.document_repo.delete(db, id=document_id)

        return {
            "id": document_id,
            "filename": document.filename,
            "chunks_deleted": chunks_deleted,
            "status": "deleted",
        }

    def get_document_chunks(
        self,
        db: Session,
        document_id: str,
        skip: int = 0,
        limit: int = 100,
        user_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get chunks for a specific document.

        Args:
            db: Database session
            document_id: The ID of the document
            skip: Number of records to skip
            limit: Maximum number of records to return
            user_id: Optional user ID for access control

        Returns:
            List of document chunks with content

        Raises:
            ResourceNotFoundException: If the document doesn't exist
            PermissionError: If the user doesn't have access to the document
        """
        document = self.document_repo.get_by_id(
            db, document_id, raise_if_not_found=True
        )

        # Check if the user has access to this document
        if user_id and document.user_id != user_id:
            logger.warning(
                f"User {user_id} attempted to access chunks for document {document_id} owned by {document.user_id}"
            )
            raise PermissionError("User does not have access to this document")

        chunks = self.chunk_repo.get_chunks_by_document_id(db, document_id, skip, limit)

        # Convert to dictionary and exclude embedding vectors (they can be large)
        result = []
        for chunk in chunks:
            chunk_dict = {
                "id": chunk.id,
                "document_id": chunk.document_id,
                "chunk_index": chunk.chunk_index,
                "content": chunk.content,
                "metadata": chunk.chunk_metadata,
                "page_number": chunk.page_number,
                "embedding_model": chunk.embedding_model,
            }
            result.append(chunk_dict)

        return result
