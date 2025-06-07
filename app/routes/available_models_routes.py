"""
Route handlers for available models service.
"""

from typing import Dict, List, Any
from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

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
        """
        try:
            # Default model configurations (fallback if registry not available)
            default_models = [
                ModelInfo(
                    name="gpt-4",
                    provider="openai", 
                    status="available",
                    max_tokens=8192,
                    cost_per_1k_tokens=0.03
                ),
                ModelInfo(
                    name="gpt-4-turbo",
                    provider="openai",
                    status="available", 
                    max_tokens=128000,
                    cost_per_1k_tokens=0.01
                ),
                ModelInfo(
                    name="claude-3-sonnet",
                    provider="anthropic",
                    status="available",
                    max_tokens=200000,
                    cost_per_1k_tokens=0.003
                ),
                ModelInfo(
                    name="claude-3-haiku",
                    provider="anthropic",
                    status="available",
                    max_tokens=200000,
                    cost_per_1k_tokens=0.00025
                ),
                ModelInfo(
                    name="gemini-pro",
                    provider="google",
                    status="available",
                    max_tokens=32768,
                    cost_per_1k_tokens=0.0005
                ),
                # HuggingFace models - free tier
                ModelInfo(
                    name="meta-llama/Llama-2-7b-chat-hf",
                    provider="huggingface",
                    status="available",
                    max_tokens=4096,
                    cost_per_1k_tokens=0.0  # Free tier
                ),
                ModelInfo(
                    name="meta-llama/Meta-Llama-3-8B-Instruct",
                    provider="huggingface", 
                    status="available",
                    max_tokens=8192,
                    cost_per_1k_tokens=0.0  # Free tier
                ),
                ModelInfo(
                    name="mistralai/Mistral-7B-Instruct-v0.3",
                    provider="huggingface",
                    status="available", 
                    max_tokens=32768,
                    cost_per_1k_tokens=0.0  # Free tier
                ),
                ModelInfo(
                    name="Qwen/Qwen2.5-7B-Instruct",
                    provider="huggingface",
                    status="available",
                    max_tokens=32768,
                    cost_per_1k_tokens=0.0  # Free tier
                )
            ]
            
            models = default_models
            
            # Try to get from model registry if available
            if hasattr(http_request.app.state, 'model_registry'):
                try:
                    model_registry = http_request.app.state.model_registry
                    # If model_registry has methods, use them
                    if hasattr(model_registry, 'list_models'):
                        registry_models = await model_registry.list_models()
                        # Convert to our format if needed
                        models = registry_models if registry_models else default_models
                except Exception as e:
                    logger.warning(f"Could not fetch from model registry: {e}")
                    # Fall back to default models
            
            healthy_count = len([m for m in models if m.status == "available"])
            
            logger.info(f"Returning {len(models)} models, {healthy_count} healthy")
            
            return AvailableModelsResponse(
                models=models,
                total_count=len(models),
                healthy_count=healthy_count
            )
            
        except Exception as e:
            logger.error(f"Error fetching available models: {str(e)}")
            # Return minimal fallback response
            fallback_models = [
                ModelInfo(
                    name="gpt-4",
                    provider="openai",
                    status="unknown",
                    max_tokens=8192,
                    cost_per_1k_tokens=0.03
                )
            ]
            
            return AvailableModelsResponse(
                models=fallback_models,
                total_count=1,
                healthy_count=0
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

    return router


router = create_router()  # Expose router for application
