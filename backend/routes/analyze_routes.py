#!/usr/bin/env python

"""
Analysis Routes

This module provides API routes for prompt analysis and progress tracking.
"""

import json
import logging
import time
from typing import List, Optional, Dict, Any

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Body,
    Depends,
    File,
    Form,
    HTTPException,
    Request,
    UploadFile,
)
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from backend.models import analysis as models
from backend.models.analysis import (
    AnalysisProgress,
    AnalysisStage,
    AnalysisStageStatus,
    AnalysisProgressResponse,
    AnalysisResultsResponse,
)
from backend.database.connection import get_db
from backend.decorators.cache_decorator import cached
from backend.database.models import User
from backend.services.auth_service import auth_service
from backend.services.cache_service import cache_service
from backend.services.prompt_service import prompt_service
from backend.utils.auth import default_user_id
from backend.utils.db import default_db

# Import the mock service for development
from backend.services.mock_llm_service import MockLLMService

# Configure logging
logger = logging.getLogger("analyze_routes")

# Create a router
analyze_router = APIRouter(tags=["Analysis"])

# Create a mock service instance
mock_service = MockLLMService()

# Get database session
get_db_session = get_db

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

# Default values for form fields
DEFAULT_PATTERN = "Confidence Analysis"
DEFAULT_OPTIONS = "{}"
DEFAULT_USER_ID = None

# Default values for dependencies
default_db = Depends(get_db_session)
default_user_id = Body(None, description="User ID")

# Default values for form fields
default_prompt = Form(...)
default_selected_models = Form(...)
default_ultra_model = Form(...)
default_files = File([])
default_pattern = Form(DEFAULT_PATTERN)
default_options = Form(DEFAULT_OPTIONS)
default_user_id_form = Form(DEFAULT_USER_ID)

# Standard error messages
ERROR_MESSAGES = {
    "invalid_request": "Invalid request parameters",
    "analysis_not_found": "Analysis {analysis_id} not found",
    "internal_error": "An internal error occurred",
    "invalid_pattern": "Invalid analysis pattern: {pattern}",
    "no_models": "No valid models selected for processing",
    "processing_error": "Error processing analysis: {error}",
}


async def get_current_user(
    request: Request, db: Session = default_db
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
@cached(prefix="analyze", ttl=60*60*24)  # Cache for 24 hours
async def analyze_prompt(
    request: Request,
    analysis_request: models.AnalysisRequest,
    db: Session,
):
    """
    Analyze a prompt using multiple LLMs and an Ultra LLM

    Args:
        request: FastAPI request
        analysis_request: Analysis request data
        db: Database session

    Returns:
        Analysis results with progress tracking
    """
    # Start timer
    start_time = time.time()

    try:
        # Validate required fields
        if not analysis_request.prompt:
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",
                    "message": ERROR_MESSAGES["invalid_request"],
                },
            )

        if not analysis_request.selected_models:
            return JSONResponse(
                status_code=400,
                content={"status": "error", "message": ERROR_MESSAGES["no_models"]},
            )

        if not analysis_request.ultra_model:
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",
                    "message": ERROR_MESSAGES["invalid_request"],
                },
            )

        # Generate unique analysis ID
        analysis_id = f"analysis_{int(time.time())}_{hash(analysis_request.prompt)}"

        # Map pattern name
        pattern_name = (
            analysis_request.pattern.lower()
            if analysis_request.pattern
            else "comprehensive"
        )
        pattern_key = PATTERN_NAME_MAPPING.get(pattern_name, "comprehensive_analysis")

        # Process the prompt
        try:
            result = await prompt_service.process_prompt(analysis_request)
        except Exception as e:
            logger.error(f"Error processing analysis: {str(e)}")
            return JSONResponse(
                status_code=500,
                content={
                    "status": "error",
                    "message": ERROR_MESSAGES["processing_error"].format(error=str(e)),
                },
            )

        # Calculate processing time
        processing_time = time.time() - start_time

        # Return standardized response
        return {
            "status": "success",
            "analysis_id": analysis_id,
            "results": {
                "model_responses": result.model_responses,
                "ultra_response": result.ultra_response,
                "performance": {
                    "total_time_seconds": processing_time,
                    "model_times": result.model_times,
                    "token_counts": result.token_counts,
                },
            },
        }

    except Exception as e:
        logger.error(f"Unexpected error in analyze endpoint: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": ERROR_MESSAGES["internal_error"]},
        )


@analyze_router.post("/api/analyze-with-docs")
async def analyze_with_docs(
    background_tasks: BackgroundTasks,
    prompt: str = default_prompt,
    selected_models: str = default_selected_models,
    ultra_model: str = default_ultra_model,
    files: List[UploadFile] = default_files,
    pattern: str = default_pattern,
    options: str = default_options,
    user_id: str = default_user_id_form,
):
    """Process documents and analyze them with models"""
    try:
        # Parse JSON strings
        try:
            # Validate JSON but don't store unused variables
            json.loads(selected_models)
            json.loads(options)
        except json.JSONDecodeError:
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",
                    "message": "Invalid JSON in selected_models or options",
                },
            )

        # Process files if any
        if files:
            # In a real implementation, you would handle file processing
            # For now, we'll just acknowledge the files
            file_names = [file.filename for file in files if file.filename is not None]
            logger.info(f"Processing files: {', '.join(file_names)}")

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
            status_code=500, content={"status": "error", "message": f"Error: {str(e)}"}
        )


@analyze_router.get("/api/analyze/{analysis_id}/progress")
async def get_analysis_progress(
    analysis_id: str,
    db: Session,
):
    """
    Get the progress of a multi-stage analysis

    Args:
        analysis_id: The ID of the analysis to track
        db: Database session

    Returns:
        Progress information for the analysis
    """
    try:
        # Get progress from the prompt service
        progress = await prompt_service.get_analysis_progress(analysis_id)

        if not progress:
            raise HTTPException(
                status_code=404, detail=f"Analysis {analysis_id} not found"
            )

        return {"status": "success", "analysis_id": analysis_id, "progress": progress}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error getting analysis progress: {str(e)}"
        )


@analyze_router.get(
    "/api/analyze/{analysis_id}/results", response_model=AnalysisResultsResponse
)
async def get_analysis_results(
    analysis_id: str, request: Request, db: Session = default_db
):
    """
    Get the results of a completed analysis

    Args:
        analysis_id: Unique identifier for the analysis
        request: FastAPI request
        db: Database session

    Returns:
        Analysis results

    Raises:
        HTTPException: If analysis is not found or not completed
    """
    try:
        # Get results from cache
        results = await cache_service.get(
            "analyze_results", {"analysis_id": analysis_id}
        )

        if not results:
            # Check if analysis exists in progress
            progress = await cache_service.get(
                "analysis_progress", {"analysis_id": analysis_id}
            )

            if not progress:
                logger.warning(f"Analysis not found: {analysis_id}")
                raise HTTPException(
                    status_code=404,
                    detail=ERROR_MESSAGES["analysis_not_found"].format(
                        analysis_id=analysis_id
                    ),
                )

            if progress["status"] != "completed":
                logger.info(f"Analysis not completed: {analysis_id}")
                raise HTTPException(
                    status_code=400,
                    detail=ERROR_MESSAGES["analysis_not_completed"].format(
                        analysis_id=analysis_id
                    ),
                )

        # Ensure results is not None
        if results is None:
            logger.warning(f"Null results for analysis: {analysis_id}")
            results = {}

        # Validate results format
        try:
            # Check required fields
            required_fields = ["model_responses", "ultra_response", "performance"]
            for field in required_fields:
                if field not in results:
                    logger.error(f"Missing required field in results: {field}")
                    raise HTTPException(
                        status_code=500, detail=ERROR_MESSAGES["internal_error"]
                    )

            # Validate performance metrics
            performance = results["performance"]
            if not isinstance(performance, dict):
                logger.error("Invalid performance metrics format")
                raise HTTPException(
                    status_code=500, detail=ERROR_MESSAGES["internal_error"]
                )

            # Validate model responses
            model_responses = results["model_responses"]
            if not isinstance(model_responses, dict):
                logger.error("Invalid model responses format")
                raise HTTPException(
                    status_code=500, detail=ERROR_MESSAGES["internal_error"]
                )

            # Validate ultra response
            ultra_response = results["ultra_response"]
            if not isinstance(ultra_response, dict):
                logger.error("Invalid ultra response format")
                raise HTTPException(
                    status_code=500, detail=ERROR_MESSAGES["internal_error"]
                )

        except Exception as e:
            logger.error(f"Error validating results format: {str(e)}")
            raise HTTPException(
                status_code=500, detail=ERROR_MESSAGES["internal_error"]
            )

        return AnalysisResultsResponse(
            status="success", analysis_id=analysis_id, results=results
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting analysis results: {str(e)}")
        raise HTTPException(status_code=500, detail=ERROR_MESSAGES["internal_error"])
