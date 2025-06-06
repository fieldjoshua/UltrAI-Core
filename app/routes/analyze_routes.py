#!/usr/bin/env python

"""
Analysis Routes

This module provides API routes for prompt analysis and progress tracking.
"""

import json
import logging
import time
from typing import List, Optional

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

from app.database.connection import get_db
from app.database.models import User
from app.decorators.cache_decorator import cached
from app.models import analysis as models
from app.models.analysis import AnalysisResultsResponse
from app.services.auth_service import auth_service
from app.services.cache_service import cache_service

# Configure logging
logger = logging.getLogger("analyze_routes")


def create_router(model_registry, prompt_template_manager, analysis_pipeline):
    router = APIRouter(tags=["Analysis"])

    # Dependency injection for services
    def get_analysis_pipeline():
        return analysis_pipeline

    def get_model_registry():
        return model_registry

    def get_prompt_template_manager():
        return prompt_template_manager

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
            try:
                user_id_int = int(user_id)
            except ValueError:
                return None
            return auth_service.get_user(db, user_id_int)
        except Exception as e:
            logger.error(f"Error getting user from token: {str(e)}")
            return None

    @router.post("/api/analyze")
    @cached(prefix="analyze", ttl=60 * 60 * 24)
    async def analyze_prompt(
        request: Request,
        analysis_request: models.AnalysisRequest,
        db: Session = Depends(get_db_session),
        analysis_pipeline=Depends(get_analysis_pipeline),
        model_registry=Depends(get_model_registry),
        prompt_template_manager=Depends(get_prompt_template_manager),
    ):
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
            pattern_key = PATTERN_NAME_MAPPING.get(
                pattern_name, "comprehensive_analysis"
            )

            # Log the analysis request for debugging
            logger.debug(f"Processing analysis request: {analysis_request}")
            logger.debug(f"Using pattern: {pattern_name} (mapped to: {pattern_key})")

            # Parse selected_models to handle both string and list input
            selected_models = []
            if isinstance(analysis_request.selected_models, str):
                try:
                    selected_models = json.loads(analysis_request.selected_models)
                except:
                    selected_models = [analysis_request.selected_models]
            elif isinstance(analysis_request.selected_models, list):
                selected_models = analysis_request.selected_models

            # Use the PromptService to actually process the analysis
            try:
                # Get available models from the service
                available_models = model_registry.get_available_models()
                logger.info(f"Available models: {list(available_models.keys())}")

                # Validate that selected models exist in our registry
                valid_models = []
                for model in selected_models:
                    if model in available_models:
                        valid_models.append(model)
                    else:
                        logger.warning(f"Model {model} not found in registry, skipping")

                if not valid_models:
                    return JSONResponse(
                        status_code=400,
                        content={
                            "status": "error",
                            "message": ERROR_MESSAGES["no_models"],
                        },
                    )

                # Validate ultra model exists
                if analysis_request.ultra_model not in available_models:
                    logger.warning(
                        f"Ultra model {analysis_request.ultra_model} not found, using fallback"
                    )
                    ultra_model = valid_models[0]  # Use first valid model as fallback
                else:
                    ultra_model = analysis_request.ultra_model

                # Process the analysis using the prompt service
                logger.info(
                    f"Processing analysis with models: {valid_models}, ultra: {ultra_model}, pattern: {pattern_key}"
                )
                result = await prompt_template_manager.analyze_prompt(
                    prompt=analysis_request.prompt,
                    models=valid_models,
                    ultra_model=ultra_model,
                    pattern=pattern_key,
                    options=analysis_request.options or {},
                )

                # Log successful analysis
                logger.info(
                    f"Analysis completed successfully with {len(result.get('model_responses', {}))} model responses"
                )

                # Calculate processing time
                processing_time = time.time() - start_time

                # Format the response to ensure consistent format for frontend
                # Frontend expects direct access to model_responses and ultra_response
                response_data = {
                    "status": "success",
                    "analysis_id": analysis_id,
                    "model_responses": result.get("model_responses", {}),
                    "ultra_response": result.get("ultra_response", ""),
                    "performance": result.get("performance", {}),
                    "metadata": result.get("metadata", {}),
                }

                # Return the response
                return response_data
            except Exception as e:
                logger.error(f"Error formatting response: {str(e)}", exc_info=True)
                return JSONResponse(
                    status_code=500,
                    content={
                        "status": "error",
                        "message": f"Error formatting response: {str(e)}",
                    },
                )

        except Exception as e:
            logger.error(
                f"Unexpected error in analyze endpoint: {str(e)}", exc_info=True
            )
            return JSONResponse(
                status_code=500,
                content={
                    "status": "error",
                    "message": ERROR_MESSAGES["internal_error"],
                },
            )

    @router.post("/api/analyze-with-docs")
    async def analyze_with_docs(
        background_tasks: BackgroundTasks,
        prompt: str = Form(...),
        selected_models: str = Form(...),
        ultra_model: str = Form(...),
        files: List[UploadFile] = File([]),
        pattern: str = Form(DEFAULT_PATTERN),
        options: str = Form(DEFAULT_OPTIONS),
        user_id: str = Form(DEFAULT_USER_ID),
        prompt_template_manager=Depends(get_prompt_template_manager),
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
                file_names = [
                    file.filename for file in files if file.filename is not None
                ]
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
                status_code=500,
                content={"status": "error", "message": f"Error: {str(e)}"},
            )

    @router.get("/api/analyze/{analysis_id}/progress")
    async def get_analysis_progress(
        analysis_id: str,
        prompt_template_manager=Depends(get_prompt_template_manager),
    ):
        """
        Get the progress of a multi-stage analysis

        Args:
            analysis_id: The ID of the analysis to track
            prompt_template_manager: PromptTemplateManager instance

        Returns:
            Progress information for the analysis
        """
        try:
            # Get progress from the prompt service
            progress = await prompt_template_manager.get_analysis_progress(analysis_id)

            if not progress:
                raise HTTPException(
                    status_code=404, detail=f"Analysis {analysis_id} not found"
                )

            return {
                "status": "success",
                "analysis_id": analysis_id,
                "progress": progress,
            }
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error getting analysis progress: {str(e)}"
            )

    @router.get(
        "/api/analyze/{analysis_id}/results", response_model=AnalysisResultsResponse
    )
    async def get_analysis_results(
        analysis_id: str,
        request: Request,
        db: Session = default_db,
        prompt_template_manager=Depends(get_prompt_template_manager),
    ):
        """
        Get the results of a completed analysis

        Args:
            analysis_id: Unique identifier for the analysis
            request: FastAPI request
            db: Database session
            prompt_template_manager: PromptTemplateManager instance

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
            raise HTTPException(
                status_code=500, detail=ERROR_MESSAGES["internal_error"]
            )

    return router
