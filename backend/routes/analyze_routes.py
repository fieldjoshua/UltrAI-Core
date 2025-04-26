#!/usr/bin/env python

"""
Analysis routes for the Ultra backend.

This module provides API routes for analyzing prompts with various models.
"""

import json
import logging

# import os # Removed unused import
# import sys # No longer used, assuming app structure handles path
import time

# import traceback # Removed unused import
# from datetime import datetime # Removed unused import
from typing import List, Optional, Dict, Any

from fastapi import (
    File,
    APIRouter,
    BackgroundTasks,
    Body,
    Depends,
    Form,
    HTTPException,
    Request,
    UploadFile,
)
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from backend.config import Config
from backend.database.connection import get_db
from backend.database.models import User, Analysis, Document
from backend.decorators.cache_decorator import cached
from backend.models import analysis as models
from backend.services.auth_service import auth_service
from backend.services.cache_service import cache_service
from backend.services.llm_service import LLMService, MockLLMService
from backend.utils.cache import generate_cache_key, response_cache
from backend.utils.metrics import (
    performance_metrics,
    processing_times,
    update_metrics_history,
)
from backend.utils.error_handler import handle_error

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


async def get_current_user(
    request: Request, db: Session = Depends(get_db)
) -> Optional[User]:
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
@cached(prefix="analyze", ttl=60 * 60 * 24)  # Cache for 24 hours
async def analyze_prompt(
    request: Request,
    analysis_request: models.AnalysisRequest,  # Ensure this model uses selected_models, ultra_model
    user_id: Optional[str] = Body(
        None, description="User ID"
    ),  # Keep user_id if needed
    db: Session = Depends(get_db),
):
    """
    Analyze a prompt using multiple LLMs and an Ultra LLM

    Args:
        request: FastAPI request
        analysis_request: Analysis request data
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
        if not analysis_request.prompt:
            return JSONResponse(
                status_code=400,
                content={"status": "error", "message": "Prompt is required"},
            )

        if not analysis_request.selected_models:
            return JSONResponse(
                status_code=400,
                content={"status": "error", "message": "Selected models are required"},
            )

        if not analysis_request.ultra_model:
            return JSONResponse(
                status_code=400,
                content={"status": "error", "message": "Ultra model is required"},
            )

        # Map pattern name
        pattern_name = (
            analysis_request.pattern.lower()
            if analysis_request.pattern
            else "comprehensive"
        )
        pattern_key = PATTERN_NAME_MAPPING.get(pattern_name, "comprehensive_analysis")

        # Create cache key data for checking
        cache_key_data = {
            "prompt": analysis_request.prompt,
            "selected_models": sorted(analysis_request.selected_models),
            "ultra_model": analysis_request.ultra_model,
            "pattern": pattern_key,
            "ala_carte_options": sorted(
                [opt.value for opt in analysis_request.ala_carte_options]
            )
            if analysis_request.ala_carte_options
            else [],
            "output_format": analysis_request.output_format.value,
            "options": analysis_request.options,
        }

        # Check if we have cached results
        if await cache_service.exists("analyze", cache_key_data):
            # Update performance metrics
            logger.info(f"Cache hit for prompt: {analysis_request.prompt[:30]}...")

            # Get cached result
            cached_result = await cache_service.get("analyze", cache_key_data)
            if cached_result:
                return cached_result

        # Use mock service to process the request
        result = mock_service.analyze(
            prompt=analysis_request.prompt,
            llms=analysis_request.selected_models,
            ultra_llm=analysis_request.ultra_model,
            pattern=pattern_key,
            ala_carte_options=analysis_request.ala_carte_options,
            output_format=analysis_request.output_format.value,
            options=analysis_request.options,
        )

        # Get processing time
        processing_time = time.time() - start_time

        # Add performance metrics
        result["performance"] = {
            "total_time_seconds": processing_time,
            "model_times": result.get("model_times", {}),
            "token_counts": result.get("token_counts", {}),
        }

        # Add request info
        result["request"] = {
            "prompt": analysis_request.prompt,
            "selected_models": sorted(analysis_request.selected_models),
            "ultra_model": analysis_request.ultra_model,
            "pattern": pattern_key,
        }

        # Cache the result for future requests
        await cache_service.set("analyze", cache_key_data, result)

        return result

    except Exception as e:
        logger.error(f"Error analyzing prompt: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": f"Error analyzing prompt: {str(e)}"},
        )


@analyze_router.post("/api/analyze-with-docs")
async def analyze_with_docs(
    background_tasks: BackgroundTasks,
    prompt: str = Form(...),
    selectedModels: str = Form(...),  # NOTE: Still uses old naming convention
    ultraModel: str = Form(...),  # NOTE: Still uses old naming convention
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
            file_names = [
                file.filename for file in files
            ]  # NOTE: Type error might occur here if file.filename can be None
            # Filter out potential None values before joining
            valid_file_names = [name for name in file_names if name is not None]
            logger.info(
                f"Processing files: {', '.join(valid_file_names)}"
            )  # Type error potentially fixed here

        # Create a document context
        document_context = f"Analyzing with {len(files)} documents" if files else ""

        # Combine with prompt
        combined_prompt = (
            f"{prompt}\n\n{document_context}" if document_context else prompt
        )

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


@analyze_router.post("/analyze")
async def analyze_document(
    document_id: str,
    llm_id: str,
    analysis_type: str,
    prompt: str,
    db: Session = Depends(get_db),
):
    """Analyze a document using the specified LLM."""
    try:
        # Check if document exists
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")

        # Create analysis record
        analysis = Analysis(
            document_id=document_id,
            llm_id=llm_id,
            analysis_type=analysis_type,
            prompt=prompt,
            status="processing",
        )
        db.add(analysis)
        db.commit()
        db.refresh(analysis)

        # Get LLM service
        llm_service = MockLLMService()  # TODO: Get from factory

        # Process document
        result = await llm_service.process_document(
            document_id=document_id,
            llm_id=llm_id,
            analysis_type=analysis_type,
            prompt=prompt,
        )

        # Update analysis record
        analysis.status = "completed"
        analysis.result = result["result"]
        db.commit()
        db.refresh(analysis)

        return {
            "analysis_id": analysis.id,
            "status": analysis.status,
            "result": analysis.result,
            "created_at": analysis.created_at,
        }

    except Exception as e:
        handle_error(e)


@analyze_router.get("/types")
async def get_analysis_types():
    """Get available analysis types."""
    return {
        "types": [
            {
                "id": "summarize",
                "name": "Text Summarization",
                "description": "Generate a concise summary of the document",
                "supported_llms": ["gpt-4", "claude-3", "llama-2"],
            },
            {
                "id": "sentiment",
                "name": "Sentiment Analysis",
                "description": "Analyze the emotional tone of the document",
                "supported_llms": ["gpt-4", "claude-3", "mistral"],
            },
            {
                "id": "key_points",
                "name": "Key Points Extraction",
                "description": "Extract main points and arguments from the document",
                "supported_llms": ["gpt-4", "claude-3", "mixtral"],
            },
            {
                "id": "topics",
                "name": "Topic Modeling",
                "description": "Identify main topics and themes in the document",
                "supported_llms": ["gpt-4", "claude-3", "llama-2"],
            },
            {
                "id": "entities",
                "name": "Entity Recognition",
                "description": "Identify and extract named entities from the document",
                "supported_llms": ["gpt-4", "claude-3", "mistral"],
            },
        ]
    }


@analyze_router.get("/{analysis_id}")
async def get_analysis(
    analysis_id: str,
    db: Session = Depends(get_db),
):
    """Get analysis results by ID."""
    try:
        analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")

        return {
            "analysis_id": analysis.id,
            "document_id": analysis.document_id,
            "llm_id": analysis.llm_id,
            "analysis_type": analysis.analysis_type,
            "status": analysis.status,
            "result": analysis.result,
            "created_at": analysis.created_at,
        }

    except Exception as e:
        handle_error(e)
