"""
Tests for resilient LLM adapter with circuit breakers, retries, and timeouts.
"""

import asyncio
import pytest
from unittest.mock import Mock, AsyncMock, patch
import httpx

from app.services.resilient_llm_adapter import (
    ResilientLLMAdapter,
    CircuitBreaker,
    CircuitState,
    CircuitBreakerConfig,
    RetryConfig,
    ProviderConfig,
    create_resilient_adapter,
)
from app.services.llm_adapters import OpenAIAdapter, AnthropicAdapter, GeminiAdapter


class TestCircuitBreaker:
    """Test circuit breaker functionality"""

    def test_circuit_breaker_initialization(self):
        """Test circuit breaker initializes in closed state"""
        config = CircuitBreakerConfig(failure_threshold=3, success_threshold=2)
        breaker = CircuitBreaker(config)
        
        assert breaker.state == CircuitState.CLOSED
        assert breaker.failure_count == 0
        assert breaker.success_count == 0

    def test_circuit_breaker_opens_after_failures(self):
        """Test circuit breaker opens after failure threshold"""
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
        config = CircuitBreakerConfig(failure_threshold=2, timeout=0.1)  # 100ms timeout
        breaker = CircuitBreaker(config)
        
        # Cause failures to open circuit
        for i in range(2):
            try:
                breaker.call(lambda: 1/0)
            except:
                pass
        
        assert breaker.state == CircuitState.OPEN
        
        # Wait for timeout
        import time
        time.sleep(0.2)
        
        # Next call should transition to half-open
        try:
            breaker.call(lambda: "success")
        except Exception as e:
            if "Circuit breaker is OPEN" not in str(e):
                assert breaker.state == CircuitState.HALF_OPEN

    @pytest.mark.asyncio
    async def test_async_circuit_breaker(self):
        """Test async circuit breaker operations"""
        config = CircuitBreakerConfig(failure_threshold=2, success_threshold=1)
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
            try:
                await breaker.async_call(async_failure)
            except:
                pass
        
        assert breaker.state == CircuitState.OPEN


class TestResilientLLMAdapter:
    """Test resilient LLM adapter functionality"""

    @pytest.fixture
    def mock_adapter(self):
        """Create a mock base adapter"""
        adapter = Mock()
        adapter.model = "test-model"
        adapter.generate = AsyncMock(return_value={"generated_text": "Test response"})
        return adapter

    @pytest.mark.asyncio
    async def test_successful_generation(self, mock_adapter):
        """Test successful text generation"""
        resilient = ResilientLLMAdapter(mock_adapter, "test")
        
        result = await resilient.generate("Test prompt")
        
        assert result["generated_text"] == "Test response"
        assert resilient.metrics["successful_requests"] == 1
        assert resilient.metrics["failed_requests"] == 0
        assert resilient.metrics["retries"] == 0

    @pytest.mark.asyncio
    async def test_retry_on_timeout(self, mock_adapter):
        """Test retry behavior on timeout"""
        # First call times out, second succeeds
        mock_adapter.generate = AsyncMock(
            side_effect=[
                httpx.ReadTimeout("Timeout"),
                {"generated_text": "Success after retry"}
            ]
        )
        
        resilient = ResilientLLMAdapter(mock_adapter, "test")
        result = await resilient.generate("Test prompt")
        
        assert result["generated_text"] == "Success after retry"
        assert resilient.metrics["retries"] == 1
        assert resilient.metrics["successful_requests"] == 1

    @pytest.mark.asyncio
    async def test_no_retry_on_client_error(self, mock_adapter):
        """Test that 4xx errors are not retried"""
        # Simulate 400 Bad Request
        response = Mock()
        response.status_code = 400
        mock_adapter.generate = AsyncMock(
            side_effect=httpx.HTTPStatusError("Bad request", request=Mock(), response=response)
        )
        
        resilient = ResilientLLMAdapter(mock_adapter, "test")
        result = await resilient.generate("Test prompt")
        
        assert "Error:" in result["generated_text"]
        assert resilient.metrics["retries"] == 0  # No retries for client errors
        assert mock_adapter.generate.call_count == 1

    @pytest.mark.asyncio
    async def test_circuit_breaker_integration(self, mock_adapter):
        """Test circuit breaker prevents requests after failures"""
        # Configure with low failure threshold
        config = ProviderConfig(
            name="test",
            timeout=30.0,
            circuit_breaker=CircuitBreakerConfig(failure_threshold=2, min_calls=2),
            retry=RetryConfig(max_attempts=1)  # No retries for this test
        )
        
        resilient = ResilientLLMAdapter(mock_adapter, "test")
        resilient.config = config
        resilient.circuit_breaker = CircuitBreaker(config.circuit_breaker)
        
        # Simulate failures
        mock_adapter.generate = AsyncMock(side_effect=Exception("API Error"))
        
        # First two calls should fail and open the circuit
        for i in range(2):
            result = await resilient.generate("Test prompt")
            assert "Error:" in result["generated_text"]
        
        # Circuit should be open now
        assert resilient.circuit_breaker.state == CircuitState.OPEN
        
        # Next call should fail immediately without calling the adapter
        call_count_before = mock_adapter.generate.call_count
        result = await resilient.generate("Test prompt")
        assert "Circuit breaker is OPEN" in result["generated_text"]
        assert mock_adapter.generate.call_count == call_count_before  # No new calls

    @pytest.mark.asyncio
    async def test_exponential_backoff_with_jitter(self, mock_adapter):
        """Test exponential backoff with jitter between retries"""
        # All calls fail to test retry delays
        mock_adapter.generate = AsyncMock(side_effect=httpx.ReadTimeout("Timeout"))
        
        config = ProviderConfig(
            name="test",
            timeout=30.0,
            retry=RetryConfig(
                max_attempts=3,
                initial_delay=0.1,  # 100ms
                max_delay=1.0,
                exponential_base=2.0,
                jitter=0.1
            )
        )
        
        resilient = ResilientLLMAdapter(mock_adapter, "test")
        resilient.config = config
        
        import time
        start_time = time.time()
        await resilient.generate("Test prompt")
        elapsed = time.time() - start_time
        
        # Should have delays between retries (roughly 0.1 + 0.2 = 0.3s minimum)
        assert elapsed > 0.25  # Account for jitter
        assert resilient.metrics["retries"] == 2  # 3 attempts total

    @pytest.mark.asyncio
    async def test_provider_specific_timeouts(self):
        """Test that provider-specific timeouts are applied"""
        # Test OpenAI timeout
        openai_adapter = OpenAIAdapter("test-key", "gpt-4")
        openai_resilient = create_resilient_adapter(openai_adapter)
        assert openai_resilient.config.timeout == 30.0
        
        # Test Anthropic timeout (longer)
        anthropic_adapter = AnthropicAdapter("test-key", "claude-3")
        anthropic_resilient = create_resilient_adapter(anthropic_adapter)
        assert anthropic_resilient.config.timeout == 45.0
        
        # Test Google timeout (shorter)
        google_adapter = GeminiAdapter("test-key", "gemini-pro")
        google_resilient = create_resilient_adapter(google_adapter)
        assert google_resilient.config.timeout == 25.0

    def test_metrics_tracking(self):
        """Test metrics are properly tracked"""
        mock_adapter = Mock()
        resilient = ResilientLLMAdapter(mock_adapter, "test")
        
        metrics = resilient.get_metrics()
        assert metrics["provider"] == "test"
        assert "total_requests" in metrics["metrics"]
        assert "circuit_breaker" in metrics
        assert metrics["config"]["timeout"] == 30.0  # Default

    @pytest.mark.asyncio
    async def test_cleanup(self, mock_adapter):
        """Test resource cleanup"""
        resilient = ResilientLLMAdapter(mock_adapter, "test")
        
        # Mock the HTTP client
        resilient.client = Mock()
        resilient.client.aclose = AsyncMock()
        
        await resilient.close()
        resilient.client.aclose.assert_called_once()


class TestProviderConfigurations:
    """Test provider-specific configurations"""

    def test_openai_config(self):
        """Test OpenAI configuration"""
        from app.services.resilient_llm_adapter import PROVIDER_CONFIGS
        
        config = PROVIDER_CONFIGS["openai"]
        assert config.timeout == 30.0
        assert config.circuit_breaker.failure_threshold == 5
        assert config.retry.max_attempts == 3

    def test_anthropic_config(self):
        """Test Anthropic configuration"""
        from app.services.resilient_llm_adapter import PROVIDER_CONFIGS
        
        config = PROVIDER_CONFIGS["anthropic"]
        assert config.timeout == 45.0  # Longer for complex prompts
        assert config.circuit_breaker.failure_threshold == 3  # More conservative
        assert config.retry.initial_delay == 2.0  # Slower retry

    def test_google_config(self):
        """Test Google configuration"""
        from app.services.resilient_llm_adapter import PROVIDER_CONFIGS
        
        config = PROVIDER_CONFIGS["google"]
        assert config.timeout == 25.0  # Faster
        assert config.retry.max_attempts == 4  # More retries
        assert config.retry.initial_delay == 0.5  # Faster retry


@pytest.mark.integration
class TestResilientAdapterIntegration:
    """Integration tests with real adapter classes"""

    @pytest.mark.asyncio
    async def test_create_resilient_adapter_detection(self):
        """Test that create_resilient_adapter correctly detects provider"""
        # Mock API keys
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            openai = OpenAIAdapter("test-key", "gpt-4")
            resilient = create_resilient_adapter(openai)
            assert resilient.provider_name == "openai"
        
        with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'}):
            anthropic = AnthropicAdapter("test-key", "claude-3")
            resilient = create_resilient_adapter(anthropic)
            assert resilient.provider_name == "anthropic"
        
        with patch.dict('os.environ', {'GOOGLE_API_KEY': 'test-key'}):
            gemini = GeminiAdapter("test-key", "gemini-pro")
            resilient = create_resilient_adapter(gemini)
            assert resilient.provider_name == "google"