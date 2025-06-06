"""Automatic recovery workflows for common failure scenarios.

This module provides automated recovery procedures that can restore
service functionality after various types of failures.
"""

import asyncio
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional, Set

from .circuit_breaker import CircuitBreakerManager, CircuitState
from .fallback_handler import FallbackHandler
from .retry_handler import RetryConfig, RetryHandler

logger = logging.getLogger(__name__)


@dataclass
class RecoveryConfig:
    """Configuration for recovery workflows."""

    max_recovery_attempts: int = 3
    recovery_interval: int = 60  # seconds between recovery attempts
    enable_auto_recovery: bool = True
    recovery_timeout: int = 300  # total timeout for recovery
    notify_on_recovery: bool = True
    health_check_interval: int = 30  # seconds


class RecoveryAction(ABC):
    """Abstract base class for recovery actions."""

    @abstractmethod
    async def execute(self, context: Dict[str, Any]) -> bool:
        """Execute the recovery action.

        Returns:
            True if recovery was successful, False otherwise
        """
        pass

    @abstractmethod
    def can_recover(self, error_type: str, context: Dict[str, Any]) -> bool:
        """Check if this action can handle the error."""
        pass


class CircuitBreakerRecoveryAction(RecoveryAction):
    """Recovery action for circuit breaker issues."""

    def __init__(self, circuit_manager: CircuitBreakerManager):
        self.circuit_manager = circuit_manager

    async def execute(self, context: Dict[str, Any]) -> bool:
        """Reset circuit breaker if conditions are met."""
        service_name = context.get("service_name")
        if not service_name:
            return False

        breaker = self.circuit_manager.get_breaker(service_name)
        if not breaker:
            return False

        # Check if service is healthy again
        if await self._check_service_health(service_name):
            await self.circuit_manager.reset_breaker(service_name)
            logger.info(f"Circuit breaker reset for service: {service_name}")
            return True

        return False

    def can_recover(self, error_type: str, context: Dict[str, Any]) -> bool:
        """Check if this action can handle circuit breaker errors."""
        return error_type == "CIRCUIT_OPEN"

    async def _check_service_health(self, service_name: str) -> bool:
        """Check if service is healthy."""
        # Implementation would depend on service type
        # This is a placeholder
        return True


class DatabaseRecoveryAction(RecoveryAction):
    """Recovery action for database connection issues."""

    def __init__(self, db_manager):
        self.db_manager = db_manager

    async def execute(self, context: Dict[str, Any]) -> bool:
        """Attempt to restore database connection."""
        try:
            # Attempt to reconnect
            await self.db_manager.reconnect()

            # Verify connection
            await self.db_manager.execute("SELECT 1")

            logger.info("Database connection recovered")
            return True

        except Exception as e:
            logger.error(f"Database recovery failed: {str(e)}")
            return False

    def can_recover(self, error_type: str, context: Dict[str, Any]) -> bool:
        """Check if this action can handle database errors."""
        return error_type in ["DB_CONNECTION_LOST", "DB_TIMEOUT"]


class CacheRecoveryAction(RecoveryAction):
    """Recovery action for cache service issues."""

    def __init__(self, cache_service):
        self.cache_service = cache_service

    async def execute(self, context: Dict[str, Any]) -> bool:
        """Attempt to restore cache service."""
        try:
            # Clear corrupted cache entries
            if context.get("clear_cache"):
                await self.cache_service.clear()

            # Reconnect to cache service
            await self.cache_service.reconnect()

            # Warm up cache with essential data
            await self._warm_up_cache()

            logger.info("Cache service recovered")
            return True

        except Exception as e:
            logger.error(f"Cache recovery failed: {str(e)}")
            return False

    def can_recover(self, error_type: str, context: Dict[str, Any]) -> bool:
        """Check if this action can handle cache errors."""
        return error_type in ["CACHE_CONNECTION_LOST", "CACHE_CORRUPTED"]

    async def _warm_up_cache(self):
        """Warm up cache with essential data."""
        # Implementation depends on application needs
        pass


class ServiceRestartRecoveryAction(RecoveryAction):
    """Recovery action for restarting failed services."""

    def __init__(self, service_manager):
        self.service_manager = service_manager

    async def execute(self, context: Dict[str, Any]) -> bool:
        """Restart a failed service."""
        service_name = context.get("service_name")
        if not service_name:
            return False

        try:
            # Stop the service
            await self.service_manager.stop_service(service_name)

            # Wait for clean shutdown
            await asyncio.sleep(5)

            # Start the service
            await self.service_manager.start_service(service_name)

            # Verify service is running
            if await self.service_manager.is_healthy(service_name):
                logger.info(f"Service {service_name} restarted successfully")
                return True

            return False

        except Exception as e:
            logger.error(f"Service restart failed: {str(e)}")
            return False

    def can_recover(self, error_type: str, context: Dict[str, Any]) -> bool:
        """Check if this action can handle service failures."""
        return error_type in ["SERVICE_CRASHED", "SERVICE_UNRESPONSIVE"]


class RecoveryWorkflow:
    """Manages recovery workflows for different failure scenarios."""

    def __init__(self, config: RecoveryConfig):
        """Initialize recovery workflow manager."""
        self.config = config
        self.recovery_actions: List[RecoveryAction] = []
        self.recovery_history: List[Dict[str, Any]] = []
        self.active_recoveries: Set[str] = set()
        self._lock = asyncio.Lock()

    def register_action(self, action: RecoveryAction):
        """Register a recovery action."""
        self.recovery_actions.append(action)
        logger.info(f"Registered recovery action: {action.__class__.__name__}")

    async def handle_failure(self, error_type: str, context: Dict[str, Any]) -> bool:
        """Handle failure with automatic recovery."""
        if not self.config.enable_auto_recovery:
            return False

        recovery_id = f"{error_type}:{context.get('service_name', 'unknown')}"

        async with self._lock:
            if recovery_id in self.active_recoveries:
                logger.info(f"Recovery already in progress for: {recovery_id}")
                return False

            self.active_recoveries.add(recovery_id)

        try:
            return await self._execute_recovery(error_type, context, recovery_id)
        finally:
            async with self._lock:
                self.active_recoveries.discard(recovery_id)

    async def _execute_recovery(
        self, error_type: str, context: Dict[str, Any], recovery_id: str
    ) -> bool:
        """Execute recovery workflow."""
        start_time = time.time()
        recovery_record = {
            "recovery_id": recovery_id,
            "error_type": error_type,
            "start_time": datetime.now(),
            "attempts": [],
            "success": False,
        }

        for attempt in range(self.config.max_recovery_attempts):
            if time.time() - start_time > self.config.recovery_timeout:
                logger.error(f"Recovery timeout for: {recovery_id}")
                break

            attempt_record = {
                "attempt": attempt + 1,
                "timestamp": datetime.now(),
                "actions": [],
            }

            # Try each recovery action
            for action in self.recovery_actions:
                if not action.can_recover(error_type, context):
                    continue

                action_name = action.__class__.__name__

                try:
                    success = await action.execute(context)

                    attempt_record["actions"].append(
                        {"action": action_name, "success": success, "error": None}
                    )

                    if success:
                        recovery_record["success"] = True
                        recovery_record["end_time"] = datetime.now()
                        recovery_record["attempts"].append(attempt_record)
                        self.recovery_history.append(recovery_record)

                        logger.info(f"Recovery successful for: {recovery_id}")

                        if self.config.notify_on_recovery:
                            await self._notify_recovery_success(recovery_record)

                        return True

                except Exception as e:
                    logger.error(f"Recovery action {action_name} failed: {str(e)}")
                    attempt_record["actions"].append(
                        {"action": action_name, "success": False, "error": str(e)}
                    )

            recovery_record["attempts"].append(attempt_record)

            # Wait before next attempt
            if attempt < self.config.max_recovery_attempts - 1:
                await asyncio.sleep(self.config.recovery_interval)

        # All attempts failed
        recovery_record["end_time"] = datetime.now()
        self.recovery_history.append(recovery_record)

        logger.error(f"Recovery failed for: {recovery_id}")

        if self.config.notify_on_recovery:
            await self._notify_recovery_failure(recovery_record)

        return False

    async def _notify_recovery_success(self, record: Dict[str, Any]):
        """Notify about successful recovery."""
        # Implementation depends on notification system
        pass

    async def _notify_recovery_failure(self, record: Dict[str, Any]):
        """Notify about failed recovery."""
        # Implementation depends on notification system
        pass

    def get_recovery_status(self) -> Dict[str, Any]:
        """Get current recovery status."""
        return {
            "active_recoveries": list(self.active_recoveries),
            "recent_recoveries": self.recovery_history[-10:],
            "recovery_stats": self._calculate_stats(),
        }

    def _calculate_stats(self) -> Dict[str, Any]:
        """Calculate recovery statistics."""
        if not self.recovery_history:
            return {"total_recoveries": 0, "success_rate": 0, "average_duration": 0}

        successful = sum(1 for r in self.recovery_history if r["success"])
        total = len(self.recovery_history)

        durations = []
        for record in self.recovery_history:
            if "end_time" in record:
                duration = (record["end_time"] - record["start_time"]).total_seconds()
                durations.append(duration)

        return {
            "total_recoveries": total,
            "success_rate": successful / total if total > 0 else 0,
            "average_duration": sum(durations) / len(durations) if durations else 0,
            "by_error_type": self._stats_by_error_type(),
        }

    def _stats_by_error_type(self) -> Dict[str, Dict[str, Any]]:
        """Calculate statistics by error type."""
        stats = {}

        for record in self.recovery_history:
            error_type = record["error_type"]

            if error_type not in stats:
                stats[error_type] = {"total": 0, "successful": 0, "failed": 0}

            stats[error_type]["total"] += 1

            if record["success"]:
                stats[error_type]["successful"] += 1
            else:
                stats[error_type]["failed"] += 1

        return stats


class HealthCheckRecovery:
    """Continuous health checking and recovery system."""

    def __init__(
        self, recovery_workflow: RecoveryWorkflow, health_check_config: Dict[str, Any]
    ):
        """Initialize health check recovery."""
        self.recovery_workflow = recovery_workflow
        self.health_checks = health_check_config
        self.running = False
        self._check_task = None

    async def start(self):
        """Start health check monitoring."""
        if self.running:
            return

        self.running = True
        self._check_task = asyncio.create_task(self._monitor_health())
        logger.info("Health check recovery started")

    async def stop(self):
        """Stop health check monitoring."""
        self.running = False

        if self._check_task:
            self._check_task.cancel()

            try:
                await self._check_task
            except asyncio.CancelledError:
                pass

        logger.info("Health check recovery stopped")

    async def _monitor_health(self):
        """Monitor service health and trigger recovery."""
        while self.running:
            for service_name, check_config in self.health_checks.items():
                try:
                    # Execute health check
                    is_healthy = await self._check_health(service_name, check_config)

                    if not is_healthy:
                        # Trigger recovery
                        context = {
                            "service_name": service_name,
                            "check_config": check_config,
                        }

                        await self.recovery_workflow.handle_failure(
                            "HEALTH_CHECK_FAILED", context
                        )

                except Exception as e:
                    logger.error(f"Health check error for {service_name}: {str(e)}")

            # Wait before next check
            await asyncio.sleep(self.recovery_workflow.config.health_check_interval)

    async def _check_health(
        self, service_name: str, check_config: Dict[str, Any]
    ) -> bool:
        """Execute health check for a service."""
        check_type = check_config.get("type", "http")

        if check_type == "http":
            return await self._http_health_check(check_config)
        elif check_type == "tcp":
            return await self._tcp_health_check(check_config)
        elif check_type == "custom":
            check_func = check_config.get("check_function")
            if check_func:
                return await check_func()

        return True

    async def _http_health_check(self, config: Dict[str, Any]) -> bool:
        """Execute HTTP health check."""
        # Implementation depends on HTTP client
        # This is a placeholder
        return True

    async def _tcp_health_check(self, config: Dict[str, Any]) -> bool:
        """Execute TCP health check."""
        # Implementation depends on network library
        # This is a placeholder
        return True
