"""
Health check endpoints for the Ultra backend.

This module provides comprehensive endpoints for checking the health of the API
and its dependencies, including database, cache, LLM providers, and more.
"""

import os
import socket
import platform
import time
import psutil
from typing import Dict, Any, Optional, List, Union
from enum import Enum

from fastapi import APIRouter, Depends, Request, Response, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from backend.utils.dependency_manager import dependency_registry
from backend.utils.logging import get_logger
from backend.database.connection import check_database_connection, get_database_status, is_using_fallback
from backend.services.cache_service import cache_service
from backend.utils.jwt_wrapper import is_using_pyjwt, get_jwt_status
from backend.utils.metrics import start_time, get_current_metrics
from backend.utils.health_check import (
    health_check_registry, HealthCheck, HealthStatus, ServiceType,
    check_database_health, check_redis_health, check_jwt_health, 
    check_llm_provider_health, check_system_health, check_network_health,
    check_storage_health
)

# Create router
health_router = APIRouter(tags=["Health"])

# Set up logger
logger = get_logger("health", "logs/health.log")

# API and instance information
API_VERSION = os.getenv("API_VERSION", "0.1.0")
API_ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
INSTANCE_ID = socket.gethostname()


class DependencyStatus(BaseModel):
    """Status of a dependency"""
    name: str = Field(..., description="Dependency name")
    is_available: bool = Field(..., description="Whether dependency is available")
    is_required: bool = Field(..., description="Whether dependency is required")
    module_name: str = Field(..., description="Python module name")
    error: Optional[str] = Field(None, description="Error message if dependency is not available")
    installation_cmd: Optional[str] = Field(None, description="Command to install the dependency")


class FeatureStatus(BaseModel):
    """Status of a feature"""
    name: str = Field(..., description="Feature name")
    enabled: bool = Field(..., description="Whether feature is enabled")
    dependencies: Optional[List[str]] = Field(None, description="Dependencies required for this feature")


class ServiceStatus(BaseModel):
    """Status of a specific service"""
    service: str = Field(..., description="Service name")
    status: str = Field(..., description="Service status (ok, degraded, unavailable)")
    details: Optional[Dict[str, Any]] = Field(None, description="Service-specific details")
    using_fallback: Optional[bool] = Field(None, description="Whether service is using fallback")


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Overall system status")
    api_version: str = Field(..., description="API version")
    environment: str = Field(..., description="Deployment environment")
    instance_id: str = Field(..., description="Instance ID")
    uptime: int = Field(..., description="Uptime in seconds")
    dependencies: Optional[Dict[str, Dict[str, Any]]] = Field(None, description="Dependency statuses")
    features: Optional[Dict[str, bool]] = Field(None, description="Feature flags")
    services: Optional[Dict[str, Dict[str, Any]]] = Field(None, description="Service statuses")


# Register health checks
def register_health_checks():
    """Register all health checks with the registry"""
    # Database health check
    health_check_registry.register(HealthCheck(
        name="database",
        service_type=ServiceType.DATABASE,
        check_fn=check_database_health,
        description="PostgreSQL database connection",
        is_critical=True,
    ))
    
    # Redis health check
    health_check_registry.register(HealthCheck(
        name="redis",
        service_type=ServiceType.CACHE,
        check_fn=check_redis_health,
        description="Redis cache connection",
        is_critical=False,
    ))
    
    # JWT health check
    health_check_registry.register(HealthCheck(
        name="jwt",
        service_type=ServiceType.AUTH,
        check_fn=check_jwt_health,
        description="JWT authentication",
        is_critical=False,
    ))
    
    # LLM provider health checks
    health_check_registry.register(HealthCheck(
        name="openai",
        service_type=ServiceType.LLM_PROVIDER,
        check_fn=lambda: check_llm_provider_health("openai", "OPENAI_API_KEY"),
        description="OpenAI API",
        is_critical=False,
    ))
    
    health_check_registry.register(HealthCheck(
        name="anthropic",
        service_type=ServiceType.LLM_PROVIDER,
        check_fn=lambda: check_llm_provider_health("anthropic", "ANTHROPIC_API_KEY"),
        description="Anthropic API",
        is_critical=False,
    ))
    
    health_check_registry.register(HealthCheck(
        name="google",
        service_type=ServiceType.LLM_PROVIDER,
        check_fn=lambda: check_llm_provider_health("google", "GOOGLE_API_KEY"),
        description="Google AI API",
        is_critical=False,
    ))
    
    # System health check
    health_check_registry.register(HealthCheck(
        name="system",
        service_type=ServiceType.SYSTEM,
        check_fn=check_system_health,
        description="System resources",
        is_critical=False,
        check_interval=30,  # Check more frequently
    ))
    
    # Network health check
    health_check_registry.register(HealthCheck(
        name="network",
        service_type=ServiceType.NETWORK,
        check_fn=lambda: check_network_health("api.openai.com", 443),
        description="Network connectivity",
        is_critical=False,
    ))
    
    # Storage health check
    health_check_registry.register(HealthCheck(
        name="storage",
        service_type=ServiceType.STORAGE,
        check_fn=lambda: check_storage_health("document_storage"),
        description="Document storage",
        is_critical=True,
    ))

# Register health checks
register_health_checks()


@health_router.get("/health")
async def basic_health_check():
    """
    Simple health check endpoint for load balancers and basic monitoring.
    Returns a minimal response with overall status and uptime.
    """
    overall_status, _ = health_check_registry.get_overall_status()
    return {
        "status": overall_status,
        "uptime": int(time.time() - start_time)
    }


@health_router.get("/api/health")
async def api_health_check(
    detail: bool = Query(False, description="Include detailed service status"),
    service: Optional[str] = Query(None, description="Check specific service"),
    type: Optional[str] = Query(None, description="Filter by service type"),
    include_system: bool = Query(False, description="Include system metrics")
):
    """
    API health check endpoint with configurable level of detail.
    
    Args:
        detail: Whether to include detailed service information
        service: Optional specific service to check
        type: Optional service type to filter by
        include_system: Whether to include system metrics
        
    Returns:
        Health check response
    """
    # Calculate uptime
    uptime = int(time.time() - start_time)
    
    # Basic health check response
    response = {
        "status": "ok",
        "api_version": API_VERSION,
        "environment": API_ENVIRONMENT,
        "instance_id": INSTANCE_ID,
        "uptime": uptime,
    }
    
    # If requesting specific service
    if service:
        health_check = health_check_registry.get(service)
        if health_check:
            service_status = health_check.check()
            return {
                "service": service,
                "status": service_status.get("status", "unknown"),
                "details": service_status,
            }
        else:
            return JSONResponse(
                status_code=404, 
                content={"error": f"Service '{service}' not found"}
            )
    
    # Filter by service type if specified
    if type:
        try:
            service_type = ServiceType(type)
            services = health_check_registry.get_by_type(service_type)
            service_statuses = {
                name: check.check() for name, check in services.items()
            }
            
            response.update({
                "service_type": type,
                "services": service_statuses,
            })
            
            # Update overall status based on services of this type
            if any(status.get("status") == HealthStatus.CRITICAL for status in service_statuses.values()):
                response["status"] = HealthStatus.CRITICAL
            elif any(status.get("status") == HealthStatus.DEGRADED for status in service_statuses.values()):
                response["status"] = HealthStatus.DEGRADED
                
            return response
        except ValueError:
            return JSONResponse(
                status_code=400, 
                content={"error": f"Invalid service type: {type}"}
            )
    
    # For detailed response, include service checks
    if detail:
        # Get all service statuses
        service_statuses = health_check_registry.check_all()
        
        # Get dependencies and features
        all_dependencies = dependency_registry.get_all_statuses()
        all_features = dependency_registry.get_feature_flags()
        
        # Update response with detailed info
        response.update({
            "dependencies": all_dependencies,
            "features": all_features,
            "services": service_statuses,
        })
        
        # Update overall status
        overall_status, failing_services = health_check_registry.get_overall_status()
        response["status"] = overall_status
        
        if failing_services:
            response["failing_services"] = failing_services
    
    # Include system metrics if requested
    if include_system:
        # Get system information
        memory_info = psutil.virtual_memory()
        disk_info = psutil.disk_usage('/')
        
        # Get application metrics
        metrics = get_current_metrics()
        
        response["system"] = {
            "memory": {
                "total_gb": round(memory_info.total / (1024**3), 2),
                "available_gb": round(memory_info.available / (1024**3), 2),
                "percent_used": memory_info.percent,
                "application_mb": round(metrics.get("memory_usage_mb", 0), 2),
            },
            "disk": {
                "total_gb": round(disk_info.total / (1024**3), 2),
                "free_gb": round(disk_info.free / (1024**3), 2),
                "percent_used": disk_info.percent,
            },
            "requests": {
                "processed": metrics.get("requests_processed", 0),
                "avg_time": metrics.get("avg_processing_time", 0),
            },
        }
    
    return response


@health_router.get("/api/health/system")
async def get_system_health():
    """
    Detailed system health information including memory, disk, and CPU usage.
    """
    system_check = health_check_registry.get("system")
    if system_check:
        return system_check.check(force=True)
    else:
        # Fallback to direct check if not registered
        return check_system_health()


@health_router.get("/api/health/dependencies")
async def get_dependencies_status() -> Dict[str, Any]:
    """
    Get detailed dependencies status for the API.
    """
    # Get dependencies and features
    all_dependencies = dependency_registry.get_all_statuses()
    all_features = dependency_registry.get_feature_flags()
    
    # Build response
    response = {
        "dependencies": all_dependencies,
        "features": all_features,
    }
    
    # Get required dependencies status
    required_ok, missing_required = dependency_registry.get_required_status()
    response["all_required_available"] = required_ok
    
    if not required_ok:
        response["missing_required"] = missing_required
    
    return response


@health_router.get("/api/health/services")
async def get_services_status(
    service_type: Optional[str] = Query(None, description="Filter by service type"),
    force_check: bool = Query(False, description="Force fresh health checks")
) -> Dict[str, Any]:
    """
    Get detailed service status information.
    
    Args:
        service_type: Optional service type to filter by
        force_check: Whether to force fresh health checks
        
    Returns:
        Service status information
    """
    # Filter by service type if specified
    if service_type:
        try:
            service_type_enum = ServiceType(service_type)
            services = health_check_registry.get_by_type(service_type_enum)
            service_statuses = {
                name: check.check(force=force_check) for name, check in services.items()
            }
            
            return {
                "service_type": service_type,
                "services": service_statuses,
            }
        except ValueError:
            return JSONResponse(
                status_code=400, 
                content={"error": f"Invalid service type: {service_type}"}
            )
    else:
        # Get all service statuses
        service_statuses = health_check_registry.check_all()
        return {
            "services": service_statuses,
        }


@health_router.get("/api/health/llm")
async def get_llm_health(
    provider: Optional[str] = Query(None, description="Specific LLM provider to check"),
    force_check: bool = Query(False, description="Force fresh health checks")
) -> Dict[str, Any]:
    """
    Get health status of LLM providers.
    
    Args:
        provider: Optional specific provider to check
        force_check: Whether to force fresh health checks
        
    Returns:
        LLM provider health status
    """
    # Filter LLM providers
    llm_providers = health_check_registry.get_by_type(ServiceType.LLM_PROVIDER)
    
    # Check specific provider if requested
    if provider:
        if provider in llm_providers:
            provider_status = llm_providers[provider].check(force=force_check)
            return {
                "provider": provider,
                "status": provider_status.get("status", "unknown"),
                "details": provider_status,
            }
        else:
            return JSONResponse(
                status_code=404, 
                content={"error": f"LLM provider '{provider}' not found"}
            )
    
    # Check all providers
    provider_statuses = {
        name: check.check(force=force_check) for name, check in llm_providers.items()
    }
    
    # Determine overall status
    overall_status = HealthStatus.OK
    if any(status.get("status") == HealthStatus.CRITICAL for status in provider_statuses.values()):
        overall_status = HealthStatus.CRITICAL
    elif any(status.get("status") == HealthStatus.UNAVAILABLE for status in provider_statuses.values()):
        overall_status = HealthStatus.DEGRADED
    
    return {
        "status": overall_status,
        "providers": provider_statuses,
    }


@health_router.get("/ping")
async def ping() -> Dict[str, str]:
    """
    Simple ping endpoint for load balancers and monitoring.
    
    Returns:
        Response with "pong" message
    """
    return {"message": "pong"}


@health_router.get("/info")
async def api_info() -> Dict[str, Any]:
    """
    Get API and environment information.
    
    Returns:
        API information
    """
    return {
        "api_version": API_VERSION,
        "environment": API_ENVIRONMENT,
        "platform": platform.platform(),
        "python_version": platform.python_version(),
        "hostname": socket.gethostname(),
    }