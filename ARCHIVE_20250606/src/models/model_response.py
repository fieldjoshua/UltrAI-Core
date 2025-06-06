"""
ModelResponse Class

This module provides a standardized format for LLM responses.
"""

from datetime import datetime
from typing import Any, Dict, Optional


class ModelResponse:
    """
    Standardized response format for LLM responses.

    This class provides a consistent structure for responses from different LLMs,
    simplifying comparison and analysis.
    """

    def __init__(
        self,
        model_name: str,
        content: Optional[str] = None,
        error: Optional[str] = None,
        stage: str = "initial",
        tokens_used: Optional[int] = None,
        timestamp: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize a ModelResponse object.

        Args:
            model_name: Name of the LLM model
            content: Response content (text)
            error: Error message, if any
            stage: Processing stage (initial, meta, synthesis)
            tokens_used: Number of tokens used
            timestamp: Response timestamp
            metadata: Additional metadata
        """
        self.model_name = model_name
        self.content = content
        self.error = error
        self.stage = stage
        self.tokens_used = tokens_used
        self.timestamp = timestamp or datetime.now().timestamp()
        self.metadata = metadata or {}
        self.processing_time: Optional[float] = None
        self.quality: Optional[float] = None

    @property
    def is_error(self) -> bool:
        """Check if the response is an error."""
        return self.error is not None

    @property
    def is_empty(self) -> bool:
        """Check if the response is empty."""
        return not self.content and not self.error

    def set_processing_time(self, processing_time: float) -> None:
        """Set the processing time for this response."""
        self.processing_time = processing_time

    def set_quality(self, quality: float) -> None:
        """Set the quality score for this response."""
        self.quality = max(0.0, min(quality, 1.0))  # Clamp to 0-1 range

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "model_name": self.model_name,
            "content": self.content,
            "error": self.error,
            "stage": self.stage,
            "tokens_used": self.tokens_used,
            "timestamp": self.timestamp,
            "processing_time": self.processing_time,
            "quality": self.quality,
            "metadata": self.metadata,
        }

    def to_json(self) -> Dict[str, Any]:
        """Alias for to_dict, for JSON serialization."""
        return self.to_dict()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ModelResponse":
        """Create a ModelResponse from a dictionary."""
        response = cls(
            model_name=data.get("model_name", "unknown"),
            content=data.get("content"),
            error=data.get("error"),
            stage=data.get("stage", "initial"),
            tokens_used=data.get("tokens_used"),
            timestamp=data.get("timestamp"),
            metadata=data.get("metadata", {}),
        )

        if "processing_time" in data:
            response.processing_time = data["processing_time"]

        if "quality" in data:
            response.quality = data["quality"]

        return response

    def __str__(self) -> str:
        """String representation of the response."""
        if self.is_error:
            return f"[{self.model_name}] ERROR: {self.error}"
        elif self.content:
            content_preview = (
                (self.content[:77] + "...") if len(self.content) > 80 else self.content
            )
            return f"[{self.model_name}] {content_preview}"
        else:
            return f"[{self.model_name}] Empty response"
