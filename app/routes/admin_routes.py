from fastapi import APIRouter, Request
import os
from typing import Dict, Any

from app.utils.logging import get_logger
from app.services.provider_health_manager import provider_health_manager

logger = get_logger("admin_routes")

router = APIRouter(tags=["Admin"])


@router.get("/admin/overview")
async def admin_overview(http_request: Request) -> Dict[str, Any]:
    try:
        # Keys status
        api_keys_status = {
            "openai": bool(os.getenv("OPENAI_API_KEY")),
            "anthropic": bool(os.getenv("ANTHROPIC_API_KEY")),
            "google": bool(os.getenv("GOOGLE_API_KEY")),
            "huggingface": bool(os.getenv("HUGGINGFACE_API_KEY")),
        }

        # Orchestrator health
        orchestrator_available = hasattr(http_request.app.state, "orchestration_service")

        # Provider health summary
        try:
            health_summary = await provider_health_manager.get_health_summary()
        except Exception as e:
            logger.warning(f"admin: health summary unavailable: {e}")
            health_summary = {"_system": {"status": "unknown", "available_providers": [], "total_providers": 0}}

        return {
            "status": "ok",
            "keys": api_keys_status,
            "orchestrator": {
                "available": orchestrator_available
            },
            "providers": health_summary,
        }
    except Exception as e:
        logger.error(f"admin overview failed: {e}")
        return {"status": "error", "error": str(e)}


@router.get("/admin/providers/quick-check")
async def admin_providers_quick_check() -> Dict[str, Any]:
    try:
        summary = await provider_health_manager.get_health_summary()
        system = summary.get("_system", {})
        return {
            "status": "ok",
            "available": system.get("available_providers", []),
            "total": system.get("total_providers", 0),
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}
