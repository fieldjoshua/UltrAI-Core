"""
Cache decorators for the Ultra backend.

This module provides decorators for caching function results.
"""

import functools
import inspect
from typing import Any, Callable, Dict, Optional, TypeVar, cast

from backend.services.cache_service import cache_service
from backend.utils.logging import get_logger

# Set up logger
logger = get_logger("cache_decorator", "logs/cache.log")

# Type variables for better type hinting
T = TypeVar('T')
R = TypeVar('R')


def cached(prefix: str, ttl: Optional[int] = None) -> Callable[[Callable[..., R]], Callable[..., R]]:
    """
    Decorator for caching function results

    Args:
        prefix: Cache key prefix
        ttl: Time-to-live in seconds (optional)

    Returns:
        Decorated function that uses cache
    """
    def decorator(func: Callable[..., R]) -> Callable[..., R]:
        # Check if function is async
        is_async = inspect.iscoroutinefunction(func)

        if is_async:
            @functools.wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any) -> R:
                # Skip cache on debug parameter
                skip_cache = kwargs.pop('skip_cache', False)

                if not cache_service.is_enabled() or skip_cache:
                    return await func(*args, **kwargs)

                # Create a dictionary of function arguments
                cache_data = _create_cache_key_data(func, args, kwargs)

                # Try to get from cache
                cached_result = await cache_service.get(prefix, cache_data)

                if cached_result is not None:
                    logger.debug(f"Cache hit for {func.__name__}: {cache_data}")
                    return cast(R, cached_result.get("result"))

                # Execute function and store result
                result = await func(*args, **kwargs)

                # Store in cache
                await cache_service.set(
                    prefix,
                    cache_data,
                    {"result": result},
                    ttl=ttl
                )

                return result

            return async_wrapper
        else:
            @functools.wraps(func)
            def sync_wrapper(*args: Any, **kwargs: Any) -> R:
                # Skip cache on debug parameter
                skip_cache = kwargs.pop('skip_cache', False)

                if not cache_service.is_enabled() or skip_cache:
                    return func(*args, **kwargs)

                # Create a dictionary of function arguments
                cache_data = _create_cache_key_data(func, args, kwargs)

                # Try to get from cache (use synchronous version)
                try:
                    if cache_service.redis:
                        key = cache_service._generate_key(prefix, cache_data)
                        cached_data = cache_service.redis.get(key)

                        if cached_data:
                            import json
                            try:
                                cached_result = json.loads(cached_data)
                                logger.debug(f"Cache hit for {func.__name__}: {cache_data}")
                                return cast(R, cached_result.get("result"))
                            except json.JSONDecodeError:
                                logger.error(f"Error decoding cache data for key: {key}")
                except Exception as e:
                    logger.error(f"Error reading from cache: {str(e)}")

                # Execute function and store result
                result = func(*args, **kwargs)

                # Store in cache (use synchronous version)
                try:
                    if cache_service.redis:
                        key = cache_service._generate_key(prefix, cache_data)
                        import json
                        serialized_value = json.dumps({"result": result})
                        cache_ttl = ttl or cache_service.DEFAULT_CACHE_TTL
                        cache_service.redis.setex(key, cache_ttl, serialized_value)
                except Exception as e:
                    logger.error(f"Error writing to cache: {str(e)}")

                return result

            return sync_wrapper

    return decorator


def invalidate_cache(prefix: str) -> Callable[[Callable[..., R]], Callable[..., R]]:
    """
    Decorator for invalidating cache for a specific prefix after function execution

    Args:
        prefix: Cache key prefix to invalidate

    Returns:
        Decorated function that invalidates cache
    """
    def decorator(func: Callable[..., R]) -> Callable[..., R]:
        # Check if function is async
        is_async = inspect.iscoroutinefunction(func)

        if is_async:
            @functools.wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any) -> R:
                # Execute function first
                result = await func(*args, **kwargs)

                # Invalidate cache after execution
                if cache_service.is_enabled():
                    await cache_service.clear_by_pattern(f"{prefix}:*")

                return result

            return async_wrapper
        else:
            @functools.wraps(func)
            def sync_wrapper(*args: Any, **kwargs: Any) -> R:
                # Execute function first
                result = func(*args, **kwargs)

                # Invalidate cache after execution
                if cache_service.is_enabled() and cache_service.redis:
                    keys = cache_service.redis.keys(f"{cache_service.CACHE_PREFIX}{prefix}:*")
                    if keys:
                        cache_service.redis.delete(*keys)

                return result

            return sync_wrapper

    return decorator


def _create_cache_key_data(func: Callable, args: Any, kwargs: Any) -> Dict[str, Any]:
    """
    Create a dictionary for the cache key based on function arguments

    Args:
        func: Function being called
        args: Positional arguments
        kwargs: Keyword arguments

    Returns:
        Dictionary for cache key
    """
    # Get function signature to map args to parameter names
    sig = inspect.signature(func)
    params = list(sig.parameters.keys())

    # Create a dictionary of args by parameter name
    args_dict = {}

    # Add positional arguments by name
    for i, arg in enumerate(args):
        if i < len(params):
            # Skip 'self' and 'cls' parameters
            param_name = params[i]
            if param_name not in ('self', 'cls'):
                args_dict[param_name] = arg
        else:
            # Handle excess positional args (rare)
            args_dict[f"arg{i}"] = arg

    # Add keyword arguments
    for key, value in kwargs.items():
        args_dict[key] = value

    # Add function module and name for uniqueness
    return {
        "module": func.__module__,
        "function": func.__qualname__,
        "args": args_dict
    }