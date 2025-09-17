"""
Response sanitizer to remove sensitive fields like cost/pricing.

This module provides utilities to ensure no cost, price, or billing
fields leak into API responses.
"""

from typing import Any, Dict, List, Union
import logging

logger = logging.getLogger(__name__)

# Fields to remove from responses
SENSITIVE_FIELDS = {
    "cost", "costs", "total_cost", "cost_per_token",
    "price", "prices", "pricing", "total_price", 
    "fee", "fees", "charge", "charges",
    "billing", "payment", "invoice", "credit",
    "balance", "amount_due", "transaction_amount"
}


def sanitize_response(data: Any) -> Any:
    """
    Recursively remove sensitive fields from response data.
    
    Args:
        data: Response data to sanitize
        
    Returns:
        Sanitized data with sensitive fields removed
    """
    if isinstance(data, dict):
        # Create new dict without sensitive fields
        sanitized = {}
        removed_fields = []
        
        for key, value in data.items():
            if key.lower() in SENSITIVE_FIELDS:
                removed_fields.append(key)
            else:
                # Recursively sanitize nested data
                sanitized[key] = sanitize_response(value)
        
        if removed_fields:
            logger.debug(f"Removed sensitive fields: {removed_fields}")
            
        return sanitized
        
    elif isinstance(data, list):
        # Recursively sanitize list items
        return [sanitize_response(item) for item in data]
        
    else:
        # Return primitive values as-is
        return data


def sanitize_error_response(error_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize error responses to ensure no cost information leaks.
    
    Args:
        error_dict: Error response dictionary
        
    Returns:
        Sanitized error response
    """
    # Remove any cost-related fields
    sanitized = sanitize_response(error_dict)
    
    # Ensure standard error structure
    if "error" in sanitized and isinstance(sanitized["error"], str):
        # Check error message for cost-related terms
        error_msg = sanitized["error"]
        cost_terms = ["cost", "price", "billing", "payment", "balance", "credit"]
        
        for term in cost_terms:
            if term in error_msg.lower():
                # Replace with generic message
                sanitized["error"] = "Service temporarily unavailable"
                logger.warning(f"Sanitized error message containing '{term}'")
                break
                
    return sanitized


def create_safe_response(
    success: bool,
    data: Any = None,
    error: str = None,
    metadata: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Create a safe response ensuring no sensitive data leaks.
    
    Args:
        success: Whether the operation was successful
        data: Response data (will be sanitized)
        error: Error message if any
        metadata: Additional metadata (will be sanitized)
        
    Returns:
        Safe response dictionary
    """
    response = {"success": success}
    
    if data is not None:
        response["data"] = sanitize_response(data)
        
    if error is not None:
        response["error"] = error
        
    if metadata is not None:
        # Sanitize metadata but keep essential fields
        safe_metadata = sanitize_response(metadata)
        if safe_metadata:
            response["metadata"] = safe_metadata
            
    return response