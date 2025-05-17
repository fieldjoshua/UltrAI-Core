"""
ParallelOrchestrator module for advanced parallel orchestration.

This module provides an advanced implementation of the BaseOrchestrator that
optimizes for parallel execution with adaptive task allocation. It can dynamically
prioritize providers based on their performance characteristics.
"""

import asyncio
import logging
import time
from typing import Any, Dict, List, Optional, Set, Tuple

from src.orchestration.base_orchestrator import BaseOrchestrator
from src.orchestration.simple_orchestrator import OrchestratorResponse

logger = logging.getLogger(__name__)


class ParallelOrchestrator(BaseOrchestrator):
    """
    Advanced orchestrator that implements parallel processing strategies:
    1. Dynamic provider prioritization based on performance
    2. Adaptive concurrency control for optimal resource utilization
    3. Graceful degradation under system pressure
    4. Progressive response aggregation as results arrive

    This implementation is optimized for high-throughput scenarios where
    multiple LLM requests need to be processed efficiently.
    """

    def __init__(
        self,
        max_retries: int = 3,
        timeout_seconds: int = 30,
        max_parallel_providers: int = 0,  # 0 means no limit
        use_early_stopping: bool = True,
        min_responses_needed: int = 1,
    ):
        """
        Initialize the parallel orchestrator.

        Args:
            max_retries: Maximum number of retries for failed requests
            timeout_seconds: Timeout for LLM requests in seconds
            max_parallel_providers: Maximum number of providers to use in parallel (0 = no limit)
            use_early_stopping: Whether to stop processing when sufficient quality responses are received
            min_responses_needed: Minimum number of successful responses needed before synthesis
        """
        super().__init__(
            max_retries=max_retries,
            parallel_requests=True,  # Always use parallel requests
            timeout_seconds=timeout_seconds,
        )
        self.max_parallel_providers = max_parallel_providers
        self.use_early_stopping = use_early_stopping
        self.min_responses_needed = min_responses_needed
        self.provider_performance: Dict[str, Dict[str, float]] = {}
        self.logger = logging.getLogger("orchestrator.parallel")

    def _update_provider_performance(
        self, provider_id: str, latency: float, success: bool
    ) -> None:
        """
        Update the performance metrics for a provider.

        Args:
            provider_id: The provider ID
            latency: Request latency in seconds
            success: Whether the request was successful
        """
        if provider_id not in self.provider_performance:
            self.provider_performance[provider_id] = {
                "avg_latency": latency,
                "success_rate": 1.0 if success else 0.0,
                "request_count": 1,
            }
            return

        # Update existing metrics with exponential moving average
        perf = self.provider_performance[provider_id]
        count = perf["request_count"]
        alpha = 1.0 / (count + 1)  # Weight for the new sample

        perf["avg_latency"] = (1 - alpha) * perf["avg_latency"] + alpha * latency
        perf["success_rate"] = (1 - alpha) * perf["success_rate"] + alpha * (
            1.0 if success else 0.0
        )
        perf["request_count"] += 1

    def _sort_providers_by_performance(self, provider_ids: List[str]) -> List[str]:
        """
        Sort providers by their performance (prioritizing fast, reliable providers).

        Args:
            provider_ids: List of provider IDs to sort

        Returns:
            Sorted list of provider IDs
        """
        # For providers we have performance data on, sort by a composite score
        # (normalized success rate / normalized latency)
        providers_with_perf = []
        providers_without_perf = []

        for pid in provider_ids:
            if pid in self.provider_performance:
                providers_with_perf.append(pid)
            else:
                providers_without_perf.append(pid)

        # If we don't have data for any providers, return the original list
        if not providers_with_perf:
            return provider_ids

        # Calculate scores
        scores = {}
        max_latency = max(
            self.provider_performance[pid]["avg_latency"] for pid in providers_with_perf
        )

        for pid in providers_with_perf:
            perf = self.provider_performance[pid]
            # Normalize latency (higher is better)
            norm_latency = (
                1.0 - (perf["avg_latency"] / max_latency) if max_latency > 0 else 0.5
            )
            # Combined score (higher is better)
            scores[pid] = perf["success_rate"] * norm_latency

        # Sort providers with performance data by descending score
        sorted_providers = sorted(
            providers_with_perf, key=lambda pid: scores[pid], reverse=True
        )

        # Add providers without performance data at the end
        return sorted_providers + providers_without_perf

    async def _process_with_early_stopping(
        self, prompt: str, provider_ids: List[str], **options
    ) -> Dict[str, Dict[str, Any]]:
        """
        Process providers in priority order with early stopping.

        Args:
            prompt: The prompt to process
            provider_ids: Ordered list of provider IDs to use
            **options: Additional processing options

        Returns:
            Dictionary of provider responses
        """
        responses: Dict[str, Dict[str, Any]] = {}
        successful_count = 0
        max_providers = (
            self.max_parallel_providers
            if self.max_parallel_providers > 0
            else len(provider_ids)
        )

        # Sort providers by performance
        sorted_provider_ids = self._sort_providers_by_performance(provider_ids)
        active_providers: Set[str] = set()
        remaining_providers = sorted_provider_ids.copy()

        # Process providers in batches, stopping early if we have enough successful responses
        while remaining_providers and len(active_providers) < max_providers:
            # Fill the active set up to max_providers
            while remaining_providers and len(active_providers) < max_providers:
                pid = remaining_providers.pop(0)
                active_providers.add(pid)

            # Create tasks for active providers
            tasks = {}
            for pid in active_providers:
                task = asyncio.create_task(
                    self.send_request_to_provider(pid, prompt, **options)
                )
                tasks[pid] = task

            # Wait for any task to complete
            done, pending = await asyncio.wait(
                tasks.values(), return_when=asyncio.FIRST_COMPLETED
            )

            # Process completed tasks
            for task in done:
                # Find the provider ID for this task
                pid = next(pid for pid, t in tasks.items() if t == task)
                active_providers.remove(pid)

                try:
                    response, metadata = await task
                    latency = metadata.get("latency", 0.0)

                    # Update performance metrics
                    self._update_provider_performance(pid, latency, True)

                    responses[pid] = {
                        "success": True,
                        "response": response,
                        "metadata": metadata,
                    }
                    successful_count += 1

                    self.logger.info(
                        f"Received successful response from provider '{pid}'"
                    )

                    # Check if we have enough successful responses and early stopping is enabled
                    if (
                        self.use_early_stopping
                        and successful_count >= self.min_responses_needed
                    ):
                        # Cancel any pending tasks
                        for p_task in pending:
                            p_task.cancel()

                        # Add failure entries for the canceled providers
                        for p_pid in [pid for pid, t in tasks.items() if t in pending]:
                            responses[p_pid] = {
                                "success": False,
                                "error": "Canceled due to early stopping",
                                "error_type": "EarlyStopping",
                                "timestamp": time.time(),
                            }

                        self.logger.info(
                            f"Early stopping after {successful_count} successful responses"
                        )
                        return responses

                except Exception as e:
                    # Update performance metrics
                    self._update_provider_performance(pid, self.timeout_seconds, False)

                    responses[pid] = {
                        "success": False,
                        "error": str(e),
                        "error_type": type(e).__name__,
                        "timestamp": time.time(),
                    }

                    self.logger.warning(f"Request to provider '{pid}' failed: {e}")

        # Wait for any remaining tasks to complete
        while active_providers:
            # Wait for any task to complete
            done, pending = await asyncio.wait(
                [tasks[pid] for pid in active_providers],
                return_when=asyncio.FIRST_COMPLETED,
            )

            # Process completed tasks
            for task in done:
                # Find the provider ID for this task
                pid = next(pid for pid, t in tasks.items() if t == task)
                active_providers.remove(pid)

                try:
                    response, metadata = await task
                    latency = metadata.get("latency", 0.0)

                    # Update performance metrics
                    self._update_provider_performance(pid, latency, True)

                    responses[pid] = {
                        "success": True,
                        "response": response,
                        "metadata": metadata,
                    }
                    successful_count += 1

                    self.logger.info(
                        f"Received successful response from provider '{pid}'"
                    )
                except Exception as e:
                    # Update performance metrics
                    self._update_provider_performance(pid, self.timeout_seconds, False)

                    responses[pid] = {
                        "success": False,
                        "error": str(e),
                        "error_type": type(e).__name__,
                        "timestamp": time.time(),
                    }

                    self.logger.warning(f"Request to provider '{pid}' failed: {e}")

        return responses

    async def _select_best_response(
        self, responses: Dict[str, Dict[str, Any]]
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Select the best response from multiple providers.

        Args:
            responses: Dictionary of provider responses

        Returns:
            Tuple of (provider_id, response_info)
        """
        # Filter for successful responses
        successful = {
            pid: info for pid, info in responses.items() if info.get("success", False)
        }

        if not successful:
            raise ValueError("No successful responses to select from")

        # If only one successful response, return it
        if len(successful) == 1:
            pid = list(successful.keys())[0]
            return pid, successful[pid]

        # If we have performance data, select the best provider based on:
        # 1. Success rate (historical reliability)
        # 2. Response latency (speed)
        candidates = list(successful.keys())

        # If we have complete performance data for all candidates
        if all(pid in self.provider_performance for pid in candidates):
            # Select the provider with the highest success rate
            sorted_candidates = sorted(
                candidates,
                key=lambda pid: self.provider_performance[pid]["success_rate"],
                reverse=True,
            )

            # Take the top 3 most reliable providers
            top_reliable = sorted_candidates[: min(3, len(sorted_candidates))]

            # From those, select the one with lowest latency
            best_pid = min(
                top_reliable,
                key=lambda pid: self.provider_performance[pid]["avg_latency"],
            )

            return best_pid, successful[best_pid]

        # If we don't have complete performance data, use the current latency
        best_pid = min(
            candidates,
            key=lambda pid: successful[pid]
            .get("metadata", {})
            .get("latency", float("inf")),
        )

        return best_pid, successful[best_pid]

    async def process(
        self, prompt: str, provider_ids: Optional[List[str]] = None, **options
    ) -> Dict[str, Any]:
        """
        Process a prompt using optimized parallel orchestration.

        Args:
            prompt: The prompt to process
            provider_ids: Optional list of provider IDs to use (defaults to all registered)
            **options: Additional processing options

        Returns:
            Dictionary with processing results
        """
        start_time = asyncio.get_event_loop().time()

        # Get provider IDs to use
        if provider_ids is None or not provider_ids:
            provider_ids = list(self.providers.keys())

        # Validate provider IDs
        provider_ids = [pid for pid in provider_ids if pid in self.providers]

        # Check if we have any valid providers
        if not provider_ids:
            error_msg = "No valid providers specified"
            self.logger.error(error_msg)
            return {
                "error": error_msg,
                "responses": [],
                "best_response": None,
                "metadata": {
                    "processing_time": asyncio.get_event_loop().time() - start_time,
                    "providers_requested": 0,
                    "providers_successful": 0,
                    "early_stopping_triggered": False,
                },
            }

        # Process providers with optimized parallel execution
        self.logger.info(f"Processing prompt with up to {len(provider_ids)} providers")
        early_stopping_active = (
            self.use_early_stopping and self.min_responses_needed < len(provider_ids)
        )

        responses = await self._process_with_early_stopping(
            prompt, provider_ids, **options
        )

        # Count successful responses
        successful_responses = {
            pid: info for pid, info in responses.items() if info.get("success", False)
        }

        # If no successful responses, return error
        if not successful_responses:
            error_msg = "No successful responses from any provider"
            self.logger.error(error_msg)
            return {
                "error": error_msg,
                "responses": [
                    {
                        "provider_id": pid,
                        "success": info.get("success", False),
                        "error": info.get("error", "Unknown error"),
                        "error_type": info.get("error_type", "Unknown"),
                    }
                    for pid, info in responses.items()
                ],
                "best_response": None,
                "metadata": {
                    "processing_time": asyncio.get_event_loop().time() - start_time,
                    "providers_requested": len(provider_ids),
                    "providers_successful": 0,
                    "early_stopping_triggered": any(
                        info.get("error_type") == "EarlyStopping"
                        for info in responses.values()
                    ),
                },
            }

        # Select the best response from successful providers
        try:
            best_provider_id, best_response = await self._select_best_response(
                responses
            )
            best_result = {
                "provider_id": best_provider_id,
                "response": best_response.get("response", ""),
                "metadata": best_response.get("metadata", {}),
            }
        except Exception as e:
            self.logger.error(f"Error selecting best response: {e}")
            best_result = None

        # Return consolidated results
        return {
            "responses": [
                {
                    "provider_id": pid,
                    "success": info.get("success", False),
                    "response": (
                        info.get("response", "") if info.get("success", False) else None
                    ),
                    "error": (
                        info.get("error") if not info.get("success", False) else None
                    ),
                    "metadata": (
                        info.get("metadata", {}) if info.get("success", False) else None
                    ),
                }
                for pid, info in responses.items()
            ],
            "best_response": best_result,
            "metadata": {
                "processing_time": asyncio.get_event_loop().time() - start_time,
                "providers_requested": len(provider_ids),
                "providers_successful": len(successful_responses),
                "early_stopping_triggered": any(
                    info.get("error_type") == "EarlyStopping"
                    for info in responses.values()
                ),
            },
        }
