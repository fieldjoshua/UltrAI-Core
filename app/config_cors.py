"""
CORS configuration settings for the application.
"""

import os
from typing import List  # noqa: F401


def get_cors_config() -> dict:
    """
    Get CORS configuration based on environment.

    Returns:
        dict: CORS configuration settings
    """
    # Environment-specific origins
    allowed_origins = []
    # Production origins (lock down to known frontends)
    production_origins = [
        "https://ultr-ai-core.vercel.app",
        "https://ultrai-core.onrender.com",
        "https://ultrai-core-4lut.onrender.com",  # Render preview URL
        # Current production/demo UI hosts
        "https://ultrai-prod-ui.onrender.com",
        "https://ultrai-demo-ui.onrender.com",
    ]
    # Development origins
    development_origins = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173"
    ]
    # Determine environment and set appropriate origins
    environment = os.getenv("ENVIRONMENT", "development").lower()
    if environment == "production":
        allowed_origins = production_origins
    elif environment == "development":
        allowed_origins = development_origins + production_origins
    else:
        # Staging/test environments
        allowed_origins = development_origins + production_origins
    return {
        "allow_origins": allowed_origins,
        "allow_credentials": True,
        "allow_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": [
            "Content-Type",
            "Authorization",
            "X-Requested-With",
            "Accept",
            "Origin",
            "Cache-Control",
            "X-File-Name"
        ],
        "expose_headers": ["X-Total-Count", "X-Page-Count"],
        "max_age": 600,  # 10 minutes
    }


def is_allowed_origin(origin: str) -> bool:
    """
    Check if an origin should be allowed for CORS.

    Args:
        origin: The origin to check

    Returns:
        bool: True if the origin should be allowed
    """
    if not origin:
        return False

    # Get configured origins
    cors_config = get_cors_config()
    allowed_origins = cors_config.get("allow_origins", [])

    # Check exact match
    if origin in allowed_origins:
        return True

    # Check if it's a Render subdomain
    if ".onrender.com" in origin and origin.startswith("https://"):
        return True

    return False
