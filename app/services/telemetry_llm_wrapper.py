"""
Telemetry wrapper for LLM adapters to track metrics.

This wrapper:
- Tracks LLM request duration
- Records token usage (input/output)
- Calculates and records costs
- Integrates with OpenTelemetry spans
"""

import time
from typing import Dict, Any, Optional
import tiktoken

from app.services.telemetry_service import telemetry
from app.utils.logging import get_logger

logger = get_logger(__name__)


# Token pricing per 1K tokens (as of 2025)
TOKEN_PRICING = {
    # OpenAI
    "gpt-4": {"input": 0.03, "output": 0.06},
    "gpt-4o": {"input": 0.005, "output": 0.015},
    "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
    "o1": {"input": 0.015, "output": 0.06},
    "o1-preview": {"input": 0.015, "output": 0.06},
    "o1-mini": {"input": 0.003, "output": 0.012},
    
    # Anthropic
    "claude-3-opus": {"input": 0.015, "output": 0.075},
    "claude-3-sonnet": {"input": 0.003, "output": 0.015},
    "claude-3-haiku": {"input": 0.00025, "output": 0.00125},
    "claude-3-5-sonnet": {"input": 0.003, "output": 0.015},
    "claude-3-5-haiku": {"input": 0.001, "output": 0.005},
    
    # Google
    "gemini-pro": {"input": 0.00025, "output": 0.0005},
    "gemini-1.5-pro": {"input": 0.0005, "output": 0.0015},
    "gemini-1.5-flash": {"input": 0.000075, "output": 0.0003},
    "gemini-2.0-flash-exp": {"input": 0.0001, "output": 0.0004},
}


class TelemetryLLMWrapper:
    """Wrapper to add telemetry to LLM adapters."""
    
    def __init__(self, adapter, provider: str, model: str):
        """
        Initialize telemetry wrapper.
        
        Args:
            adapter: Base LLM adapter
            provider: Provider name (openai, anthropic, google)
            model: Model name
        """
        self.adapter = adapter
        self.provider = provider
        self.model = model
        self._tokenizer = None
    
    def _get_tokenizer(self):
        """Get or create tokenizer for token counting."""
        if self._tokenizer is None:
            try:
                # Use cl100k_base for GPT-4 and similar models
                self._tokenizer = tiktoken.get_encoding("cl100k_base")
            except:
                # Fallback to approximate counting
                self._tokenizer = None
        return self._tokenizer
    
    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count for text."""
        tokenizer = self._get_tokenizer()
        if tokenizer:
            try:
                return len(tokenizer.encode(text))
            except:
                pass
        
        # Fallback: rough estimate (1 token ≈ 4 characters)
        return len(text) // 4
    
    def _calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost based on token usage."""
        # Find pricing for this model
        pricing = None
        
        # Check exact match first
        if self.model in TOKEN_PRICING:
            pricing = TOKEN_PRICING[self.model]
        else:
            # Check partial matches
            for model_key, model_pricing in TOKEN_PRICING.items():
                if model_key in self.model or self.model in model_key:
                    pricing = model_pricing
                    break
        
        if not pricing:
            # Default pricing if model not found
            pricing = {"input": 0.001, "output": 0.002}
        
        # Calculate cost (pricing is per 1K tokens)
        input_cost = (input_tokens / 1000.0) * pricing["input"]
        output_cost = (output_tokens / 1000.0) * pricing["output"]
        
        return input_cost + output_cost
    
    async def generate(self, prompt: str) -> Dict[str, Any]:
        """
        Generate response with telemetry tracking.
        
        Args:
            prompt: Input prompt
            
        Returns:
            Response dict with generated_text
        """
        start_time = time.time()
        
        # Estimate input tokens
        input_tokens = self._estimate_tokens(prompt)
        
        # Create span for this LLM call
        span_attributes = {
            "llm.provider": self.provider,
            "llm.model": self.model,
            "llm.prompt_length": len(prompt),
            "llm.input_tokens": input_tokens,
        }
        
        with telemetry.trace_span(f"llm.{self.provider}.generate", span_attributes) as span:
            try:
                # Call underlying adapter
                result = await self.adapter.generate(prompt)
                
                # Extract generated text
                generated_text = result.get("generated_text", "")
                success = not generated_text.startswith("Error:")
                
                # Estimate output tokens
                output_tokens = self._estimate_tokens(generated_text)
                
                # Calculate cost
                cost = self._calculate_cost(input_tokens, output_tokens) if success else 0.0
                
                # Update span attributes
                if span:
                    span.set_attribute("llm.output_tokens", output_tokens)
                    span.set_attribute("llm.total_tokens", input_tokens + output_tokens)
                    span.set_attribute("llm.cost_usd", cost)
                    span.set_attribute("llm.success", success)
                
                # Record metrics
                duration_ms = (time.time() - start_time) * 1000
                telemetry.record_llm_request(
                    provider=self.provider,
                    model=self.model,
                    duration_ms=duration_ms,
                    success=success,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    cost=cost
                )
                
                # Log the request
                logger.info(
                    f"LLM request completed: {self.provider}/{self.model}",
                    extra={
                        "provider": self.provider,
                        "model": self.model,
                        "duration_ms": duration_ms,
                        "input_tokens": input_tokens,
                        "output_tokens": output_tokens,
                        "cost_usd": cost,
                        "success": success,
                    }
                )
                
                return result
                
            except Exception as e:
                # Record error
                duration_ms = (time.time() - start_time) * 1000
                telemetry.record_llm_request(
                    provider=self.provider,
                    model=self.model,
                    duration_ms=duration_ms,
                    success=False
                )
                telemetry.record_error("llm_error", provider=self.provider)
                
                logger.error(
                    f"LLM request failed: {self.provider}/{self.model}",
                    extra={
                        "provider": self.provider,
                        "model": self.model,
                        "duration_ms": duration_ms,
                        "error": str(e),
                    },
                    exc_info=True
                )
                
                raise
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get metrics from underlying adapter if available."""
        if hasattr(self.adapter, "get_metrics"):
            return self.adapter.get_metrics()
        return {}
    
    async def close(self):
        """Clean up resources."""
        if hasattr(self.adapter, "close"):
            await self.adapter.close()


def wrap_llm_adapter_with_telemetry(adapter, provider: str, model: str):
    """
    Wrap an LLM adapter with telemetry tracking.
    
    Args:
        adapter: Base LLM adapter
        provider: Provider name
        model: Model name
        
    Returns:
        TelemetryLLMWrapper instance
    """
    return TelemetryLLMWrapper(adapter, provider, model)