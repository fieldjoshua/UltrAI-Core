"""
LLM Fallback Service.

This module provides a fallback service for LLM calls, implementing retry mechanisms,
circuit breakers, caching, and provider failover strategies.
"""

import asyncio
import logging
import time
import random
from typing import Dict, List, Any, Optional, Tuple, Callable, Set, AsyncGenerator

from backend.utils.logging import get_logger
from backend.services.cache_service import cache_service
from src.models.circuit_breaker import CircuitBreaker, CircuitBreakerRegistry

# Set up logger
logger = get_logger("llm_fallback", "logs/llm_fallback.log")

# Create a global circuit breaker registry
circuit_registry = CircuitBreakerRegistry()

# Cache keys
CACHE_PREFIX = "llm:fallback:"
CACHE_TTL_SECONDS = 3600  # 1 hour default TTL for fallback responses


class LLMFallbackService:
    """
    LLM Fallback Service for handling LLM failures with fallback strategies.
    
    This service provides:
    1. Provider failover
    2. Circuit breaker pattern
    3. Retry mechanisms
    4. Cache-based fallbacks
    5. Mock fallbacks as a last resort
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the LLM Fallback Service.
        
        Args:
            config: Optional configuration with settings
        """
        self.config = config or {}
        
        # Fallback configuration
        self.max_retries = self.config.get("MAX_RETRIES", 3)
        self.retry_delay_base = self.config.get("RETRY_DELAY_BASE", 2.0)
        self.retry_delay_max = self.config.get("RETRY_DELAY_MAX", 10.0)
        self.circuit_failure_threshold = self.config.get("CIRCUIT_FAILURE_THRESHOLD", 5)
        self.circuit_recovery_timeout = self.config.get("CIRCUIT_RECOVERY_TIMEOUT", 60)
        self.enable_cache_fallback = self.config.get("ENABLE_CACHE_FALLBACK", True)
        self.cache_ttl = self.config.get("CACHE_TTL", CACHE_TTL_SECONDS)
        self.enable_mock_fallback = self.config.get("ENABLE_MOCK_FALLBACK", True)
        
        # LLM provider priority configuration
        self.provider_priority = self.config.get("PROVIDER_PRIORITY", [
            "openai", "anthropic", "gemini", "mistral", "docker_modelrunner"
        ])
        
        # Provider to model mapping
        self.provider_model_mapping = self.config.get("PROVIDER_MODEL_MAPPING", {
            "openai": {
                "gpt4o": "gpt-4o",
                "gpt4turbo": "gpt-4-turbo",
                "gpt4": "gpt-4",
                "gpt35turbo": "gpt-3.5-turbo"
            },
            "anthropic": {
                "claude37": "claude-3-haiku-20240307",
                "claude3opus": "claude-3-opus-20240229",
                "claude3sonnet": "claude-3-sonnet-20240229",
                "claude3haiku": "claude-3-haiku-20240307"
            },
            "gemini": {
                "gemini15": "gemini-1.5-pro",
                "gemini10": "gemini-pro"
            },
            "mistral": {
                "mistral": "mistral-large-latest",
                "mixtral": "mixtral-8x7b-32768"
            },
            "docker_modelrunner": {
                "llama3": "llama3:8b",
                "phi3": "phi3:mini"
            }
        })
        
        # Initialize provider availability (assume all available initially)
        self.provider_availability = {provider: True for provider in self.provider_priority}
        
        # Provider API key environment variables
        self.provider_api_keys = {
            "openai": "OPENAI_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY",
            "gemini": "GOOGLE_API_KEY",
            "mistral": "MISTRAL_API_KEY",
            "cohere": "COHERE_API_KEY"
        }
        
        # Create circuit breakers for each provider
        for provider in self.provider_priority:
            circuit_registry.get_or_create(
                f"llm:{provider}",
                failure_threshold=self.circuit_failure_threshold,
                recovery_timeout=self.circuit_recovery_timeout
            )
            
        logger.info(f"LLM Fallback Service initialized with {len(self.provider_priority)} providers")
    
    def _get_cache_key(self, prompt: str, model: str, options: Dict[str, Any]) -> str:
        """
        Generate a cache key for a given prompt and model.
        
        Args:
            prompt: The prompt to generate a response for
            model: The model to use
            options: Additional options that affect the response
            
        Returns:
            A cache key string
        """
        import hashlib
        import json
        
        # Normalize and sort options for consistent hashing
        normalized_options = {k: str(v) for k, v in sorted(options.items()) 
                             if k not in ['stream', 'timeout']}
        
        # Create hash from prompt and options
        data_to_hash = f"{prompt}:{model}:{json.dumps(normalized_options)}"
        hash_key = hashlib.sha256(data_to_hash.encode()).hexdigest()
        
        return f"{CACHE_PREFIX}{model}:{hash_key}"
    
    def _get_provider_for_model(self, model: str) -> List[Tuple[str, str]]:
        """
        Get potential providers for a given model ID with their native model names.
        
        Args:
            model: The model ID to look up
            
        Returns:
            List of (provider, native_model_name) tuples in priority order
        """
        providers = []
        
        # Check each provider for model mapping
        for provider in self.provider_priority:
            if provider in self.provider_model_mapping:
                mapping = self.provider_model_mapping[provider]
                if model in mapping:
                    providers.append((provider, mapping[model]))
        
        # If no mapping found, try some default fallbacks
        if not providers:
            # Default model fallbacks if no direct mapping exists
            if "gpt" in model:
                providers.append(("openai", "gpt-4-turbo"))
            elif "claude" in model:
                providers.append(("anthropic", "claude-3-haiku-20240307"))
            elif "gemini" in model:
                providers.append(("gemini", "gemini-pro"))
            elif "mistral" in model or "mixtral" in model:
                providers.append(("mistral", "mistral-large-latest"))
            elif "llama" in model:
                providers.append(("docker_modelrunner", "llama3:8b"))
            else:
                # If all else fails, try each provider with their default model
                providers.extend([
                    ("openai", "gpt-4-turbo"),
                    ("anthropic", "claude-3-haiku-20240307"),
                    ("gemini", "gemini-pro"),
                    ("mistral", "mistral-large-latest"),
                    ("docker_modelrunner", "phi3:mini")
                ])
        
        return providers
    
    async def _exponential_backoff(self, attempt: int) -> None:
        """
        Wait with exponential backoff.
        
        Args:
            attempt: The current attempt number (0-based)
        """
        delay = min(
            self.retry_delay_base * (2 ** attempt) + random.uniform(0, 1),
            self.retry_delay_max
        )
        await asyncio.sleep(delay)
    
    async def _try_get_from_cache(self, prompt: str, model: str, options: Dict[str, Any]) -> Optional[str]:
        """
        Try to get a response from the cache.
        
        Args:
            prompt: The prompt to generate a response for
            model: The model to use
            options: Additional options
            
        Returns:
            Cached response if available, None otherwise
        """
        if not self.enable_cache_fallback:
            return None
            
        cache_key = self._get_cache_key(prompt, model, options)
        cached_response = await cache_service.get_json(CACHE_PREFIX, {"key": cache_key})
        
        if cached_response and "response" in cached_response:
            logger.info(f"Using cached response for model {model}")
            return cached_response["response"]
            
        return None
    
    async def _save_to_cache(self, prompt: str, model: str, options: Dict[str, Any], response: str) -> None:
        """
        Save a response to the cache.
        
        Args:
            prompt: The prompt that was used
            model: The model that was used
            options: Additional options
            response: The response to cache
        """
        if not self.enable_cache_fallback:
            return
            
        cache_key = self._get_cache_key(prompt, model, options)
        cache_data = {
            "response": response,
            "timestamp": time.time(),
            "model": model
        }
        
        await cache_service.set_json(CACHE_PREFIX, {"key": cache_key}, cache_data, ttl=self.cache_ttl)
    
    async def _generate_mock_response(self, prompt: str, model: str) -> str:
        """
        Generate a mock response for a given prompt and model.
        
        Args:
            prompt: The prompt to generate a response for
            model: The model to mock
            
        Returns:
            A mock response
        """
        # Try to use the mock LLM service if available
        try:
            from backend.services.mock_llm_service import MockLLMService
            
            mock_service = MockLLMService()
            response = await mock_service._generate_model_response(model, prompt)
            
            # Add clear indication this is a fallback response
            fallback_notice = (
                "\n\n[NOTE: This response was generated by a fallback mock service "
                "because the requested model or service was unavailable. "
                "The response may not reflect the capabilities of the requested model.]"
            )
            
            return response + fallback_notice
        except ImportError:
            # If mock service is not available, generate a very basic response
            word_count = min(len(prompt.split()), 100)  # Use prompt length to determine response length
            return (
                f"[Fallback Mock Response for {model}]\n\n"
                f"I would provide a detailed response to your prompt about "
                f"{' '.join(prompt.split()[:5])}..., but the requested model or service "
                f"is currently unavailable. This is an automatically generated fallback response."
            )
    
    async def generate_with_fallback(
        self, 
        prompt: str, 
        model: str, 
        options: Dict[str, Any] = None,
        provider_client_factory: Optional[Callable] = None
    ) -> str:
        """
        Generate a response with fallback mechanisms.
        
        Args:
            prompt: The prompt to generate a response for
            model: The model to use
            options: Additional options
            provider_client_factory: Function to create provider clients
            
        Returns:
            The generated response, potentially from a fallback source
            
        Raises:
            Exception: If all fallback mechanisms fail
        """
        options = options or {}
        
        # First, check cache for an existing response
        cached_response = await self._try_get_from_cache(prompt, model, options)
        if cached_response:
            return cached_response
        
        # Get potential providers for this model
        model_providers = self._get_provider_for_model(model)
        
        # Try each provider
        last_error = None
        tried_providers = set()
        
        for provider_name, native_model in model_providers:
            # Skip if we've already tried this provider
            if provider_name in tried_providers:
                continue
                
            tried_providers.add(provider_name)
            
            # Check circuit breaker
            circuit = circuit_registry.get_or_create(f"llm:{provider_name}")
            if not circuit.allow_request():
                logger.warning(f"Circuit breaker open for provider {provider_name}, skipping")
                continue
            
            # Try with retries
            for attempt in range(self.max_retries):
                try:
                    if not provider_client_factory:
                        # Without a factory, we can't create a client
                        raise ValueError("No provider client factory available")
                    
                    # Create the client
                    client = provider_client_factory(provider_name)
                    
                    # Generate the response
                    response = await client.generate(
                        prompt=prompt,
                        model=native_model,
                        **options
                    )
                    
                    # Success - record it and cache the response
                    circuit.record_success()
                    await self._save_to_cache(prompt, model, options, response)
                    
                    return response
                except Exception as e:
                    last_error = e
                    logger.warning(
                        f"Error calling {provider_name} (attempt {attempt+1}/{self.max_retries}): {e}"
                    )
                    
                    # Only apply backoff if we're going to retry
                    if attempt < self.max_retries - 1:
                        await self._exponential_backoff(attempt)
            
            # All attempts failed for this provider
            logger.error(f"All attempts failed for provider {provider_name}")
            circuit.record_failure()
        
        # If we get here, all providers failed
        logger.error(f"All providers failed for model {model}")
        
        # Try mock fallback as last resort
        if self.enable_mock_fallback:
            logger.info(f"Using mock fallback for model {model}")
            return await self._generate_mock_response(prompt, model)
        
        # If mock fallback is disabled, reraise the last error
        raise last_error or RuntimeError(f"Failed to generate response for model {model}")
    
    async def stream_generate_with_fallback(
        self,
        prompt: str,
        model: str,
        options: Dict[str, Any] = None,
        provider_client_factory: Optional[Callable] = None
    ) -> AsyncGenerator[str, None]:
        """
        Stream-generate a response with fallback mechanisms.
        
        Args:
            prompt: The prompt to generate a response for
            model: The model to use
            options: Additional options
            provider_client_factory: Function to create provider clients
            
        Yields:
            Chunks of the generated response
            
        Note:
            When falling back to cached or mock responses, the entire response is
            yielded as a single chunk.
        """
        options = options or {}
        
        # First, check cache for an existing response
        cached_response = await self._try_get_from_cache(prompt, model, options)
        if cached_response:
            yield cached_response
            return
        
        # Get potential providers for this model
        model_providers = self._get_provider_for_model(model)
        
        # Try each provider
        last_error = None
        tried_providers = set()
        full_response = ""
        
        for provider_name, native_model in model_providers:
            # Skip if we've already tried this provider
            if provider_name in tried_providers:
                continue
                
            tried_providers.add(provider_name)
            
            # Check circuit breaker
            circuit = circuit_registry.get_or_create(f"llm:{provider_name}")
            if not circuit.allow_request():
                logger.warning(f"Circuit breaker open for provider {provider_name}, skipping")
                continue
            
            # Try with retries
            for attempt in range(self.max_retries):
                try:
                    if not provider_client_factory:
                        # Without a factory, we can't create a client
                        raise ValueError("No provider client factory available")
                    
                    # Create the client
                    client = provider_client_factory(provider_name)
                    
                    # Stream the response
                    async for chunk in client.stream_generate(
                        prompt=prompt,
                        model=native_model,
                        **options
                    ):
                        full_response += chunk
                        yield chunk
                    
                    # Success - record it and cache the response
                    circuit.record_success()
                    await self._save_to_cache(prompt, model, options, full_response)
                    
                    return
                except Exception as e:
                    last_error = e
                    logger.warning(
                        f"Error streaming from {provider_name} (attempt {attempt+1}/{self.max_retries}): {e}"
                    )
                    
                    # Only apply backoff if we're going to retry
                    if attempt < self.max_retries - 1:
                        await self._exponential_backoff(attempt)
            
            # All attempts failed for this provider
            logger.error(f"All streaming attempts failed for provider {provider_name}")
            circuit.record_failure()
        
        # If we get here, all providers failed
        logger.error(f"All providers failed for streaming model {model}")
        
        # Try mock fallback as last resort
        if self.enable_mock_fallback:
            logger.info(f"Using mock fallback for streaming model {model}")
            mock_response = await self._generate_mock_response(prompt, model)
            yield mock_response
            return
        
        # If mock fallback is disabled, reraise the last error
        raise last_error or RuntimeError(f"Failed to stream response for model {model}")
    
    def get_provider_status(self) -> Dict[str, Any]:
        """
        Get the status of all LLM providers.
        
        Returns:
            Dictionary with provider status information
        """
        status = {
            "providers": {},
            "circuits": circuit_registry.get_all_status()
        }
        
        # Add provider-specific status
        for provider in self.provider_priority:
            circuit_name = f"llm:{provider}"
            circuit = circuit_registry.get(circuit_name)
            
            if circuit:
                circuit_state = circuit.state.value
                failure_count = circuit.stats.failure_count
            else:
                circuit_state = "unknown"
                failure_count = 0
            
            status["providers"][provider] = {
                "available": self.provider_availability.get(provider, False),
                "circuit_state": circuit_state,
                "failure_count": failure_count,
                "priority": self.provider_priority.index(provider) if provider in self.provider_priority else -1
            }
        
        return status

    
# Create a global instance
llm_fallback_service = LLMFallbackService()