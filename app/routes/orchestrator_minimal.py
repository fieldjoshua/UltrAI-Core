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
    router = APIRouter(tags=["Orchestrator_Minimal"])

    return router


router = create_router()  # Expose router for application
