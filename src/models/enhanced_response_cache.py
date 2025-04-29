"""
Enhanced Response Cache Module.

This module provides an improved caching system for model responses with tiered storage,
adaptive TTL, and intelligent cache warming capabilities.
"""

import hashlib
import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, AsyncGenerator

from src.data.cache.unified_cache import CacheConfig, CacheLevel, UnifiedCache
from src.models import ModelResponse


class CacheStatus(Enum):
    """Status of a cache operation."""

    HIT = "hit"
    MISS = "miss"
    EXPIRED = "expired"
    ERROR = "error"


@dataclass
class CacheOperationResult:
    """Result of a cache operation."""

    status: CacheStatus
    source: Optional[str] = None  # "memory", "disk", "distributed", None if miss
    key: Optional[str] = None
    response: Optional[ModelResponse] = None
    latency_ms: float = 0.0


class EnhancedResponseCache:
    """
    Enhanced cache for model responses with tiered storage and intelligent features.

    Features:
    - Multi-level caching (memory, disk, distributed)
    - Adaptive TTL based on response quality and popularity
    - Intelligent cache warming for frequent patterns
    - Advanced metrics collection
    - Cache stability tracking
    - Support for streaming response caching
    """

    def __init__(
        self,
        memory_cache_size_mb: int = 512,
        disk_cache_enabled: bool = True,
        disk_cache_size_mb: int = 1024,
        default_ttl_seconds: int = 3600,
        frequency_boost_enabled: bool = True,
        quality_boost_enabled: bool = True,
        cache_warming_enabled: bool = True,
        distributed_cache_enabled: bool = False,
    ):
        """
        Initialize the enhanced response cache.

        Args:
            memory_cache_size_mb: Memory cache size in MB
            disk_cache_enabled: Whether to enable disk caching
            disk_cache_size_mb: Disk cache size in MB
            default_ttl_seconds: Default TTL in seconds
            frequency_boost_enabled: Whether to extend TTL for frequently accessed items
            quality_boost_enabled: Whether to extend TTL for high-quality responses
            cache_warming_enabled: Whether to enable proactive cache warming
            distributed_cache_enabled: Whether to enable distributed caching
        """
        self.logger = logging.getLogger(__name__)

        # Configure the unified cache
        unified_config = CacheConfig(
            memory_cache_size_mb=memory_cache_size_mb,
            disk_cache_enabled=disk_cache_enabled,
            disk_cache_max_size_mb=disk_cache_size_mb,
            default_ttl_seconds=default_ttl_seconds,
            collect_metrics=True,
        )

        # Create unified cache instance
        self.cache = UnifiedCache(unified_config)
        self.default_ttl_seconds = default_ttl_seconds

        # Feature flags
        self.frequency_boost_enabled = frequency_boost_enabled
        self.quality_boost_enabled = quality_boost_enabled
        self.cache_warming_enabled = cache_warming_enabled
        self.distributed_cache_enabled = distributed_cache_enabled

        # Cache namespaces for organization
        self.response_namespace = "model_responses"
        self.meta_namespace = "cache_metadata"

        # Tracking for frequency boost
        self.access_counts: Dict[str, int] = {}
        self.last_access_times: Dict[str, float] = {}

        # Tracking for pattern warming
        self.pattern_usage: Dict[str, int] = {}
        self.model_stage_frequency: Dict[Tuple[str, str], int] = {}

        # Performance monitoring
        self.total_hits = 0
        self.total_misses = 0
        self.operation_latencies: List[float] = []

        # Warm-up tracking
        self.warm_candidates: Set[str] = set()
        self.last_warm_time = time.time()
        self.warm_interval_seconds = 300  # 5 minutes

        self.logger.info(
            f"Enhanced response cache initialized: "
            f"memory={memory_cache_size_mb}MB, "
            f"disk={'enabled' if disk_cache_enabled else 'disabled'}"
        )

    def _generate_cache_key(self, model_name: str, stage: str, prompt_hash: str) -> str:
        """
        Generate a standardized cache key.

        Args:
            model_name: The name of the model
            stage: The processing stage
            prompt_hash: Hash of the prompt

        Returns:
            Standardized cache key
        """
        combined = f"{model_name}:{stage}:{prompt_hash}"
        # Using MD5 for cache key generation only, not for security purposes
        return hashlib.md5(combined.encode(), usedforsecurity=False).hexdigest()

    def _calculate_adaptive_ttl(self, response: ModelResponse) -> int:
        """
        Calculate adaptive TTL based on response quality and access frequency.

        Args:
            response: The model response

        Returns:
            TTL in seconds
        """
        ttl = self.default_ttl_seconds

        # Quality boost - higher quality responses get longer TTL
        if self.quality_boost_enabled and response.quality:
            quality_score = (
                response.quality.coherence_score
                + response.quality.technical_depth
                + response.quality.strategic_value
                + response.quality.uniqueness
            ) / 4

            # Boost TTL up to 2x for high quality responses
            quality_multiplier = 1.0 + quality_score
            ttl = int(ttl * min(quality_multiplier, 2.0))

        # Frequency boost - frequently accessed responses get longer TTL
        key = self._generate_cache_key(
            response.model,
            "stage",  # We don't have stage in response, so using a placeholder
            str(hash(response.prompt)),
        )

        if self.frequency_boost_enabled and key in self.access_counts:
            # Boost TTL up to 3x for frequently accessed responses
            access_count = self.access_counts.get(key, 0)
            frequency_multiplier = min(1.0 + (access_count * 0.1), 3.0)
            ttl = int(ttl * frequency_multiplier)

        return ttl

    def _update_access_stats(self, key: str) -> None:
        """
        Update access statistics for a key.

        Args:
            key: The cache key
        """
        current_time = time.time()

        # Update access count and time
        self.access_counts[key] = self.access_counts.get(key, 0) + 1
        self.last_access_times[key] = current_time

        # Add to warm candidates if accessed frequently
        if self.access_counts[key] >= 3:
            self.warm_candidates.add(key)

    def _parse_key_components(self, key: str) -> Tuple[str, str, str]:
        """
        Parse model, stage, and prompt hash from a cache key.

        Args:
            key: The cache key

        Returns:
            Tuple of (model_name, stage, prompt_hash)
        """
        try:
            # This is a heuristic to get the original components
            # In a real implementation, we might store this metadata separately
            original_key = self.cache.get(key, namespace=self.meta_namespace)
            if original_key:
                return tuple(original_key.split(":"))

            # Fallback to empty components
            return ("unknown", "unknown", "unknown")
        except Exception as e:
            self.logger.error(f"Error parsing key components: {e}")
            return ("unknown", "unknown", "unknown")

    def _warm_cache_if_needed(self) -> None:
        """Proactively warm the cache for frequently accessed patterns."""
        if not self.cache_warming_enabled:
            return

        current_time = time.time()
        if current_time - self.last_warm_time < self.warm_interval_seconds:
            return

        self.last_warm_time = current_time

        # Process a limited number of warm candidates
        processed = 0
        for key in list(self.warm_candidates)[:10]:
            try:
                # Check if the item is already in memory
                if self.cache.exists(key, namespace=self.response_namespace):
                    disk_result = self.cache.get(key, namespace=self.response_namespace)

                    # If it exists, refresh its TTL to keep it longer
                    if disk_result:
                        model, stage, _ = self._parse_key_components(key)

                        # Record the model and stage frequency
                        model_stage_key = (model, stage)
                        self.model_stage_frequency[model_stage_key] = (
                            self.model_stage_frequency.get(model_stage_key, 0) + 1
                        )

                        # Make sure it's in memory by getting it again
                        self.cache.get(key, namespace=self.response_namespace)

                self.warm_candidates.remove(key)
                processed += 1

            except Exception as e:
                self.logger.error(f"Error warming cache for key {key}: {e}")
                self.warm_candidates.remove(key)

        if processed > 0:
            self.logger.info(f"Warmed cache for {processed} items")

    def get(self, key: str) -> Optional[ModelResponse]:
        """
        Get a response from the cache.

        Args:
            key: The cache key

        Returns:
            The cached response, or None if not found
        """
        start_time = time.time()

        try:
            # Check if we need to warm the cache
            self._warm_cache_if_needed()

            # Try to get from unified cache
            result = self.cache.get(key, namespace=self.response_namespace)

            if result:
                # Record as hit
                self.total_hits += 1
                self._update_access_stats(key)

                # Record latency
                latency_ms = (time.time() - start_time) * 1000
                self.operation_latencies.append(latency_ms)

                return result
            else:
                # Record as miss
                self.total_misses += 1
                return None

        except Exception as e:
            self.logger.error(f"Error getting cached response for key {key}: {e}")
            return None

    def set(self, key: str, response: ModelResponse) -> None:
        """
        Add a response to the cache.

        Args:
            key: The cache key
            response: The response to cache
        """
        start_time = time.time()

        try:
            # Calculate adaptive TTL
            ttl = self._calculate_adaptive_ttl(response)

            # Store the original key components for reference
            original_components = f"{response.model}:stage:{hash(response.prompt)}"
            self.cache.set(
                key, original_components, ttl_seconds=ttl, namespace=self.meta_namespace
            )

            # Determine appropriate cache level based on response size
            # Large responses might only go to disk to save memory
            content_size = len(response.content)

            if content_size > 100000:  # If content is larger than 100KB
                cache_level = CacheLevel.DISK
            else:
                cache_level = CacheLevel.BOTH

            # Store the response
            self.cache.set(
                key,
                response,
                ttl_seconds=ttl,
                namespace=self.response_namespace,
                cache_level=cache_level,
            )

            # Record latency
            latency_ms = (time.time() - start_time) * 1000
            self.operation_latencies.append(latency_ms)

        except Exception as e:
            self.logger.error(f"Error caching response for key {key}: {e}")

    def clear_expired(self) -> None:
        """Clear expired cache entries."""
        try:
            # This is handled automatically by UnifiedCache's _check_expiry method
            # But we can force an immediate check
            self.cache._check_expiry(force=True)

            # Also clean up our tracking dictionaries
            current_time = time.time()
            expired_time = current_time - (self.default_ttl_seconds * 2)

            # Remove old access stats
            access_keys = list(self.last_access_times.keys())
            for key in access_keys:
                if self.last_access_times[key] < expired_time:
                    self.last_access_times.pop(key, None)
                    self.access_counts.pop(key, None)

        except Exception as e:
            self.logger.error(f"Error clearing expired cache entries: {e}")

    def get_metrics(self) -> Dict[str, Any]:
        """
        Get cache metrics.

        Returns:
            Dictionary with cache metrics
        """
        # Get metrics from the unified cache
        unified_metrics = self.cache.get_metrics()

        # Calculate our own metrics
        total_ops = self.total_hits + self.total_misses
        hit_ratio = self.total_hits / total_ops if total_ops > 0 else 0

        avg_latency = (
            sum(self.operation_latencies) / len(self.operation_latencies)
            if self.operation_latencies
            else 0
        )

        # Combined metrics
        return {
            **unified_metrics,
            "enhanced_metrics": {
                "total_hits": self.total_hits,
                "total_misses": self.total_misses,
                "hit_ratio": hit_ratio,
                "avg_latency_ms": avg_latency,
                "tracked_items": len(self.access_counts),
                "warm_candidates": len(self.warm_candidates),
                "model_stage_pairs": len(self.model_stage_frequency),
            },
        }

    def get_pattern_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about pattern usage.

        Returns:
            Dictionary with pattern statistics
        """
        # Sort model_stage_frequency by frequency
        sorted_pairs = sorted(
            self.model_stage_frequency.items(), key=lambda x: x[1], reverse=True
        )

        # Convert to dictionary for JSON serialization
        top_pairs = {
            f"{model}:{stage}": freq for (model, stage), freq in sorted_pairs[:10]
        }

        return {
            "top_model_stage_pairs": top_pairs,
            "total_tracked_pairs": len(self.model_stage_frequency),
        }

    def optimize(self) -> None:
        """Optimize the cache based on usage patterns."""
        # Perform cache optimization tasks
        try:
            # 1. Clear expired entries
            self.clear_expired()

            # 2. Prune rarely accessed entries
            if len(self.access_counts) > 1000:
                # Sort by access count and keep only the top 1000
                sorted_keys = sorted(
                    self.access_counts.items(), key=lambda x: x[1], reverse=True
                )

                for key, _ in sorted_keys[1000:]:
                    self.access_counts.pop(key, None)
                    self.last_access_times.pop(key, None)

            # 3. Clear operation latencies if too many
            if len(self.operation_latencies) > 10000:
                self.operation_latencies = self.operation_latencies[-1000:]

            self.logger.info("Cache optimization completed")

        except Exception as e:
            self.logger.error(f"Error optimizing cache: {e}")

    def generate_stream_cache_key(
        self, model_name: str, stage: str, prompt_hash: str
    ) -> str:
        """
        Generate a standardized cache key for streaming responses.

        Args:
            model_name: The name of the model
            stage: The processing stage
            prompt_hash: Hash of the prompt

        Returns:
            Standardized cache key with stream identifier
        """
        combined = f"stream:{model_name}:{stage}:{prompt_hash}"
        return hashlib.md5(combined.encode(), usedforsecurity=False).hexdigest()

    async def get_stream(self, key: str) -> Optional[AsyncGenerator[str, None]]:
        """
        Get a streaming response from the cache.

        Args:
            key: The cache key

        Returns:
            An async generator yielding cached chunks, or None if not found
        """
        start_time = time.time()

        try:
            # Check if the cached response exists
            stream_marker = self.cache.get(key, namespace=self.response_namespace)

            if not stream_marker:
                # Record as miss
                self.total_misses += 1
                return None

            # If we have a cached stream, get the number of chunks
            chunk_count_key = f"{key}:count"
            chunk_count = self.cache.get(chunk_count_key, namespace=self.meta_namespace)

            if not chunk_count or chunk_count <= 0:
                # Invalid or corrupted cache entry
                self.logger.warning(f"Invalid stream cache entry for key {key}")
                return None

            # Record as hit
            self.total_hits += 1
            self._update_access_stats(key)

            # Record latency for the first hit
            latency_ms = (time.time() - start_time) * 1000
            self.operation_latencies.append(latency_ms)

            # Define an async generator to yield the cached chunks
            async def stream_generator():
                for i in range(chunk_count):
                    chunk_key = f"{key}:chunk:{i}"
                    chunk = self.cache.get(chunk_key, namespace=self.response_namespace)
                    if chunk:
                        yield chunk

            return stream_generator()

        except Exception as e:
            self.logger.error(f"Error getting cached stream for key {key}: {e}")
            return None

    async def set_stream(
        self,
        key: str,
        chunks: List[str],
        response_info: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Add a streaming response to the cache.

        Args:
            key: The cache key
            chunks: List of content chunks from the streaming response
            response_info: Optional metadata about the response
        """
        start_time = time.time()

        try:
            # Calculate adaptive TTL based on response metadata if available
            ttl = self.default_ttl_seconds
            if response_info and "model" in response_info:
                # Create a basic model response object for TTL calculation
                basic_response = ModelResponse(
                    model=response_info.get("model", "unknown"),
                    content="".join(chunks),
                    prompt=response_info.get("prompt", ""),
                    timestamp=time.time(),
                    tokens_used=response_info.get("tokens_used", 0),
                )
                ttl = self._calculate_adaptive_ttl(basic_response)

            # Store a stream marker
            self.cache.set(
                key,
                "stream",
                ttl_seconds=ttl,
                namespace=self.response_namespace,
                cache_level=CacheLevel.BOTH,
            )

            # Store count of chunks
            chunk_count_key = f"{key}:count"
            self.cache.set(
                chunk_count_key,
                len(chunks),
                ttl_seconds=ttl,
                namespace=self.meta_namespace,
            )

            # Store each chunk separately
            for i, chunk in enumerate(chunks):
                chunk_key = f"{key}:chunk:{i}"
                self.cache.set(
                    chunk_key,
                    chunk,
                    ttl_seconds=ttl,
                    namespace=self.response_namespace,
                    cache_level=CacheLevel.BOTH,
                )

            # Store original components for reference
            if response_info and "model" in response_info:
                original_components = (
                    f"{response_info.get('model')}:"
                    f"{response_info.get('stage', 'unknown')}:"
                    f"{hash(response_info.get('prompt', ''))}"
                )
                self.cache.set(
                    f"{key}:info",
                    original_components,
                    ttl_seconds=ttl,
                    namespace=self.meta_namespace,
                )

            # Record latency
            latency_ms = (time.time() - start_time) * 1000
            self.operation_latencies.append(latency_ms)

        except Exception as e:
            self.logger.error(f"Error caching streaming response for key {key}: {e}")
