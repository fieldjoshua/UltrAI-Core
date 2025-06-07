"""
Route handlers for the Ultra backend.
"""

from fastapi import APIRouter


def create_router() -> APIRouter:
    """
    Create the router with all endpoints.

    Returns:
        APIRouter: The configured router
    """
    router = APIRouter(tags=["Document_Analysis"])

    return router


document_analysis_router = create_router()  # Expose router for application
