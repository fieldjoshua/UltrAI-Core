#!/usr/bin/env python3
"""Setup and verify production Redis configuration."""

import os
import sys
from pathlib import Path

# Add backend to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.config_redis import (
    get_cache_config,
    get_rate_limit_config,
    get_redis_config,
    test_redis_connection,
)
from backend.utils.logging import get_logger

logger = get_logger("redis_setup")


def setup_production_redis():
    """Setup and verify production Redis."""
    print("Production Redis Setup")
    print("=" * 40)
    
    # Check if REDIS_URL is set
    redis_url = os.environ.get("REDIS_URL")
    if not redis_url:
        print("WARNING: REDIS_URL environment variable not set!")
        print("Using default local Redis configuration")
        print("Please set REDIS_URL for production deployment")
        print("Example: redis://user:password@host:port/0")
    else:
        print(f"Redis URL configured: {redis_url.split('@')[0]}@...")  # Hide credentials
    
    # Get Redis configuration
    redis_config = get_redis_config()
    cache_config = get_cache_config()
    rate_limit_config = get_rate_limit_config()
    
    # Test connection
    print("\nTesting Redis connection...")
    if test_redis_connection(redis_config):
        print("✓ Redis connection successful")
    else:
        print("✗ Redis connection failed")
        return False
    
    print("\nRedis configuration summary:")
    print(f"- Host: {redis_config['host']}")
    print(f"- Port: {redis_config['port']}")
    print(f"- Database: {redis_config['db']}")
    print(f"- Max connections: {redis_config.get('max_connections', 'default')}")
    print(f"- SSL enabled: {redis_config.get('ssl', False)}")
    
    print("\nCache configuration:")
    print(f"- TTL: {cache_config['ttl']}s")
    print(f"- Max entries: {cache_config['max_entries']}")
    print(f"- Key prefix: {cache_config['key_prefix']}")
    print(f"- Compression: {cache_config['enable_compression']}")
    
    print("\nRate limiting configuration:")
    print(f"- Requests: {rate_limit_config['requests']}")
    print(f"- Window: {rate_limit_config['window']}s")
    print(f"- Key prefix: {rate_limit_config['key_prefix']}")
    
    # Test cache operations
    try:
        import redis
        client = redis.Redis(**redis_config)
        
        # Test cache
        print("\nTesting cache operations...")
        cache_key = f"{cache_config['key_prefix']}test"
        client.setex(cache_key, cache_config['ttl'], "test_value")
        value = client.get(cache_key)
        client.delete(cache_key)
        print("✓ Cache operations successful")
        
        # Test rate limiting
        print("\nTesting rate limit operations...")
        rate_key = f"{rate_limit_config['key_prefix']}test:user"
        client.incr(rate_key)
        client.expire(rate_key, rate_limit_config['window'])
        count = client.get(rate_key)
        client.delete(rate_key)
        print("✓ Rate limit operations successful")
        
    except Exception as e:
        print(f"✗ Redis operations test failed: {str(e)}")
        return False
    
    print("\nRedis setup complete!")
    return True


if __name__ == "__main__":
    # Load environment variables from .env.production if it exists
    env_path = Path(".env.production")
    if env_path.exists():
        from dotenv import load_dotenv
        load_dotenv(env_path)
        print(f"Loaded environment from {env_path}")
    
    success = setup_production_redis()
    sys.exit(0 if success else 1)