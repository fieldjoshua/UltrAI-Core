"""
Advanced caching service for UltraAI Core with Redis support and fallback.
"""

import json
import hashlib
import time
from typing import Any, Optional, Dict, List, Callable
from datetime import datetime, timedelta
import asyncio
from functools import wraps

import redis.asyncio as redis
from redis.asyncio.retry import Retry
from redis.backoff import ExponentialBackoff
from redis.exceptions import RedisError, ConnectionError, TimeoutError

from app.config import Config
from app.utils.logging import get_logger

# Optional Prometheus metrics support
try:
    from prometheus_client import Counter, Gauge

    ULTRA_CACHE_HITS = Counter("ultra_cache_hits_total", "Total cache hits")
    ULTRA_CACHE_MISSES = Counter("ultra_cache_misses_total", "Total cache misses")
    ULTRA_CACHE_ERRORS = Counter("ultra_cache_errors_total", "Total cache errors")
    ULTRA_CACHE_MEMORY_FALLBACKS = Counter(
        "ultra_cache_memory_fallbacks_total", "Total memory fallback occurrences"
    )
    ULTRA_CACHE_MEMORY_SIZE = Gauge(
        "ultra_cache_memory_size", "Number of entries in in-memory cache"
    )
    ULTRA_CACHE_REDIS_AVAILABLE = Gauge(
        "ultra_cache_redis_available", "1 if Redis available, else 0"
    )
except Exception:  # pragma: no cover - metrics are optional
    ULTRA_CACHE_HITS = None
    ULTRA_CACHE_MISSES = None
    ULTRA_CACHE_ERRORS = None
    ULTRA_CACHE_MEMORY_FALLBACKS = None
    ULTRA_CACHE_MEMORY_SIZE = None
    ULTRA_CACHE_REDIS_AVAILABLE = None

logger = get_logger("cache_service")


class CacheService:
    """Advanced caching service with Redis and in-memory fallback."""
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.memory_cache: Dict[str, Dict[str, Any]] = {}
        self.cache_stats = {
            "hits": 0,
            "misses": 0,
            "errors": 0,
            "memory_fallbacks": 0
        }
        self._initialize_redis()
    
    def is_redis_available(self) -> bool:
        """Return True if Redis client is initialized and available."""
        return self.redis_client is not None
    
    def _initialize_redis(self):
        """Initialize Redis connection with retry logic."""
        if not Config.ENABLE_CACHE or not Config.REDIS_URL:
            logger.info("Cache disabled or Redis URL not configured")
            return
        
        try:
            # Configure retry with exponential backoff
            retry = Retry(ExponentialBackoff(), retries=3)
            
            self.redis_client = redis.from_url(
                Config.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry=retry,
                retry_on_error=[ConnectionError, TimeoutError]
            )
            logger.info("Redis client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Redis client: {e}")
            self.redis_client = None
    
    def get(self, key: str, ignore_ttl: bool = False) -> Optional[Any]:
        """Synchronous get for unit tests and internal memory fallback."""
        try:
            # Memory cache path (used in tests or when Redis unavailable)
            if key in self.memory_cache:
                entry = self.memory_cache[key]
                if ignore_ttl or entry["expires_at"] > time.time():
                    self.cache_stats["memory_fallbacks"] += 1
                    if ULTRA_CACHE_MEMORY_FALLBACKS:
                        ULTRA_CACHE_MEMORY_FALLBACKS.inc()
                    if ULTRA_CACHE_HITS:
                        ULTRA_CACHE_HITS.inc()
                    return entry["value"]
                # Expired
                del self.memory_cache[key]

            self.cache_stats["misses"] += 1
            if ULTRA_CACHE_MISSES:
                ULTRA_CACHE_MISSES.inc()
            return None
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            self.cache_stats["errors"] += 1
            if ULTRA_CACHE_ERRORS:
                ULTRA_CACHE_ERRORS.inc()
            return None

    async def aget(self, key: str, ignore_ttl: bool = False) -> Optional[Any]:
        """Async get supporting Redis; falls back to memory."""
        try:
            if self.redis_client and not ignore_ttl:
                try:
                    value = await self.redis_client.get(key)
                    if value:
                        self.cache_stats["hits"] += 1
                        if ULTRA_CACHE_HITS:
                            ULTRA_CACHE_HITS.inc()
                        return json.loads(value)
                except (RedisError, ConnectionError) as e:
                    logger.warning(f"Redis get error, falling back to memory: {e}")
                    self.cache_stats["errors"] += 1
                    if ULTRA_CACHE_ERRORS:
                        ULTRA_CACHE_ERRORS.inc()
            return self.get(key, ignore_ttl=ignore_ttl)
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            self.cache_stats["errors"] += 1
            if ULTRA_CACHE_ERRORS:
                ULTRA_CACHE_ERRORS.inc()
            return None
    
    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Synchronous set into memory cache (test path)."""
        try:
            self.memory_cache[key] = {"value": value, "expires_at": time.time() + ttl}
            if ULTRA_CACHE_MEMORY_SIZE:
                ULTRA_CACHE_MEMORY_SIZE.set(len(self.memory_cache))
            return True
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            self.cache_stats["errors"] += 1
            if ULTRA_CACHE_ERRORS:
                ULTRA_CACHE_ERRORS.inc()
            return False

    async def aset(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Async set supporting Redis; falls back to memory."""
        try:
            serialized_value = json.dumps(value)
            if self.redis_client:
                try:
                    await self.redis_client.setex(key, ttl, serialized_value)
                    return True
                except (RedisError, ConnectionError) as e:
                    logger.warning(f"Redis set error, falling back to memory: {e}")
                    self.cache_stats["errors"] += 1
                    if ULTRA_CACHE_ERRORS:
                        ULTRA_CACHE_ERRORS.inc()
                    if ULTRA_CACHE_MEMORY_FALLBACKS:
                        ULTRA_CACHE_MEMORY_FALLBACKS.inc()
            return self.set(key, value, ttl)
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            self.cache_stats["errors"] += 1
            if ULTRA_CACHE_ERRORS:
                ULTRA_CACHE_ERRORS.inc()
            return False
    
    def delete(self, key: str) -> bool:
        """Synchronous delete from memory cache."""
        try:
            deleted = False
            if key in self.memory_cache:
                del self.memory_cache[key]
                deleted = True
            if ULTRA_CACHE_MEMORY_SIZE:
                ULTRA_CACHE_MEMORY_SIZE.set(len(self.memory_cache))
            return deleted
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False

    async def adelete(self, key: str) -> bool:
        """Async delete supporting Redis; falls back to memory."""
        try:
            if self.redis_client:
                try:
                    await self.redis_client.delete(key)
                except (RedisError, ConnectionError) as e:
                    logger.warning(f"Redis delete error: {e}")
            return self.delete(key)
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False
    
    async def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern."""
        count = 0
        
        try:
            # Clear from Redis
            if self.redis_client:
                try:
                    cursor = 0
                    while True:
                        cursor, keys = await self.redis_client.scan(
                            cursor, match=pattern, count=100
                        )
                        if keys:
                            await self.redis_client.delete(*keys)
                            count += len(keys)
                        if cursor == 0:
                            break
                except (RedisError, ConnectionError) as e:
                    logger.warning(f"Redis clear pattern error: {e}")
            
            # Clear from memory cache
            keys_to_delete = [k for k in self.memory_cache if pattern.replace('*', '') in k]
            for key in keys_to_delete:
                del self.memory_cache[key]
                count += 1
            
            return count
            
        except Exception as e:
            logger.error(f"Cache clear pattern error: {e}")
            return count
    
    async def _cleanup_memory_cache(self):
        """Clean up expired entries from memory cache."""
        current_time = time.time()
        expired_keys = [
            k for k, v in self.memory_cache.items() 
            if v["expires_at"] <= current_time
        ]
        
        for key in expired_keys:
            del self.memory_cache[key]
        
        logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")

    # --- Synchronous helpers expected by unit tests ---
    def exists(self, key: str) -> bool:
        return key in self.memory_cache and self.memory_cache[key]["expires_at"] > time.time()

    def increment(self, key: str, amount: int = 1) -> int:
        current = self.get(key) or 0
        new_val = int(current) + amount
        self.set(key, new_val)
        return new_val

    def flush(self) -> bool:
        self.memory_cache.clear()
        return True

    # --- JSON convenience (async) ---
    async def set_json(self, prefix: str, data: Dict[str, Any], payload: Any, ttl: int = 3600) -> bool:
        key = f"{prefix}:{hashlib.md5(json.dumps(data, sort_keys=True).encode()).hexdigest()}"
        return await self.aset(key, payload, ttl)

    async def get_json(self, prefix: str, data: Dict[str, Any]) -> Optional[Any]:
        key = f"{prefix}:{hashlib.md5(json.dumps(data, sort_keys=True).encode()).hexdigest()}"
        return await self.aget(key)

    async def exists_json(self, prefix: str, data: Dict[str, Any]) -> bool:
        return (await self.get_json(prefix, data)) is not None

    async def delete_json(self, prefix: str, data: Dict[str, Any]) -> bool:
        key = f"{prefix}:{hashlib.md5(json.dumps(data, sort_keys=True).encode()).hexdigest()}"
        return await self.adelete(key)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_requests = self.cache_stats["hits"] + self.cache_stats["misses"]
        hit_rate = (self.cache_stats["hits"] / total_requests * 100) if total_requests > 0 else 0

        # Update gauges if available
        if ULTRA_CACHE_MEMORY_SIZE:
            ULTRA_CACHE_MEMORY_SIZE.set(len(self.memory_cache))
        if ULTRA_CACHE_REDIS_AVAILABLE:
            ULTRA_CACHE_REDIS_AVAILABLE.set(1 if self.redis_client is not None else 0)

        return {
            **self.cache_stats,
            "hit_rate": round(hit_rate, 2),
            "memory_cache_size": len(self.memory_cache),
            "redis_available": self.redis_client is not None
        }
    
    async def close(self):
        """Close cache connections."""
        if self.redis_client:
            await self.redis_client.close()
            logger.info("Redis connection closed")


def cache_key(*args, **kwargs) -> str:
    """Generate cache key from arguments."""
    key_data = {
        "args": args,
        "kwargs": kwargs
    }
    key_string = json.dumps(key_data, sort_keys=True)
    return hashlib.md5(key_string.encode()).hexdigest()


def cached(ttl: int = 3600, key_prefix: str = ""):
    """Decorator for caching function results."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key_parts = [key_prefix, func.__name__]
            cache_key_parts.extend(str(arg) for arg in args)
            cache_key_parts.extend(f"{k}:{v}" for k, v in sorted(kwargs.items()))
            key = ":".join(cache_key_parts)
            
            # Get cache service from function's module
            cache_service = getattr(func.__module__, '_cache_service', None)
            if not cache_service:
                # No cache service available, just call function
                return await func(*args, **kwargs)
            
            # Try to get from cache
            cached_value = await cache_service.get(key)
            if cached_value is not None:
                logger.debug(f"Cache hit for {func.__name__}")
                return cached_value
            
            # Call function and cache result
            result = await func(*args, **kwargs)
            await cache_service.set(key, result, ttl)
            
            return result
        
        return wrapper
    return decorator


# Global cache service instance
_cache_service: Optional[CacheService] = None


def get_cache_service() -> CacheService:
    """Get or create cache service instance."""
    global _cache_service
    if _cache_service is None:
        _cache_service = CacheService()
    return _cache_service


async def close_cache_service():
    """Close cache service connections."""
    global _cache_service
    if _cache_service:
        await _cache_service.close()
        _cache_service = None

# Backward-compatible alias for modules importing `cache_service`
# This provides a ready-to-use singleton instance.
cache_service: CacheService = get_cache_service()