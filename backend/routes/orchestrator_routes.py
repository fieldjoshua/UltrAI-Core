"""
Orchestrator Routes

This module provides API routes for the modular LLM orchestration system.
It interfaces with the Simple Core orchestrator to provide:
- Model selection
- Analysis processing 
- Response synthesis
"""

import logging
import os
import sys
from typing import Dict, List, Optional, Any

from fastapi import APIRouter, HTTPException, Body, Query
from pydantic import BaseModel, Field

# Add project root to Python path to ensure we can import our orchestrator
# even when FastAPI is run from elsewhere
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import our orchestrator
try:
    from src.simple_core.factory import create_from_env
except ImportError:
    raise ImportError(
        "Failed to import the simple_core orchestrator. "
        "Please ensure the src/simple_core directory exists and contains the necessary modules."
    )

# Create a router
orchestrator_router = APIRouter(tags=["Orchestrator"])

# Configure logging
logger = logging.getLogger("orchestrator_routes")


# Request and response models
class OrchestrationRequest(BaseModel):
    """Request model for orchestration"""
    prompt: str = Field(..., min_length=1, description="The prompt to process")
    models: Optional[List[str]] = Field(
        None, description="List of models to use (default: all available models)"
    )
    lead_model: Optional[str] = Field(
        None, description="The primary model to use for synthesizing results"
    )
    analysis_type: Optional[str] = Field(
        "comparative", description="Type of analysis to perform (comparative or factual)"
    )
    options: Optional[Dict[str, Any]] = Field(
        None, description="Additional options for the orchestrator"
    )


class ModelListResponse(BaseModel):
    """Response model for available models"""
    status: str
    models: List[str]


@orchestrator_router.get("/orchestrator/models", response_model=ModelListResponse)
async def get_available_orchestrator_models():
    """
    Get all models available through the orchestrator
    
    Returns:
        List of available model names
    """
    try:
        # Initialize orchestrator
        orchestrator = create_from_env(modular=True)
        
        if not orchestrator:
            # Fallback to mock models if orchestrator couldn't be created
            logger.warning("Orchestrator initialization failed, returning mock models")
            return {
                "status": "success",
                "models": [
                    "openai-gpt4o", 
                    "anthropic-claude", 
                    "google-gemini", 
                    "deepseek-chat"
                ]
            }
        
        # Get available models
        available_models = orchestrator.get_available_models()
        
        return {
            "status": "success",
            "models": available_models
        }
    except Exception as e:
        logger.error(f"Error getting available models: {str(e)}")
        # Return mock list instead of error for better frontend experience
        return {
            "status": "error",
            "models": [
                "openai-gpt4o", 
                "anthropic-claude", 
                "google-gemini", 
                "deepseek-chat"
            ]
        }


@orchestrator_router.post("/orchestrator/process")
async def process_with_orchestrator(request: OrchestrationRequest):
    """
    Process a prompt using the orchestrator
    
    Args:
        request: Orchestration request containing prompt and options
        
    Returns:
        Processed results from the orchestrator
    """
    try:
        logger.info(f"Processing orchestration request with prompt: {request.prompt[:50]}...")
        
        # Initialize orchestrator - use modular orchestrator for most flexibility
        orchestrator = create_from_env(
            modular=True, 
            analysis_type=request.analysis_type
        )
        
        if not orchestrator:
            logger.error("Failed to create orchestrator")
            raise HTTPException(
                status_code=500, 
                detail="Failed to initialize orchestrator. Please check your API keys and configuration."
            )
            
        # Convert request to format expected by orchestrator
        orchestrator_request = {
            "prompt": request.prompt,
            "model_names": request.models or [],
            "lead_model": request.lead_model,
            "analysis_type": request.analysis_type or "comparative",
            "options": request.options or {}
        }
            
        # Process the request
        result = await orchestrator.process(orchestrator_request)
        
        # Return the result directly
        return result
    except Exception as e:
        logger.error(f"Error processing orchestration request: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error processing request: {str(e)}"
        )