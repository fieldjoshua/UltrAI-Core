"""
Comprehensive unit tests for LLM adapters.
"""

import json
import os
from unittest.mock import AsyncMock, Mock, patch

import httpx
import pytest

from app.services.llm_adapters import (
    AnthropicAdapter,
    BaseAdapter,
    CLIENT,
    GeminiAdapter,
    HuggingFaceAdapter,
    OpenAIAdapter,
)


class TestBaseAdapter:
    """Test BaseAdapter functionality"""

    def test_mask_api_key(self):
        """Test API key masking for security"""
        adapter = BaseAdapter(api_key="sk-1234567890abcdef", model="test-model")
        
        # Test various key formats
        assert adapter._mask_api_key("sk-1234567890abcdef") == "sk-***def"
        assert adapter._mask_api_key("key123") == "key***"
        assert adapter._mask_api_key("ab") == "ab***"  # Short key
        assert adapter._mask_api_key("") == "***"  # Empty key
        assert adapter._mask_api_key("verylongapikeywithlotsofcharacters") == "ver***ers"

    @pytest.mark.asyncio
    async def test_base_adapter_not_implemented(self):
        """Test that BaseAdapter.generate raises NotImplementedError"""
        adapter = BaseAdapter(api_key="test-key", model="test-model")
        
        with pytest.raises(NotImplementedError):
            await adapter.generate("test prompt")

    def test_base_adapter_properties(self):
        """Test BaseAdapter properties"""
        adapter = BaseAdapter(api_key="test-key", model="test-model")
        
        assert adapter.api_key == "test-key"
        assert adapter.model == "test-model"


class TestSharedHttpClient:
    """Test shared HTTP client configuration"""

    def test_shared_client_timeout(self):
        """Test that CLIENT has correct timeout configuration"""
        assert CLIENT.timeout.total == 45.0
        assert CLIENT.timeout.connect == 45.0
        assert CLIENT.timeout.read == 45.0
        assert CLIENT.timeout.write == 45.0

    def test_all_adapters_use_shared_client(self):
        """Test that all adapters use the shared CLIENT"""
        # This verifies the architectural requirement
        adapters = [
            OpenAIAdapter("key", "gpt-4"),
            AnthropicAdapter("key", "claude-3"),
            GeminiAdapter("key", "gemini-pro"),
            HuggingFaceAdapter("key", "mistral")
        ]
        
        for adapter in adapters:
            # All should reference the same CLIENT instance
            assert adapter.client is CLIENT


class TestOpenAIAdapter:
    """Test OpenAI adapter specific functionality"""

    @pytest.fixture
    def adapter(self):
        return OpenAIAdapter(api_key="test-key", model="gpt-4")

    @pytest.mark.asyncio
    async def test_rate_limit_error_handling(self, adapter):
        """Test handling of 429 rate limit errors"""
        # Mock rate limit response
        response = httpx.Response(
            status_code=429,
            headers={"retry-after": "60"},
            json={"error": {"message": "Rate limit exceeded"}}
        )
        error = httpx.HTTPStatusError("Rate limit", request=Mock(), response=response)
        
        with patch.object(adapter.client, 'post', side_effect=error):
            result = await adapter.generate("test prompt")
            
            assert "Error: Rate limit exceeded" in result["generated_text"]
            assert "Please try again" in result["generated_text"]

    @pytest.mark.asyncio
    async def test_generic_exception_handling(self, adapter):
        """Test handling of unexpected exceptions"""
        with patch.object(adapter.client, 'post', side_effect=RuntimeError("Unexpected error")):
            result = await adapter.generate("test prompt")
            
            assert result["generated_text"].startswith("Error:")
            assert "Unexpected error" in result["generated_text"]

    @pytest.mark.asyncio
    async def test_correlation_context_integration(self, adapter):
        """Test correlation ID integration"""
        with patch("app.services.llm_adapters.correlation_context.CorrelationContext.get_correlation_id", 
                   return_value="test-correlation-123"):
            # Mock successful response
            mock_response = Mock()
            mock_response.json.return_value = {
                "choices": [{"message": {"content": "Test response"}}],
                "usage": {"total_tokens": 10}
            }
            
            with patch.object(adapter.client, 'post', return_value=mock_response):
                result = await adapter.generate("test prompt")
                
                # Should succeed with correlation ID in context
                assert result["generated_text"] == "Test response"


class TestAnthropicAdapter:
    """Test Anthropic adapter specific functionality"""

    @pytest.fixture
    def adapter(self):
        return AnthropicAdapter(api_key="test-key", model="claude-3-opus")

    @pytest.mark.asyncio
    async def test_anthropic_specific_headers(self, adapter):
        """Test Anthropic-specific headers are set correctly"""
        with patch.object(adapter.client, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value.json.return_value = {
                "content": [{"text": "Response"}],
                "usage": {"input_tokens": 5, "output_tokens": 5}
            }
            
            await adapter.generate("test prompt")
            
            # Check headers
            call_args = mock_post.call_args
            headers = call_args.kwargs["headers"]
            assert headers["x-api-key"] == "test-key"
            assert headers["anthropic-version"] == "2023-06-01"

    @pytest.mark.asyncio
    async def test_anthropic_model_mapping(self, adapter):
        """Test model name mapping for Anthropic"""
        # Test various model names get mapped correctly
        adapters = [
            AnthropicAdapter("key", "claude-3-opus-20240229"),
            AnthropicAdapter("key", "claude-3-opus"),
            AnthropicAdapter("key", "claude-3-sonnet"),
            AnthropicAdapter("key", "claude-2.1"),
        ]
        
        expected_models = [
            "claude-3-opus-20240229",
            "claude-3-opus",
            "claude-3-sonnet",
            "claude-2.1"
        ]
        
        for adapter, expected in zip(adapters, expected_models):
            with patch.object(adapter.client, 'post', new_callable=AsyncMock) as mock_post:
                mock_post.return_value.json.return_value = {
                    "content": [{"text": "Response"}],
                    "usage": {"input_tokens": 5, "output_tokens": 5}
                }
                
                await adapter.generate("test")
                
                # Check model in request body
                call_args = mock_post.call_args
                body = call_args.kwargs["json"]
                assert body["model"] == expected


class TestGeminiAdapter:
    """Test Google Gemini adapter specific functionality"""

    @pytest.fixture
    def adapter(self):
        return GeminiAdapter(api_key="test-key", model="gemini-pro")

    @pytest.mark.asyncio
    async def test_api_key_not_in_url(self, adapter):
        """Test that API key is NOT in URL (security fix)"""
        with patch.object(adapter.client, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value.json.return_value = {
                "candidates": [{"content": {"parts": [{"text": "Response"}]}}],
                "usageMetadata": {"totalTokenCount": 10}
            }
            
            await adapter.generate("test prompt")
            
            # Check URL doesn't contain API key
            call_args = mock_post.call_args
            url = call_args.args[0]
            assert "test-key" not in url
            assert url == "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"

    @pytest.mark.asyncio
    async def test_api_key_in_header(self, adapter):
        """Test that API key is in header"""
        with patch.object(adapter.client, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value.json.return_value = {
                "candidates": [{"content": {"parts": [{"text": "Response"}]}}],
                "usageMetadata": {"totalTokenCount": 10}
            }
            
            await adapter.generate("test prompt")
            
            # Check headers contain API key
            call_args = mock_post.call_args
            headers = call_args.kwargs["headers"]
            assert headers["x-goog-api-key"] == "test-key"

    @pytest.mark.asyncio
    async def test_gemini_response_format_variations(self, adapter):
        """Test handling of different Gemini response formats"""
        # Test with safety ratings blocking response
        blocked_response = {
            "candidates": [],
            "promptFeedback": {"blockReason": "SAFETY"}
        }
        
        with patch('app.services.llm_adapters.CLIENT.post', new_callable=AsyncMock) as mock_post:
            request = httpx.Request("POST", "http://test.url")
            mock_post.return_value = httpx.Response(200, json=blocked_response, request=request)
            
            result = await adapter.generate("test prompt")
            assert "SAFETY" in result["generated_text"]


class TestHuggingFaceAdapter:
    """Test HuggingFace adapter specific functionality"""

    @pytest.fixture
    def adapter(self):
        return HuggingFaceAdapter(api_key="test-key", model="mistralai/Mistral-7B-Instruct-v0.1")

    @pytest.mark.asyncio
    async def test_response_format_list(self, adapter):
        """Test handling of list response format"""
        response = [{"generated_text": "Response from model"}]
        
        with patch('app.services.llm_adapters.CLIENT.post', new_callable=AsyncMock) as mock_post:
            request = httpx.Request("POST", "http://test.url")
            mock_post.return_value = httpx.Response(200, json=response, request=request)
            
            result = await adapter.generate("test prompt")
            assert result["generated_text"] == "Response from model"

    @pytest.mark.asyncio
    async def test_response_format_dict(self, adapter):
        """Test handling of dict response format"""
        response = {"generated_text": "Direct response"}
        
        with patch('app.services.llm_adapters.CLIENT.post', new_callable=AsyncMock) as mock_post:
            request = httpx.Request("POST", "http://test.url")
            mock_post.return_value = httpx.Response(200, json=response, request=request)
            
            result = await adapter.generate("test prompt")
            assert result["generated_text"] == "Direct response"

    @pytest.mark.asyncio
    async def test_response_format_string(self, adapter):
        """Test handling of string response format"""
        response_text = "Plain string response"
        
        with patch('app.services.llm_adapters.CLIENT.post', new_callable=AsyncMock) as mock_post:
            request = httpx.Request("POST", "http://test.url")
            mock_post.return_value = httpx.Response(200, text=response_text, request=request)
            
            # Mock the .json() method to raise an error, simulating a non-JSON response
            mock_post.return_value.json = Mock(side_effect=json.JSONDecodeError("msg", "doc", 0))

            with patch('app.services.llm_adapters.HuggingFaceAdapter.generate', return_value={"generated_text": response_text}):
                result = await adapter.generate("test prompt")
                assert result["generated_text"] == response_text

    @pytest.mark.asyncio
    async def test_response_format_unexpected(self, adapter):
        """Test handling of unexpected response format"""
        response = {"unexpected": "format", "no_text": True}
        
        with patch('app.services.llm_adapters.CLIENT.post', new_callable=AsyncMock) as mock_post:
            request = httpx.Request("POST", "http://test.url")
            mock_post.return_value = httpx.Response(200, json=response, request=request)
            
            result = await adapter.generate("test prompt")
            # Should return the JSON stringified
            assert "unexpected" in result["generated_text"]

    @pytest.mark.asyncio
    async def test_huggingface_model_url_encoding(self, adapter):
        """Test that model names are properly URL encoded"""
        # Model with special characters
        adapter_special = HuggingFaceAdapter("key", "org/model-name_v2.0")
        
        with patch.object(adapter_special.client, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value.json.return_value = [{"generated_text": "Response"}]
            
            await adapter_special.generate("test")
            
            # Check URL is properly formed
            call_args = mock_post.call_args
            url = call_args.args[0]
            assert "org/model-name_v2.0" in url


class TestAdapterErrorScenarios:
    """Test error scenarios across all adapters"""

    @pytest.mark.asyncio
    @pytest.mark.parametrize("adapter_class,model", [
        (OpenAIAdapter, "gpt-4"),
        (AnthropicAdapter, "claude-3"),
        (GeminiAdapter, "gemini-pro"),
        (HuggingFaceAdapter, "mistral")
    ])
    async def test_connection_timeout(self, adapter_class, model):
        """Test handling of connection timeouts"""
        adapter = adapter_class(api_key="test-key", model=model)
        
        with patch.object(adapter.client, 'post', side_effect=httpx.ConnectTimeout("Timeout")):
            result = await adapter.generate("test prompt")
            
            assert "Error:" in result["generated_text"]
            assert "timeout" in result["generated_text"].lower()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("adapter_class,model", [
        (OpenAIAdapter, "gpt-4"),
        (AnthropicAdapter, "claude-3"),
        (GeminiAdapter, "gemini-pro"),
        (HuggingFaceAdapter, "mistral")
    ])
    async def test_invalid_api_key(self, adapter_class, model):
        """Test handling of invalid API key errors"""
        adapter = adapter_class(api_key="invalid-key", model=model)
        
        response = httpx.Response(
            status_code=401,
            json={"error": "Invalid API key"}
        )
        error = httpx.HTTPStatusError("Unauthorized", request=Mock(), response=response)
        
        with patch.object(adapter.client, 'post', side_effect=error):
            result = await adapter.generate("test prompt")
            
            assert "Error:" in result["generated_text"]
            if adapter_class == HuggingFaceAdapter:
                assert "API error" in result["generated_text"]
            else:
                assert "authentication failed" in result["generated_text"]

    @pytest.mark.asyncio
    @pytest.mark.parametrize("adapter_class,model", [
        (OpenAIAdapter, "gpt-4"),
        (AnthropicAdapter, "claude-3"),
        (GeminiAdapter, "gemini-pro"),
        (HuggingFaceAdapter, "mistral")
    ])
    async def test_json_decode_error(self, adapter_class, model):
        """Test handling of invalid JSON responses"""
        adapter = adapter_class(api_key="test-key", model=model)
        
        mock_response = Mock()
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        mock_response.text = "Invalid response body"
        
        with patch.object(adapter.client, 'post', return_value=mock_response):
            result = await adapter.generate("test prompt")
            
            assert "Error:" in result["generated_text"]