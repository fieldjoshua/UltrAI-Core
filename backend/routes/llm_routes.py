"""
LLM Routes

This module provides API routes for LLM availability, configuration, and management.
"""

import logging
from typing import List, Optional

from fastapi import APIRouter, HTTPException
from backend.services.llm_config_service import llm_config_service

# Import the models we created
from backend.models.llm_models import (
    ModelsResponse,
    ModelResponse,
    ModelStatusResponse,
    PatternsResponse,
    AnalysisModesResponse,
)

# Create a router
llm_router = APIRouter(tags=["LLM Management"])

# Configure logging
logger = logging.getLogger("llm_routes")


@llm_router.get("/api/llms", response_model=ModelsResponse)
async def get_available_llms(
    tags: Optional[List[str]] = None,
    capability: Optional[str] = None,
):
    """
    Get all available LLM models with optional filtering

    Args:
        tags: Optional list of tags to filter models by
        capability: Optional capability to filter models by

    Returns:
        List of available LLM models
    """
    try:
        if tags:
            models = llm_config_service.get_models_by_tags(tags)
        elif capability:
            # For capabilities requiring specific values other than True,
            # that would need to be handled in a more complex way
            models = llm_config_service.get_models_by_capability(capability)
        else:
            models = llm_config_service.get_available_models()

        return {
            "status": "success",
            "count": len(models),
            "models": list(models.values()),
        }
    except Exception as e:
        logger.error(f"Error getting available LLMs: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error retrieving LLM information: {str(e)}"
        )


@llm_router.get("/api/llms/{model_name}", response_model=ModelResponse)
async def get_llm_details(model_name: str):
    """
    Get detailed information about a specific LLM model

    Args:
        model_name: Name of the model to retrieve

    Returns:
        Detailed model information
    """
    model = llm_config_service.get_model_details(model_name)

    if not model:
        raise HTTPException(status_code=404, detail=f"Model {model_name} not found")

    return {"status": "success", "model": model}


@llm_router.get("/api/llms/{model_name}/status", response_model=ModelStatusResponse)
async def get_llm_status(model_name: str):
    """
    Get the current status of a specific LLM model

    Args:
        model_name: Name of the model to check

    Returns:
        Model status information
    """
    status = llm_config_service.get_model_status(model_name)

    return {"status": "success", "model_status": status}


@llm_router.get("/api/patterns", response_model=PatternsResponse)
async def get_available_patterns():
    """
    Get all available analysis patterns

    Returns:
        List of available pattern names
    """
    patterns = llm_config_service.get_available_analysis_patterns()

    return {"status": "success", "count": len(patterns), "patterns": patterns}


@llm_router.get("/api/analysis-modes", response_model=AnalysisModesResponse)
async def get_available_analysis_modes():
    """
    Get all available analysis modes

    Returns:
        List of available analysis modes with details
    """
    modes = llm_config_service.get_available_analysis_modes()

    return {"status": "success", "count": len(modes), "modes": modes}
