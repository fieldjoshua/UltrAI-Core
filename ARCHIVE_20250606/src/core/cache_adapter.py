"""
Adapters for integrating UnifiedCache with existing caching systems.

This module provides adapters that allow the UnifiedCache to be used as
drop-in replacements for the existing caching systems in the codebase.
"""

import logging
from typing import Any, Dict, Optional

from src.data.cache.unified_cache import CacheConfig, UnifiedCache


class CacheManagerAdapter:
    """
    Adapter that makes UnifiedCache compatible with the CacheManager interface.

    This adapter allows UnifiedCache to be used as a drop-in replacement for
    the CacheManager class in src/core/ultra_performance.py.
    """

    def __init__(self, config=None):
        """
        Initialize the adapter.

        Args:
            config: Configuration object containing performance settings
        """
        self.logger = logging.getLogger(__name__)

        # Default cache size if config not provided
        cache_size_mb = 512
        if (
            config
            and hasattr(config, "performance")
            and hasattr(config.performance, "cache_size_mb")
        ):
            cache_size_mb = config.performance.cache_size_mb

        # Create UnifiedCache instance
        unified_config = CacheConfig(
            memory_cache_size_mb=cache_size_mb,
            disk_cache_enabled=True,
            default_ttl_seconds=3600,  # 1 hour
            collect_metrics=True,
        )
        self.cache = UnifiedCache(unified_config)
        self.namespace = "cache_manager"

        self.logger.info(
            f"CacheManagerAdapter initialized with cache size: {cache_size_mb}MB"
        )

    def add_to_cache(self, key: str, value: Any):
        """
        Add item to cache with size tracking.

        Args:
            key: Cache key
            value: Value to cache
        """
        try:
            self.cache.set(key, value, namespace=self.namespace)
        except Exception as e:
            self.logger.error(f"Failed to add item to cache: {e}")

    def get_from_cache(self, key: str) -> Optional[Any]:
        """
        Retrieve item from cache.

        Args:
            key: Cache key

        Returns:
            The cached value or None if not found
        """
        return self.cache.get(key, namespace=self.namespace)

    def clear_cache(self):
        """Clear all items from this adapter's namespace."""
        self.cache.clear(namespace=self.namespace)

    def get_metrics(self) -> Dict[str, Any]:
        """Get cache performance metrics."""
        return self.cache.get_metrics()


class ResponseCacheAdapter:
    """
    Adapter that makes UnifiedCache compatible with the ResponseCache interface.

    This adapter allows UnifiedCache to be used as a drop-in replacement for
    the ResponseCache class in src/models.py.
    """

    def __init__(
        self, max_age_hours: int = 24, unified_cache: Optional[UnifiedCache] = None
    ):
        """
        Initialize the adapter.

        Args:
            max_age_hours: Maximum age of cache entries in hours
            unified_cache: Optional shared UnifiedCache instance
        """
        self.logger = logging.getLogger(__name__)
        self.max_age_hours = max_age_hours

        if unified_cache:
            self.cache = unified_cache
        else:
            # Create a dedicated UnifiedCache instance
            unified_config = CacheConfig(
                memory_cache_size_mb=256,  # Smaller default size for response cache
                disk_cache_enabled=True,
                default_ttl_seconds=max_age_hours * 3600,
                collect_metrics=True,
            )
            self.cache = UnifiedCache(unified_config)

        self.namespace = "response_cache"
        self.logger.info(
            f"ResponseCacheAdapter initialized with TTL: {max_age_hours} hours"
        )

    def get(self, key: str) -> Optional[Any]:
        """
        Get a cached response.

        Args:
            key: Cache key

        Returns:
            The cached response or None if not found
        """
        response = self.cache.get(key, namespace=self.namespace)
        return response

    def set(self, key: str, response: Any):
        """
        Cache a response.

        Args:
            key: Cache key
            response: Response object to cache
        """
        self.cache.set(
            key,
            response,
            ttl_seconds=self.max_age_hours * 3600,
            namespace=self.namespace,
        )

    def clear_expired(self):
        """Clear expired cache entries."""
        # This is automatically handled by UnifiedCache's _check_expiry method
        # But we can force an immediate check
        self.cache._check_expiry(force=True)

    def get_metrics(self) -> Dict[str, Any]:
        """Get cache performance metrics."""
        return self.cache.get_metrics()


class UnifiedCacheFactory:
    """Factory class for creating and managing UnifiedCache instances."""

    _instances: Dict[str, UnifiedCache] = {}

    @classmethod
    def get_instance(
        cls, name: str = "default", config: Optional[CacheConfig] = None
    ) -> UnifiedCache:
        """
        Get or create a UnifiedCache instance.

        Args:
            name: Name of the cache instance
            config: Optional configuration for new instances

        Returns:
            UnifiedCache instance
        """
        if name not in cls._instances:
            if config is None:
                config = CacheConfig()
            cls._instances[name] = UnifiedCache(config)

        return cls._instances[name]

    @classmethod
    def get_metrics(cls) -> Dict[str, Dict[str, Any]]:
        """
        Get metrics for all cache instances.

        Returns:
            Dictionary mapping instance names to their metrics
        """
        return {
            name: instance.get_metrics() for name, instance in cls._instances.items()
        }
