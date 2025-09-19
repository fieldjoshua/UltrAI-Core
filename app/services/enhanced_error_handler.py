"""
Enhanced Error Handler for UltrAI Orchestration Pipeline

This module provides advanced error handling capabilities including:
- Circuit breaker patterns for provider health management
- Graceful degradation strategies 
- Enhanced timeout management
- Smart fallback response generation
- Error correlation and recovery suggestions

Integration points with Aux Model's work:
- Uses provider health probes for circuit breaker decisions
- Coordinates with 503 error payload generation
- Provides error details for UI status displays
"""

import asyncio
import time
import uuid
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from datetime import datetime, timedelta

from app.config import Config
from app.utils.logging import get_logger, CorrelationContext

logger = get_logger("enhanced_error_handler")


class ErrorSeverity(Enum):
    """Error severity levels for prioritization."""
    LOW = "low"           # Non-critical, can continue
    MEDIUM = "medium"     # Degraded functionality  
    HIGH = "high"         # Significant impact
    CRITICAL = "critical" # Service unavailable


class ProviderState(Enum):
    """Circuit breaker states for providers."""
    HEALTHY = "healthy"         # Normal operation
    DEGRADED = "degraded"       # Some issues but operational  
    CIRCUIT_OPEN = "circuit_open"  # Temporarily disabled
    CIRCUIT_CLOSED = "circuit_closed"  # Permanently disabled


@dataclass
class ErrorContext:
    """Enhanced error context with correlation tracking."""
    correlation_id: str
    stage: str
    provider: str
    model: str
    error_type: str
    error_message: str
    severity: ErrorSeverity
    timestamp: datetime
    retry_count: int = 0
    recoverable: bool = True
    suggested_action: Optional[str] = None


@dataclass
class CircuitBreakerState:
    """Circuit breaker state for a provider."""
    provider: str
    state: ProviderState
    failure_count: int = 0
    last_failure_time: Optional[datetime] = None
    last_success_time: Optional[datetime] = None
    next_retry_time: Optional[datetime] = None
    consecutive_failures: int = 0
    
    # Circuit breaker thresholds
    failure_threshold: int = 5  # Open circuit after 5 failures
    recovery_timeout: int = 60  # Try recovery after 60 seconds
    degraded_threshold: int = 3  # Mark degraded after 3 failures


class EnhancedErrorHandler:
    """Enhanced error handler with circuit breaker patterns and graceful degradation."""
    
    def __init__(self):
        self.circuit_breakers: Dict[str, CircuitBreakerState] = {}
        self.error_history: List[ErrorContext] = []
        self.active_timeouts: Set[str] = set()
        self.fallback_responses_cache: Dict[str, str] = {}
        
        # Enhanced timeout configurations
        self.timeout_configs = {
            "initial_response": {
                "stage_timeout": Config.INITIAL_RESPONSE_TIMEOUT,
                "model_timeout": Config.LLM_REQUEST_TIMEOUT,
                "warning_threshold": Config.LLM_REQUEST_TIMEOUT * 0.8
            },
            "peer_review_and_revision": {
                "stage_timeout": Config.PEER_REVIEW_TIMEOUT,
                "model_timeout": Config.LLM_REQUEST_TIMEOUT,
                "warning_threshold": Config.LLM_REQUEST_TIMEOUT * 0.8
            },
            "ultra_synthesis": {
                "stage_timeout": Config.ULTRA_SYNTHESIS_TIMEOUT,
                "model_timeout": Config.LLM_REQUEST_TIMEOUT,
                "warning_threshold": Config.LLM_REQUEST_TIMEOUT * 0.8
            },
            "concurrent_execution": {
                "stage_timeout": Config.CONCURRENT_EXECUTION_TIMEOUT,
                "model_timeout": Config.LLM_REQUEST_TIMEOUT,
                "warning_threshold": Config.CONCURRENT_EXECUTION_TIMEOUT * 0.8
            }
        }
        
        logger.info("Enhanced Error Handler initialized with circuit breaker patterns")
    
    def get_provider_circuit_state(self, provider: str) -> CircuitBreakerState:
        """Get or create circuit breaker state for a provider."""
        if provider not in self.circuit_breakers:
            self.circuit_breakers[provider] = CircuitBreakerState(
                provider=provider,
                state=ProviderState.HEALTHY
            )
        return self.circuit_breakers[provider]
    
    async def handle_provider_error(
        self, 
        provider: str, 
        model: str, 
        error: Exception, 
        stage: str,
        correlation_id: Optional[str] = None
    ) -> ErrorContext:
        """Handle provider-specific errors with circuit breaker logic."""
        correlation_id = correlation_id or CorrelationContext.get_correlation_id()
        
        # Classify error severity and type
        error_type, severity, recoverable = self._classify_error(error, provider)
        
        # Create error context
        error_context = ErrorContext(
            correlation_id=correlation_id,
            stage=stage,
            provider=provider,
            model=model,
            error_type=error_type,
            error_message=str(error),
            severity=severity,
            timestamp=datetime.utcnow(),
            recoverable=recoverable,
            suggested_action=self._get_suggested_action(error_type, provider)
        )
        
        # Update circuit breaker state
        await self._update_circuit_breaker(provider, error_context)
        
        # Log error with enhanced context
        logger.error(
            f"Provider error: {provider}/{model} - {error_type}",
            extra={
                "correlation_id": correlation_id,
                "stage": stage,
                "provider": provider,
                "model": model,
                "error_type": error_type,
                "severity": severity.value,
                "recoverable": recoverable,
                "circuit_state": self.circuit_breakers[provider].state.value
            },
            exc_info=True
        )
        
        # Store in error history (keep last 100 errors)
        self.error_history.append(error_context)
        if len(self.error_history) > 100:
            self.error_history.pop(0)
            
        return error_context
    
    async def handle_stage_timeout(
        self, 
        stage: str, 
        elapsed_time: float,
        correlation_id: Optional[str] = None
    ) -> ErrorContext:
        """Handle stage-level timeout with smart recovery suggestions."""
        correlation_id = correlation_id or CorrelationContext.get_correlation_id()
        
        timeout_config = self.timeout_configs.get(stage, self.timeout_configs["initial_response"])
        stage_timeout = timeout_config["stage_timeout"]
        
        # Determine severity based on how much we exceeded the timeout
        if elapsed_time > stage_timeout * 1.5:
            severity = ErrorSeverity.HIGH
        elif elapsed_time > stage_timeout * 1.2:
            severity = ErrorSeverity.MEDIUM
        else:
            severity = ErrorSeverity.LOW
            
        error_context = ErrorContext(
            correlation_id=correlation_id,
            stage=stage,
            provider="orchestration",
            model="pipeline",
            error_type="stage_timeout",
            error_message=f"Stage {stage} timed out after {elapsed_time:.2f}s (limit: {stage_timeout}s)",
            severity=severity,
            timestamp=datetime.utcnow(),
            recoverable=True,
            suggested_action=self._get_timeout_recovery_action(stage, elapsed_time, stage_timeout)
        )
        
        logger.warning(
            f"Stage timeout: {stage} exceeded {elapsed_time:.2f}s",
            extra={
                "correlation_id": correlation_id,
                "stage": stage,
                "elapsed_time": elapsed_time,
                "timeout_limit": stage_timeout,
                "severity": severity.value
            }
        )
        
        self.error_history.append(error_context)
        return error_context
    
    async def should_attempt_provider(self, provider: str) -> Tuple[bool, Optional[str]]:
        """Check if provider should be attempted based on circuit breaker state."""
        circuit_state = self.get_provider_circuit_state(provider)
        current_time = datetime.utcnow()
        
        if circuit_state.state == ProviderState.HEALTHY:
            return True, None
            
        elif circuit_state.state == ProviderState.DEGRADED:
            # Allow attempts but with degraded expectations
            return True, f"Provider {provider} in degraded state - may have slower response times"
            
        elif circuit_state.state == ProviderState.CIRCUIT_OPEN:
            # Check if recovery timeout has passed
            if (circuit_state.next_retry_time and 
                current_time >= circuit_state.next_retry_time):
                # Try recovery - move to degraded state
                circuit_state.state = ProviderState.DEGRADED
                circuit_state.next_retry_time = None
                logger.info(
                    f"Circuit breaker recovery attempt for {provider}",
                    extra={"provider": provider, "previous_failures": circuit_state.consecutive_failures}
                )
                return True, f"Provider {provider} attempting recovery from circuit breaker"
            else:
                # Still in timeout period
                retry_in = int((circuit_state.next_retry_time - current_time).total_seconds())
                return False, f"Provider {provider} circuit breaker open - retry in {retry_in}s"
                
        else:  # CIRCUIT_CLOSED
            return False, f"Provider {provider} permanently disabled due to repeated failures"
    
    async def record_provider_success(self, provider: str, response_time: float):
        """Record successful provider response and update circuit breaker."""
        circuit_state = self.get_provider_circuit_state(provider)
        circuit_state.last_success_time = datetime.utcnow()
        
        # Reset failure counters on success
        if circuit_state.consecutive_failures > 0:
            logger.info(
                f"Provider {provider} recovered - resetting failure count from {circuit_state.consecutive_failures}",
                extra={"provider": provider, "response_time": response_time}
            )
            circuit_state.consecutive_failures = 0
            circuit_state.failure_count = max(0, circuit_state.failure_count - 1)
            
        # Return to healthy state if previously degraded
        if circuit_state.state in [ProviderState.DEGRADED, ProviderState.CIRCUIT_OPEN]:
            circuit_state.state = ProviderState.HEALTHY
            logger.info(f"Provider {provider} returned to healthy state")
    
    def generate_fallback_response(
        self, 
        stage: str, 
        original_prompt: str, 
        available_context: Dict[str, Any],
        correlation_id: Optional[str] = None
    ) -> str:
        """Generate intelligent fallback response when stages fail."""
        correlation_id = correlation_id or CorrelationContext.get_correlation_id()
        
        # Check cache for similar fallback responses
        cache_key = f"{stage}:{hash(original_prompt) % 10000}"
        if cache_key in self.fallback_responses_cache:
            logger.info(
                f"Using cached fallback response for {stage}",
                extra={"correlation_id": correlation_id, "stage": stage}
            )
            return self.fallback_responses_cache[cache_key]
        
        # Generate context-aware fallback based on stage
        if stage == "initial_response":
            fallback = self._generate_initial_response_fallback(original_prompt, available_context)
        elif stage == "peer_review_and_revision":
            fallback = self._generate_peer_review_fallback(original_prompt, available_context)
        elif stage == "ultra_synthesis":
            fallback = self._generate_synthesis_fallback(original_prompt, available_context)
        else:
            fallback = self._generate_generic_fallback(original_prompt, available_context)
        
        # Cache the fallback (keep cache small - max 50 entries)
        if len(self.fallback_responses_cache) >= 50:
            # Remove oldest entry
            oldest_key = next(iter(self.fallback_responses_cache))
            del self.fallback_responses_cache[oldest_key]
            
        self.fallback_responses_cache[cache_key] = fallback
        
        logger.info(
            f"Generated fallback response for {stage}",
            extra={
                "correlation_id": correlation_id,
                "stage": stage,
                "response_length": len(fallback)
            }
        )
        
        return fallback
    
    def get_error_summary(self, correlation_id: Optional[str] = None) -> Dict[str, Any]:
        """Get comprehensive error summary for monitoring and debugging."""
        current_time = datetime.utcnow()
        
        # Filter errors by correlation_id if provided
        relevant_errors = self.error_history
        if correlation_id:
            relevant_errors = [e for e in self.error_history if e.correlation_id == correlation_id]
        
        # Provider health summary
        provider_health = {}
        for provider, circuit_state in self.circuit_breakers.items():
            provider_health[provider] = {
                "state": circuit_state.state.value,
                "failure_count": circuit_state.failure_count,
                "consecutive_failures": circuit_state.consecutive_failures,
                "last_failure": circuit_state.last_failure_time.isoformat() if circuit_state.last_failure_time else None,
                "last_success": circuit_state.last_success_time.isoformat() if circuit_state.last_success_time else None,
                "next_retry": circuit_state.next_retry_time.isoformat() if circuit_state.next_retry_time else None
            }
        
        # Recent error analysis
        recent_errors = [e for e in relevant_errors if (current_time - e.timestamp).total_seconds() < 300]  # Last 5 minutes
        error_by_severity = {}
        for severity in ErrorSeverity:
            error_by_severity[severity.value] = len([e for e in recent_errors if e.severity == severity])
        
        return {
            "provider_health": provider_health,
            "recent_errors": {
                "total_count": len(recent_errors),
                "by_severity": error_by_severity,
                "recoverable_count": len([e for e in recent_errors if e.recoverable])
            },
            "correlation_id": correlation_id,
            "timestamp": current_time.isoformat()
        }
    
    def _classify_error(self, error: Exception, provider: str) -> Tuple[str, ErrorSeverity, bool]:
        """Classify error type, severity, and recoverability."""
        error_msg = str(error).lower()
        error_type = type(error).__name__
        
        # Rate limiting errors
        if any(pattern in error_msg for pattern in ["rate limit", "429", "quota", "too many"]):
            return "rate_limit", ErrorSeverity.MEDIUM, True
            
        # Timeout errors
        if any(pattern in error_msg for pattern in ["timeout", "timed out", "deadline"]):
            return "timeout", ErrorSeverity.MEDIUM, True
            
        # Authentication errors
        if any(pattern in error_msg for pattern in ["auth", "unauthorized", "api key", "401", "403"]):
            return "authentication", ErrorSeverity.HIGH, False
            
        # Network errors
        if any(pattern in error_msg for pattern in ["connection", "network", "dns", "resolve"]):
            return "network", ErrorSeverity.HIGH, True
            
        # Service unavailable
        if any(pattern in error_msg for pattern in ["503", "service unavailable", "server error"]):
            return "service_unavailable", ErrorSeverity.HIGH, True
            
        # Model not found
        if any(pattern in error_msg for pattern in ["model not found", "404", "not found"]):
            return "model_not_found", ErrorSeverity.HIGH, False
            
        # Content filtering
        if any(pattern in error_msg for pattern in ["content policy", "safety", "filtered"]):
            return "content_filtered", ErrorSeverity.LOW, False
            
        # Generic server errors
        if any(pattern in error_msg for pattern in ["500", "internal server", "server error"]):
            return "server_error", ErrorSeverity.HIGH, True
            
        # Unknown error
        return "unknown", ErrorSeverity.MEDIUM, True
    
    def _get_suggested_action(self, error_type: str, provider: str) -> str:
        """Get recovery suggestion based on error type."""
        suggestions = {
            "rate_limit": f"Wait before retrying {provider}. Consider reducing request frequency.",
            "timeout": f"Retry with exponential backoff. Check {provider} service status.",
            "authentication": f"Verify {provider.upper()}_API_KEY environment variable is set correctly.",
            "network": f"Check network connectivity and {provider} service availability.",
            "service_unavailable": f"{provider} service is temporarily down. Retry later.",
            "model_not_found": f"Verify model name is correct for {provider}. Check available models.",
            "content_filtered": "Modify prompt to comply with content policies.",
            "server_error": f"{provider} experiencing server issues. Retry with backoff.",
            "unknown": f"Check {provider} documentation for error details."
        }
        return suggestions.get(error_type, "Check provider documentation and retry.")
    
    def _get_timeout_recovery_action(self, stage: str, elapsed_time: float, timeout_limit: float) -> str:
        """Get stage-specific timeout recovery suggestions."""
        if stage == "initial_response":
            return f"Consider reducing number of models or increasing INITIAL_RESPONSE_TIMEOUT (current: {timeout_limit}s)"
        elif stage == "peer_review_and_revision":
            return f"Peer review taking longer than expected. Consider increasing PEER_REVIEW_TIMEOUT (current: {timeout_limit}s)"
        elif stage == "ultra_synthesis":
            return f"Synthesis stage timeout. Consider increasing ULTRA_SYNTHESIS_TIMEOUT (current: {timeout_limit}s)"
        else:
            return f"Stage {stage} exceeded timeout. Consider optimizing or increasing timeout limits."
    
    async def _update_circuit_breaker(self, provider: str, error_context: ErrorContext):
        """Update circuit breaker state based on error."""
        circuit_state = self.get_provider_circuit_state(provider)
        current_time = datetime.utcnow()
        
        circuit_state.last_failure_time = current_time
        circuit_state.failure_count += 1
        circuit_state.consecutive_failures += 1
        
        # Update state based on failure thresholds
        if circuit_state.consecutive_failures >= circuit_state.failure_threshold:
            if circuit_state.state != ProviderState.CIRCUIT_OPEN:
                circuit_state.state = ProviderState.CIRCUIT_OPEN
                circuit_state.next_retry_time = current_time + timedelta(seconds=circuit_state.recovery_timeout)
                logger.warning(
                    f"Circuit breaker opened for {provider} after {circuit_state.consecutive_failures} failures",
                    extra={"provider": provider, "next_retry": circuit_state.next_retry_time.isoformat()}
                )
        elif circuit_state.consecutive_failures >= circuit_state.degraded_threshold:
            if circuit_state.state == ProviderState.HEALTHY:
                circuit_state.state = ProviderState.DEGRADED
                logger.info(f"Provider {provider} marked as degraded after {circuit_state.consecutive_failures} failures")
    
    def _generate_initial_response_fallback(self, prompt: str, context: Dict[str, Any]) -> str:
        """Generate fallback for initial response stage."""
        return f"""I apologize, but I'm currently experiencing technical difficulties connecting to the AI models. 

Your question: "{prompt[:200]}{'...' if len(prompt) > 200 else ''}"

While I cannot provide my full analysis at this moment due to service limitations, I recommend:
1. Please try your request again in a few moments
2. For urgent matters, you may want to break down complex questions into simpler parts
3. Check back later when our AI models are fully operational

This is a temporary service interruption, and normal functionality should resume shortly."""
    
    def _generate_peer_review_fallback(self, prompt: str, context: Dict[str, Any]) -> str:
        """Generate fallback for peer review stage."""
        initial_responses = context.get("responses", {})
        if initial_responses:
            models = list(initial_responses.keys())
            return f"""Based on the initial responses from {len(models)} AI model(s), here's a consolidated view:

While the peer review phase encountered technical difficulties, the initial analysis from our models provides valuable insights. The responses show consistency in addressing your question about: "{prompt[:150]}{'...' if len(prompt) > 150 else ''}"

Note: This response bypassed the usual peer review enhancement due to temporary service limitations. For the most comprehensive analysis, please retry your request when all systems are operational."""
        else:
            return self._generate_initial_response_fallback(prompt, context)
    
    def _generate_synthesis_fallback(self, prompt: str, context: Dict[str, Any]) -> str:
        """Generate fallback for synthesis stage."""
        revised_responses = context.get("revised_responses", {})
        initial_responses = context.get("responses", {})
        responses = revised_responses or initial_responses
        
        if responses:
            model_count = len(responses)
            return f"""# Ultra Synthesis™ (Emergency Mode)

**Query:** {prompt[:200]}{'...' if len(prompt) > 200 else ''}

**Analysis Status:** Due to technical limitations with our synthesis engine, this response combines insights from {model_count} AI model(s) without the full Ultra Synthesis™ processing.

**Key Insights Available:**
The models provided substantial analysis that addresses your question. While we cannot perform the complete intelligence multiplication process at this time, the individual model responses contain valuable information.

**Recommendation:** For the complete Ultra Synthesis™ experience with advanced cross-model analysis and intelligence multiplication, please retry your request when all systems are fully operational.

*This is a degraded-mode response due to temporary service limitations.*"""
        else:
            return self._generate_initial_response_fallback(prompt, context)
    
    def _generate_generic_fallback(self, prompt: str, context: Dict[str, Any]) -> str:
        """Generate generic fallback response."""
        return f"""I apologize for the service interruption. Your request regarding "{prompt[:100]}{'...' if len(prompt) > 100 else ''}" could not be processed due to temporary technical difficulties.

Please try again in a few moments. Our AI systems are working to restore full functionality."""


# Global instance for use across the application
enhanced_error_handler = EnhancedErrorHandler()