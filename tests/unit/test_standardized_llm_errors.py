"""
Unit tests for standardized LLM error responses.

This module tests the enhanced LLM adapters to ensure they produce
consistent error responses across all providers.
"""

import pytest
import httpx
from unittest.mock import AsyncMock, Mock, patch

from app.models.llm_errors import ErrorType, LLMErrorResponse
from app.services.enhanced_llm_adapters import (
    EnhancedOpenAIAdapter,
    EnhancedAnthropicAdapter,
    EnhancedGeminiAdapter,
    EnhancedHuggingFaceAdapter
)


@pytest.fixture
def mock_client():
    """Create a mock HTTP client."""
    client = AsyncMock(spec=httpx.AsyncClient)
    return client


@pytest.fixture
def openai_adapter(mock_client):
    """Create an OpenAI adapter with mock client."""
    return EnhancedOpenAIAdapter("test-key", "gpt-4", mock_client)


@pytest.fixture
def anthropic_adapter(mock_client):
    """Create an Anthropic adapter with mock client."""
    return EnhancedAnthropicAdapter("test-key", "claude-3-sonnet", mock_client)


@pytest.fixture
def gemini_adapter(mock_client):
    """Create a Gemini adapter with mock client."""
    return EnhancedGeminiAdapter("test-key", "gemini-pro", mock_client)


@pytest.fixture
def huggingface_adapter(mock_client):
    """Create a HuggingFace adapter with mock client."""
    return EnhancedHuggingFaceAdapter("test-key", "meta-llama/Llama-2-7b", mock_client)


class TestStandardizedErrors:
    """Test standardized error responses across all adapters."""
    
    @pytest.mark.asyncio
    async def test_authentication_error_openai(self, openai_adapter, mock_client):
        """Test OpenAI authentication error produces standard format."""
        # Mock 401 response
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 401
        mock_response.headers = {}
        mock_client.post.side_effect = httpx.HTTPStatusError(
            "401 Unauthorized",
            request=Mock(),
            response=mock_response
        )
        
        result = await openai_adapter.generate("test prompt")
        
        # Verify error format
        assert "generated_text" in result
        assert "Error:" in result["generated_text"]
        assert "authentication failed" in result["generated_text"].lower()
        assert result["provider"] == "openai"
    
    @pytest.mark.asyncio
    async def test_authentication_error_anthropic(self, anthropic_adapter, mock_client):
        """Test Anthropic authentication error produces standard format."""
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 401
        mock_response.headers = {}
        mock_client.post.side_effect = httpx.HTTPStatusError(
            "401 Unauthorized",
            request=Mock(),
            response=mock_response
        )
        
        result = await anthropic_adapter.generate("test prompt")
        
        assert "generated_text" in result
        assert "Error:" in result["generated_text"]
        assert "authentication failed" in result["generated_text"].lower()
        assert result["provider"] == "anthropic"
    
    @pytest.mark.asyncio
    async def test_rate_limit_error_all_providers(self, openai_adapter, anthropic_adapter, 
                                                  gemini_adapter, huggingface_adapter, mock_client):
        """Test rate limit errors are consistent across providers."""
        # Mock 429 response with retry-after header
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 429
        mock_response.headers = {"retry-after": "60"}
        mock_client.post.side_effect = httpx.HTTPStatusError(
            "429 Too Many Requests",
            request=Mock(),
            response=mock_response
        )
        
        # Test all adapters
        adapters = [
            ("openai", openai_adapter),
            ("anthropic", anthropic_adapter),
            ("google", gemini_adapter),
            ("huggingface", huggingface_adapter)
        ]
        
        for provider_name, adapter in adapters:
            result = await adapter.generate("test prompt")
            
            assert "generated_text" in result
            assert "Error:" in result["generated_text"]
            # Check for rate limit or quota exceeded messages
            error_text = result["generated_text"].lower()
            assert ("rate limit exceeded" in error_text or "quota exceeded" in error_text)
            assert result["provider"] == provider_name
    
    @pytest.mark.asyncio
    async def test_model_not_found_error(self, openai_adapter, mock_client):
        """Test model not found error format."""
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 404
        mock_response.headers = {}
        mock_client.post.side_effect = httpx.HTTPStatusError(
            "404 Not Found",
            request=Mock(),
            response=mock_response
        )
        
        result = await openai_adapter.generate("test prompt")
        
        assert "generated_text" in result
        assert "Error:" in result["generated_text"]
        assert "not found" in result["generated_text"].lower()
        assert "gpt-4" in result["generated_text"]  # Should include model name
    
    @pytest.mark.asyncio
    async def test_timeout_error(self, gemini_adapter, mock_client):
        """Test timeout error produces standard format."""
        mock_client.post.side_effect = httpx.ReadTimeout("Request timed out")
        
        result = await gemini_adapter.generate("test prompt")
        
        assert "generated_text" in result
        assert "Error:" in result["generated_text"]
        assert "timed out" in result["generated_text"].lower()
        assert result["provider"] == "google"
    
    @pytest.mark.asyncio
    async def test_huggingface_model_loading(self, huggingface_adapter, mock_client):
        """Test HuggingFace model loading error."""
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 503
        mock_response.headers = {}
        mock_response.json.return_value = {"estimated_time": 45}
        mock_client.post.side_effect = httpx.HTTPStatusError(
            "503 Service Unavailable",
            request=Mock(),
            response=mock_response
        )
        
        result = await huggingface_adapter.generate("test prompt")
        
        assert "generated_text" in result
        assert "Model is loading" in result["generated_text"]
        assert "30 seconds" in result["generated_text"] or "45 seconds" in result["generated_text"]
    
    @pytest.mark.asyncio
    async def test_success_response_format(self, openai_adapter, mock_client):
        """Test successful response maintains backward compatibility."""
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{
                "message": {"content": "This is a test response"},
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 20,
                "total_tokens": 30
            }
        }
        mock_response.raise_for_status = Mock()
        mock_client.post.return_value = mock_response
        
        result = await openai_adapter.generate("test prompt")
        
        assert "generated_text" in result
        assert result["generated_text"] == "This is a test response"
        assert "error" not in result


class TestErrorResponseModel:
    """Test the error response model."""
    
    def test_error_response_to_legacy_format(self):
        """Test error response converts to legacy format correctly."""
        error = LLMErrorResponse(
            error_type=ErrorType.RATE_LIMIT_EXCEEDED,
            error_message="Rate limit hit",
            provider="openai",
            model="gpt-4",
            status_code=429,
            retry_after=60
        )
        
        legacy = error.to_legacy_format()
        
        assert "generated_text" in legacy
        assert "Error:" in legacy["generated_text"]
        assert "rate limit exceeded" in legacy["generated_text"].lower()
        assert legacy["provider"] == "openai"
    
    def test_authentication_error_legacy_format(self):
        """Test authentication error legacy format."""
        error = LLMErrorResponse(
            error_type=ErrorType.AUTHENTICATION_FAILED,
            error_message="Invalid key",
            provider="anthropic",
            model="claude-3",
            status_code=401
        )
        
        legacy = error.to_legacy_format()
        
        assert "Error: Anthropic API authentication failed" in legacy["generated_text"]
        assert "Check API key" in legacy["generated_text"]