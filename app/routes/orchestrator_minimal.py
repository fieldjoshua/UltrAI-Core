"""
Route handlers for the orchestrator service.
"""

from typing import Dict, Any, Optional, List
from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel, Field

from app.utils.logging import get_logger
from app.services.output_formatter import OutputFormatter
from app.middleware.auth_middleware import require_auth, AuthUser

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
    include_pipeline_details: bool = Field(
        default=False, description="Include all pipeline stages (initial responses, peer review) in output. Default returns only Ultra Synthesis."
    )
    include_initial_responses: bool = Field(
        default=False, description="Include initial model responses even in streamlined output"
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
    pipeline_info: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Information about the pipeline execution including progress and stages",
    )


def create_router() -> APIRouter:
    """
    Create the router with all endpoints.

    Returns:
        APIRouter: The configured router
    """
    router = APIRouter(tags=["Orchestrator"])

    @router.post("/orchestrator/analyze", response_model=AnalysisResponse)
    async def analyze_query(
        request: AnalysisRequest, 
        http_request: Request,
        current_user: AuthUser = Depends(require_auth)
    ):
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

            # If models not provided, select smartly
            selected_models = request.selected_models
            logger.info(f"📊 Models requested by client: {selected_models}")
            
            if not selected_models:
                try:
                    # Try to use defaults from orchestration service
                    default_models = await orchestration_service._default_models_from_env()
                    logger.info(f"🔍 Default models from env: {default_models}")
                    
                    if default_models:
                        selected_models = default_models[:2]  # Use first 2 available models
                        logger.info(f"✅ Using default models: {selected_models}")
                    else:
                        # Fallback to model selector service
                        if hasattr(http_request.app.state, "services"):
                            svc = http_request.app.state.services.get("model_selector")
                        else:
                            svc = None
                        if svc:
                            top = await svc.choose_models(
                                query=request.query,
                                candidate_models=None,
                                desired_count=2,
                                query_type=request.analysis_type,
                            )
                            selected_models = top
                            logger.info(f"🤖 Auto-selected model(s): {selected_models}")
                except Exception as e:
                    logger.error(f"Model selection failed: {e}")
                    # Hard fallback to ensure we have at least one model
                    selected_models = ["gpt-4o"]
                    logger.warning(f"⚠️ Using fallback model: {selected_models}")

            # Run the analysis pipeline
            pipeline_results = await orchestration_service.run_pipeline(
                input_data=request.query,
                options=pipeline_options,
                user_id=request.user_id,
                selected_models=selected_models,
            )

            # Process results into response format
            analysis_results = {}
            saved_files = None
            ultra_synthesis_result = None

            # Initialize output formatter
            formatter = OutputFormatter()

            # Ensure pipeline_results is a dict
            if not isinstance(pipeline_results, dict):
                logger.error(f"Pipeline returned unexpected type: {type(pipeline_results)}")
                return AnalysisResponse(
                    success=False,
                    results={},
                    error="Pipeline returned invalid results format",
                )

            # Debug logging
            logger.info(f"Pipeline results type: {type(pipeline_results)}")
            logger.info(
                f"Pipeline results keys: {list(pipeline_results.keys()) if isinstance(pipeline_results, dict) else 'Not a dict'}"
            )

            # First pass: extract ultra synthesis and metadata
            try:
                for stage_name, stage_result in pipeline_results.items():
                    if stage_name == "_metadata":
                        # Extract saved files info from metadata
                        if "saved_files" in stage_result:
                            saved_files = stage_result["saved_files"]
                        continue

                    if stage_name == "ultra_synthesis":
                        # Extract Ultra Synthesis result
                        if hasattr(stage_result, "error") and stage_result.error:
                            ultra_synthesis_result = {
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

                            if isinstance(output, dict):
                                # Check for synthesis or synthesis_enhanced
                                if "synthesis_enhanced" in output:
                                    ultra_synthesis_result = output["synthesis_enhanced"]
                                elif "synthesis" in output:
                                    synthesis_val = output.get("synthesis")
                                    if isinstance(synthesis_val, dict):
                                        ultra_synthesis_result = (
                                            synthesis_val.get("content")
                                            or synthesis_val.get("text")
                                            or ""
                                        )
                                    else:
                                        ultra_synthesis_result = synthesis_val or ""
                                else:
                                    ultra_synthesis_result = output
                            else:
                                ultra_synthesis_result = output

            except Exception as e:
                logger.error(f"Error processing pipeline results: {str(e)}", exc_info=True)
                return AnalysisResponse(
                    success=False,
                    results={},
                    error=f"Error processing pipeline results: {str(e)}",
                )

            # Second pass: handle pipeline details if requested
            if request.include_pipeline_details:
                logger.info("Processing pipeline details view")
                # Include all stages for detailed view
                try:
                    for stage_name, stage_result in pipeline_results.items():
                        if stage_name == "_metadata":
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

                            analysis_results[stage_name] = {
                                "output": output,
                                "quality": quality,
                                "status": "completed",
                            }

                except Exception as e:
                    logger.error(f"Error processing pipeline details: {str(e)}", exc_info=True)
                    # Fall back to simple output on error
                    if ultra_synthesis_result is not None:
                        analysis_results = {
                            "ultra_synthesis": ultra_synthesis_result,
                            "status": "completed",
                            "error": f"Could not process full pipeline details: {str(e)}",
                        }
                    else:
                        return AnalysisResponse(
                            success=False,
                            results={},
                            error=f"Error processing pipeline details: {str(e)}",
                        )

                # Use formatter to create enhanced output
                if not analysis_results.get("error"):
                    try:
                        formatted_output = formatter.format_pipeline_output(
                            pipeline_results,
                            include_initial_responses=True,
                            include_peer_review=True,
                            include_metadata=request.options.get("include_metadata", False)
                            if request.options
                            else False,
                        )

                        # Add formatted output to results
                        analysis_results["formatted_output"] = formatted_output
                    except Exception as e:
                        logger.error(f"Error formatting output: {str(e)}")
            else:
                # Return only Ultra Synthesis (default behavior)
                if ultra_synthesis_result is not None:
                    # Build pipeline data for formatter
                    formatter_input = {"ultra_synthesis": {"synthesis": ultra_synthesis_result}}

                    # Add initial responses if requested
                    if request.include_initial_responses and "initial_response" in pipeline_results:
                        initial_stage = pipeline_results["initial_response"]
                        if hasattr(initial_stage, "output"):
                            formatter_input["initial_response"] = initial_stage.output
                        else:
                            formatter_input["initial_response"] = initial_stage

                    # Create a formatted version
                    simple_formatted = formatter.format_pipeline_output(
                        formatter_input,
                        include_initial_responses=request.include_initial_responses,
                        include_peer_review=False,
                        include_metadata=False,
                    )

                    analysis_results = {
                        "ultra_synthesis": ultra_synthesis_result,
                        "formatted_synthesis": simple_formatted.get(
                            "full_document", ultra_synthesis_result
                        ),
                        "status": "completed",
                    }

                    # Add initial responses if requested
                    if request.include_initial_responses and "initial_responses" in simple_formatted:
                        analysis_results["initial_responses"] = simple_formatted["initial_responses"]

                else:
                    analysis_results = {
                        "error": "Ultra Synthesis stage not completed",
                        "status": "failed",
                    }

            processing_time = time.time() - start_time

            # Create pipeline info
            completed_stages = list(pipeline_results.keys())
            if "_metadata" in completed_stages:
                completed_stages.remove("_metadata")

            pipeline_info = {
                "stages_completed": completed_stages,
                "total_stages": len(completed_stages),
                "models_used": selected_models or [],
                "pipeline_type": "3-stage optimized" if len(completed_stages) >= 3 else "partial",
                "include_details": request.include_pipeline_details,
            }

            logger.info(f"Analysis completed in {processing_time:.2f} seconds")
            logger.info(f"Pipeline stages completed: {completed_stages}")
            if saved_files:
                logger.info(f"Output files saved: {saved_files}")

            return AnalysisResponse(
                success=True,
                results=analysis_results,
                processing_time=processing_time,
                saved_files=saved_files,
                pipeline_info=pipeline_info,
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
