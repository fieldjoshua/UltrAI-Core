import asyncio
import httpx
from typing import Dict, Any

from app.utils.logging import get_logger

logger = get_logger("provider_probe")

class ProviderProbe:
    """A small utility to actively probe provider health with a short timeout."""

    PROBE_ENDPOINTS = {
        "openai": "https://api.openai.com/v1/models",
        "anthropic": "https://api.anthropic.com/v1/messages",
        "google": "https://generativelanguage.googleapis.com/v1beta/models",
    }
    
    DEFAULT_TIMEOUT = 5.0

    async def check_provider(self, provider: str, api_key: str) -> Dict[str, Any]:
        """
        Checks the health of a single provider.

        Args:
            provider: The name of the provider (e.g., 'openai').
            api_key: The API key for the provider.

        Returns:
            A dictionary with the provider's status.
        """
        if provider not in self.PROBE_ENDPOINTS:
            return {"provider": provider, "status": "error", "message": "Unknown provider"}

        url = self.PROBE_ENDPOINTS[provider]
        headers = self._get_auth_headers(provider, api_key)

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, timeout=self.DEFAULT_TIMEOUT)
                
                if response.status_code == 200:
                    return {"provider": provider, "status": "healthy", "latency_ms": response.elapsed.total_seconds() * 1000}
                else:
                    return {
                        "provider": provider,
                        "status": "unhealthy",
                        "error": f"HTTP {response.status_code}: {response.text}",
                    }
        except httpx.TimeoutException:
            logger.warning(f"Health probe for {provider} timed out after {self.DEFAULT_TIMEOUT}s.")
            return {"provider": provider, "status": "unhealthy", "error": "Request timed out"}
        except httpx.RequestError as e:
            logger.error(f"Health probe for {provider} failed: {e}")
            return {"provider": provider, "status": "unhealthy", "error": str(e)}

    def _get_auth_headers(self, provider: str, api_key: str) -> Dict[str, str]:
        """Returns the appropriate authentication headers for a given provider."""
        if provider == "openai":
            return {"Authorization": f"Bearer {api_key}"}
        elif provider == "anthropic":
            return {"x-api-key": api_key, "anthropic-version": "2023-06-01"}
        elif provider == "google":
            return {"x-goog-api-key": api_key}
        return {}

# Global instance
provider_probe = ProviderProbe()
