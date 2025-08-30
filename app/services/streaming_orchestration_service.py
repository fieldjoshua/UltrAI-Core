"""
Streaming orchestration service for real-time pipeline updates.

This module extends the base orchestration service to support streaming
responses, enabling clients to receive real-time updates as the pipeline
processes through its stages.
"""

import asyncio
import json
from typing import AsyncGenerator, Dict, Any, List, Optional
from datetime import datetime

from app.services.orchestration_service import OrchestrationService
from app.models.streaming_response import (
    StreamEvent,
    StreamEventType,
    PipelineStartEvent,
    StageStartEvent,
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
        config = stream_config or self.streaming_config
        self._event_sequence = 0  # Reset sequence for new stream
        
        # Send pipeline start event
        start_event = PipelineStartEvent(
            sequence=self._next_sequence(),
            data={
                "query": str(input_data)[:200],  # Truncate for event
                "selected_models": selected_models or [],
                "total_stages": len(self.pipeline_stages),
                "options": options or {}
            }
        )
        yield self._format_sse(start_event)
        
        # Default model selection if needed
        if not selected_models:
            selected_models = await self._default_models_from_env()
        
        selected_models = self._validate_model_names(selected_models)
        if not selected_models:
            error_event = self._create_event(
                StreamEventType.PIPELINE_ERROR.value,
                {"error": "No valid models provided after validation"}
            )
            yield self._format_sse(error_event)
            return
        
        current_data = input_data
        
        # Process each stage with streaming
        for i, stage in enumerate(self.pipeline_stages):
            # Send stage start event
            stage_event = StageStartEvent(
                sequence=self._next_sequence(),
                data={
                    "stage_name": stage.name,
                    "stage_index": i,
                    "total_stages": len(self.pipeline_stages),
                    "description": stage.description
                }
            )
            yield self._format_sse(stage_event)
            
            try:
                # Handle stage based on type
                if stage.name == "initial_response":
                    async for event in self._stream_initial_response(
                        current_data, selected_models, options
                    ):
                        yield self._format_sse(event)
                        
                elif stage.name == "peer_review_and_revision":
                    # Check if we should skip
                    model_count = self._count_successful_models(current_data)
                    if model_count < 2:
                        skip_event = self._create_event(
                            StreamEventType.STAGE_COMPLETE.value,
                            {
                                "stage_name": stage.name,
                                "skipped": True,
                                "reason": "Fewer than two working models"
                            }
                        )
                        yield self._format_sse(skip_event)
                        continue
                    
                    # Stream peer review
                    stage_result = await self.peer_review_and_revision(
                        current_data, selected_models, options
                    )
                    current_data = stage_result
                    
                elif stage.name == "ultra_synthesis":
                    # Stream synthesis with chunks if enabled
                    if config.synthesis_streaming:
                        async for event in self._stream_ultra_synthesis(
                            current_data, selected_models, options, config
                        ):
                            yield self._format_sse(event)
                    else:
                        # Non-streaming synthesis
                        stage_result = await self.ultra_synthesis(
                            current_data, selected_models, options
                        )
                        current_data = stage_result
                
                # Send stage complete event
                complete_event = self._create_event(
                    StreamEventType.STAGE_COMPLETE.value,
                    {
                        "stage_name": stage.name,
                        "stage_index": i,
                        "success": True
                    }
                )
                yield self._format_sse(complete_event)
                
            except Exception as e:
                # Send stage error event
                error_event = self._create_event(
                    StreamEventType.STAGE_ERROR.value,
                    {
                        "stage_name": stage.name,
                        "stage_index": i,
                        "error": str(e)
                    }
                )
                yield self._format_sse(error_event)
                break
        
        # Send pipeline complete event
        complete_event = self._create_event(
            StreamEventType.PIPELINE_COMPLETE.value,
            {
                "total_stages": len(self.pipeline_stages),
                "success": True
            }
        )
        yield self._format_sse(complete_event)
    
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
                start_event = self._create_event(
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
                            "response_time": 0  # TODO: Track actual time
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
        
        # Execute models concurrently
        tasks = [execute_and_stream(model) for model in models]
        responses = {}
        
        # Process results as they complete
        for coro in asyncio.as_completed(tasks):
            model, result, event = await coro
            yield event
            
            if "generated_text" in result:
                responses[model] = result["generated_text"]
        
        # Return aggregated responses through stage complete
        self._last_initial_responses = {
            "stage": "initial_response",
            "responses": responses,
            "prompt": prompt,
            "successful_models": list(responses.keys())
        }
    
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
        return f"""Given the user's initial query, please review the revised drafts from all LLMs. Keep commentary to a minimum unless it helps with the original inquiry. Do not reference the process, but produce the best, most thorough answer to the original query.

ORIGINAL QUERY: {original_prompt}

REVISED LLM DRAFTS:
{responses}

Create a comprehensive Ultra Synthesis™ document that directly answers the original query with maximum thoroughness."""
    
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