"""
Analysis routes for the Ultra backend.

This module provides API routes for analyzing prompts with various models.
"""

import json
import logging
import os
import time
import traceback
from datetime import datetime
from typing import Dict, List, Any, Optional, Union

from fastapi import APIRouter, BackgroundTasks, Body, Depends, File, Form, HTTPException, Request, UploadFile, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from backend.config import Config
from backend.utils.cache import response_cache, generate_cache_key
from backend.utils.metrics import performance_metrics, update_metrics_history, processing_times
from backend.database.connection import get_db
from backend.decorators.cache_decorator import cached
from backend.database.models import User
from backend.services.auth_service import auth_service
from backend.services.cache_service import cache_service

# Import the mock service for development
from backend.services.mock_llm_service import MockLLMService

# Check if PatternOrchestrator is available, use mock if not
try:
    from backend.integrations.pattern_orchestrator import PatternOrchestrator
    ORCHESTRATOR_AVAILABLE = True
except ImportError:
    ORCHESTRATOR_AVAILABLE = False
    from backend.services.mock_llm_service import MockLLMService
    mock_service = MockLLMService()

# Check if PricingIntegration is available, use mock if not
try:
    from backend.integrations.pricing import PricingIntegration
    PRICING_INTEGRATION_AVAILABLE = True
except ImportError:
    PRICING_INTEGRATION_AVAILABLE = False
    from backend.services.mock_pricing_service import MockPricingService
    mock_pricing = MockPricingService()

# Configure logging
logger = logging.getLogger("analyze_routes")

# Create a router
analyze_router = APIRouter(tags=["Analysis"])

# Create a mock service instance
mock_service = MockLLMService()

# Define pattern name mappings
PATTERN_NAME_MAPPING = {
    "comparative": "comparative_analysis",
    "comprehensive": "comprehensive_analysis",
    "concise": "concise_analysis",
    "contextual": "contextual_understanding",
    "creative": "creative_exploration",
    "critical": "critical_evaluation",
    "empirical": "empirical_assessment",
    "evaluative": "evaluative_assessment",
    "explanatory": "explanatory_discourse",
    "investigative": "investigative_inquiry",
    "reflective": "reflective_consideration",
    "speculative": "speculative_reasoning",
    "structured": "structured_analysis",
    "custom": "custom_pattern",
}

async def get_current_user(request: Request, db: Session = Depends(get_db)) -> Optional[User]:
    """
    Get the current user from the request

    Args:
        request: FastAPI request
        db: Database session

    Returns:
        User if authenticated, None otherwise
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return None

    try:
        scheme, token = auth_header.split()
        if scheme.lower() != "bearer":
            return None

        user_id = auth_service.verify_token(token)
        if not user_id:
            return None

        # Convert to int
        try:
            user_id_int = int(user_id)
        except ValueError:
            return None

        return auth_service.get_user(db, user_id_int)
    except Exception as e:
        logger.error(f"Error getting user from token: {str(e)}")
        return None


@analyze_router.post("/api/analyze")
@cached(prefix="analyze", ttl=60*60*24)  # Cache for 24 hours
async def analyze_prompt(
    request: Request,
    prompt: str = Body(..., description="Prompt to analyze"),
    selected_models: List[str] = Body(..., description="Models to use"),
    ultra_model: str = Body(..., description="Ultra model to use"),
    pattern: Optional[str] = Body(None, description="Analysis pattern"),
    options: Dict[str, Any] = Body({}, description="Additional options"),
    user_id: Optional[str] = Body(None, description="User ID"),
    db: Session = Depends(get_db)
):
    """
    Analyze a prompt using multiple LLMs and an Ultra LLM

    Args:
        request: FastAPI request
        prompt: Prompt to analyze
        selected_models: Models to use for analysis
        ultra_model: Ultra model to use
        pattern: Analysis pattern
        options: Additional options
        user_id: User ID
        db: Database session

    Returns:
        Analysis results
    """
    # Get current user
    user = await get_current_user(request, db)

    # Start timer
    start_time = time.time()

    try:
        # Validate required fields
        if not prompt:
            return JSONResponse(
                status_code=400,
                content={"status": "error", "message": "Prompt is required"}
            )

        if not selected_models or not isinstance(selected_models, list):
            return JSONResponse(
                status_code=400,
                content={"status": "error", "message": "Selected models are required"}
            )

        if not ultra_model:
            return JSONResponse(
                status_code=400,
                content={"status": "error", "message": "Ultra model is required"}
            )

        # Map pattern name
        pattern_key = pattern.lower() if pattern else "comprehensive"
        pattern_name = PATTERN_NAME_MAPPING.get(pattern_key, "comprehensive_analysis")

        # Create cache key data for checking
        cache_key_data = {
            "prompt": prompt,
            "selected_models": sorted(selected_models),
            "ultra_model": ultra_model,
            "pattern": pattern_name,
            "options": options
        }

        # Check if we have cached results
        if await cache_service.exists("analyze", cache_key_data):
            # Update performance metrics
            logger.info(f"Cache hit for prompt: {prompt[:30]}...")

            # Get cached result
            cached_result = await cache_service.get("analyze", cache_key_data)
            if cached_result:
                return cached_result

        # Use mock service to process the request
        result = mock_service.analyze(
            prompt=prompt,
            llms=selected_models,
            ultra_llm=ultra_model,
            pattern=pattern_name,
            options=options
        )

        # Get processing time
        processing_time = time.time() - start_time

        # Add performance metrics
        result["performance"] = {
            "total_time_seconds": processing_time,
            "model_times": result.get("model_times", {}),
            "token_counts": result.get("token_counts", {})
        }

        # Add request info
        result["request"] = {
            "prompt": prompt,
            "selected_models": selected_models,
            "ultra_model": ultra_model,
            "pattern": pattern_name
        }

        # Cache the result for future requests
        await cache_service.set("analyze", cache_key_data, result)

        return result

    except Exception as e:
        logger.error(f"Error analyzing prompt: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": f"Error analyzing prompt: {str(e)}"}
        )

@analyze_router.post("/api/analyze-with-docs")
async def analyze_with_docs(
    background_tasks: BackgroundTasks,
    prompt: str = Form(...),
    selectedModels: str = Form(...),
    ultraModel: str = Form(...),
    files: List[UploadFile] = File([]),
    pattern: str = Form("Confidence Analysis"),
    options: str = Form("{}"),
    userId: str = Form(None),
):
    """Process documents and analyze them with models"""
    try:
        # Parse JSON strings
        try:
            selected_models = json.loads(selectedModels)
            options_dict = json.loads(options)
        except json.JSONDecodeError:
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",
                    "message": "Invalid JSON in selectedModels or options",
                },
            )

        # Process files if any
        if files:
            # In a real implementation, you would handle file processing
            # For now, we'll just acknowledge the files
            file_names = [file.filename for file in files]
            logger.info(f"Processing files: {', '.join(file_names)}")

        # Create a document context
        document_context = f"Analyzing with {len(files)} documents" if files else ""

        # Combine with prompt
        combined_prompt = f"{prompt}\n\n{document_context}" if document_context else prompt

        # Use the analyze endpoint to process the prompt
        # In a real implementation, you would properly process the documents
        # and incorporate their content into the analysis

        return {
            "status": "success",
            "message": "Document analysis initiated",
            "prompt": combined_prompt,
            "files_processed": len(files),
        }
    except Exception as e:
        logger.error(f"Error in analyze with docs: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": f"Error: {str(e)}"},
        )

# Second implementation of analyze that differs from the first one in main.py
@analyze_router.post("/api/analyze-legacy")
async def analyze_legacy(request: dict = Body(...)):
    """
    Analyze a prompt using multiple LLMs and an Ultra LLM (legacy implementation)
    """
    global processing_times
    start_processing = time.time()

    try:
        # Extract request parameters
        prompt = request.get("prompt", "")
        models = request.get("models", ["gpt4o", "gpt4turbo"])
        ultra_model = request.get("ultraModel", "gpt4o")
        pattern = request.get("pattern", "confidence")
        user_id = request.get("userId")
        session_id = request.get("sessionId")

        # Basic validation
        if not prompt.strip():
            raise HTTPException(status_code=400, detail="Prompt cannot be empty")

        # Use cache if available
        cache_key = generate_cache_key(prompt, models, ultra_model, pattern)
        cached_response = (
            response_cache.get(cache_key) if hasattr(response_cache, "get") else None
        )

        if cached_response:
            performance_metrics["cache_hits"] += 1
            logger.info(f"Cache hit for prompt: {prompt[:30]}...")
            end_processing = time.time()
            processing_time = end_processing - start_processing
            processing_times.append(processing_time)
            performance_metrics["requests_processed"] += 1
            update_metrics_history()

            return cached_response

        # Check if we should use mock
        if Config.use_mock and hasattr(Config, 'mock_service') and Config.mock_service:
            logger.info(f"Using mock service for prompt: {prompt[:30]}...")
            # Use the async analyze_prompt for consistency
            result = await Config.mock_service.analyze_prompt(
                prompt, models, ultra_model, pattern
            )

            # Cache the result
            if hasattr(response_cache, "update"):
                response_cache[cache_key] = result

            # Update metrics
            end_processing = time.time()
            processing_time = end_processing - start_processing
            processing_times.append(processing_time)
            performance_metrics["requests_processed"] += 1
            update_metrics_history()

            return result

        # Use orchestrator if available
        if ORCHESTRATOR_AVAILABLE:
            logger.info(f"Using pattern orchestrator for prompt: {prompt[:30]}...")
            # Get or create orchestrator
            orchestrator = PatternOrchestrator()
            orchestrator.ultra_model = ultra_model

            # Use the full process for better results
            result = await orchestrator.orchestrate_full_process(prompt)

            # Cache the result
            if hasattr(response_cache, "update"):
                response_cache[cache_key] = result

            # Update metrics
            end_processing = time.time()
            processing_time = end_processing - start_processing
            processing_times.append(processing_time)
            performance_metrics["requests_processed"] += 1
            update_metrics_history()

            return result

        # Fallback to basic analysis
        raise HTTPException(status_code=500, detail="No analysis service available")

    except Exception as e:
        logger.error(f"Error in analyze endpoint: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")