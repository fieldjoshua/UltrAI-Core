from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, Request, Response
"""
Route handlers for the Ultra backend.

This module provides API routes for various endpoints.
"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, Request, Response
"""
Minimal Orchestrator Routes - Drop-in replacement for /api/orchestrator/feather

Provides compatibility with existing frontend while implementing Ultra Synthesis
"""
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
import logging
import os

# Choose which orchestrator to use based on environment
USE_BASIC = os.getenv("USE_BASIC_ORCHESTRATOR", "false").lower() == "true"

if USE_BASIC:
    from app.services.basic_orchestrator import BasicOrchestrator
    logger = logging.getLogger(__name__)
    logger.info("Using BasicOrchestrator (reliability focus)")
else:
    from app.services.minimal_orchestrator import MinimalOrchestrator
    logger = logging.getLogger(__name__)
    logger.info("Using MinimalOrchestrator (Ultra Synthesis)")

# Create router
router = APIRouter(prefix="/api/orchestrator", tags=["orchestrator"])

# Initialize orchestrator (singleton)
if USE_BASIC:
    orchestrator = BasicOrchestrator()
else:
    orchestrator = MinimalOrchestrator()


class FeatherRequest(BaseModel):
    """Request model matching frontend expectations"""
    prompt: str
    models: List[str]
    args: Dict[str, Any] = {}
    kwargs: Dict[str, Any] = {}


class FeatherResponse(BaseModel):
    """Response model matching frontend expectations"""
    status: str
    model_responses: Dict[str, str]
    ultra_response: str
    performance: Dict[str, Any]
    cached: bool = False
    message: Optional[str] = None
    error: Optional[str] = None


@router.post("/feather", response_model=FeatherResponse)
async def orchestrate_feather(request: FeatherRequest) -> FeatherResponse:
    """
    Create orchestrate feather.
    WARNING: This endpoint is for development/testing only. Do not use in production.
    """
    try:
        # Validate request
        if not request.prompt:
            raise HTTPException(status_code=400, detail="Prompt cannot be empty")

        if not request.models:
            request.models = ["gpt4o", "claude37"]  # Default models

        # Extract ultra_model from args if provided
        ultra_model = request.args.get("ultra_model", request.models[0])

        # Log request for debugging
        logger.info(f"Orchestration request: {len(request.models)} models, pattern: {request.args.get('pattern', 'none')}")

        # Call orchestrator based on which one we're using
        if USE_BASIC:
            # Basic orchestrator just does parallel calls
            result = await orchestrator.orchestrate_basic(
                prompt=request.prompt,
                models=request.models,
                combine=True
            )
        else:
            # Minimal orchestrator uses Ultra Synthesis
            result = await orchestrator.orchestrate(
                prompt=request.prompt,
                models=request.models,
                ultra_model=ultra_model
            )

        # Return in expected format
        return FeatherResponse(
            status=result["status"],
            model_responses=result["model_responses"],
            ultra_response=result.get("ultra_response", result.get("combined_response", "")),
            performance=result["performance"],
            cached=result.get("cached", False)
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Orchestration error: {str(e)}", exc_info=True)

        # Return error response in expected format
        return FeatherResponse(
            status="error",
            model_responses={},
            ultra_response=f"An error occurred during orchestration: {str(e)}",
            performance={"total_time_seconds": 0, "model_times": {}},
            cached=False,
            error=str(e)
        )


@router.get("/health")
    """
    Get orchestrator health.
    WARNING: This endpoint is for development/testing only. Do not use in production.
    """
    try:
        # Check if we have any adapters initialized
        adapter_count = sum(len(models) for models in orchestrator.adapters.values())

        return {
            "status": "healthy" if adapter_count > 0 else "degraded",
            "adapters_initialized": adapter_count,
            "available_providers": list(orchestrator.adapters.keys())
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


@router.get("/models")
    """
    Get list available models.
    WARNING: This endpoint is for development/testing only. Do not use in production.
    """
    available = []

    for provider, models in orchestrator.adapters.items():
        for model_name in models.keys():
            # Find frontend name for this backend model
            frontend_name = None
            for fn, bn in orchestrator.model_mappings.items():
                if bn == model_name:
                    frontend_name = fn
                    break

            available.append({
                "id": frontend_name or model_name,
                "name": frontend_name or model_name,
                "provider": provider,
                "available": True
            })

    return {
        "models": available,
        "count": len(available)
    }