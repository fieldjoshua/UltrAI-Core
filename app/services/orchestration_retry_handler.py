"""Enhanced retry handler specifically for orchestration service with rate limit detection.

This module provides intelligent retry logic with exponential backoff specifically
tailored for LLM API calls, including rate limit detection and provider-specific handling.
"""

import asyncio
import logging
import re
import time
from typing import Any, Callable, Dict, Optional, Tuple

from app.config import Config
from app.utils.retry_handler import RetryConfig, RetryHandler

logger = logging.getLogger(__name__)


class OrchestrationRetryHandler:
    """Specialized retry handler for orchestration with rate limit detection."""

    # Rate limit patterns for different providers
    RATE_LIMIT_PATTERNS = {
        "openai": [
            r"rate.?limit",
            r"429",
            r"too many requests",
            r"quota exceeded",
            r"rate_limit_exceeded",
        ],
        "anthropic": [
            r"rate.?limit", 
            r"429",
            r"too many requests",
            r"RateLimitError",
            r"quota exceeded",
        ],
        "google": [
            r"quota.?exceed",
            r"rate.?limit",
            r"429",
            r"RESOURCE_EXHAUSTED",
        ],
        "huggingface": [
            r"rate.?limit",
            r"too many requests", 
            r"429",
            r"503.*loading",  # Model loading
        ],
    }

    def __init__(self):
        """Initialize retry handler with configuration from environment."""
        self.max_attempts = Config.MAX_RETRY_ATTEMPTS
        self.initial_delay = Config.RETRY_INITIAL_DELAY
        self.max_delay = Config.RETRY_MAX_DELAY
        self.exponential_base = Config.RETRY_EXPONENTIAL_BASE
        self.rate_limit_detection = Config.RATE_LIMIT_DETECTION_ENABLED
        self.rate_limit_retry = Config.RATE_LIMIT_RETRY_ENABLED

        # Create retry handler
        self.retry_config = RetryConfig(
            max_attempts=self.max_attempts,
            initial_delay=self.initial_delay,
            max_delay=self.max_delay,
            exponential_base=self.exponential_base,
            jitter=True,
            retry_on=(Exception,),
            exclude=(ValueError, KeyError, TypeError),  # Don't retry on programming errors
        )
        self.retry_handler = RetryHandler(self.retry_config)

    def detect_rate_limit(self, error_message: str, provider: str) -> bool:
        """Detect if error is a rate limit error based on provider patterns."""
        if not self.rate_limit_detection:
            return False

        error_lower = str(error_message).lower()
        patterns = self.RATE_LIMIT_PATTERNS.get(provider, [])
        
        for pattern in patterns:
            if re.search(pattern, error_lower, re.IGNORECASE):
                logger.info(f"Rate limit detected for {provider}: {error_message}")
                return True
        
        return False

    def calculate_rate_limit_delay(self, attempt: int, provider: str) -> float:
        """Calculate delay for rate-limited request with provider-specific logic."""
        base_delay = self.initial_delay * (self.exponential_base ** attempt)
        
        # Provider-specific delays
        provider_multipliers = {
            "openai": 1.5,      # OpenAI tends to need longer waits
            "anthropic": 1.2,   # Anthropic moderate waits
            "google": 1.0,      # Google standard waits
            "huggingface": 2.0, # HuggingFace may need model loading time
        }
        
        multiplier = provider_multipliers.get(provider, 1.0)
        delay = min(base_delay * multiplier, self.max_delay)
        
        # Add jitter to prevent thundering herd
        if delay > 0:
            jitter = delay * 0.1 * (0.5 - asyncio.get_event_loop().time() % 1)
            delay += jitter
            
        return max(0, delay)

    async def execute_with_retry(
        self,
        func: Callable,
        provider: str,
        model: str,
        *args,
        **kwargs
    ) -> Tuple[bool, Any]:
        """Execute function with intelligent retry handling.
        
        Returns:
            Tuple of (success, result/error)
        """
        last_error = None
        
        for attempt in range(self.max_attempts):
            try:
                # Execute the function
                result = await func(*args, **kwargs)
                
                # Check if result contains rate limit error
                if isinstance(result, dict):
                    error_text = result.get("error", "") or result.get("generated_text", "")
                    if self.detect_rate_limit(error_text, provider):
                        if not self.rate_limit_retry:
                            return False, {"error": "Rate limited", "provider": provider}
                        
                        # Calculate delay and retry
                        delay = self.calculate_rate_limit_delay(attempt, provider)
                        logger.warning(
                            f"Rate limit detected for {model} ({provider}), "
                            f"attempt {attempt + 1}/{self.max_attempts}, "
                            f"waiting {delay:.1f}s"
                        )
                        await asyncio.sleep(delay)
                        continue
                
                # Success!
                if attempt > 0:
                    logger.info(f"Retry successful for {model} after {attempt} attempts")
                
                return True, result
                
            except asyncio.TimeoutError:
                last_error = "Timeout exceeded"
                logger.warning(f"Timeout for {model}, attempt {attempt + 1}/{self.max_attempts}")
                
                if attempt < self.max_attempts - 1:
                    delay = self.calculate_rate_limit_delay(attempt, provider)
                    await asyncio.sleep(delay)
                    
            except Exception as e:
                last_error = str(e)
                error_str = str(e)
                
                # Check if it's a rate limit error
                if self.detect_rate_limit(error_str, provider):
                    if not self.rate_limit_retry:
                        return False, {"error": "Rate limited", "provider": provider}
                    
                    delay = self.calculate_rate_limit_delay(attempt, provider)
                    logger.warning(
                        f"Rate limit exception for {model} ({provider}), "
                        f"attempt {attempt + 1}/{self.max_attempts}, "
                        f"waiting {delay:.1f}s"
                    )
                    
                    if attempt < self.max_attempts - 1:
                        await asyncio.sleep(delay)
                        continue
                
                # For non-rate-limit errors, use standard retry delay
                if attempt < self.max_attempts - 1:
                    delay = self.initial_delay * (self.exponential_base ** attempt)
                    logger.warning(
                        f"Error for {model}: {error_str}, "
                        f"attempt {attempt + 1}/{self.max_attempts}, "
                        f"retrying in {delay:.1f}s"
                    )
                    await asyncio.sleep(delay)
        
        # All attempts failed
        logger.error(f"All retry attempts failed for {model}: {last_error}")
        return False, {"error": f"Failed after {self.max_attempts} attempts: {last_error}"}

    async def execute_with_timeout(
        self,
        func: Callable,
        timeout: float,
        provider: str,
        model: str,
        *args,
        **kwargs
    ) -> Tuple[bool, Any]:
        """Execute function with timeout and retry handling."""
        try:
            # Wrap function with timeout
            async def wrapped():
                return await asyncio.wait_for(
                    self.execute_with_retry(func, provider, model, *args, **kwargs),
                    timeout=timeout
                )
            
            return await wrapped()
            
        except asyncio.TimeoutError:
            logger.error(f"Overall timeout ({timeout}s) exceeded for {model}")
            return False, {"error": f"Timeout exceeded ({timeout}s)"}