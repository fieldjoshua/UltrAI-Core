"""
Resource Optimizer Module.

This module provides resource optimization capabilities for the EnhancedOrchestrator,
including memory monitoring, intelligent garbage collection, resource-aware scheduling,
adaptive concurrency control, and horizontal scaling support.
"""

import asyncio
import gc
import logging
import platform
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple

import psutil


class ResourceStatus(Enum):
    """Status of system resources."""

    OPTIMAL = "optimal"
    WARNING = "warning"
    CRITICAL = "critical"


class OptimizationAction(Enum):
    """Action to take for resource optimization."""

    NONE = "none"
    REDUCE_CONCURRENCY = "reduce_concurrency"
    INCREASE_CONCURRENCY = "increase_concurrency"
    LIMIT_BATCH_SIZE = "limit_batch_size"
    CLEAR_CACHE = "clear_cache"
    FORCE_GC = "force_gc"
    OFFLOAD_WORK = "offload_work"


@dataclass
class ResourceThreshold:
    """Threshold for resource monitoring."""

    warning_level: float
    critical_level: float
    action: OptimizationAction = OptimizationAction.NONE
    cooldown_seconds: float = 60.0


@dataclass
class ResourceMetrics:
    """Current resource metrics."""

    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    memory_used_mb: float = 0.0
    memory_available_mb: float = 0.0
    disk_percent: float = 0.0
    disk_used_gb: float = 0.0
    disk_available_gb: float = 0.0
    net_connections: int = 0
    timestamp: float = field(default_factory=time.time)


@dataclass
class ConcurrencyConfig:
    """Configuration for adaptive concurrency control."""

    min_concurrency: int = 1
    max_concurrency: int = 10
    current_concurrency: int = 3
    scale_up_threshold: float = 0.6  # CPU usage below this triggers scale up
    scale_down_threshold: float = 0.8  # CPU usage above this triggers scale down
    scale_step: int = 1
    cooldown_seconds: float = 30.0
    last_adjustment_time: float = 0.0


class ResourceOptimizer:
    """
    Resource optimization for the EnhancedOrchestrator.

    Features:
    - Real-time system resource monitoring
    - Memory usage tracking and limits
    - Intelligent garbage collection triggering
    - Resource-aware scheduling for heavy operations
    - Adaptive concurrency control
    - Horizontal scaling support
    """

    def __init__(
        self,
        memory_limit_mb: Optional[int] = None,
        cpu_threshold: float = 0.8,
        enable_gc_optimization: bool = True,
        enable_adaptive_concurrency: bool = True,
        gc_threshold_count: int = 10000,
        monitoring_interval_seconds: float = 10.0,
        enable_horizontal_scaling: bool = False,
        worker_pool_size: int = 0,
    ):
        """
        Initialize the resource optimizer.

        Args:
            memory_limit_mb: Memory limit in MB (None = auto-detect 80% of system
                memory)
            cpu_threshold: CPU usage threshold (0.0-1.0) for optimization actions
            enable_gc_optimization: Whether to enable garbage collection optimization
            enable_adaptive_concurrency: Whether to enable adaptive concurrency
            gc_threshold_count: Number of objects before triggering garbage collection
            monitoring_interval_seconds: Interval for resource monitoring
            enable_horizontal_scaling: Whether to enable horizontal scaling
            worker_pool_size: Size of the worker pool for horizontal scaling
        """
        self.logger = logging.getLogger(__name__)

        # Configure memory limit
        system_memory = psutil.virtual_memory().total / (1024 * 1024)  # MB
        self.memory_limit_mb = (
            memory_limit_mb if memory_limit_mb else int(system_memory * 0.8)
        )

        # Resource thresholds
        self.thresholds = {
            "cpu": ResourceThreshold(
                warning_level=cpu_threshold * 0.9,
                critical_level=cpu_threshold,
                action=OptimizationAction.REDUCE_CONCURRENCY,
            ),
            "memory": ResourceThreshold(
                warning_level=0.8,
                critical_level=0.9,
                action=OptimizationAction.CLEAR_CACHE,
            ),
            "disk": ResourceThreshold(
                warning_level=0.8,
                critical_level=0.95,
                action=OptimizationAction.NONE,
            ),
        }

        # Monitoring configuration
        self.monitoring_interval = monitoring_interval_seconds
        self.last_check_time = 0.0
        self.current_metrics = ResourceMetrics()
        self.metrics_history: List[ResourceMetrics] = []
        self.history_size = 100  # Keep the last 100 metrics records

        # GC optimization configuration
        self.enable_gc_optimization = enable_gc_optimization
        self.gc_threshold_count = gc_threshold_count
        self.last_gc_time = 0.0
        self.gc_interval_seconds = 60.0  # Minimum time between forced GC
        self.object_counts: List[int] = []

        # Adaptive concurrency control
        self.enable_adaptive_concurrency = enable_adaptive_concurrency
        self.concurrency_config = ConcurrencyConfig()

        # Horizontal scaling configuration
        self.enable_horizontal_scaling = enable_horizontal_scaling
        self.worker_pool_size = worker_pool_size
        self.active_workers = 0
        self.worker_queue: asyncio.Queue = asyncio.Queue()
        self.worker_statuses: Dict[str, Dict[str, Any]] = {}

        # Callbacks for optimization actions
        self.action_callbacks: Dict[OptimizationAction, List[Callable]] = {
            action: [] for action in OptimizationAction
        }

        # Last action times for cooldowns
        self.last_action_times: Dict[OptimizationAction, float] = {
            action: 0.0 for action in OptimizationAction
        }

        # Publish system info at startup
        self._log_system_info()

    def _log_system_info(self) -> None:
        """Log system information."""
        try:
            system_info = {
                "system": platform.system(),
                "version": platform.version(),
                "python": platform.python_version(),
                "cpu_count": psutil.cpu_count(logical=True),
                "physical_cores": psutil.cpu_count(logical=False),
                "total_memory_mb": psutil.virtual_memory().total / (1024 * 1024),
                "memory_limit_mb": self.memory_limit_mb,
            }
            self.logger.info(f"System information: {system_info}")
        except Exception as e:
            self.logger.error(f"Error getting system information: {e}")

    def add_action_callback(
        self, action: OptimizationAction, callback: Callable[..., Any]
    ) -> None:
        """
        Add a callback for a specific optimization action.

        Args:
            action: The optimization action to trigger the callback
            callback: The callback function to execute
        """
        self.action_callbacks[action].append(callback)

    def get_current_metrics(self) -> ResourceMetrics:
        """
        Get current system resource metrics.

        Returns:
            ResourceMetrics object with current values
        """
        try:
            # Update if monitoring interval has passed
            current_time = time.time()
            if current_time - self.last_check_time >= self.monitoring_interval:
                self._update_metrics()

            return self.current_metrics
        except Exception as e:
            self.logger.error(f"Error getting current metrics: {e}")
            return ResourceMetrics()

    def _update_metrics(self) -> None:
        """Update resource metrics."""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=0.5)

            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_used_mb = memory.used / (1024 * 1024)
            memory_available_mb = memory.available / (1024 * 1024)

            # Disk usage
            disk = psutil.disk_usage("/")
            disk_percent = disk.percent
            disk_used_gb = disk.used / (1024 * 1024 * 1024)
            disk_available_gb = disk.free / (1024 * 1024 * 1024)

            # Network connections
            net_connections = len(psutil.net_connections())

            # Create metrics object
            metrics = ResourceMetrics(
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                memory_used_mb=memory_used_mb,
                memory_available_mb=memory_available_mb,
                disk_percent=disk_percent,
                disk_used_gb=disk_used_gb,
                disk_available_gb=disk_available_gb,
                net_connections=net_connections,
                timestamp=time.time(),
            )

            # Update current metrics
            self.current_metrics = metrics

            # Add to history and trim
            self.metrics_history.append(metrics)
            if len(self.metrics_history) > self.history_size:
                self.metrics_history = self.metrics_history[-self.history_size :]

            self.last_check_time = time.time()
        except Exception as e:
            self.logger.error(f"Error updating metrics: {e}")

    def get_resource_status(self) -> Dict[str, ResourceStatus]:
        """
        Get the status of system resources.

        Returns:
            Dictionary mapping resource names to status values
        """
        metrics = self.get_current_metrics()
        statuses = {}

        # Check CPU status
        if metrics.cpu_percent >= self.thresholds["cpu"].critical_level * 100:
            statuses["cpu"] = ResourceStatus.CRITICAL
        elif metrics.cpu_percent >= self.thresholds["cpu"].warning_level * 100:
            statuses["cpu"] = ResourceStatus.WARNING
        else:
            statuses["cpu"] = ResourceStatus.OPTIMAL

        # Check memory status
        if metrics.memory_percent >= self.thresholds["memory"].critical_level * 100:
            statuses["memory"] = ResourceStatus.CRITICAL
        elif metrics.memory_percent >= self.thresholds["memory"].warning_level * 100:
            statuses["memory"] = ResourceStatus.WARNING
        else:
            statuses["memory"] = ResourceStatus.OPTIMAL

        # Check disk status
        if metrics.disk_percent >= self.thresholds["disk"].critical_level * 100:
            statuses["disk"] = ResourceStatus.CRITICAL
        elif metrics.disk_percent >= self.thresholds["disk"].warning_level * 100:
            statuses["disk"] = ResourceStatus.WARNING
        else:
            statuses["disk"] = ResourceStatus.OPTIMAL

        return statuses

    def check_memory_limit(self) -> Tuple[bool, float]:
        """
        Check if current memory usage is within the specified limit.

        Returns:
            Tuple of (is_within_limit, percentage_used)
        """
        metrics = self.get_current_metrics()
        is_within_limit = metrics.memory_used_mb < self.memory_limit_mb
        percent_used = (
            metrics.memory_used_mb / self.memory_limit_mb
            if self.memory_limit_mb > 0
            else 0
        )

        return is_within_limit, percent_used

    def trigger_garbage_collection(self, force: bool = False) -> bool:
        """
        Trigger garbage collection if necessary or forced.

        Args:
            force: Whether to force garbage collection

        Returns:
            Whether garbage collection was performed
        """
        if not self.enable_gc_optimization and not force:
            return False

        current_time = time.time()

        # Check if we're within the cooldown period
        if not force and current_time - self.last_gc_time < self.gc_interval_seconds:
            return False

        # Count objects to determine if GC is needed
        count_objects = len(gc.get_objects())
        self.object_counts.append(count_objects)

        # Keep only the most recent counts
        if len(self.object_counts) > 10:
            self.object_counts = self.object_counts[-10:]

        # Determine if GC should be triggered
        should_trigger = (
            force
            or count_objects > self.gc_threshold_count
            or (
                len(self.object_counts) > 5
                and self.object_counts[-1] > self.object_counts[-5] * 1.5
            )
        )

        if should_trigger:
            # Perform garbage collection
            self.logger.info(
                f"Triggering garbage collection (objects: {count_objects})"
            )
            collected = gc.collect(generation=2)  # Full collection
            self.last_gc_time = current_time
            self.logger.info(
                f"Garbage collection complete, collected {collected} objects"
            )
            return True

        return False

    def update_concurrency(self) -> Optional[int]:
        """
        Update concurrency settings based on current resource usage.

        Returns:
            New concurrency value if changed, None otherwise
        """
        if not self.enable_adaptive_concurrency:
            return None

        current_time = time.time()
        config = self.concurrency_config

        # Check if we're within the cooldown period
        if current_time - config.last_adjustment_time < config.cooldown_seconds:
            return None

        metrics = self.get_current_metrics()
        cpu_usage = metrics.cpu_percent / 100.0  # Convert to 0-1 scale

        # Determine if concurrency should be adjusted
        new_concurrency = config.current_concurrency

        if cpu_usage > config.scale_down_threshold:
            # High CPU usage - decrease concurrency
            new_concurrency = max(
                config.min_concurrency, config.current_concurrency - config.scale_step
            )
            action = "decrease"
        elif cpu_usage < config.scale_up_threshold and metrics.memory_percent < 70:
            # Low CPU usage and memory not critical - increase concurrency
            new_concurrency = min(
                config.max_concurrency, config.current_concurrency + config.scale_step
            )
            action = "increase"
        else:
            # No change needed
            return None

        if new_concurrency != config.current_concurrency:
            self.logger.info(
                f"Adjusting concurrency from {config.current_concurrency} "
                f"to {new_concurrency} (CPU: {cpu_usage:.2f}, action: {action})"
            )
            config.current_concurrency = new_concurrency
            config.last_adjustment_time = current_time
            return new_concurrency

        return None

    def optimize(self) -> Dict[str, Any]:
        """
        Perform resource optimization based on current metrics.

        Returns:
            Dictionary with optimization results
        """
        # Update metrics
        self._update_metrics()

        # Get resource status
        statuses = self.get_resource_status()
        results = {"actions": [], "status": statuses}

        # Check if optimization actions are needed
        current_time = time.time()

        # Check CPU utilization
        if statuses["cpu"] == ResourceStatus.CRITICAL:
            action = self.thresholds["cpu"].action
            last_action_time = self.last_action_times.get(action, 0)

            if (
                current_time - last_action_time
                > self.thresholds["cpu"].cooldown_seconds
            ):
                # Take CPU optimization action (usually reducing concurrency)
                self._execute_action(action)
                results["actions"].append(str(action.value))
                self.last_action_times[action] = current_time

        # Check memory utilization
        if statuses["memory"] == ResourceStatus.CRITICAL:
            action = self.thresholds["memory"].action
            last_action_time = self.last_action_times.get(action, 0)

            if (
                current_time - last_action_time
                > self.thresholds["memory"].cooldown_seconds
            ):
                # Take memory optimization action (usually clearing cache or GC)
                self._execute_action(action)
                results["actions"].append(str(action.value))
                self.last_action_times[action] = current_time

                # Also trigger garbage collection
                if self.trigger_garbage_collection(force=True):
                    results["actions"].append(str(OptimizationAction.FORCE_GC.value))

        # Update concurrency if enabled
        new_concurrency = self.update_concurrency()
        if new_concurrency is not None:
            if new_concurrency < self.concurrency_config.current_concurrency:
                results["actions"].append(
                    str(OptimizationAction.REDUCE_CONCURRENCY.value)
                )
            else:
                results["actions"].append(
                    str(OptimizationAction.INCREASE_CONCURRENCY.value)
                )

            results["concurrency"] = new_concurrency

        # Periodic garbage collection check
        if (
            self.enable_gc_optimization
            and current_time - self.last_gc_time >= self.gc_interval_seconds
        ):
            if self.trigger_garbage_collection():
                results["actions"].append(str(OptimizationAction.FORCE_GC.value))

        return results

    def _execute_action(self, action: OptimizationAction) -> None:
        """
        Execute a specific optimization action.

        Args:
            action: The action to execute
        """
        self.logger.info(f"Executing optimization action: {action.value}")

        # Execute registered callbacks
        for callback in self.action_callbacks.get(action, []):
            try:
                callback()
            except Exception as e:
                self.logger.error(
                    f"Error executing callback for action {action.value}: {e}"
                )

        # Built-in actions
        if action == OptimizationAction.FORCE_GC:
            self.trigger_garbage_collection(force=True)

    async def schedule_resource_aware(
        self,
        task_fn: Callable,
        *args,
        priority: int = 1,
        memory_requirement_mb: Optional[float] = None,
        cpu_requirement: Optional[float] = None,
        **kwargs,
    ) -> Any:
        """
        Schedule a task with resource awareness.

        Args:
            task_fn: The task function to execute
            *args: Arguments to pass to the task function
            priority: Priority level (higher = more important)
            memory_requirement_mb: Estimated memory requirement in MB
            cpu_requirement: Estimated CPU requirement (0-1 scale)
            **kwargs: Keyword arguments to pass to the task function

        Returns:
            Result of the task function
        """
        # Check current resource availability
        metrics = self.get_current_metrics()
        is_within_memory, _ = self.check_memory_limit()

        # If memory requirement specified, check if we have enough available
        if memory_requirement_mb is not None:
            memory_available = metrics.memory_available_mb
            has_enough_memory = memory_available >= memory_requirement_mb

            if not has_enough_memory:
                self.logger.warning(
                    f"Insufficient memory for task: "
                    f"required={memory_requirement_mb}MB, "
                    f"available={memory_available}MB. "
                    f"Will wait for resources."
                )

                # Wait for memory to be available
                while not has_enough_memory:
                    # Trigger optimization to free up resources
                    self.optimize()
                    await asyncio.sleep(1)

                    # Check again
                    self._update_metrics()
                    memory_available = self.current_metrics.memory_available_mb
                    has_enough_memory = memory_available >= memory_requirement_mb

        # If CPU requirement specified, check if we have enough available
        if cpu_requirement is not None:
            cpu_available = 1.0 - (metrics.cpu_percent / 100.0)
            has_enough_cpu = cpu_available >= cpu_requirement

            if not has_enough_cpu:
                self.logger.warning(
                    f"High CPU utilization for task: required={cpu_requirement}, "
                    f"available={cpu_available:.2f}. Will wait for resources."
                )

                # Wait for CPU to be available
                while not has_enough_cpu:
                    # Try optimization
                    self.optimize()
                    await asyncio.sleep(1)

                    # Check again
                    self._update_metrics()
                    cpu_available = 1.0 - (self.current_metrics.cpu_percent / 100.0)
                    has_enough_cpu = cpu_available >= cpu_requirement

        # Execute the task
        try:
            if asyncio.iscoroutinefunction(task_fn):
                return await task_fn(*args, **kwargs)
            else:
                return task_fn(*args, **kwargs)
        finally:
            # Update metrics after task completion
            self._update_metrics()

            # Check if we need to optimize after the task
            self.optimize()

    async def execute_with_adaptive_concurrency(
        self, tasks: List[Callable], *args, **kwargs
    ) -> List[Any]:
        """
        Execute multiple tasks with adaptive concurrency.

        Args:
            tasks: List of task functions to execute
            *args: Arguments to pass to tasks
            **kwargs: Keyword arguments to pass to tasks

        Returns:
            List of task results
        """
        results = []
        pending = []

        # Use the current concurrency setting
        concurrency = self.concurrency_config.current_concurrency
        self.logger.info(f"Executing {len(tasks)} tasks with concurrency {concurrency}")

        # Create semaphore to limit concurrency
        semaphore = asyncio.Semaphore(concurrency)

        async def execute_task(task_fn):
            async with semaphore:
                if asyncio.iscoroutinefunction(task_fn):
                    return await task_fn(*args, **kwargs)
                else:
                    return task_fn(*args, **kwargs)

        # Create tasks
        for task_fn in tasks:
            task = asyncio.create_task(execute_task(task_fn))
            pending.append(task)

        # Process tasks as they complete
        while pending:
            done, pending = await asyncio.wait(
                pending, return_when=asyncio.FIRST_COMPLETED
            )

            # Collect results
            for task in done:
                try:
                    result = task.result()
                    results.append(result)
                except Exception as e:
                    self.logger.error(f"Task execution error: {e}")
                    results.append(None)

            # Check if we need to adjust concurrency
            new_concurrency = self.update_concurrency()
            if new_concurrency is not None and new_concurrency != concurrency:
                concurrency = new_concurrency
                self.logger.info(f"Adjusted concurrency to {concurrency}")

                # Semaphore can't be directly modified, so we need to create a new one
                # This affects only new tasks, not ones already running
                semaphore = asyncio.Semaphore(concurrency)

        return results

    def get_metrics_history(self) -> List[Dict[str, Any]]:
        """
        Get historical metrics data.

        Returns:
            List of metrics dictionaries
        """
        return [
            {
                "timestamp": m.timestamp,
                "cpu_percent": m.cpu_percent,
                "memory_percent": m.memory_percent,
                "memory_used_mb": m.memory_used_mb,
                "memory_available_mb": m.memory_available_mb,
                "disk_percent": m.disk_percent,
            }
            for m in self.metrics_history
        ]

    def get_optimization_status(self) -> Dict[str, Any]:
        """
        Get current optimization status summary.

        Returns:
            Dictionary with optimization status
        """
        return {
            "memory_limit_mb": self.memory_limit_mb,
            "current_memory_mb": self.current_metrics.memory_used_mb,
            "memory_percent": self.current_metrics.memory_percent,
            "cpu_percent": self.current_metrics.cpu_percent,
            "gc_enabled": self.enable_gc_optimization,
            "last_gc_time": self.last_gc_time,
            "concurrency": self.concurrency_config.current_concurrency,
            "adaptive_concurrency": self.enable_adaptive_concurrency,
            "horizontal_scaling": self.enable_horizontal_scaling,
            "active_workers": self.active_workers,
        }
