import hashlib
import logging
import os
import pickle  # nosec B403 # Pickle is used only for internal cache data that is not exposed to users
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from threading import Lock
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd


class CacheLevel(Enum):
    """Cache level determines where data is stored."""

    MEMORY = "memory"  # Memory only
    DISK = "disk"  # Disk only
    BOTH = "both"  # Both memory and disk


@dataclass
class CacheConfig:
    """Configuration for the unified cache system."""

    # Memory cache settings
    memory_cache_size_mb: int = 512
    memory_cache_eviction_policy: str = "lru"  # lru, fifo, lfu

    # Disk cache settings
    disk_cache_enabled: bool = True
    disk_cache_dir: str = "src/data/cache/disk_cache"
    disk_cache_max_size_mb: int = 1024

    # TTL settings
    default_ttl_seconds: int = 3600  # 1 hour
    check_expiry_interval: int = 60  # Check expiry every 60 seconds

    # Compression settings
    compress_disk_cache: bool = True
    compression_threshold_kb: int = 100  # Compress if item is larger than this

    # Validation
    validate_cache_integrity: bool = True

    # Monitoring
    collect_metrics: bool = True


@dataclass
class CacheMetrics:
    """Metrics for cache performance monitoring."""

    hits: int = 0
    misses: int = 0
    memory_hits: int = 0
    disk_hits: int = 0
    evictions: int = 0
    errors: int = 0
    total_items: int = 0
    memory_size_bytes: int = 0
    disk_size_bytes: int = 0
    write_time_ms: List[float] = field(default_factory=list)
    read_time_ms: List[float] = field(default_factory=list)

    def get_hit_ratio(self) -> float:
        """Calculate hit ratio."""
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0

    def get_avg_write_time(self) -> float:
        """Calculate average write time in ms."""
        return (
            sum(self.write_time_ms) / len(self.write_time_ms)
            if self.write_time_ms
            else 0
        )

    def get_avg_read_time(self) -> float:
        """Calculate average read time in ms."""
        return (
            sum(self.read_time_ms) / len(self.read_time_ms) if self.read_time_ms else 0
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        return {
            "hits": self.hits,
            "misses": self.misses,
            "hit_ratio": self.get_hit_ratio(),
            "memory_hits": self.memory_hits,
            "disk_hits": self.disk_hits,
            "evictions": self.evictions,
            "errors": self.errors,
            "total_items": self.total_items,
            "memory_size_mb": self.memory_size_bytes / (1024 * 1024),
            "disk_size_mb": self.disk_size_bytes / (1024 * 1024),
            "avg_write_time_ms": self.get_avg_write_time(),
            "avg_read_time_ms": self.get_avg_read_time(),
        }


class UnifiedCache:
    """
    Unified caching system with memory and disk storage.

    Features:
    - Hierarchical cache (memory and disk)
    - Configurable TTL for entries
    - Automatic cache invalidation
    - Size-based eviction policies
    - Metrics collection
    - Thread-safe operations
    - Support for complex data types
    """

    def __init__(self, config: Optional[CacheConfig] = None):
        """Initialize the cache with optional configuration."""
        self.config = config or CacheConfig()
        self.logger = logging.getLogger(__name__)

        # Initialize caches
        self.memory_cache: Dict[str, Dict[str, Any]] = {}
        self.memory_cache_size = 0
        self.last_access_time: Dict[str, float] = {}  # For LRU
        self.access_frequency: Dict[str, int] = {}  # For LFU

        # Create disk cache directory if enabled
        if self.config.disk_cache_enabled:
            os.makedirs(self.config.disk_cache_dir, exist_ok=True)

        # Thread safety
        self.lock = Lock()

        # Metrics
        self.metrics = CacheMetrics()

        # Last expiry check
        self.last_expiry_check = time.time()

        self.logger.info(f"Initialized UnifiedCache with config: {self.config}")

    def _generate_key(self, key: str, namespace: str = "default") -> str:
        """Generate a standardized cache key."""
        combined = f"{namespace}:{key}"
        # Using MD5 for cache key generation only, not for security purposes
        return hashlib.md5(combined.encode(), usedforsecurity=False).hexdigest()

    def _get_disk_path(self, key: str) -> Path:
        """Get the path to the disk cache file for a key."""
        # Create subdirectories based on the first 2 chars of the key for better file distribution
        subdir = key[:2]
        directory = Path(self.config.disk_cache_dir) / subdir
        directory.mkdir(exist_ok=True)
        return directory / f"{key}.cache"

    def _check_expiry(self, force: bool = False) -> None:
        """Check and remove expired items from cache."""
        current_time = time.time()

        # Only check if interval has passed or forced
        if not force and (
            current_time - self.last_expiry_check < self.config.check_expiry_interval
        ):
            return

        self.last_expiry_check = current_time

        # Check memory cache
        with self.lock:
            expired_keys = []
            for key, item in self.memory_cache.items():
                if item["expiry"] < current_time:
                    expired_keys.append(key)

            # Remove expired items
            for key in expired_keys:
                self._remove_from_memory(key)

        # Check disk cache if enabled
        if self.config.disk_cache_enabled:
            cache_dir = Path(self.config.disk_cache_dir)
            for subdir in cache_dir.iterdir():
                if not subdir.is_dir():
                    continue

                for cache_file in subdir.glob("*.cache"):
                    try:
                        with open(cache_file, "rb") as f:
                            metadata = pickle.load(
                                f
                            )  # nosec B301 # Cache files are internally generated and not user-provided
                            if metadata["expiry"] < current_time:
                                cache_file.unlink()
                    except Exception as e:
                        self.logger.error(
                            f"Error checking disk cache expiry for {cache_file}: {e}"
                        )
                        self.metrics.errors += 1
                        # Remove corrupted file
                        if self.config.validate_cache_integrity:
                            try:
                                cache_file.unlink()
                            except Exception:
                                self.logger.error(
                                    f"Failed to remove corrupted cache file: {cache_file}"
                                )

    def _update_metrics(self, operation: str, **kwargs) -> None:
        """Update cache metrics."""
        if not self.config.collect_metrics:
            return

        if operation == "hit":
            self.metrics.hits += 1
            if kwargs.get("source") == "memory":
                self.metrics.memory_hits += 1
            elif kwargs.get("source") == "disk":
                self.metrics.disk_hits += 1
        elif operation == "miss":
            self.metrics.misses += 1
        elif operation == "write":
            self.metrics.write_time_ms.append(kwargs.get("time_ms", 0))
        elif operation == "read":
            self.metrics.read_time_ms.append(kwargs.get("time_ms", 0))
        elif operation == "evict":
            self.metrics.evictions += 1
        elif operation == "error":
            self.metrics.errors += 1

        # Update size metrics
        self.metrics.memory_size_bytes = self.memory_cache_size

        # Update total items
        self.metrics.total_items = len(self.memory_cache)

        # Calculate disk size (expensive, do occasionally)
        if operation == "size_check" and self.config.disk_cache_enabled:
            try:
                total_size = 0
                cache_dir = Path(self.config.disk_cache_dir)
                for subdir in cache_dir.iterdir():
                    if not subdir.is_dir():
                        continue
                    for cache_file in subdir.glob("*.cache"):
                        total_size += cache_file.stat().st_size
                self.metrics.disk_size_bytes = total_size
            except Exception as e:
                self.logger.error(f"Error calculating disk cache size: {e}")

    def _remove_from_memory(self, key: str) -> None:
        """Remove an item from memory cache."""
        if key in self.memory_cache:
            item_size = self.memory_cache[key].get("size", 0)
            del self.memory_cache[key]
            self.memory_cache_size -= item_size

            # Clean up tracking dictionaries
            if key in self.last_access_time:
                del self.last_access_time[key]
            if key in self.access_frequency:
                del self.access_frequency[key]

            self._update_metrics("evict")

    def _evict_if_needed(self, required_space: int) -> None:
        """Evict items if memory cache is full."""
        if (
            self.memory_cache_size + required_space
            <= self.config.memory_cache_size_mb * 1024 * 1024
        ):
            return

        # Determine which eviction policy to use
        if self.config.memory_cache_eviction_policy == "lru":
            # Evict least recently used
            sorted_keys = sorted(self.last_access_time.items(), key=lambda x: x[1])

        elif self.config.memory_cache_eviction_policy == "lfu":
            # Evict least frequently used
            sorted_keys = sorted(self.access_frequency.items(), key=lambda x: x[1])

        else:  # Default to FIFO
            # Evict oldest items first
            sorted_keys = sorted(
                self.memory_cache.items(), key=lambda x: x[1]["created"]
            )
            sorted_keys = [(k, v["created"]) for k, v in sorted_keys]

        # Evict until we have enough space
        space_to_free = (
            self.memory_cache_size
            + required_space
            - (self.config.memory_cache_size_mb * 1024 * 1024)
        )
        freed_space = 0

        for key, _ in sorted_keys:
            if key in self.memory_cache:
                item_size = self.memory_cache[key].get("size", 0)
                self._remove_from_memory(key)
                freed_space += item_size
                if freed_space >= space_to_free:
                    break

    def _get_from_memory(self, key: str) -> Optional[Any]:
        """Get an item from memory cache."""
        if key not in self.memory_cache:
            return None

        item = self.memory_cache[key]

        # Check if expired
        if item["expiry"] < time.time():
            self._remove_from_memory(key)
            return None

        # Update access metrics
        current_time = time.time()
        self.last_access_time[key] = current_time
        self.access_frequency[key] = self.access_frequency.get(key, 0) + 1

        return item["value"]

    def _get_from_disk(self, key: str) -> Optional[Tuple[Any, int]]:
        """Get an item from disk cache."""
        if not self.config.disk_cache_enabled:
            return None

        disk_path = self._get_disk_path(key)
        if not disk_path.exists():
            return None

        try:
            start_time = time.time()
            with open(disk_path, "rb") as f:
                item_data = pickle.load(
                    f
                )  # nosec B301 # Cache files are internally generated and not user-provided

            # Check if expired
            if item_data["expiry"] < time.time():
                disk_path.unlink()
                return None

            read_time_ms = (time.time() - start_time) * 1000
            self._update_metrics("read", time_ms=read_time_ms)

            return item_data["value"], item_data.get("size", 0)

        except Exception as e:
            self.logger.error(f"Error reading from disk cache for key {key}: {e}")
            self._update_metrics("error")

            # Remove corrupted file
            if self.config.validate_cache_integrity:
                try:
                    disk_path.unlink()
                except Exception:
                    self.logger.error(
                        f"Failed to remove corrupted cache file: {disk_path}"
                    )

            return None

    def _save_to_disk(
        self, key: str, value: Any, expiry: float, item_size: int
    ) -> None:
        """Save an item to disk cache."""
        if not self.config.disk_cache_enabled:
            return

        disk_path = self._get_disk_path(key)

        try:
            start_time = time.time()

            # Prepare item data
            item_data = {
                "key": key,
                "value": value,
                "expiry": expiry,
                "created": time.time(),
                "size": item_size,
            }

            # Save to disk
            with open(disk_path, "wb") as f:
                pickle.dump(
                    item_data, f
                )  # nosec B301 # Internal cache serialization, not processing user data

            write_time_ms = (time.time() - start_time) * 1000
            self._update_metrics("write", time_ms=write_time_ms)

        except Exception as e:
            self.logger.error(f"Error writing to disk cache for key {key}: {e}")
            self._update_metrics("error")

            # Clean up failed writes
            try:
                if disk_path.exists():
                    disk_path.unlink()
            except Exception:
                self.logger.error(f"Failed to remove corrupted cache file: {disk_path}")

    def get(self, key: str, namespace: str = "default") -> Optional[Any]:
        """
        Get an item from the cache.

        Args:
            key: The cache key
            namespace: Optional namespace to organize keys

        Returns:
            The cached value or None if not found
        """
        # Generate standardized key
        cache_key = self._generate_key(key, namespace)

        # Periodically check for expired items
        self._check_expiry()

        # First try memory cache
        with self.lock:
            value = self._get_from_memory(cache_key)
            if value is not None:
                self._update_metrics("hit", source="memory")
                return value

        # Then try disk cache
        if self.config.disk_cache_enabled:
            result = self._get_from_disk(cache_key)
            if result is not None:
                value, size = result

                # Optionally store in memory for faster access
                with self.lock:
                    self._evict_if_needed(size)

                    # Calculate expiry time by checking disk cache
                    disk_path = self._get_disk_path(cache_key)
                    try:
                        with open(disk_path, "rb") as f:
                            item_data = pickle.load(
                                f
                            )  # nosec B301 # Cache files are internally generated and not user-provided
                            expiry = item_data["expiry"]
                    except Exception:
                        # Default to config TTL if we can't read expiry
                        expiry = time.time() + self.config.default_ttl_seconds

                    # Store in memory
                    self.memory_cache[cache_key] = {
                        "value": value,
                        "expiry": expiry,
                        "created": time.time(),
                        "size": size,
                    }

                    self.memory_cache_size += size
                    self.last_access_time[cache_key] = time.time()
                    self.access_frequency[cache_key] = 1

                self._update_metrics("hit", source="disk")
                return value

        # Not found in any cache
        self._update_metrics("miss")
        return None

    def set(
        self,
        key: str,
        value: Any,
        ttl_seconds: Optional[int] = None,
        namespace: str = "default",
        cache_level: CacheLevel = CacheLevel.BOTH,
    ) -> bool:
        """
        Set an item in the cache.

        Args:
            key: The cache key
            value: The value to cache
            ttl_seconds: Optional TTL in seconds (uses default if None)
            namespace: Optional namespace to organize keys
            cache_level: Where to store the item (memory, disk, or both)

        Returns:
            True if successful, False otherwise
        """
        # Generate standardized key
        cache_key = self._generate_key(key, namespace)

        # Calculate expiry time
        ttl = (
            ttl_seconds if ttl_seconds is not None else self.config.default_ttl_seconds
        )
        expiry = time.time() + ttl

        try:
            # Estimate size in bytes
            item_size = self._estimate_size(value)

            # Memory cache
            if cache_level in [CacheLevel.MEMORY, CacheLevel.BOTH]:
                with self.lock:
                    # Evict items if needed
                    self._evict_if_needed(item_size)

                    # Add to memory cache
                    self.memory_cache[cache_key] = {
                        "value": value,
                        "expiry": expiry,
                        "created": time.time(),
                        "size": item_size,
                    }

                    self.memory_cache_size += item_size
                    self.last_access_time[cache_key] = time.time()
                    self.access_frequency[cache_key] = 1

            # Disk cache
            if self.config.disk_cache_enabled and cache_level in [
                CacheLevel.DISK,
                CacheLevel.BOTH,
            ]:
                self._save_to_disk(cache_key, value, expiry, item_size)

            return True

        except Exception as e:
            self.logger.error(f"Error setting cache for key {key}: {e}")
            self._update_metrics("error")
            return False

    def delete(self, key: str, namespace: str = "default") -> bool:
        """
        Delete an item from the cache.

        Args:
            key: The cache key
            namespace: Optional namespace to organize keys

        Returns:
            True if successful, False otherwise
        """
        cache_key = self._generate_key(key, namespace)

        success = True

        # Remove from memory
        with self.lock:
            if cache_key in self.memory_cache:
                self._remove_from_memory(cache_key)

        # Remove from disk
        if self.config.disk_cache_enabled:
            disk_path = self._get_disk_path(cache_key)
            try:
                if disk_path.exists():
                    disk_path.unlink()
            except Exception as e:
                self.logger.error(f"Error deleting from disk cache for key {key}: {e}")
                self._update_metrics("error")
                success = False

        return success

    def clear(self, namespace: Optional[str] = None) -> bool:
        """
        Clear cache entries, optionally filtered by namespace.

        Args:
            namespace: Optional namespace to clear (clears all if None)

        Returns:
            True if successful, False otherwise
        """
        try:
            # Clear memory cache
            with self.lock:
                if namespace is None:
                    # Clear all
                    self.memory_cache.clear()
                    self.last_access_time.clear()
                    self.access_frequency.clear()
                    self.memory_cache_size = 0
                else:
                    # Clear only items in namespace
                    prefix = f"{namespace}:"
                    keys_to_remove = []

                    for key in self.memory_cache:
                        if key.startswith(prefix):
                            keys_to_remove.append(key)

                    for key in keys_to_remove:
                        self._remove_from_memory(key)

            # Clear disk cache
            if self.config.disk_cache_enabled:
                cache_dir = Path(self.config.disk_cache_dir)

                if namespace is None:
                    # Clear all subdirectories
                    for subdir in cache_dir.iterdir():
                        if subdir.is_dir():
                            for cache_file in subdir.glob("*.cache"):
                                cache_file.unlink()
                else:
                    # Clear only items in namespace
                    prefix = f"{namespace}:"
                    for subdir in cache_dir.iterdir():
                        if subdir.is_dir():
                            for cache_file in subdir.glob("*.cache"):
                                try:
                                    with open(cache_file, "rb") as f:
                                        item_data = pickle.load(
                                            f
                                        )  # nosec B301 # Cache files are internally generated and not user-provided
                                        if item_data["key"].startswith(prefix):
                                            cache_file.unlink()
                                except Exception:
                                    # If we can't read the file, delete it anyway
                                    try:
                                        cache_file.unlink()
                                    except Exception:
                                        self.logger.error(
                                            f"Failed to remove corrupted cache file: {cache_file}"
                                        )

            return True

        except Exception as e:
            self.logger.error(f"Error clearing cache: {e}")
            self._update_metrics("error")
            return False

    def _estimate_size(self, value: Any) -> int:
        """Estimate the size of a value in bytes."""
        if isinstance(value, (str, bytes)):
            return len(value)
        elif isinstance(value, pd.DataFrame):
            return value.memory_usage(deep=True).sum()
        else:
            try:
                # Try pickle - but only for size estimation of our own cache objects
                pickled = pickle.dumps(
                    value
                )  # nosec B301 # Used only for size estimation of internal objects
                return len(pickled)
            except Exception:
                # Fallback to a rough estimate
                import sys

                return sys.getsizeof(value)

    def get_metrics(self) -> Dict[str, Any]:
        """Get cache performance metrics."""
        if not self.config.collect_metrics:
            return {}

        # Update disk size metrics occasionally
        self._update_metrics("size_check")

        return self.metrics.to_dict()

    def get_keys(self, namespace: Optional[str] = None) -> List[str]:
        """
        Get all keys in the cache, optionally filtered by namespace.

        Args:
            namespace: Optional namespace to filter by

        Returns:
            List of keys
        """
        with self.lock:
            if namespace is None:
                return list(self.memory_cache.keys())
            else:
                prefix = f"{namespace}:"
                return [k for k in self.memory_cache.keys() if k.startswith(prefix)]

    def get_namespaces(self) -> List[str]:
        """
        Get all namespaces in the cache.

        Returns:
            List of namespace strings
        """
        with self.lock:
            namespaces = set()
            for key in self.memory_cache.keys():
                parts = key.split(":", 1)
                if len(parts) > 1:
                    namespaces.add(parts[0])
            return list(namespaces)

    def exists(self, key: str, namespace: str = "default") -> bool:
        """
        Check if a key exists in the cache.

        Args:
            key: The cache key
            namespace: Optional namespace to organize keys

        Returns:
            True if the key exists and is not expired, False otherwise
        """
        cache_key = self._generate_key(key, namespace)

        # Check memory cache
        with self.lock:
            if cache_key in self.memory_cache:
                item = self.memory_cache[cache_key]
                if item["expiry"] >= time.time():
                    return True
                else:
                    # Remove expired item
                    self._remove_from_memory(cache_key)

        # Check disk cache
        if self.config.disk_cache_enabled:
            disk_path = self._get_disk_path(cache_key)
            if disk_path.exists():
                try:
                    with open(disk_path, "rb") as f:
                        item_data = pickle.load(
                            f
                        )  # nosec B301 # Cache files are internally generated and not user-provided

                    if item_data["expiry"] >= time.time():
                        return True
                    else:
                        # Remove expired item
                        disk_path.unlink()
                except Exception:
                    # If we can't read the file, assume it's invalid
                    try:
                        disk_path.unlink()
                    except Exception:
                        self.logger.error(
                            f"Failed to remove corrupted cache file: {disk_path}"
                        )

        return False

    def refresh_ttl(
        self, key: str, namespace: str = "default", ttl_seconds: Optional[int] = None
    ) -> bool:
        """
        Refresh the TTL for an existing cache item.

        Args:
            key: The cache key
            namespace: Optional namespace to organize keys
            ttl_seconds: Optional new TTL in seconds (uses default if None)

        Returns:
            True if successful, False otherwise
        """
        # Get the value first
        value = self.get(key, namespace)
        if value is None:
            return False

        # Set with new TTL
        return self.set(key, value, ttl_seconds, namespace)

    def dump_to_disk(self) -> bool:
        """
        Dump all memory cache to disk for persistence.

        Returns:
            True if successful, False otherwise
        """
        if not self.config.disk_cache_enabled:
            return False

        success = True

        with self.lock:
            for key, item in self.memory_cache.items():
                try:
                    self._save_to_disk(key, item["value"], item["expiry"], item["size"])
                except Exception as e:
                    self.logger.error(f"Error dumping to disk for key {key}: {e}")
                    self._update_metrics("error")
                    success = False

        return success

    def load_from_disk(self) -> bool:
        """
        Load all disk cache into memory.

        Returns:
            True if successful, False otherwise
        """
        if not self.config.disk_cache_enabled:
            return False

        success = True
        cache_dir = Path(self.config.disk_cache_dir)

        with self.lock:
            # Clear memory cache first
            self.memory_cache.clear()
            self.last_access_time.clear()
            self.access_frequency.clear()
            self.memory_cache_size = 0

            # Load from disk
            for subdir in cache_dir.iterdir():
                if not subdir.is_dir():
                    continue

                for cache_file in subdir.glob("*.cache"):
                    try:
                        with open(cache_file, "rb") as f:
                            item_data = pickle.load(
                                f
                            )  # nosec B301 # Cache files are internally generated and not user-provided

                        # Skip expired items
                        if item_data["expiry"] < time.time():
                            cache_file.unlink()
                            continue

                        key = item_data["key"]
                        value = item_data["value"]
                        expiry = item_data["expiry"]
                        size = item_data.get("size", self._estimate_size(value))

                        # Add to memory cache if we have space
                        if (
                            self.memory_cache_size + size
                            <= self.config.memory_cache_size_mb * 1024 * 1024
                        ):
                            self.memory_cache[key] = {
                                "value": value,
                                "expiry": expiry,
                                "created": time.time(),
                                "size": size,
                            }

                            self.memory_cache_size += size
                            self.last_access_time[key] = time.time()
                            self.access_frequency[key] = 1

                    except Exception as e:
                        self.logger.error(
                            f"Error loading from disk for file {cache_file}: {e}"
                        )
                        self._update_metrics("error")
                        success = False

                        # Remove corrupted file
                        if self.config.validate_cache_integrity:
                            try:
                                cache_file.unlink()
                            except Exception:
                                self.logger.error(
                                    f"Failed to remove corrupted cache file: {cache_file}"
                                )

        return success

    def get_stats(self) -> Dict[str, Any]:
        """
        Get detailed statistics about the cache.

        Returns:
            Dictionary with cache statistics
        """
        with self.lock:
            memory_stats = {
                "total_items": len(self.memory_cache),
                "size_bytes": self.memory_cache_size,
                "size_mb": self.memory_cache_size / (1024 * 1024),
                "percent_full": (
                    self.memory_cache_size
                    / (self.config.memory_cache_size_mb * 1024 * 1024)
                )
                * 100,
                "keys": list(self.memory_cache.keys())[
                    :10
                ],  # Just the first 10 for brevity
            }

            disk_stats = {
                "enabled": self.config.disk_cache_enabled,
                "path": self.config.disk_cache_dir,
            }

            if self.config.disk_cache_enabled:
                # Count disk items
                cache_dir = Path(self.config.disk_cache_dir)
                disk_items = 0
                disk_size = 0

                try:
                    for subdir in cache_dir.iterdir():
                        if not subdir.is_dir():
                            continue
                        for cache_file in subdir.glob("*.cache"):
                            disk_items += 1
                            disk_size += cache_file.stat().st_size

                    disk_stats.update(
                        {
                            "total_items": disk_items,
                            "size_bytes": disk_size,
                            "size_mb": disk_size / (1024 * 1024),
                            "percent_full": (
                                disk_size
                                / (self.config.disk_cache_max_size_mb * 1024 * 1024)
                            )
                            * 100,
                        }
                    )
                except Exception as e:
                    self.logger.error(f"Error getting disk stats: {e}")
                    disk_stats.update({"error": str(e)})

            return {
                "memory_cache": memory_stats,
                "disk_cache": disk_stats,
                "metrics": self.get_metrics() if self.config.collect_metrics else {},
                "config": {
                    "memory_size_mb": self.config.memory_cache_size_mb,
                    "disk_size_mb": self.config.disk_cache_max_size_mb,
                    "default_ttl_seconds": self.config.default_ttl_seconds,
                    "eviction_policy": self.config.memory_cache_eviction_policy,
                },
            }
