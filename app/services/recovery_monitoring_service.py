"""Recovery monitoring service for tracking and alerting.

This service monitors error recovery operations, tracks metrics,
and provides alerting for recovery failures.
"""

import asyncio
import logging
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set

from ..models.base_models import MetricType
from ..utils.circuit_breaker import CircuitBreakerManager
from ..utils.metrics import MetricsCollector
from ..utils.recovery_workflows import RecoveryWorkflow

logger = logging.getLogger(__name__)


@dataclass
class RecoveryMetrics:
    """Metrics for recovery operations."""

    total_recoveries: int = 0
    successful_recoveries: int = 0
    failed_recoveries: int = 0
    active_recoveries: int = 0
    recovery_duration_ms: List[float] = field(default_factory=list)
    last_check_timestamp: Optional[datetime] = None
    alerts_triggered: int = 0


@dataclass
class AlertConfig:
    """Configuration for recovery alerts."""

    recovery_failure_threshold: int = 3  # consecutive failures
    recovery_time_threshold: float = 300.0  # seconds
    service_down_threshold: int = 5  # minutes
    alert_cooldown: int = 300  # seconds between alerts
    enabled_alerts: Set[str] = field(
        default_factory=lambda: {
            "recovery_failure",
            "prolonged_recovery",
            "service_down",
            "circuit_open",
        }
    )


class RecoveryMonitoringService:
    """Service for monitoring recovery operations."""

    def __init__(
        self,
        recovery_workflow: RecoveryWorkflow,
        circuit_manager: CircuitBreakerManager,
        metrics_collector: MetricsCollector,
        alert_config: AlertConfig = None,
    ):
        """Initialize recovery monitoring service."""
        self.recovery_workflow = recovery_workflow
        self.circuit_manager = circuit_manager
        self.metrics_collector = metrics_collector
        self.alert_config = alert_config or AlertConfig()

        self.metrics: Dict[str, RecoveryMetrics] = defaultdict(RecoveryMetrics)
        self.alert_history: List[Dict[str, Any]] = []
        self.last_alert_time: Dict[str, float] = {}
        self.consecutive_failures: Dict[str, int] = defaultdict(int)

        self.running = False
        self._monitor_task = None
        self._metrics_task = None

    async def start(self):
        """Start monitoring service."""
        if self.running:
            return

        self.running = True
        self._monitor_task = asyncio.create_task(self._monitor_loop())
        self._metrics_task = asyncio.create_task(self._collect_metrics_loop())

        logger.info("Recovery monitoring service started")

    async def stop(self):
        """Stop monitoring service."""
        self.running = False

        tasks = [self._monitor_task, self._metrics_task]
        for task in tasks:
            if task:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

        logger.info("Recovery monitoring service stopped")

    async def _monitor_loop(self):
        """Main monitoring loop."""
        while self.running:
            try:
                await self._check_recovery_status()
                await self._check_circuit_breakers()
                await self._check_service_health()

                # Update last check timestamp
                for key in self.metrics:
                    self.metrics[key].last_check_timestamp = datetime.now()

            except Exception as e:
                logger.error(f"Error in monitoring loop: {str(e)}")

            await asyncio.sleep(30)  # Check every 30 seconds

    async def _collect_metrics_loop(self):
        """Metrics collection loop."""
        while self.running:
            try:
                await self._publish_metrics()
            except Exception as e:
                logger.error(f"Error publishing metrics: {str(e)}")

            await asyncio.sleep(60)  # Publish metrics every minute

    async def _check_recovery_status(self):
        """Check current recovery status."""
        status = self.recovery_workflow.get_recovery_status()

        # Update metrics from recovery workflow
        for recovery in status.get("recent_recoveries", []):
            service_name = recovery.get("recovery_id", "").split(":")[1]
            metrics = self.metrics[service_name]

            metrics.total_recoveries += 1

            if recovery.get("success"):
                metrics.successful_recoveries += 1
                self.consecutive_failures[service_name] = 0
            else:
                metrics.failed_recoveries += 1
                self.consecutive_failures[service_name] += 1

                # Check for alert condition
                if (
                    self.consecutive_failures[service_name]
                    >= self.alert_config.recovery_failure_threshold
                ):
                    await self._trigger_alert(
                        "recovery_failure",
                        {
                            "service": service_name,
                            "consecutive_failures": self.consecutive_failures[
                                service_name
                            ],
                            "last_error": recovery.get("error_type"),
                        },
                    )

            # Calculate recovery duration
            if "start_time" in recovery and "end_time" in recovery:
                duration = (
                    recovery["end_time"] - recovery["start_time"]
                ).total_seconds() * 1000
                metrics.recovery_duration_ms.append(duration)

                # Check for prolonged recovery
                if duration > self.alert_config.recovery_time_threshold * 1000:
                    await self._trigger_alert(
                        "prolonged_recovery",
                        {
                            "service": service_name,
                            "duration_seconds": duration / 1000,
                            "threshold_seconds": self.alert_config.recovery_time_threshold,
                        },
                    )

        # Update active recoveries count
        active_recoveries = status.get("active_recoveries", [])
        for service_name in self.metrics:
            service_recoveries = [r for r in active_recoveries if service_name in r]
            self.metrics[service_name].active_recoveries = len(service_recoveries)

    async def _check_circuit_breakers(self):
        """Check circuit breaker status."""
        all_statuses = self.circuit_manager.get_all_statuses()

        for service_name, status in all_statuses.items():
            if status["state"] == "open":
                # Circuit is open - service is failing
                await self._trigger_alert(
                    "circuit_open",
                    {
                        "service": service_name,
                        "failure_count": status["stats"]["failure_count"],
                        "last_failure": status["stats"]["last_failure"],
                    },
                )

    async def _check_service_health(self):
        """Check overall service health."""
        # This would integrate with your health check system
        # For now, we'll use circuit breaker status as a proxy

        all_statuses = self.circuit_manager.get_all_statuses()

        for service_name, status in all_statuses.items():
            if status["state"] == "open":
                # Check how long the service has been down
                last_failure = status["stats"].get("last_failure")
                if last_failure:
                    last_failure_time = datetime.fromisoformat(last_failure)
                    downtime_minutes = (
                        datetime.now() - last_failure_time
                    ).total_seconds() / 60

                    if downtime_minutes >= self.alert_config.service_down_threshold:
                        await self._trigger_alert(
                            "service_down",
                            {
                                "service": service_name,
                                "downtime_minutes": downtime_minutes,
                                "state": status["state"],
                            },
                        )

    async def _publish_metrics(self):
        """Publish recovery metrics."""
        for service_name, metrics in self.metrics.items():
            # Success rate
            if metrics.total_recoveries > 0:
                success_rate = metrics.successful_recoveries / metrics.total_recoveries
                await self.metrics_collector.record_metric(
                    MetricType.GAUGE,
                    f"recovery.success_rate.{service_name}",
                    success_rate,
                )

            # Active recoveries
            await self.metrics_collector.record_metric(
                MetricType.GAUGE,
                f"recovery.active.{service_name}",
                metrics.active_recoveries,
            )

            # Average recovery duration
            if metrics.recovery_duration_ms:
                avg_duration = sum(metrics.recovery_duration_ms) / len(
                    metrics.recovery_duration_ms
                )
                await self.metrics_collector.record_metric(
                    MetricType.GAUGE,
                    f"recovery.duration_ms.{service_name}",
                    avg_duration,
                )

            # Total counts
            await self.metrics_collector.record_metric(
                MetricType.COUNTER,
                f"recovery.total.{service_name}",
                metrics.total_recoveries,
            )

            await self.metrics_collector.record_metric(
                MetricType.COUNTER,
                f"recovery.failed.{service_name}",
                metrics.failed_recoveries,
            )

    async def _trigger_alert(self, alert_type: str, data: Dict[str, Any]):
        """Trigger an alert if conditions are met."""
        if alert_type not in self.alert_config.enabled_alerts:
            return

        # Check cooldown
        last_alert = self.last_alert_time.get(alert_type, 0)
        if time.time() - last_alert < self.alert_config.alert_cooldown:
            return

        # Create alert
        alert = {
            "type": alert_type,
            "timestamp": datetime.now(),
            "data": data,
            "severity": self._get_alert_severity(alert_type),
        }

        self.alert_history.append(alert)
        self.last_alert_time[alert_type] = time.time()

        # Update metrics
        service_name = data.get("service", "unknown")
        self.metrics[service_name].alerts_triggered += 1

        # Log alert
        logger.warning(f"Recovery alert triggered: {alert_type} for {service_name}")

        # Send alert (implementation depends on alerting system)
        await self._send_alert(alert)

    def _get_alert_severity(self, alert_type: str) -> str:
        """Get severity level for alert type."""
        severity_map = {
            "recovery_failure": "warning",
            "prolonged_recovery": "warning",
            "service_down": "critical",
            "circuit_open": "error",
        }
        return severity_map.get(alert_type, "info")

    async def _send_alert(self, alert: Dict[str, Any]):
        """Send alert to notification system."""
        # Implementation depends on your notification system
        # Could be email, Slack, PagerDuty, etc.
        pass

    def get_monitoring_status(self) -> Dict[str, Any]:
        """Get current monitoring status."""
        return {
            "metrics": {
                service: {
                    "total_recoveries": metrics.total_recoveries,
                    "successful_recoveries": metrics.successful_recoveries,
                    "failed_recoveries": metrics.failed_recoveries,
                    "active_recoveries": metrics.active_recoveries,
                    "success_rate": (
                        metrics.successful_recoveries / metrics.total_recoveries
                        if metrics.total_recoveries > 0
                        else 0
                    ),
                    "avg_duration_ms": (
                        sum(metrics.recovery_duration_ms)
                        / len(metrics.recovery_duration_ms)
                        if metrics.recovery_duration_ms
                        else 0
                    ),
                    "last_check": (
                        metrics.last_check_timestamp.isoformat()
                        if metrics.last_check_timestamp
                        else None
                    ),
                    "alerts_triggered": metrics.alerts_triggered,
                }
                for service, metrics in self.metrics.items()
            },
            "recent_alerts": self.alert_history[-10:],
            "consecutive_failures": dict(self.consecutive_failures),
            "monitoring_running": self.running,
        }

    def get_alert_history(
        self,
        alert_type: Optional[str] = None,
        service: Optional[str] = None,
        since: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        """Get alert history with optional filters."""
        alerts = self.alert_history

        if alert_type:
            alerts = [a for a in alerts if a["type"] == alert_type]

        if service:
            alerts = [a for a in alerts if a["data"].get("service") == service]

        if since:
            alerts = [a for a in alerts if a["timestamp"] >= since]

        return alerts

    def clear_alerts(self, service: Optional[str] = None):
        """Clear alert history and reset counters."""
        if service:
            # Clear alerts for specific service
            self.alert_history = [
                a for a in self.alert_history if a["data"].get("service") != service
            ]

            if service in self.consecutive_failures:
                self.consecutive_failures[service] = 0

            if service in self.metrics:
                self.metrics[service].alerts_triggered = 0
        else:
            # Clear all alerts
            self.alert_history = []
            self.consecutive_failures.clear()

            for metrics in self.metrics.values():
                metrics.alerts_triggered = 0


class RecoveryDashboard:
    """Dashboard data aggregator for recovery monitoring."""

    def __init__(
        self,
        monitoring_service: RecoveryMonitoringService,
        recovery_workflow: RecoveryWorkflow,
        circuit_manager: CircuitBreakerManager,
    ):
        """Initialize recovery dashboard."""
        self.monitoring_service = monitoring_service
        self.recovery_workflow = recovery_workflow
        self.circuit_manager = circuit_manager

    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive dashboard data."""
        monitoring_status = self.monitoring_service.get_monitoring_status()
        recovery_status = self.recovery_workflow.get_recovery_status()
        circuit_status = self.circuit_manager.get_all_statuses()

        # Calculate aggregate metrics
        total_services = len(monitoring_status["metrics"])
        healthy_services = sum(
            1
            for service, status in circuit_status.items()
            if status["state"] == "closed"
        )

        # Get recent failures
        recent_failures = []
        for service, metrics in monitoring_status["metrics"].items():
            if metrics["failed_recoveries"] > 0:
                recent_failures.append(
                    {
                        "service": service,
                        "failures": metrics["failed_recoveries"],
                        "success_rate": metrics["success_rate"],
                    }
                )

        recent_failures.sort(key=lambda x: x["failures"], reverse=True)

        return {
            "summary": {
                "total_services": total_services,
                "healthy_services": healthy_services,
                "unhealthy_services": total_services - healthy_services,
                "active_recoveries": sum(
                    m["active_recoveries"]
                    for m in monitoring_status["metrics"].values()
                ),
                "recent_alerts": len(monitoring_status["recent_alerts"]),
            },
            "services": {
                service: {
                    "health": (
                        "healthy"
                        if circuit_status.get(service, {}).get("state") == "closed"
                        else "unhealthy"
                    ),
                    "circuit_state": circuit_status.get(service, {}).get(
                        "state", "unknown"
                    ),
                    "recovery_metrics": monitoring_status["metrics"].get(service, {}),
                    "consecutive_failures": monitoring_status[
                        "consecutive_failures"
                    ].get(service, 0),
                }
                for service in set(
                    list(monitoring_status["metrics"].keys())
                    + list(circuit_status.keys())
                )
            },
            "recent_failures": recent_failures[:5],
            "recovery_history": recovery_status.get("recent_recoveries", [])[-10:],
            "alerts": monitoring_status["recent_alerts"][-10:],
            "timestamp": datetime.now().isoformat(),
        }
