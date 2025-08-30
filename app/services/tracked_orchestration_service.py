"""
Orchestration service with comprehensive request tracking.

This module extends the orchestration service to include request ID tracking
throughout the entire pipeline, making debugging and monitoring much easier.
"""

from typing import Any, Dict, List, Optional
from fastapi import Request

from app.services.orchestration_service import OrchestrationService
from app.services.tracked_llm_adapters import (
    TrackedOpenAIAdapter,
    TrackedAnthropicAdapter,
    TrackedGeminiAdapter,
    TrackedHuggingFaceAdapter,
    TRACKED_CLIENT
)
from app.utils.logging import get_logger

logger = get_logger("tracked_orchestration")


class TrackedOrchestrationService(OrchestrationService):
    """Orchestration service with request tracking capabilities."""
    
    def __init__(self, *args, **kwargs):
        """Initialize tracked orchestration service."""
        super().__init__(*args, **kwargs)
        self._current_request_id = None
        self._current_correlation_id = None
    
    def set_request_context(self, request: Request):
        """
        Set request context from FastAPI request.
        
        Args:
            request: FastAPI request object
        """
        self._current_request_id = getattr(request.state, "request_id", None)
        self._current_correlation_id = getattr(request.state, "correlation_id", None)
        
        # Update tracked client with IDs
        TRACKED_CLIENT.set_tracking_ids(
            self._current_request_id,
            self._current_correlation_id
        )
        
        logger.info(
            "Set orchestration request context",
            extra={
                "request_id": self._current_request_id,
                "correlation_id": self._current_correlation_id
            }
        )
    
    def _create_adapter(self, model: str, prompt_type: str = "generation"):
        """
        Create appropriate adapter with request tracking.
        
        Args:
            model: Model name to create adapter for
            prompt_type: Type of prompt (generation, peer_review)
            
        Returns:
            Tuple of (adapter, mapped_model) or (None, None) if creation fails
        """
        try:
            import os
            
            if model.startswith("gpt") or model.startswith("o1"):
                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key:
                    logger.warning(f"No OpenAI API key found for {model}")
                    return None, None
                
                adapter = TrackedOpenAIAdapter(api_key, model)
                adapter.set_tracking_ids(self._current_request_id, self._current_correlation_id)
                return adapter, model
                
            elif model.startswith("claude"):
                api_key = os.getenv("ANTHROPIC_API_KEY")
                if not api_key:
                    logger.warning(f"No Anthropic API key found for {model}")
                    return None, None
                
                # Fix model name mapping
                mapped_model = model
                if model == "claude-3-sonnet":
                    mapped_model = "claude-3-sonnet-20240229"
                    
                adapter = TrackedAnthropicAdapter(api_key, mapped_model)
                adapter.set_tracking_ids(self._current_request_id, self._current_correlation_id)
                return adapter, mapped_model
                
            elif model.startswith("gemini"):
                api_key = os.getenv("GOOGLE_API_KEY")
                if not api_key:
                    logger.warning(f"No Google API key found for {model}")
                    return None, None
                
                adapter = TrackedGeminiAdapter(api_key, model)
                adapter.set_tracking_ids(self._current_request_id, self._current_correlation_id)
                return adapter, model
                
            elif "/" in model:  # HuggingFace model
                api_key = os.getenv("HUGGINGFACE_API_KEY")
                if not api_key:
                    logger.warning(f"No HuggingFace API key found for {model}")
                    return None, None
                
                adapter = TrackedHuggingFaceAdapter(api_key, model)
                adapter.set_tracking_ids(self._current_request_id, self._current_correlation_id)
                return adapter, model
                
            else:
                logger.warning(f"Unknown model provider for: {model}")
                return None, None
                
        except Exception as e:
            logger.error(
                f"Failed to create tracked adapter for {model}: {e}",
                extra={
                    "request_id": self._current_request_id,
                    "correlation_id": self._current_correlation_id,
                    "model": model,
                    "error": str(e)
                }
            )
            return None, None
    
    async def run_pipeline(
        self,
        input_data: Any,
        options: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        selected_models: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Run pipeline with request tracking.
        
        Args:
            input_data: The input data for analysis
            options: Additional options for the pipeline
            user_id: Optional user ID for cost tracking
            selected_models: Models to use for analysis
            
        Returns:
            Pipeline results
        """
        logger.info(
            "Starting tracked pipeline execution",
            extra={
                "request_id": self._current_request_id,
                "correlation_id": self._current_correlation_id,
                "selected_models": selected_models,
                "user_id": user_id
            }
        )
        
        # Log each stage as we progress
        original_run_stage = self._run_stage
        
        async def tracked_run_stage(stage, input_data, options=None):
            logger.info(
                f"Starting stage: {stage.name}",
                extra={
                    "request_id": self._current_request_id,
                    "correlation_id": self._current_correlation_id,
                    "stage": stage.name,
                    "stage_description": stage.description
                }
            )
            
            result = await original_run_stage(stage, input_data, options)
            
            logger.info(
                f"Completed stage: {stage.name}",
                extra={
                    "request_id": self._current_request_id,
                    "correlation_id": self._current_correlation_id,
                    "stage": stage.name,
                    "success": result.error is None,
                    "error": result.error
                }
            )
            
            return result
        
        # Temporarily replace the run_stage method
        self._run_stage = tracked_run_stage
        
        try:
            # Run the pipeline with tracking
            result = await super().run_pipeline(
                input_data,
                options,
                user_id,
                selected_models
            )
            
            logger.info(
                "Pipeline execution completed",
                extra={
                    "request_id": self._current_request_id,
                    "correlation_id": self._current_correlation_id,
                    "success": True,
                    "stages_completed": len(result)
                }
            )
            
            return result
            
        except Exception as e:
            logger.error(
                "Pipeline execution failed",
                extra={
                    "request_id": self._current_request_id,
                    "correlation_id": self._current_correlation_id,
                    "error": str(e),
                    "error_type": type(e).__name__
                },
                exc_info=e
            )
            raise
        finally:
            # Restore original method
            self._run_stage = original_run_stage