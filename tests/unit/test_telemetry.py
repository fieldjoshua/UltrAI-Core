"""
Tests for telemetry service and integrations.
"""

import pytest
import asyncio
import time
from unittest.mock import Mock, patch, AsyncMock

from app.services.telemetry_service import TelemetryService, telemetry
from app.services.telemetry_llm_wrapper import TelemetryLLMWrapper


@pytest.mark.unit
class TestTelemetryService:
    """Test the telemetry service."""

    def test_telemetry_initialization(self):
        """Test that telemetry service initializes properly."""
        service = TelemetryService()
        assert service is not None
        
    def test_record_request(self):
        """Test recording HTTP request metrics."""
        service = TelemetryService()
        # Should not raise exceptions even if not initialized
        service.record_request("GET", "/api/test", 200, 150.5)
        service.record_request("POST", "/api/test", 500, 250.0)
        
    def test_record_llm_request(self):
        """Test recording LLM request metrics."""
        service = TelemetryService()
        # Should not raise exceptions even if not initialized
        service.record_llm_request(
            provider="openai",
            model="gpt-4",
            duration_ms=2500.0,
            success=True,
            input_tokens=100,
            output_tokens=200,
            cost=0.015
        )
        
    def test_record_stage_duration(self):
        """Test recording pipeline stage duration."""
        service = TelemetryService()
        # Should not raise exceptions even if not initialized
        service.record_stage_duration("initial_response", 3000.0)
        service.record_stage_duration("ultra_synthesis", 1500.0)
        
    def test_record_error(self):
        """Test recording errors."""
        service = TelemetryService()
        # Should not raise exceptions even if not initialized
        service.record_error("llm_error", provider="openai", stage="initial_response")
        service.record_error("stage_error", stage="peer_review")
        
    def test_trace_span_context_manager(self):
        """Test trace span context manager."""
        service = TelemetryService()
        
        # Should work even without initialization
        with service.trace_span("test_operation", {"key": "value"}) as span:
            # Span may be None if not initialized
            pass
            
    def test_measure_stage_context_manager(self):
        """Test measure stage context manager."""
        service = TelemetryService()
        
        # Should work even without initialization
        with service.measure_stage("test_stage") as span:
            time.sleep(0.1)  # Simulate work
            
        # Should handle exceptions properly
        with pytest.raises(ValueError):
            with service.measure_stage("error_stage"):
                raise ValueError("Test error")


@pytest.mark.unit
class TestTelemetryLLMWrapper:
    """Test the telemetry LLM wrapper."""

    @pytest.mark.asyncio
    async def test_wrapper_initialization(self):
        """Test wrapper initialization."""
        mock_adapter = AsyncMock()
        wrapper = TelemetryLLMWrapper(mock_adapter, "openai", "gpt-4")
        
        assert wrapper.adapter == mock_adapter
        assert wrapper.provider == "openai"
        assert wrapper.model == "gpt-4"
        
    @pytest.mark.asyncio
    async def test_wrapper_generate_success(self):
        """Test wrapper generate with successful response."""
        # Mock adapter
        mock_adapter = AsyncMock()
        mock_adapter.generate.return_value = {
            "generated_text": "This is a test response from the model."
        }
        
        # Create wrapper
        wrapper = TelemetryLLMWrapper(mock_adapter, "openai", "gpt-4")
        
        # Call generate
        result = await wrapper.generate("Test prompt")
        
        # Verify
        assert result["generated_text"] == "This is a test response from the model."
        mock_adapter.generate.assert_called_once_with("Test prompt")
        
    @pytest.mark.asyncio
    async def test_wrapper_generate_error(self):
        """Test wrapper generate with error response."""
        # Mock adapter
        mock_adapter = AsyncMock()
        mock_adapter.generate.return_value = {
            "generated_text": "Error: API rate limit exceeded"
        }
        
        # Create wrapper
        wrapper = TelemetryLLMWrapper(mock_adapter, "anthropic", "claude-3")
        
        # Call generate
        result = await wrapper.generate("Test prompt")
        
        # Should return error as-is
        assert "Error:" in result["generated_text"]
        
    @pytest.mark.asyncio
    async def test_wrapper_generate_exception(self):
        """Test wrapper generate with exception."""
        # Mock adapter that raises exception
        mock_adapter = AsyncMock()
        mock_adapter.generate.side_effect = Exception("Connection failed")
        
        # Create wrapper
        wrapper = TelemetryLLMWrapper(mock_adapter, "google", "gemini-pro")
        
        # Should propagate exception
        with pytest.raises(Exception) as exc_info:
            await wrapper.generate("Test prompt")
        assert "Connection failed" in str(exc_info.value)
        
    def test_token_estimation(self):
        """Test token estimation logic."""
        mock_adapter = Mock()
        wrapper = TelemetryLLMWrapper(mock_adapter, "openai", "gpt-4")
        
        # Test with short text
        tokens = wrapper._estimate_tokens("Hello world!")
        assert tokens > 0
        assert tokens < 10  # Should be around 3 tokens
        
        # Test with longer text
        long_text = "This is a much longer text that should result in more tokens. " * 10
        tokens = wrapper._estimate_tokens(long_text)
        assert tokens > 50
        
    def test_cost_calculation(self):
        """Test cost calculation."""
        mock_adapter = Mock()
        wrapper = TelemetryLLMWrapper(mock_adapter, "openai", "gpt-4")
        
        # Test with known model
        cost = wrapper._calculate_cost(1000, 2000)  # 1K input, 2K output
        assert cost > 0
        assert cost == (1.0 * 0.03 + 2.0 * 0.06)  # GPT-4 pricing
        
        # Test with different model
        wrapper.model = "gpt-3.5-turbo"
        cost = wrapper._calculate_cost(1000, 2000)
        assert cost == (1.0 * 0.0005 + 2.0 * 0.0015)  # GPT-3.5 pricing
        
        # Test with unknown model (should use defaults)
        wrapper.model = "unknown-model"
        cost = wrapper._calculate_cost(1000, 1000)
        assert cost > 0  # Should use default pricing
        
    @pytest.mark.asyncio
    async def test_wrapper_metrics(self):
        """Test that wrapper properly tracks metrics."""
        mock_adapter = AsyncMock()
        mock_adapter.generate.return_value = {
            "generated_text": "Test response"
        }
        
        # Mock telemetry methods
        with patch.object(telemetry, 'record_llm_request') as mock_record:
            wrapper = TelemetryLLMWrapper(mock_adapter, "openai", "gpt-4")
            await wrapper.generate("Test prompt")
            
            # Verify telemetry was called
            mock_record.assert_called_once()
            call_args = mock_record.call_args
            assert call_args[1]['provider'] == "openai"
            assert call_args[1]['model'] == "gpt-4"
            assert call_args[1]['success'] is True
            assert call_args[1]['input_tokens'] > 0
            assert call_args[1]['output_tokens'] > 0
            assert call_args[1]['cost'] > 0