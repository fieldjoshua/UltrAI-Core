"""
Health service for the Ultra backend.

This module provides functionality for checking the health of various components of the system
and returning a comprehensive health status.
"""

import os
import sys
import platform
import socket
import logging
import psutil
import datetime
from typing import Dict, Any, List, Optional, Tuple

from backend.config import Config
from backend.services.cache_service import cache_service
from backend.services.llm_config_service import llm_config_service

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
            "version": os.getenv("ULTRA_VERSION", "1.0.0")
        }
        
        # Add services status
        self._check_services()
        health_info["services"] = {name: info["status"] for name, info in self.service_status.items()}
        
        # Check if any service is degraded or down
        degraded_services = [name for name, info in self.service_status.items() 
                            if info["status"] != "healthy"]
        
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
                "debug": Config.DEBUG
            }
            health_info["service_details"] = self.service_status
            
            # Add LLM provider information if available
            if llm_config_service:
                available_models = llm_config_service.get_available_models()
                health_info["llm_providers"] = {
                    "count": len(available_models),
                    "providers": [model["provider"] for model in available_models],
                    "default_provider": Config.DEFAULT_PROVIDER,
                    "default_model": Config.DEFAULT_MODEL
                }
        
        return health_info
    
    def _update_system_info(self) -> None:
        """Update system information"""
        try:
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            self.system_info = {
                "hostname": socket.gethostname(),
                "os": {
                    "platform": sys.platform,
                    "name": platform.system(),
                    "version": platform.version(),
                    "release": platform.release()
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
                    "disk_percent": disk.percent
                }
            }
        except Exception as e:
            logger.error(f"Error updating system info: {str(e)}")
            self.system_info = {
                "hostname": socket.gethostname(),
                "error": f"Failed to get complete system info: {str(e)}"
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
            from backend.database.connection import get_db_connection
            
            conn = get_db_connection()
            if conn:
                # Try a simple query
                conn.execute("SELECT 1").fetchone()
                self.service_status["database"] = {
                    "status": "healthy",
                    "message": "Database connection is working",
                    "last_checked": datetime.datetime.now().isoformat()
                }
            else:
                self.service_status["database"] = {
                    "status": "degraded",
                    "message": "Database connection is not available",
                    "last_checked": datetime.datetime.now().isoformat()
                }
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            self.service_status["database"] = {
                "status": "critical",
                "message": f"Database error: {str(e)}",
                "last_checked": datetime.datetime.now().isoformat()
            }
    
    def _check_cache(self) -> None:
        """Check cache connection"""
        try:
            if cache_service and cache_service.is_available():
                cache_info = cache_service.get_info()
                self.service_status["cache"] = {
                    "status": "healthy",
                    "message": "Cache service is working",
                    "type": cache_info.get("type", "unknown"),
                    "last_checked": datetime.datetime.now().isoformat()
                }
            else:
                self.service_status["cache"] = {
                    "status": "degraded",
                    "message": "Cache service is not available",
                    "last_checked": datetime.datetime.now().isoformat()
                }
        except Exception as e:
            logger.error(f"Cache health check failed: {str(e)}")
            self.service_status["cache"] = {
                "status": "degraded",
                "message": f"Cache error: {str(e)}",
                "last_checked": datetime.datetime.now().isoformat()
            }
    
    def _check_llm_services(self) -> None:
        """Check LLM services"""
        try:
            if not Config.USE_MOCK and not Config.MOCK_MODE:
                # Check if LLM config service has providers
                if llm_config_service:
                    models = llm_config_service.get_available_models()
                    if models:
                        self.service_status["llm"] = {
                            "status": "healthy",
                            "message": f"LLM services are available ({len(models)} models)",
                            "providers": [model["provider"] for model in models],
                            "last_checked": datetime.datetime.now().isoformat()
                        }
                    else:
                        self.service_status["llm"] = {
                            "status": "degraded",
                            "message": "No LLM models available",
                            "last_checked": datetime.datetime.now().isoformat()
                        }
                else:
                    self.service_status["llm"] = {
                        "status": "critical",
                        "message": "LLM config service not initialized",
                        "last_checked": datetime.datetime.now().isoformat()
                    }
            else:
                self.service_status["llm"] = {
                    "status": "healthy",
                    "message": "Using mock LLM services",
                    "last_checked": datetime.datetime.now().isoformat()
                }
        except Exception as e:
            logger.error(f"LLM health check failed: {str(e)}")
            self.service_status["llm"] = {
                "status": "critical",
                "message": f"LLM service error: {str(e)}",
                "last_checked": datetime.datetime.now().isoformat()
            }
    
    def _check_mock_services(self) -> None:
        """Check mock services"""
        try:
            from backend.services.mock_llm_service import mock_llm_service
            
            if mock_llm_service:
                self.service_status["mock_llm"] = {
                    "status": "healthy",
                    "message": "Mock LLM service is available",
                    "last_checked": datetime.datetime.now().isoformat()
                }
            else:
                self.service_status["mock_llm"] = {
                    "status": "degraded",
                    "message": "Mock LLM service not initialized",
                    "last_checked": datetime.datetime.now().isoformat()
                }
        except Exception as e:
            logger.error(f"Mock service health check failed: {str(e)}")
            self.service_status["mock_llm"] = {
                "status": "degraded",
                "message": f"Mock service error: {str(e)}",
                "last_checked": datetime.datetime.now().isoformat()
            }
    
    def _check_dependencies(self) -> Dict[str, str]:
        """Check dependencies and their versions"""
        dependencies = {}
        
        try:
            import pkg_resources
            
            # Get all installed packages
            for pkg in pkg_resources.working_set:
                if pkg.key in [
                    "fastapi", "uvicorn", "sqlalchemy", "redis", 
                    "openai", "anthropic", "google-generative-ai",
                    "pydantic", "python-jose", "passlib"
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
                self.service_status[service_name]["message"]
            )
        
        return "unknown", f"Service {service_name} not found"


# Initialize health service
health_service = HealthService()