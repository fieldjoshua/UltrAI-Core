"""
Orchestrator Routes

This module provides API routes for the sophisticated UltraAI patent-protected 
Feather orchestration system. It interfaces with the PatternOrchestrator to provide:
- 4-stage Feather analysis (Initial → Meta → Hyper → Ultra)
- Multi-LLM model selection and orchestration
- Pattern-driven analysis (gut, confidence, critique, etc.)
- Quality evaluation and scoring
"""

import logging
import os
import sys
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Body, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

# Import our sophisticated orchestrator through the integration module
ORCHESTRATOR_AVAILABLE = False
PatternOrchestrator = None
get_pattern_mapping = None

try:
    # Import from the integration module which handles path setup
    from backend.integrations.pattern_orchestrator_integration import (
        PatternOrchestrator, 
        get_pattern_mapping, 
        ORCHESTRATOR_AVAILABLE
    )
    if ORCHESTRATOR_AVAILABLE:
        print("✅ Successfully imported sophisticated PatternOrchestrator via integration")
    else:
        print("⚠️ Using fallback PatternOrchestrator from integration")
except Exception as e:
    print(f"❌ Failed to import from integration module: {e}")
    # Use a fallback implementation
    ORCHESTRATOR_AVAILABLE = False
    
    class FallbackPatternOrchestrator:
        def __init__(self, api_keys, pattern="gut", output_format="plain"):
            print("⚠️ Using fallback stub PatternOrchestrator - sophisticated features not available")
            self.available_models = ["claude-3-opus", "gpt-4-turbo", "gemini-pro"]
        
        async def orchestrate_full_process(self, prompt):
            return {
                "initial_responses": {"claude-3-opus": "Mock initial response"},
                "meta_responses": {"claude-3-opus": "Mock meta response"},
                "hyper_responses": {"claude-3-opus": "Mock hyper response"},
                "ultra_response": "Mock ultra response - sophisticated orchestrator not available",
                "processing_time": 0.0
            }
    
    PatternOrchestrator = FallbackPatternOrchestrator
    
    def get_pattern_mapping():
        return {
            "gut": {"name": "gut", "description": "Gut-based intuitive analysis"},
            "confidence": {"name": "confidence", "description": "Confidence scoring analysis"},
            "critique": {"name": "critique", "description": "Critical analysis pattern"},
            "fact_check": {"name": "fact_check", "description": "Fact-checking analysis"},
            "perspective": {"name": "perspective", "description": "Multi-perspective analysis"},
            "scenario": {"name": "scenario", "description": "Scenario-based analysis"}
        }

# Create a router
orchestrator_router = APIRouter(tags=["Orchestrator"])

# Add a simple test route to verify router inclusion
@orchestrator_router.get("/orchestrator/test")
async def test_orchestrator_router():
    """Simple test endpoint to verify orchestrator router is properly included"""
    return {
        "status": "success",
        "message": "Orchestrator router is working",
        "routes_available": ["models", "patterns", "feather", "process"]
    }

# Configure logging
logger = logging.getLogger("orchestrator_routes")


# Request and response models for sophisticated orchestration
class FeatherOrchestrationRequest(BaseModel):
    """Request model for 4-stage Feather orchestration"""

    prompt: str = Field(..., min_length=1, description="The prompt to process")
    models: Optional[List[str]] = Field(
        None, description="List of models to use (default: all available models)"
    )
    pattern: Optional[str] = Field(
        "gut", description="Analysis pattern to use (gut, confidence, critique, fact_check, perspective, scenario)"
    )
    ultra_model: Optional[str] = Field(
        None, description="The model to use for ultra synthesis (default: best available)"
    )
    output_format: Optional[str] = Field(
        "plain", description="Output format (plain, markdown, json)"
    )


class OrchestrationRequest(BaseModel):
    """Legacy request model for backward compatibility"""

    prompt: str = Field(..., min_length=1, description="The prompt to process")
    models: Optional[List[str]] = Field(
        None, description="List of models to use (default: all available models)"
    )
    lead_model: Optional[str] = Field(
        None, description="The primary model to use for synthesizing results"
    )
    analysis_type: Optional[str] = Field(
        "comparative",
        description="Type of analysis to perform (comparative or factual)",
    )
    options: Optional[Dict[str, Any]] = Field(
        None, description="Additional options for the orchestrator"
    )


class ModelListResponse(BaseModel):
    """Response model for available models"""

    status: str
    models: List[str]


class PatternListResponse(BaseModel):
    """Response model for available analysis patterns"""

    status: str
    patterns: List[Dict[str, str]]


class FeatherOrchestrationResponse(BaseModel):
    """Response model for 4-stage Feather orchestration"""

    status: str
    initial_responses: Dict[str, str]
    meta_responses: Dict[str, str]
    hyper_responses: Dict[str, str]
    ultra_response: str
    processing_time: float
    pattern_used: str
    models_used: List[str]


@orchestrator_router.get("/orchestrator/models")
async def get_available_orchestrator_models():
    """
    Get all models available through the sophisticated PatternOrchestrator

    Returns:
        List of available model names from the sophisticated orchestrator
    """
    print("🔍 DEBUG: get_available_orchestrator_models called")
    try:
        if not ORCHESTRATOR_AVAILABLE:
            # Fallback to mock models if sophisticated orchestrator couldn't be imported
            logger.warning("Sophisticated orchestrator not available, returning mock models")
            return {
                "status": "success",
                "models": [
                    "claude-3-opus",
                    "gpt-4-turbo",
                    "gemini-pro",
                    "mistral-large",
                    "perplexity-llama",
                    "cohere-command",
                ],
            }

        # Get API keys from environment
        api_keys = {
            "anthropic": os.getenv("ANTHROPIC_API_KEY"),
            "openai": os.getenv("OPENAI_API_KEY"),
            "google": os.getenv("GOOGLE_API_KEY"),
            "mistral": os.getenv("MISTRAL_API_KEY"),
            "perplexity": os.getenv("PERPLEXITY_API_KEY"),
            "cohere": os.getenv("COHERE_API_KEY"),
            "deepseek": os.getenv("DEEPSEEK_API_KEY"),
        }
        # Remove empty keys
        api_keys = {k: v for k, v in api_keys.items() if v}

        if not api_keys:
            logger.warning("No API keys found, returning default model list")
            return {
                "status": "success",
                "models": ["claude-3-opus", "gpt-4-turbo", "gemini-pro"],
            }

        # Initialize sophisticated orchestrator
        orchestrator = PatternOrchestrator(api_keys=api_keys, pattern="gut")

        # Get available models from the orchestrator
        available_models = orchestrator.available_models

        # Map internal model names to user-friendly names
        model_mapping = {
            "anthropic": "claude-3-opus",
            "openai": "gpt-4-turbo", 
            "google": "gemini-pro",
            "mistral": "mistral-large",
            "cohere": "cohere-command",
            "perplexity": "perplexity-llama",
        }

        mapped_models = [model_mapping.get(model, model) for model in available_models]

        return {"status": "success", "models": mapped_models}
    except Exception as e:
        logger.error(f"Error getting available models: {str(e)}")
        # Return default list instead of error for better frontend experience
        return {
            "status": "success", 
            "models": ["claude-3-opus", "gpt-4-turbo", "gemini-pro"],
        }


@orchestrator_router.get("/orchestrator/patterns")
async def get_available_analysis_patterns():
    """
    Get all available analysis patterns for the sophisticated orchestrator

    Returns:
        List of available analysis patterns with descriptions
    """
    try:
        if not ORCHESTRATOR_AVAILABLE:
            # Fallback patterns if sophisticated orchestrator couldn't be imported
            logger.warning("Sophisticated orchestrator not available, returning default patterns")
            return {
                "status": "success",
                "patterns": [
                    {"name": "gut", "description": "Basic gut analysis pattern"},
                    {"name": "confidence", "description": "Confidence-based analysis"},
                    {"name": "critique", "description": "Critical analysis pattern"},
                ],
            }

        # Get patterns from the sophisticated orchestrator
        patterns = get_pattern_mapping()
        
        pattern_list = []
        for pattern_name, pattern_obj in patterns.items():
            if isinstance(pattern_obj, dict):
                # Handle dict format from fallback
                pattern_list.append({
                    "name": pattern_obj.get("name", pattern_name),
                    "description": pattern_obj.get("description", f"{pattern_name} analysis"),
                    "stages": pattern_obj.get("stages", ["initial", "meta", "hyper", "ultra"])
                })
            elif pattern_obj:
                # Handle object format from real implementation
                pattern_list.append({
                    "name": pattern_name,
                    "description": getattr(pattern_obj, 'description', f"{pattern_name} analysis"),
                    "stages": getattr(pattern_obj, 'stages', ["initial", "meta", "hyper", "ultra"])
                })

        return {"status": "success", "patterns": pattern_list}
    except Exception as e:
        logger.error(f"Error getting available patterns: {str(e)}")
        # Return default patterns instead of error
        return {
            "status": "success",
            "patterns": [
                {"name": "gut", "description": "Gut-based intuitive analysis"},
                {"name": "confidence", "description": "Confidence scoring and agreement tracking"},
                {"name": "critique", "description": "Structured critique and revision process"},
                {"name": "fact_check", "description": "Rigorous fact-checking process"},
                {"name": "perspective", "description": "Multi-perspective analysis"},
                {"name": "scenario", "description": "Scenario-based analysis"},
            ],
        }


@orchestrator_router.post("/orchestrator/feather", response_model=FeatherOrchestrationResponse)
async def process_with_feather_orchestration(request: FeatherOrchestrationRequest):
    """
    Process a prompt using the sophisticated 4-stage Feather orchestration

    Args:
        request: Feather orchestration request containing prompt, models, pattern, etc.

    Returns:
        Complete 4-stage orchestration results (Initial → Meta → Hyper → Ultra)
    """
    try:
        logger.info(
            f"Processing Feather orchestration request with pattern '{request.pattern}' and prompt: {request.prompt[:50]}..."
        )

        if not ORCHESTRATOR_AVAILABLE:
            raise HTTPException(
                status_code=503,
                detail="Sophisticated orchestrator not available. Please check server configuration.",
            )

        # Get API keys from environment
        api_keys = {
            "anthropic": os.getenv("ANTHROPIC_API_KEY"),
            "openai": os.getenv("OPENAI_API_KEY"),
            "google": os.getenv("GOOGLE_API_KEY"),
            "mistral": os.getenv("MISTRAL_API_KEY"),
            "perplexity": os.getenv("PERPLEXITY_API_KEY"),
            "cohere": os.getenv("COHERE_API_KEY"),
            "deepseek": os.getenv("DEEPSEEK_API_KEY"),
        }
        # Remove empty keys
        api_keys = {k: v for k, v in api_keys.items() if v}

        if not api_keys:
            raise HTTPException(
                status_code=500,
                detail="No API keys configured. Please set at least one LLM API key.",
            )

        # Initialize sophisticated orchestrator with selected pattern
        orchestrator = PatternOrchestrator(
            api_keys=api_keys, 
            pattern=request.pattern or "gut",
            output_format=request.output_format or "plain"
        )

        # Set ultra model if specified
        if request.ultra_model:
            # Map user-friendly names back to internal names
            model_reverse_mapping = {
                "claude-3-opus": "claude",
                "gpt-4-turbo": "chatgpt",
                "gemini-pro": "gemini",
                "mistral-large": "mistral",
                "cohere-command": "cohere",
                "perplexity-llama": "perplexity",
            }
            ultra_model = model_reverse_mapping.get(request.ultra_model, request.ultra_model)
            # Set the ultra model on the orchestrator
            setattr(orchestrator, 'ultra_model', ultra_model)

        # Run the sophisticated 4-stage orchestration
        result = await orchestrator.orchestrate_full_process(request.prompt)

        # Get the models that were actually used
        models_used = list(result["initial_responses"].keys())

        return {
            "status": "success",
            "initial_responses": result["initial_responses"],
            "meta_responses": result["meta_responses"],
            "hyper_responses": result["hyper_responses"],
            "ultra_response": result["ultra_response"],
            "processing_time": result["processing_time"],
            "pattern_used": request.pattern or "gut",
            "models_used": models_used,
        }
    except Exception as e:
        logger.error(f"Error processing Feather orchestration request: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error processing Feather orchestration: {str(e)}"
        )


@orchestrator_router.post("/orchestrator/process")
async def process_with_orchestrator(request: OrchestrationRequest):
    """
    Legacy endpoint for backward compatibility - now uses sophisticated PatternOrchestrator

    Args:
        request: Orchestration request containing prompt and options

    Returns:
        Processed results from the sophisticated orchestrator
    """
    try:
        logger.info(
            f"Processing legacy orchestration request with prompt: {request.prompt[:50]}..."
        )

        if not ORCHESTRATOR_AVAILABLE:
            raise HTTPException(
                status_code=503,
                detail="Sophisticated orchestrator not available. Please check server configuration.",
            )

        # Get API keys from environment
        api_keys = {
            "anthropic": os.getenv("ANTHROPIC_API_KEY"),
            "openai": os.getenv("OPENAI_API_KEY"),
            "google": os.getenv("GOOGLE_API_KEY"),
            "mistral": os.getenv("MISTRAL_API_KEY"),
            "perplexity": os.getenv("PERPLEXITY_API_KEY"),
            "cohere": os.getenv("COHERE_API_KEY"),
            "deepseek": os.getenv("DEEPSEEK_API_KEY"),
        }
        # Remove empty keys
        api_keys = {k: v for k, v in api_keys.items() if v}

        if not api_keys:
            raise HTTPException(
                status_code=500,
                detail="No API keys configured. Please set at least one LLM API key.",
            )

        # Map analysis_type to pattern for backward compatibility
        pattern_mapping = {
            "comparative": "confidence",  # Confidence analysis shows model agreement
            "factual": "fact_check",      # Fact check analysis for factual queries
            "critical": "critique",       # Critique analysis for critical thinking
        }
        analysis_type = request.analysis_type or "comparative"
        pattern = pattern_mapping.get(analysis_type, "gut")

        # Initialize sophisticated orchestrator
        orchestrator = PatternOrchestrator(
            api_keys=api_keys, 
            pattern=pattern,
            output_format="plain"
        )

        # Set lead model as ultra model if specified
        if request.lead_model:
            model_reverse_mapping = {
                "claude-3-opus": "claude",
                "gpt-4-turbo": "chatgpt", 
                "gemini-pro": "gemini",
                "mistral-large": "mistral",
                "openai-gpt4o": "chatgpt",
                "anthropic-claude": "claude",
                "google-gemini": "gemini",
                "deepseek-chat": "deepseek",
            }
            ultra_model = model_reverse_mapping.get(request.lead_model, "claude")
            # Set the ultra model on the orchestrator
            setattr(orchestrator, 'ultra_model', ultra_model)

        # Run the sophisticated orchestration
        result = await orchestrator.orchestrate_full_process(request.prompt)

        # Format result for backward compatibility
        return {
            "status": "success",
            "result": result["ultra_response"],
            "processing_time": result["processing_time"],
            "models_used": list(result["initial_responses"].keys()),
            "analysis_type": request.analysis_type,
            "pattern_used": pattern,
            # Include full sophisticated results for clients that can handle them
            "sophisticated_results": {
                "initial_responses": result["initial_responses"],
                "meta_responses": result["meta_responses"],
                "hyper_responses": result["hyper_responses"],
                "ultra_response": result["ultra_response"],
            }
        }
    except Exception as e:
        logger.error(f"Error processing orchestration request: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error processing request: {str(e)}"
        )
