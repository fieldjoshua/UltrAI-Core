"""Redis configuration for production environment."""

import os
from typing import Dict, Optional
from urllib.parse import urlparse

from backend.utils.logging import get_logger

logger = get_logger("redis_config")


def parse_redis_url(url: str) -> Dict[str, any]:
    """Parse Redis URL into components."""
    parsed = urlparse(url)
    
    components = {
        "host": parsed.hostname or "localhost",
        "port": parsed.port or 6379,
        "db": 0,
        "password": parsed.password,
        "username": parsed.username,
    }
    
    # Extract database number from path
    if parsed.path and parsed.path != "/":
        try:
            components["db"] = int(parsed.path.lstrip("/"))
        except ValueError:
            pass
    
    # SSL support
    if parsed.scheme in ["rediss", "redis+ssl"]:
        components["ssl"] = True
        components["ssl_cert_reqs"] = "required"
    
    return components


def get_redis_config() -> Dict[str, any]:
    """Get Redis configuration from environment variables."""
    redis_url = os.environ.get("REDIS_URL", "")
    
    if not redis_url:
        logger.warning("REDIS_URL not configured, using default local Redis")
        return {
            "host": "localhost",
            "port": 6379,
            "db": 0,
            "decode_responses": True,
            "retry_on_timeout": True,
            "socket_keepalive": True,
            "socket_connect_timeout": 5,
            "socket_timeout": 5,
        }
    
    # Parse Redis URL
    components = parse_redis_url(redis_url)
    
    # Build configuration
    config = {
        "host": components["host"],
        "port": components["port"],
        "db": components["db"],
        "decode_responses": True,
        "retry_on_timeout": True,
        "socket_keepalive": True,
        "socket_connect_timeout": 5,
        "socket_timeout": 5,
        "max_connections": int(os.environ.get("REDIS_MAX_CONNECTIONS", "50")),
    }
    
    # Add password if present
    redis_password = os.environ.get("REDIS_PASSWORD", components.get("password"))
    if redis_password:
        config["password"] = redis_password
    
    # Add username if present (Redis 6.0+)
    if components.get("username"):
        config["username"] = components["username"]
    
    # SSL configuration
    if components.get("ssl"):
        config["ssl"] = True
        config["ssl_cert_reqs"] = components.get("ssl_cert_reqs", "required")
        
        # Additional SSL options from environment
        if os.environ.get("REDIS_SSL_CERT"):
            config["ssl_certfile"] = os.environ.get("REDIS_SSL_CERT")
        if os.environ.get("REDIS_SSL_KEY"):
            config["ssl_keyfile"] = os.environ.get("REDIS_SSL_KEY")
        if os.environ.get("REDIS_SSL_CA"):
            config["ssl_ca_certs"] = os.environ.get("REDIS_SSL_CA")
    
    return config


def get_cache_config() -> Dict[str, any]:
    """Get cache-specific configuration."""
    return {
        "ttl": int(os.environ.get("CACHE_TTL", "3600")),  # 1 hour default
        "max_entries": int(os.environ.get("CACHE_MAX_ENTRIES", "10000")),
        "key_prefix": os.environ.get("CACHE_KEY_PREFIX", "ultra:cache:"),
        "enable_compression": os.environ.get("CACHE_ENABLE_COMPRESSION", "true").lower() == "true",
    }


def get_rate_limit_config() -> Dict[str, any]:
    """Get rate limiting configuration."""
    return {
        "requests": int(os.environ.get("RATE_LIMIT_REQUESTS", "100")),
        "window": int(os.environ.get("RATE_LIMIT_WINDOW", "60")),  # seconds
        "key_prefix": os.environ.get("RATE_LIMIT_KEY_PREFIX", "ultra:ratelimit:"),
    }


def test_redis_connection(config: Dict[str, any]) -> bool:
    """Test Redis connection with given configuration."""
    import redis
    
    try:
        # Create Redis client
        client = redis.Redis(**config)
        
        # Test the connection
        client.ping()
        
        # Test basic operations
        test_key = "_test_connection"
        client.set(test_key, "test_value", ex=10)
        value = client.get(test_key)
        client.delete(test_key)
        
        logger.info("Redis connection test successful")
        return True
    except Exception as e:
        logger.error(f"Redis connection test failed: {str(e)}")
        return False