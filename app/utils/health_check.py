"""
Health check utilities for the Ultra backend.

This module provides functions for checking the health of external services and dependencies.
It defines a common interface for health checks and includes implementations for various
services like databases, caches, and LLM APIs.
"""

import os
import socket
import ssl
import threading
import time
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from urllib.parse import urlparse

import requests

# Import dependency registry but avoid unused import warning
from app.utils.dependency_manager import dependency_registry  # noqa: F401
from app.utils.logging import get_logger

# Get logger
logger = get_logger("health_check", "logs/health_check.log")

# Cache for health check results to avoid repeated checks in a short period
health_check_cache = {}
# Lock for thread safety
health_check_lock = threading.RLock()
# Cache TTL in seconds
HEALTH_CHECK_CACHE_TTL = int(os.getenv("HEALTH_CHECK_CACHE_TTL", "60"))
# Health check timeout in seconds
HEALTH_CHECK_TIMEOUT = int(os.getenv("HEALTH_CHECK_TIMEOUT", "5"))


class HealthStatus(str, Enum):
    """Health status enum for consistent status reporting"""

    OK = "ok"
    DEGRADED = "degraded"
    CRITICAL = "critical"
    UNAVAILABLE = "unavailable"
    UNKNOWN = "unknown"


class ServiceType(str, Enum):
    """Types of services that can be health-checked"""

    DATABASE = "database"
    CACHE = "cache"
    AUTH = "auth"
    LLM_PROVIDER = "llm_provider"
    STORAGE = "storage"
    NETWORK = "network"
    SYSTEM = "system"
    EXTERNAL_API = "external_api"
    CUSTOM = "custom"


class HealthCheck:
    """Base class for health checks"""

    def __init__(
        self,
        name: str,
        service_type: ServiceType,
        check_fn: Callable[[], Dict[str, Any]],
        description: str = "",
        is_critical: bool = False,
        check_interval: int = HEALTH_CHECK_CACHE_TTL,
        timeout: int = HEALTH_CHECK_TIMEOUT,
        dependent_services: List[str] = None,
    ):
        """
        Initialize health check

        Args:
            name: Name of the service
            service_type: Type of service
            check_fn: Function to call to check health
            description: Description of the service
            is_critical: Whether service is critical (affects overall status)
            check_interval: How often to check health in seconds
            timeout: Timeout for health check in seconds
            dependent_services: List of services this service depends on
        """
        self.name = name
        self.service_type = service_type
        self.check_fn = check_fn
        self.description = description
        self.is_critical = is_critical
        self.check_interval = check_interval
        self.timeout = timeout
        self.dependent_services = dependent_services or []
        self.last_check_time = 0
        self.last_check_result = None

    def check(self, force: bool = False) -> Dict[str, Any]:
        """
        Check health of service

        Args:
            force: Force check even if cached result is available

        Returns:
            Health check result
        """
        current_time = time.time()

        # Check if we can use cached result
        if (
            not force
            and self.last_check_result is not None
            and current_time - self.last_check_time < self.check_interval
        ):
            return self.last_check_result

        # Run the health check
        try:
            # Set timeout using threading.Timer
            result_container = {"result": None, "exception": None}

            def run_check():
                try:
                    result_container["result"] = self.check_fn()
                except Exception as e:
                    result_container["exception"] = e

            # Create and start the thread
            check_thread = threading.Thread(target=run_check)
            check_thread.daemon = True
            start_time = time.time()
            check_thread.start()
            check_thread.join(timeout=self.timeout)

            duration = time.time() - start_time

            if check_thread.is_alive():
                # Timeout occurred
                result = {
                    "status": HealthStatus.UNAVAILABLE,
                    "message": f"Health check timed out after {self.timeout} seconds",
                    "duration_ms": int(duration * 1000),
                    "timestamp": datetime.utcnow().isoformat(),
                }
            elif result_container["exception"] is not None:
                # Exception occurred
                result = {
                    "status": HealthStatus.UNAVAILABLE,
                    "message": f"Health check failed: {str(result_container['exception'])}",
                    "error": str(result_container["exception"]),
                    "duration_ms": int(duration * 1000),
                    "timestamp": datetime.utcnow().isoformat(),
                }
            else:
                # Successfully got result
                result = result_container["result"]
                if "duration_ms" not in result:
                    result["duration_ms"] = int(duration * 1000)
                if "timestamp" not in result:
                    result["timestamp"] = datetime.utcnow().isoformat()
        except Exception as e:
            # This should rarely happen since we catch exceptions in the thread
            logger.error(f"Error in health check {self.name}: {str(e)}")
            result = {
                "status": HealthStatus.UNAVAILABLE,
                "message": f"Health check error: {str(e)}",
                "error": str(e),
                "duration_ms": 0,
                "timestamp": datetime.utcnow().isoformat(),
            }

        # Update last check time and result
        self.last_check_time = current_time
        self.last_check_result = result

        return result


class CircuitBreaker:
    """
    Circuit breaker implementation for services to prevent cascading failures

    This implements a basic circuit breaker pattern:
    - CLOSED: Normal operation, failure count tracked
    - OPEN: Service requests blocked for a cooling period
    - HALF-OPEN: Testing if service has recovered
    """

    # Circuit breaker states
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Circuit tripped, failing fast
    HALF_OPEN = "half_open"  # Testing if service is back

    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        half_open_max_calls: int = 1,
    ):
        """
        Initialize circuit breaker

        Args:
            name: Name of the circuit (usually service name)
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Seconds to wait before trying service again
            half_open_max_calls: Max calls to allow in half-open state
        """
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_calls = half_open_max_calls

        self.state = self.CLOSED
        self.failure_count = 0
        self.last_failure_time = 0
        self.last_success_time = time.time()
        self.half_open_calls = 0
        self.lock = threading.RLock()

    def record_success(self) -> None:
        """Record a successful service call"""
        with self.lock:
            self.last_success_time = time.time()
            self.failure_count = 0
            if self.state != self.CLOSED:
                logger.info(f"Circuit breaker {self.name} closed after successful call")
                self.state = self.CLOSED
                self.half_open_calls = 0

    def record_failure(self) -> None:
        """Record a failed service call"""
        with self.lock:
            self.failure_count += 1
            self.last_failure_time = time.time()

            if (
                self.state == self.CLOSED
                and self.failure_count >= self.failure_threshold
            ):
                logger.warning(
                    f"Circuit breaker {self.name} tripped after {self.failure_count} failures"
                )
                self.state = self.OPEN
            elif self.state == self.HALF_OPEN:
                logger.warning(
                    f"Circuit breaker {self.name} reopened after test failure"
                )
                self.state = self.OPEN
                self.half_open_calls = 0

    def allow_request(self) -> bool:
        """
        Check if request should be allowed

        Returns:
            True if request is allowed, False if circuit is open
        """
        with self.lock:
            current_time = time.time()

            if self.state == self.CLOSED:
                return True
            elif self.state == self.OPEN:
                # Check if recovery timeout has elapsed
                if current_time - self.last_failure_time > self.recovery_timeout:
                    logger.info(
                        f"Circuit breaker {self.name} half-open after {self.recovery_timeout}s timeout"
                    )
                    self.state = self.HALF_OPEN
                    self.half_open_calls = 0
                    return True
                return False
            elif self.state == self.HALF_OPEN:
                # Allow limited calls in half-open state
                if self.half_open_calls < self.half_open_max_calls:
                    self.half_open_calls += 1
                    return True
                return False

            # Unknown state, allow request but warn
            logger.warning(
                f"Circuit breaker {self.name} in unknown state, allowing request"
            )
            return True

    def expected_recovery_time(self) -> Optional[float]:
        """
        Get expected recovery time in seconds

        Returns:
            Seconds until circuit might close, or None if closed
        """
        with self.lock:
            if self.state == self.CLOSED:
                return None
            elif self.state == self.OPEN:
                elapsed = time.time() - self.last_failure_time
                remaining = max(0, self.recovery_timeout - elapsed)
                return remaining
            elif self.state == self.HALF_OPEN:
                return 0  # Already in recovery
            return None

    def get_status(self) -> Dict[str, Any]:
        """
        Get current circuit breaker status

        Returns:
            Dictionary with status details
        """
        with self.lock:
            return {
                "name": self.name,
                "state": self.state,
                "failure_count": self.failure_count,
                "last_failure": (
                    datetime.fromtimestamp(self.last_failure_time).isoformat()
                    if self.last_failure_time > 0
                    else None
                ),
                "last_success": (
                    datetime.fromtimestamp(self.last_success_time).isoformat()
                    if self.last_success_time > 0
                    else None
                ),
                "recovery_timeout": self.recovery_timeout,
                "failure_threshold": self.failure_threshold,
                "expected_recovery_seconds": self.expected_recovery_time(),
            }


class HealthCheckRegistry:
    """Registry for health checks"""

    def __init__(self):
        """Initialize health check registry"""
        self.health_checks: Dict[str, HealthCheck] = {}
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.lock = threading.RLock()

    def register(self, health_check: HealthCheck) -> None:
        """
        Register a health check

        Args:
            health_check: Health check to register
        """
        with self.lock:
            self.health_checks[health_check.name] = health_check

            # Create a circuit breaker for this service if it's a critical LLM provider
            if (
                health_check.service_type == ServiceType.LLM_PROVIDER
                and health_check.is_critical
            ):
                self.circuit_breakers[health_check.name] = CircuitBreaker(
                    name=health_check.name,
                    failure_threshold=3,  # More aggressive for LLM providers
                    recovery_timeout=300,  # 5 minutes for API services
                )
                logger.info(f"Created circuit breaker for {health_check.name}")

    def unregister(self, name: str) -> None:
        """
        Unregister a health check

        Args:
            name: Name of health check to unregister
        """
        with self.lock:
            if name in self.health_checks:
                del self.health_checks[name]
            if name in self.circuit_breakers:
                del self.circuit_breakers[name]

    def get(self, name: str) -> Optional[HealthCheck]:
        """
        Get a health check by name

        Args:
            name: Name of health check to get

        Returns:
            Health check or None if not found
        """
        return self.health_checks.get(name)

    def get_all(self) -> Dict[str, HealthCheck]:
        """
        Get all health checks

        Returns:
            Dictionary of all health checks
        """
        return self.health_checks.copy()

    def get_by_type(self, service_type: ServiceType) -> Dict[str, HealthCheck]:
        """
        Get health checks by service type

        Args:
            service_type: Service type to filter by

        Returns:
            Dictionary of health checks of the specified type
        """
        return {
            name: check
            for name, check in self.health_checks.items()
            if check.service_type == service_type
        }

    def check_all(
        self, include_types: List[ServiceType] = None
    ) -> Dict[str, Dict[str, Any]]:
        """
        Check health of all registered services

        Args:
            include_types: List of service types to include (None for all)

        Returns:
            Dictionary of health check results
        """
        results = {}

        # Make a copy to avoid modification during iteration
        health_checks_to_check = self.health_checks.copy()

        for name, check in health_checks_to_check.items():
            # Skip if not in include_types
            if include_types and check.service_type not in include_types:
                continue

            # Check if circuit breaker allows the request
            if (
                name in self.circuit_breakers
                and not self.circuit_breakers[name].allow_request()
            ):
                # Circuit is open, fail fast
                recovery_time = self.circuit_breakers[name].expected_recovery_time()
                recovery_msg = (
                    f" (expected recovery in {int(recovery_time)}s)"
                    if recovery_time
                    else ""
                )

                results[name] = {
                    "status": HealthStatus.UNAVAILABLE,
                    "message": f"Circuit breaker open for {name}{recovery_msg}",
                    "circuit_breaker": self.circuit_breakers[name].get_status(),
                    "timestamp": datetime.utcnow().isoformat(),
                }
                continue

            try:
                result = check.check()
                results[name] = result

                # Update circuit breaker based on result
                if name in self.circuit_breakers:
                    status = result.get("status", HealthStatus.UNKNOWN)
                    if status == HealthStatus.OK:
                        self.circuit_breakers[name].record_success()
                    elif status in (HealthStatus.CRITICAL, HealthStatus.UNAVAILABLE):
                        self.circuit_breakers[name].record_failure()

            except Exception as e:
                logger.error(f"Error checking {name}: {str(e)}")
                results[name] = {
                    "status": HealthStatus.UNAVAILABLE,
                    "message": f"Error checking health: {str(e)}",
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat(),
                }

                # Record failure in circuit breaker
                if name in self.circuit_breakers:
                    self.circuit_breakers[name].record_failure()

        return results

    def get_overall_status(self) -> Tuple[HealthStatus, List[str]]:
        """
        Get overall health status based on critical services

        Returns:
            Tuple of (status, list of failing critical services)
        """
        overall_status = HealthStatus.OK
        failing_critical = []
        degraded_services = []

        for name, check in self.health_checks.items():
            # Skip non-critical services for overall status
            if not check.is_critical:
                continue

            # Check if circuit breaker is open
            if (
                name in self.circuit_breakers
                and not self.circuit_breakers[name].allow_request()
            ):
                failing_critical.append(f"{name} (circuit open)")
                overall_status = HealthStatus.CRITICAL
                continue

            result = check.check()
            status = result.get("status", HealthStatus.UNKNOWN)

            if status == HealthStatus.CRITICAL or status == HealthStatus.UNAVAILABLE:
                # Critical service is down
                failing_critical.append(name)
                overall_status = HealthStatus.CRITICAL
            elif (
                status == HealthStatus.DEGRADED
                and overall_status != HealthStatus.CRITICAL
            ):
                # Service is degraded (but not critical failure yet)
                degraded_services.append(name)
                overall_status = HealthStatus.DEGRADED

        return overall_status, failing_critical + degraded_services

    def get_circuit_breakers(self) -> Dict[str, Dict[str, Any]]:
        """
        Get status of all circuit breakers

        Returns:
            Dictionary of circuit breaker statuses
        """
        return {name: cb.get_status() for name, cb in self.circuit_breakers.items()}


# Create a global health check registry
health_check_registry = HealthCheckRegistry()


# Common health check implementations


def check_database_health() -> Dict[str, Any]:
    """
    Check database health

    Returns:
        Health check result
    """
    from app.database.connection import (
        check_database_connection,
        get_database_status,
        is_using_fallback,
    )

    # Get detailed database status
    db_status = get_database_status()

    # Determine overall status
    if not db_status.get("connected", False):
        if is_using_fallback():
            return {
                "status": HealthStatus.DEGRADED,
                "message": "Database connection failed, using fallback",
                "details": db_status,
                "using_fallback": True,
                "timestamp": datetime.utcnow().isoformat(),
            }
        else:
            return {
                "status": HealthStatus.CRITICAL,
                "message": "Database connection failed",
                "details": db_status,
                "using_fallback": False,
                "timestamp": datetime.utcnow().isoformat(),
            }

    # Database is connected
    return {
        "status": HealthStatus.OK,
        "message": "Database connection successful",
        "details": db_status,
        "using_fallback": is_using_fallback(),
        "timestamp": datetime.utcnow().isoformat(),
    }


def check_redis_health() -> Dict[str, Any]:
    """
    Check Redis health

    Returns:
        Health check result
    """
    from app.services.cache_service import cache_service

    # Get cache status
    cache_details = cache_service.get_status()

    # Determine overall status
    if not cache_service.is_redis_available():
        return {
            "status": HealthStatus.DEGRADED,
            "message": "Redis not available, using in-memory cache",
            "details": cache_details,
            "using_fallback": True,
            "timestamp": datetime.utcnow().isoformat(),
        }

    # Redis is available
    return {
        "status": HealthStatus.OK,
        "message": "Redis connection successful",
        "details": cache_details,
        "using_fallback": False,
        "timestamp": datetime.utcnow().isoformat(),
    }


def check_jwt_health() -> Dict[str, Any]:
    """
    Check JWT implementation health

    Returns:
        Health check result
    """
    from app.utils.jwt_wrapper import get_jwt_status, is_using_pyjwt

    # Get JWT status
    jwt_details = get_jwt_status()

    # Determine overall status
    if not is_using_pyjwt():
        return {
            "status": HealthStatus.DEGRADED,
            "message": "Using fallback JWT implementation",
            "details": jwt_details,
            "using_fallback": True,
            "timestamp": datetime.utcnow().isoformat(),
        }

    # PyJWT is available
    return {
        "status": HealthStatus.OK,
        "message": "Using PyJWT implementation",
        "details": jwt_details,
        "using_fallback": False,
        "timestamp": datetime.utcnow().isoformat(),
    }


def check_llm_provider_health(provider: str, api_key_env_var: str) -> Dict[str, Any]:
    """
    Check LLM provider health

    Args:
        provider: Provider name (openai, anthropic, google, etc.)
        api_key_env_var: Environment variable name for API key

    Returns:
        Health check result
    """
    # Check if API key is available
    api_key = os.getenv(api_key_env_var)
    if not api_key:
        return {
            "status": HealthStatus.UNAVAILABLE,
            "message": f"No API key found for {provider}",
            "api_key_configured": False,
            "timestamp": datetime.utcnow().isoformat(),
        }

    # Check if module is available
    provider_info = {
        "openai": {
            "dependency": "openai",
            "api_endpoint": "https://api.openai.com/v1/models",
            "headers": {"Authorization": f"Bearer {api_key}"},
        },
        "anthropic": {
            "dependency": "anthropic",
            "api_endpoint": "https://api.anthropic.com/v1/messages",
            "headers": {"x-api-key": api_key, "anthropic-version": "2023-06-01"},
        },
        "google": {
            "dependency": "google.generativeai",
            "api_endpoint": "https://generativelanguage.googleapis.com/v1beta/models",
            "params": {"key": api_key},
        },
    }

    if provider not in provider_info:
        return {
            "status": HealthStatus.UNKNOWN,
            "message": f"Unknown provider: {provider}",
            "timestamp": datetime.utcnow().isoformat(),
        }

    # Check if dependency is available
    provider_dependency = provider_info[provider]["dependency"]
    if provider_dependency == "openai":
        from app.utils.dependency_manager import openai_dependency

        if not openai_dependency.is_available():
            return {
                "status": HealthStatus.UNAVAILABLE,
                "message": f"{provider} module not available",
                "provider": provider,
                "dependency_available": False,
                "api_key_configured": bool(api_key),
                "timestamp": datetime.utcnow().isoformat(),
            }
    elif provider_dependency == "anthropic":
        from app.utils.dependency_manager import anthropic_dependency

        if not anthropic_dependency.is_available():
            return {
                "status": HealthStatus.UNAVAILABLE,
                "message": f"{provider} module not available",
                "provider": provider,
                "dependency_available": False,
                "api_key_configured": bool(api_key),
                "timestamp": datetime.utcnow().isoformat(),
            }
    elif provider_dependency == "google.generativeai":
        from app.utils.dependency_manager import google_ai_dependency

        if not google_ai_dependency.is_available():
            return {
                "status": HealthStatus.UNAVAILABLE,
                "message": f"{provider} module not available",
                "provider": provider,
                "dependency_available": False,
                "api_key_configured": bool(api_key),
                "timestamp": datetime.utcnow().isoformat(),
            }

    # Check API connection by making a lightweight request
    try:
        # Make request with proper error handling for each provider
        api_endpoint = provider_info[provider]["api_endpoint"]
        headers = provider_info[provider].get("headers", {})
        params = provider_info[provider].get("params", {})

        # Make the request
        start_time = time.time()
        response = requests.get(
            api_endpoint, headers=headers, params=params, timeout=HEALTH_CHECK_TIMEOUT
        )
        duration_ms = int((time.time() - start_time) * 1000)

        # Check response
        if response.status_code == 200:
            return {
                "status": HealthStatus.OK,
                "message": f"{provider} API connection successful",
                "provider": provider,
                "dependency_available": True,
                "api_key_configured": True,
                "duration_ms": duration_ms,
                "timestamp": datetime.utcnow().isoformat(),
            }
        elif response.status_code == 401 or response.status_code == 403:
            return {
                "status": HealthStatus.UNAVAILABLE,
                "message": f"{provider} API authentication failed",
                "provider": provider,
                "dependency_available": True,
                "api_key_configured": True,
                "api_key_valid": False,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
                "timestamp": datetime.utcnow().isoformat(),
            }
        else:
            return {
                "status": HealthStatus.DEGRADED,
                "message": f"{provider} API returned unexpected status",
                "provider": provider,
                "dependency_available": True,
                "api_key_configured": True,
                "status_code": response.status_code,
                "error": response.text[:200],  # Limit error text length
                "duration_ms": duration_ms,
                "timestamp": datetime.utcnow().isoformat(),
            }
    except requests.exceptions.Timeout:
        return {
            "status": HealthStatus.DEGRADED,
            "message": f"{provider} API request timed out",
            "provider": provider,
            "dependency_available": True,
            "api_key_configured": True,
            "duration_ms": HEALTH_CHECK_TIMEOUT * 1000,
            "timestamp": datetime.utcnow().isoformat(),
        }
    except requests.exceptions.ConnectionError:
        return {
            "status": HealthStatus.UNAVAILABLE,
            "message": f"{provider} API connection failed",
            "provider": provider,
            "dependency_available": True,
            "api_key_configured": True,
            "error": "Connection error",
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        return {
            "status": HealthStatus.UNAVAILABLE,
            "message": f"{provider} API check failed: {str(e)}",
            "provider": provider,
            "dependency_available": True,
            "api_key_configured": True,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
        }


def check_system_health() -> Dict[str, Any]:
    """
    Check system health (CPU, memory, disk)

    Returns:
        Health check result
    """
    import psutil

    try:
        # Get system information
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        cpu_percent = psutil.cpu_percent(interval=0.1)

        # Define threshold limits
        memory_threshold_critical = 95  # %
        memory_threshold_warning = 85  # %
        disk_threshold_critical = 95  # %
        disk_threshold_warning = 85  # %
        cpu_threshold_critical = 95  # %
        cpu_threshold_warning = 80  # %

        # Determine status based on thresholds
        is_critical = False
        is_warning = False

        warnings = []
        criticals = []

        # Check memory
        if memory.percent >= memory_threshold_critical:
            criticals.append(f"Memory usage critical: {memory.percent}%")
            is_critical = True
        elif memory.percent >= memory_threshold_warning:
            warnings.append(f"Memory usage high: {memory.percent}%")
            is_warning = True

        # Check disk
        if disk.percent >= disk_threshold_critical:
            criticals.append(f"Disk usage critical: {disk.percent}%")
            is_critical = True
        elif disk.percent >= disk_threshold_warning:
            warnings.append(f"Disk usage high: {disk.percent}%")
            is_warning = True

        # Check CPU
        if cpu_percent >= cpu_threshold_critical:
            criticals.append(f"CPU usage critical: {cpu_percent}%")
            is_critical = True
        elif cpu_percent >= cpu_threshold_warning:
            warnings.append(f"CPU usage high: {cpu_percent}%")
            is_warning = True

        # Determine overall status
        if is_critical:
            status = HealthStatus.CRITICAL
            message = "System resources critically low"
        elif is_warning:
            status = HealthStatus.DEGRADED
            message = "System resources running low"
        else:
            status = HealthStatus.OK
            message = "System resources OK"

        # Update Prometheus metrics
        try:
            from app.utils.metrics import MetricsCollector

            metrics = MetricsCollector()
            metrics.update_system_metrics()
        except ImportError:
            # Continue even if Prometheus is not available
            pass

        # Build response
        return {
            "status": status,
            "message": message,
            "warnings": warnings,
            "criticals": criticals,
            "details": {
                "memory": {
                    "total_gb": round(memory.total / (1024**3), 2),
                    "available_gb": round(memory.available / (1024**3), 2),
                    "used_gb": round((memory.total - memory.available) / (1024**3), 2),
                    "percent": memory.percent,
                },
                "disk": {
                    "total_gb": round(disk.total / (1024**3), 2),
                    "free_gb": round(disk.free / (1024**3), 2),
                    "used_gb": round(disk.used / (1024**3), 2),
                    "percent": disk.percent,
                },
                "cpu": {
                    "percent": cpu_percent,
                    "cores": psutil.cpu_count(logical=False),
                    "logical_cores": psutil.cpu_count(logical=True),
                },
            },
            "metrics_enabled": True,
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        return {
            "status": HealthStatus.UNKNOWN,
            "message": f"Failed to check system health: {str(e)}",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
        }


def check_network_health(
    domain: str = "api.openai.com", port: int = 443
) -> Dict[str, Any]:
    """
    Check network connectivity by testing if a domain is reachable

    Args:
        domain: Domain to check
        port: Port to check

    Returns:
        Health check result
    """
    start_time = time.time()

    try:
        # Try to resolve the domain
        addresses = socket.getaddrinfo(domain, port)

        # Try to connect to the first address
        for addr in addresses:
            sockaddr = addr[4]
            try:
                s = socket.socket(addr[0], addr[1])
                s.settimeout(HEALTH_CHECK_TIMEOUT)
                s.connect(sockaddr)
                s.close()

                # Add SSL verification for HTTPS domains
                if port == 443:
                    try:
                        context = ssl.create_default_context()
                        with socket.create_connection(
                            (domain, port), timeout=HEALTH_CHECK_TIMEOUT
                        ) as sock:
                            with context.wrap_socket(
                                sock, server_hostname=domain
                            ) as ssock:
                                cert = ssock.getpeercert()
                    except ssl.SSLError as e:
                        return {
                            "status": HealthStatus.DEGRADED,
                            "message": f"SSL verification failed for {domain}:{port}",
                            "domain": domain,
                            "port": port,
                            "error": str(e),
                            "duration_ms": int((time.time() - start_time) * 1000),
                            "timestamp": datetime.utcnow().isoformat(),
                        }

                # Connection successful
                return {
                    "status": HealthStatus.OK,
                    "message": f"Connection to {domain}:{port} successful",
                    "domain": domain,
                    "port": port,
                    "duration_ms": int((time.time() - start_time) * 1000),
                    "timestamp": datetime.utcnow().isoformat(),
                }
            except socket.timeout:
                return {
                    "status": HealthStatus.DEGRADED,
                    "message": f"Connection to {domain}:{port} timed out",
                    "domain": domain,
                    "port": port,
                    "error": "Connection timed out",
                    "duration_ms": int((time.time() - start_time) * 1000),
                    "timestamp": datetime.utcnow().isoformat(),
                }
            except Exception as e:
                continue  # Try next address if available

        return {
            "status": HealthStatus.UNAVAILABLE,
            "message": f"Failed to connect to {domain}:{port}",
            "domain": domain,
            "port": port,
            "error": "All addresses failed",
            "duration_ms": int((time.time() - start_time) * 1000),
            "timestamp": datetime.utcnow().isoformat(),
        }
    except socket.gaierror:
        return {
            "status": HealthStatus.UNAVAILABLE,
            "message": f"Failed to resolve {domain}",
            "domain": domain,
            "port": port,
            "error": "Domain resolution failed",
            "duration_ms": int((time.time() - start_time) * 1000),
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        return {
            "status": HealthStatus.UNAVAILABLE,
            "message": f"Network check error: {str(e)}",
            "domain": domain,
            "port": port,
            "error": str(e),
            "duration_ms": int((time.time() - start_time) * 1000),
            "timestamp": datetime.utcnow().isoformat(),
        }


def check_storage_health(path: str = "document_storage") -> Dict[str, Any]:
    """
    Check if storage directory is available and writable

    Args:
        path: Path to check

    Returns:
        Health check result
    """
    import os
    import tempfile
    import uuid

    start_time = time.time()

    try:
        # Make sure directory exists
        if not os.path.exists(path):
            try:
                os.makedirs(path)
            except Exception as e:
                return {
                    "status": HealthStatus.CRITICAL,
                    "message": f"Storage directory {path} does not exist and could not be created",
                    "path": path,
                    "error": str(e),
                    "duration_ms": int((time.time() - start_time) * 1000),
                    "timestamp": datetime.utcnow().isoformat(),
                }

        # Check if directory is writable by creating a temp file
        temp_filename = f"healthcheck_{uuid.uuid4().hex}.tmp"
        temp_filepath = os.path.join(path, temp_filename)

        try:
            with open(temp_filepath, "w") as f:
                f.write("test")
            os.remove(temp_filepath)

            # Directory is writable
            return {
                "status": HealthStatus.OK,
                "message": f"Storage directory {path} is writable",
                "path": path,
                "duration_ms": int((time.time() - start_time) * 1000),
                "timestamp": datetime.utcnow().isoformat(),
            }
        except Exception as e:
            return {
                "status": HealthStatus.CRITICAL,
                "message": f"Storage directory {path} is not writable",
                "path": path,
                "error": str(e),
                "duration_ms": int((time.time() - start_time) * 1000),
                "timestamp": datetime.utcnow().isoformat(),
            }
    except Exception as e:
        return {
            "status": HealthStatus.UNAVAILABLE,
            "message": f"Storage check error: {str(e)}",
            "path": path,
            "error": str(e),
            "duration_ms": int((time.time() - start_time) * 1000),
            "timestamp": datetime.utcnow().isoformat(),
        }
