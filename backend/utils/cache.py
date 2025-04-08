import hashlib
from cachetools import TTLCache
from typing import List


# Add response caching
response_cache = TTLCache(maxsize=100, ttl=3600)  # Cache for 1 hour


def generate_cache_key(prompt: str, models: List[str], ultra_model: str, pattern: str) -> str:
    """Generate a unique cache key based on request parameters"""
    key_data = f"{prompt}|{','.join(sorted(models))}|{ultra_model}|{pattern}"
    # Set usedforsecurity=False as this is for caching, not security purposes
    return hashlib.md5(key_data.encode(), usedforsecurity=False).hexdigest()


class MemoryCacheObject:
    """Simple memory cache size reporter"""
    def size(self) -> int:
        return 0


class CacheObject:
    """Cache object wrapper with memory cache attribute"""
    def __init__(self):
        self.memory_cache = MemoryCacheObject()