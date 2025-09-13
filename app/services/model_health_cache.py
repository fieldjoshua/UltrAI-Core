"""
Centralized model health caching service.

This module provides a centralized cache for model health checks to avoid
repeated probing of LLM endpoints across different services.
"""

import time
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta

from app.services.llm_adapters import CLIENT
from app.utils.logging import get_logger

logger = get_logger("model_health_cache")


class ModelHealthCache:
    """Centralized cache for model health status."""
    
    _instance: Optional['ModelHealthCache'] = None
    _health_cache: Dict[str, Dict[str, Any]] = {}
    _CACHE_TTL_SECONDS = 300  # 5 minutes
    
    def __new__(cls):
        """Ensure singleton pattern for the health cache."""
        if cls._instance is None:
            cls._instance = super(ModelHealthCache, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the health cache (only runs once due to singleton)."""
        if not hasattr(self, '_initialized'):
            self._initialized = True
            logger.info("Model health cache service initialized")
    
    def get_cached_health(self, model: str) -> Optional[bool]:
        """
        Get cached health status for a model if still valid.
        
        Args:
            model: Model identifier
            
        Returns:
            True if healthy, False if unhealthy, None if not cached or expired
        """
        now = time.time()
        cache_entry = self._health_cache.get(model)
        
        if cache_entry and now - cache_entry["ts"] < self._CACHE_TTL_SECONDS:
            return cache_entry["ok"]
        
        return None
    
    def set_health_status(self, model: str, is_healthy: bool) -> None:
        """
        Update health status for a model.
        
        Args:
            model: Model identifier
            is_healthy: Whether the model is healthy
        """
        self._health_cache[model] = {"ok": is_healthy, "ts": time.time()}
        status = "healthy" if is_healthy else "unhealthy"
        logger.info(f"Updated health status for {model}: {status}")
    
    def clear_cache(self, model: Optional[str] = None) -> None:
        """
        Clear health cache for a specific model or all models.
        
        Args:
            model: Specific model to clear, or None to clear all
        """
        if model:
            self._health_cache.pop(model, None)
            logger.info(f"Cleared health cache for {model}")
        else:
            self._health_cache.clear()
            logger.info("Cleared all model health cache")
    
    def get_all_cached_status(self) -> Dict[str, Dict[str, Any]]:
        """Get all cached health statuses with metadata."""
        now = time.time()
        result = {}
        
        for model, entry in self._health_cache.items():
            age_seconds = now - entry["ts"]
            is_expired = age_seconds >= self._CACHE_TTL_SECONDS
            
            result[model] = {
                "is_healthy": entry["ok"],
                "checked_at": datetime.fromtimestamp(entry["ts"]).isoformat(),
                "age_seconds": int(age_seconds),
                "is_expired": is_expired
            }
        
        return result
    
    async def probe_model(self, model: str, api_key: str) -> bool:
        """
        Probe a model with a minimal request to check health.
        Results are automatically cached.
        
        Args:
            model: Model identifier
            api_key: API key for the model
            
        Returns:
            True if healthy, False otherwise
        """
        # Check cache first
        cached = self.get_cached_health(model)
        if cached is not None:
            logger.debug(f"Using cached health status for {model}: {cached}")
            return cached
        
        # Perform health check
        is_healthy = await self._do_probe(model, api_key)
        
        # Cache the result
        self.set_health_status(model, is_healthy)
        
        return is_healthy
    
    async def _do_probe(self, model: str, api_key: str) -> bool:
        """
        Internal method to perform actual health probe.
        
        Args:
            model: Model identifier
            api_key: API key for the model
            
        Returns:
            True if healthy (HTTP 200/503 for HF), False otherwise
        """
        try:
            if model.startswith("gpt"):
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                }
                payload = {
                    "model": model,
                    "messages": [{"role": "user", "content": "ping"}],
                    "max_tokens": 1,
                }
                r = await CLIENT.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers=headers,
                    json=payload,
                )
                return r.status_code == 200
            
            elif "/" in model:  # Hugging Face style
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                }
                url = f"https://api-inference.huggingface.co/models/{model}"
                r = await CLIENT.post(url, headers=headers, json={"inputs": "ping"})
                # HF returns 503 while model is loading which is acceptable
                return r.status_code in (200, 503)
            
            elif model.startswith("claude"):
                headers = {
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json",
                }
                payload = {
                    "model": model,
                    "max_tokens": 1,
                    "messages": [{"role": "user", "content": "ping"}],
                }
                r = await CLIENT.post(
                    "https://api.anthropic.com/v1/messages",
                    headers=headers,
                    json=payload,
                )
                return r.status_code == 200
            
            elif model.startswith("gemini"):
                url = (
                    f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
                    f"?key={api_key}"
                )
                payload = {
                    "contents": [{"parts": [{"text": "ping"}]}],
                    "generationConfig": {"maxOutputTokens": 1},
                }
                r = await CLIENT.post(url, headers={"Content-Type": "application/json"}, json=payload)
                return r.status_code == 200
                
        except Exception as e:
            logger.warning(f"Health probe failed for {model}: {e}")
            return False
        
        return False


# Global singleton instance
model_health_cache = ModelHealthCache()