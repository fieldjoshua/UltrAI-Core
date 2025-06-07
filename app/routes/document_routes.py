"""
Route handlers for the Ultra backend.
"""

import logging
from typing import Dict
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse


def create_router(document_processor=None) -> APIRouter:
    """
    Create the router with all endpoints.

    Returns:
        APIRouter: The configured router
    """
    router = APIRouter(tags=["Document"])

    return router


document_router = create_router()  # Expose router for application
