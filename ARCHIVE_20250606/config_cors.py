"""CORS configuration for production environment."""

import os
from typing import List


def get_allowed_origins() -> List[str]:
    """Get allowed CORS origins from environment."""
    env_origins = os.environ.get("CORS_ORIGINS", "")
    
    if env_origins:
        # Parse comma-separated origins from environment
        origins = [origin.strip() for origin in env_origins.split(",") if origin.strip()]
    else:
        # Default production origins
        origins = [
            "https://ultrai.app",
            "https://www.ultrai.app",
            "https://api.ultrai.app",
        ]
    
    # Add additional origins for specific environments
    if os.environ.get("ENVIRONMENT") == "development":
        origins.extend([
            "http://localhost:3000",
            "http://localhost:3009",
            "http://localhost:3001",
            "http://localhost:5173",
        ])
    
    # Add frontend container for Docker deployments
    if os.environ.get("DOCKER_DEPLOYMENT") == "true":
        origins.append("http://frontend:3009")
    
    return origins


def get_cors_config():
    """Get CORS configuration for production."""
    return {
        "allow_origins": get_allowed_origins(),
        "allow_credentials": True,
        "allow_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        "allow_headers": [
            "Content-Type",
            "Authorization",
            "X-API-Key",
            "X-CSRF-Token",
            "X-Request-ID",
            "Accept",
            "Accept-Language",
            "Cache-Control",
            "Pragma",
        ],
        "expose_headers": [
            "X-Request-ID",
            "X-Rate-Limit-Limit",
            "X-Rate-Limit-Remaining",
            "X-Rate-Limit-Reset",
        ],
        "max_age": 3600,  # 1 hour
    }


def validate_origin(origin: str, allowed_origins: List[str]) -> bool:
    """Validate if an origin is allowed."""
    # Direct match
    if origin in allowed_origins:
        return True
    
    # Check for subdomain wildcards
    for allowed in allowed_origins:
        if allowed.startswith("*."):
            domain = allowed[2:]
            if origin.endswith(domain):
                return True
    
    return False