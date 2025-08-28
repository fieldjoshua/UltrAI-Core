"""
Model Availability Routes

API endpoints for checking model availability and getting recommendations.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Request, Query
from pydantic import BaseModel
import time

from app.services.model_availability import ModelAvailabilityChecker, AvailabilityStatus
from app.utils.logging import get_logger

logger = get_logger("model_availability_routes")


class ModelAvailabilityRequest(BaseModel):
    """Request for checking model availability."""
    models: List[str]
    query: Optional[str] = None
    check_in_parallel: bool = True


class ModelAvailabilityInfo(BaseModel):
    """Model availability information."""
    model_name: str
    status: str
    response_time: Optional[float] = None
    error_message: Optional[str] = None
    recommended: bool = False
    performance_score: Optional[float] = None


class ModelAvailabilityResponse(BaseModel):
    """Response for model availability check."""
    success: bool
    models: Dict[str, ModelAvailabilityInfo]
    summary: Dict[str, Any]
    check_duration: float
    error: Optional[str] = None


def create_router():
    """Create the model availability router."""
    router = APIRouter()

    @router.post("/models/check-availability")
    async def check_model_availability(
        request: ModelAvailabilityRequest,
        http_request: Request
    ) -> ModelAvailabilityResponse:
        """
        Check availability of specified models.

        This endpoint performs real-time availability checks for the requested models
        and optionally provides recommendations based on the query.
        """
        start_time = time.time()

        try:
            # Get services from app state
            model_selector = None
            if hasattr(http_request.app.state, "services"):
                model_selector = http_request.app.state.services.get("model_selector")

            # Create availability checker
            checker = ModelAvailabilityChecker(model_selector=model_selector)

            # Check all models
            logger.info(f"Checking availability for {len(request.models)} models")
            results = await checker.check_all_models(
                models=request.models,
                query=request.query,
                parallel=request.check_in_parallel
            )

            # Convert to response format
            models_info = {}
            for model, availability in results.items():
                models_info[model] = ModelAvailabilityInfo(
                    model_name=model,
                    status=availability.status.value,
                    response_time=availability.response_time,
                    error_message=availability.error_message,
                    recommended=availability.recommended_for_query,
                    performance_score=availability.performance_score
                )

            # Get summary
            summary = checker.get_availability_summary(results)

            check_duration = time.time() - start_time
            logger.info(f"Availability check completed in {check_duration:.2f}s")

            return ModelAvailabilityResponse(
                success=True,
                models=models_info,
                summary=summary,
                check_duration=check_duration
            )

        except Exception as e:
            logger.error(f"Model availability check failed: {str(e)}")
            return ModelAvailabilityResponse(
                success=False,
                models={},
                summary={},
                check_duration=time.time() - start_time,
                error=str(e)
            )

    @router.get("/models/quick-check")
    async def quick_availability_check(
        http_request: Request,
        models: Any = Query(..., description="Models to check; accepts comma-separated string or list")
    ) -> Dict[str, Any]:
        """
        Quick availability check for models (uses cache when possible).

        This is a lighter-weight endpoint that prioritizes speed over accuracy.
        """
        try:
            # Normalize models input to a list of strings
            model_list: List[str] = []
            if isinstance(models, str):
                model_list = [m.strip() for m in models.split(",") if m and isinstance(m, str)]
            elif isinstance(models, list):
                model_list = [str(m).strip() for m in models if m is not None and str(m).strip()]
            elif isinstance(models, dict):
                # Accept dict with key 'models' or flatten values
                if "models" in models and isinstance(models["models"], list):
                    model_list = [str(m).strip() for m in models["models"] if m is not None and str(m).strip()]
                else:
                    # Fallback: take all values
                    model_list = [str(v).strip() for v in models.values() if v is not None and str(v).strip()]
            else:
                # Last resort
                model_list = [str(models).strip()] if models is not None else []

            if not model_list:
                return {
                    "success": False,
                    "error": "No models provided",
                }

            # Get services
            model_selector = None
            if hasattr(http_request.app.state, "services"):
                model_selector = http_request.app.state.services.get("model_selector")

            # Create checker and do quick check
            checker = ModelAvailabilityChecker(model_selector=model_selector)

            results = {}
            for model in model_list:
                # Try cache first
                cached = checker._get_cached_availability(model)
                if cached:
                    results[model] = {
                        "status": cached.status.value,
                        "cached": True
                    }
                else:
                    # Do actual check
                    availability = await checker.check_single_model(model)
                    results[model] = {
                        "status": availability.status.value,
                        "cached": False
                    }

            return {
                "success": True,
                "models": results,
                "timestamp": time.time()
            }

        except Exception as e:
            logger.error(f"Quick check failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    @router.get("/models/recommendations")
    async def get_model_recommendations(
        http_request: Request,
        query: str = Query(..., description="The query to get recommendations for"),
        limit: int = Query(5, description="Maximum number of recommendations")
    ) -> Dict[str, Any]:
        """
        Get model recommendations based on query type and availability.
        """
        try:
            # Default model list
            all_models = [
                "gpt-4",
                "gpt-4-turbo",
                "gpt-4o",
                "gpt-4o-mini",
                "o1-preview",
                "claude-3-5-sonnet-20241022",
                "claude-3-5-haiku-20241022",
                "claude-3-opus-20240229",
                "gemini-1.5-pro",
                "gemini-1.5-flash",
                "gemini-2.0-flash-exp"
            ]

            # Get services
            model_selector = None
            if hasattr(http_request.app.state, "services"):
                model_selector = http_request.app.state.services.get("model_selector")

            # Check availability with query context
            checker = ModelAvailabilityChecker(model_selector=model_selector)
            results = await checker.check_all_models(
                models=all_models,
                query=query,
                parallel=True
            )

            # Filter and sort recommendations
            recommendations = []
            for model, availability in results.items():
                if availability.status == AvailabilityStatus.AVAILABLE and availability.recommended_for_query:
                    recommendations.append({
                        "model": model,
                        "performance_score": availability.performance_score,
                        "response_time": availability.response_time,
                        "reason": "High performance for query type"
                    })

            # Sort by performance score
            recommendations.sort(key=lambda x: x.get("performance_score", 0), reverse=True)

            return {
                "success": True,
                "query": query,
                "recommendations": recommendations[:limit],
                "total_available": sum(1 for a in results.values() if a.status == AvailabilityStatus.AVAILABLE)
            }

        except Exception as e:
            logger.error(f"Recommendations failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    @router.get("/models/api-keys-status")
    async def get_api_keys_status(http_request: Request) -> Dict[str, Any]:
        """
        Check which API keys are configured (without exposing the actual keys).
        
        This helps diagnose why certain models aren't working.
        """
        import os
        
        api_keys_status = {
            "openai": {
                "configured": bool(os.getenv("OPENAI_API_KEY")),
                "env_var": "OPENAI_API_KEY",
                "provider": "OpenAI",
                "models": ["gpt-4o", "gpt-4", "gpt-3.5-turbo", "o1-preview", "o1-mini"]
            },
            "anthropic": {
                "configured": bool(os.getenv("ANTHROPIC_API_KEY")),
                "env_var": "ANTHROPIC_API_KEY", 
                "provider": "Anthropic",
                "models": ["claude-3-5-sonnet-20241022", "claude-3-5-haiku-20241022", "claude-3-opus-20240229"]
            },
            "google": {
                "configured": bool(os.getenv("GOOGLE_API_KEY")),
                "env_var": "GOOGLE_API_KEY",
                "provider": "Google",
                "models": ["gemini-1.5-pro", "gemini-1.5-flash", "gemini-2.0-flash-exp"]
            },
            "huggingface": {
                "configured": bool(os.getenv("HUGGINGFACE_API_KEY")),
                "env_var": "HUGGINGFACE_API_KEY",
                "provider": "HuggingFace",
                "models": ["meta-llama/Meta-Llama-3-8B-Instruct", "mistralai/Mistral-7B-Instruct-v0.1"]
            }
        }
        
        # Count configured providers
        configured_count = sum(1 for provider in api_keys_status.values() if provider["configured"])
        total_count = len(api_keys_status)
        
        # List missing providers
        missing_providers = [
            provider["provider"] 
            for provider in api_keys_status.values() 
            if not provider["configured"]
        ]
        
        return {
            "status": "ok",
            "providers": api_keys_status,
            "summary": {
                "total_providers": total_count,
                "configured_providers": configured_count,
                "missing_providers": missing_providers,
                "all_configured": configured_count == total_count
            },
            "message": (
                "All API keys configured" 
                if configured_count == total_count 
                else f"Missing API keys for: {', '.join(missing_providers)}"
            )
        }

    return router


router = create_router()  # Expose router for application
