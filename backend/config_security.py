"""Security configuration for production environment."""

import os
from typing import Dict, Optional


def get_csp_directives() -> Dict[str, str]:
    """Get Content Security Policy directives from environment or defaults."""
    env_csp = os.environ.get("CSP_POLICY", "")
    
    if env_csp:
        # Parse the environment CSP string into directives
        directives = {}
        parts = env_csp.split(";")
        for part in parts:
            part = part.strip()
            if " " in part:
                key, value = part.split(" ", 1)
                directives[key] = value
        return directives
    
    # Default production CSP
    return {
        "default-src": "'self'",
        "script-src": "'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net",
        "style-src": "'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.jsdelivr.net https://unpkg.com",
        "img-src": "'self' data: https:",
        "font-src": "'self' https://fonts.gstatic.com",
        "connect-src": "'self' https://api.ultrai.app wss://api.ultrai.app",
        "frame-src": "'none'",
        "object-src": "'none'",
        "base-uri": "'self'",
        "form-action": "'self'",
        "frame-ancestors": "'none'",
        "upgrade-insecure-requests": "",
    }


def get_security_config() -> Dict[str, any]:
    """Get security configuration from environment variables."""
    return {
        "csp_directives": get_csp_directives(),
        "hsts_max_age": int(os.environ.get("HSTS_MAX_AGE", "31536000")),
        "hsts_include_subdomains": os.environ.get("HSTS_INCLUDE_SUBDOMAINS", "true").lower() == "true",
        "hsts_preload": os.environ.get("HSTS_PRELOAD", "false").lower() == "true",
        "frame_options": os.environ.get("X_FRAME_OPTIONS", "DENY"),
        "content_type_options": os.environ.get("X_CONTENT_TYPE_OPTIONS", "nosniff"),
        "xss_protection": os.environ.get("X_XSS_PROTECTION", "1; mode=block"),
        "referrer_policy": os.environ.get("REFERRER_POLICY", "strict-origin-when-cross-origin"),
        "permissions_policy": os.environ.get("PERMISSIONS_POLICY", None),
    }