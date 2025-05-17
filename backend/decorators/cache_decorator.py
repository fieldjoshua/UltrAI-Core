"""
Cache decorators for the Ultra backend.

This module provides decorators for caching function results.
"""

import functools
import hashlib
import inspect
import json
from typing import Any, Callable, Dict, Optional, TypeVar, cast

from backend.services.cache_service import cache_service
from backend.utils.logging import get_logger

# Set up logger
logger = get_logger("cache_decorator", "logs/cache.log")

# Type variables for better type hinting
T = TypeVar("T")
R = TypeVar("R")


def cached(
    prefix: str, ttl: Optional[int] = None
) -> Callable[[Callable[..., R]], Callable[..., R]]:
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
                skip_cache = kwargs.pop("skip_cache", False)

                if not cache_service.cache_enabled or skip_cache:
                    return await func(*args, **kwargs)

                # Create a dictionary of function arguments
                cache_data = _create_cache_key_data(func, args, kwargs)

                # Generate cache key
                cache_key = _generate_key(prefix, cache_data)
                
                # Try to get from cache (synchronous)
                cached_result = cache_service.implementation.get_dict(cache_key)
                if cached_result is not None:
                    logger.debug(f"Cache hit for {func.__name__}: {cache_data}")
                    return cast(R, cached_result.get("result"))

                # Execute function
                result = await func(*args, **kwargs)

                # Store in cache (synchronous)
                cache_service.implementation.set_dict(cache_key, {"result": result, **cache_data}, ttl)
                logger.debug(f"Cached result for {func.__name__}: {cache_data}")

                return result

            return async_wrapper
        else:

            @functools.wraps(func)
            def sync_wrapper(*args: Any, **kwargs: Any) -> R:
                # Skip cache on debug parameter
                skip_cache = kwargs.pop("skip_cache", False)

                if not cache_service.cache_enabled or skip_cache:
                    return func(*args, **kwargs)

                # Create a dictionary of function arguments
                cache_data = _create_cache_key_data(func, args, kwargs)

                # Generate cache key
                cache_key = _generate_key(prefix, cache_data)
                
                # Try to get from cache (synchronous)
                cached_result = cache_service.implementation.get_dict(cache_key)
                if cached_result is not None:
                    logger.debug(f"Cache hit for {func.__name__}: {cache_data}")
                    return cast(R, cached_result.get("result"))

                # Execute function
                result = func(*args, **kwargs)

                # Store in cache (synchronous)
                cache_service.implementation.set_dict(cache_key, {"result": result, **cache_data}, ttl)
                logger.debug(f"Cached result for {func.__name__}: {cache_data}")

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

                # Invalidate cache after execution (synchronous)
                if cache_service.cache_enabled:
                    pattern = f"{prefix}:*"
                    keys = cache_service.keys(pattern)
                    for key in keys:
                        cache_service.delete(key)

                return result

            return async_wrapper
        else:

            @functools.wraps(func)
            def sync_wrapper(*args: Any, **kwargs: Any) -> R:
                # Execute function first
                result = func(*args, **kwargs)

                # Invalidate cache after execution (synchronous)
                if cache_service.cache_enabled:
                    pattern = f"{prefix}:*"
                    keys = cache_service.keys(pattern)
                    for key in keys:
                        cache_service.delete(key)

                return result

            return sync_wrapper

    return decorator


def _generate_key(prefix: str, data: Dict[str, Any]) -> str:
    """
    Generate a cache key from prefix and data
    
    Args:
        prefix: Cache key prefix
        data: Dictionary of data to include in key
        
    Returns:
        Generated cache key
    """
    # Convert Pydantic models to dictionaries
    serializable_data = _make_serializable(data)
    
    # Create a consistent string representation of the data
    data_str = json.dumps(serializable_data, sort_keys=True)
    
    # Hash the data to create a key
    hash_value = hashlib.md5(data_str.encode()).hexdigest()[:16]
    
    return f"{prefix}:{hash_value}"


def _make_serializable(data: Any) -> Any:
    """
    Make data JSON serializable by converting Pydantic models and other non-serializable types
    
    Args:
        data: Data to make serializable
        
    Returns:
        Serializable version of the data
    """
    from datetime import datetime, date
    
    # Handle None
    if data is None:
        return None
    
    # Handle Pydantic models
    if hasattr(data, "dict"):  # Pydantic models have a dict() method
        return data.dict()
    
    # Handle datetime objects
    if isinstance(data, (datetime, date)):
        return data.isoformat()
    
    # Handle dictionaries
    if isinstance(data, dict):
        return {str(k): _make_serializable(v) for k, v in data.items()}
    
    # Handle lists and tuples
    if isinstance(data, (list, tuple)):
        return [_make_serializable(item) for item in data]
    
    # Handle sets
    if isinstance(data, set):
        return list(data)
    
    # Handle SQLAlchemy objects or other ORM objects
    if hasattr(data, "__dict__") and hasattr(data, "__class__"):
        # Only serialize simple attributes, skip complex ones
        return str(data)
    
    # Handle basic types
    if isinstance(data, (str, int, float, bool)):
        return data
    
    # For everything else, convert to string
    return str(data)


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
            if param_name not in ("self", "cls"):
                args_dict[param_name] = arg
        else:
            # Handle excess positional args (rare)
            args_dict[f"arg{i}"] = arg

    # Add keyword arguments
    for key, value in kwargs.items():
        args_dict[key] = value

    # Add function module and name for uniqueness
    return {"module": func.__module__, "function": func.__qualname__, "args": args_dict}
