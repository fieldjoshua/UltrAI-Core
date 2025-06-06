"""
Unified monitoring system for UltraAI backend.

This module integrates structured logging, health checks, metrics collection,
and other monitoring components into a cohesive system for observability.
It provides functions to initialize and configure the monitoring system
and integrate it with the FastAPI application.
"""

import logging
import os
import time
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from backend.config import Config
from backend.utils.health_check import (
    CircuitBreaker,
    HealthCheck,
    HealthCheckRegistry,
    HealthStatus,
    ServiceType,
    check_database_health,
    check_llm_provider_health,
    check_redis_health,
    check_system_health,
    health_check_registry,
)
from backend.utils.structured_logging import (
    EnhancedLogger,
    LogCategory,
    RequestContext,
    apply_structured_logging_middleware,
    configure_logging,
    get_enhanced_logger,
    setup_structured_logging_middleware,
    with_performance_logging,
    with_request_context,
)

# Create logger for this module
logger = get_enhanced_logger(__name__)


class MonitoringSystem:
    """Unified monitoring system for the UltraAI backend"""

    _instance = None

    def __new__(cls):
        """Singleton pattern to ensure only one monitoring system is created"""
        if cls._instance is None:
            cls._instance = super(MonitoringSystem, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize monitoring system if not already initialized"""
        if self._initialized:
            return

        self.health_registry = health_check_registry
        self.log_level = os.environ.get("LOG_LEVEL", "INFO")
        self.app_name = os.environ.get("APP_NAME", "ultra")
        self.environment = os.environ.get("ENVIRONMENT", "development")
        self.metrics_enabled = os.environ.get("ENABLE_METRICS", "false").lower() in (
            "true",
            "1",
            "yes",
        )
        self.start_time = time.time()
        self._initialized = True

    def configure(self, app: FastAPI) -> None:
        """
        Configure monitoring for the FastAPI application

        Args:
            app: FastAPI application to configure
        """
        # Configure structured logging
        log_dir = os.environ.get("LOG_DIR", "logs")
        enable_json = os.environ.get("LOG_JSON", "true").lower() in ("true", "1", "yes")

        configure_logging(
            app_name=self.app_name,
            log_level=self.log_level,
            log_dir=log_dir,
            enable_json_logging=enable_json,
            console_output=True,
            log_file_output=True,
        )

        # Set up logging middleware but don't apply it yet (just configure it)
        setup_structured_logging_middleware(app)

        # Register basic health checks
        self._register_health_checks()

        # Configure request tracking middleware
        @app.middleware("http")
        async def request_tracking_middleware(request: Request, call_next):
            # Generate request ID if not present
            request_id = request.headers.get("X-Request-ID")
            if not request_id:
                request_id = str(RequestContext.get_request_id())

            # Set request context
            RequestContext.set_request_id(request_id)

            # Extract user ID if available
            user_id = None
            if hasattr(request.state, "user"):
                user_id = getattr(request.state.user, "id", None)

            if user_id:
                RequestContext.set_user_id(str(user_id))

            # Process request with context
            start_time = time.time()
            try:
                response = await call_next(request)

                # Add request ID to response headers
                response.headers["X-Request-ID"] = request_id

                # Calculate request duration
                duration_ms = (time.time() - start_time) * 1000

                # Add timing header for debugging
                if Config.DEBUG:
                    response.headers["X-Response-Time"] = f"{duration_ms:.2f}ms"

                # Log request completion
                logger.info(
                    f"Request completed: {request.method} {request.url.path}",
                    category=LogCategory.REQUEST,
                    extra={
                        "method": request.method,
                        "path": request.url.path,
                        "status_code": response.status_code,
                        "duration_ms": duration_ms,
                        "client_ip": request.client.host if request.client else None,
                    },
                )

                return response
            except Exception as e:
                # Calculate duration even for errors
                duration_ms = (time.time() - start_time) * 1000

                # Log error
                logger.error(
                    f"Error processing request: {request.method} {request.url.path}",
                    exc_info=e,
                    category=LogCategory.ERROR,
                    extra={
                        "method": request.method,
                        "path": request.url.path,
                        "duration_ms": duration_ms,
                        "error": str(e),
                        "error_type": e.__class__.__name__,
                    },
                )
                raise
            finally:
                # Clear request context
                RequestContext.clear()

        # Log successful initialization
        logger.info(
            f"Monitoring system initialized for {self.app_name} in {self.environment} environment",
            extra={
                "app_name": self.app_name,
                "environment": self.environment,
                "log_level": self.log_level,
                "metrics_enabled": self.metrics_enabled,
            },
        )

    def _register_health_checks(self) -> None:
        """Register default health checks with the registry"""
        try:
            # Database health check
            self.health_registry.register(
                HealthCheck(
                    name="database",
                    service_type=ServiceType.DATABASE,
                    check_fn=check_database_health,
                    description="Database connectivity and query execution",
                    is_critical=True,
                    check_interval=60,  # Check every 60 seconds
                )
            )

            # Redis health check (if configured)
            if os.environ.get("REDIS_URL"):
                self.health_registry.register(
                    HealthCheck(
                        name="redis",
                        service_type=ServiceType.CACHE,
                        check_fn=check_redis_health,
                        description="Redis cache connectivity",
                        is_critical=False,
                        check_interval=60,
                    )
                )

            # LLM provider health checks (if not in mock mode)
            if not Config.USE_MOCK and not Config.MOCK_MODE:
                # OpenAI
                if os.environ.get("OPENAI_API_KEY"):
                    self.health_registry.register(
                        HealthCheck(
                            name="openai",
                            service_type=ServiceType.LLM_PROVIDER,
                            check_fn=lambda: check_llm_provider_health(
                                "openai", "OPENAI_API_KEY"
                            ),
                            description="OpenAI API connectivity",
                            is_critical=Config.DEFAULT_PROVIDER == "openai",
                            check_interval=300,  # Check every 5 minutes
                        )
                    )

                # Anthropic
                if os.environ.get("ANTHROPIC_API_KEY"):
                    self.health_registry.register(
                        HealthCheck(
                            name="anthropic",
                            service_type=ServiceType.LLM_PROVIDER,
                            check_fn=lambda: check_llm_provider_health(
                                "anthropic", "ANTHROPIC_API_KEY"
                            ),
                            description="Anthropic API connectivity",
                            is_critical=Config.DEFAULT_PROVIDER == "anthropic",
                            check_interval=300,
                        )
                    )

                # Google AI
                if os.environ.get("GOOGLE_API_KEY"):
                    self.health_registry.register(
                        HealthCheck(
                            name="google",
                            service_type=ServiceType.LLM_PROVIDER,
                            check_fn=lambda: check_llm_provider_health(
                                "google", "GOOGLE_API_KEY"
                            ),
                            description="Google AI API connectivity",
                            is_critical=Config.DEFAULT_PROVIDER == "google",
                            check_interval=300,
                        )
                    )

            # System health check
            self.health_registry.register(
                HealthCheck(
                    name="system",
                    service_type=ServiceType.SYSTEM,
                    check_fn=check_system_health,
                    description="System resources (CPU, memory, disk)",
                    is_critical=True,
                    check_interval=60,
                )
            )

            logger.info("Health checks registered with monitoring system")
        except Exception as e:
            logger.error(f"Error registering health checks: {str(e)}", exc_info=e)

    def get_status(self) -> Dict[str, Any]:
        """
        Get overall monitoring system status

        Returns:
            Dictionary with monitoring system status
        """
        uptime_seconds = time.time() - self.start_time

        # Get overall health status
        health_status, failing_services = self.health_registry.get_overall_status()

        # Get circuit breaker information
        circuit_breakers = self.health_registry.get_circuit_breakers()
        open_circuits = [
            name for name, cb in circuit_breakers.items() if cb["state"] != "closed"
        ]

        return {
            "status": "healthy" if health_status == HealthStatus.OK else "degraded",
            "uptime_seconds": uptime_seconds,
            "environment": self.environment,
            "app_name": self.app_name,
            "health": {
                "status": health_status.value,
                "failing_services": failing_services,
            },
            "circuit_breakers": {
                "total": len(circuit_breakers),
                "open": len(open_circuits),
                "open_circuits": open_circuits,
            },
            "logging": {
                "level": self.log_level,
                "json_enabled": os.environ.get("LOG_JSON", "true").lower()
                in ("true", "1", "yes"),
            },
            "metrics": {
                "enabled": self.metrics_enabled,
            },
        }


# Singleton instance
monitoring_system = MonitoringSystem()


def setup_monitoring(app: FastAPI) -> None:
    """
    Set up monitoring for a FastAPI application

    Args:
        app: FastAPI application to configure
    """
    monitoring_system.configure(app)


def get_uptime() -> float:
    """
    Get application uptime in seconds

    Returns:
        Uptime in seconds
    """
    return time.time() - monitoring_system.start_time


def log_startup_event(app_name: str, version: str, config: Dict[str, Any]) -> None:
    """
    Log application startup event with important configuration details

    Args:
        app_name: Application name
        version: Application version
        config: Application configuration
    """
    # Sanitize config to remove sensitive values
    safe_config = {}
    sensitive_keys = ["api_key", "password", "secret", "token", "key"]

    for key, value in config.items():
        # Skip keys with sensitive information
        if any(sensitive in key.lower() for sensitive in sensitive_keys):
            safe_config[key] = "[REDACTED]"
        else:
            safe_config[key] = value

    # Log startup
    logger.info(
        f"{app_name} v{version} starting up",
        category=LogCategory.SYSTEM,
        extra={
            "app_name": app_name,
            "version": version,
            "environment": monitoring_system.environment,
            "config": safe_config,
        },
    )
