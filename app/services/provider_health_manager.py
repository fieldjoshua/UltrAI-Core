"""
Provider Health Manager for graceful degradation of LLM services.

This service monitors LLM provider health and implements graceful degradation
when providers are unavailable or performing poorly.
"""

import asyncio
import os
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field

from app.utils.logging import get_logger
from app.services.provider_probe import provider_probe

logger = get_logger("provider_health_manager")


@dataclass
class ProviderHealth:
    """Health status for a single provider."""
    provider: str
    status: str  # "healthy", "degraded", "unhealthy"
    last_success: Optional[datetime] = None
    last_failure: Optional[datetime] = None
    consecutive_failures: int = 0
    error_rate: float = 0.0
    average_latency_ms: float = 0.0
    last_error_message: Optional[str] = None
    models_available: List[str] = field(default_factory=list)
    
    @property
    def is_available(self) -> bool:
        """Check if provider is available for use."""
        return self.status in ["healthy", "degraded"]
    
    @property
    def minutes_since_last_success(self) -> Optional[float]:
        """Minutes since last successful request."""
        if not self.last_success:
            return None
        return (datetime.now() - self.last_success).total_seconds() / 60


class ProviderHealthManager:
    """Manages health status and graceful degradation for LLM providers."""
    
    # Health thresholds
    ERROR_RATE_THRESHOLD = 0.3  # 30% error rate triggers degraded status
    CONSECUTIVE_FAILURE_THRESHOLD = 3  # 3 consecutive failures = unhealthy
    RECOVERY_WINDOW_MINUTES = int(os.getenv("PROVIDER_RECOVERY_WINDOW_MINUTES", "5"))  # Time to wait before retrying unhealthy provider
    LATENCY_DEGRADED_THRESHOLD_MS = 10000  # 10s latency = degraded
    
    def __init__(self):
        """Initialize the provider health manager."""
        self._provider_health: Dict[str, ProviderHealth] = {}
        self._request_history: Dict[str, List[Tuple[bool, float]]] = defaultdict(list)
        self._lock = asyncio.Lock()
        
    async def probe_providers(self) -> None:
        """Actively probe providers to update their health status."""
        # This can be called periodically or at startup
        # For now, it will be used by get_health_summary
        providers_to_check = {
            "openai": os.getenv("OPENAI_API_KEY"),
            "anthropic": os.getenv("ANTHROPIC_API_KEY"),
            "google": os.getenv("GOOGLE_API_KEY"),
        }

        tasks = []
        for provider, api_key in providers_to_check.items():
            if api_key:
                tasks.append(provider_probe.check_provider(provider, api_key))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Provider probe task failed: {result}")
                continue
            
            provider = result.get("provider")
            if provider:
                if result.get("status") == "healthy":
                    await self.record_success(provider, "probe", result.get("latency_ms", 0))
                else:
                    await self.record_failure(provider, result.get("error", "Probe failed"))
    
    async def get_provider_health(self, provider: str) -> ProviderHealth:
        """Get health status for a specific provider."""
        async with self._lock:
            if provider not in self._provider_health:
                self._provider_health[provider] = ProviderHealth(
                    provider=provider,
                    status="healthy"  # Assume healthy until proven otherwise
                )
            return self._provider_health[provider]
    
    async def record_success(
        self,
        provider: str,
        model: str,
        latency_ms: float
    ) -> None:
        """Record a successful request to a provider."""
        async with self._lock:
            health = await self._get_or_create_health(provider)
            
            # Update success metrics
            health.last_success = datetime.now()
            health.consecutive_failures = 0
            
            # Add model to available list if not present
            if model not in health.models_available:
                health.models_available.append(model)
            
            # Update request history
            self._add_request_history(provider, True, latency_ms)
            
            # Recalculate health status
            await self._update_health_status(provider)
            
            logger.info(
                f"Provider {provider} success recorded. "
                f"Status: {health.status}, Latency: {latency_ms:.0f}ms"
            )
    
    async def record_failure(
        self,
        provider: str,
        error_message: str,
        model: Optional[str] = None
    ) -> None:
        """Record a failed request to a provider."""
        async with self._lock:
            health = await self._get_or_create_health(provider)
            
            # Update failure metrics
            health.last_failure = datetime.now()
            health.consecutive_failures += 1
            health.last_error_message = error_message
            
            # Remove model from available list on persistent failures
            if model and health.consecutive_failures >= 2:
                if model in health.models_available:
                    health.models_available.remove(model)
            
            # Update request history
            self._add_request_history(provider, False, 0)
            
            # Recalculate health status
            await self._update_health_status(provider)
            
            logger.warning(
                f"Provider {provider} failure recorded. "
                f"Status: {health.status}, Consecutive failures: {health.consecutive_failures}, "
                f"Error: {error_message[:100]}"
            )
    
    async def get_available_providers(self) -> List[str]:
        """Get list of currently available providers (healthy or degraded)."""
        async with self._lock:
            available = []
            for provider, health in self._provider_health.items():
                # Check if provider should be retried after being unhealthy
                if health.status == "unhealthy" and health.last_failure:
                    time_since_failure = datetime.now() - health.last_failure
                    if time_since_failure > timedelta(minutes=self.RECOVERY_WINDOW_MINUTES):
                        # Reset to degraded for retry
                        health.status = "degraded"
                        health.consecutive_failures = 0
                        logger.info(
                            f"Provider {provider} moved from unhealthy to degraded "
                            f"for retry after {self.RECOVERY_WINDOW_MINUTES} minutes"
                        )
                
                if health.is_available:
                    available.append(provider)
            
            return available
    
    async def get_health_summary(self) -> Dict[str, Dict]:
        """Get comprehensive health summary for all providers."""
        try:
            # Actively probe providers before generating the summary
            await self.probe_providers()

            async with self._lock:
                summary = {}
                for provider, health in self._provider_health.items():
                    summary[provider] = {
                        "status": health.status,
                        "is_available": health.is_available,
                        "consecutive_failures": health.consecutive_failures,
                        "error_rate": round(health.error_rate, 3),
                        "average_latency_ms": round(health.average_latency_ms, 0),
                        "models_available": health.models_available,
                        "last_success": health.last_success.isoformat() if health.last_success else None,
                        "last_failure": health.last_failure.isoformat() if health.last_failure else None,
                        "minutes_since_last_success": health.minutes_since_last_success,
                        "last_error": health.last_error_message[:100] if health.last_error_message else None,
                    }

                # Add overall system health
                available_providers = await self.get_available_providers()
                total_providers = len(self._provider_health)

                system_status = "healthy"
                if len(available_providers) == 0:
                    system_status = "critical"
                elif len(available_providers) == 1:
                    system_status = "degraded"
                elif len(available_providers) < total_providers:
                    system_status = "partial"

                summary["_system"] = {
                    "status": system_status,
                    "available_providers": available_providers,
                    "total_providers": total_providers,
                    "minimum_required": 2,  # For Ultra orchestration
                    "meets_requirements": len(available_providers) >= 2,
                }
                return summary
        except Exception as e:
            # Non-fatal: return minimal summary instead of raising
            logger.warning(f"get_health_summary failed: {e}")
            return {
                "_system": {
                    "status": "unknown",
                    "available_providers": [],
                    "total_providers": 0,
                    "minimum_required": 2,
                    "meets_requirements": False,
                }
            }
    
    async def get_degradation_message(self) -> Optional[str]:
        """Get user-friendly message about current degradation status."""
        summary = await self.get_health_summary()
        system = summary["_system"]
        
        if system["status"] == "healthy":
            return None
        
        available = system["available_providers"]
        total = system["total_providers"]
        
        if system["status"] == "critical":
            return (
                "⚠️ All AI providers are currently unavailable. "
                "Please try again in a few minutes."
            )
        elif not system["meets_requirements"]:
            return (
                f"⚠️ Limited AI capacity: Only {len(available)} of {total} providers available. "
                f"Ultra orchestration requires at least 2 providers. "
                f"Results may be limited to single model responses."
            )
        elif system["status"] == "partial":
            unavailable = total - len(available)
            return (
                f"ℹ️ Running with reduced capacity: {unavailable} provider(s) temporarily unavailable. "
                f"Service is operational but some models may not be accessible."
            )
        
        return None
    
    async def _get_or_create_health(self, provider: str) -> ProviderHealth:
        """Get or create health entry for provider (must be called with lock)."""
        if provider not in self._provider_health:
            self._provider_health[provider] = ProviderHealth(
                provider=provider,
                status="healthy"
            )
        return self._provider_health[provider]
    
    def _add_request_history(
        self,
        provider: str,
        success: bool,
        latency_ms: float
    ) -> None:
        """Add request to history (must be called with lock)."""
        # Keep last 100 requests per provider
        history = self._request_history[provider]
        history.append((success, latency_ms))
        if len(history) > 100:
            history.pop(0)
    
    async def _update_health_status(self, provider: str) -> None:
        """Update health status based on recent metrics (must be called with lock)."""
        health = self._provider_health[provider]
        history = self._request_history[provider]
        
        if not history:
            return
        
        # Calculate error rate
        recent_requests = history[-20:]  # Last 20 requests
        failures = sum(1 for success, _ in recent_requests if not success)
        health.error_rate = failures / len(recent_requests)
        
        # Calculate average latency
        successful_latencies = [
            latency for success, latency in recent_requests
            if success and latency > 0
        ]
        if successful_latencies:
            health.average_latency_ms = sum(successful_latencies) / len(successful_latencies)
        
        # Determine health status
        if health.consecutive_failures >= self.CONSECUTIVE_FAILURE_THRESHOLD:
            health.status = "unhealthy"
        elif health.error_rate >= self.ERROR_RATE_THRESHOLD:
            health.status = "degraded"
        elif health.average_latency_ms >= self.LATENCY_DEGRADED_THRESHOLD_MS:
            health.status = "degraded"
        else:
            health.status = "healthy"


# Global instance
provider_health_manager = ProviderHealthManager()