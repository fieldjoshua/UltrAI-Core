"""
Route handlers for the orchestrator service.
"""

import time
from typing import Dict, Any, Optional, List
import os
from fastapi import APIRouter, HTTPException, Request, Depends
import asyncio
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.utils.logging import get_logger
from app.services.output_formatter import OutputFormatter
from app.middleware.combined_auth_middleware import require_auth, AuthUser
from app.services.model_health_cache import model_health_cache
from app.models.streaming_response import StreamingAnalysisRequest, StreamingConfig

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
        default=False,
        description="Include all pipeline stages (initial responses, peer review) in output. Default returns only Ultra Synthesis.",
    )
    include_initial_responses: bool = Field(
        default=False,
        description="Include initial model responses even in streamlined output",
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

    @router.get(
        "/orchestrator/status",
        summary="Get orchestration service status",
        description="Check if the orchestration service is ready to handle requests. Returns model availability and provider status.",
        responses={
            200: {
                "description": "Service status",
                "content": {
                    "application/json": {
                        "example": {
                            "status": "healthy",
                            "service_available": True,
                            "message": "Service operational with 3 models",
                            "models": {
                                "available": ["gpt-4", "claude-3-5-sonnet-20241022", "gemini-1.5-flash"],
                                "count": 3,
                                "required": 3,
                                "single_model_fallback": False,
                                "providers_present": ["openai", "anthropic", "google"],
                                "required_providers": ["openai", "anthropic", "google"]
                            },
                            "ready": True,
                            "timestamp": 1234567890.123
                        }
                    }
                }
            }
        }
    )
    async def get_service_status(http_request: Request):
        """Check the service status including model availability."""
        try:
            if not hasattr(http_request.app.state, "orchestration_service"):
                return {
                    "status": "error",
                    "message": "Orchestration service not initialized",
                    "service_available": False,
                }

            # Fast-fail for status endpoint: avoid network probes; use cached health first
            available_models = []
            try:
                candidates = [
                    ("gpt-4o", os.getenv("OPENAI_API_KEY")),
                    ("gpt-3.5-turbo", os.getenv("OPENAI_API_KEY")),
                    ("claude-3-5-sonnet-20241022", os.getenv("ANTHROPIC_API_KEY")),
                    ("claude-3-5-haiku-20241022", os.getenv("ANTHROPIC_API_KEY")),
                    ("gemini-1.5-pro", os.getenv("GOOGLE_API_KEY")),
                    ("gemini-1.5-flash", os.getenv("GOOGLE_API_KEY")),
                ]
                for model, key in candidates:
                    if not key:
                        continue
                    cached_ok = model_health_cache.get_cached_health(model)
                    if cached_ok:
                        available_models.append(model)
            except Exception as _e:
                logger.warning(f"status fast-fail path error: {_e}")

            # If cache produced no results, fall back to service discovery with a very short timeout
            if not available_models and hasattr(http_request.app.state, "orchestration_service"):
                orchestration_service = http_request.app.state.orchestration_service
                try:
                    available_models = await asyncio.wait_for(
                        orchestration_service._default_models_from_env(), timeout=2.0
                    )
                except Exception:
                    # On timeout or error, keep fast-fail behavior (no probes)
                    available_models = []

            model_count = len(available_models)

            # Determine service status
            from app.config import Config

            required_models = Config.MINIMUM_MODELS_REQUIRED
            required_providers = set(getattr(Config, "REQUIRED_PROVIDERS", []))

            # Infer providers from model names
            providers_present = set()
            for m in available_models:
                if m.startswith("gpt") or m.startswith("o1"):
                    providers_present.add("openai")
                elif m.startswith("claude"):
                    providers_present.add("anthropic")
                elif m.startswith("gemini"):
                    providers_present.add("google")

            if model_count >= required_models and (
                not required_providers or required_providers.issubset(providers_present)
            ):
                status = "healthy"
                service_available = True
                message = f"Service operational with {model_count} models"
            elif model_count >= 1 and Config.ENABLE_SINGLE_MODEL_FALLBACK:
                status = "degraded"
                service_available = True
                message = f"Service in degraded mode with only {model_count} model(s)"
            else:
                status = "unavailable"
                service_available = False
                # For status endpoint, prefer count-based message per tests
                if model_count < required_models:
                    message = (
                        f"Service unavailable. Only {model_count} model(s) available, {required_models} required"
                    )
                elif required_providers and not required_providers.issubset(
                    providers_present
                ):
                    missing = list(required_providers - providers_present)
                    message = f"Service unavailable. Missing providers: {missing}"
                else:
                    message = (
                        f"Service unavailable. Only {model_count} model(s) available, {required_models} required"
                    )

            return {
                "status": status,
                "service_available": service_available,
                "message": message,
                "models": {
                    "available": available_models,
                    "count": model_count,
                    "required": required_models,
                    "single_model_fallback": Config.ENABLE_SINGLE_MODEL_FALLBACK,
                    "providers_present": list(providers_present),
                    "required_providers": (
                        list(required_providers) if required_providers else []
                    ),
                },
                "ready": service_available and status == "healthy",
                "timestamp": time.time(),
            }

        except Exception as e:
            logger.error(f"Error checking service status: {e}")
            return {"status": "error", "message": str(e), "service_available": False}

    @router.post(
        "/orchestrator/analyze",
        response_model=AnalysisResponse,
        summary="Analyze text using multi-model orchestration",
        description="Process text through the 3-stage Ultra Synthesis™ pipeline with multiple LLMs.",
        responses={
            200: {
                "description": "Analysis completed successfully",
                "content": {
                    "application/json": {
                        "example": {
                            "success": True,
                            "results": {
                                "ultra_synthesis": "The comprehensive analysis shows...",
                                "formatted_synthesis": "# Analysis Results\n\nThe comprehensive analysis...",
                                "status": "completed"
                            },
                            "processing_time": 12.34,
                            "pipeline_info": {
                                "stages_completed": ["initial_response", "peer_review_and_revision", "ultra_synthesis"],
                                "total_stages": 3,
                                "models_used": ["gpt-4", "claude-3-5-sonnet-20241022", "gemini-1.5-flash"],
                                "pipeline_type": "3-stage optimized",
                                "include_details": False
                            }
                        }
                    }
                }
            },
            503: {
                "description": "Service unavailable due to insufficient models or missing providers",
                "content": {
                    "application/json": {
                        "example": {
                            "error": "SERVICE_UNAVAILABLE",
                            "message": "Missing required providers: ['anthropic']",
                            "details": {
                                "providers_present": ["openai", "google"],
                                "required_providers": ["openai", "anthropic", "google"],
                                "missing_providers": ["anthropic"],
                                "selected_models": ["gpt-4", "gemini-1.5-flash"]
                            }
                        }
                    }
                }
            }
        }
    )
    async def analyze_query(
        request: AnalysisRequest,
        http_request: Request,
        current_user: AuthUser = Depends(require_auth),
    ):
        """Main analysis endpoint using the orchestration service."""
        try:
            import time

            start_time = time.time()

            logger.info(
                f"Starting analysis for query: {request.query[:100]}...",
                extra={
                    "request_id": getattr(http_request.state, "request_id", None),
                    "correlation_id": getattr(
                        http_request.state, "correlation_id", None
                    ),
                },
            )

            # Get orchestration service from app state
            if not hasattr(http_request.app.state, "orchestration_service"):
                raise HTTPException(
                    status_code=503, detail="Orchestration service not available"
                )

            orchestration_service = http_request.app.state.orchestration_service

            # Use tracked orchestration if available
            if hasattr(orchestration_service, "set_request_context"):
                orchestration_service.set_request_context(http_request)

            # Prepare options with save_outputs flag
            pipeline_options = request.options or {}
            pipeline_options["save_outputs"] = request.save_outputs

            # If models not provided, select smartly (require 3 healthy models)
            selected_models = request.selected_models
            logger.info(f"📊 Models requested by client: {selected_models}")
            from app.config import Config as _Cfg

            required_models = _Cfg.MINIMUM_MODELS_REQUIRED
            # Parse REQUIRED_PROVIDERS from env at request time so tests can control it dynamically
            env_req = os.getenv("REQUIRED_PROVIDERS", "").strip()
            if env_req:
                required_providers = set([p for p in env_req.replace(" ", "").split(",") if p])
            else:
                required_providers = set()

            if not selected_models:
                try:
                    default_models = (
                        await orchestration_service._default_models_from_env()
                    )
                    logger.info(f"🔍 Default models from env: {default_models}")
                    if default_models:
                        selected_models = default_models[:required_models]
                        logger.info(f"✅ Using default models: {selected_models}")
                except Exception as e:
                    logger.error(f"Model selection failed: {e}")

            # Calculate providers present from selected models
            providers_present = set()
            if selected_models:
                for m in selected_models:
                    if m.startswith("gpt") or m.startswith("o1"):
                        providers_present.add("openai")
                    elif m.startswith("claude"):
                        providers_present.add("anthropic")
                    elif m.startswith("gemini"):
                        providers_present.add("google")

            # Enforce gating: prefer explicit missing provider error over count error
            if required_providers and not required_providers.issubset(providers_present):
                missing = list(required_providers - providers_present)
                raise HTTPException(
                    status_code=503,
                    detail={
                        "error": "SERVICE_UNAVAILABLE",
                        "message": f"Missing required providers: {missing}",
                        "details": {
                            "providers_present": list(providers_present),
                            "required_providers": list(required_providers),
                            "missing_providers": missing,
                            "selected_models": selected_models
                        },
                    },
                )

            if not selected_models or len(selected_models) < required_models:
                raise HTTPException(
                    status_code=503,
                    detail={
                        "error": "SERVICE_UNAVAILABLE",
                        "message": f"Insufficient healthy models. Require {required_models}.",
                        "details": {
                            "selected_models": selected_models or [],
                            "required_models": required_models,
                            "providers_present": list(providers_present),
                            "required_providers": list(required_providers),
                        },
                    },
                )

            # Run the analysis pipeline
            pipeline_results = await orchestration_service.run_pipeline(
                input_data=request.query,
                options=pipeline_options,
                user_id=request.user_id,
                selected_models=selected_models,
            )

            # Check for SERVICE_UNAVAILABLE error
            if (
                isinstance(pipeline_results, dict)
                and pipeline_results.get("error") == "SERVICE_UNAVAILABLE"
            ):
                logger.error(f"Service unavailable: {pipeline_results.get('message')}")
                # Return 503 Service Unavailable
                raise HTTPException(
                    status_code=503,
                    detail={
                        "error": "SERVICE_UNAVAILABLE",
                        "message": pipeline_results.get(
                            "message", "Service temporarily unavailable"
                        ),
                        "details": pipeline_results.get("details", {}),
                    },
                )

            # Process results into response format
            analysis_results = {}
            saved_files = None
            ultra_synthesis_result = None

            # Initialize output formatter
            formatter = OutputFormatter()

            # Ensure pipeline_results is a dict
            if not isinstance(pipeline_results, dict):
                logger.error(
                    f"Pipeline returned unexpected type: {type(pipeline_results)}"
                )
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
                            if (
                                hasattr(stage_result, "quality")
                                and stage_result.quality
                            ):
                                quality = stage_result.quality.__dict__

                            if isinstance(output, dict):
                                # Check for synthesis or synthesis_enhanced
                                if "synthesis_enhanced" in output:
                                    ultra_synthesis_result = output[
                                        "synthesis_enhanced"
                                    ]
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
                logger.error(
                    f"Error processing pipeline results: {str(e)}", exc_info=True
                )
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
                            if (
                                hasattr(stage_result, "quality")
                                and stage_result.quality
                            ):
                                quality = stage_result.quality.__dict__

                            analysis_results[stage_name] = {
                                "output": output,
                                "quality": quality,
                                "status": "completed",
                            }

                except Exception as e:
                    logger.error(
                        f"Error processing pipeline details: {str(e)}", exc_info=True
                    )
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
                            include_metadata=(
                                request.options.get("include_metadata", False)
                                if request.options
                                else False
                            ),
                        )

                        # Add formatted output to results
                        analysis_results["formatted_output"] = formatted_output
                    except Exception as e:
                        logger.error(f"Error formatting output: {str(e)}")
            else:
                # Return only Ultra Synthesis (default behavior)
                if ultra_synthesis_result is not None:
                    # Build pipeline data for formatter
                    formatter_input = {
                        "ultra_synthesis": {"synthesis": ultra_synthesis_result}
                    }

                    # Add initial responses if requested
                    if (
                        request.include_initial_responses
                        and "initial_response" in pipeline_results
                    ):
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
                    if (
                        request.include_initial_responses
                        and "initial_responses" in simple_formatted
                    ):
                        analysis_results["initial_responses"] = simple_formatted[
                            "initial_responses"
                        ]

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
                "pipeline_type": (
                    "3-stage optimized" if len(completed_stages) >= 3 else "partial"
                ),
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

        except HTTPException as exc:
            # Bubble up HTTP exceptions so tests/clients receive intended status codes (e.g., 503 gating)
            raise exc
        except Exception as e:
            logger.error(f"Analysis failed: {str(e)}")
            return AnalysisResponse(success=False, results={}, error=str(e))

    @router.post(
        "/orchestrator/analyze/stream",
        summary="Stream analysis results using SSE",
        description="Process text through the orchestration pipeline with real-time Server-Sent Events updates.",
        responses={
            200: {
                "description": "SSE stream established",
                "content": {
                    "text/event-stream": {
                        "example": "data: {\"event\": \"analysis_start\", \"timestamp\": 1234567890.123}\n\n"
                    }
                }
            },
            503: {
                "description": "Service unavailable due to insufficient models or missing providers",
                "content": {
                    "application/json": {
                        "example": {
                            "error": "SERVICE_UNAVAILABLE",
                            "message": "Insufficient healthy models. Require 3.",
                            "details": {
                                "selected_models": ["gpt-4"],
                                "required_models": 3,
                                "providers_present": ["openai"],
                                "required_providers": ["openai", "anthropic", "google"]
                            }
                        }
                    }
                }
            }
        }
    )
    async def analyze_query_stream(
        request: StreamingAnalysisRequest,
        http_request: Request,
        current_user: AuthUser = Depends(require_auth),
    ):
        """Streaming analysis endpoint using Server-Sent Events."""
        try:
            logger.info(
                f"Starting streaming analysis for query: {request.query[:100]}..."
            )

            # Get orchestration service
            if not hasattr(http_request.app.state, "orchestration_service"):
                raise HTTPException(
                    status_code=503, detail="Orchestration service not available"
                )

            orchestration_service = http_request.app.state.orchestration_service

            # Check if service supports streaming
            if not hasattr(orchestration_service, "stream_pipeline"):
                # Try to import and create streaming service
                try:
                    from app.services.streaming_orchestration_service import (
                        StreamingOrchestrationService,
                    )

                    # Create streaming service with same dependencies
                    streaming_service = StreamingOrchestrationService(
                        model_registry=orchestration_service.model_registry,
                        quality_evaluator=orchestration_service.quality_evaluator,
                        rate_limiter=orchestration_service.rate_limiter,
                        token_manager=orchestration_service.token_manager,
                        transaction_service=orchestration_service.transaction_service,
                    )

                    # Store for future requests
                    http_request.app.state.streaming_orchestration_service = (
                        streaming_service
                    )
                    orchestration_service = streaming_service

                except ImportError:
                    raise HTTPException(
                        status_code=501,
                        detail="Streaming not implemented. Use /orchestrator/analyze for non-streaming.",
                    )

            # Configure streaming
            streaming_config = StreamingConfig(
                enabled=True,
                chunk_size=request.chunk_size,
                synthesis_streaming="synthesis_chunks" in request.stream_stages,
                include_partial_responses="model_responses" in request.stream_stages,
            )

            # Model selection (similar to non-streaming endpoint)
            selected_models = request.selected_models
            from app.config import Config as _Cfg

            required_models = _Cfg.MINIMUM_MODELS_REQUIRED
            required_providers = set(getattr(_Cfg, "REQUIRED_PROVIDERS", []))
            if not selected_models:
                try:
                    default_models = (
                        await orchestration_service._default_models_from_env()
                    )
                    if default_models:
                        selected_models = default_models[:required_models]
                except Exception as e:
                    logger.error(f"Model selection failed: {e}")

            # Calculate providers present from selected models
            providers_present = set()
            if selected_models:
                for m in selected_models:
                    if m.startswith("gpt") or m.startswith("o1"):
                        providers_present.add("openai")
                    elif m.startswith("claude"):
                        providers_present.add("anthropic")
                    elif m.startswith("gemini"):
                        providers_present.add("google")

            if not selected_models or len(selected_models) < required_models:
                raise HTTPException(
                    status_code=503,
                    detail={
                        "error": "SERVICE_UNAVAILABLE",
                        "message": f"Insufficient healthy models. Require {required_models}.",
                        "details": {
                            "selected_models": selected_models or [],
                            "required_models": required_models,
                            "providers_present": list(providers_present),
                            "required_providers": list(required_providers)
                        },
                    },
                )

            if required_providers and not required_providers.issubset(
                providers_present
            ):
                missing = list(required_providers - providers_present)
                raise HTTPException(
                    status_code=503,
                    detail={
                        "error": "SERVICE_UNAVAILABLE",
                        "message": f"Missing required providers: {missing}",
                        "details": {
                            "providers_present": list(providers_present),
                            "required_providers": list(required_providers),
                            "missing_providers": missing,
                            "selected_models": selected_models
                        },
                    },
                )

            # Create async generator for streaming
            async def event_stream():
                """Generate Server-Sent Events."""
                try:
                    async for event in orchestration_service.stream_pipeline(
                        input_data=request.query,
                        options=request.options,
                        user_id=request.user_id,
                        selected_models=selected_models,
                        stream_config=streaming_config,
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
                    "X-Accel-Buffering": "no",  # Disable proxy buffering
                },
            )

        except HTTPException:
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
