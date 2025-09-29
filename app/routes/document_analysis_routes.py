"""
Route handlers for the Ultra backend.
"""

from fastapi import APIRouter, HTTPException, status
import os


def create_router() -> APIRouter:
    """
    Create the router with all endpoints.

    Returns:
        APIRouter: The configured router
    """
    router = APIRouter(tags=["Document_Analysis"])

    # Feature gate: return 501 for analysis endpoints when RAG is disabled
    rag_enabled = os.getenv("RAG_ENABLED", "false").lower() == "true"
    if not rag_enabled:
        @router.post("/documents/{document_id}/analyze")
        async def _analyze_disabled(document_id: str):
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail="Document analysis is disabled",
            )

    return router


document_analysis_router = create_router()  # Expose router for application
