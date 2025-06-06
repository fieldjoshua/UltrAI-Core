"""
Security configuration settings for the application.
"""


def get_security_config() -> dict:
    """
    Get security configuration based on environment.

    Returns:
        dict: Security configuration settings
    """
    # Default security settings
    return {
        "csp_directives": {
            "default-src": ["'self'"],
            "script-src": ["'self'", "'unsafe-inline'"],
            "style-src": ["'self'", "'unsafe-inline'"],
            "img-src": ["'self'", "data:", "https:"],
            "connect-src": ["'self'"],
            "font-src": ["'self'"],
            "object-src": ["'none'"],
            "media-src": ["'self'"],
            "frame-src": ["'none'"],
        },
        "hsts_max_age": 31536000,  # 1 year
        "hsts_include_subdomains": True,
        "hsts_preload": True,
    }
