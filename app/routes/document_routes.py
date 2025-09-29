"""
Route handlers for the Ultra backend.
"""

import logging
from typing import Dict, List
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
import os
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.services.document_service import DocumentService
from app.middleware.auth_dependencies import get_current_user


logger = logging.getLogger(__name__)


def create_router(document_processor=None) -> APIRouter:
    """
    Create the router with all endpoints.

    Returns:
        APIRouter: The configured router
    """
    router = APIRouter(tags=["Document"])

    # Feature gate: return 501 for all document endpoints when RAG is disabled
    rag_enabled = os.getenv("RAG_ENABLED", "false").lower() == "true"
    if not rag_enabled:

        @router.get("/documents")
        async def _documents_disabled():
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail="Document features are disabled",
            )

        @router.post("/documents/upload")
        async def _upload_disabled():
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail="Document features are disabled",
            )

        @router.delete("/documents/{document_id}")
        async def _delete_disabled(document_id: str):
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail="Document features are disabled",
            )

        @router.get("/documents/{document_id}")
        async def _get_document_disabled(document_id: str):
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail="Document features are disabled",
            )

        @router.get("/documents/{document_id}/chunks")
        async def _get_chunks_disabled(document_id: str):
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail="Document features are disabled",
            )
    else:
        # RAG is enabled - implement actual functionality
        document_service = DocumentService()

        @router.get("/documents", response_model=List[Dict])
        async def get_user_documents(
            skip: int = 0,  # noqa: E251,E252
            limit: int = 100,  # noqa: E251,E252
            db: Session = Depends(get_db),  # noqa: E251,E252
            current_user = Depends(get_current_user)  # noqa: E251,E252
        ):
            """Get all documents for the current user."""
            try:
                user_id: str = str(getattr(current_user, "id", ""))
                documents = document_service.get_user_documents(
                    db, user_id, skip, limit
                )
                return documents
            except Exception as e:
                logger.error(f"Error retrieving documents for user {getattr(current_user, 'id', 'unknown')}: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to retrieve documents"
                )

        @router.get("/documents/{document_id}", response_model=Dict)
        async def get_document(
            document_id: str,
            db: Session = Depends(get_db),  # noqa: E251,E252
            current_user = Depends(get_current_user)  # noqa: E251,E252
        ):
            """Get a specific document by ID."""
            try:
                user_id: str = str(getattr(current_user, "id", ""))
                document = document_service.get_document_by_id(
                    db, document_id, user_id
                )
                return document
            except PermissionError:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied to this document"
                )
            except Exception as e:
                logger.error(f"Error retrieving document {document_id}: {e}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Document not found"
                )

        @router.delete("/documents/{document_id}", response_model=Dict)
        async def delete_document(
            document_id: str,
            db: Session = Depends(get_db),  # noqa: E251,E252
            current_user = Depends(get_current_user)  # noqa: E251,E252
        ):
            """Delete a document and its chunks."""
            try:
                user_id: str = str(getattr(current_user, "id", ""))
                result = document_service.delete_document(
                    db, document_id, user_id
                )
                return result
            except PermissionError:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied to this document"
                )
            except Exception as e:
                logger.error(f"Error deleting document {document_id}: {e}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Document not found"
                )

        @router.get("/documents/{document_id}/chunks", response_model=List[Dict])
        async def get_document_chunks(
            document_id: str,
            skip: int = 0,  # noqa: E251,E252
            limit: int = 100,  # noqa: E251,E252
            db: Session = Depends(get_db),  # noqa: E251,E252
            current_user = Depends(get_current_user)  # noqa: E251,E252
        ):
            """Get chunks for a specific document."""
            try:
                user_id: str = str(getattr(current_user, "id", ""))
                chunks = document_service.get_document_chunks(
                    db, document_id, skip, limit, user_id
                )
                return chunks
            except PermissionError:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied to this document"
                )
            except Exception as e:
                logger.error(f"Error retrieving chunks for document {document_id}: {e}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Document not found"
                )

        @router.post("/documents/upload", response_model=Dict)
        async def upload_document(
            file: UploadFile = File(...),  # noqa: E251,E252
            db: Session = Depends(get_db),  # noqa: E251,E252
            current_user = Depends(get_current_user)  # noqa: E251,E252
        ):
            """Upload and process a new document."""
            try:
                # For now, return a placeholder response until document processor is fully implemented
                return {
                    "message": "Document upload functionality requires full RAG implementation",
                    "filename": file.filename,
                    "content_type": file.content_type,
                    "status": "pending_implementation"
                }
            except Exception as e:
                logger.error(f"Error uploading document: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to upload document"
                )

    return router


document_router = create_router()  # Expose router for application
