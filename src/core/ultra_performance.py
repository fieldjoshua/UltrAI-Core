import os
import psutil
import torch
import logging
import platform
import time
import sys
from typing import Dict, Any, Optional, List
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from ultra_config import UltraConfig
from ultra_base import UltraBase

@dataclass
class PerformanceConfig:
    """Performance configuration settings."""
    max_memory_percent: float = 85.0
    max_cpu_percent: float = 90.0
    thread_pool_size: Optional[int] = None
    batch_size: int = 32
    cache_size_mb: int = 512
    gpu_memory_fraction: float = 0.8

class ResourceManager:
    """Manages system resources and optimization."""
    
    def __init__(self, config: UltraConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self._initialize_resources()
    
    def _initialize_resources(self):
        """Initialize resource management."""
        self.device = self._detect_device()
        self.cpu_count = psutil.cpu_count(logical=False)
        self.thread_pool = ThreadPoolExecutor(
            max_workers=self.cpu_count
        )
        self.process = psutil.Process()
        
        # Log initial resource state
        self.logger.info(f"Device: {self.device}")
        self.logger.info(f"CPU cores: {self.cpu_count}")
        self.logger.info(f"Total memory: {psutil.virtual_memory().total / (1024**3):.2f} GB")
    
    def _detect_device(self) -> str:
        """Detect and configure compute device."""
        if torch.backends.mps.is_available():
            device = "mps"
            torch.backends.mps.enable_fallback_to_cpu = True
        elif torch.cuda.is_available():
            device = "cuda"
            torch.backends.cudnn.benchmark = True
        else:
            device = "cpu"
        return device
    
    def get_resource_usage(self) -> Dict[str, float]:
        """Get current resource usage."""
        return {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent
        }
    
    def check_resource_availability(self) -> bool:
        """Check if resources are available."""
        usage = self.get_resource_usage()
        return (
            usage["cpu_percent"] < self.config.performance.max_cpu_percent and
            usage["memory_percent"] < self.config.performance.max_memory_percent
        )
    
    def optimize_batch_size(self, initial_batch_size: int) -> int:
        """Dynamically optimize batch size based on available resources."""
        if self.device == "cpu":
            # Reduce batch size on CPU
            return max(1, initial_batch_size // 2)
        return initial_batch_size

class CacheManager:
    """Manages memory and disk caching."""
    
    def __init__(self, config: UltraConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.cache = {}
        self.cache_size = 0
    
    def add_to_cache(self, key: str, value: Any):
        """Add item to cache with size tracking."""
        try:
            item_size = sys.getsizeof(value) / (1024 * 1024)  # Size in MB
            
            if self.cache_size + item_size > self.config.performance.cache_size_mb:
                self._evict_cache_items()
            
            self.cache[key] = value
            self.cache_size += item_size
        except Exception as e:
            self.logger.error(f"Failed to add item to cache: {e}")
    
    def get_from_cache(self, key: str) -> Optional[Any]:
        """Retrieve item from cache."""
        return self.cache.get(key)
    
    def _evict_cache_items(self):
        """Evict items from cache when full."""
        while self.cache and self.cache_size > self.config.performance.cache_size_mb * 0.8:
            key = next(iter(self.cache))
            item_size = sys.getsizeof(self.cache[key]) / (1024 * 1024)
            del self.cache[key]
            self.cache_size -= item_size

class HardwareOptimizer:
    """Optimizes code execution for specific hardware."""
    
    def __init__(self, config: UltraConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.device = self._detect_device()
        self._configure_hardware()
    
    def _detect_device(self) -> Dict[str, Any]:
        """Detect hardware capabilities."""
        return {
            "platform": platform.system(),
            "processor": platform.processor(),
            "machine": platform.machine(),
            "gpu_available": torch.backends.mps.is_available() or torch.cuda.is_available(),
            "cpu_cores": psutil.cpu_count(logical=False)
        }
    
    def _configure_hardware(self):
        """Configure hardware-specific optimizations."""
        if self.device["platform"] == "Darwin" and self.device["gpu_available"]:
            # Configure for Apple Silicon
            torch.backends.mps.enable_fallback_to_cpu = True
        elif torch.cuda.is_available():
            # Configure for NVIDIA GPU
            torch.backends.cudnn.benchmark = True
            torch.backends.cudnn.deterministic = False
    
    def get_optimal_settings(self) -> Dict[str, Any]:
        """Get optimal settings for current hardware."""
        settings = {
            "batch_size": self.config.performance.batch_size,
            "num_workers": self.device["cpu_cores"],
            "pin_memory": self.device["gpu_available"],
        }
        
        if self.device["gpu_available"]:
            settings["device"] = "mps" if self.device["platform"] == "Darwin" else "cuda"
        else:
            settings["device"] = "cpu"
        
        return settings

class PerformanceMonitor:
    """Monitors and reports performance metrics."""
    
    def __init__(self, config: UltraConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.metrics = {
            "cpu_usage": [],
            "memory_usage": [],
            "execution_times": [],
            "batch_sizes": [],
            "cache_hits": 0,
            "cache_misses": 0
        }
    
    def record_metric(self, metric_type: str, value: float):
        """Record a performance metric."""
        if metric_type in self.metrics:
            self.metrics[metric_type].append(value)
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get summary of performance metrics."""
        return {
            "avg_cpu_usage": sum(self.metrics["cpu_usage"]) / len(self.metrics["cpu_usage"]) if self.metrics["cpu_usage"] else 0,
            "avg_memory_usage": sum(self.metrics["memory_usage"]) / len(self.metrics["memory_usage"]) if self.metrics["memory_usage"] else 0,
            "avg_execution_time": sum(self.metrics["execution_times"]) / len(self.metrics["execution_times"]) if self.metrics["execution_times"] else 0,
            "cache_hit_ratio": self.metrics["cache_hits"] / (self.metrics["cache_hits"] + self.metrics["cache_misses"]) if (self.metrics["cache_hits"] + self.metrics["cache_misses"]) > 0 else 0
        }
    
    def log_performance_alert(self, metric_type: str, value: float, threshold: float):
        """Log performance alerts when thresholds are exceeded."""
        if value > threshold:
            self.logger.warning(
                f"Performance alert: {metric_type} exceeded threshold "
                f"(value: {value:.2f}, threshold: {threshold:.2f})"
            ) 