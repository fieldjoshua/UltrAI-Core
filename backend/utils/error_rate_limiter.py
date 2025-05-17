"""Rate limiting for error responses.

This module provides rate limiting specifically for error responses
to prevent information leakage through timing attacks and to reduce
load during failure scenarios.
"""

import asyncio
import hashlib
import logging
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class ErrorRateLimitConfig:
    """Configuration for error rate limiting."""

    # Rate limit windows
    window_size: int = 60  # seconds
    max_errors_per_window: int = 50

    # Per-error-type limits
    error_type_limits: Dict[str, int] = field(
        default_factory=lambda: {
            "authentication": 5,  # Strict limit for auth errors
            "validation": 20,
            "server_error": 30,
            "timeout": 15,
            "rate_limit": 10,
        }
    )

    # Client-specific limits
    client_window_size: int = 300  # 5 minutes
    max_errors_per_client: int = 100

    # Progressive delay configuration
    enable_progressive_delay: bool = True
    min_delay: float = 0.0  # seconds
    max_delay: float = 5.0  # seconds
    delay_factor: float = 0.1  # Delay multiplier per error


class ErrorRateLimiter:
    """Rate limiter for error responses."""

    def __init__(self, config: ErrorRateLimitConfig):
        """Initialize error rate limiter."""
        self.config = config
        self.error_counts: Dict[str, Dict[float, int]] = defaultdict(
            lambda: defaultdict(int)
        )
        self.client_errors: Dict[str, Dict[float, int]] = defaultdict(
            lambda: defaultdict(int)
        )
        self.error_timestamps: Dict[str, list] = defaultdict(list)
        self._lock = asyncio.Lock()

    async def check_limit(
        self,
        error_type: str,
        client_id: Optional[str] = None,
        error_details: Optional[Dict[str, Any]] = None,
    ) -> Tuple[bool, Optional[float]]:
        """Check if error response should be rate limited.

        Returns:
            (should_limit, delay_seconds)
        """
        async with self._lock:
            current_time = time.time()

            # Check global error rate limit
            if await self._check_global_limit(error_type, current_time):
                delay = self._calculate_delay(error_type, client_id)
                return True, delay

            # Check client-specific limit
            if client_id and await self._check_client_limit(client_id, current_time):
                delay = self._calculate_delay(error_type, client_id)
                return True, delay

            # Check error-type specific limit
            if await self._check_error_type_limit(error_type, current_time):
                delay = self._calculate_delay(error_type, client_id)
                return True, delay

            # Record the error
            await self._record_error(error_type, client_id, current_time)

            return False, None

    async def _check_global_limit(self, error_type: str, current_time: float) -> bool:
        """Check global error rate limit."""
        window_start = current_time - self.config.window_size

        # Clean old entries
        self._clean_old_entries(self.error_counts[error_type], window_start)

        # Count errors in current window
        total_errors = sum(self.error_counts[error_type].values())

        return total_errors >= self.config.max_errors_per_window

    async def _check_client_limit(self, client_id: str, current_time: float) -> bool:
        """Check client-specific error rate limit."""
        if not client_id:
            return False

        window_start = current_time - self.config.client_window_size

        # Clean old entries
        self._clean_old_entries(self.client_errors[client_id], window_start)

        # Count client errors in window
        client_error_count = sum(self.client_errors[client_id].values())

        return client_error_count >= self.config.max_errors_per_client

    async def _check_error_type_limit(
        self, error_type: str, current_time: float
    ) -> bool:
        """Check error-type specific rate limit."""
        # Map error type to category
        error_category = self._get_error_category(error_type)

        if error_category not in self.config.error_type_limits:
            return False

        limit = self.config.error_type_limits[error_category]
        window_start = current_time - self.config.window_size

        # Count errors of this type
        type_errors = 0
        for timestamp, count in self.error_counts[error_type].items():
            if timestamp >= window_start:
                type_errors += count

        return type_errors >= limit

    async def _record_error(
        self, error_type: str, client_id: Optional[str], current_time: float
    ):
        """Record an error occurrence."""
        # Record in global counts
        self.error_counts[error_type][current_time] += 1

        # Record in client counts
        if client_id:
            self.client_errors[client_id][current_time] += 1

        # Record timestamp for pattern analysis
        self.error_timestamps[error_type].append(current_time)

        # Keep timestamp list manageable
        if len(self.error_timestamps[error_type]) > 1000:
            self.error_timestamps[error_type] = self.error_timestamps[error_type][
                -1000:
            ]

    def _calculate_delay(self, error_type: str, client_id: Optional[str]) -> float:
        """Calculate delay for rate-limited response."""
        if not self.config.enable_progressive_delay:
            return self.config.min_delay

        # Calculate delay based on error frequency
        recent_errors = self._count_recent_errors(error_type, client_id)

        delay = self.config.min_delay + (recent_errors * self.config.delay_factor)
        delay = min(delay, self.config.max_delay)

        # Add jitter to prevent synchronized retries
        jitter = delay * 0.1 * (2 * time.time() % 1 - 1)

        return max(0, delay + jitter)

    def _count_recent_errors(
        self, error_type: str, client_id: Optional[str], window: float = 60.0
    ) -> int:
        """Count recent errors for progressive delay calculation."""
        current_time = time.time()
        window_start = current_time - window

        count = 0

        # Count global errors
        for timestamp, error_count in self.error_counts[error_type].items():
            if timestamp >= window_start:
                count += error_count

        # Count client errors
        if client_id:
            for timestamp, error_count in self.client_errors[client_id].items():
                if timestamp >= window_start:
                    count += error_count

        return count

    def _get_error_category(self, error_type: str) -> str:
        """Map error type to category for rate limiting."""
        # Map common error types to categories
        if error_type.startswith("AUTH_"):
            return "authentication"
        elif error_type.startswith("VAL_"):
            return "validation"
        elif error_type.startswith("TIMEOUT_"):
            return "timeout"
        elif error_type.startswith("RATE_"):
            return "rate_limit"
        elif error_type.startswith("SRV_"):
            return "server_error"
        else:
            return "other"

    def _clean_old_entries(self, counts: Dict[float, int], window_start: float):
        """Remove entries older than the window start."""
        old_timestamps = [ts for ts in counts.keys() if ts < window_start]
        for ts in old_timestamps:
            del counts[ts]

    def get_stats(self) -> Dict[str, Any]:
        """Get rate limiting statistics."""
        current_time = time.time()

        stats = {
            "current_time": current_time,
            "error_types": {},
            "top_clients": [],
            "rate_limit_triggers": self._get_rate_limit_triggers(),
        }

        # Error type statistics
        for error_type, timestamps in self.error_timestamps.items():
            recent_count = sum(1 for ts in timestamps if ts >= current_time - 300)
            stats["error_types"][error_type] = {
                "total_count": len(timestamps),
                "recent_count": recent_count,
                "rate": recent_count / 5,  # per minute
            }

        # Top clients by error count
        client_totals = []
        for client_id, counts in self.client_errors.items():
            total = sum(counts.values())
            if total > 0:
                client_totals.append((client_id, total))

        client_totals.sort(key=lambda x: x[1], reverse=True)
        stats["top_clients"] = [
            {"client_id": client_id, "error_count": count}
            for client_id, count in client_totals[:10]
        ]

        return stats

    def _get_rate_limit_triggers(self) -> Dict[str, int]:
        """Get count of rate limit triggers by type."""
        # This would need to be tracked separately
        # For now, return empty dict
        return {}


class DistributedErrorRateLimiter(ErrorRateLimiter):
    """Distributed error rate limiter using shared storage."""

    def __init__(self, config: ErrorRateLimitConfig, redis_client=None):
        """Initialize distributed rate limiter."""
        super().__init__(config)
        self.redis = redis_client
        self.key_prefix = "error_rate_limit:"

    async def check_limit(
        self,
        error_type: str,
        client_id: Optional[str] = None,
        error_details: Optional[Dict[str, Any]] = None,
    ) -> Tuple[bool, Optional[float]]:
        """Check rate limit using distributed storage."""
        if not self.redis:
            # Fallback to local implementation
            return await super().check_limit(error_type, client_id, error_details)

        current_time = time.time()

        # Use Redis for distributed counting
        pipe = self.redis.pipeline()

        # Global error count
        global_key = f"{self.key_prefix}global:{error_type}"
        pipe.zadd(global_key, {str(current_time): current_time})
        pipe.zremrangebyscore(global_key, 0, current_time - self.config.window_size)
        pipe.zcard(global_key)

        # Client error count
        if client_id:
            client_key = f"{self.key_prefix}client:{client_id}"
            pipe.zadd(client_key, {str(current_time): current_time})
            pipe.zremrangebyscore(
                client_key, 0, current_time - self.config.client_window_size
            )
            pipe.zcard(client_key)

        results = await pipe.execute()

        # Check limits
        global_count = results[2]
        if global_count >= self.config.max_errors_per_window:
            delay = self._calculate_delay(error_type, client_id)
            return True, delay

        if client_id:
            client_count = results[5]
            if client_count >= self.config.max_errors_per_client:
                delay = self._calculate_delay(error_type, client_id)
                return True, delay

        return False, None


class SmartErrorRateLimiter(ErrorRateLimiter):
    """Enhanced rate limiter with pattern detection."""

    def __init__(self, config: ErrorRateLimitConfig):
        """Initialize smart rate limiter."""
        super().__init__(config)
        self.patterns: Dict[str, Dict[str, Any]] = {}
        self.suspicious_clients: set = set()

    async def check_limit(
        self,
        error_type: str,
        client_id: Optional[str] = None,
        error_details: Optional[Dict[str, Any]] = None,
    ) -> Tuple[bool, Optional[float]]:
        """Check rate limit with pattern detection."""
        # Check if client is suspicious
        if client_id and client_id in self.suspicious_clients:
            # Apply stricter limits
            return True, self.config.max_delay

        # Regular rate limit check
        should_limit, delay = await super().check_limit(
            error_type, client_id, error_details
        )

        # Analyze patterns
        if error_details:
            await self._analyze_pattern(error_type, client_id, error_details)

        return should_limit, delay

    async def _analyze_pattern(
        self, error_type: str, client_id: Optional[str], error_details: Dict[str, Any]
    ):
        """Analyze error patterns for suspicious activity."""
        pattern_key = f"{error_type}:{client_id or 'unknown'}"

        if pattern_key not in self.patterns:
            self.patterns[pattern_key] = {
                "error_sequence": [],
                "timing_pattern": [],
                "suspicious_score": 0,
            }

        pattern = self.patterns[pattern_key]
        current_time = time.time()

        # Record error in sequence
        pattern["error_sequence"].append(
            {"time": current_time, "details": error_details}
        )

        # Keep sequence manageable
        if len(pattern["error_sequence"]) > 100:
            pattern["error_sequence"] = pattern["error_sequence"][-100:]

        # Analyze timing patterns
        if len(pattern["error_sequence"]) > 1:
            time_diff = current_time - pattern["error_sequence"][-2]["time"]
            pattern["timing_pattern"].append(time_diff)

            # Check for automated patterns
            if self._is_automated_pattern(pattern["timing_pattern"]):
                pattern["suspicious_score"] += 1

        # Check for credential stuffing patterns
        if error_type.startswith("AUTH_") and self._is_credential_stuffing(pattern):
            pattern["suspicious_score"] += 5

        # Mark client as suspicious if score is high
        if client_id and pattern["suspicious_score"] > 10:
            self.suspicious_clients.add(client_id)
            logger.warning(f"Client {client_id} marked as suspicious")

    def _is_automated_pattern(self, timing_pattern: list) -> bool:
        """Detect automated request patterns."""
        if len(timing_pattern) < 5:
            return False

        # Check for consistent timing (bot-like behavior)
        recent_timings = timing_pattern[-10:]
        avg_timing = sum(recent_timings) / len(recent_timings)

        # Calculate variance
        variance = sum((t - avg_timing) ** 2 for t in recent_timings) / len(
            recent_timings
        )

        # Low variance indicates automated behavior
        return variance < 0.1 and avg_timing < 2.0

    def _is_credential_stuffing(self, pattern: Dict[str, Any]) -> bool:
        """Detect credential stuffing patterns."""
        auth_errors = [
            e
            for e in pattern["error_sequence"]
            if e["details"].get("error_code", "").startswith("AUTH_")
        ]

        if len(auth_errors) < 5:
            return False

        # Check for different usernames with same client
        usernames = set()
        for error in auth_errors[-20:]:
            username = error["details"].get("username")
            if username:
                usernames.add(username)

        # Multiple usernames from same client indicates stuffing
        return len(usernames) > 5

    def get_suspicious_clients(self) -> list:
        """Get list of suspicious clients."""
        return list(self.suspicious_clients)

    def clear_suspicious_client(self, client_id: str):
        """Remove client from suspicious list."""
        self.suspicious_clients.discard(client_id)
