"""
Cache management routes.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Body
from typing import Dict, Any, Optional

from app.middleware.auth_dependencies import get_current_admin_user
from app.services.cache_service import get_cache_service
from app.utils.logging import get_logger

logger = get_logger("cache_routes")
router = APIRouter(prefix="/cache", tags=["Cache"])


@router.get("/stats", response_model=Dict[str, Any])
async def get_cache_stats(
    current_user: Any = Depends(get_current_admin_user)
) -> Dict[str, Any]:
    """Get cache statistics (admin only)."""
    try:
        cache_service = get_cache_service()
        stats = cache_service.get_stats()
        
        return {
            "status": "success",
            "stats": stats
        }
    except Exception as e:
        logger.error(f"Failed to get cache stats: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve cache statistics")


@router.post("/clear")
async def clear_cache(
    payload: Optional[Dict[str, str]] = Body(None),
    current_user: Any = Depends(get_current_admin_user)
) -> Dict[str, Any]:
    """Clear cache entries (admin only)."""
    try:
        cache_service = get_cache_service()
        pattern = payload.get("pattern") if payload else None
        
        if pattern:
            # Clear specific pattern
            count = await cache_service.clear_pattern(pattern)
            message = f"Cleared {count} cache entries matching pattern: {pattern}"
            cleared_count = count
        else:
            # Clear all cache
            await cache_service.flush()
            message = "Cleared all cache entries (Redis + memory)"
            cleared_count = -1  # Indicates a full flush

        logger.info(message)
        
        return {
            "status": "success",
            "message": message,
            "cleared": cleared_count,
            "pattern": pattern
        }
    except Exception as e:
        logger.error(f"Failed to clear cache: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to clear cache")


@router.get("/health", response_model=Dict[str, Any])
async def cache_health() -> Dict[str, Any]:
    """Check cache service health."""
    try:
        cache_service = get_cache_service()
        
        # Test Redis connectivity
        redis_healthy = await cache_service.is_redis_available()
        
        return {
            "healthy": True,
            "redis_available": redis_healthy,
            "memory_cache_size": len(cache_service.memory_cache),
        }
    except Exception as e:
        logger.error(f"Cache health check failed: {e}", exc_info=True)
        return {
            "healthy": False,
            "redis_available": False,
            "memory_cache_size": 0,
            "error": str(e)
        }