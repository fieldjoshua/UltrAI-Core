"""
Enhanced LLM adapters with standardized error handling.

This module provides updated versions of all LLM adapters that use
consistent error responses while maintaining backward compatibility.
"""

import httpx
import logging
from typing import Dict, Any, Optional

from app.services.base_llm_adapter import EnhancedBaseAdapter
from app.models.llm_errors import ErrorType
from app.utils.logging import CorrelationContext

logger = logging.getLogger(__name__)


class EnhancedOpenAIAdapter(EnhancedBaseAdapter):
    """Enhanced OpenAI adapter with standardized error handling."""
    
    PROVIDER_NAME = "openai"
    
    async def _handle_http_status_error(self, error: httpx.HTTPStatusError) -> Dict[str, Any]:
        """Handle OpenAI-specific HTTP status errors."""
        status_code = error.response.status_code
        
        if status_code == 401:
            return self._create_error_response(
                error_type=ErrorType.AUTHENTICATION_FAILED,
                error_message="Invalid OpenAI API key",
                status_code=status_code,
                error_code="invalid_api_key"
            )
        
        elif status_code == 404:
            return self._create_error_response(
                error_type=ErrorType.MODEL_NOT_FOUND,
                error_message=f"Model '{self.model}' not found. You may need access to this model.",
                status_code=status_code,
                error_code="model_not_found"
            )
        
        elif status_code == 429:
            retry_after = self._extract_retry_after(error.response)
            return self._create_error_response(
                error_type=ErrorType.RATE_LIMIT_EXCEEDED,
                error_message="OpenAI API rate limit exceeded",
                status_code=status_code,
                error_code="rate_limit_exceeded",
                retry_after=retry_after
            )
        
        elif status_code >= 500:
            return self._create_error_response(
                error_type=ErrorType.SERVER_ERROR,
                error_message=f"OpenAI server error: {error.response.text[:200]}",
                status_code=status_code
            )
        
        else:
            return self._create_error_response(
                error_type=ErrorType.UNKNOWN_ERROR,
                error_message=f"OpenAI API error: HTTP {status_code}",
                status_code=status_code,
                details={"response": error.response.text[:500]}
            )
    
    async def generate(self, prompt: str) -> Dict[str, Any]:
        """Generate response using OpenAI API."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
        }
        
        try:
            request_id = CorrelationContext.get_correlation_id()
            logger.info(
                "OpenAI request",
                extra={"requestId": request_id, "model": self.model},
            )
            
            response = await self.client.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
            
            # Extract token usage if available
            usage = data.get("usage")
            finish_reason = data["choices"][0].get("finish_reason")
            
            return self._create_success_response(
                generated_text=data["choices"][0]["message"]["content"],
                usage=usage,
                finish_reason=finish_reason
            )
            
        except Exception as e:
            # Try common error handling first
            error_response = await self._handle_common_errors(e)
            if error_response:
                return error_response
            
            # Fallback to generic error
            return self._create_error_response(
                error_type=ErrorType.UNKNOWN_ERROR,
                error_message=f"Unexpected error: {str(e)}",
                details={"exception": type(e).__name__}
            )


class EnhancedAnthropicAdapter(EnhancedBaseAdapter):
    """Enhanced Anthropic adapter with standardized error handling."""
    
    PROVIDER_NAME = "anthropic"
    
    async def _handle_http_status_error(self, error: httpx.HTTPStatusError) -> Dict[str, Any]:
        """Handle Anthropic-specific HTTP status errors."""
        status_code = error.response.status_code
        
        if status_code == 401:
            return self._create_error_response(
                error_type=ErrorType.AUTHENTICATION_FAILED,
                error_message="Invalid Anthropic API key",
                status_code=status_code,
                error_code="authentication_error"
            )
        
        elif status_code == 404:
            return self._create_error_response(
                error_type=ErrorType.MODEL_NOT_FOUND,
                error_message=f"Model '{self.model}' not found or invalid endpoint",
                status_code=status_code,
                error_code="not_found_error"
            )
        
        elif status_code == 429:
            retry_after = self._extract_retry_after(error.response)
            return self._create_error_response(
                error_type=ErrorType.RATE_LIMIT_EXCEEDED,
                error_message="Anthropic API rate limit exceeded",
                status_code=status_code,
                error_code="rate_limit_error",
                retry_after=retry_after
            )
        
        elif status_code == 400:
            # Parse error details if available
            try:
                error_data = error.response.json()
                error_message = error_data.get("error", {}).get("message", "Bad request")
            except:
                error_message = "Invalid request to Anthropic API"
            
            return self._create_error_response(
                error_type=ErrorType.INVALID_REQUEST,
                error_message=error_message,
                status_code=status_code,
                error_code="invalid_request_error"
            )
        
        elif status_code >= 500:
            return self._create_error_response(
                error_type=ErrorType.SERVER_ERROR,
                error_message=f"Anthropic server error",
                status_code=status_code,
                error_code="api_error"
            )
        
        else:
            return self._create_error_response(
                error_type=ErrorType.UNKNOWN_ERROR,
                error_message=f"Anthropic API error: HTTP {status_code}",
                status_code=status_code
            )
    
    async def generate(self, prompt: str) -> Dict[str, Any]:
        """Generate response using Anthropic API."""
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "max_tokens": 4096,
            "messages": [{"role": "user", "content": prompt}],
        }
        
        try:
            logger.info(
                "Anthropic request",
                extra={"requestId": CorrelationContext.get_correlation_id(), "model": self.model},
            )
            
            response = await self.client.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            
            # Extract usage information
            usage = data.get("usage")
            stop_reason = data.get("stop_reason")
            
            return self._create_success_response(
                generated_text=data["content"][0]["text"],
                usage=usage,
                finish_reason=stop_reason
            )
            
        except Exception as e:
            error_response = await self._handle_common_errors(e)
            if error_response:
                return error_response
            
            return self._create_error_response(
                error_type=ErrorType.UNKNOWN_ERROR,
                error_message=f"Unexpected error: {str(e)}",
                details={"exception": type(e).__name__}
            )


class EnhancedGeminiAdapter(EnhancedBaseAdapter):
    """Enhanced Google Gemini adapter with standardized error handling."""
    
    PROVIDER_NAME = "google"
    
    async def _handle_http_status_error(self, error: httpx.HTTPStatusError) -> Dict[str, Any]:
        """Handle Gemini-specific HTTP status errors."""
        status_code = error.response.status_code
        
        if status_code == 401 or status_code == 403:
            return self._create_error_response(
                error_type=ErrorType.AUTHENTICATION_FAILED,
                error_message="Invalid Google API key or insufficient permissions",
                status_code=status_code,
                error_code="UNAUTHENTICATED"
            )
        
        elif status_code == 404:
            return self._create_error_response(
                error_type=ErrorType.MODEL_NOT_FOUND,
                error_message=f"Model '{self.model}' not found",
                status_code=status_code,
                error_code="NOT_FOUND"
            )
        
        elif status_code == 429:
            retry_after = self._extract_retry_after(error.response)
            return self._create_error_response(
                error_type=ErrorType.QUOTA_EXCEEDED,
                error_message="Google API quota exceeded",
                status_code=status_code,
                error_code="RESOURCE_EXHAUSTED",
                retry_after=retry_after
            )
        
        elif status_code == 400:
            # Try to extract specific error from response
            try:
                error_data = error.response.json()
                error_message = error_data.get("error", {}).get("message", "Invalid request")
            except:
                error_message = "Invalid request to Gemini API"
            
            return self._create_error_response(
                error_type=ErrorType.INVALID_REQUEST,
                error_message=error_message,
                status_code=status_code,
                error_code="INVALID_ARGUMENT"
            )
        
        elif status_code >= 500:
            return self._create_error_response(
                error_type=ErrorType.SERVER_ERROR,
                error_message="Google server error",
                status_code=status_code,
                error_code="INTERNAL"
            )
        
        else:
            return self._create_error_response(
                error_type=ErrorType.UNKNOWN_ERROR,
                error_message=f"Gemini API error: HTTP {status_code}",
                status_code=status_code
            )
    
    async def generate(self, prompt: str) -> Dict[str, Any]:
        """Generate response using Google Gemini API."""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": self.api_key
        }
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        
        try:
            logger.info(
                "Google Gemini request",
                extra={"requestId": CorrelationContext.get_correlation_id(), "model": self.model},
            )
            
            response = await self.client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            
            # Extract the generated text
            generated_text = data["candidates"][0]["content"]["parts"][0]["text"]
            
            # Extract usage metadata if available
            usage_metadata = data.get("usageMetadata")
            finish_reason = data["candidates"][0].get("finishReason")
            
            return self._create_success_response(
                generated_text=generated_text,
                usage=usage_metadata,
                finish_reason=finish_reason
            )
            
        except Exception as e:
            error_response = await self._handle_common_errors(e)
            if error_response:
                return error_response
            
            return self._create_error_response(
                error_type=ErrorType.UNKNOWN_ERROR,
                error_message=f"Unexpected error: {str(e)}",
                details={"exception": type(e).__name__}
            )


class EnhancedHuggingFaceAdapter(EnhancedBaseAdapter):
    """Enhanced HuggingFace adapter with standardized error handling."""
    
    PROVIDER_NAME = "huggingface"
    
    def __init__(self, api_key: str, model: str, client: httpx.AsyncClient):
        super().__init__(api_key, model, client)
        self.model_id = model  # HuggingFace uses model ID format
    
    async def _handle_http_status_error(self, error: httpx.HTTPStatusError) -> Dict[str, Any]:
        """Handle HuggingFace-specific HTTP status errors."""
        status_code = error.response.status_code
        
        if status_code == 401:
            return self._create_error_response(
                error_type=ErrorType.AUTHENTICATION_FAILED,
                error_message="Invalid HuggingFace API token",
                status_code=status_code,
                error_code="invalid_token"
            )
        
        elif status_code == 404:
            return self._create_error_response(
                error_type=ErrorType.MODEL_NOT_FOUND,
                error_message=f"Model '{self.model_id}' not found on HuggingFace",
                status_code=status_code,
                error_code="model_not_found"
            )
        
        elif status_code == 429:
            retry_after = self._extract_retry_after(error.response)
            return self._create_error_response(
                error_type=ErrorType.RATE_LIMIT_EXCEEDED,
                error_message="HuggingFace API rate limit exceeded",
                status_code=status_code,
                error_code="too_many_requests",
                retry_after=retry_after
            )
        
        elif status_code == 503:
            # Model loading is a common 503 case for HuggingFace
            try:
                error_data = error.response.json()
                estimated_time = error_data.get("estimated_time", 30)
            except:
                estimated_time = 30
            
            return self._create_error_response(
                error_type=ErrorType.MODEL_LOADING,
                error_message=f"Model is loading, please retry in {estimated_time} seconds",
                status_code=status_code,
                error_code="model_loading",
                retry_after=int(estimated_time)
            )
        
        elif status_code >= 500:
            return self._create_error_response(
                error_type=ErrorType.SERVER_ERROR,
                error_message="HuggingFace server error",
                status_code=status_code
            )
        
        else:
            return self._create_error_response(
                error_type=ErrorType.UNKNOWN_ERROR,
                error_message=f"HuggingFace API error: HTTP {status_code}",
                status_code=status_code
            )
    
    async def generate(self, prompt: str) -> Dict[str, Any]:
        """Generate response using HuggingFace Inference API."""
        url = f"https://api-inference.huggingface.co/models/{self.model_id}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        # Different payload format for different model types
        if "llama" in self.model_id.lower() or "mistral" in self.model_id.lower():
            # Chat models
            payload = {
                "inputs": f"<s>[INST] {prompt} [/INST]",
                "parameters": {
                    "max_new_tokens": 1000,
                    "temperature": 0.7,
                    "do_sample": True,
                    "return_full_text": False,
                },
            }
        else:
            # Text generation models
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": 1000,
                    "temperature": 0.7,
                    "do_sample": True,
                    "return_full_text": False,
                },
            }
        
        try:
            response = await self.client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            
            # Handle different response formats
            generated_text = None
            if isinstance(data, list) and len(data) > 0:
                if isinstance(data[0], dict) and "generated_text" in data[0]:
                    generated_text = data[0]["generated_text"]
                elif isinstance(data[0], str):
                    generated_text = data[0]
            elif isinstance(data, dict) and "generated_text" in data:
                generated_text = data["generated_text"]
            
            if generated_text is None:
                generated_text = str(data)
            
            return self._create_success_response(generated_text=generated_text)
            
        except Exception as e:
            error_response = await self._handle_common_errors(e)
            if error_response:
                return error_response
            
            return self._create_error_response(
                error_type=ErrorType.UNKNOWN_ERROR,
                error_message=f"Unexpected error: {str(e)}",
                details={"exception": type(e).__name__}
            )