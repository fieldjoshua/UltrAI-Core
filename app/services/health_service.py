"""
Health service for the Ultra backend.

This module provides functionality for checking the health of various components of the system
and returning a comprehensive health status.
"""

import datetime
import logging
import os
import platform
import socket
import sys
from typing import Any, Dict, List, Optional, Tuple

import psutil

from app.config import Config
from app.services.cache_service import cache_service
from app.services.llm_config_service import llm_config_service

# Configure logging
logger = logging.getLogger("health_service")


class HealthService:
    """Service for checking application health"""

    def __init__(self):
        """Initialize the health service"""
        self.start_time = datetime.datetime.now()
        self.last_check_time = None
        self.service_status = {}
        self.dependency_status = {}

        # Initialize with default status
        self._update_system_info()

    def get_health_status(self, detailed: bool = False) -> Dict[str, Any]:
        """
        Get the health status of the application

        Args:
            detailed: Whether to include detailed information

        Returns:
            Dictionary with health status information
        """
        self.last_check_time = datetime.datetime.now()

        # Basic health info
        health_info = {
            "status": "ok",
            "timestamp": self.last_check_time.isoformat(),
            "uptime": str(self.last_check_time - self.start_time),
            "environment": Config.ENVIRONMENT,
            "version": os.getenv("ULTRA_VERSION", "1.0.0"),
        }

        # Add services status
        self._check_services()
        health_info["services"] = {
            name: info["status"] for name, info in self.service_status.items()
        }

        # Check if any service is degraded or down
        degraded_services = [
            name
            for name, info in self.service_status.items()
            if info["status"] != "healthy"
        ]

        if degraded_services:
            health_info["status"] = "degraded"
            health_info["degraded_services"] = degraded_services

        # Add detailed information if requested
        if detailed:
            self._update_system_info()
            health_info["system"] = self.system_info
            health_info["dependencies"] = self._check_dependencies()
            health_info["configuration"] = {
                "mock_mode": Config.USE_MOCK or Config.MOCK_MODE,
                "cache_enabled": Config.ENABLE_CACHE,
                "auth_enabled": Config.ENABLE_AUTH,
                "rate_limit_enabled": Config.ENABLE_RATE_LIMIT,
                "debug": Config.DEBUG,
            }
            health_info["service_details"] = self.service_status

            # Add LLM provider information if available
            if llm_config_service:
                available_models = llm_config_service.get_available_models()
                health_info["llm_providers"] = {
                    "count": len(available_models),
                    "providers": [model["provider"] for model in available_models],
                    "default_provider": Config.DEFAULT_PROVIDER,
                    "default_model": Config.DEFAULT_MODEL,
                }

        return health_info

    def _update_system_info(self) -> None:
        """Update system information"""
        try:
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")

            self.system_info = {
                "hostname": socket.gethostname(),
                "os": {
                    "platform": sys.platform,
                    "name": platform.system(),
                    "version": platform.version(),
                    "release": platform.release(),
                },
                "python": {
                    "version": platform.python_version(),
                    "implementation": platform.python_implementation(),
                },
                "resources": {
                    "cpu_count": os.cpu_count(),
                    "cpu_percent": psutil.cpu_percent(interval=None),
                    "memory_total": memory.total,
                    "memory_available": memory.available,
                    "memory_percent": memory.percent,
                    "disk_total": disk.total,
                    "disk_free": disk.free,
                    "disk_percent": disk.percent,
                },
            }
        except Exception as e:
            logger.error(f"Error updating system info: {str(e)}")
            self.system_info = {
                "hostname": socket.gethostname(),
                "error": f"Failed to get complete system info: {str(e)}",
            }

    def _check_services(self) -> None:
        """Check the status of all services"""
        # Check database connection
        self._check_database()

        # Check cache connection
        self._check_cache()

        # Check LLM services
        self._check_llm_services()

        # If in mock mode, check mock services
        if Config.USE_MOCK or Config.MOCK_MODE:
            self._check_mock_services()

    def _check_database(self) -> None:
        """Check database connection"""
        try:
            # Import here to avoid circular imports
            from app.database.connection import check_database_connection

            if check_database_connection():
                self.service_status["database"] = {
                    "status": "healthy",
                    "message": "Database connection is working",
                    "last_checked": datetime.datetime.now().isoformat(),
                }
            else:
                self.service_status["database"] = {
                    "status": "degraded",
                    "message": "Database connection is not available",
                    "last_checked": datetime.datetime.now().isoformat(),
                }
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            self.service_status["database"] = {
                "status": "critical",
                "message": f"Database error: {str(e)}",
                "last_checked": datetime.datetime.now().isoformat(),
            }

    def _check_cache(self) -> None:
        """Check cache connection"""
        try:
            if cache_service and hasattr(cache_service, 'is_redis_available'):
                cache_type = "redis" if cache_service.is_redis_available() else "memory"
                self.service_status["cache"] = {
                    "status": "healthy",
                    "message": f"Cache service is working ({cache_type})",
                    "type": cache_type,
                    "last_checked": datetime.datetime.now().isoformat(),
                }
            else:
                self.service_status["cache"] = {
                    "status": "degraded",
                    "message": "Cache service is not available",
                    "last_checked": datetime.datetime.now().isoformat(),
                }
        except Exception as e:
            logger.error(f"Cache health check failed: {str(e)}")
            self.service_status["cache"] = {
                "status": "degraded",
                "message": f"Cache error: {str(e)}",
                "last_checked": datetime.datetime.now().isoformat(),
            }

    def _check_llm_services(self) -> None:
        """Check LLM services"""
        try:
            if not Config.USE_MOCK and not Config.MOCK_MODE:
                # Check if LLM config service has providers
                if llm_config_service:
                    models = llm_config_service.get_available_models()
                    if models:
                        # Check individual provider connectivity
                        providers_status = self._check_llm_provider_connectivity()
                        available_providers = [
                            p
                            for p, status in providers_status.items()
                            if status.get("status") in ["healthy", "ok"]
                        ]

                        if available_providers:
                            self.service_status["llm"] = {
                                "status": "healthy",
                                "message": f"LLM services are available ({len(models)} models, {len(available_providers)} providers)",
                                "providers": [model["provider"] for model in models.values()],
                                "last_checked": datetime.datetime.now().isoformat(),
                                "provider_details": providers_status,
                            }
                        else:
                            self.service_status["llm"] = {
                                "status": "degraded",
                                "message": "Models configured but no providers are reachable",
                                "providers": [model["provider"] for model in models.values()],
                                "last_checked": datetime.datetime.now().isoformat(),
                                "provider_details": providers_status,
                            }
                    else:
                        self.service_status["llm"] = {
                            "status": "degraded",
                            "message": "No LLM models available",
                            "last_checked": datetime.datetime.now().isoformat(),
                        }
                else:
                    self.service_status["llm"] = {
                        "status": "critical",
                        "message": "LLM config service not initialized",
                        "last_checked": datetime.datetime.now().isoformat(),
                    }
            else:
                self.service_status["llm"] = {
                    "status": "healthy",
                    "message": "Using mock LLM services",
                    "last_checked": datetime.datetime.now().isoformat(),
                }
        except Exception as e:
            logger.error(f"LLM health check failed: {str(e)}")
            self.service_status["llm"] = {
                "status": "critical",
                "message": f"LLM service error: {str(e)}",
                "last_checked": datetime.datetime.now().isoformat(),
            }

    def _check_llm_provider_connectivity(self) -> Dict[str, Dict[str, Any]]:
        """
        Check connectivity to each LLM provider

        Returns:
            Dictionary of provider status information
        """
        from app.utils.dependency_manager import (
            anthropic_dependency,
            google_ai_dependency,
            openai_dependency,
        )
        from app.utils.health_check import check_llm_provider_health

        results = {}

        # Check OpenAI connectivity
        if openai_dependency.is_available():
            try:
                results["openai"] = check_llm_provider_health(
                    "openai", "OPENAI_API_KEY"
                )
            except Exception as e:
                logger.error(f"OpenAI health check failed: {str(e)}")
                results["openai"] = {
                    "status": "critical",
                    "message": f"OpenAI health check error: {str(e)}",
                    "timestamp": datetime.datetime.now().isoformat(),
                }

        # Check Anthropic connectivity
        if anthropic_dependency.is_available():
            try:
                results["anthropic"] = check_llm_provider_health(
                    "anthropic", "ANTHROPIC_API_KEY"
                )
            except Exception as e:
                logger.error(f"Anthropic health check failed: {str(e)}")
                results["anthropic"] = {
                    "status": "critical",
                    "message": f"Anthropic health check error: {str(e)}",
                    "timestamp": datetime.datetime.now().isoformat(),
                }

        # Check Google Gemini connectivity
        if google_ai_dependency.is_available():
            try:
                results["google"] = check_llm_provider_health(
                    "google", "GOOGLE_API_KEY"
                )
            except Exception as e:
                logger.error(f"Google Gemini health check failed: {str(e)}")
                results["google"] = {
                    "status": "critical",
                    "message": f"Google Gemini health check error: {str(e)}",
                    "timestamp": datetime.datetime.now().isoformat(),
                }

        # Check if model runner is available
        try:
            if os.getenv("USE_MODEL_RUNNER", "false").lower() in ("true", "1", "yes"):
                # For model runner, we'll use a simpler check since it's local
                import subprocess

                try:
                    # Use a quick command to check if Docker Model Runner is responsive
                    result = subprocess.run(
                        ["docker", "model", "list"],
                        capture_output=True,
                        text=True,
                        check=False,
                        timeout=5,  # Short timeout
                    )

                    if result.returncode == 0:
                        # Parse output to get model count
                        lines = result.stdout.strip().split("\n")
                        model_count = max(0, len(lines) - 1)  # Subtract header line

                        results["model_runner"] = {
                            "status": "healthy",
                            "message": f"Docker Model Runner is available with {model_count} models",
                            "models": model_count,
                            "timestamp": datetime.datetime.now().isoformat(),
                        }
                    else:
                        results["model_runner"] = {
                            "status": "degraded",
                            "message": f"Docker Model Runner returned error: {result.stderr}",
                            "timestamp": datetime.datetime.now().isoformat(),
                        }
                except subprocess.TimeoutExpired:
                    results["model_runner"] = {
                        "status": "degraded",
                        "message": "Docker Model Runner command timed out",
                        "timestamp": datetime.datetime.now().isoformat(),
                    }
                except Exception as e:
                    results["model_runner"] = {
                        "status": "critical",
                        "message": f"Docker Model Runner check failed: {str(e)}",
                        "timestamp": datetime.datetime.now().isoformat(),
                    }
        except Exception as e:
            logger.error(f"Model runner health check failed: {str(e)}")

        return results

    def _check_mock_services(self) -> None:
        """Check mock services"""
        try:
            from app.services.mock_llm_service import mock_llm_service

            if mock_llm_service:
                self.service_status["mock_llm"] = {
                    "status": "healthy",
                    "message": "Mock LLM service is available",
                    "last_checked": datetime.datetime.now().isoformat(),
                }
            else:
                self.service_status["mock_llm"] = {
                    "status": "degraded",
                    "message": "Mock LLM service not initialized",
                    "last_checked": datetime.datetime.now().isoformat(),
                }
        except Exception as e:
            logger.error(f"Mock service health check failed: {str(e)}")
            self.service_status["mock_llm"] = {
                "status": "degraded",
                "message": f"Mock service error: {str(e)}",
                "last_checked": datetime.datetime.now().isoformat(),
            }

    def _check_dependencies(self) -> Dict[str, str]:
        """Check dependencies and their versions"""
        dependencies = {}

        try:
            import pkg_resources

            # Get all installed packages
            for pkg in pkg_resources.working_set:
                if pkg.key in [
                    "fastapi",
                    "uvicorn",
                    "sqlalchemy",
                    "redis",
                    "openai",
                    "anthropic",
                    "google-generative-ai",
                    "pydantic",
                    "python-jose",
                    "passlib",
                ]:
                    dependencies[pkg.key] = pkg.version
        except Exception as e:
            logger.error(f"Error checking dependencies: {str(e)}")
            dependencies["error"] = str(e)

        return dependencies

    def check_service_status(self, service_name: str) -> Tuple[str, str]:
        """
        Check a specific service status

        Args:
            service_name: Name of the service to check

        Returns:
            Tuple of (status, message)
        """
        if service_name not in self.service_status:
            self._check_services()

        if service_name in self.service_status:
            return (
                self.service_status[service_name]["status"],
                self.service_status[service_name]["message"],
            )

        return "unknown", f"Service {service_name} not found"


# Initialize health service
health_service = HealthService()
