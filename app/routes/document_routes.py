"""
Route handlers for the Ultra backend.
"""

import logging
from typing import Dict
from fastapi import APIRouter, Depends, HTTPException, status
import os
from fastapi.responses import JSONResponse


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

    return router


document_router = create_router()  # Expose router for application
