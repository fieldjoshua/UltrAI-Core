"""
Resource Manager for the EnhancedOrchestrator

This module implements adaptive resource management capabilities to optimize
resource allocation based on workload patterns and system load.
"""

import logging
import os
import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple

import psutil

logger = logging.getLogger(__name__)


class ResourcePriority(Enum):
    """Priority levels for resource allocation."""

    CRITICAL = 0  # Mission-critical tasks, highest priority
    HIGH = 1  # Important tasks that should not be delayed
    MEDIUM = 2  # Standard priority for most operations
    LOW = 3  # Background tasks that can be delayed
    BACKGROUND = 4  # Tasks that run only when system is idle


class ResourceType(Enum):
    """Types of resources that can be managed."""

    CPU = "cpu"
    MEMORY = "memory"
    GPU = "gpu"
    DISK_IO = "disk_io"
    NETWORK = "network"
    MODEL_TOKENS = "model_tokens"  # Token usage for LLM models


@dataclass
class ResourceUsage:
    """Tracks resource usage for a specific service or component."""

    cpu_percent: float = 0.0
    memory_mb: float = 0.0
    gpu_percent: float = 0.0
    disk_io_ops: int = 0
    network_kbps: float = 0.0
    token_count: int = 0
    last_updated: float = 0.0


@dataclass
class ResourceThresholds:
    """Defines resource usage thresholds for scaling decisions."""

    cpu_percent_high: float = 80.0
    cpu_percent_low: float = 20.0
    memory_mb_high: float = 1024.0
    memory_mb_low: float = 256.0
    gpu_percent_high: float = 70.0
    gpu_percent_low: float = 10.0
    token_rate_high: int = 1000
    token_rate_low: int = 100


@dataclass
class ResourceAllocation:
    """Resource allocation configuration for a component."""

    max_concurrent_requests: int = 10
    max_tokens_per_minute: int = 100000
    max_memory_mb: int = 1024
    priority: ResourcePriority = ResourcePriority.MEDIUM
    throttle_enabled: bool = True
    dedicated_cpu_cores: List[int] = field(default_factory=list)
    gpu_memory_limit_mb: Optional[int] = None
    io_priority: int = 4  # 0-7, lower is higher priority


class ResourceManager:
    """
    Manages system resources adaptively for the EnhancedOrchestrator.

    This class provides capabilities for tracking resource usage, applying
    constraints and throttling, and optimizing allocation based on workload patterns.
    """

    _instance = None
    _lock = threading.Lock()
    _initialized = False

    def __new__(cls, *args, **kwargs):
        """Implement singleton pattern for the ResourceManager."""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(ResourceManager, cls).__new__(cls)
        return cls._instance

    def __init__(self, enable_monitoring: bool = True):
        """Initialize the resource manager."""
        if self._initialized:
            return

        self._initialized = True
        self._component_usage: Dict[str, ResourceUsage] = {}
        self._component_allocations: Dict[str, ResourceAllocation] = {}
        self._thresholds = ResourceThresholds()
        self._monitoring_thread = None
        self._stop_monitoring = threading.Event()
        self._callbacks: Dict[str, List[Tuple[Callable, Dict[str, Any]]]] = {}
        self._last_system_check = 0
        self._system_check_interval = 5  # seconds

        # Initialize system-level metrics
        self._system_metrics = {
            "cpu_total": 0.0,
            "memory_total_mb": 0.0,
            "memory_available_mb": 0.0,
            "disk_io_total": 0,
            "net_total_kbps": 0.0,
        }

        # Start monitoring if enabled
        if enable_monitoring:
            self._start_monitoring()

    def register_component(
        self, component_id: str, allocation: Optional[ResourceAllocation] = None
    ) -> None:
        """
        Register a component for resource management.

        Args:
            component_id: Unique identifier for the component
            allocation: Optional resource allocation settings for the component
        """
        if allocation is None:
            allocation = ResourceAllocation()

        self._component_allocations[component_id] = allocation
        self._component_usage[component_id] = ResourceUsage(last_updated=time.time())
        logger.debug(f"Registered component {component_id} for resource management")

    def unregister_component(self, component_id: str) -> None:
        """
        Remove a component from resource management.

        Args:
            component_id: Unique identifier for the component
        """
        if component_id in self._component_allocations:
            del self._component_allocations[component_id]
        if component_id in self._component_usage:
            del self._component_usage[component_id]

    def update_usage(
        self, component_id: str, resource_type: ResourceType, value: float
    ) -> None:
        """
        Update usage metrics for a specific component and resource type.

        Args:
            component_id: Unique identifier for the component
            resource_type: Type of resource to update
            value: New value for the resource usage
        """
        if component_id not in self._component_usage:
            self.register_component(component_id)

        usage = self._component_usage[component_id]

        if resource_type == ResourceType.CPU:
            usage.cpu_percent = value
        elif resource_type == ResourceType.MEMORY:
            usage.memory_mb = value
        elif resource_type == ResourceType.GPU:
            usage.gpu_percent = value
        elif resource_type == ResourceType.DISK_IO:
            usage.disk_io_ops = int(value)
        elif resource_type == ResourceType.NETWORK:
            usage.network_kbps = value
        elif resource_type == ResourceType.MODEL_TOKENS:
            usage.token_count += int(value)

        usage.last_updated = time.time()
        self._trigger_callbacks(
            "usage_updated",
            {
                "component_id": component_id,
                "resource_type": resource_type,
                "value": value,
            },
        )

    def get_allocation(self, component_id: str) -> Optional[ResourceAllocation]:
        """
        Get the current resource allocation for a component.

        Args:
            component_id: Unique identifier for the component

        Returns:
            Resource allocation for the component, or None if not found
        """
        return self._component_allocations.get(component_id)

    def update_allocation(
        self, component_id: str, allocation: ResourceAllocation
    ) -> None:
        """
        Update resource allocation for a component.

        Args:
            component_id: Unique identifier for the component
            allocation: New resource allocation settings
        """
        if component_id not in self._component_allocations:
            self.register_component(component_id, allocation)
        else:
            self._component_allocations[component_id] = allocation

        self._trigger_callbacks(
            "allocation_updated",
            {"component_id": component_id, "allocation": allocation},
        )

    def get_usage(self, component_id: str) -> Optional[ResourceUsage]:
        """
        Get the current resource usage for a component.

        Args:
            component_id: Unique identifier for the component

        Returns:
            Resource usage for the component, or None if not found
        """
        return self._component_usage.get(component_id)

    def get_system_metrics(self) -> Dict[str, float]:
        """
        Get current system-wide resource metrics.

        Returns:
            Dictionary of system resource metrics
        """
        current_time = time.time()

        # Only update system metrics every few seconds to avoid overhead
        if current_time - self._last_system_check >= self._system_check_interval:
            try:
                # Update CPU
                self._system_metrics["cpu_total"] = psutil.cpu_percent(interval=0.1)

                # Update memory
                mem = psutil.virtual_memory()
                self._system_metrics["memory_total_mb"] = mem.total / (1024 * 1024)
                self._system_metrics["memory_available_mb"] = mem.available / (
                    1024 * 1024
                )

                # Update disk I/O
                disk_io = psutil.disk_io_counters()
                if disk_io:
                    self._system_metrics["disk_io_total"] = (
                        disk_io.read_count + disk_io.write_count
                    )

                # Update network
                net_io = psutil.net_io_counters()
                if net_io:
                    io_bytes = net_io.bytes_sent + net_io.bytes_recv
                    self._system_metrics["net_total_kbps"] = io_bytes / 1024

                self._last_system_check = current_time

            except Exception as e:
                logger.warning(f"Error updating system metrics: {str(e)}")

        return self._system_metrics

    def can_allocate(
        self, component_id: str, resource_type: ResourceType, requested_amount: float
    ) -> bool:
        """
        Check if a resource allocation is possible given system constraints.

        Args:
            component_id: Component requesting resources
            resource_type: Type of resource requested
            requested_amount: Amount of resource requested

        Returns:
            True if allocation is possible, False otherwise
        """
        # If component isn't registered, register it with default allocation
        if component_id not in self._component_allocations:
            self.register_component(component_id)

        allocation = self._component_allocations[component_id]
        system_metrics = self.get_system_metrics()

        # Check based on resource type
        if resource_type == ResourceType.CPU:
            # Check if system CPU is already too high
            if system_metrics["cpu_total"] > self._thresholds.cpu_percent_high:
                if allocation.priority.value > ResourcePriority.HIGH.value:
                    return False

        elif resource_type == ResourceType.MEMORY:
            # Check memory constraints
            available_memory = system_metrics["memory_available_mb"]
            if requested_amount > available_memory * 0.8:
                return False

            if requested_amount > allocation.max_memory_mb:
                return False

        elif resource_type == ResourceType.MODEL_TOKENS:
            # Check token rate limits
            usage = self._component_usage.get(component_id)
            if usage:
                # Calculate tokens used in the last minute
                one_minute_ago = time.time() - 60
                if one_minute_ago <= usage.last_updated:
                    tokens_used = usage.token_count + requested_amount
                    if tokens_used > allocation.max_tokens_per_minute:
                        return False

        return True

    def optimize_resources(self) -> Dict[str, Any]:
        """
        Optimize resource allocation based on current usage patterns.

        Returns:
            Dictionary with optimization actions taken
        """
        actions = {"scaled_up": [], "scaled_down": [], "reallocated": []}

        system_metrics = self.get_system_metrics()
        high_priority_ids = []
        low_usage_ids = []

        # Identify components that need more resources and those that can spare resources
        for component_id, usage in self._component_usage.items():
            allocation = self._component_allocations.get(component_id)
            if not allocation:
                continue

            # Identify high priority components with high usage
            if allocation.priority.value <= ResourcePriority.HIGH.value:
                if usage.cpu_percent > self._thresholds.cpu_percent_high:
                    high_priority_ids.append(component_id)

            # Identify low usage components
            if usage.cpu_percent < self._thresholds.cpu_percent_low:
                if usage.memory_mb < self._thresholds.memory_mb_low:
                    if allocation.priority.value >= ResourcePriority.MEDIUM.value:
                        low_usage_ids.append(component_id)

        # Perform optimizations based on system load
        system_overloaded = (
            system_metrics["cpu_total"] > self._thresholds.cpu_percent_high
        )

        if system_overloaded:
            # Throttle low priority components
            for component_id in low_usage_ids:
                allocation = self._component_allocations[component_id]
                if allocation.throttle_enabled:
                    # Reduce max concurrent requests
                    new_max = max(1, allocation.max_concurrent_requests // 2)
                    if new_max < allocation.max_concurrent_requests:
                        allocation.max_concurrent_requests = new_max
                        actions["scaled_down"].append(
                            {
                                "component_id": component_id,
                                "max_concurrent_requests": new_max,
                            }
                        )

                    # Reduce token rate
                    new_rate = max(1000, allocation.max_tokens_per_minute // 2)
                    if new_rate < allocation.max_tokens_per_minute:
                        allocation.max_tokens_per_minute = new_rate
                        actions["scaled_down"].append(
                            {
                                "component_id": component_id,
                                "max_tokens_per_minute": new_rate,
                            }
                        )
        else:
            # System has available resources, scale up high priority components
            for component_id in high_priority_ids:
                allocation = self._component_allocations[component_id]

                # Increase max concurrent requests
                new_max = min(100, allocation.max_concurrent_requests * 2)
                if new_max > allocation.max_concurrent_requests:
                    allocation.max_concurrent_requests = new_max
                    actions["scaled_up"].append(
                        {
                            "component_id": component_id,
                            "max_concurrent_requests": new_max,
                        }
                    )

                # Increase token rate
                new_rate = min(500000, allocation.max_tokens_per_minute * 2)
                if new_rate > allocation.max_tokens_per_minute:
                    allocation.max_tokens_per_minute = new_rate
                    actions["scaled_up"].append(
                        {
                            "component_id": component_id,
                            "max_tokens_per_minute": new_rate,
                        }
                    )

        # Reallocate CPU cores if needed for high priority components
        if high_priority_ids and os.name == "posix":
            try:
                available_cores = list(range(psutil.cpu_count()))
                used_cores = []

                # Collect cores already allocated
                for allocation in self._component_allocations.values():
                    used_cores.extend(allocation.dedicated_cpu_cores)

                # Find available cores not yet allocated
                available_cores = [c for c in available_cores if c not in used_cores]

                # Allocate cores to high priority components if needed
                for component_id in high_priority_ids:
                    allocation = self._component_allocations[component_id]
                    if len(allocation.dedicated_cpu_cores) < 2 and available_cores:
                        core_to_add = available_cores.pop(0)
                        allocation.dedicated_cpu_cores.append(core_to_add)
                        actions["reallocated"].append(
                            {
                                "component_id": component_id,
                                "dedicated_cpu_cores": allocation.dedicated_cpu_cores,
                            }
                        )
            except Exception as e:
                logger.warning(f"Failed to reallocate CPU cores: {str(e)}")

        self._trigger_callbacks("resources_optimized", actions)
        return actions

    def _start_monitoring(self) -> None:
        """Start the background monitoring thread."""
        if self._monitoring_thread is not None and self._monitoring_thread.is_alive():
            return

        self._stop_monitoring.clear()
        self._monitoring_thread = threading.Thread(
            target=self._monitoring_loop, daemon=True, name="ResourceMonitoringThread"
        )
        self._monitoring_thread.start()
        logger.debug("Started resource monitoring thread")

    def stop_monitoring(self) -> None:
        """Stop the background monitoring thread."""
        if self._monitoring_thread is not None:
            self._stop_monitoring.set()
            self._monitoring_thread.join(timeout=2)
            self._monitoring_thread = None
            logger.debug("Stopped resource monitoring thread")

    def _monitoring_loop(self) -> None:
        """Background thread for monitoring resource usage."""
        logger.debug("Resource monitoring thread started")
        monitoring_interval = 10  # seconds
        optimization_interval = 60  # seconds
        last_optimization = time.time()

        try:
            while not self._stop_monitoring.is_set():
                try:
                    # Update system metrics
                    self.get_system_metrics()

                    # Check if it's time to optimize
                    current_time = time.time()
                    if current_time - last_optimization >= optimization_interval:
                        self.optimize_resources()
                        last_optimization = current_time

                    # Wait for next monitoring cycle
                    self._stop_monitoring.wait(monitoring_interval)

                except Exception as e:
                    logger.error(f"Error in resource monitoring loop: {str(e)}")
                    # Sleep to avoid tight error loops
                    time.sleep(5)

        finally:
            logger.debug("Resource monitoring thread stopped")

    def register_callback(self, event_type: str, callback: Callable, **kwargs) -> None:
        """
        Register a callback for resource events.

        Args:
            event_type: Type of event to subscribe to
            callback: Function to call when event occurs
            **kwargs: Additional data to pass to the callback
        """
        if event_type not in self._callbacks:
            self._callbacks[event_type] = []

        self._callbacks[event_type].append((callback, kwargs))

    def unregister_callback(self, event_type: str, callback: Callable) -> None:
        """
        Unregister a callback for resource events.

        Args:
            event_type: Type of event the callback was registered for
            callback: Function to unregister
        """
        if event_type in self._callbacks:
            self._callbacks[event_type] = [
                (cb, kwargs)
                for cb, kwargs in self._callbacks[event_type]
                if cb != callback
            ]

    def _trigger_callbacks(self, event_type: str, event_data: Dict[str, Any]) -> None:
        """
        Trigger callbacks for a specific event type.

        Args:
            event_type: Type of event that occurred
            event_data: Data associated with the event
        """
        if event_type not in self._callbacks:
            return

        for callback, kwargs in self._callbacks[event_type]:
            try:
                callback(event_data=event_data, **kwargs)
            except Exception as e:
                logger.error(f"Error in resource event callback: {str(e)}")


def get_resource_manager() -> ResourceManager:
    """
    Get the singleton instance of the ResourceManager.

    Returns:
        The ResourceManager instance
    """
    return ResourceManager()


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    # Get resource manager instance
    resource_mgr = get_resource_manager()

    # Register a component with high priority
    high_priority = ResourceAllocation(
        max_concurrent_requests=20,
        max_tokens_per_minute=200000,
        priority=ResourcePriority.HIGH,
    )
    resource_mgr.register_component("critical_model", high_priority)

    # Register a component with lower priority
    low_priority = ResourceAllocation(
        max_concurrent_requests=5,
        max_tokens_per_minute=50000,
        priority=ResourcePriority.LOW,
    )
    resource_mgr.register_component("background_model", low_priority)

    # Update usage for components
    resource_mgr.update_usage("critical_model", ResourceType.CPU, 75.0)
    resource_mgr.update_usage("critical_model", ResourceType.MEMORY, 512.0)
    resource_mgr.update_usage("critical_model", ResourceType.MODEL_TOKENS, 1000)

    resource_mgr.update_usage("background_model", ResourceType.CPU, 15.0)
    resource_mgr.update_usage("background_model", ResourceType.MEMORY, 128.0)

    # Register a callback for resource optimization
    def on_optimization(event_data, **kwargs):
        print(f"Resource optimization performed: {event_data}")
        print(f"Custom data: {kwargs.get('custom_data')}")

    resource_mgr.register_callback(
        "resources_optimized", on_optimization, custom_data="Optimization triggered"
    )

    # Test allocation check
    can_allocate = resource_mgr.can_allocate(
        "critical_model", ResourceType.MODEL_TOKENS, 5000
    )
    print(f"Can allocate tokens: {can_allocate}")

    # Run optimization manually
    actions = resource_mgr.optimize_resources()
    print(f"Optimization actions: {actions}")

    # Wait a bit to let monitoring thread run
    time.sleep(2)

    # Show current system metrics
    metrics = resource_mgr.get_system_metrics()
    print(f"System metrics: {metrics}")

    # Clean up
    resource_mgr.stop_monitoring()
