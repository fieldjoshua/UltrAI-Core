"""
Minimal Orchestrator Routes - Drop-in replacement for /api/orchestrator/feather

Provides compatibility with existing frontend while implementing Ultra Synthesis
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging

from backend.services.minimal_orchestrator import MinimalOrchestrator

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/orchestrator", tags=["orchestrator"])

# Initialize orchestrator (singleton)
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
async def orchestrate_feather(request: FeatherRequest):
    """
    Drop-in replacement for the feather orchestration endpoint.
    
    Implements Ultra Synthesis™ regardless of pattern parameter.
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
        
        # Call orchestrator (always uses Ultra Synthesis)
        result = await orchestrator.orchestrate(
            prompt=request.prompt,
            models=request.models,
            ultra_model=ultra_model
        )
        
        # Return in expected format
        return FeatherResponse(
            status=result["status"],
            model_responses=result["model_responses"],
            ultra_response=result["ultra_response"],
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
async def orchestrator_health():
    """Health check endpoint"""
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
async def list_available_models():
    """List all available models"""
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