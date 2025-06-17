"""
Route handlers for the orchestrator service.
"""

from typing import Dict, Any, Optional, List
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from app.utils.logging import get_logger

logger = get_logger("orchestrator_routes")


class AnalysisRequest(BaseModel):
    """Request model for analysis endpoint."""

    query: str = Field(..., description="The query or text to analyze")
    analysis_type: str = Field(
        default="simple", description="Type of analysis to perform"
    )
    options: Optional[Dict[str, Any]] = Field(
        default=None, description="Additional analysis options"
    )
    user_id: Optional[str] = Field(
        default=None, description="User ID for cost tracking"
    )
    selected_models: Optional[List[str]] = Field(
        default=None, description="Models to use for analysis"
    )
    save_outputs: bool = Field(
        default=False, description="Whether to save pipeline outputs as JSON/TXT files"
    )


class AnalysisResponse(BaseModel):
    """Response model for analysis endpoint."""

    success: bool = Field(..., description="Whether the analysis was successful")
    results: Dict[str, Any] = Field(..., description="Analysis results")
    error: Optional[str] = Field(
        default=None, description="Error message if analysis failed"
    )
    processing_time: Optional[float] = Field(
        default=None, description="Processing time in seconds"
    )
    saved_files: Optional[Dict[str, str]] = Field(
        default=None,
        description="Paths to saved output files if save_outputs was enabled",
    )


def create_router() -> APIRouter:
    """
    Create the router with all endpoints.

    Returns:
        APIRouter: The configured router
    """
    router = APIRouter(tags=["Orchestrator"])

    @router.post("/orchestrator/analyze", response_model=AnalysisResponse)
    async def analyze_query(request: AnalysisRequest, http_request: Request):
        """
        Main analysis endpoint using the orchestration service.

        This endpoint provides the core analysis functionality by routing
        requests through the multi-stage orchestration pipeline.
        """
        try:
            import time

            start_time = time.time()

            logger.info(f"Starting analysis for query: {request.query[:100]}...")

            # Get orchestration service from app state
            if not hasattr(http_request.app.state, "orchestration_service"):
                raise HTTPException(
                    status_code=503, detail="Orchestration service not available"
                )

            orchestration_service = http_request.app.state.orchestration_service

            # Prepare options with save_outputs flag
            pipeline_options = request.options or {}
            pipeline_options["save_outputs"] = request.save_outputs

            # Run the analysis pipeline
            pipeline_results = await orchestration_service.run_pipeline(
                input_data=request.query,
                options=pipeline_options,
                user_id=request.user_id,
                selected_models=request.selected_models,
            )

            # Process results into response format
            analysis_results = {}
            saved_files = None

            for stage_name, stage_result in pipeline_results.items():
                if stage_name == "_metadata":
                    # Extract saved files info from metadata
                    if "saved_files" in stage_result:
                        saved_files = stage_result["saved_files"]
                    continue

                if hasattr(stage_result, "error") and stage_result.error:
                    analysis_results[stage_name] = {
                        "error": stage_result.error,
                        "status": "failed",
                    }
                else:
                    output = (
                        stage_result.output
                        if hasattr(stage_result, "output")
                        else stage_result
                    )
                    quality = None
                    if hasattr(stage_result, "quality") and stage_result.quality:
                        quality = stage_result.quality.__dict__

                    # Special handling: flatten Ultra-Synthesis so 'synthesis' sits at the top level
                    if (
                        stage_name == "ultra_synthesis"
                        and isinstance(output, dict)
                        and "synthesis" in output
                    ):
                        synthesis_val = output.get("synthesis")
                        if isinstance(synthesis_val, dict):
                            synthesis_text = (
                                synthesis_val.get("content")
                                or synthesis_val.get("text")
                                or ""
                            )
                            # Replace dict with normalized string for downstream clients
                            output["synthesis"] = synthesis_text
                        else:
                            synthesis_text = synthesis_val or ""
                        analysis_results[stage_name] = {
                            **output,  # exposes 'synthesis', 'meta_analysis', etc.
                            "output": synthesis_text,  # legacy alias expected by some clients
                            "quality": quality,
                            "status": "completed",
                        }
                    else:
                        analysis_results[stage_name] = {
                            "output": output,
                            "quality": quality,
                            "status": "completed",
                        }

            processing_time = time.time() - start_time

            logger.info(f"Analysis completed in {processing_time:.2f} seconds")
            if saved_files:
                logger.info(f"Output files saved: {saved_files}")

            return AnalysisResponse(
                success=True,
                results=analysis_results,
                processing_time=processing_time,
                saved_files=saved_files,
            )

        except Exception as e:
            logger.error(f"Analysis failed: {str(e)}")
            return AnalysisResponse(success=False, results={}, error=str(e))

    @router.get("/orchestrator/health")
    async def orchestrator_health(http_request: Request):
        """Check orchestrator service health."""
        try:
            if hasattr(http_request.app.state, "orchestration_service"):
                return {"status": "healthy", "service": "orchestration"}
            else:
                return {
                    "status": "degraded",
                    "service": "orchestration",
                    "error": "Service not initialized",
                }
        except Exception as e:
            return {"status": "error", "service": "orchestration", "error": str(e)}

    return router


router = create_router()  # Expose router for application
