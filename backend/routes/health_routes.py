"""
Health check endpoints for the Ultra backend.

This module provides endpoints for checking the health of the application and its services.
"""

from fastapi import APIRouter, Query, HTTPException, Depends, status
from typing import Dict, Any, Optional

from backend.config import Config
from backend.services.health_service import health_service
from backend.utils.logging import get_logger

# Configure router - use prefix for direct inclusion in app
router = APIRouter(tags=["health"])

# Configure logging
logger = get_logger("health_routes")

@router.get("/health", summary="Get application health status", response_model=Dict[str, Any])
async def get_health(detail: bool = Query(False, description="Include detailed health information")):
    """
    Get the health status of the application.
    
    - **detail**: Set to true to include detailed information about services and system.
    
    Returns a health status object with overall status and service information.
    """
    try:
        # Log the health check
        logger.info(f"Health check requested with detail={detail}")
        
        # Get health status
        health_status = health_service.get_health_status(detailed=detail)
        
        # Return health status
        return health_status
    except Exception as e:
        logger.error(f"Error retrieving health status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving health status: {str(e)}"
        )

@router.get("/health/{service_name}", summary="Check specific service health", response_model=Dict[str, Any])
async def check_service_health(service_name: str):
    """
    Check the health of a specific service.
    
    - **service_name**: Name of the service to check
    
    Returns the health status of the specified service.
    """
    try:
        # Log the service health check
        logger.info(f"Service health check requested for {service_name}")
        
        # Check service status
        status, message = health_service.check_service_status(service_name)
        
        # Return service status
        return {
            "service": service_name,
            "status": status,
            "message": message,
            "environment": Config.ENVIRONMENT
        }
    except Exception as e:
        logger.error(f"Error checking service {service_name} health: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error checking service health: {str(e)}"
        )