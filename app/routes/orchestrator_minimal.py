"""
Route handlers for the orchestrator service.
"""

import time
import os
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field, field_validator

from app.utils.logging import get_logger
from app.services.output_formatter import OutputFormatter
from app.middleware.combined_auth_middleware import require_auth, AuthUser
from app.models.streaming_response import StreamingAnalysisRequest, StreamingConfig
from app.services.provider_health_manager import provider_health_manager
from app.services.sse_event_bus import sse_event_bus

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


class StatusResponse(BaseModel):
    """Response model for the service status endpoint."""
    status: str = Field(..., description="Service status (e.g., 'healthy', 'degraded', 'unavailable')")
    service_available: bool = Field(..., description="Whether the service is available to handle requests")
    message: str = Field(..., description="A human-readable message about the service status")
    environment: str = Field(..., description="The current application environment (e.g., 'development', 'production')")
    api_keys_configured: Dict[str, bool] = Field(..., description="Status of API key configuration for each provider")
    models: Dict[str, Any] = Field(..., description="Information about available and required models")
    provider_health: Dict[str, Any] = Field(..., description="Health status of the underlying model providers")
    timestamp: float = Field(..., description="The timestamp of the status check")

class ErrorDetail(BaseModel):
    """Standardized error detail for 503 responses."""
    providers_present: List[str] = Field(..., description="List of providers that are currently available.")
    required_providers: List[str] = Field(..., description="List of providers required for the service to be healthy.")

class ServiceUnavailableResponse(BaseModel):
    """Response model for 503 Service Unavailable errors."""
    detail: str = Field(..., description="A human-readable error message.")
    error_details: Optional[ErrorDetail] = Field(None, description="Detailed provider information for readiness failures.")


def create_router() -> APIRouter:
    """
    Create the router with all endpoints.

    Returns:
        APIRouter: The configured router
    """
    router = APIRouter(tags=["Orchestrator"])

    @router.get("/orchestrator/events")
    async def orchestrator_events(correlation_id: str, http_request: Request):
        """Server-Sent Events stream for real-time orchestration updates.

        Query params:
          - correlation_id: trace id to subscribe to
        """
        if not correlation_id:
            raise HTTPException(status_code=400, detail="correlation_id is required")

        # Allow read-only access (auth optional based on middleware config)
        async def gen():
            async for frame in sse_event_bus.subscribe(correlation_id):
                yield frame

        return StreamingResponse(
            gen(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )

    @router.get(
        "/orchestrator/status",
        response_model=StatusResponse,
        summary="Get Service Status",
        description="Checks the operational status of the orchestration service, including model availability and provider health.",
        responses={
            200: {"description": "Service is operational."},
            503: {"description": "Service is not initialized or in an error state.", "model": ServiceUnavailableResponse},
        }
    )
    async def get_service_status(http_request: Request):
        """
        Check the service status including model availability.

        Returns:
            dict: Service status with model counts and health
        """
        try:
            if not hasattr(http_request.app.state, "orchestration_service"):
                raise HTTPException(
                    status_code=503,
                    detail="Orchestration service not initialized"
                )

            orchestration_service = http_request.app.state.orchestration_service

            # Get available models
            available_models = await orchestration_service._default_models_from_env()
            model_count = len(available_models)

            # Soft display fallback: if empty or below minimum, provide a non-authoritative suggested list based on configured providers
            # This prevents empty UI while not changing availability policy downstream.
            if model_count < 2:
                fallback: List[str] = []
                try:
                    if os.getenv("OPENAI_API_KEY"):
                        fallback.extend(["gpt-4o", "gpt-3.5-turbo"])
                    if os.getenv("ANTHROPIC_API_KEY"):
                        fallback.extend(["claude-3-5-sonnet-20241022", "claude-3-haiku-20240307"])
                    if os.getenv("GOOGLE_API_KEY"):
                        fallback.extend(["gemini-1.5-pro", "gemini-1.5-flash"])
                except Exception:
                    pass
                # Deduplicate while preserving order
                seen = set()
                fallback = [m for m in fallback if not (m in seen or seen.add(m))]
                # Only use fallback if it helps reach at least two display models
                if len(fallback) >= 2:
                    logger.warning("orchestrator/status: using display fallback model list due to insufficient healthy models")
                    available_models = fallback
                    model_count = len(available_models)

            # Get provider health summary (non-fatal)
            try:
                health_summary = await provider_health_manager.get_health_summary()
                available_providers = health_summary["_system"]["available_providers"]
                degradation_message = await provider_health_manager.get_degradation_message()
            except Exception as _e:
                logger.warning(f"provider_health_manager unavailable: {_e}")
                health_summary = {"_system": {"available_providers": [], "total_providers": 0, "meets_requirements": False}}
                available_providers = []
                degradation_message = None

            # Check API key status
            api_key_status = {
                "openai": bool(os.getenv("OPENAI_API_KEY")),
                "anthropic": bool(os.getenv("ANTHROPIC_API_KEY")),
                "google": bool(os.getenv("GOOGLE_API_KEY")),
                "huggingface": bool(os.getenv("HUGGINGFACE_API_KEY"))
            }

            # Determine service status
            from app.config import Config
            required_models = Config.MINIMUM_MODELS_REQUIRED

            if model_count >= required_models and len(available_providers) >= 2:
                status = "healthy"
                service_available = True
                message = f"Service operational with {model_count} models"
            elif model_count >= 1 and Config.ENABLE_SINGLE_MODEL_FALLBACK:
                status = "degraded"
                service_available = True
                message = degradation_message or f"Service in degraded mode with only {model_count} model(s)"
            else:
                status = "unavailable"
                service_available = False
                message = degradation_message or f"Service unavailable. Only {model_count} model(s) available, {required_models} required"

            return {
                "status": status,
                "service_available": service_available,
                "message": message,
                "environment": Config.ENVIRONMENT,
                "api_keys_configured": api_key_status,
                "models": {
                    "available": available_models,
                    "count": model_count,
                    "required": required_models,
                    "single_model_fallback": Config.ENABLE_SINGLE_MODEL_FALLBACK
                },
                "provider_health": {
                    "available_providers": available_providers,
                    "total_providers": health_summary["_system"]["total_providers"],
                    "meets_requirements": health_summary["_system"]["meets_requirements"],
                    "details": {k: v for k, v in health_summary.items() if k != "_system"}
                },
                "timestamp": time.time()
            }

        except Exception as e:
            logger.error(f"Error checking service status: {e}", exc_info=True)
            raise HTTPException(
                status_code=503,
                detail=f"An unexpected error occurred: {str(e)}"
            )

    @router.post(
        "/orchestrator/analyze",
        response_model=AnalysisResponse,
        summary="Run Multi-Stage Analysis",
        description="Submits a query for analysis through a multi-stage pipeline involving multiple AI models.",
        responses={
            200: {"description": "Analysis completed successfully."},
            503: {"description": "Service is unavailable due to insufficient models or providers.", "model": ServiceUnavailableResponse},
        }
    )
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

            logger.info(
                f"Starting analysis for query: {request.query[:100]}...",
                extra={
                    "request_id": getattr(http_request.state, "request_id", None),
                    "correlation_id": getattr(http_request.state, "correlation_id", None)
                }
            )
            corr_id = (
                getattr(http_request.state, "correlation_id", None)
                or getattr(http_request.state, "request_id", None)
                or ""
            )
            # Notify start
            await sse_event_bus.publish(corr_id, "analysis_start", {"models": request.selected_models or []})

            # Get orchestration service from app state
            if not hasattr(http_request.app.state, "orchestration_service"):
                raise HTTPException(
                    status_code=503,
                    detail="Orchestration service is not initialized"
                )

            orchestration_service = http_request.app.state.orchestration_service

            # Check model availability BEFORE processing
            available_models = await orchestration_service._default_models_from_env()
            model_count = len(available_models)

            # Enforce minimum model requirement
            from app.config import Config as _Cfg  # local import to avoid top-level cycles
            required_models_cfg = getattr(_Cfg, "MINIMUM_MODELS_REQUIRED", 3)
            # Enforce required providers: OpenAI, Anthropic, Google
            required_providers = set(getattr(_Cfg, "REQUIRED_PROVIDERS", ["openai","anthropic","google"]))
            try:
                health_summary = await provider_health_manager.get_health_summary()
                available_providers_list = health_summary.get("_system", {}).get("available_providers", [])
                available_provider_set = set(available_providers_list)
                missing = [p for p in required_providers if p not in available_provider_set]
            except Exception:
                available_provider_set = set()
                missing = list(required_providers)

            if model_count < required_models_cfg or missing:
                logger.error(f"Insufficient models available: {model_count} < {required_models_cfg} or missing providers: {missing}")
                message = (
                    f"UltraAI requires at least {required_models_cfg} models and providers: "
                    f"{sorted(list(required_providers))}; missing: {sorted(missing)}; "
                    f"available_models={model_count}"
                )
                error_detail = ErrorDetail(
                    providers_present=sorted(list(available_provider_set)),
                    required_providers=sorted(list(required_providers)),
                )
                raise HTTPException(
                    status_code=503,
                    detail={
                        "detail": message,
                        "error_details": error_detail.dict()
                    }
                )

            # Use tracked orchestration if available
            if hasattr(orchestration_service, "set_request_context"):
                orchestration_service.set_request_context(http_request)

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
                        try:
                            from app.config import Config as _Cfg2
                            required_n = getattr(_Cfg2, "MINIMUM_MODELS_REQUIRED", 3)
                        except Exception:
                            required_n = 3
                        selected_models = default_models[:required_n]
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

            # Emit per-model selection events before running pipeline
            try:
                if selected_models:
                    for m in selected_models:
                        await sse_event_bus.publish(corr_id, "model_selected", {"model": m})
            except Exception:
                pass

            # Run the analysis pipeline
            # Stage start events
            await sse_event_bus.publish(corr_id, "initial_start", {})
            pipeline_results = await orchestration_service.run_pipeline(
                input_data=request.query,
                options=pipeline_options,
                user_id=request.user_id,
                selected_models=selected_models,
            )
            await sse_event_bus.publish(corr_id, "pipeline_complete", {})

            # Check for SERVICE_UNAVAILABLE error
            if isinstance(pipeline_results, dict) and pipeline_results.get("error") == "SERVICE_UNAVAILABLE":
                logger.error(f"Service unavailable: {pipeline_results.get('message')}")
                await sse_event_bus.publish(corr_id, "service_unavailable", pipeline_results)
                # Raise 503 with a flat message to satisfy error handler
                raise HTTPException(
                    status_code=503,
                    detail=str(pipeline_results.get("message", "Service temporarily unavailable"))
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

                    # Also expose meta_analysis (if present) for UI without enabling full details
                    try:
                        if "meta_analysis" in pipeline_results:
                            meta_stage = pipeline_results["meta_analysis"]
                            if hasattr(meta_stage, "output"):
                                analysis_results["meta_analysis"] = meta_stage.output
                            else:
                                analysis_results["meta_analysis"] = meta_stage
                    except Exception:
                        pass

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

            # Add degradation message if service is degraded
            degradation_message = await provider_health_manager.get_degradation_message()
            if degradation_message:
                pipeline_info["service_status"] = degradation_message

            logger.info(f"Analysis completed in {processing_time:.2f} seconds")
            logger.info(f"Pipeline stages completed: {completed_stages}")
            if saved_files:
                logger.info(f"Output files saved: {saved_files}")
            # Emit per-model completion events
            try:
                for m in (selected_models or []):
                    await sse_event_bus.publish(corr_id, "model_completed", {"model": m})
            except Exception:
                pass

            await sse_event_bus.publish(
                corr_id,
                "analysis_complete",
                {"processing_time": processing_time, "stages": completed_stages},
            )

            return AnalysisResponse(
                success=True,
                results=analysis_results,
                processing_time=processing_time,
                saved_files=saved_files,
                pipeline_info=pipeline_info,
            )

        except HTTPException:
            # Propagate HTTP errors (e.g., 503 when requirements aren't met)
            raise
        except Exception as e:
            logger.error(f"Analysis failed: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

    @router.post(
        "/orchestrator/analyze/stream",
        summary="Stream Multi-Stage Analysis via SSE",
        description="Submits a query for analysis and streams back real-time events as the pipeline progresses.",
        responses={
            200: {"description": "SSE stream successfully initiated."},
            503: {"description": "Service is unavailable or not initialized.", "model": ServiceUnavailableResponse},
            501: {"description": "Streaming functionality is not implemented or enabled."},
        }
    )
    async def analyze_query_stream(
        request: StreamingAnalysisRequest,
        http_request: Request,
        current_user: AuthUser = Depends(require_auth)
    ):
        """
        Streaming analysis endpoint using Server-Sent Events.

        This endpoint provides real-time updates as the orchestration pipeline
        processes through its stages, enabling responsive user interfaces.

        Returns:
            StreamingResponse: Server-Sent Events stream
        """
        try:
            logger.info(f"Starting streaming analysis for query: {request.query[:100]}...")

            # Get orchestration service
            if not hasattr(http_request.app.state, "orchestration_service"):
                raise HTTPException(
                    status_code=503,
                    detail={
                        "error": "SERVICE_UNAVAILABLE",
                        "message": "Orchestration service is not initialized",
                        "details": {
                            "reason": "The orchestration service has not been properly started. This is typically a server configuration issue.",
                            "action": "Please try again in a few moments or contact support if the issue persists."
                        }
                    }
                )

            orchestration_service = http_request.app.state.orchestration_service

            # Check if service supports streaming
            if not hasattr(orchestration_service, "stream_pipeline"):
                # Try to import and create streaming service
                try:
                    from app.services.streaming_orchestration_service import StreamingOrchestrationService

                    # Create streaming service with same dependencies
                    streaming_service = StreamingOrchestrationService(
                        model_registry=orchestration_service.model_registry,
                        quality_evaluator=orchestration_service.quality_evaluator,
                        rate_limiter=orchestration_service.rate_limiter,
                        token_manager=orchestration_service.token_manager,
                        transaction_service=orchestration_service.transaction_service
                    )

                    # Store for future requests
                    http_request.app.state.streaming_orchestration_service = streaming_service
                    orchestration_service = streaming_service

                except ImportError:
                    raise HTTPException(
                        status_code=501,
                        detail={
                            "error": "NOT_IMPLEMENTED",
                            "message": "Streaming is not available on this server",
                            "details": {
                                "reason": "The streaming module is not installed or configured",
                                "alternative": "Use POST /orchestrator/analyze for non-streaming analysis",
                                "action": "Please use the standard analysis endpoint instead"
                            }
                        }
                    )

            # Configure streaming
            streaming_config = StreamingConfig(
                enabled=True,
                chunk_size=request.chunk_size,
                synthesis_streaming="synthesis_chunks" in request.stream_stages,
                include_partial_responses="model_responses" in request.stream_stages
            )

            # Model selection (similar to non-streaming endpoint)
            selected_models = request.selected_models
            if not selected_models:
                try:
                    default_models = await orchestration_service._default_models_from_env()
                    if default_models:
                        selected_models = default_models[:2]
                    else:
                        selected_models = ["gpt-4o", "claude-3-5-sonnet-20241022"]
                except Exception as e:
                    logger.error(f"Model selection failed: {e}")
                    selected_models = ["gpt-4o"]

            # Create async generator for streaming
            async def event_stream():
                """Generate Server-Sent Events."""
                try:
                    async for event in orchestration_service.stream_pipeline(
                        input_data=request.query,
                        options=request.options,
                        user_id=request.user_id,
                        selected_models=selected_models,
                        stream_config=streaming_config
                    ):
                        yield event
                except Exception as e:
                    logger.error(f"Streaming error: {str(e)}")
                    yield f"data: {{'event': 'error', 'data': {{'error': '{str(e)}'}}}}\n\n"

            # Return streaming response
            return StreamingResponse(
                event_stream(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "X-Accel-Buffering": "no"  # Disable proxy buffering
                }
            )

        except HTTPException:
            # Propagate HTTP errors
            raise
        except Exception as e:
            logger.error(f"Streaming analysis failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

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
