"""
Response optimization utilities for API performance.
"""

from typing import Any, Dict, List, Optional, Set
from datetime import datetime
import json

from app.utils.logging import get_logger

logger = get_logger("response_optimization")


def optimize_json_response(data: Any, fields_to_include: Optional[Set[str]] = None, 
                          fields_to_exclude: Optional[Set[str]] = None,
                          max_depth: int = 10) -> Any:
    """
    Optimize JSON response by removing unnecessary fields and reducing size.
    
    Args:
        data: The response data to optimize
        fields_to_include: If provided, only include these fields
        fields_to_exclude: Fields to exclude from response
        max_depth: Maximum depth for nested structures
        
    Returns:
        Optimized response data
    """
    if max_depth <= 0:
        return None
    
    if isinstance(data, dict):
        result = {}
        for key, value in data.items():
            # Skip excluded fields
            if fields_to_exclude and key in fields_to_exclude:
                continue
            
            # Only include specified fields if provided
            if fields_to_include and key not in fields_to_include:
                continue
            
            # Recursively optimize nested structures
            optimized_value = optimize_json_response(
                value, fields_to_include, fields_to_exclude, max_depth - 1
            )
            
            # Only include non-null values
            if optimized_value is not None:
                result[key] = optimized_value
        
        return result
    
    elif isinstance(data, list):
        # Optimize each item in the list
        return [
            optimize_json_response(item, fields_to_include, fields_to_exclude, max_depth - 1)
            for item in data
            if item is not None
        ]
    
    else:
        # Return primitive values as-is
        return data


def paginate_response(data: List[Any], page: int = 1, page_size: int = 20) -> Dict[str, Any]:
    """
    Paginate list responses for better performance.
    
    Args:
        data: List of items to paginate
        page: Current page number (1-indexed)
        page_size: Number of items per page
        
    Returns:
        Paginated response with metadata
    """
    total_items = len(data)
    total_pages = (total_items + page_size - 1) // page_size
    
    # Ensure page is within valid range
    page = max(1, min(page, total_pages or 1))
    
    # Calculate slice indices
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    
    # Get page items
    items = data[start_idx:end_idx]
    
    return {
        "items": items,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total_items": total_items,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1
        }
    }


def truncate_long_strings(data: Any, max_length: int = 1000) -> Any:
    """
    Truncate long strings in response to reduce size.
    
    Args:
        data: Response data
        max_length: Maximum string length
        
    Returns:
        Data with truncated strings
    """
    if isinstance(data, str):
        if len(data) > max_length:
            return data[:max_length] + "... [truncated]"
        return data
    
    elif isinstance(data, dict):
        return {
            key: truncate_long_strings(value, max_length)
            for key, value in data.items()
        }
    
    elif isinstance(data, list):
        return [truncate_long_strings(item, max_length) for item in data]
    
    else:
        return data


def create_summary_response(full_data: Dict[str, Any], 
                          summary_fields: List[str]) -> Dict[str, Any]:
    """
    Create a summary response with only essential fields.
    
    Args:
        full_data: Complete response data
        summary_fields: Fields to include in summary
        
    Returns:
        Summary response
    """
    summary = {}
    
    for field in summary_fields:
        # Handle nested field paths (e.g., "user.name")
        parts = field.split(".")
        value = full_data
        
        for part in parts:
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                value = None
                break
        
        if value is not None:
            # Set nested value in summary
            current = summary
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            current[parts[-1]] = value
    
    return summary


def add_etag(response_data: Any) -> str:
    """
    Generate ETag for response data to enable client-side caching.
    
    Args:
        response_data: Response data to hash
        
    Returns:
        ETag string
    """
    import hashlib
    
    # Convert to JSON string for consistent hashing
    json_str = json.dumps(response_data, sort_keys=True, default=str)
    
    # Generate hash
    etag = hashlib.md5(json_str.encode()).hexdigest()
    
    return f'"{etag}"'


class ResponseOptimizer:
    """Helper class for response optimization."""
    
    @staticmethod
    def optimize_pipeline_response(pipeline_result: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize pipeline response for API delivery."""
        
        # Fields to exclude from pipeline responses
        exclude_fields = {
            "raw_response",  # Internal raw LLM responses
            "debug_info",    # Debug information
            "internal_metadata",  # Internal metadata
        }
        
        # Optimize the response
        optimized = optimize_json_response(
            pipeline_result,
            fields_to_exclude=exclude_fields
        )
        
        # Truncate very long text fields
        optimized = truncate_long_strings(optimized, max_length=5000)
        
        return optimized
    
    @staticmethod
    def create_pipeline_summary(pipeline_result: Dict[str, Any]) -> Dict[str, Any]:
        """Create a summary of pipeline results."""
        
        summary_fields = [
            "ultra_synthesis.output",
            "metadata.models_used",
            "metadata.total_tokens",
            "metadata.processing_time",
            "metadata.estimated_cost",
            "error",
            "request_id"
        ]
        
        return create_summary_response(pipeline_result, summary_fields)