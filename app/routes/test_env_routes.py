"""
Test endpoint to check environment variables.
"""

import os
from fastapi import APIRouter
from typing import Dict, Any

router = APIRouter(prefix="/test", tags=["Test"])


@router.get("/env-check")
async def check_environment() -> Dict[str, Any]:
    """Check if API keys are loaded from environment."""
    
    api_keys = {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY"),
        "GOOGLE_API_KEY": os.getenv("GOOGLE_API_KEY"),
        "HUGGINGFACE_API_KEY": os.getenv("HUGGINGFACE_API_KEY"),
    }
    
    result = {}
    for key_name, key_value in api_keys.items():
        if key_value:
            # Mask the API key for security
            masked = f"{key_value[:4]}...{key_value[-4:]}" if len(key_value) > 8 else "***"
            result[key_name] = {
                "present": True,
                "masked_value": masked,
                "length": len(key_value)
            }
        else:
            result[key_name] = {
                "present": False,
                "masked_value": None,
                "length": 0
            }
    
    return {
        "environment": os.getenv("ENVIRONMENT", "unknown"),
        "api_keys": result,
        "total_keys_found": sum(1 for v in result.values() if v["present"])
    }