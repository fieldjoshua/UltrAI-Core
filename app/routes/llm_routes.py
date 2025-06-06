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
LLM Routes

This module provides API routes for LLM availability, configuration, and management.
"""

import logging
from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException

# Create a router
llm_router = APIRouter(tags=["LLM Management"])

# Configure logging
logger = logging.getLogger("llm_routes")

# Constants
DEFAULT_MODELS: Dict[str, Dict[str, str | List[str]]] = {
    "gpt4o": {"name": "gpt4o", "tags": ["general"], "capability": "text"},
    "gpt4turbo": {"name": "gpt4turbo", "tags": ["general"], "capability": "text"},
    "claude37": {"name": "claude37", "tags": ["general"], "capability": "text"},
    "claude3opus": {"name": "claude3opus", "tags": ["general"], "capability": "text"},
    "gemini15": {"name": "gemini15", "tags": ["general"], "capability": "text"},
    "llama3": {"name": "llama3", "tags": ["general"], "capability": "text"},
}

DEFAULT_MODEL_NAMES: List[str] = list(DEFAULT_MODELS.keys())
DEFAULT_PATTERNS: List[str] = ["pattern1", "pattern2", "pattern3"]
DEFAULT_ANALYSIS_MODES: List[str] = ["mode1", "mode2", "mode3"]


class AvailableModelsResponse(BaseModel):
    """Response model for available models endpoint."""

    status: str
    available_models: List[str]


@llm_router.get(
    "/available-models",
    class AvailableModelsResponse(BaseModel):
    """Response model for availablemodelsresponse endpoint."""
    status: str
    data: Dict[str, Any]

response_model=AvailableModelsResponse,
    tags=["LLM Management"],
)
async def get_just_available_model_names() -> AvailableModelsResponse:
    """
    Get just the names of available LLM models.
    WARNING: This endpoint is for development/testing only. Do not use in production.
    """
    return AvailableModelsResponse(
        status="success",
        available_models=DEFAULT_MODEL_NAMES,
    )


@llm_router.get(
    "/models-list",
    response_model=AvailableModelsResponse,
    tags=["LLM Management"],
)
async def get_available_models_list() -> AvailableModelsResponse:
    """
    Get a list of available LLM models.
    WARNING: This endpoint is for development/testing only. Do not use in production.
    """
    return AvailableModelsResponse(
        status="success",
        available_models=DEFAULT_MODEL_NAMES,
    )


class ModelsResponse(BaseModel):
    """Response model for models endpoint."""

    status: str
    count: int
    models: List[Dict[str, str | List[str]]]


@llm_router.get("/llms", class ModelsResponse(BaseModel):
    """Response model for modelsresponse endpoint."""
    status: str
    data: Dict[str, Any]

response_model=ModelsResponse)
async def get_available_llms(
    tags: Optional[List[str]] = None,
    capability: Optional[str] = None,
) -> ModelsResponse:
    """
    Get available LLMs with optional filtering by tags or capability.
    WARNING: This endpoint is for development/testing only. Do not use in production.
    """
    models = DEFAULT_MODELS.copy()

    if tags:
        models = {
            k: v for k, v in models.items() if any(tag in v["tags"] for tag in tags)
        }
    elif capability:
        models = {k: v for k, v in models.items() if v["capability"] == capability}

    return ModelsResponse(
        status="success",
        count=len(models),
        models=list(models.values()),
    )


class ModelResponse(BaseModel):
    """Response model for single model endpoint."""

    status: str
    model: Dict[str, str | List[str]]


@llm_router.get("/llms/{model_name}", class ModelResponse(BaseModel):
    """Response model for modelresponse endpoint."""
    status: str
    data: Dict[str, Any]

response_model=ModelResponse)
async def get_llm_details(model_name: str) -> ModelResponse:
    """
    Get details for a specific LLM model.
    WARNING: This endpoint is for development/testing only. Do not use in production.
    """
    model = DEFAULT_MODELS.get(model_name)
    if not model:
        raise HTTPException(status_code=404, detail=f"Model {model_name} not found")

    return ModelResponse(
        status="success",
        model=model,
    )


class ModelStatusResponse(BaseModel):
    """Response model for model status endpoint."""

    status: str
    model_status: str


@llm_router.get("/llms/{model_name}/status", class ModelStatusResponse(BaseModel):
    """Response model for modelstatusresponse endpoint."""
    status: str
    data: Dict[str, Any]

response_model=ModelStatusResponse)
async def get_llm_status(model_name: str) -> ModelStatusResponse:
    """
    Get the status of a specific LLM model.
    WARNING: This endpoint is for development/testing only. Do not use in production.
    """
    if model_name not in DEFAULT_MODELS:
        raise HTTPException(status_code=404, detail=f"Model {model_name} not found")

    return ModelStatusResponse(
        status="success",
        model_status="available",
    )


class PatternsResponse(BaseModel):
    """Response model for patterns endpoint."""

    status: str
    count: int
    patterns: List[str]


@llm_router.get("/patterns", class PatternsResponse(BaseModel):
    """Response model for patternsresponse endpoint."""
    status: str
    data: Dict[str, Any]

response_model=PatternsResponse)
async def get_available_patterns() -> PatternsResponse:
    """
    Get available analysis patterns.
    WARNING: This endpoint is for development/testing only. Do not use in production.
    """
    return PatternsResponse(
        status="success",
        count=len(DEFAULT_PATTERNS),
        patterns=DEFAULT_PATTERNS,
    )


class AnalysisModesResponse(BaseModel):
    """Response model for analysis modes endpoint."""

    status: str
    count: int
    modes: List[str]


@llm_router.get("/analysis-modes", class AnalysisModesResponse(BaseModel):
    """Response model for analysismodesresponse endpoint."""
    status: str
    data: Dict[str, Any]

response_model=AnalysisModesResponse)
async def get_available_analysis_modes() -> AnalysisModesResponse:
    """
    Get available analysis modes.
    WARNING: This endpoint is for development/testing only. Do not use in production.
    """
    return AnalysisModesResponse(
        status="success",
        count=len(DEFAULT_ANALYSIS_MODES),
        modes=DEFAULT_ANALYSIS_MODES,
    )
