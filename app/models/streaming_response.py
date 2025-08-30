"""
Streaming response models for orchestrator.

This module provides models and utilities for streaming responses from
the orchestration pipeline, enabling real-time updates to clients.
"""

from typing import Optional, Dict, Any, List, Literal
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime


class StreamEventType(str, Enum):
    """Types of events that can be streamed."""
    
    # Pipeline lifecycle events
    PIPELINE_START = "pipeline_start"
    PIPELINE_COMPLETE = "pipeline_complete"
    PIPELINE_ERROR = "pipeline_error"
    
    # Stage events
    STAGE_START = "stage_start"
    STAGE_PROGRESS = "stage_progress"
    STAGE_COMPLETE = "stage_complete"
    STAGE_ERROR = "stage_error"
    
    # Model events
    MODEL_START = "model_start"
    MODEL_RESPONSE = "model_response"
    MODEL_COMPLETE = "model_complete"
    MODEL_ERROR = "model_error"
    
    # Synthesis events
    SYNTHESIS_START = "synthesis_start"
    SYNTHESIS_CHUNK = "synthesis_chunk"
    SYNTHESIS_COMPLETE = "synthesis_complete"


class StreamEvent(BaseModel):
    """Base class for all streaming events."""
    
    event: str = Field(..., description="Type of streaming event")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Event timestamp")
    sequence: int = Field(..., description="Event sequence number")
    data: Dict[str, Any] = Field(..., description="Event-specific data")


class PipelineStartEvent(StreamEvent):
    """Event sent when pipeline starts."""
    
    event: Literal["pipeline_start"] = "pipeline_start"
    data: Dict[str, Any] = Field(
        ...,
        description="Contains: query, selected_models, total_stages, options"
    )


class StageStartEvent(StreamEvent):
    """Event sent when a pipeline stage starts."""
    
    event: Literal["stage_start"] = "stage_start"
    data: Dict[str, Any] = Field(
        ...,
        description="Contains: stage_name, stage_index, total_stages, description"
    )


class ModelResponseEvent(StreamEvent):
    """Event sent when a model generates a response."""
    
    event: Literal["model_response"] = "model_response"
    data: Dict[str, Any] = Field(
        ...,
        description="Contains: model, response_text, tokens_used, response_time"
    )


class SynthesisChunkEvent(StreamEvent):
    """Event sent for streaming synthesis text chunks."""
    
    event: Literal["synthesis_chunk"] = "synthesis_chunk"
    data: Dict[str, Any] = Field(
        ...,
        description="Contains: chunk_text, chunk_index, model_used"
    )


class StreamingAnalysisRequest(BaseModel):
    """Request model for streaming analysis endpoint."""
    
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
    stream_stages: List[str] = Field(
        default=["synthesis_chunks"],
        description="Which stages to stream: all, synthesis_chunks, model_responses"
    )
    chunk_size: int = Field(
        default=50,
        description="Approximate size of synthesis chunks in tokens"
    )


class StreamingConfig(BaseModel):
    """Configuration for streaming behavior."""
    
    enabled: bool = Field(default=True, description="Whether streaming is enabled")
    chunk_size: int = Field(default=50, description="Default chunk size")
    buffer_size: int = Field(default=10, description="Event buffer size")
    heartbeat_interval: int = Field(default=30, description="Heartbeat interval in seconds")
    include_partial_responses: bool = Field(
        default=True,
        description="Include partial model responses as they arrive"
    )
    synthesis_streaming: bool = Field(
        default=True,
        description="Stream synthesis as it's generated"
    )