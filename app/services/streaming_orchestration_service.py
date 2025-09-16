"""
Streaming orchestration service for real-time pipeline updates.

This module extends the base orchestration service to support streaming
responses, enabling clients to receive real-time updates as the pipeline
processes through its stages.
"""

import asyncio
import json
from typing import AsyncGenerator, Dict, Any, List, Optional

from app.services.orchestration_service import OrchestrationService
from app.models.streaming_response import (
    StreamEvent,
    StreamEventType,
    PipelineStartEvent,
    ModelResponseEvent,
    SynthesisChunkEvent,
    StreamingConfig
)
from app.utils.logging import get_logger

logger = get_logger("streaming_orchestration")


class StreamingOrchestrationService(OrchestrationService):
    """Extended orchestration service with streaming support."""

    def __init__(self, *args, **kwargs):
        """Initialize streaming orchestration service."""
        super().__init__(*args, **kwargs)
        self.streaming_config = StreamingConfig()
        self._event_sequence = 0

    def _next_sequence(self) -> int:
        """Get next event sequence number."""
        self._event_sequence += 1
        return self._event_sequence

    def _create_event(
        self,
        event_type: str,
        data: Dict[str, Any]
    ) -> StreamEvent:
        """Create a streaming event."""
        return StreamEvent(
            event=event_type,
            sequence=self._next_sequence(),
            data=data
        )

    async def stream_pipeline(
        self,
        input_data: Any,
        options: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        selected_models: Optional[List[str]] = None,
        stream_config: Optional[StreamingConfig] = None
    ) -> AsyncGenerator[str, None]:
        """
        Run pipeline with streaming events.

        Yields:
            Server-Sent Event formatted strings
        """
        self._event_sequence = 0  # Reset sequence for new stream

        # Send pipeline start event
        start_event = PipelineStartEvent(
            sequence=self._next_sequence(),
            data={
                "query": str(input_data)[:200],
                "selected_models": selected_models or [],
                "total_stages": len(self.pipeline_stages),
                "options": options or {}
            }
        )
        yield self._format_sse(start_event)

        # Default model selection if needed
        if not selected_models:
            selected_models = await self._default_models_from_env()

        # Enforce minimum required models for streaming pipeline
        from app.config import Config as _Cfg
        # Check providers
        try:
            from app.services.provider_health_manager import provider_health_manager
            health_summary = await provider_health_manager.get_health_summary()
            available_providers = health_summary["_system"]["available_providers"]
        except Exception:
            available_providers = []

        required_providers = getattr(_Cfg, "REQUIRED_PROVIDERS", ["openai", "anthropic", "google"])
        missing_providers = [p for p in required_providers if p not in available_providers]

        if (not selected_models) or (len(selected_models) < _Cfg.MINIMUM_MODELS_REQUIRED) or missing_providers:
            error_text = (
                "Service requires at least "
                f"{_Cfg.MINIMUM_MODELS_REQUIRED} models and providers: "
                f"{sorted(required_providers)}; "
                f"{len(selected_models or [])} models provided; "
                f"missing providers: {sorted(missing_providers)}"
            )
            error_event = self._create_event(
                StreamEventType.PIPELINE_ERROR.value,
                {
                    "error": error_text,
                    "models_provided": selected_models or [],
                    "required_providers": required_providers,
                    "missing_providers": missing_providers
                }
            )
            yield self._format_sse(error_event)
            return

        selected_models = self._validate_model_names(selected_models)
        if not selected_models:
            error_event = self._create_event(
                StreamEventType.PIPELINE_ERROR.value,
                {"error": "No valid models provided after validation"}
            )
            yield self._format_sse(error_event)
            return

    async def _stream_initial_response(
        self,
        prompt: str,
        models: List[str],
        options: Optional[Dict[str, Any]] = None
    ) -> AsyncGenerator[StreamEvent, None]:
        """Stream initial response generation from multiple models."""
        # Create tasks for concurrent model execution
        async def execute_and_stream(model: str):
            """Execute model and return result."""
            try:
                # Send model start event
                _ = self._create_event(
                    StreamEventType.MODEL_START.value,
                    {"model": model, "stage": "initial_response"}
                )

                # Execute model
                result = await self._execute_model_with_retry(model, prompt)

                if "generated_text" in result:
                    # Send model response event
                    response_event = ModelResponseEvent(
                        sequence=self._next_sequence(),
                        data={
                            "model": model,
                            "response_text": result["generated_text"],
                            "tokens_used": result.get("usage", {}),
                            "response_time": 0
                        }
                    )
                    return (model, result, response_event)
                else:
                    # Send model error event
                    error_event = self._create_event(
                        StreamEventType.MODEL_ERROR.value,
                        {
                            "model": model,
                            "error": result.get("error", "Unknown error")
                        }
                    )
                    return (model, result, error_event)

            except Exception as e:
                error_event = self._create_event(
                    StreamEventType.MODEL_ERROR.value,
                    {"model": model, "error": str(e)}
                )
                return (model, {"error": str(e)}, error_event)

    async def _stream_ultra_synthesis(
        self,
        data: Dict[str, Any],
        models: List[str],
        options: Optional[Dict[str, Any]],
        config: StreamingConfig
    ) -> AsyncGenerator[StreamEvent, None]:
        """Stream ultra synthesis generation."""
        # Send synthesis start event
        yield self._create_event(
            StreamEventType.SYNTHESIS_START.value,
            {"models_available": models}
        )

        # Prepare synthesis (same as regular ultra_synthesis)
        if "revised_responses" in data and data["revised_responses"]:
            responses_to_synthesize = data["revised_responses"]
        elif "responses" in data and data["responses"]:
            responses_to_synthesize = data["responses"]
        else:
            yield self._create_event(
                StreamEventType.STAGE_ERROR.value,
                {"error": "No responses available for synthesis"}
            )
            return

        # Get original prompt
        original_prompt = self._extract_original_prompt(data)

        # Create synthesis prompt
        meta_analysis = self._format_responses_for_synthesis(responses_to_synthesize)
        synthesis_prompt = self._create_synthesis_prompt(original_prompt, meta_analysis)

        # Select best model for synthesis
        synthesis_model = self._select_synthesis_model(models, responses_to_synthesize)

        # For now, generate full synthesis then chunk it
        # TODO: Implement true streaming from LLM adapters
        result = await self._execute_model_with_retry(synthesis_model, synthesis_prompt)

        if "generated_text" in result:
            synthesis_text = result["generated_text"]

            # Chunk the synthesis text
            chunks = self._chunk_text(synthesis_text, config.chunk_size)

            # Stream chunks
            for i, chunk in enumerate(chunks):
                chunk_event = SynthesisChunkEvent(
                    sequence=self._next_sequence(),
                    data={
                        "chunk_text": chunk,
                        "chunk_index": i,
                        "model_used": synthesis_model,
                        "total_chunks": len(chunks)
                    }
                )
                yield chunk_event

                # Small delay between chunks for demonstration
                await asyncio.sleep(0.05)

            # Send synthesis complete
            yield self._create_event(
                StreamEventType.SYNTHESIS_COMPLETE.value,
                {
                    "model_used": synthesis_model,
                    "total_length": len(synthesis_text)
                }
            )
        else:
            # Send error
            yield self._create_event(
                StreamEventType.STAGE_ERROR.value,
                {"error": result.get("error", "Synthesis generation failed")}
            )

    def _format_sse(self, event: StreamEvent) -> str:
        """Format event as Server-Sent Event."""
        data = {
            "event": event.event,
            "sequence": event.sequence,
            "timestamp": event.timestamp.isoformat(),
            "data": event.data
        }
        return f"data: {json.dumps(data)}\n\n"

    def _count_successful_models(self, data: Dict[str, Any]) -> int:
        """Count successful models from previous stage."""
        if isinstance(data, dict):
            if "successful_models" in data:
                return len(data["successful_models"])
            if "responses" in data:
                return len(data["responses"])
        return 0

    def _extract_original_prompt(self, data: Dict[str, Any]) -> str:
        """Extract original prompt from pipeline data."""
        if isinstance(data, dict):
            if "prompt" in data:
                return data["prompt"]
            if "input_data" in data and isinstance(data["input_data"], dict):
                return data["input_data"].get("prompt", "Unknown prompt")
        return "Unknown prompt"

    def _format_responses_for_synthesis(self, responses: Dict[str, str]) -> str:
        """Format model responses for synthesis prompt."""
        formatted = []
        for model, response in responses.items():
            formatted.append(f"**{model}:** {response}")
        return "\n\n".join(formatted)

    def _create_synthesis_prompt(self, original_prompt: str, responses: str) -> str:
        """Create synthesis prompt."""
        preface = (
            "Given the user's initial query, please review the revised drafts from all LLMs. "
            "Keep commentary to a minimum unless it helps with the original inquiry. "
            "Do not reference the process, but produce the best, most thorough answer to the original query.\n\n"
        )
        body = (
            f"ORIGINAL QUERY: {original_prompt}\n\n"
            "REVISED LLM DRAFTS:\n"
            f"{responses}\n\n"
        )
        tail = (
            "Create a comprehensive Ultra Synthesis\u2122 document that directly answers the "
            "original query with maximum thoroughness."
        )
        return preface + body + tail

    def _select_synthesis_model(
        self,
        available_models: List[str],
        successful_responses: Dict[str, str]
    ) -> str:
        """Select best model for synthesis."""
        # Prefer models that succeeded in previous stages
        for model in successful_responses.keys():
            if model in available_models:
                return model

        # Fallback to first available or default
        return available_models[0] if available_models else "claude-3-5-sonnet-20241022"

    def _chunk_text(self, text: str, chunk_size: int) -> List[str]:
        """Split text into chunks for streaming."""
        words = text.split()
        chunks = []
        current_chunk = []

        for word in words:
            current_chunk.append(word)
            if len(current_chunk) >= chunk_size:
                chunks.append(" ".join(current_chunk))
                current_chunk = []

        if current_chunk:
            chunks.append(" ".join(current_chunk))

        return chunks
