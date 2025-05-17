"""
Base Orchestrator Module.

This module provides the foundation for the iterative LLM orchestration system,
implementing core functionality for managing LLM providers, parallel request processing,
and response handling.
"""

import asyncio
import logging
import time
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from src.models.llm_adapter import LLMAdapter, create_adapter_async


class BaseOrchestrator(ABC):
    """
    Base orchestrator that handles core LLM coordination functionality.

    This class provides the foundation for the LLM orchestration system with:
    - LLM provider registration and management
    - Parallel LLM request processing
    - Error handling and retries
    - Mock mode support for development

    Subclasses should implement specific orchestration strategies and response synthesis.
    """

    def __init__(
        self,
        max_retries: int = 3,
        parallel_requests: bool = True,
        timeout_seconds: int = 30,
    ):
        """
        Initialize the base orchestrator.

        Args:
            max_retries: Maximum number of retries for failed requests
            parallel_requests: Whether to process LLM requests in parallel
            timeout_seconds: Timeout for LLM requests in seconds
        """
        self.providers: Dict[str, LLMAdapter] = {}
        self.provider_configs: Dict[str, Dict[str, Any]] = {}
        self.logger = logging.getLogger("orchestrator.base")
        self.max_retries = max_retries
        self.parallel_requests = parallel_requests
        self.timeout_seconds = timeout_seconds
        self.request_stats: Dict[str, Dict[str, Any]] = {}

    async def register_provider(
        self,
        provider_id: str,
        provider_type: str,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        **provider_options
    ) -> bool:
        """
        Register an LLM provider with the orchestrator.

        Args:
            provider_id: Unique identifier for this provider instance
            provider_type: Type of provider (openai, anthropic, etc.)
            api_key: API key for the provider
            model: Default model to use with this provider
            **provider_options: Additional provider-specific options

        Returns:
            True if registration was successful, False otherwise
        """
        try:
            # Store configuration for reference and potential reconnection
            self.provider_configs[provider_id] = {
                "provider_type": provider_type,
                "api_key": api_key,
                "model": model,
                **provider_options
            }

            # Create the provider adapter
            provider = await create_adapter_async(
                provider_type,
                api_key=api_key,
                model=model,
                **provider_options
            )

            self.providers[provider_id] = provider
            self.logger.info(f"Registered provider '{provider_id}' ({provider_type})")

            # Initialize stats for this provider
            self.request_stats[provider_id] = {
                "requests_total": 0,
                "requests_successful": 0,
                "total_latency": 0.0,
                "errors": {},
                "last_error": None,
                "last_request_time": None,
            }

            return True
        except Exception as e:
            self.logger.error(f"Failed to register provider '{provider_id}': {e}")
            return False

    def get_registered_providers(self) -> List[str]:
        """
        Get the list of registered provider IDs.

        Returns:
            List of provider IDs
        """
        return list(self.providers.keys())

    def get_provider_info(self, provider_id: str) -> Dict[str, Any]:
        """
        Get information about a specific provider.

        Args:
            provider_id: The provider ID

        Returns:
            Dictionary with provider information

        Raises:
            ValueError: If the provider is not registered
        """
        if provider_id not in self.providers:
            raise ValueError(f"Provider '{provider_id}' is not registered")

        provider = self.providers[provider_id]
        capabilities = provider.get_capabilities()
        stats = self.request_stats.get(provider_id, {})

        return {
            "provider_id": provider_id,
            "provider_type": provider.name,
            "capabilities": capabilities,
            "stats": stats,
            "config": {
                k: v for k, v in self.provider_configs[provider_id].items()
                if k \!= "api_key"  # Don't include the API key in the returned info
            }
        }

    async def check_provider_availability(self, provider_id: str) -> bool:
        """
        Check if a provider is available.

        Args:
            provider_id: The provider ID

        Returns:
            True if the provider is available, False otherwise
        """
        if provider_id not in self.providers:
            return False

        try:
            provider = self.providers[provider_id]
            return await provider.check_availability()
        except Exception as e:
            self.logger.warning(f"Provider '{provider_id}' availability check failed: {e}")
            return False

    async def get_available_providers(self) -> List[str]:
        """
        Get a list of all available providers.

        Returns:
            List of available provider IDs
        """
        available_providers = []
        availability_tasks = [
            self.check_provider_availability(provider_id)
            for provider_id in self.providers
        ]

        results = await asyncio.gather(*availability_tasks, return_exceptions=True)

        for i, provider_id in enumerate(self.providers):
            if isinstance(results[i], bool) and results[i]:
                available_providers.append(provider_id)

        return available_providers

    async def send_request_to_provider(
        self,
        provider_id: str,
        prompt: str,
        model: Optional[str] = None,
        **options
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Send a request to a specific provider with retry logic.

        Args:
            provider_id: The provider ID
            prompt: The prompt to send
            model: Optional model override
            **options: Additional request options

        Returns:
            Tuple of (response_text, metadata)

        Raises:
            ValueError: If the provider is not registered
            RuntimeError: If all retry attempts fail
        """
        if provider_id not in self.providers:
            raise ValueError(f"Provider '{provider_id}' is not registered")

        provider = self.providers[provider_id]
        request_options = options.copy()

        # Use specified model or fall back to the provider's default
        if model:
            request_options["model"] = model

        # Update request stats
        self.request_stats[provider_id]["requests_total"] += 1
        self.request_stats[provider_id]["last_request_time"] = time.time()

        # Try to send the request with retries
        for attempt in range(self.max_retries):
            try:
                start_time = time.time()

                # Add timeout to the request
                response = await asyncio.wait_for(
                    provider.generate(prompt, **request_options),
                    timeout=self.timeout_seconds
                )

                end_time = time.time()
                latency = end_time - start_time

                # Update successful request stats
                self.request_stats[provider_id]["requests_successful"] += 1
                self.request_stats[provider_id]["total_latency"] += latency

                # Return the response with metadata
                metadata = {
                    "provider_id": provider_id,
                    "provider_type": provider.name,
                    "latency": latency,
                    "timestamp": datetime.now().isoformat(),
                    "attempt": attempt + 1,
                }

                return response, metadata

            except asyncio.TimeoutError:
                error_type = "timeout"
                error_msg = f"Request timed out after {self.timeout_seconds} seconds"
                self.logger.warning(
                    f"Attempt {attempt + 1}/{self.max_retries} for provider '{provider_id}' "
                    f"timed out after {self.timeout_seconds} seconds"
                )
            except Exception as e:
                error_type = type(e).__name__
                error_msg = str(e)
                self.logger.warning(
                    f"Attempt {attempt + 1}/{self.max_retries} for provider '{provider_id}' "
                    f"failed: {error_type}: {error_msg}"
                )

            # Update error stats
            if error_type not in self.request_stats[provider_id]["errors"]:
                self.request_stats[provider_id]["errors"][error_type] = 0
            self.request_stats[provider_id]["errors"][error_type] += 1
            self.request_stats[provider_id]["last_error"] = {
                "type": error_type,
                "message": error_msg,
                "timestamp": datetime.now().isoformat(),
            }

            # Exponential backoff before retry
            if attempt < self.max_retries - 1:
                backoff_time = 0.5 * (2 ** attempt)  # 0.5, 1, 2, 4, 8, ...
                await asyncio.sleep(backoff_time)

        # If we get here, all retries have failed
        error_message = f"All {self.max_retries} attempts failed for provider '{provider_id}'"
        self.logger.error(error_message)
        raise RuntimeError(error_message)

    async def process_with_providers(
        self,
        prompt: str,
        provider_ids: Optional[List[str]] = None,
        model_override: Optional[Dict[str, str]] = None,
        **options
    ) -> Dict[str, Dict[str, Any]]:
        """
        Process a prompt with multiple providers in parallel.

        Args:
            prompt: The prompt to send
            provider_ids: List of provider IDs to use (defaults to all registered)
            model_override: Optional model overrides by provider ID
            **options: Additional request options for all providers

        Returns:
            Dictionary mapping provider IDs to their responses and metadata
        """
        # If no providers specified, use all registered providers
        if provider_ids is None:
            provider_ids = list(self.providers.keys())
        else:
            # Validate that specified providers exist
            for provider_id in provider_ids:
                if provider_id not in self.providers:
                    raise ValueError(f"Provider '{provider_id}' is not registered")

        if not provider_ids:
            self.logger.warning("No providers specified and none registered")
            return {}

        # Process requests in parallel or sequentially
        if self.parallel_requests:
            # Create tasks for all provider requests
            tasks = []
            for provider_id in provider_ids:
                # Get model override for this provider if specified
                model = None
                if model_override and provider_id in model_override:
                    model = model_override[provider_id]

                # Create task for this provider
                task = asyncio.create_task(
                    self.send_request_to_provider(
                        provider_id, prompt, model=model, **options
                    )
                )
                tasks.append((provider_id, task))

            # Wait for all tasks to complete
            results = {}
            for provider_id, task in tasks:
                try:
                    response, metadata = await task
                    results[provider_id] = {
                        "success": True,
                        "response": response,
                        "metadata": metadata,
                    }
                except Exception as e:
                    self.logger.error(f"Request to provider '{provider_id}' failed: {e}")
                    results[provider_id] = {
                        "success": False,
                        "error": str(e),
                        "error_type": type(e).__name__,
                        "timestamp": datetime.now().isoformat(),
                    }
        else:
            # Process requests sequentially
            results = {}
            for provider_id in provider_ids:
                # Get model override for this provider if specified
                model = None
                if model_override and provider_id in model_override:
                    model = model_override[provider_id]

                try:
                    response, metadata = await self.send_request_to_provider(
                        provider_id, prompt, model=model, **options
                    )
                    results[provider_id] = {
                        "success": True,
                        "response": response,
                        "metadata": metadata,
                    }
                except Exception as e:
                    self.logger.error(f"Request to provider '{provider_id}' failed: {e}")
                    results[provider_id] = {
                        "success": False,
                        "error": str(e),
                        "error_type": type(e).__name__,
                        "timestamp": datetime.now().isoformat(),
                    }

        return results

    async def fallback_chain(
        self,
        prompt: str,
        provider_sequence: List[str],
        **options
    ) -> Optional[Tuple[str, Dict[str, Any]]]:
        """
        Try providers in sequence until one succeeds.

        Args:
            prompt: The prompt to send
            provider_sequence: Ordered list of provider IDs to try
            **options: Additional request options

        Returns:
            Tuple of (response_text, metadata) or None if all fail
        """
        for provider_id in provider_sequence:
            if provider_id not in self.providers:
                self.logger.warning(f"Provider '{provider_id}' in fallback chain not registered, skipping")
                continue

            try:
                response, metadata = await self.send_request_to_provider(
                    provider_id, prompt, **options
                )
                # If we get here, the request succeeded
                return response, metadata
            except Exception as e:
                self.logger.warning(f"Fallback to provider '{provider_id}' failed: {e}")
                continue

        # If we get here, all providers failed
        self.logger.error(f"All providers in fallback chain failed: {provider_sequence}")
        return None

    @abstractmethod
    async def process(
        self,
        prompt: str,
        **options
    ) -> Dict[str, Any]:
        """
        Process a prompt and return results.

        This method should be implemented by subclasses to define the specific
        orchestration strategy and response synthesis approach.

        Args:
            prompt: The prompt to process
            **options: Additional processing options

        Returns:
            Dictionary with processing results
        """
        pass

    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the orchestrator's operations.

        Returns:
            Dictionary with orchestrator statistics
        """
        total_requests = sum(
            stats["requests_total"] for stats in self.request_stats.values()
        )
        successful_requests = sum(
            stats["requests_successful"] for stats in self.request_stats.values()
        )

        # Calculate success rate
        success_rate = 0.0
        if total_requests > 0:
            success_rate = successful_requests / total_requests

        # Aggregate error counts across providers
        error_counts = {}
        for provider_id, stats in self.request_stats.items():
            for error_type, count in stats.get("errors", {}).items():
                if error_type not in error_counts:
                    error_counts[error_type] = 0
                error_counts[error_type] += count

        return {
            "providers": {
                provider_id: {
                    "requests_total": stats["requests_total"],
                    "requests_successful": stats["requests_successful"],
                    "success_rate": (
                        stats["requests_successful"] / stats["requests_total"]
                        if stats["requests_total"] > 0 else 0.0
                    ),
                    "avg_latency": (
                        stats["total_latency"] / stats["requests_successful"]
                        if stats["requests_successful"] > 0 else 0.0
                    ),
                    "error_counts": stats.get("errors", {}),
                }
                for provider_id, stats in self.request_stats.items()
            },
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "success_rate": success_rate,
            "error_counts": error_counts,
        }
EOF < /dev/null
