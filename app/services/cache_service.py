"""
Caching service for the Ultra backend.

This module provides a caching system with Redis backend and in-memory fallback.
It uses dependency_manager to handle graceful degradation when Redis is unavailable.
"""

import hashlib
import json
import os
import pickle  # nosec B403
import threading
import time
from collections import OrderedDict
from typing import Any, Dict, List, Optional

from app.utils.dependency_manager import redis_dependency
from app.utils.logging import get_logger

# Set up logger
logger = get_logger("cache_service", "logs/cache.log")

# Redis configuration
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB_CACHE", "1"))  # Different DB than rate limiting
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)
REDIS_URL = os.getenv("REDIS_URL", f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}")

# Cache configuration
DEFAULT_CACHE_TTL = int(
    os.getenv("CACHE_TTL", str(60 * 60 * 24))
)  # 24 hours in seconds
CACHE_ENABLED = os.getenv("CACHE_ENABLED", "true").lower() in ("true", "1", "yes")
CACHE_PREFIX = "ultra:cache:"
MAX_MEMORY_ITEMS = int(os.getenv("MAX_MEMORY_ITEMS", "1000"))


class CacheInterface:
    """Abstract interface for cache implementations"""

    def get(self, key: str) -> Optional[Any]:
        """Get a value from the cache"""
        raise NotImplementedError()

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set a value in the cache with optional TTL"""
        raise NotImplementedError()

    def delete(self, key: str) -> bool:
        """Delete a value from the cache"""
        raise NotImplementedError()

    def exists(self, key: str) -> bool:
        """Check if a key exists in the cache"""
        raise NotImplementedError()

    def increment(self, key: str, amount: int = 1) -> int:
        """Increment a numeric value in the cache"""
        raise NotImplementedError()

    def expire(self, key: str, ttl: int) -> bool:
        """Set expiration time for a key"""
        raise NotImplementedError()

    def flush(self) -> bool:
        """Clear all entries in the cache"""
        raise NotImplementedError()

    def keys(self, pattern: str) -> List[str]:
        """Get all keys matching a pattern"""
        raise NotImplementedError()

    def get_dict(self, key: str) -> Optional[Dict[str, Any]]:
        """Get a dictionary value (JSON) from the cache"""
        value = self.get(key)
        if value is None:
            return None

        if isinstance(value, dict):
            return value

        try:
            return json.loads(value) if isinstance(value, str) else value
        except json.JSONDecodeError:
            logger.error(f"Error decoding JSON for key: {key}")
            return None

    def set_dict(
        self, key: str, value: Dict[str, Any], ttl: Optional[int] = None
    ) -> bool:
        """Set a dictionary value (as JSON) in the cache"""
        try:
            serialized = json.dumps(value)
            return self.set(key, serialized, ttl)
        except (TypeError, json.JSONDecodeError) as e:
            logger.error(f"Error encoding JSON for key {key}: {str(e)}")
            return False


class RedisCache(CacheInterface):
    """Redis-based cache implementation"""

    def __init__(self):
        """Initialize Redis cache"""
        super().__init__()
        self.client = None

        try:
            # Get Redis module from dependency manager
            redis_module = redis_dependency.get_module()

            # Initialize Redis client
            self.client = redis_module.Redis(
                host=REDIS_HOST,
                port=REDIS_PORT,
                db=REDIS_DB,
                password=REDIS_PASSWORD,
                decode_responses=False,  # Keep as bytes for pickle compatibility
                socket_timeout=5.0,  # 5 second timeout for Redis operations
                socket_connect_timeout=2.0,  # 2 second timeout for connections
            )

            # Test connection
            self.client.ping()
            logger.info("Connected to Redis cache")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {str(e)}")
            self.client = None
            # Don't raise exception - just return None and let service fallback to memory cache

    def get(self, key: str) -> Optional[Any]:
        """Get a value from Redis"""
        if not self.client:
            return None

        try:
            value = self.client.get(key)
            if value is None:
                return None
            return pickle.loads(value)  # nosec B301
        except Exception as e:
            logger.error(f"Error getting key {key} from Redis: {str(e)}")
            return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set a value in Redis with optional TTL"""
        if not self.client:
            return False

        try:
            serialized = pickle.dumps(value)
            if ttl is not None:
                return bool(self.client.setex(key, ttl, serialized))
            else:
                return bool(self.client.set(key, serialized))
        except Exception as e:
            logger.error(f"Error setting key {key} in Redis: {str(e)}")
            return False

    def delete(self, key: str) -> bool:
        """Delete a value from Redis"""
        if not self.client:
            return False

        try:
            return bool(self.client.delete(key))
        except Exception as e:
            logger.error(f"Error deleting key {key} from Redis: {str(e)}")
            return False

    def exists(self, key: str) -> bool:
        """Check if a key exists in Redis"""
        if not self.client:
            return False

        try:
            return bool(self.client.exists(key))
        except Exception as e:
            logger.error(f"Error checking existence of key {key} in Redis: {str(e)}")
            return False

    def increment(self, key: str, amount: int = 1) -> int:
        """Increment a numeric value in Redis"""
        if not self.client:
            return 0

        try:
            return int(self.client.incrby(key, amount))
        except Exception as e:
            logger.error(f"Error incrementing key {key} in Redis: {str(e)}")
            return 0

    def expire(self, key: str, ttl: int) -> bool:
        """Set expiration time for a key in Redis"""
        if not self.client:
            return False

        try:
            return bool(self.client.expire(key, ttl))
        except Exception as e:
            logger.error(f"Error setting expiry for key {key} in Redis: {str(e)}")
            return False

    def flush(self) -> bool:
        """Clear all entries in Redis database"""
        if not self.client:
            return False

        try:
            self.client.flushdb()
            return True
        except Exception as e:
            logger.error(f"Error flushing Redis database: {str(e)}")
            return False

    def keys(self, pattern: str) -> List[str]:
        """Get all keys matching a pattern from Redis"""
        if not self.client:
            return []

        try:
            # Convert bytes to strings
            return [k.decode("utf-8") for k in self.client.keys(pattern)]
        except Exception as e:
            logger.error(
                f"Error getting keys with pattern {pattern} from Redis: {str(e)}"
            )
            return []


class CacheEntry:
    """Entry in the memory cache"""

    def __init__(self, value: Any, ttl: Optional[int] = None):
        """
        Initialize cache entry

        Args:
            value: Value to store
            ttl: Time-to-live in seconds (None for no expiry)
        """
        self.value = value
        self.created_at = time.time()
        self.ttl = ttl
        self.expires_at = self.created_at + ttl if ttl is not None else None

    def is_expired(self) -> bool:
        """Check if entry is expired"""
        if self.expires_at is None:
            return False
        return time.time() > self.expires_at


class MemoryCache(CacheInterface):
    """In-memory cache implementation using OrderedDict for LRU behavior"""

    def __init__(self, max_items: int = MAX_MEMORY_ITEMS):
        """
        Initialize memory cache

        Args:
            max_items: Maximum number of items to store
        """
        super().__init__()
        self.max_items = max_items
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.lock = threading.RLock()  # Reentrant lock for thread safety
        logger.info(
            f"Initialized in-memory cache with max capacity of {max_items} items"
        )

    def _cleanup_expired(self) -> None:
        """Remove expired entries"""
        with self.lock:
            expired_keys = [k for k, v in self.cache.items() if v.is_expired()]
            for key in expired_keys:
                self.cache.pop(key, None)

    def get(self, key: str) -> Optional[Any]:
        """Get a value from memory cache"""
        self._cleanup_expired()
        with self.lock:
            entry = self.cache.get(key)
            if entry is None or entry.is_expired():
                if entry is not None:
                    # Remove expired entry
                    self.cache.pop(key, None)
                return None

            # Move to end (most recently used)
            self.cache.move_to_end(key)
            return entry.value

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set a value in memory cache with optional TTL"""
        self._cleanup_expired()
        with self.lock:
            # Ensure we don't exceed max items
            if key not in self.cache and len(self.cache) >= self.max_items:
                # Remove oldest item (first in ordered dict)
                self.cache.popitem(last=False)

            self.cache[key] = CacheEntry(value, ttl)
            # Move to end (most recently used)
            self.cache.move_to_end(key)
            return True

    def delete(self, key: str) -> bool:
        """Delete a value from memory cache"""
        with self.lock:
            if key in self.cache:
                self.cache.pop(key)
                return True
            return False

    def exists(self, key: str) -> bool:
        """Check if a key exists in memory cache"""
        self._cleanup_expired()
        with self.lock:
            if key not in self.cache:
                return False
            entry = self.cache[key]
            if entry.is_expired():
                self.cache.pop(key)
                return False
            return True

    def increment(self, key: str, amount: int = 1) -> int:
        """Increment a numeric value in memory cache"""
        self._cleanup_expired()
        with self.lock:
            entry = self.cache.get(key)
            if entry is None or entry.is_expired():
                # If key doesn't exist, create it
                self.cache[key] = CacheEntry(amount, entry.ttl if entry else None)
                return amount

            # If value exists, increment it
            if isinstance(entry.value, (int, float)):
                entry.value += amount
                return entry.value
            else:
                # Not a number, set it to the amount
                entry.value = amount
                return amount

    def expire(self, key: str, ttl: int) -> bool:
        """Set expiration time for a key in memory cache"""
        with self.lock:
            entry = self.cache.get(key)
            if entry is None:
                return False

            entry.ttl = ttl
            entry.expires_at = time.time() + ttl
            return True

    def flush(self) -> bool:
        """Clear all entries in memory cache"""
        with self.lock:
            self.cache.clear()
            return True

    def keys(self, pattern: str) -> List[str]:
        """Get all keys matching a pattern from memory cache"""
        import re

        self._cleanup_expired()

        # Convert Redis-style pattern to regex
        pattern = pattern.replace("*", ".*").replace("?", ".")
        regex = re.compile(f"^{pattern}$")

        with self.lock:
            return [k for k in self.cache.keys() if regex.match(k)]


class CacheService:
    """
    Service for caching data using Redis with in-memory fallback

    This service tries to use Redis if available, but falls back to in-memory
    caching if Redis is not available or has an error. It provides caching for
    arbitrary Python objects with support for TTL.
    """

    def __init__(self):
        """Initialize cache service with Redis or memory backend"""
        self.cache_enabled = CACHE_ENABLED
        self.implementation: CacheInterface = None

        if not self.cache_enabled:
            logger.info("Cache is disabled by configuration")
            self.implementation = MemoryCache()
            return

        # Try to use Redis first, fall back to memory cache
        try:
            if redis_dependency.is_available():
                logger.info("Using Redis for caching")
                cache_impl = RedisCache()
                # If Redis client failed to initialize, fallback to in-memory cache
                if getattr(cache_impl, "client", None):
                    self.implementation = cache_impl
                else:
                    logger.warning(
                        "Redis client unavailable, falling back to in-memory cache"
                    )
                    self.implementation = MemoryCache()
            else:
                logger.info("Redis not available, using in-memory cache")
                self.implementation = MemoryCache()
        except Exception as e:
            logger.warning(f"Error initializing Redis cache: {str(e)}")
            logger.info("Falling back to in-memory cache")
            self.implementation = MemoryCache()

    def is_redis_available(self) -> bool:
        """Check if Redis is being used for caching"""
        return isinstance(self.implementation, RedisCache)

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a value from the cache

        Args:
            key: Cache key
            default: Default value if key not found

        Returns:
            Cached value or default
        """
        if not self.cache_enabled:
            return default

        value = self.implementation.get(key)
        return default if value is None else value

    def set(self, key: str, value: Any, ttl: Optional[int] = DEFAULT_CACHE_TTL) -> bool:
        """
        Set a value in the cache

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (None for no expiration)

        Returns:
            True if successful, False otherwise
        """
        if not self.cache_enabled:
            return False

        return self.implementation.set(key, value, ttl)

    def delete(self, key: str) -> bool:
        """
        Delete a value from the cache

        Args:
            key: Cache key

        Returns:
            True if successful, False otherwise
        """
        if not self.cache_enabled:
            return False

        return self.implementation.delete(key)

    def exists(self, key: str) -> bool:
        """
        Check if a key exists in the cache

        Args:
            key: Cache key

        Returns:
            True if key exists, False otherwise
        """
        if not self.cache_enabled:
            return False

        return self.implementation.exists(key)

    def increment(self, key: str, amount: int = 1) -> int:
        """
        Increment a numeric value in the cache

        Args:
            key: Cache key
            amount: Amount to increment by

        Returns:
            New value after increment
        """
        if not self.cache_enabled:
            return 0

        return self.implementation.increment(key, amount)

    def expire(self, key: str, ttl: int) -> bool:
        """
        Set expiration time for a key

        Args:
            key: Cache key
            ttl: Time-to-live in seconds

        Returns:
            True if successful, False otherwise
        """
        if not self.cache_enabled:
            return False

        return self.implementation.expire(key, ttl)

    def flush(self) -> bool:
        """
        Clear all entries in the cache

        Returns:
            True if successful, False otherwise
        """
        if not self.cache_enabled:
            return False

        return self.implementation.flush()

    def keys(self, pattern: str = "*") -> List[str]:
        """
        Get all keys matching a pattern

        Args:
            pattern: Key pattern (Redis glob-style)

        Returns:
            List of matching keys
        """
        if not self.cache_enabled:
            return []

        return self.implementation.keys(pattern)

    # --- Compatibility with existing code --- #

    def _generate_key(self, prefix: str, data: Dict[str, Any]) -> str:
        """
        Generate a cache key from data (legacy method for compatibility)

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

    async def get_json(
        self, prefix: str, data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Get JSON data from cache (legacy method for compatibility)

        Args:
            prefix: Key prefix for namespace
            data: Data that was used to store the value

        Returns:
            Cached data if found and not expired, None otherwise
        """
        if not self.cache_enabled:
            return None

        key = self._generate_key(prefix, data)
        return self.implementation.get_dict(key)

    async def set_json(
        self,
        prefix: str,
        data: Dict[str, Any],
        value: Dict[str, Any],
        ttl: int = DEFAULT_CACHE_TTL,
    ) -> bool:
        """
        Store JSON data in cache (legacy method for compatibility)

        Args:
            prefix: Key prefix for namespace
            data: Data used to generate the key
            value: Value to store
            ttl: Time-to-live in seconds

        Returns:
            True if successful, False otherwise
        """
        if not self.cache_enabled:
            return False

        key = self._generate_key(prefix, data)
        return self.implementation.set_dict(key, value, ttl)

    async def delete_json(self, prefix: str, data: Dict[str, Any]) -> bool:
        """
        Delete JSON data from cache (legacy method for compatibility)

        Args:
            prefix: Key prefix for namespace
            data: Data used to generate the key

        Returns:
            True if deleted, False otherwise
        """
        if not self.cache_enabled:
            return False

        key = self._generate_key(prefix, data)
        return self.implementation.delete(key)

    async def exists_json(self, prefix: str, data: Dict[str, Any]) -> bool:
        """
        Check if JSON data exists in cache (legacy method for compatibility)

        Args:
            prefix: Key prefix for namespace
            data: Data used to generate the key

        Returns:
            True if exists, False otherwise
        """
        if not self.cache_enabled:
            return False

        key = self._generate_key(prefix, data)
        return self.implementation.exists(key)

    async def clear_by_pattern(self, pattern: str) -> int:
        """
        Clear all cache entries matching a pattern (legacy method for compatibility)

        Args:
            pattern: Pattern to match keys (e.g., "analyze:*")

        Returns:
            Number of keys deleted
        """
        if not self.cache_enabled:
            return 0

        keys = self.implementation.keys(f"{CACHE_PREFIX}{pattern}")
        deleted = 0

        for key in keys:
            if self.implementation.delete(key):
                deleted += 1

        return deleted

    def get_status(self) -> Dict[str, Any]:
        """
        Get cache service status

        Returns:
            Dictionary with status information
        """
        status = {
            "enabled": self.cache_enabled,
            "type": type(self.implementation).__name__,
            "redis_available": self.is_redis_available(),
            "max_memory_items": MAX_MEMORY_ITEMS,
            "default_ttl": DEFAULT_CACHE_TTL,
        }

        if isinstance(self.implementation, MemoryCache):
            status["items_count"] = len(self.implementation.cache)

        return status

    # Legacy alias for get_status
    async def get_stats(self) -> Dict[str, Any]:
        """Legacy alias for get_status"""
        return self.get_status()

    def clear_expired(self) -> None:
        """Force cleanup of expired items (memory cache only)"""
        if isinstance(self.implementation, MemoryCache):
            self.implementation._cleanup_expired()


# Create a global instance
cache_service = CacheService()
