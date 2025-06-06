"""
Caching Utility

This module provides caching functionality for LLM responses to reduce
redundant API calls and improve performance.
"""

import time
from typing import Any, Callable, Dict, Optional


class SimpleCache:
    """
    A simple in-memory cache for storing and retrieving responses.

    This cache uses a dictionary with expiration times for each entry.
    """

    def __init__(self, ttl: int = 3600):
        """
        Initialize the cache.

        Args:
            ttl: Time-to-live in seconds (default: 1 hour)
        """
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.ttl = ttl

    def get(self, key: str) -> Optional[Any]:
        """
        Get a value from the cache.

        Args:
            key: Cache key

        Returns:
            The cached value, or None if not found or expired
        """
        if key not in self.cache:
            return None

        entry = self.cache[key]
        if time.time() > entry["expiry"]:
            del self.cache[key]
            return None

        return entry["value"]

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Set a value in the cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Optional custom TTL in seconds
        """
        expiry = time.time() + (ttl if ttl is not None else self.ttl)
        self.cache[key] = {"value": value, "expiry": expiry}

    def delete(self, key: str) -> bool:
        """
        Delete a value from the cache.

        Args:
            key: Cache key

        Returns:
            True if deleted, False if not found
        """
        if key in self.cache:
            del self.cache[key]
            return True
        return False

    def clear(self) -> None:
        """Clear all items from the cache."""
        self.cache.clear()

    def cleanup(self) -> int:
        """
        Remove all expired entries from the cache.

        Returns:
            Number of entries removed
        """
        now = time.time()
        expired_keys = [
            key for key, entry in self.cache.items() if now > entry["expiry"]
        ]
        for key in expired_keys:
            del self.cache[key]
        return len(expired_keys)

    def size(self) -> int:
        """
        Get the current size of the cache.

        Returns:
            Number of entries in the cache
        """
        return len(self.cache)


def cached(func: Optional[Callable] = None, ttl: int = 3600) -> Callable:
    """
    Decorator to cache function results.

    Args:
        func: Function to decorate
        ttl: Time-to-live in seconds

    Returns:
        Decorated function
    """
    # Initialize cache
    cache = SimpleCache(ttl=ttl)

    def decorator(f: Callable) -> Callable:
        async def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            key_parts = [f.__name__]
            key_parts.extend(str(arg) for arg in args)
            key_parts.extend(f"{k}:{v}" for k, v in sorted(kwargs.items()))
            cache_key = ":".join(key_parts)

            # Check cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result

            # Call function and cache result
            result = await f(*args, **kwargs)
            cache.set(cache_key, result)
            return result

        return wrapper

    # Handle both @cached and @cached(ttl=3600) syntax
    if func is None:
        return decorator
    return decorator(func)
