"""
CORS configuration settings for the application.
"""


def get_cors_config() -> dict:
    """
    Get CORS configuration based on environment.

    Returns:
        dict: CORS configuration settings
    """
    # Default CORS settings
    return {
        "allow_origins": ["*"],  # In production, replace with specific origins
        "allow_credentials": True,
        "allow_methods": ["*"],
        "allow_headers": ["*"],
        "expose_headers": ["*"],
        "max_age": 600,  # 10 minutes
    }
