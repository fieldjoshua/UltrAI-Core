"""
Provider health probe utility for quick health checks.

This module provides a 5-second health probe for LLM providers
to be used by status checks. It performs minimal API calls to
verify provider availability without changing behavior.
"""

import asyncio
import logging
from typing import Dict, Tuple, Optional
import httpx
from app.services.llm_adapters import CLIENT

logger = logging.getLogger(__name__)

# 5 second timeout for health probes
HEALTH_PROBE_TIMEOUT = 5.0


async def probe_openai_health(api_key: str) -> Tuple[bool, Optional[str]]:
    """
    Probe OpenAI API health with a minimal request.
    
    Args:
        api_key: OpenAI API key
        
    Returns:
        Tuple of (is_healthy, error_message)
    """
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Use models endpoint for a lightweight check
        async with httpx.AsyncClient(timeout=HEALTH_PROBE_TIMEOUT) as client:
            response = await client.get(
                "https://api.openai.com/v1/models/gpt-4",
                headers=headers
            )
            
            if response.status_code == 200:
                return True, None
            elif response.status_code == 401:
                return False, "Invalid API key"
            elif response.status_code == 404:
                return False, "Model not found"
            else:
                return False, f"HTTP {response.status_code}"
                
    except asyncio.TimeoutError:
        return False, "Timeout after 5 seconds"
    except Exception as e:
        return False, str(e)


async def probe_anthropic_health(api_key: str) -> Tuple[bool, Optional[str]]:
    """
    Probe Anthropic API health with a minimal request.
    
    Args:
        api_key: Anthropic API key
        
    Returns:
        Tuple of (is_healthy, error_message)
    """
    try:
        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }
        
        # Minimal completion request
        payload = {
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 1,
            "messages": [{"role": "user", "content": "Hi"}]
        }
        
        async with httpx.AsyncClient(timeout=HEALTH_PROBE_TIMEOUT) as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                return True, None
            elif response.status_code == 401:
                return False, "Invalid API key"
            elif response.status_code == 404:
                return False, "Model not found"
            else:
                return False, f"HTTP {response.status_code}"
                
    except asyncio.TimeoutError:
        return False, "Timeout after 5 seconds"
    except Exception as e:
        return False, str(e)


async def probe_google_health(api_key: str) -> Tuple[bool, Optional[str]]:
    """
    Probe Google Gemini API health with a minimal request.
    
    Args:
        api_key: Google API key
        
    Returns:
        Tuple of (is_healthy, error_message)
    """
    try:
        # Check model info endpoint
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash"
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": api_key
        }
        
        async with httpx.AsyncClient(timeout=HEALTH_PROBE_TIMEOUT) as client:
            response = await client.get(url, headers=headers)
            
            if response.status_code == 200:
                return True, None
            elif response.status_code == 401 or response.status_code == 403:
                return False, "Invalid API key"
            elif response.status_code == 404:
                return False, "Model not found"
            else:
                return False, f"HTTP {response.status_code}"
                
    except asyncio.TimeoutError:
        return False, "Timeout after 5 seconds"
    except Exception as e:
        return False, str(e)


async def probe_all_providers(
    openai_key: Optional[str] = None,
    anthropic_key: Optional[str] = None,
    google_key: Optional[str] = None
) -> Dict[str, Dict[str, any]]:
    """
    Probe all configured providers in parallel.
    
    Args:
        openai_key: OpenAI API key (optional)
        anthropic_key: Anthropic API key (optional)
        google_key: Google API key (optional)
        
    Returns:
        Dictionary with health status for each provider
    """
    results = {}
    tasks = []
    provider_names = []
    
    if openai_key:
        tasks.append(probe_openai_health(openai_key))
        provider_names.append("openai")
        
    if anthropic_key:
        tasks.append(probe_anthropic_health(anthropic_key))
        provider_names.append("anthropic")
        
    if google_key:
        tasks.append(probe_google_health(google_key))
        provider_names.append("google")
    
    if tasks:
        # Run all probes in parallel with 5s timeout
        probe_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for provider, result in zip(provider_names, probe_results):
            if isinstance(result, Exception):
                results[provider] = {
                    "healthy": False,
                    "error": str(result),
                    "latency_ms": 5000
                }
            else:
                is_healthy, error = result
                results[provider] = {
                    "healthy": is_healthy,
                    "error": error,
                    "latency_ms": None  # Could add timing if needed
                }
    
    return results


# Convenience function for use in status checks
async def quick_health_check() -> Dict[str, bool]:
    """
    Quick health check for all providers using environment variables.
    
    Returns:
        Dictionary mapping provider names to health status
    """
    import os
    
    results = await probe_all_providers(
        openai_key=os.getenv("OPENAI_API_KEY"),
        anthropic_key=os.getenv("ANTHROPIC_API_KEY"),
        google_key=os.getenv("GOOGLE_API_KEY")
    )
    
    return {
        provider: info["healthy"] 
        for provider, info in results.items()
    }