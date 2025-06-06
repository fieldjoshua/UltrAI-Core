#!/usr/bin/env python

"""
Analysis Routes

This module provides API routes for prompt analysis and progress tracking.
It implements the multi-layered architecture from the UltraLLMOrchestrator patent,
with robust error handling and resource management.
"""

import json
import time
from typing import List, Optional, Any

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Form,
    Request,
    UploadFile,
)
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.core.error_handling import (
    ResourceNotFoundError,
    ValidationError,
    ProcessingError,
    InternalServerError,
)
from app.database.connection import get_db
from app.database.models import User
from app.utils.cache_decorator import cached
from app.models import analysis as models
from app.models.analysis import AnalysisResultsResponse
from app.services.auth_service import auth_service
from app.services.cache_service import cache_service
from app.utils.logging import get_logger

# Configure logging
logger = get_logger("analyze_routes")

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

# Default FastAPI dependencies
REQUIRED_FORM = Form(...)
REQUIRED_FILE = File(...)
EMPTY_DICT = Depends(lambda: {})

# Form field dependencies
PROMPT_FORM = Form(...)
SELECTED_MODELS_FORM = Form(...)
ULTRA_MODEL_FORM = Form(...)
FILES_FORM = File(...)
PATTERN_FORM = Form(DEFAULT_PATTERN)
OPTIONS_FORM = Form(DEFAULT_OPTIONS)
USER_ID_FORM = Form(DEFAULT_USER_ID)

# Standard error messages
ERROR_MESSAGES = {
    "invalid_request": "Invalid request parameters",
    "analysis_not_found": "Analysis {analysis_id} not found",
    "internal_error": "An internal error occurred",
    "invalid_pattern": "Invalid analysis pattern: {pattern}",
    "no_models": "No valid models selected for processing",
    "processing_error": "Error processing analysis: {error}",
}

# Get database session
get_db_session = get_db

# Create empty dict for default options
EMPTY_OPTIONS = {}

# Create default dependencies
DEFAULT_DB = Depends(get_db_session)


def create_router(
    model_registry: Any,
    prompt_template_manager: Any,
    analysis_pipeline: Any,
    auth_service: Any = auth_service,
    cache_service: Any = cache_service,
) -> APIRouter:
    """
    Create the analysis router with dependencies.

    Args:
        model_registry: The model registry service
        prompt_template_manager: The prompt template manager service
        analysis_pipeline: The analysis pipeline service
        auth_service: The authentication service
        cache_service: The cache service

    Returns:
        APIRouter: The configured router
    """
    router = APIRouter(tags=["Analysis"])

    async def get_current_user(
        request: Request, db: Session = DEFAULT_DB
    ) -> Optional[User]:
        """
        Get the current user from the request.

        Args:
            request: The request object
            db: The database session

        Returns:
            Optional[User]: The current user if authenticated, None otherwise

        Raises:
            InternalServerError: If there is an error processing the token
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
            try:
                user_id_int = int(user_id)
            except ValueError:
                return None
            return auth_service.get_user(db, user_id_int)
        except Exception as e:
            logger.error(f"Error getting user from token: {str(e)}")
            raise InternalServerError("Error processing authentication token")

    @router.post("/api/analyze")
    @cached(prefix="analyze", ttl=60 * 60 * 24)
    async def analyze_prompt(
        request: Request,
        analysis_request: models.AnalysisRequest,
        db: Session = DEFAULT_DB,
    ) -> JSONResponse:
        """
        Analyze a prompt using the specified models and pattern.

        WARNING: This endpoint is for development/testing only. Do not use in production.

        Args:
            request: The request object
            analysis_request: The analysis request data
            db: The database session

        Returns:
            JSONResponse: The analysis results

        Raises:
            ValidationError: If required fields are missing
            ProcessingError: If there is an error processing the analysis
            InternalServerError: If there is an unexpected error
        """
        # Start timer
        start_time = time.time()

        try:
            # Validate required fields
            if not analysis_request.prompt:
                raise ValidationError(ERROR_MESSAGES["invalid_request"])

            if not analysis_request.selected_models:
                raise ValidationError(ERROR_MESSAGES["no_models"])

            if not analysis_request.ultra_model:
                raise ValidationError(ERROR_MESSAGES["invalid_request"])

            # Generate unique analysis ID
            analysis_id = (
                f"analysis_{int(time.time())}_{hash(str(analysis_request.prompt))}"
            )

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
                except json.JSONDecodeError:
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
                    raise ValidationError(ERROR_MESSAGES["no_models"])

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
                    options=analysis_request.options or EMPTY_OPTIONS,
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
                    "processing_time": processing_time,
                }

                return JSONResponse(content=response_data)

            except Exception as e:
                logger.error(f"Error processing analysis: {str(e)}")
                raise ProcessingError(
                    ERROR_MESSAGES["processing_error"].format(error=str(e))
                )

        except (ValidationError, ProcessingError):
            raise
        except Exception as e:
            logger.error(f"Error in analyze_prompt: {str(e)}")
            raise InternalServerError(ERROR_MESSAGES["internal_error"])

    @router.post("/api/analyze-with-docs")
    async def analyze_with_docs(
        background_tasks: BackgroundTasks,
        prompt: str = PROMPT_FORM,
        selected_models: str = SELECTED_MODELS_FORM,
        ultra_model: str = ULTRA_MODEL_FORM,
        files: List[UploadFile] = FILES_FORM,
        pattern: str = PATTERN_FORM,
        options: str = OPTIONS_FORM,
        user_id: str = USER_ID_FORM,
    ) -> JSONResponse:
        """
        Analyze a prompt with document context.

        Args:
            background_tasks: FastAPI background tasks
            prompt: The prompt to analyze
            selected_models: The models to use for analysis
            ultra_model: The ultra model to use
            files: The document files to analyze
            pattern: The analysis pattern to use
            options: Additional options for analysis
            user_id: The user ID

        Returns:
            JSONResponse: The analysis results

        Raises:
            ProcessingError: If there is an error processing the analysis
        """
        try:
            # Parse selected models
            try:
                models_list = json.loads(selected_models)
            except json.JSONDecodeError:
                models_list = [selected_models]

            # Process files
            processed_files = []
            for file in files:
                content = await file.read()
                processed_files.append(
                    {
                        "name": file.filename,
                        "content": content.decode(),
                        "type": file.content_type,
                    }
                )

            # Generate analysis ID
            analysis_id = f"analysis_{int(time.time())}_{hash(str(prompt))}"

            # Map pattern name
            pattern_name = pattern.lower() if pattern else "comprehensive"
            pattern_key = PATTERN_NAME_MAPPING.get(
                pattern_name, "comprehensive_analysis"
            )

            # Process analysis in background
            background_tasks.add_task(
                prompt_template_manager.analyze_with_docs,
                prompt=prompt,
                models=models_list,
                ultra_model=ultra_model,
                files=processed_files,
                pattern=pattern_key,
                options=json.loads(options) if options else EMPTY_OPTIONS,
                user_id=user_id,
            )

            return JSONResponse(
                content={
                    "status": "success",
                    "analysis_id": analysis_id,
                    "message": "Analysis started",
                }
            )

        except Exception as e:
            logger.error(f"Error in analyze_with_docs: {str(e)}")
            raise ProcessingError(
                ERROR_MESSAGES["processing_error"].format(error=str(e))
            )

    @router.get("/api/analyze/{analysis_id}/progress")
    async def get_analysis_progress(analysis_id: str) -> JSONResponse:
        """
        Get the progress of an analysis.

        Args:
            analysis_id: The ID of the analysis

        Returns:
            JSONResponse: The analysis progress

        Raises:
            ProcessingError: If there is an error getting the progress
        """
        try:
            progress = await prompt_template_manager.get_analysis_progress(analysis_id)
            return JSONResponse(content=progress)
        except Exception as e:
            logger.error(f"Error getting analysis progress: {str(e)}")
            raise ProcessingError(
                ERROR_MESSAGES["processing_error"].format(error=str(e))
            )

    @router.get(
        "/api/analyze/{analysis_id}/results", response_model=AnalysisResultsResponse
    )
    async def get_analysis_results(
        analysis_id: str,
        request: Request,
        db: Session = DEFAULT_DB,
    ) -> AnalysisResultsResponse:
        """
        Get the results of an analysis.

        Args:
            analysis_id: The ID of the analysis
            request: The request object
            db: The database session

        Returns:
            AnalysisResultsResponse: The analysis results

        Raises:
            ResourceNotFoundError: If the analysis is not found
            ProcessingError: If there is an error getting the results
            InternalServerError: If there is an unexpected error
        """
        try:
            # Get current user
            user = await get_current_user(request, db)

            # Get results from cache or service
            results = await prompt_template_manager.get_analysis_results(
                analysis_id, user.id if user else None
            )

            if not results:
                raise ResourceNotFoundError(
                    ERROR_MESSAGES["analysis_not_found"].format(analysis_id=analysis_id)
                )

            return results

        except (ResourceNotFoundError, ProcessingError):
            raise
        except Exception as e:
            logger.error(f"Error getting analysis results: {str(e)}")
            raise InternalServerError(ERROR_MESSAGES["internal_error"])

    return router
