from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, Request, Response
"""
Route handlers for the Ultra backend.

This module provides API routes for various endpoints.
"""

from fastapi import APIRouter
from typing import Dict, Any, List
import os
import sys

router = APIRouter(prefix="/debug", tags=["debug"])


@router.get("/ping")
async def ping() -> Dict[str, str]:
    """Simple ping endpoint that should always work."""
    return {"message": "pong", "status": "ok"}


@router.get("/env")
async def get_env() -> Dict[str, Any]:
    """Get environment information."""
    return {
        "python_version": sys.version,
        "environment": os.environ.get("ENVIRONMENT", "not set"),
        "port": os.environ.get("PORT", "not set"),
        "use_mock": os.environ.get("USE_MOCK", "not set"),
        "testing": os.environ.get("TESTING", "not set"),
        "api_keys_configured": {
            "openai": bool(os.environ.get("OPENAI_API_KEY")),
            "anthropic": bool(os.environ.get("ANTHROPIC_API_KEY")),
            "google": bool(os.environ.get("GOOGLE_API_KEY")),
        },
    }


@router.get("/routes")
async def get_routes() -> Dict[str, Any]:
    """
    List all registered routes.
    WARNING: This endpoint exposes all registered routes and should not be enabled in production environments.
    """
    from app.app import create_app

    app = create_app()
    routes: List[Dict[str, Any]] = []
    for route in app.routes:
        path = getattr(route, "path", None)
        methods = getattr(route, "methods", None)
        if path and methods:
            routes.append(
                {
                    "path": path,
                    "methods": list(methods) if methods else [],
                    "name": getattr(route, "name", "unknown"),
                }
            )
    return {
        "route_count": len(routes),
        "routes": sorted(routes, key=lambda x: x["path"]),
    }
