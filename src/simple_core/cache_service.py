"""
Simple cache service for LLM responses

This module provides a basic in-memory cache for LLM responses
to avoid redundant API calls and improve performance.
"""

import asyncio
import logging
import time
from typing import Any, Dict, Optional, Union

logger = logging.getLogger(__name__)


class CacheService:
    """
    Simple in-memory cache for LLM responses

    Features:
    - Configurable TTL (time-to-live) for cache entries
    - Thread-safe access with asyncio locks
    - Optional size limit
    """

    def __init__(self, ttl_seconds: int = 3600, max_size: Optional[int] = 1000):
        """
        Initialize the cache service

        Args:
            ttl_seconds: Time-to-live in seconds for cache entries (default: 1 hour)
            max_size: Maximum number of entries in the cache (default: 1000, None for unlimited)
        """
        self.ttl_seconds = ttl_seconds
        self.max_size = max_size
        self.cache: Dict[str, Dict[str, Any]] = {}  # key -> (value, timestamp)
        self.lock = asyncio.Lock()

    async def get(self, key: str) -> Optional[Any]:
        """
        Get a value from the cache

        Args:
            key: Cache key

        Returns:
            Cached value if found and not expired, None otherwise
        """
        async with self.lock:
            if key not in self.cache:
                return None

            entry = self.cache[key]
            timestamp = entry["timestamp"]

            # Check if entry is expired
            if time.time() - timestamp > self.ttl_seconds:
                # Remove expired entry
                del self.cache[key]
                return None

            logger.debug(f"Cache hit for key: {key}")
            return entry["value"]

    async def set(self, key: str, value: Any) -> None:
        """
        Set a value in the cache

        Args:
            key: Cache key
            value: Value to cache
        """
        async with self.lock:
            # Check if we need to enforce size limit
            if self.max_size is not None and len(self.cache) >= self.max_size:
                # Remove oldest entry if at capacity
                self._remove_oldest_entry()

            # Store value with timestamp
            self.cache[key] = {"value": value, "timestamp": time.time()}
            logger.debug(f"Cached value for key: {key}")

    async def invalidate(self, key: str) -> None:
        """
        Invalidate a specific cache entry

        Args:
            key: Cache key to invalidate
        """
        async with self.lock:
            if key in self.cache:
                del self.cache[key]
                logger.debug(f"Invalidated cache for key: {key}")

    async def clear(self) -> None:
        """Clear all entries from the cache"""
        async with self.lock:
            self.cache.clear()
            logger.debug("Cache cleared")

    def _remove_oldest_entry(self) -> None:
        """Remove the oldest entry from the cache (called when at capacity)"""
        if not self.cache:
            return

        # Find the entry with the oldest timestamp
        oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k]["timestamp"])
        del self.cache[oldest_key]
        logger.debug(f"Removed oldest cache entry with key: {oldest_key}")
