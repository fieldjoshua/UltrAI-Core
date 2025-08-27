"""
Cache management routes.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, Any

from app.middleware.auth_dependencies import get_current_admin_user
from app.services.cache_service import get_cache_service
from app.utils.logging import get_logger

logger = get_logger("cache_routes")
router = APIRouter(prefix="/cache", tags=["Cache"])


@router.get("/stats", response_model=Dict[str, Any])
async def get_cache_stats(
    current_user=Depends(get_current_admin_user)
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
        logger.error(f"Failed to get cache stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve cache statistics")


@router.delete("/clear")
async def clear_cache(
    pattern: str = Query(None, description="Optional pattern to match keys (e.g., 'pipeline:*')"),
    current_user=Depends(get_current_admin_user)
) -> Dict[str, Any]:
    """Clear cache entries (admin only)."""
    try:
        cache_service = get_cache_service()
        
        if pattern:
            # Clear specific pattern
            count = await cache_service.clear_pattern(pattern)
            message = f"Cleared {count} cache entries matching pattern: {pattern}"
        else:
            # Clear all cache
            # For Redis: use FLUSHDB
            count = 0
            if cache_service.redis_client:
                await cache_service.redis_client.flushdb()
                count += 1
            
            # Clear memory cache
            memory_count = len(cache_service.memory_cache)
            cache_service.memory_cache.clear()
            count += memory_count
            
            message = f"Cleared all cache entries (Redis + {memory_count} memory entries)"
        
        logger.info(message)
        
        return {
            "status": "success",
            "message": message,
            "cleared_count": count
        }
    except Exception as e:
        logger.error(f"Failed to clear cache: {e}")
        raise HTTPException(status_code=500, detail="Failed to clear cache")


@router.get("/health")
async def cache_health() -> Dict[str, Any]:
    """Check cache service health."""
    try:
        cache_service = get_cache_service()
        
        # Test Redis connectivity
        redis_healthy = False
        if cache_service.redis_client:
            try:
                await cache_service.redis_client.ping()
                redis_healthy = True
            except Exception:
                pass
        
        return {
            "status": "healthy",
            "redis": {
                "connected": redis_healthy,
                "url_configured": bool(cache_service.redis_client)
            },
            "memory_cache": {
                "size": len(cache_service.memory_cache),
                "enabled": True
            }
        }
    except Exception as e:
        logger.error(f"Cache health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }