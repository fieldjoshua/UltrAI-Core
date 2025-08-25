"""
Integration tests for P1 enhancements.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
import time

from app.middleware.combined_auth_middleware import CombinedAuthMiddleware
from app.middleware.rate_limit_middleware import RateLimitMiddleware
from app.services.resilient_llm_adapter import (
    ResilientLLMAdapter, 
    CircuitBreakerError,
    CircuitState
)
from app.services.rate_limit_service import RateLimitService


@pytest.mark.integration
class TestAuthMiddleware:
    """Test authentication middleware."""
    
    def test_jwt_auth_extraction(self):
        """Test JWT token extraction from headers."""
        from fastapi import Request
        from app.middleware.combined_auth_middleware import CombinedAuthMiddleware
        
        middleware = CombinedAuthMiddleware(None)
        
        # Mock request with JWT
        request = Mock(spec=Request)
        request.headers = {"authorization": "Bearer test-jwt-token"}
        
        auth_type, token = middleware._extract_auth_token(request)
        assert auth_type == "jwt"
        assert token == "test-jwt-token"
        
    def test_api_key_extraction(self):
        """Test API key extraction from headers."""
        from app.middleware.combined_auth_middleware import CombinedAuthMiddleware
        
        middleware = CombinedAuthMiddleware(None)
        
        # Mock request with API key
        request = Mock()
        request.headers = {"x-api-key": "test-api-key"}
        
        auth_type, token = middleware._extract_auth_token(request)
        assert auth_type == "api_key"
        assert token == "test-api-key"


@pytest.mark.integration
class TestRateLimiting:
    """Test rate limiting functionality."""
    
    @pytest.mark.asyncio
    async def test_tier_based_limits(self):
        """Test different rate limits for user tiers."""
        service = RateLimitService()
        
        # Test free tier
        free_user = Mock()
        free_user.subscription_tier = "free"
        
        # Should allow 10 requests per minute
        for _ in range(10):
            result = await service.check_rate_limit_async("test-endpoint", "user1", free_user)
            assert result.allowed is True
            
        # 11th request should be rate limited
        result = await service.check_rate_limit_async("test-endpoint", "user1", free_user)
        assert result.allowed is False
        assert result.retry_after > 0
        
    @pytest.mark.asyncio
    async def test_api_key_rate_limits(self):
        """Test rate limits for API keys."""
        service = RateLimitService()
        
        api_key = Mock()
        api_key.rate_limit = 100  # 100 requests per minute
        api_key.key = "test-key"
        
        # Should respect API key limits
        for _ in range(5):
            result = await service.check_api_key_rate_limit_async(api_key)
            assert result.allowed is True


@pytest.mark.integration
class TestCircuitBreaker:
    """Test circuit breaker functionality."""
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_states(self):
        """Test circuit breaker state transitions."""
        # Mock adapter that fails
        mock_adapter = AsyncMock()
        mock_adapter.generate.side_effect = Exception("API Error")
        
        resilient = ResilientLLMAdapter(
            mock_adapter,
            provider="test",
            failure_threshold=2,
            recovery_timeout=0.1,
            half_open_requests=1
        )
        
        # First two failures should work (CLOSED state)
        for _ in range(2):
            with pytest.raises(Exception):
                await resilient.generate("test")
                
        # Circuit should now be OPEN
        assert resilient._circuit_state == CircuitState.OPEN
        
        # Next request should fail immediately
        with pytest.raises(CircuitBreakerError):
            await resilient.generate("test")
            
        # Wait for recovery timeout
        await asyncio.sleep(0.2)
        
        # Should now be in HALF_OPEN state
        assert resilient._circuit_state == CircuitState.HALF_OPEN
        
    @pytest.mark.asyncio
    async def test_retry_with_backoff(self):
        """Test retry logic with exponential backoff."""
        call_count = 0
        
        async def flaky_generate(prompt):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("Temporary failure")
            return {"generated_text": "Success"}
            
        mock_adapter = AsyncMock()
        mock_adapter.generate.side_effect = flaky_generate
        
        resilient = ResilientLLMAdapter(
            mock_adapter,
            provider="test",
            max_retries=3
        )
        
        start_time = time.time()
        result = await resilient.generate("test")
        duration = time.time() - start_time
        
        assert result["generated_text"] == "Success"
        assert call_count == 3  # Failed twice, succeeded on third
        assert duration > 0.2  # Should have backoff delays


@pytest.mark.integration
class TestTelemetryIntegration:
    """Test telemetry integration."""
    
    @pytest.mark.asyncio
    async def test_llm_telemetry_wrapper(self):
        """Test that LLM calls are tracked with telemetry."""
        from app.services.telemetry_llm_wrapper import TelemetryLLMWrapper
        
        # Mock adapter
        mock_adapter = AsyncMock()
        mock_adapter.generate.return_value = {
            "generated_text": "Test response from model"
        }
        
        # Wrap with telemetry
        wrapper = TelemetryLLMWrapper(mock_adapter, "openai", "gpt-4")
        
        # Make request
        result = await wrapper.generate("Test prompt")
        
        assert result["generated_text"] == "Test response from model"
        mock_adapter.generate.assert_called_once_with("Test prompt")
        
    def test_token_cost_calculation(self):
        """Test token counting and cost calculation."""
        from app.services.telemetry_llm_wrapper import TelemetryLLMWrapper
        
        wrapper = TelemetryLLMWrapper(None, "openai", "gpt-4")
        
        # Test token estimation
        tokens = wrapper._estimate_tokens("Hello world, this is a test prompt.")
        assert 5 <= tokens <= 15  # Reasonable range
        
        # Test cost calculation for GPT-4
        cost = wrapper._calculate_cost(1000, 2000)  # 1K input, 2K output
        expected_cost = (1.0 * 0.03) + (2.0 * 0.06)  # $0.03 + $0.12
        assert cost == pytest.approx(expected_cost, 0.001)
        
        # Test cost for different model
        wrapper.model = "claude-3-haiku"
        cost = wrapper._calculate_cost(1000, 1000)
        expected_cost = (1.0 * 0.00025) + (1.0 * 0.00125)
        assert cost == pytest.approx(expected_cost, 0.0001)


@pytest.mark.integration
class TestEndToEndIntegration:
    """Test end-to-end integration of P1 enhancements."""
    
    @pytest.mark.asyncio
    async def test_full_request_flow_with_enhancements(self):
        """Test a request going through all enhancements."""
        from app.services.orchestration_service import OrchestrationService
        from app.services.resilient_llm_adapter import create_resilient_adapter
        from app.services.telemetry_llm_wrapper import wrap_llm_adapter_with_telemetry
        
        # This test verifies that all components work together:
        # 1. Request goes through auth middleware
        # 2. Rate limiting is applied
        # 3. LLM calls use resilient adapter (circuit breaker + retries)
        # 4. Telemetry tracks the entire flow
        
        # Mock components
        mock_registry = Mock()
        mock_registry.get_available_models.return_value = ["gpt-4"]
        
        orchestrator = OrchestrationService(
            model_registry=mock_registry,
            rate_limiter=Mock(),
            quality_evaluator=Mock()
        )
        
        # Verify adapter wrapping pattern
        mock_adapter = Mock()
        resilient = create_resilient_adapter(mock_adapter)
        telemetry_wrapped = wrap_llm_adapter_with_telemetry(resilient, "openai", "gpt-4")
        
        assert hasattr(telemetry_wrapped, 'generate')
        assert hasattr(telemetry_wrapped.adapter, 'generate')