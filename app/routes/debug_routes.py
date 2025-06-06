"""




Route handlers for the Ultra backend.




"""

import logging
from typing import Any, Dict, Optional
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse


def create_router() -> APIRouter:
    """
    Create the router with all endpoints.

    Returns:
        APIRouter: The configured router
    """
    router = APIRouter(tags=["debug"])

    return router
