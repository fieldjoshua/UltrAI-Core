"""
Standardized error response models for LLM adapters.

This module provides consistent error structures across all LLM providers,
improving debugging and error handling throughout the orchestration pipeline.
"""

from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class ErrorType(str, Enum):
    """Standardized error types for LLM operations."""
    
    # Authentication and authorization
    AUTHENTICATION_FAILED = "authentication_failed"
    INVALID_API_KEY = "invalid_api_key"
    
    # Rate limiting
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    QUOTA_EXCEEDED = "quota_exceeded"
    
    # Model issues
    MODEL_NOT_FOUND = "model_not_found"
    MODEL_LOADING = "model_loading"
    
    # Request issues
    INVALID_REQUEST = "invalid_request"
    TIMEOUT = "timeout"
    
    # Network and server issues
    NETWORK_ERROR = "network_error"
    SERVER_ERROR = "server_error"
    
    # General errors
    UNKNOWN_ERROR = "unknown_error"


class LLMErrorResponse(BaseModel):
    """Standardized error response for all LLM adapters."""
    
    error: bool = Field(default=True, description="Indicates this is an error response")
    error_type: ErrorType = Field(..., description="Categorized error type")
    error_code: Optional[str] = Field(default=None, description="Provider-specific error code")
    error_message: str = Field(..., description="Human-readable error message")
    provider: str = Field(..., description="LLM provider name (openai, anthropic, google, huggingface)")
    model: str = Field(..., description="Model that was attempted")
    status_code: Optional[int] = Field(default=None, description="HTTP status code if applicable")
    retry_after: Optional[int] = Field(default=None, description="Seconds to wait before retry (for rate limits)")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Additional provider-specific details")
    
    def to_legacy_format(self) -> Dict[str, Any]:
        """Convert to legacy format for backward compatibility."""
        # Map to the current format expected by orchestration_service.py
        error_prefix = "Error: "
        
        if self.error_type == ErrorType.AUTHENTICATION_FAILED:
            text = f"{error_prefix}{self.provider.title()} API authentication failed. Check API key."
        elif self.error_type == ErrorType.RATE_LIMIT_EXCEEDED:
            text = f"{error_prefix}{self.provider.title()} API rate limit exceeded. Please retry later."
        elif self.error_type == ErrorType.MODEL_NOT_FOUND:
            text = f"{error_prefix}Model {self.model} not found in {self.provider.title()} API"
        elif self.error_type == ErrorType.TIMEOUT:
            text = f"{error_prefix}{self.provider.title()} request timed out."
        elif self.error_type == ErrorType.MODEL_LOADING:
            text = "Model is loading on HuggingFace. Please try again in 30 seconds."
        else:
            text = f"{error_prefix}{self.error_message}"
        
        return {
            "generated_text": text,
            "error": self.error_message,
            "error_details": self.error_message,
            "provider": self.provider
        }


class LLMSuccessResponse(BaseModel):
    """Standardized success response for all LLM adapters."""
    
    generated_text: str = Field(..., description="Generated text from the model")
    model: str = Field(..., description="Model that generated the response")
    provider: str = Field(..., description="LLM provider name")
    usage: Optional[Dict[str, int]] = Field(default=None, description="Token usage information")
    finish_reason: Optional[str] = Field(default=None, description="Reason for completion")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")