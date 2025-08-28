"""
Route handlers for available models service.
"""

from typing import Dict, List, Any
from fastapi import APIRouter, Request
from pydantic import BaseModel, Field
import os

from app.utils.logging import get_logger

logger = get_logger("available_models_routes")


class ModelInfo(BaseModel):
    """Information about an available model."""
    name: str = Field(..., description="Model name")
    provider: str = Field(..., description="Model provider (openai, anthropic, google)")
    status: str = Field(..., description="Model status (available, unavailable, degraded)")
    max_tokens: int = Field(..., description="Maximum token limit")
    cost_per_1k_tokens: float = Field(default=0.0, description="Cost per 1000 tokens")


class AvailableModelsResponse(BaseModel):
    """Response model for available models endpoint."""
    models: List[ModelInfo] = Field(..., description="List of available models")
    total_count: int = Field(..., description="Total number of models")
    healthy_count: int = Field(..., description="Number of healthy models")


def create_router() -> APIRouter:
    """
    Create the router with all endpoints.

    Returns:
        APIRouter: The configured router
    """
    router = APIRouter(tags=["Available_Models"])

    @router.get("/available-models", response_model=AvailableModelsResponse)
    async def get_available_models(http_request: Request):
        """
        Get list of available LLM models and their status.
        
        Returns information about all configured models including
        their availability, token limits, and basic cost information.
        Only shows models that have API keys configured.
        """
        # Check which API keys are configured
        openai_configured = bool(os.getenv("OPENAI_API_KEY"))
        anthropic_configured = bool(os.getenv("ANTHROPIC_API_KEY"))
        google_configured = bool(os.getenv("GOOGLE_API_KEY"))
        huggingface_configured = bool(os.getenv("HUGGINGFACE_API_KEY"))
        
        available_models = []
        
        # OpenAI Models (only add if API key is configured)
        if openai_configured:
            openai_models = [
                # GPT-4 Models
                ModelInfo(
                    name="gpt-4o",
                    provider="openai", 
                    status="available",
                    max_tokens=128000,
                    cost_per_1k_tokens=0.005
                ),
                ModelInfo(
                    name="gpt-4o-mini",
                    provider="openai",
                    status="available", 
                    max_tokens=128000,
                    cost_per_1k_tokens=0.00015
                ),
                ModelInfo(
                    name="gpt-4-turbo-preview",
                    provider="openai",
                    status="available",
                    max_tokens=128000,
                    cost_per_1k_tokens=0.01
                ),
                ModelInfo(
                    name="gpt-4",
                    provider="openai",
                    status="available",
                    max_tokens=8192,
                    cost_per_1k_tokens=0.03
                ),
                # O1 Reasoning Models
                ModelInfo(
                    name="o1-preview",
                    provider="openai",
                    status="available", 
                    max_tokens=128000,
                    cost_per_1k_tokens=0.015
                ),
                ModelInfo(
                    name="o1-mini",
                    provider="openai",
                    status="available", 
                    max_tokens=65536,
                    cost_per_1k_tokens=0.003
                ),
                # GPT-3.5 Models
                ModelInfo(
                    name="gpt-3.5-turbo",
                    provider="openai",
                    status="available",
                    max_tokens=16385,
                    cost_per_1k_tokens=0.0005
                ),
                ModelInfo(
                    name="gpt-3.5-turbo-16k",
                    provider="openai",
                    status="available",
                    max_tokens=16385,
                    cost_per_1k_tokens=0.003
                ),
            ]
            available_models.extend(openai_models)
            
        # Anthropic Models (only add if API key is configured)
        if anthropic_configured:
            anthropic_models = [
                # Claude 3.5 Models
                ModelInfo(
                    name="claude-3-5-sonnet-20241022",
                    provider="anthropic",
                    status="available",
                    max_tokens=200000,
                    cost_per_1k_tokens=0.003
                ),
                ModelInfo(
                    name="claude-3-5-haiku-20241022",
                    provider="anthropic",
                    status="available",
                    max_tokens=200000,
                    cost_per_1k_tokens=0.0008
                ),
                # Claude 3 Models
                ModelInfo(
                    name="claude-3-opus-20240229",
                    provider="anthropic",
                    status="available",
                    max_tokens=200000,
                    cost_per_1k_tokens=0.015
                ),
                ModelInfo(
                    name="claude-3-sonnet-20240229",
                    provider="anthropic",
                    status="available",
                    max_tokens=200000,
                    cost_per_1k_tokens=0.003
                ),
                ModelInfo(
                    name="claude-3-haiku-20240307",
                    provider="anthropic",
                    status="available",
                    max_tokens=200000,
                    cost_per_1k_tokens=0.00025
                ),
                # Legacy aliases for compatibility
                ModelInfo(
                    name="claude-3-sonnet",
                    provider="anthropic",
                    status="available",
                    max_tokens=200000,
                    cost_per_1k_tokens=0.003
                ),
            ]
            available_models.extend(anthropic_models)
            
        # Google Models (only add if API key is configured)
        if google_configured:
            google_models = [
                # Gemini 1.5 Models
                ModelInfo(
                    name="gemini-1.5-pro",
                    provider="google",
                    status="available",
                    max_tokens=1000000,
                    cost_per_1k_tokens=0.0035
                ),
                ModelInfo(
                    name="gemini-1.5-pro-latest",
                    provider="google",
                    status="available",
                    max_tokens=2000000,
                    cost_per_1k_tokens=0.0035
                ),
                ModelInfo(
                    name="gemini-1.5-flash",
                    provider="google",
                    status="available",
                    max_tokens=1000000,
                    cost_per_1k_tokens=0.00035
                ),
                ModelInfo(
                    name="gemini-1.5-flash-latest",
                    provider="google",
                    status="available",
                    max_tokens=1000000,
                    cost_per_1k_tokens=0.00035
                ),
                # Gemini 2.0 Models (Experimental)
                ModelInfo(
                    name="gemini-2.0-flash-exp",
                    provider="google",
                    status="available",
                    max_tokens=1000000,
                    cost_per_1k_tokens=0.0
                ),
                # Legacy names
                ModelInfo(
                    name="gemini-pro",
                    provider="google",
                    status="available",
                    max_tokens=1000000,
                    cost_per_1k_tokens=0.0035
                ),
            ]
            available_models.extend(google_models)
            
        # HuggingFace Models (only add if API key is configured)
        if huggingface_configured:
            huggingface_models = [
                ModelInfo(
                    name="meta-llama/Meta-Llama-3-8B-Instruct",
                    provider="huggingface",
                    status="available",
                    max_tokens=8192,
                    cost_per_1k_tokens=0.0
                ),
                ModelInfo(
                    name="meta-llama/Meta-Llama-3-70B-Instruct",
                    provider="huggingface",
                    status="available",
                    max_tokens=8192,
                    cost_per_1k_tokens=0.0
                ),
                ModelInfo(
                    name="mistralai/Mistral-7B-Instruct-v0.1",
                    provider="huggingface",
                    status="available",
                    max_tokens=32768,
                    cost_per_1k_tokens=0.0
                ),
                ModelInfo(
                    name="mistralai/Mixtral-8x7B-Instruct-v0.1",
                    provider="huggingface",
                    status="available",
                    max_tokens=32768,
                    cost_per_1k_tokens=0.0
                ),
                ModelInfo(
                    name="google/gemma-7b-it",
                    provider="huggingface",
                    status="available",
                    max_tokens=8192,
                    cost_per_1k_tokens=0.0
                ),
                ModelInfo(
                    name="microsoft/phi-2",
                    provider="huggingface",
                    status="available",
                    max_tokens=2048,
                    cost_per_1k_tokens=0.0
                ),
            ]
            available_models.extend(huggingface_models)
        
        try:
            # Check if we have the model registry for dynamic model info
            if hasattr(http_request.app.state, 'model_registry'):
                model_registry = http_request.app.state.model_registry
                registered_models = model_registry.list_models()
                
                # Update status based on registry info
                for model_info in available_models:
                    for reg_model in registered_models:
                        if reg_model['name'] == model_info.name:
                            # Update with actual runtime status
                            if reg_model.get('error_count', 0) > 10:
                                model_info.status = "degraded"
                            break
            
            # Count healthy models
            healthy_count = sum(1 for m in available_models if m.status == "available")
            
            # Log summary
            logger.info(f"Returning {len(available_models)} available models ({healthy_count} healthy)")
            if not available_models:
                logger.warning("No models available - check API key configuration")
            
            return AvailableModelsResponse(
                models=available_models,
                total_count=len(available_models),
                healthy_count=healthy_count
            )
            
        except Exception as e:
            logger.error(f"Error fetching available models: {str(e)}")
            # Return whatever we have even if registry check fails
            healthy_count = sum(1 for m in available_models if m.status == "available")
            
            return AvailableModelsResponse(
                models=available_models,
                total_count=len(available_models),
                healthy_count=healthy_count
            )

    @router.get("/models/health")
    async def models_health(http_request: Request):
        """Check model service health."""
        try:
            if hasattr(http_request.app.state, 'model_registry'):
                return {"status": "healthy", "service": "model_registry"}
            else:
                return {"status": "degraded", "service": "model_registry", "error": "Service not initialized"}
        except Exception as e:
            return {"status": "error", "service": "model_registry", "error": str(e)}

    @router.get("/models/providers-summary") 
    async def get_providers_summary(http_request: Request):
        """Get summary of configured providers and their model counts."""
        providers = {
            "openai": {
                "configured": bool(os.getenv("OPENAI_API_KEY")),
                "model_count": 8,
                "models": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo-preview", "gpt-4", "o1-preview", "o1-mini", "gpt-3.5-turbo", "gpt-3.5-turbo-16k"]
            },
            "anthropic": {
                "configured": bool(os.getenv("ANTHROPIC_API_KEY")),
                "model_count": 6,
                "models": ["claude-3-5-sonnet-20241022", "claude-3-5-haiku-20241022", "claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307", "claude-3-sonnet"]
            },
            "google": {
                "configured": bool(os.getenv("GOOGLE_API_KEY")),
                "model_count": 6,
                "models": ["gemini-1.5-pro", "gemini-1.5-pro-latest", "gemini-1.5-flash", "gemini-1.5-flash-latest", "gemini-2.0-flash-exp", "gemini-pro"]
            },
            "huggingface": {
                "configured": bool(os.getenv("HUGGINGFACE_API_KEY")),
                "model_count": 6,
                "models": ["meta-llama/Meta-Llama-3-8B-Instruct", "meta-llama/Meta-Llama-3-70B-Instruct", "mistralai/Mistral-7B-Instruct-v0.1", "mistralai/Mixtral-8x7B-Instruct-v0.1", "google/gemma-7b-it", "microsoft/phi-2"]
            }
        }
        
        configured_providers = [name for name, info in providers.items() if info["configured"]]
        total_available_models = sum(info["model_count"] for name, info in providers.items() if info["configured"])
        
        return {
            "providers": providers,
            "configured_providers": configured_providers,
            "total_configured_providers": len(configured_providers),
            "total_available_models": total_available_models
        }

    return router


router = create_router()  # Expose router for application