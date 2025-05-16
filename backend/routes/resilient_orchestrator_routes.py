"""
Resilient Orchestrator Routes with API Failure Handling.

This module enhances the orchestrator routes with comprehensive failure handling
using circuit breakers, retries, fallbacks, and caching.
"""

import logging
import os
import sys
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from backend.services.api_failure_handler import APIProvider, api_failure_handler
from backend.utils.auth_middleware import get_current_user
from backend.utils.errors import LLMError, NetworkError

# Add project root to Python path
sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

# Import our orchestrator
try:
    from src.simple_core.factory import create_from_env
except ImportError:
    raise ImportError("Failed to import simple_core orchestrator")

# Create a router
resilient_orchestrator_router = APIRouter(tags=["Resilient Orchestrator"])

# Configure logging
logger = logging.getLogger("resilient_orchestrator_routes")


# Request and response models
class ResilientOrchestrationRequest(BaseModel):
    """Request model for resilient orchestration"""

    prompt: str = Field(..., min_length=1, description="The prompt to process")
    models: Optional[List[str]] = Field(None, description="List of models to use")
    lead_model: Optional[str] = Field(None, description="Primary model for synthesis")
    analysis_type: Optional[str] = Field("comparative", description="Type of analysis")
    enable_fallback: bool = Field(True, description="Enable fallback providers")
    enable_cache: bool = Field(True, description="Enable response caching")
    max_retries: Optional[int] = Field(None, description="Override max retries")
    timeout: Optional[int] = Field(None, description="Override timeout in seconds")


class ProviderHealthResponse(BaseModel):
    """Response model for provider health status"""

    status: str
    providers: Dict[str, Any]
    overall_health: float


@resilient_orchestrator_router.post("/resilient/analyze")
async def analyze_with_resilience(
    request: ResilientOrchestrationRequest,
    current_user: Optional[Dict] = Depends(get_current_user),
):
    """Execute analysis with comprehensive failure handling."""
    try:
        # Override configuration if specified
        if request.max_retries is not None:
            api_failure_handler.retry_handler.config.max_attempts = request.max_retries
        if request.timeout is not None:
            api_failure_handler.timeout_handler.config.default_timeout = request.timeout

        # Initialize orchestrator
        orchestrator = create_from_env(modular=True)

        if not orchestrator:
            raise LLMError(
                message="Failed to initialize orchestrator",
                code="SYS_001",
                status_code=500,
            )

        # Map models to providers
        provider_mapping = {
            "openai-gpt4o": APIProvider.OPENAI,
            "anthropic-claude": APIProvider.ANTHROPIC,
            "google-gemini": APIProvider.GOOGLE,
            "mistral-large": APIProvider.MISTRAL,
            "groq-llama": APIProvider.GROQ,
            "docker-model": APIProvider.DOCKER_MODEL_RUNNER,
        }

        # Determine primary provider
        primary_provider = APIProvider.OPENAI  # Default
        if request.lead_model and request.lead_model in provider_mapping:
            primary_provider = provider_mapping[request.lead_model]

        # Create wrapped orchestration function
        async def orchestrate_request():
            return await orchestrator.orchestrate(
                prompt=request.prompt,
                models=request.models,
                lead_model=request.lead_model,
                analysis_type=request.analysis_type,
                options=request.options,
            )

        # Execute with failure handling
        result = await api_failure_handler.execute_api_call(
            primary_provider=primary_provider,
            api_function=orchestrate_request,
            operation="orchestrate",
            client_id=current_user.get("id") if current_user else None,
            enable_fallback=request.enable_fallback,
            enable_cache=request.enable_cache,
        )

        return {
            "status": "success",
            "result": result,
            "metadata": {
                "provider_used": primary_provider.value,
                "fallback_used": api_failure_handler.stats["fallback_used"] > 0,
                "cached_response": api_failure_handler.stats["cache_hits"] > 0,
            },
        }

    except LLMError as e:
        logger.error(f"LLM error in resilient orchestration: {str(e)}")
        raise HTTPException(
            status_code=e.status_code,
            detail={"error": e.code, "message": e.message, "context": e.context},
        )
    except Exception as e:
        logger.error(f"Unexpected error in resilient orchestration: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "INTERNAL_ERROR",
                "message": "An unexpected error occurred during orchestration",
            },
        )


@resilient_orchestrator_router.get(
    "/resilient/health", response_model=ProviderHealthResponse
)
async def get_provider_health():
    """Get health status of all LLM providers."""
    try:
        health_data = await api_failure_handler.get_provider_health()

        # Calculate overall health score
        total_success = 0
        total_calls = 0

        for provider_data in health_data.values():
            total_calls += provider_data["total_calls"]
            total_success += (
                provider_data["success_rate"] * provider_data["total_calls"]
            )

        overall_health = total_success / total_calls if total_calls > 0 else 0

        return {
            "status": "success",
            "providers": health_data,
            "overall_health": overall_health,
        }

    except Exception as e:
        logger.error(f"Error getting provider health: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "HEALTH_CHECK_ERROR",
                "message": "Failed to retrieve provider health status",
            },
        )


@resilient_orchestrator_router.post("/resilient/reset-provider/{provider}")
async def reset_provider(
    provider: str, current_user: Optional[Dict] = Depends(get_current_user)
):
    """Manually reset a provider's circuit breaker."""
    try:
        # Map string to provider enum
        provider_enum = APIProvider(provider)

        # Only allow admins to reset providers
        if not current_user or current_user.get("role") != "admin":
            raise HTTPException(
                status_code=403, detail="Only administrators can reset providers"
            )

        await api_failure_handler.reset_provider(provider_enum)

        return {"status": "success", "message": f"Provider {provider} has been reset"}

    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid provider: {provider}")
    except Exception as e:
        logger.error(f"Error resetting provider: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "RESET_ERROR",
                "message": f"Failed to reset provider {provider}",
            },
        )


@resilient_orchestrator_router.get("/resilient/statistics")
async def get_failure_statistics():
    """Get comprehensive failure handling statistics."""
    try:
        stats = api_failure_handler.get_statistics()

        # Format statistics for response
        return {
            "status": "success",
            "statistics": {
                "total_calls": stats["total_calls"],
                "successful_calls": stats["successful_calls"],
                "failed_calls": stats["failed_calls"],
                "success_rate": stats["success_rate"],
                "fallback_used": stats["fallback_used"],
                "circuit_breaker_rejections": stats["circuit_open_rejections"],
                "rate_limited_calls": stats["rate_limited_calls"],
                "cache_hits": stats["cache_hits"],
                "provider_breakdown": stats["provider_statistics"],
            },
        }

    except Exception as e:
        logger.error(f"Error getting statistics: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={"error": "STATS_ERROR", "message": "Failed to retrieve statistics"},
        )
