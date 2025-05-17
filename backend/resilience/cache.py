"""
Distributed cache system for Ultra.

This module provides a multi-level distributed caching system with in-memory, disk,
and Redis caching options.
"""

import asyncio
import json
import logging
import os
import pickle
import time
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, TypeVar, Union

try:
    import redis.asyncio as aioredis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

# Configure logger
logger = logging.getLogger("distributed_cache")

# Type variable for cache key
K = TypeVar("K")
V = TypeVar("V")


class CacheMetrics:
    """Metrics collector for cache performance."""

    def __init__(self):
        """Initialize cache metrics."""
        self.hits = {"memory": 0, "disk": 0, "redis": 0}
        self.misses = 0
        self.puts = {"memory": 0, "disk": 0, "redis": 0}
        self.evictions = {"memory": 0, "disk": 0, "redis": 0}
        self.errors = {"memory": 0, "disk": 0, "redis": 0}
        self.latency = {"memory": [], "disk": [], "redis": []}

    def record_hit(self, level: str):
        """Record a cache hit at the specified level."""
        if level in self.hits:
            self.hits[level] += 1

    def record_miss(self):
        """Record a cache miss."""
        self.misses += 1

    def record_put(self, level: str):
        """Record a cache put at the specified level."""
        if level in self.puts:
            self.puts[level] += 1

    def record_eviction(self, level: str):
        """Record a cache eviction at the specified level."""
        if level in self.evictions:
            self.evictions[level] += 1

    def record_error(self, level: str):
        """Record a cache error at the specified level."""
        if level in self.errors:
            self.errors[level] += 1

    def record_latency(self, level: str, latency: float):
        """Record cache operation latency at the specified level."""
        if level in self.latency:
            self.latency[level].append(latency)
            # Only keep the last 100 latency samples
            if len(self.latency[level]) > 100:
                self.latency[level].pop(0)

    def get_hit_rate(self) -> Dict[str, float]:
        """Get the hit rate for each cache level."""
        result = {}
        total_requests = sum(self.hits.values()) + self.misses

        if total_requests > 0:
            for level in self.hits:
                result[level] = self.hits[level] / total_requests
            result["overall"] = sum(self.hits.values()) / total_requests

        return result

    def get_average_latency(self) -> Dict[str, float]:
        """Get the average latency for each cache level."""
        result = {}

        for level in self.latency:
            if self.latency[level]:
                result[level] = sum(self.latency[level]) / len(self.latency[level])
            else:
                result[level] = 0.0

        return result

    def get_metrics(self) -> Dict[str, Any]:
        """Get all cache metrics."""
        return {
            "hits": self.hits,
            "misses": self.misses,
            "puts": self.puts,
            "evictions": self.evictions,
            "errors": self.errors,
            "hit_rate": self.get_hit_rate(),
            "average_latency": self.get_average_latency(),
        }

    def reset(self):
        """Reset all metrics."""
        self.hits = {"memory": 0, "disk": 0, "redis": 0}
        self.misses = 0
        self.puts = {"memory": 0, "disk": 0, "redis": 0}
        self.evictions = {"memory": 0, "disk": 0, "redis": 0}
        self.errors = {"memory": 0, "disk": 0, "redis": 0}
        self.latency = {"memory": [], "disk": [], "redis": []}


class LRUCache:
    """In-memory LRU cache implementation."""

    def __init__(self, capacity: int = 1000):
        """
        Initialize in-memory LRU cache.

        Args:
            capacity: Maximum number of items to store in the cache
        """
        self.capacity = capacity
        self.cache: Dict[str, Tuple[Any, float, Optional[float]]] = {}
        self.usage_order: List[str] = []
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> Optional[Any]:
        """
        Get an item from the cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found or expired
        """
        start_time = time.time()
        try:
            async with self._lock:
                if key not in self.cache:
                    return None

                value, timestamp, ttl = self.cache[key]

                # Check if the item has expired
                if ttl is not None and time.time() - timestamp > ttl:
                    # Remove expired item
                    del self.cache[key]
                    self.usage_order.remove(key)
                    return None

                # Update usage order
                self.usage_order.remove(key)
                self.usage_order.append(key)

                return value
        finally:
            # Record operation latency
            latency = time.time() - start_time
            logger.debug(f"Memory cache get for {key} took {latency:.6f}s")

    async def put(
        self,
        key: str,
        value: Any,
        ttl_seconds: Optional[float] = None,
    ) -> None:
        """
        Store an item in the cache.

        Args:
            key: Cache key
            value: Value to store
            ttl_seconds: Time-to-live in seconds (None for no expiration)
        """
        start_time = time.time()
        try:
            async with self._lock:
                # Remove key if it already exists
                if key in self.cache:
                    self.usage_order.remove(key)

                # Evict least recently used items if cache is full
                while len(self.cache) >= self.capacity and self.usage_order:
                    lru_key = self.usage_order.pop(0)
                    del self.cache[lru_key]

                # Store new item
                self.cache[key] = (value, time.time(), ttl_seconds)
                self.usage_order.append(key)
        finally:
            # Record operation latency
            latency = time.time() - start_time
            logger.debug(f"Memory cache put for {key} took {latency:.6f}s")

    async def delete(self, key: str) -> bool:
        """
        Delete an item from the cache.

        Args:
            key: Cache key

        Returns:
            True if the item was deleted, False if not found
        """
        async with self._lock:
            if key in self.cache:
                del self.cache[key]
                self.usage_order.remove(key)
                return True
            return False

    async def clear(self) -> None:
        """Clear the cache."""
        async with self._lock:
            self.cache.clear()
            self.usage_order.clear()

    async def get_keys(self) -> List[str]:
        """Get all keys in the cache."""
        async with self._lock:
            return self.usage_order.copy()

    async def get_size(self) -> int:
        """Get the number of items in the cache."""
        async with self._lock:
            return len(self.cache)


class DiskCache:
    """Disk-based cache implementation."""

    def __init__(self, cache_dir: str):
        """
        Initialize disk-based cache.

        Args:
            cache_dir: Directory to store cache files
        """
        self.cache_dir = cache_dir
        self._lock = asyncio.Lock()

        # Create cache directory if it doesn't exist
        os.makedirs(cache_dir, exist_ok=True)

        # Create metadata directory
        self.metadata_dir = os.path.join(cache_dir, "_metadata")
        os.makedirs(self.metadata_dir, exist_ok=True)

    async def get(self, key: str) -> Optional[Any]:
        """
        Get an item from the cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found or expired
        """
        start_time = time.time()
        try:
            # Get cache file path
            file_path = self._get_file_path(key)
            metadata_path = self._get_metadata_path(key)

            # Check if cache file exists
            if not os.path.exists(file_path) or not os.path.exists(metadata_path):
                return None

            # Check if item has expired
            if await self._is_expired(key):
                # Remove expired item
                await self._remove_item(key)
                return None

            # Read cache file
            try:
                with open(file_path, "rb") as f:
                    value = pickle.load(f)

                # Update access time
                await self._update_access_time(key)

                return value
            except Exception as e:
                logger.error(f"Error reading cache file for {key}: {e}")
                return None
        finally:
            # Record operation latency
            latency = time.time() - start_time
            logger.debug(f"Disk cache get for {key} took {latency:.6f}s")

    async def put(
        self,
        key: str,
        value: Any,
        ttl_seconds: Optional[float] = None,
    ) -> None:
        """
        Store an item in the cache.

        Args:
            key: Cache key
            value: Value to store
            ttl_seconds: Time-to-live in seconds (None for no expiration)
        """
        start_time = time.time()
        try:
            # Get cache file path
            file_path = self._get_file_path(key)
            metadata_path = self._get_metadata_path(key)

            # Write cache file
            try:
                with open(file_path, "wb") as f:
                    pickle.dump(value, f)

                # Write metadata
                metadata = {
                    "key": key,
                    "created_at": time.time(),
                    "last_accessed": time.time(),
                    "ttl": ttl_seconds,
                }

                with open(metadata_path, "w") as f:
                    json.dump(metadata, f)
            except Exception as e:
                logger.error(f"Error writing cache file for {key}: {e}")

                # Clean up if partial write
                if os.path.exists(file_path):
                    os.remove(file_path)
                if os.path.exists(metadata_path):
                    os.remove(metadata_path)
        finally:
            # Record operation latency
            latency = time.time() - start_time
            logger.debug(f"Disk cache put for {key} took {latency:.6f}s")

    async def delete(self, key: str) -> bool:
        """
        Delete an item from the cache.

        Args:
            key: Cache key

        Returns:
            True if the item was deleted, False if not found
        """
        return await self._remove_item(key)

    async def clear(self) -> None:
        """Clear the cache."""
        # Get all cache files
        cache_files = os.listdir(self.cache_dir)

        # Remove all cache files
        for filename in cache_files:
            if filename != "_metadata":
                file_path = os.path.join(self.cache_dir, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)

        # Remove all metadata files
        metadata_files = os.listdir(self.metadata_dir)
        for filename in metadata_files:
            file_path = os.path.join(self.metadata_dir, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)

    async def get_keys(self) -> List[str]:
        """Get all keys in the cache."""
        # Get all metadata files
        metadata_files = os.listdir(self.metadata_dir)

        # Extract keys from metadata files
        keys = []
        for filename in metadata_files:
            if filename.endswith(".json"):
                key = filename[:-5]
                if not await self._is_expired(key):
                    keys.append(key)

        return keys

    async def get_size(self) -> int:
        """Get the number of items in the cache."""
        # Get all metadata files
        metadata_files = os.listdir(self.metadata_dir)

        # Count non-expired items
        count = 0
        for filename in metadata_files:
            if filename.endswith(".json"):
                key = filename[:-5]
                if not await self._is_expired(key):
                    count += 1

        return count

    def _get_file_path(self, key: str) -> str:
        """Get the file path for a cache key."""
        # Use the key as the filename
        safe_key = key.replace("/", "_").replace(":", "_")
        return os.path.join(self.cache_dir, f"{safe_key}.pickle")

    def _get_metadata_path(self, key: str) -> str:
        """Get the metadata file path for a cache key."""
        # Use the key as the filename
        safe_key = key.replace("/", "_").replace(":", "_")
        return os.path.join(self.metadata_dir, f"{safe_key}.json")

    async def _is_expired(self, key: str) -> bool:
        """Check if a cache item has expired."""
        metadata_path = self._get_metadata_path(key)

        # Check if metadata file exists
        if not os.path.exists(metadata_path):
            return True

        try:
            # Read metadata
            with open(metadata_path, "r") as f:
                metadata = json.load(f)

            # Check TTL
            ttl = metadata.get("ttl")
            created_at = metadata.get("created_at", 0)

            if ttl is not None and time.time() - created_at > ttl:
                return True
        except Exception as e:
            logger.error(f"Error reading metadata for {key}: {e}")
            return True

        return False

    async def _update_access_time(self, key: str) -> None:
        """Update the last access time for a cache item."""
        metadata_path = self._get_metadata_path(key)

        # Check if metadata file exists
        if not os.path.exists(metadata_path):
            return

        try:
            # Read metadata
            with open(metadata_path, "r") as f:
                metadata = json.load(f)

            # Update last access time
            metadata["last_accessed"] = time.time()

            # Write metadata
            with open(metadata_path, "w") as f:
                json.dump(metadata, f)
        except Exception as e:
            logger.error(f"Error updating access time for {key}: {e}")

    async def _remove_item(self, key: str) -> bool:
        """Remove a cache item."""
        file_path = self._get_file_path(key)
        metadata_path = self._get_metadata_path(key)

        removed = False

        # Remove cache file
        if os.path.exists(file_path):
            os.remove(file_path)
            removed = True

        # Remove metadata file
        if os.path.exists(metadata_path):
            os.remove(metadata_path)
            removed = True

        return removed


class RedisCache:
    """Redis-based cache implementation."""

    def __init__(self, redis_url: str, prefix: str = "cache:"):
        """
        Initialize Redis-based cache.

        Args:
            redis_url: Redis connection URL
            prefix: Prefix for cache keys
        """
        if not REDIS_AVAILABLE:
            raise ImportError("Redis support requires redis.asyncio package")

        self.redis_url = redis_url
        self.prefix = prefix
        self.redis = aioredis.from_url(redis_url)

    async def get(self, key: str) -> Optional[Any]:
        """
        Get an item from the cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        start_time = time.time()
        try:
            # Get prefixed key
            prefixed_key = self._get_prefixed_key(key)

            # Get value from Redis
            value = await self.redis.get(prefixed_key)

            if value is None:
                return None

            # Deserialize value
            try:
                return pickle.loads(value)
            except Exception as e:
                logger.error(f"Error deserializing Redis cache value for {key}: {e}")
                return None
        finally:
            # Record operation latency
            latency = time.time() - start_time
            logger.debug(f"Redis cache get for {key} took {latency:.6f}s")

    async def put(
        self,
        key: str,
        value: Any,
        ttl_seconds: Optional[float] = None,
    ) -> None:
        """
        Store an item in the cache.

        Args:
            key: Cache key
            value: Value to store
            ttl_seconds: Time-to-live in seconds (None for no expiration)
        """
        start_time = time.time()
        try:
            # Get prefixed key
            prefixed_key = self._get_prefixed_key(key)

            # Serialize value
            try:
                serialized_value = pickle.dumps(value)
            except Exception as e:
                logger.error(f"Error serializing value for Redis cache key {key}: {e}")
                return

            # Store in Redis
            if ttl_seconds is not None:
                await self.redis.setex(
                    prefixed_key,
                    int(ttl_seconds),
                    serialized_value,
                )
            else:
                await self.redis.set(prefixed_key, serialized_value)
        finally:
            # Record operation latency
            latency = time.time() - start_time
            logger.debug(f"Redis cache put for {key} took {latency:.6f}s")

    async def delete(self, key: str) -> bool:
        """
        Delete an item from the cache.

        Args:
            key: Cache key

        Returns:
            True if the item was deleted, False if not found
        """
        # Get prefixed key
        prefixed_key = self._get_prefixed_key(key)

        # Delete from Redis
        result = await self.redis.delete(prefixed_key)
        return result > 0

    async def clear(self) -> None:
        """Clear the cache."""
        # Get all keys with prefix
        keys = await self.redis.keys(f"{self.prefix}*")

        # Delete all keys
        if keys:
            await self.redis.delete(*keys)

    async def get_keys(self) -> List[str]:
        """Get all keys in the cache."""
        # Get all keys with prefix
        keys = await self.redis.keys(f"{self.prefix}*")

        # Remove prefix from keys
        return [key[len(self.prefix) :].decode("utf-8") for key in keys]

    async def get_size(self) -> int:
        """Get the number of items in the cache."""
        # Get all keys with prefix
        keys = await self.redis.keys(f"{self.prefix}*")
        return len(keys)

    def _get_prefixed_key(self, key: str) -> str:
        """Get the prefixed key for Redis."""
        return f"{self.prefix}{key}"


class DistributedCache:
    """Multi-level distributed caching system."""

    def __init__(
        self,
        memory_cache_size: int = 1000,
        disk_cache_dir: Optional[str] = None,
        redis_url: Optional[str] = None,
        redis_prefix: str = "cache:",
    ):
        """
        Initialize the distributed cache.

        Args:
            memory_cache_size: Maximum number of items in memory cache
            disk_cache_dir: Directory for disk cache (None to disable)
            redis_url: Redis connection URL (None to disable)
            redis_prefix: Prefix for Redis cache keys
        """
        self.memory_cache = LRUCache(memory_cache_size)
        self.disk_cache = DiskCache(disk_cache_dir) if disk_cache_dir else None

        self.redis_cache = None
        if redis_url and REDIS_AVAILABLE:
            try:
                self.redis_cache = RedisCache(redis_url, redis_prefix)
            except Exception as e:
                logger.warning(f"Failed to initialize Redis cache: {e}")

        self.metrics = CacheMetrics()
        self._lock = asyncio.Lock()

        logger.info(
            f"Initialized distributed cache with memory_cache_size={memory_cache_size}, "
            f"disk_cache_dir={disk_cache_dir}, redis_url={redis_url}"
        )

    async def get(
        self,
        key: str,
        namespace: Optional[str] = None,
    ) -> Optional[Any]:
        """
        Get an item from the cache.

        Args:
            key: Cache key
            namespace: Optional namespace for the key

        Returns:
            Cached value or None if not found
        """
        # Get namespaced key
        full_key = self._make_key(key, namespace)

        # Try memory cache first
        start_time = time.time()
        try:
            value = await self.memory_cache.get(full_key)
            if value is not None:
                self.metrics.record_hit("memory")
                self.metrics.record_latency("memory", time.time() - start_time)
                return value
        except Exception as e:
            logger.error(f"Error getting from memory cache: {e}")
            self.metrics.record_error("memory")

        # Try disk cache
        if self.disk_cache:
            start_time = time.time()
            try:
                value = await self.disk_cache.get(full_key)
                if value is not None:
                    # Promote to memory cache
                    await self.memory_cache.put(full_key, value)
                    self.metrics.record_hit("disk")
                    self.metrics.record_latency("disk", time.time() - start_time)
                    return value
            except Exception as e:
                logger.error(f"Error getting from disk cache: {e}")
                self.metrics.record_error("disk")

        # Try Redis cache
        if self.redis_cache:
            start_time = time.time()
            try:
                value = await self.redis_cache.get(full_key)
                if value is not None:
                    # Promote to memory cache
                    await self.memory_cache.put(full_key, value)

                    # Promote to disk cache if available
                    if self.disk_cache:
                        await self.disk_cache.put(full_key, value)

                    self.metrics.record_hit("redis")
                    self.metrics.record_latency("redis", time.time() - start_time)
                    return value
            except Exception as e:
                logger.error(f"Error getting from Redis cache: {e}")
                self.metrics.record_error("redis")

        self.metrics.record_miss()
        return None

    async def put(
        self,
        key: str,
        value: Any,
        namespace: Optional[str] = None,
        ttl_seconds: Optional[float] = 3600,
        levels: Optional[List[str]] = None,
    ) -> None:
        """
        Store an item in the cache.

        Args:
            key: Cache key
            value: Value to store
            namespace: Optional namespace for the key
            ttl_seconds: Time-to-live in seconds (None for no expiration)
            levels: Cache levels to use (None for all available)
        """
        # Get namespaced key
        full_key = self._make_key(key, namespace)
        levels = levels or ["memory", "disk", "redis"]

        # Store in memory cache
        if "memory" in levels:
            start_time = time.time()
            try:
                await self.memory_cache.put(full_key, value, ttl_seconds)
                self.metrics.record_put("memory")
                self.metrics.record_latency("memory", time.time() - start_time)
            except Exception as e:
                logger.error(f"Error putting to memory cache: {e}")
                self.metrics.record_error("memory")

        # Store in disk cache
        if "disk" in levels and self.disk_cache:
            start_time = time.time()
            try:
                await self.disk_cache.put(full_key, value, ttl_seconds)
                self.metrics.record_put("disk")
                self.metrics.record_latency("disk", time.time() - start_time)
            except Exception as e:
                logger.error(f"Error putting to disk cache: {e}")
                self.metrics.record_error("disk")

        # Store in Redis cache
        if "redis" in levels and self.redis_cache:
            start_time = time.time()
            try:
                await self.redis_cache.put(full_key, value, ttl_seconds)
                self.metrics.record_put("redis")
                self.metrics.record_latency("redis", time.time() - start_time)
            except Exception as e:
                logger.error(f"Error putting to Redis cache: {e}")
                self.metrics.record_error("redis")

    async def delete(
        self,
        key: str,
        namespace: Optional[str] = None,
    ) -> bool:
        """
        Delete an item from the cache.

        Args:
            key: Cache key
            namespace: Optional namespace for the key

        Returns:
            True if the item was deleted from at least one level
        """
        # Get namespaced key
        full_key = self._make_key(key, namespace)
        deleted = False

        # Delete from memory cache
        try:
            if await self.memory_cache.delete(full_key):
                deleted = True
        except Exception as e:
            logger.error(f"Error deleting from memory cache: {e}")

        # Delete from disk cache
        if self.disk_cache:
            try:
                if await self.disk_cache.delete(full_key):
                    deleted = True
            except Exception as e:
                logger.error(f"Error deleting from disk cache: {e}")

        # Delete from Redis cache
        if self.redis_cache:
            try:
                if await self.redis_cache.delete(full_key):
                    deleted = True
            except Exception as e:
                logger.error(f"Error deleting from Redis cache: {e}")

        return deleted

    async def invalidate(
        self,
        pattern: Optional[str] = None,
        namespace: Optional[str] = None,
    ) -> int:
        """
        Invalidate cache entries based on a pattern.

        Args:
            pattern: Glob pattern for keys to invalidate (None for all)
            namespace: Optional namespace for the keys

        Returns:
            Number of items invalidated
        """
        import fnmatch

        # Get all keys
        keys = []

        # Get memory cache keys
        try:
            memory_keys = await self.memory_cache.get_keys()
            keys.extend(memory_keys)
        except Exception as e:
            logger.error(f"Error getting memory cache keys: {e}")

        # Get disk cache keys
        if self.disk_cache:
            try:
                disk_keys = await self.disk_cache.get_keys()
                keys.extend(disk_keys)
            except Exception as e:
                logger.error(f"Error getting disk cache keys: {e}")

        # Get Redis cache keys
        if self.redis_cache:
            try:
                redis_keys = await self.redis_cache.get_keys()
                keys.extend(redis_keys)
            except Exception as e:
                logger.error(f"Error getting Redis cache keys: {e}")

        # Remove duplicates
        keys = list(set(keys))

        # Filter keys by namespace
        if namespace:
            namespace_prefix = f"{namespace}:"
            keys = [
                (
                    key[len(namespace_prefix) :]
                    if key.startswith(namespace_prefix)
                    else key
                )
                for key in keys
            ]

        # Filter keys by pattern
        if pattern:
            keys = [key for key in keys if fnmatch.fnmatch(key, pattern)]

        # Delete filtered keys
        count = 0
        for key in keys:
            if await self.delete(key, namespace):
                count += 1

        return count

    async def clear(self) -> None:
        """Clear the entire cache."""
        # Clear memory cache
        try:
            await self.memory_cache.clear()
        except Exception as e:
            logger.error(f"Error clearing memory cache: {e}")

        # Clear disk cache
        if self.disk_cache:
            try:
                await self.disk_cache.clear()
            except Exception as e:
                logger.error(f"Error clearing disk cache: {e}")

        # Clear Redis cache
        if self.redis_cache:
            try:
                await self.redis_cache.clear()
            except Exception as e:
                logger.error(f"Error clearing Redis cache: {e}")

        # Reset metrics
        self.metrics.reset()

    async def get_size(self) -> Dict[str, int]:
        """
        Get the size of each cache level.

        Returns:
            Dictionary with cache level sizes
        """
        result = {}

        # Get memory cache size
        try:
            result["memory"] = await self.memory_cache.get_size()
        except Exception as e:
            logger.error(f"Error getting memory cache size: {e}")
            result["memory"] = -1

        # Get disk cache size
        if self.disk_cache:
            try:
                result["disk"] = await self.disk_cache.get_size()
            except Exception as e:
                logger.error(f"Error getting disk cache size: {e}")
                result["disk"] = -1
        else:
            result["disk"] = 0

        # Get Redis cache size
        if self.redis_cache:
            try:
                result["redis"] = await self.redis_cache.get_size()
            except Exception as e:
                logger.error(f"Error getting Redis cache size: {e}")
                result["redis"] = -1
        else:
            result["redis"] = 0

        return result

    def get_metrics(self) -> Dict[str, Any]:
        """
        Get cache performance metrics.

        Returns:
            Dictionary with cache metrics
        """
        return self.metrics.get_metrics()

    def _make_key(self, key: str, namespace: Optional[str] = None) -> str:
        """
        Create a full key with optional namespace.

        Args:
            key: Cache key
            namespace: Optional namespace for the key

        Returns:
            Full cache key
        """
        if namespace:
            return f"{namespace}:{key}"
        return key


def cached(
    namespace: Optional[str] = None,
    ttl_seconds: Optional[float] = 3600,
    key_fn: Optional[Callable] = None,
):
    """
    Decorator for caching function results.

    Args:
        namespace: Cache namespace
        ttl_seconds: Cache TTL in seconds
        key_fn: Function to generate cache key from arguments

    Returns:
        Decorator function
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get cache instance
            cache = wrapper.cache
            if cache is None:
                # No cache configured, just call the function
                return await func(*args, **kwargs)

            # Generate cache key
            if key_fn:
                key = key_fn(*args, **kwargs)
            else:
                # Default key generation
                key_parts = [func.__name__]

                # Add positional arguments
                for arg in args:
                    if hasattr(arg, "__dict__"):
                        # For objects, use repr
                        key_parts.append(repr(arg))
                    else:
                        # For other types, use str
                        key_parts.append(str(arg))

                # Add keyword arguments
                for k, v in sorted(kwargs.items()):
                    if hasattr(v, "__dict__"):
                        # For objects, use repr
                        key_parts.append(f"{k}={repr(v)}")
                    else:
                        # For other types, use str
                        key_parts.append(f"{k}={v}")

                key = ":".join(key_parts)

            # Try to get from cache
            cached_value = await cache.get(key, namespace)
            if cached_value is not None:
                return cached_value

            # Call function
            result = await func(*args, **kwargs)

            # Store in cache
            await cache.put(key, result, namespace, ttl_seconds)

            return result

        # Attach cache instance
        wrapper.cache = None

        # Function to configure cache
        def set_cache(cache_instance):
            wrapper.cache = cache_instance
            return wrapper

        wrapper.set_cache = set_cache

        return wrapper

    return decorator
