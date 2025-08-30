"""
LLM adapters with request ID tracking support.

This module provides a wrapper for LLM adapters that automatically includes
request tracking headers in all outgoing API calls.
"""

import httpx
from typing import Dict, Any, Optional

from app.services.llm_adapters import (
    OpenAIAdapter,
    AnthropicAdapter,
    GeminiAdapter,
    HuggingFaceAdapter
)
from app.middleware.request_tracking_middleware import RequestIDInjector
from app.utils.logging import CorrelationContext, get_logger

logger = get_logger("tracked_llm_adapters")


class TrackedLLMAdapter:
    """Base wrapper for LLM adapters with request tracking."""
    
    def __init__(self, adapter):
        """
        Initialize tracked adapter.
        
        Args:
            adapter: The underlying LLM adapter
        """
        self.adapter = adapter
        self._request_id = None
        self._correlation_id = None
    
    def set_tracking_ids(self, request_id: Optional[str] = None, correlation_id: Optional[str] = None):
        """
        Set tracking IDs for this adapter instance.
        
        Args:
            request_id: Request ID to use
            correlation_id: Correlation ID to use
        """
        self._request_id = request_id
        self._correlation_id = correlation_id or CorrelationContext.get_correlation_id()
    
    async def generate(self, prompt: str) -> Dict[str, Any]:
        """
        Generate response with request tracking.
        
        Args:
            prompt: The prompt to send
            
        Returns:
            Response from the LLM
        """
        # Log the outgoing request
        logger.info(
            f"Sending request to {self.adapter.__class__.__name__}",
            extra={
                "request_id": self._request_id,
                "correlation_id": self._correlation_id,
                "model": self.adapter.model,
                "prompt_length": len(prompt)
            }
        )
        
        # Call the underlying adapter
        result = await self.adapter.generate(prompt)
        
        # Log the response
        if "generated_text" in result:
            logger.info(
                f"Received response from {self.adapter.__class__.__name__}",
                extra={
                    "request_id": self._request_id,
                    "correlation_id": self._correlation_id,
                    "model": self.adapter.model,
                    "response_length": len(result["generated_text"]),
                    "success": True
                }
            )
        else:
            logger.warning(
                f"Error response from {self.adapter.__class__.__name__}",
                extra={
                    "request_id": self._request_id,
                    "correlation_id": self._correlation_id,
                    "model": self.adapter.model,
                    "error": result.get("error", "Unknown error"),
                    "success": False
                }
            )
        
        return result


class TrackedHTTPClient(httpx.AsyncClient):
    """HTTP client that automatically includes tracking headers."""
    
    def __init__(self, *args, **kwargs):
        """Initialize tracked HTTP client."""
        super().__init__(*args, **kwargs)
        self._request_id = None
        self._correlation_id = None
    
    def set_tracking_ids(self, request_id: Optional[str] = None, correlation_id: Optional[str] = None):
        """Set tracking IDs for all requests from this client."""
        self._request_id = request_id
        self._correlation_id = correlation_id or CorrelationContext.get_correlation_id()
    
    async def request(self, method, url, **kwargs):
        """Make HTTP request with tracking headers."""
        # Inject tracking headers
        headers = kwargs.get("headers", {})
        headers = RequestIDInjector.inject_headers(
            headers,
            self._request_id,
            self._correlation_id
        )
        kwargs["headers"] = headers
        
        # Log outgoing request
        logger.debug(
            f"Outgoing HTTP {method} request",
            extra={
                "method": method,
                "url": str(url),
                "request_id": self._request_id,
                "correlation_id": self._correlation_id
            }
        )
        
        return await super().request(method, url, **kwargs)


# Create a tracked version of the shared client
TRACKED_CLIENT = TrackedHTTPClient(timeout=45.0)


class TrackedOpenAIAdapter(TrackedLLMAdapter):
    """OpenAI adapter with request tracking."""
    
    def __init__(self, api_key: str, model: str):
        # Create adapter with tracked client
        adapter = OpenAIAdapter(api_key, model)
        adapter.CLIENT = TRACKED_CLIENT
        super().__init__(adapter)


class TrackedAnthropicAdapter(TrackedLLMAdapter):
    """Anthropic adapter with request tracking."""
    
    def __init__(self, api_key: str, model: str):
        adapter = AnthropicAdapter(api_key, model)
        adapter.CLIENT = TRACKED_CLIENT
        super().__init__(adapter)


class TrackedGeminiAdapter(TrackedLLMAdapter):
    """Gemini adapter with request tracking."""
    
    def __init__(self, api_key: str, model: str):
        adapter = GeminiAdapter(api_key, model)
        adapter.CLIENT = TRACKED_CLIENT
        super().__init__(adapter)


class TrackedHuggingFaceAdapter(TrackedLLMAdapter):
    """HuggingFace adapter with request tracking."""
    
    def __init__(self, api_key: str, model: str):
        adapter = HuggingFaceAdapter(api_key, model)
        adapter.CLIENT = TRACKED_CLIENT
        super().__init__(adapter)