"""
Cache Factory Module.

This module provides a factory for creating and managing cache instances
with different configurations for various parts of the application.
"""

import logging
from typing import Dict, Optional

from src.data.cache.unified_cache import CacheConfig, UnifiedCache
from src.models.enhanced_response_cache import EnhancedResponseCache


class CacheFactory:
    """
    Factory for creating and managing cache instances.

    This class implements the singleton pattern to ensure only one instance
    of each cache type exists per configuration.
    """

    # Class variables to store singleton instances
    _response_cache_instances: Dict[str, EnhancedResponseCache] = {}
    _unified_cache_instances: Dict[str, UnifiedCache] = {}
    _logger = logging.getLogger(__name__)

    @classmethod
    def get_response_cache(
        cls,
        name: str = "default",
        memory_cache_size_mb: int = 512,
        disk_cache_enabled: bool = True,
        disk_cache_size_mb: int = 1024,
        default_ttl_seconds: int = 3600,
        frequency_boost_enabled: bool = True,
        quality_boost_enabled: bool = True,
        cache_warming_enabled: bool = True,
    ) -> EnhancedResponseCache:
        """
        Get or create an EnhancedResponseCache instance.

        Args:
            name: Name of the cache instance
            memory_cache_size_mb: Memory cache size in MB
            disk_cache_enabled: Whether to enable disk caching
            disk_cache_size_mb: Disk cache size in MB
            default_ttl_seconds: Default TTL in seconds
            frequency_boost_enabled: Whether to extend TTL for frequently accessed items
            quality_boost_enabled: Whether to extend TTL for high-quality responses
            cache_warming_enabled: Whether to enable proactive cache warming

        Returns:
            EnhancedResponseCache instance
        """
        if name not in cls._response_cache_instances:
            cls._logger.info(f"Creating new EnhancedResponseCache instance: {name}")

            cache = EnhancedResponseCache(
                memory_cache_size_mb=memory_cache_size_mb,
                disk_cache_enabled=disk_cache_enabled,
                disk_cache_size_mb=disk_cache_size_mb,
                default_ttl_seconds=default_ttl_seconds,
                frequency_boost_enabled=frequency_boost_enabled,
                quality_boost_enabled=quality_boost_enabled,
                cache_warming_enabled=cache_warming_enabled,
            )

            cls._response_cache_instances[name] = cache

        return cls._response_cache_instances[name]

    @classmethod
    def get_unified_cache(
        cls,
        name: str = "default",
        config: Optional[CacheConfig] = None,
    ) -> UnifiedCache:
        """
        Get or create a UnifiedCache instance.

        Args:
            name: Name of the cache instance
            config: Optional configuration for the cache

        Returns:
            UnifiedCache instance
        """
        if name not in cls._unified_cache_instances:
            cls._logger.info(f"Creating new UnifiedCache instance: {name}")

            if config is None:
                config = CacheConfig()

            cache = UnifiedCache(config)
            cls._unified_cache_instances[name] = cache

        return cls._unified_cache_instances[name]

    @classmethod
    def get_orchestrator_cache(cls) -> EnhancedResponseCache:
        """
        Get a preconfigured cache instance for the Orchestrator.

        Returns:
            EnhancedResponseCache instance optimized for orchestrator use
        """
        return cls.get_response_cache(
            name="orchestrator",
            memory_cache_size_mb=768,  # Larger memory cache for orchestrator
            disk_cache_enabled=True,
            disk_cache_size_mb=2048,  # 2GB disk cache
            default_ttl_seconds=7200,  # 2 hours default TTL
            frequency_boost_enabled=True,
            quality_boost_enabled=True,
            cache_warming_enabled=True,
        )

    @classmethod
    def get_all_metrics(cls) -> Dict[str, Dict]:
        """
        Get metrics for all cache instances.

        Returns:
            Dictionary with metrics for all cache instances
        """
        metrics = {}

        # Get metrics for response caches
        for name, cache in cls._response_cache_instances.items():
            metrics[f"response_cache_{name}"] = cache.get_metrics()

        # Get metrics for unified caches
        for name, cache in cls._unified_cache_instances.items():
            metrics[f"unified_cache_{name}"] = cache.get_metrics()

        return metrics

    @classmethod
    def optimize_all_caches(cls) -> None:
        """Optimize all cache instances."""
        cls._logger.info("Optimizing all cache instances")

        # Optimize response caches
        for name, cache in cls._response_cache_instances.items():
            try:
                cache.optimize()
                cls._logger.info(f"Optimized response cache: {name}")
            except Exception as e:
                cls._logger.error(f"Error optimizing response cache {name}: {e}")
