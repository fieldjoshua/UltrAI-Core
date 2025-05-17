"""
Available Models API Route

This module provides a dedicated endpoint for retrieving available LLM models.
"""

import logging
from typing import List

from fastapi import APIRouter, HTTPException

# Import BaseModel
from pydantic import BaseModel

# Import the services we need
from backend.services.llm_config_service import llm_config_service

# Create a router
router = APIRouter(tags=["Models"])

# Configure logging
logger = logging.getLogger("available_models_routes")


# Response model
class AvailableModelsResponse(BaseModel):
    status: str
    available_models: List[str]


@router.get(
    "/test",
    tags=["Models"],
    summary="Test endpoint",
    description="Simple test endpoint to verify router is working",
)
async def test_endpoint():
    """Test endpoint to verify router is working"""
    return {"status": "success", "message": "Test endpoint is working"}


@router.get(
    "/available-models",
    response_model=AvailableModelsResponse,
    tags=["Models"],
    summary="Get available LLM models",
    description="Returns a list of available LLM model names that can be used with the API.",
)
async def get_available_models():
    """
    Get the names of all available LLM models.

    This endpoint returns a simple list of model names that can be used
    with the analyze endpoint.

    Returns:
        JSON object with status and list of model names
    """
    try:
        # Get models from llm_config_service
        models_dict = llm_config_service.get_available_models()

        # Check if we have models
        if models_dict and len(models_dict) > 0:
            model_names = list(models_dict.keys())
        else:
            # Fallback model names if we couldn't get any real models
            logger.warning("No models found, returning fallback model list")
            model_names = [
                "gpt4o",
                "gpt4turbo",
                "claude37",
                "claude3opus",
                "gemini15",
                "llama3",
            ]

        # Return response with model names
        return {
            "status": "success",
            "available_models": model_names,
        }
    except Exception as e:
        logger.error(f"Error getting available LLM names: {str(e)}")
        # Instead of throwing an error, return a fallback list
        return {
            "status": "partial",
            "available_models": [
                "gpt4o",
                "gpt4turbo",
                "claude37",
                "claude3opus",
                "gemini15",
                "llama3",
            ],
        }
