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
Document Analysis Routes

This module provides API routes for document analysis, integrating with the Ultra LLM orchestrator.
"""

import json
import logging
import time
import uuid
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from fastapi.responses from sqlalchemy.orm import Session

from app.config import Config
from app.database.connection import get_db
from app.models.document_analysis import (
    DocumentAnalysisRequest,
    DocumentAnalysisResponse,
    DocumentChunkAnalysisRequest,
    DocumentChunkAnalysisResponse,
)
from app.services.cache_service import cache_service
from app.services.document_analysis_service import document_analysis_service
from app.services.document_processor import document_processor
from app.services.llm_config_service import llm_config_service
from app.services.prompt_service import PromptService

# Configure logging
logger = logging.getLogger("document_analysis_routes")

# Create a router
document_analysis_router = APIRouter(tags=["Document Analysis"])

# Define pattern name mappings (same as in analyze_routes.py)
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


# Dependency Injection
def get_prompt_service() -> PromptService:
    """Dependency provider for PromptService."""
    return PromptService(llm_config_service=llm_config_service)


@document_analysis_router.post(
    "/api/analyze-document", class DocumentAnalysisResponse(BaseModel):
    """Response model for documentanalysisresponse endpoint."""
    status: str
    data: Dict[str, Any]

response_model=DocumentAnalysisResponse
)
async def analyze_document(
    request: Request,
    document_analysis: DocumentAnalysisRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    prompt_svc: PromptService = Depends(get_prompt_service),
):
    """
    Analyze a document using multiple LLMs and an Ultra LLM

    Args:
        request: FastAPI request
        document_analysis: Document analysis request data
        background_tasks: FastAPI background tasks
        db: Database session
        prompt_svc: PromptService instance

    Returns:
        Analysis results with progress tracking
    """
    try:
        # Start timer
        start_time = time.time()

        # Validate required fields
        if not document_analysis.document_id:
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",
                    "message": "Document ID is required",
                },
            )

        if not document_analysis.selected_models:
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",
                    "message": "No models selected for processing",
                },
            )

        if not document_analysis.ultra_model:
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",
                    "message": "Ultra model is required",
                },
            )

        # Generate unique analysis ID
        analysis_id = f"doc_analysis_{int(time.time())}_{document_analysis.document_id}"

        # Map pattern name
        pattern_name = (
            document_analysis.pattern.lower()
            if document_analysis.pattern
            else "comprehensive"
        )
        pattern_key = PATTERN_NAME_MAPPING.get(pattern_name, "comprehensive_analysis")

        # Get document content
        try:
            # Retrieve document data
            from os import path

            from app.config import Config

            document_path = path.join(
                Config.DOCUMENT_STORAGE_PATH, document_analysis.document_id
            )
            metadata_path = path.join(document_path, "metadata.json")

            # Check if document exists
            if not path.exists(document_path):
                return JSONResponse(
                    status_code=404,
                    content={
                        "status": "error",
                        "message": f"Document not found: {document_analysis.document_id}",
                    },
                )

            # Read document metadata
            try:
                with open(metadata_path, "r") as f:
                    metadata = json.load(f)

                file_path = metadata.get("file_path", "")
                file_type = metadata.get("file_type", "")

                # Process document to extract content
                document_data = [
                    {
                        "id": document_analysis.document_id,
                        "path": file_path,
                        "name": metadata.get("original_filename", ""),
                        "type": file_type,
                    }
                ]

                # Process document using document processor
                processing_result = document_processor.process_documents(document_data)
                document_chunks = processing_result.get("chunks", [])

                if not document_chunks:
                    return JSONResponse(
                        status_code=400,
                        content={
                            "status": "error",
                            "message": "No content could be extracted from document",
                        },
                    )

                # Combine chunks for analysis
                document_content = "\n\n".join(
                    [chunk.get("text", "") for chunk in document_chunks]
                )

            except Exception as e:
                logger.error(f"Error reading document metadata: {str(e)}")
                return JSONResponse(
                    status_code=500,
                    content={
                        "status": "error",
                        "message": f"Error processing document: {str(e)}",
                    },
                )

        except Exception as e:
            logger.error(f"Error retrieving document: {str(e)}")
            return JSONResponse(
                status_code=500,
                content={
                    "status": "error",
                    "message": f"Error retrieving document: {str(e)}",
                },
            )

        # Validate selected_models
        try:
            # Get available models from the service
            available_models = llm_config_service.get_available_models()

            # Validate that selected models exist in our registry
            valid_models = []
            for model in document_analysis.selected_models:
                if model in available_models:
                    valid_models.append(model)
                else:
                    logger.warning(f"Model {model} not found in registry, skipping")

            if not valid_models:
                return JSONResponse(
                    status_code=400,
                    content={
                        "status": "error",
                        "message": "No valid models selected for processing",
                    },
                )

            # Validate ultra model exists
            if document_analysis.ultra_model not in available_models:
                logger.warning(
                    f"Ultra model {document_analysis.ultra_model} not found, using fallback"
                )
                ultra_model = valid_models[0]  # Use first valid model as fallback
            else:
                ultra_model = document_analysis.ultra_model

        except Exception as e:
            logger.error(f"Error validating models: {str(e)}")
            return JSONResponse(
                status_code=500,
                content={
                    "status": "error",
                    "message": f"Error validating models: {str(e)}",
                },
            )

        # Create analysis prompt based on document content
        analysis_prompt = (
            f"Please analyze the following document content:\n\n{document_content}"
        )

        # Process the analysis using the document analysis service
        try:
            logger.info(
                f"Processing document analysis with models: {valid_models}, ultra: {ultra_model}, pattern: {pattern_key}"
            )

            # Use the document analysis service to analyze the document
            result = await document_analysis_service.analyze_document(
                document_id=document_analysis.document_id,
                models=valid_models,
                ultra_model=ultra_model,
                pattern=pattern_key,
                options=document_analysis.options or {},
            )

            # Log successful analysis
            logger.info(
                f"Document analysis completed successfully with {len(result.get('model_responses', {}))} model responses"
            )

            # Calculate processing time
            processing_time = time.time() - start_time

            # Store the analysis results
            # Add document metadata to results
            result["document_metadata"] = {
                "id": document_analysis.document_id,
                "name": metadata.get("original_filename", ""),
                "type": file_type,
                "size": metadata.get("file_size", 0),
            }

            # Cache the results for retrieval
            await cache_service.set(
                "document_analysis_results",
                {"analysis_id": analysis_id},
                result,
                ttl=60 * 60 * 24,  # Cache for 24 hours
            )

            # Format the response
            response_data = {
                "status": "success",
                "analysis_id": analysis_id,
                "results": {
                    "model_responses": result.get("model_responses", {}),
                    "ultra_response": result.get("ultra_response", ""),
                    "performance": result.get("performance", {}),
                    "metadata": result.get("metadata", {}),
                    "document_metadata": result.get("document_metadata", {}),
                },
            }

            return response_data

        except Exception as e:
            logger.error(f"Error processing document analysis: {str(e)}", exc_info=True)
            return JSONResponse(
                status_code=500,
                content={
                    "status": "error",
                    "message": f"Error processing document analysis: {str(e)}",
                },
            )

    except Exception as e:
        logger.error(
            f"Unexpected error in document analysis endpoint: {str(e)}", exc_info=True
        )
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"An internal error occurred: {str(e)}",
            },
        )


@document_analysis_router.get("/api/document-analysis/{analysis_id}")
async def get_document_analysis_results(
    analysis_id: str,
    prompt_svc: PromptService = Depends(get_prompt_service),
):
    """
    Get the results of a document analysis

    Args:
        analysis_id: Unique identifier for the document analysis
        prompt_svc: PromptService instance

    Returns:
        Document analysis results
    """
    try:
        # Get results from cache
        results = await cache_service.get(
            "document_analysis_results", {"analysis_id": analysis_id}
        )

        if not results:
            # Analysis not found or expired
            return JSONResponse(
                status_code=404,
                content={
                    "status": "error",
                    "message": f"Analysis {analysis_id} not found",
                },
            )

        # Return the cached results
        return {
            "status": "success",
            "analysis_id": analysis_id,
            "results": {
                "model_responses": results.get("model_responses", {}),
                "ultra_response": results.get("ultra_response", ""),
                "performance": results.get("performance", {}),
                "metadata": results.get("metadata", {}),
                "document_metadata": results.get("document_metadata", {}),
            },
        }

    except Exception as e:
        logger.error(f"Error retrieving document analysis results: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Error retrieving results: {str(e)}",
            },
        )
