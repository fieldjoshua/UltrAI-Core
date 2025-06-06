"""
Rate Limiter Service

This service manages API rate limits with exponential backoff and dynamic adjustment.
"""

import asyncio
import time
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class RateLimit:
    """Rate limit configuration for an API endpoint."""

    requests_per_minute: int
    burst_limit: int
    current_requests: int = 0
    last_reset: datetime = datetime.now()
    backoff_factor: float = 1.0


class RateLimiter:
    """
    Service for managing API rate limits with exponential backoff.
    """

    def __init__(self):
        self._limits: Dict[str, RateLimit] = {}
        self._locks: Dict[str, asyncio.Lock] = {}
        self._backoff_times: Dict[str, float] = {}

    def register_endpoint(
        self, endpoint: str, requests_per_minute: int, burst_limit: Optional[int] = None
    ) -> None:
        """
        Register a new endpoint with its rate limits.

        Args:
            endpoint: The API endpoint identifier
            requests_per_minute: Maximum requests per minute
            burst_limit: Optional burst limit for short periods
        """
        self._limits[endpoint] = RateLimit(
            requests_per_minute=requests_per_minute,
            burst_limit=burst_limit or requests_per_minute,
        )
        self._locks[endpoint] = asyncio.Lock()
        self._backoff_times[endpoint] = 0.0

    async def acquire(self, endpoint: str) -> None:
        """
        Acquire a rate limit token for the endpoint.

        Args:
            endpoint: The API endpoint identifier

        Raises:
            ValueError: If endpoint is not registered
        """
        if endpoint not in self._limits:
            raise ValueError(f"Endpoint {endpoint} not registered")

        async with self._locks[endpoint]:
            limit = self._limits[endpoint]

            # Reset counter if minute has passed
            if datetime.now() - limit.last_reset > timedelta(minutes=1):
                limit.current_requests = 0
                limit.last_reset = datetime.now()
                limit.backoff_factor = 1.0

            # Check if we're over the limit
            if limit.current_requests >= limit.requests_per_minute:
                # Calculate backoff time
                backoff_time = limit.backoff_factor * 60 / limit.requests_per_minute
                limit.backoff_factor *= 2  # Exponential backoff
                await asyncio.sleep(backoff_time)
                return await self.acquire(endpoint)

            # Increment request counter
            limit.current_requests += 1

    async def release(self, endpoint: str, success: bool = True) -> None:
        """
        Release a rate limit token and adjust backoff based on success.

        Args:
            endpoint: The API endpoint identifier
            success: Whether the request was successful
        """
        if endpoint not in self._limits:
            return

        async with self._locks[endpoint]:
            limit = self._limits[endpoint]
            if success:
                # Reduce backoff on success
                limit.backoff_factor = max(1.0, limit.backoff_factor * 0.5)
            else:
                # Increase backoff on failure
                limit.backoff_factor *= 2

    def get_endpoint_stats(self, endpoint: str) -> Dict[str, Any]:
        """
        Get current statistics for an endpoint.

        Args:
            endpoint: The API endpoint identifier

        Returns:
            Dict[str, Any]: Current rate limit statistics
        """
        if endpoint not in self._limits:
            return {}

        limit = self._limits[endpoint]
        return {
            "requests_per_minute": limit.requests_per_minute,
            "current_requests": limit.current_requests,
            "backoff_factor": limit.backoff_factor,
            "time_until_reset": (
                timedelta(minutes=1) - (datetime.now() - limit.last_reset)
            ).total_seconds(),
        }
