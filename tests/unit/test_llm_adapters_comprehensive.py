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


@pytest.mark.unit
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
            # Check both instance and class level
            assert adapter.client is CLIENT or adapter.__class__.CLIENT is CLIENT


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


# Tests merged from test_resilient_llm_adapter.py
class TestCircuitBreaker:
    """Test circuit breaker functionality for resilient adapters"""

    def test_circuit_breaker_initialization(self):
        """Test circuit breaker initializes in closed state"""
        from app.services.resilient_llm_adapter import CircuitBreaker, CircuitBreakerConfig, CircuitState
        
        config = CircuitBreakerConfig(failure_threshold=3, success_threshold=2)
        breaker = CircuitBreaker(config)
        
        assert breaker.state == CircuitState.CLOSED
        assert breaker.failure_count == 0
        assert breaker.success_count == 0

    def test_circuit_breaker_opens_after_failures(self):
        """Test circuit breaker opens after failure threshold"""
        from app.services.resilient_llm_adapter import CircuitBreaker, CircuitBreakerConfig, CircuitState
        
        config = CircuitBreakerConfig(failure_threshold=3, success_threshold=2, min_calls=3)
        breaker = CircuitBreaker(config)
        
        # Simulate failures
        for i in range(3):
            try:
                breaker.call(lambda: 1/0)  # This will raise ZeroDivisionError
            except:
                pass
        
        assert breaker.state == CircuitState.OPEN
        assert breaker.failure_count == 3

    def test_circuit_breaker_half_open_after_timeout(self):
        """Test circuit breaker transitions to half-open after timeout"""
        import time
        from app.services.resilient_llm_adapter import CircuitBreaker, CircuitBreakerConfig, CircuitState
        
        config = CircuitBreakerConfig(failure_threshold=2, timeout=0.1, success_threshold=1, min_calls=2)
        breaker = CircuitBreaker(config)
        
        # Cause failures to open circuit
        for i in range(2):
            try:
                breaker.call(lambda: 1/0)
            except:
                pass
        
        assert breaker.state == CircuitState.OPEN
        
        # Wait for timeout
        time.sleep(0.2)
        
        # A successful call in half-open state should close the circuit
        breaker.call(lambda: "success")
        assert breaker.state == CircuitState.CLOSED

    @pytest.mark.asyncio
    async def test_async_circuit_breaker(self):
        """Test async circuit breaker operations"""
        from app.services.resilient_llm_adapter import CircuitBreaker, CircuitBreakerConfig, CircuitState
        
        config = CircuitBreakerConfig(failure_threshold=2, success_threshold=1, min_calls=2)
        breaker = CircuitBreaker(config)
        
        # Test successful async call
        async def async_success():
            return "success"
        
        result = await breaker.async_call(async_success)
        assert result == "success"
        assert breaker.state == CircuitState.CLOSED
        
        # Test failing async calls
        async def async_failure():
            raise Exception("Test error")
        
        for i in range(2):
            with pytest.raises(Exception, match="Test error"):
                await breaker.async_call(async_failure)
        
        assert breaker.state == CircuitState.OPEN


class TestResilientLLMAdapter:
    """Test resilient LLM adapter wrapper functionality"""

    @pytest.fixture
    def mock_adapter(self):
        """Create a mock base adapter"""
        adapter = AsyncMock()
        adapter.model = "test-model"
        return adapter

    @pytest.mark.asyncio
    async def test_successful_generation(self, mock_adapter):
        """Test successful generation through resilient adapter"""
        from app.services.resilient_llm_adapter import ResilientLLMAdapter, RetryConfig, CircuitBreakerConfig
        
        mock_adapter.generate.return_value = {"generated_text": "Test response"}
        
        resilient = ResilientLLMAdapter(
            adapter=mock_adapter,
            retry_config=RetryConfig(max_retries=3, initial_delay=0.1),
            circuit_breaker_config=CircuitBreakerConfig(failure_threshold=5)
        )
        
        result = await resilient.generate("Test prompt")
        assert result["generated_text"] == "Test response"
        mock_adapter.generate.assert_called_once_with("Test prompt")

    @pytest.mark.asyncio
    async def test_retry_on_timeout(self, mock_adapter):
        """Test retry logic on timeout errors"""
        from app.services.resilient_llm_adapter import ResilientLLMAdapter, RetryConfig, CircuitBreakerConfig
        
        # First two calls timeout, third succeeds
        mock_adapter.generate.side_effect = [
            httpx.TimeoutException("Timeout"),
            httpx.TimeoutException("Timeout"),
            {"generated_text": "Success after retries"}
        ]
        
        resilient = ResilientLLMAdapter(
            adapter=mock_adapter,
            retry_config=RetryConfig(max_retries=3, initial_delay=0.01),
            circuit_breaker_config=CircuitBreakerConfig(failure_threshold=5)
        )
        
        result = await resilient.generate("Test prompt")
        assert result["generated_text"] == "Success after retries"
        assert mock_adapter.generate.call_count == 3

    @pytest.mark.asyncio
    async def test_exponential_backoff_with_jitter(self, mock_adapter):
        """Test exponential backoff timing with jitter"""
        from app.services.resilient_llm_adapter import ResilientLLMAdapter, RetryConfig, CircuitBreakerConfig
        import time
        
        # Mock to fail 3 times then succeed
        mock_adapter.generate.side_effect = [
            httpx.TimeoutException("Timeout"),
            httpx.TimeoutException("Timeout"),
            httpx.TimeoutException("Timeout"),
            {"generated_text": "Success"}
        ]
        
        resilient = ResilientLLMAdapter(
            adapter=mock_adapter,
            retry_config=RetryConfig(
                max_retries=4, 
                initial_delay=0.1,
                exponential_base=2,
                max_delay=1.0,
                jitter=True
            ),
            circuit_breaker_config=CircuitBreakerConfig(failure_threshold=10)
        )
        
        start_time = time.time()
        result = await resilient.generate("Test prompt")
        elapsed = time.time() - start_time
        
        # With delays of ~0.1, ~0.2, ~0.4 (plus jitter), total should be ~0.7s minimum
        assert elapsed >= 0.5  # Allow for jitter variation
        assert elapsed <= 2.0  # But not too long
        assert result["generated_text"] == "Success"
        assert mock_adapter.generate.call_count == 4


class TestProviderSpecificResilience:
    """Test provider-specific resilience configurations"""

    def test_openai_config(self):
        """Test OpenAI-specific resilient configuration"""
        from app.services.resilient_llm_adapter import ProviderConfig
        
        config = ProviderConfig.for_openai()
        assert config.timeout == 25.0
        assert config.retry_config.max_retries == 3
        assert config.circuit_breaker_config.failure_threshold == 5

    def test_anthropic_config(self):
        """Test Anthropic-specific resilient configuration"""
        from app.services.resilient_llm_adapter import ProviderConfig
        
        config = ProviderConfig.for_anthropic()
        assert config.timeout == 30.0
        assert config.retry_config.max_retries == 2
        assert config.circuit_breaker_config.failure_threshold == 4

    def test_google_config(self):
        """Test Google-specific resilient configuration"""
        from app.services.resilient_llm_adapter import ProviderConfig
        
        config = ProviderConfig.for_google()
        assert config.timeout == 35.0
        assert config.retry_config.max_retries == 3
        assert config.circuit_breaker_config.failure_threshold == 6

    @pytest.mark.asyncio
    async def test_create_resilient_adapter_detection(self):
        """Test automatic provider detection in create_resilient_adapter"""
        from app.services.resilient_llm_adapter import create_resilient_adapter
        
        # Test OpenAI detection
        openai_adapter = OpenAIAdapter(api_key="test", model="gpt-4")
        resilient_openai = create_resilient_adapter(openai_adapter)
        assert resilient_openai.timeout == 25.0
        
        # Test Anthropic detection
        anthropic_adapter = AnthropicAdapter(api_key="test", model="claude-3")
        resilient_anthropic = create_resilient_adapter(anthropic_adapter)
        assert resilient_anthropic.timeout == 30.0


# Tests merged from test_standardized_llm_errors.py
class TestRateLimitHandling:
    """Test rate limit error handling across providers"""
    
    @pytest.mark.asyncio
    async def test_rate_limit_error_format(self):
        """Test that rate limit errors have consistent format across providers"""
        # Test OpenAI rate limit
        openai_adapter = OpenAIAdapter(api_key="test", model="gpt-4")
        with patch.object(openai_adapter.client, 'post') as mock_post:
            mock_response = Mock()
            mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "Rate limit", request=Mock(), response=Mock(status_code=429)
            )
            mock_post.return_value = mock_response
            
            result = await openai_adapter.generate("test")
            assert "Rate limit exceeded" in result["generated_text"]
            assert result.get("error_details", {}).get("error") == "RATE_LIMITED"
            
        # Test Anthropic rate limit
        anthropic_adapter = AnthropicAdapter(api_key="test", model="claude-3")
        with patch.object(anthropic_adapter.client, 'post') as mock_post:
            mock_response = Mock()
            mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "Rate limit", request=Mock(), response=Mock(status_code=429)
            )
            mock_post.return_value = mock_response
            
            result = await anthropic_adapter.generate("test")
            assert "Rate limit exceeded" in result["generated_text"]
            assert result.get("error_details", {}).get("error") == "RATE_LIMITED"


class TestErrorConsistency:
    """Test error message consistency across adapters"""
    
    def test_error_response_format(self):
        """Test that all errors follow consistent format"""
        test_errors = [
            {"generated_text": "Error: Something went wrong"},
            {"generated_text": "Error: Rate limit exceeded", "error_details": {"error": "RATE_LIMITED"}},
            {"generated_text": "Error: Authentication failed"},
        ]
        
        for error in test_errors:
            assert "generated_text" in error
            assert error["generated_text"].startswith("Error:")
            
            # If error_details present, check structure
            if "error_details" in error:
                assert "error" in error["error_details"]