"""
Debug routes for troubleshooting deployment issues
"""

from fastapi import APIRouter
from typing import Dict, Any
import os
import sys

router = APIRouter(prefix="/debug", tags=["debug"])

@router.get("/ping")
async def ping() -> Dict[str, str]:
    """Simple ping endpoint that should always work"""
    return {"message": "pong", "status": "ok"}

@router.get("/env")
async def get_env() -> Dict[str, Any]:
    """Get environment information"""
    return {
        "python_version": sys.version,
        "environment": os.environ.get("ENVIRONMENT", "not set"),
        "port": os.environ.get("PORT", "not set"),
        "use_mock": os.environ.get("USE_MOCK", "not set"),
        "testing": os.environ.get("TESTING", "not set"),
        "api_keys_configured": {
            "openai": bool(os.environ.get("OPENAI_API_KEY")),
            "anthropic": bool(os.environ.get("ANTHROPIC_API_KEY")),
            "google": bool(os.environ.get("GOOGLE_API_KEY"))
        }
    }

@router.get("/routes")
async def get_routes() -> Dict[str, Any]:
    """List all registered routes"""
    from fastapi import FastAPI
    from app.app import app
    
    routes = []
    for route in app.routes:
        if hasattr(route, "path") and hasattr(route, "methods"):
            routes.append({
                "path": route.path,
                "methods": list(route.methods) if route.methods else [],
                "name": route.name if hasattr(route, "name") else "unknown"
            })
    
    return {
        "route_count": len(routes),
        "routes": sorted(routes, key=lambda x: x["path"])
    }