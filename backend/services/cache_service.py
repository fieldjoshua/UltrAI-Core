"""
Caching service for the Ultra backend.

This module provides a Redis-based caching system for storing and retrieving
analysis results, reducing duplicate LLM calls and improving performance.
"""

import hashlib
import json
import os
from typing import Any, Dict, List, Optional

import redis

from backend.utils.logging import get_logger

# Set up logger
logger = get_logger("cache_service", "logs/cache.log")

# Redis configuration
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB_CACHE", "1"))  # Different DB than rate limiting
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)

# Cache configuration
DEFAULT_CACHE_TTL = 60 * 60 * 24  # 24 hours in seconds
CACHE_ENABLED = os.getenv("CACHE_ENABLED", "true").lower() == "true"
CACHE_PREFIX = "ultra:cache:"


class CacheService:
    """Service for caching analysis results and other data"""

    def __init__(self):
        """Initialize cache service with Redis connection"""
        if not CACHE_ENABLED:
            logger.info("Cache service is disabled")
            self.redis = None
            return

        try:
            self.redis = redis.Redis(
                host=REDIS_HOST,
                port=REDIS_PORT,
                db=REDIS_DB,
                password=REDIS_PASSWORD,
                decode_responses=True,
                socket_timeout=5.0,  # 5 second timeout for Redis operations
                socket_connect_timeout=2.0,  # 2 second timeout for connections
            )
            # Test connection
            self.redis.ping()
            logger.info("Connected to Redis for caching")
        except redis.RedisError as e:
            logger.error(f"Error connecting to Redis: {str(e)}")
            logger.warning("Caching will be disabled")
            self.redis = None

    def is_enabled(self) -> bool:
        """
        Check if caching is enabled

        Returns:
            True if caching is enabled, False otherwise
        """
        return CACHE_ENABLED and self.redis is not None

    def _generate_key(self, prefix: str, data: Dict[str, Any]) -> str:
        """
        Generate a cache key from data

        Args:
            prefix: Key prefix for namespace
            data: Data to generate key from

        Returns:
            Cache key string
        """
        # Create a sorted, stable representation of the data
        serialized = json.dumps(data, sort_keys=True)

        # Hash it to create a fixed-length key
        hashed = hashlib.sha256(serialized.encode()).hexdigest()

        # Return prefixed key
        return f"{CACHE_PREFIX}{prefix}:{hashed}"

    async def get(self, prefix: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Get data from cache

        Args:
            prefix: Key prefix for namespace
            data: Data that was used to store the value

        Returns:
            Cached data if found and not expired, None otherwise
        """
        if not self.is_enabled():
            return None

        try:
            key = self._generate_key(prefix, data)
            cached_data = self.redis.get(key)

            if cached_data:
                try:
                    return json.loads(cached_data)
                except json.JSONDecodeError:
                    logger.error(f"Error decoding cache data for key: {key}")
                    return None

            return None
        except redis.RedisError as e:
            logger.error(f"Redis error during cache get: {str(e)}")
            return None

    async def set(
        self,
        prefix: str,
        data: Dict[str, Any],
        value: Dict[str, Any],
        ttl: int = DEFAULT_CACHE_TTL,
    ) -> bool:
        """
        Store data in cache

        Args:
            prefix: Key prefix for namespace
            data: Data used to generate the key
            value: Value to store
            ttl: Time-to-live in seconds

        Returns:
            True if successful, False otherwise
        """
        if not self.is_enabled():
            return False

        try:
            key = self._generate_key(prefix, data)
            serialized_value = json.dumps(value)

            # Store with TTL
            return bool(self.redis.setex(key, ttl, serialized_value))
        except redis.RedisError as e:
            logger.error(f"Redis error during cache set: {str(e)}")
            return False

    async def delete(self, prefix: str, data: Dict[str, Any]) -> bool:
        """
        Delete data from cache

        Args:
            prefix: Key prefix for namespace
            data: Data used to generate the key

        Returns:
            True if deleted, False otherwise
        """
        if not self.is_enabled():
            return False

        try:
            key = self._generate_key(prefix, data)
            return bool(self.redis.delete(key))
        except redis.RedisError as e:
            logger.error(f"Redis error during cache delete: {str(e)}")
            return False

    async def exists(self, prefix: str, data: Dict[str, Any]) -> bool:
        """
        Check if data exists in cache

        Args:
            prefix: Key prefix for namespace
            data: Data used to generate the key

        Returns:
            True if exists, False otherwise
        """
        if not self.is_enabled():
            return False

        try:
            key = self._generate_key(prefix, data)
            return bool(self.redis.exists(key))
        except redis.RedisError as e:
            logger.error(f"Redis error during cache exists check: {str(e)}")
            return False

    async def clear_by_pattern(self, pattern: str) -> int:
        """
        Clear all cache entries matching a pattern

        Args:
            pattern: Pattern to match keys (e.g., "analyze:*")

        Returns:
            Number of keys deleted
        """
        if not self.is_enabled():
            return 0

        try:
            # Get all keys matching the pattern
            keys = self.redis.keys(f"{CACHE_PREFIX}{pattern}")

            if not keys:
                return 0

            # Delete them all
            return self.redis.delete(*keys)
        except redis.RedisError as e:
            logger.error(f"Redis error during cache clear by pattern: {str(e)}")
            return 0

    async def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics

        Returns:
            Dictionary with cache stats
        """
        if not self.is_enabled():
            return {"enabled": False, "keys_count": 0, "memory_used": 0, "hit_rate": 0}

        try:
            # Get all cache keys
            keys = self.redis.keys(f"{CACHE_PREFIX}*")
            keys_count = len(keys)

            # Get memory info
            memory_info = self.redis.info("memory")
            memory_used = memory_info.get("used_memory_human", "0")

            return {
                "enabled": True,
                "keys_count": keys_count,
                "memory_used": memory_used,
                "namespaces": self._count_namespaces(keys),
            }
        except redis.RedisError as e:
            logger.error(f"Redis error during cache stats collection: {str(e)}")
            return {
                "enabled": True,
                "error": str(e),
                "keys_count": 0,
                "memory_used": "0",
            }

    def _count_namespaces(self, keys: List[str]) -> Dict[str, int]:
        """
        Count keys by namespace

        Args:
            keys: List of cache keys

        Returns:
            Dict with namespace counts
        """
        namespaces = {}

        for key in keys:
            if ":" not in key:
                continue

            parts = key.split(":")
            if len(parts) >= 3:  # prefix:namespace:hash
                namespace = parts[1]
                namespaces[namespace] = namespaces.get(namespace, 0) + 1

        return namespaces


# Create a global instance
cache_service = CacheService()
