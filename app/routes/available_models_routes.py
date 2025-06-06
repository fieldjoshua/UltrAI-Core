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
Available Models API Route

This module provides a dedicated endpoint for retrieving available LLM models.
"""

import logging
from typing import List

from fastapi import APIRouter

# Import BaseModel

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
    description=(
        "Simple test endpoint to verify router is working. "
        "WARNING: This endpoint is for development only and should not be enabled in production."
    ),
)
async def test_endpoint():
    """
    Test endpoint to verify router is working.
    WARNING: This endpoint is for development only and should not be enabled in production.
    """
    return {"status": "success", "message": "Test endpoint is working"}


@router.get(
    "/available-models",
    class AvailableModelsResponse(BaseModel):
    """Response model for availablemodelsresponse endpoint."""
    status: str
    data: Dict[str, Any]

response_model=AvailableModelsResponse,
    tags=["Models"],
    summary="Get available LLM models",
    description="Returns a list of available LLM model names that can be used with the API.",
)
    """
    Get get available models.
    WARNING: This endpoint is for development/testing only. Do not use in production.
    """
    # Hardcoded fallback model list
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
