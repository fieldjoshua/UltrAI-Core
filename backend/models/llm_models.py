"""
LLM API Data Models

This module defines data models for LLM API endpoints.
"""

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ModelStatus(str, Enum):
    """Status of an LLM model"""

    READY = "ready"
    THROTTLED = "throttled"
    UNAVAILABLE = "unavailable"
    CIRCUIT_OPEN = "circuit_open"
    NOT_FOUND = "not_found"


class OutputFormat(str, Enum):
    """Output format options for analysis results"""

    PLAIN = "plain"
    MARKDOWN = "markdown"
    JSON = "json"
    HTML = "html"


class AnalysisOption(str, Enum):
    """Optional analysis features that can be enabled"""

    DETAILED = "detailed"
    BULLET_POINTS = "bullet_points"
    EXAMPLES = "examples"
    CITATIONS = "citations"
    SUMMARY = "summary"
    CODE_BLOCKS = "code_blocks"


class ModelCapabilities(BaseModel):
    """Capabilities of an LLM model"""

    max_tokens: int = Field(
        default=4096, description="Maximum tokens the model can process"
    )
    supports_streaming: bool = Field(
        default=False, description="Whether the model supports streaming"
    )
    supports_tools: bool = Field(
        default=False, description="Whether the model supports function/tool calling"
    )
    supports_vision: bool = Field(
        default=False, description="Whether the model supports vision/image input"
    )
    supports_embedding: bool = Field(
        default=False, description="Whether the model supports embeddings"
    )


class ModelInfo(BaseModel):
    """Information about an LLM model"""

    name: str = Field(..., description="Unique identifier for the model")
    provider: str = Field(..., description="Provider name (openai, anthropic, etc.)")
    model: str = Field(..., description="Specific model name")
    weight: float = Field(
        default=1.0, description="Weight for prioritizing model responses"
    )
    capabilities: ModelCapabilities = Field(
        default_factory=ModelCapabilities, description="Model capabilities"
    )
    tags: List[str] = Field(
        default_factory=list, description="Tags for model categorization"
    )
    available: bool = Field(
        default=True, description="Whether the model is currently available"
    )
    status: ModelStatus = Field(
        default=ModelStatus.READY, description="Current model status"
    )


class ModelStatusInfo(BaseModel):
    """Status information for an LLM model"""

    name: str = Field(..., description="Name of the model")
    available: bool = Field(..., description="Whether the model is available")
    status: ModelStatus = Field(..., description="Current model status")
    message: str = Field(default="", description="Status message")
    recovery_time: Optional[float] = Field(
        default=None, description="Expected recovery time in seconds"
    )


class AnalysisMode(BaseModel):
    """Analysis mode configuration"""

    name: str = Field(..., description="Name of the analysis mode")
    pattern: str = Field(..., description="Analysis pattern to use")
    model_selection_strategy: str = Field(
        default="weighted", description="Model selection strategy"
    )
    timeout: Optional[float] = Field(
        default=None, description="Maximum time to wait for responses"
    )
    description: str = Field(default="", description="Human-readable description")


class ProcessPromptRequest(BaseModel):
    """Request to process a prompt with LLMs"""

    prompt: str = Field(..., description="The prompt to process")
    selected_models: List[str] = Field(
        default_factory=list, description="Models to use for processing"
    )
    analysis_mode: str = Field(default="standard", description="Analysis mode to use")
    pattern: Optional[str] = Field(
        default=None, description="Specific pattern to use (overrides analysis_mode)"
    )
    output_format: OutputFormat = Field(
        default=OutputFormat.MARKDOWN, description="Desired output format"
    )
    options: List[AnalysisOption] = Field(
        default_factory=list, description="Analysis options to enable"
    )
    max_tokens: Optional[int] = Field(
        default=None, description="Maximum tokens to generate"
    )
    stream: bool = Field(default=False, description="Whether to stream the response")
    additional_context: Optional[Dict[str, Any]] = Field(
        default=None, description="Additional context for the prompt"
    )


class ModelResponse(BaseModel):
    """Response containing a single model"""

    status: str = Field(default="success", description="Response status")
    model: ModelInfo = Field(..., description="Model information")


class ModelsResponse(BaseModel):
    """Response containing available models"""

    status: str = Field(default="success", description="Response status")
    count: int = Field(..., description="Number of models returned")
    models: List[ModelInfo] = Field(..., description="List of available models")


class ModelStatusResponse(BaseModel):
    """Response containing model status"""

    status: str = Field(default="success", description="Response status")
    model_status: ModelStatusInfo = Field(..., description="Model status information")


class PatternsResponse(BaseModel):
    """Response containing available patterns"""

    status: str = Field(default="success", description="Response status")
    count: int = Field(..., description="Number of patterns returned")
    patterns: List[str] = Field(..., description="List of available patterns")


class AnalysisModesResponse(BaseModel):
    """Response containing available analysis modes"""

    status: str = Field(default="success", description="Response status")
    count: int = Field(..., description="Number of modes returned")
    modes: List[AnalysisMode] = Field(
        ..., description="List of available analysis modes"
    )


class ModelPrediction(BaseModel):
    """Prediction from a single model"""

    model: str = Field(..., description="Model name")
    content: str = Field(..., description="Prediction content")
    tokens_used: int = Field(default=0, description="Number of tokens used")
    processing_time: float = Field(
        default=0.0, description="Processing time in seconds"
    )
    quality_score: Optional[float] = Field(
        default=None, description="Quality score of the prediction"
    )


class PromptResult(BaseModel):
    """Result of processing a prompt"""

    prompt: str = Field(..., description="Original prompt")
    ultra_response: str = Field(..., description="Synthesized response from Ultra")
    model_responses: Dict[str, ModelPrediction] = Field(
        default_factory=dict, description="Individual model predictions"
    )
    total_processing_time: float = Field(
        default=0.0, description="Total processing time in seconds"
    )
    total_tokens: int = Field(default=0, description="Total tokens used")
    pattern_used: str = Field(..., description="Pattern used for analysis")
    analysis_mode: str = Field(..., description="Analysis mode used")


class PromptStreamUpdate(BaseModel):
    """Update for a streaming prompt response"""

    model: str = Field(..., description="Model generating the update")
    content: str = Field(..., description="New content chunk")
    done: bool = Field(default=False, description="Whether this is the final update")
    stage: str = Field(default="initial", description="Current processing stage")
    progress: float = Field(default=0.0, description="Progress percentage (0-100)")


class ErrorResponse(BaseModel):
    """Error response"""

    status: str = Field(default="error", description="Error status")
    message: str = Field(..., description="Error message")
    code: str = Field(default="unknown_error", description="Error code")
    details: Optional[Dict[str, Any]] = Field(
        default=None, description="Additional error details"
    )
