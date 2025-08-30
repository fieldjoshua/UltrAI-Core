"""
Enhanced base adapter with standardized error handling for all LLM providers.

This module provides a base class that all LLM adapters should inherit from,
ensuring consistent error handling and response formats across providers.
"""

import httpx
import logging
from typing import Dict, Any, Optional, Union
from abc import ABC, abstractmethod

from app.models.llm_errors import LLMErrorResponse, LLMSuccessResponse, ErrorType
from app.utils.logging import CorrelationContext

logger = logging.getLogger(__name__)


class EnhancedBaseAdapter(ABC):
    """Enhanced base adapter with standardized error handling."""
    
    # Provider name should be set by each adapter
    PROVIDER_NAME: str = "unknown"
    
    def __init__(self, api_key: str, model: str, client: httpx.AsyncClient):
        """Initialize adapter with API key, model, and shared HTTP client."""
        if not api_key:
            raise ValueError(f"API key for {self.PROVIDER_NAME} is missing.")
        self.api_key = api_key
        self.model = model
        self.client = client
    
    def _mask_api_key(self, api_key: str) -> str:
        """Mask API key for secure logging."""
        if len(api_key) <= 8:
            return "***"
        return f"{api_key[:4]}***{api_key[-4:]}"
    
    def _create_error_response(
        self,
        error_type: ErrorType,
        error_message: str,
        status_code: Optional[int] = None,
        error_code: Optional[str] = None,
        retry_after: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a standardized error response."""
        error_response = LLMErrorResponse(
            error_type=error_type,
            error_code=error_code,
            error_message=error_message,
            provider=self.PROVIDER_NAME,
            model=self.model,
            status_code=status_code,
            retry_after=retry_after,
            details=details
        )
        
        # Log the error with correlation ID
        request_id = CorrelationContext.get_correlation_id()
        logger.error(
            f"{self.PROVIDER_NAME} error: {error_type.value} - {error_message}",
            extra={
                "requestId": request_id,
                "model": self.model,
                "error_type": error_type.value,
                "status_code": status_code
            }
        )
        
        # Return legacy format for backward compatibility
        return error_response.to_legacy_format()
    
    def _create_success_response(
        self,
        generated_text: str,
        usage: Optional[Dict[str, int]] = None,
        finish_reason: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a standardized success response."""
        success_response = LLMSuccessResponse(
            generated_text=generated_text,
            model=self.model,
            provider=self.PROVIDER_NAME,
            usage=usage,
            finish_reason=finish_reason,
            metadata=metadata
        )
        
        # For now, return legacy format for compatibility
        return {"generated_text": generated_text}
    
    async def _handle_common_errors(self, error: Exception) -> Optional[Dict[str, Any]]:
        """Handle common errors across all providers."""
        if isinstance(error, httpx.ReadTimeout):
            return self._create_error_response(
                error_type=ErrorType.TIMEOUT,
                error_message=f"{self.PROVIDER_NAME} request timed out after 45 seconds",
                details={"timeout": 45}
            )
        
        elif isinstance(error, httpx.NetworkError):
            return self._create_error_response(
                error_type=ErrorType.NETWORK_ERROR,
                error_message=f"Network error connecting to {self.PROVIDER_NAME} API",
                details={"error": str(error)}
            )
        
        elif isinstance(error, httpx.HTTPStatusError):
            return await self._handle_http_status_error(error)
        
        # Return None to indicate the error should be handled by the specific adapter
        return None
    
    @abstractmethod
    async def _handle_http_status_error(self, error: httpx.HTTPStatusError) -> Dict[str, Any]:
        """Handle HTTP status errors - must be implemented by each adapter."""
        pass
    
    @abstractmethod
    async def generate(self, prompt: str) -> Dict[str, Any]:
        """Generate a response - must be implemented by each adapter."""
        pass
    
    def _extract_retry_after(self, response: httpx.Response) -> Optional[int]:
        """Extract retry-after value from response headers."""
        retry_after = response.headers.get("retry-after")
        if retry_after:
            try:
                return int(retry_after)
            except ValueError:
                pass
        
        # Check for common rate limit headers
        remaining = response.headers.get("x-ratelimit-remaining")
        reset = response.headers.get("x-ratelimit-reset")
        
        if remaining == "0" and reset:
            try:
                import time
                reset_time = int(reset)
                current_time = int(time.time())
                return max(reset_time - current_time, 1)
            except ValueError:
                pass
        
        return None