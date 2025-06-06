"""
Rate limiting service for the Ultra backend.

This module provides a service for enforcing rate limits based on IP address,
user ID, subscription tier, path, and method.
"""

import hashlib
import json
import os
import time
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import redis

from backend.database.models.user import User
from backend.utils.logging import get_logger

# Configure logging
logger = get_logger("rate_limit_service", "logs/rate_limit.log")

# Default rate limits by tier (requests per minute)
DEFAULT_RATE_LIMITS = {
    "anonymous": 60,  # Unauthenticated users
    "free": 100,  # Free tier users
    "basic": 300,  # Basic subscription
    "premium": 600,  # Premium subscription
    "enterprise": 1200,  # Enterprise subscription
    "internal": 0,  # Internal services (unlimited)
}

# Default rate limits by path pattern (overrides the default limits)
DEFAULT_PATH_LIMITS = {
    "/api/llm/": {
        "anonymous": 10,
        "free": 30,
        "basic": 100,
        "premium": 300,
        "enterprise": 1000,
    },
    "/api/document/": {
        "anonymous": 5,
        "free": 20,
        "basic": 50,
        "premium": 200,
        "enterprise": 500,
    },
    "/api/analyze/": {
        "anonymous": 5,
        "free": 15,
        "basic": 80,
        "premium": 250,
        "enterprise": 800,
    },
}

# Method weights - some methods cost more against the rate limit
METHOD_WEIGHTS = {
    "GET": 1,
    "OPTIONS": 0.5,
    "HEAD": 0.5,
    "POST": 2,
    "PUT": 2,
    "PATCH": 2,
    "DELETE": 2,
}

# Redis connection (optional, falls back to in-memory if not available)
REDIS_URL = os.getenv("REDIS_URL")
_redis_client = None


class RateLimitService:
    """Service for rate limiting requests based on IP address, user ID, subscription tier, path, and method"""

    def __init__(self):
        """Initialize the rate limit service"""
        self.in_memory_store = {
            "ip": {},  # IP-based rate limiting
            "user": {},  # User-based rate limiting
            "path": {},  # Path-based rate limiting
        }
        self.redis = self._get_redis_client()
        self.internal_service_tokens = {}  # token -> {service_name, expiry}
        self.bypass_keys = set()  # Special keys that bypass rate limits
        self.telemetry_enabled = True
        self.telemetry_sample_rate = (
            0.1  # Sample 10% of requests for detailed telemetry
        )

        # Load internal service tokens from environment or config
        self._load_internal_service_tokens()

        logger.info("Enhanced rate limit service initialized")

    def _load_internal_service_tokens(self):
        """Load internal service tokens from environment or configuration"""
        internal_tokens = os.getenv("INTERNAL_SERVICE_TOKENS", "")
        if internal_tokens:
            try:
                # Format: service1:token1,service2:token2
                for service_token in internal_tokens.split(","):
                    if ":" in service_token:
                        service, token = service_token.split(":", 1)
                        self.internal_service_tokens[token] = {
                            "service_name": service,
                            "expiry": None,  # No expiry for environment-defined tokens
                        }
                        logger.info(f"Loaded internal service token for: {service}")
            except Exception as e:
                logger.error(f"Error loading internal service tokens: {str(e)}")

    def _get_redis_client(self) -> Optional[redis.Redis]:
        """Get Redis client if available"""
        global _redis_client
        if _redis_client is not None:
            return _redis_client

        if REDIS_URL:
            try:
                _redis_client = redis.from_url(REDIS_URL)
                _redis_client.ping()  # Test connection
                logger.info("Connected to Redis for rate limiting")
                return _redis_client
            except Exception as e:
                logger.warning(f"Failed to connect to Redis: {str(e)}")
                logger.info("Falling back to in-memory rate limiting")
        return None

    def register_internal_service(
        self, service_name: str, secret_key: str, ttl_hours: int = 24
    ) -> str:
        """
        Register an internal service that bypasses rate limiting

        Args:
            service_name: Name of the internal service
            secret_key: Secret key for token generation
            ttl_hours: Time-to-live in hours (0 for no expiry)

        Returns:
            Token for the internal service
        """
        # Generate a unique token for this service
        token_base = f"{service_name}:{secret_key}:{uuid.uuid4().hex}"
        token = hashlib.sha256(token_base.encode()).hexdigest()

        # Calculate expiry time
        expiry = None
        if ttl_hours > 0:
            expiry = datetime.now() + timedelta(hours=ttl_hours)

        # Store the token
        self.internal_service_tokens[token] = {
            "service_name": service_name,
            "expiry": expiry.isoformat() if expiry else None,
            "created_at": datetime.now().isoformat(),
        }

        logger.info(f"Registered internal service: {service_name} (expires: {expiry})")

        return token

    def register_bypass_key(self, key: str, reason: str) -> None:
        """
        Register a key that should bypass rate limiting

        Args:
            key: Rate limit key to bypass
            reason: Reason for bypass
        """
        self.bypass_keys.add(key)
        logger.info(f"Registered rate limit bypass for key: {key} (reason: {reason})")

    def unregister_internal_service(self, token: str) -> bool:
        """
        Unregister an internal service

        Args:
            token: Token for the internal service

        Returns:
            True if token was found and removed
        """
        if token in self.internal_service_tokens:
            service_name = self.internal_service_tokens[token]["service_name"]
            del self.internal_service_tokens[token]
            logger.info(f"Unregistered internal service: {service_name}")
            return True
        return False

    def is_internal_service(self, token: str) -> bool:
        """
        Check if a request is from an internal service

        Args:
            token: Token from the request

        Returns:
            True if the request is from an internal service with a valid token
        """
        if token in self.internal_service_tokens:
            service_info = self.internal_service_tokens[token]

            # Check expiry
            if service_info["expiry"]:
                expiry_time = datetime.fromisoformat(service_info["expiry"])
                if datetime.now() > expiry_time:
                    # Token has expired, remove it
                    logger.warning(
                        f"Internal service token expired: {service_info['service_name']}"
                    )
                    del self.internal_service_tokens[token]
                    return False

            return True

        return False

    def get_rate_limit(
        self,
        user: Optional[User] = None,
        path: Optional[str] = None,
        method: Optional[str] = None,
        path_quota: Optional[int] = None,
    ) -> int:
        """
        Get the rate limit for a user based on their subscription tier, path, and method

        Args:
            user: User object (optional)
            path: Request path (optional)
            method: HTTP method (optional)
            path_quota: Override path-specific quota (optional)

        Returns:
            Rate limit value (requests per minute)
        """
        # Default tier is anonymous for unauthenticated users
        tier = "anonymous"

        # Get user's subscription tier if available
        if user:
            tier = getattr(user, "subscription_tier", "free")

        # Start with base rate limit for tier
        base_limit = DEFAULT_RATE_LIMITS.get(tier, DEFAULT_RATE_LIMITS["free"])

        # Check for path-specific rate limit
        if path and not path_quota:
            for pattern, limits in DEFAULT_PATH_LIMITS.items():
                if path.startswith(pattern):
                    if tier in limits:
                        path_quota = limits[tier]
                    break

        # Use path quota if specified
        limit = path_quota if path_quota is not None else base_limit

        # Apply method weight if method is specified
        if method and method in METHOD_WEIGHTS:
            weighted_limit = int(limit / METHOD_WEIGHTS[method])
            # Ensure rate limit is at least 1
            limit = max(1, weighted_limit)

        return limit

    def check_rate_limit(
        self,
        ip_address: str,
        user_id: Optional[str] = None,
        path: Optional[str] = None,
        method: Optional[str] = None,
        internal_token: Optional[str] = None,
        path_quota: Optional[int] = None,
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Check if a request exceeds rate limits

        Args:
            ip_address: Client IP address
            user_id: User ID (optional)
            path: Request path (optional)
            method: HTTP method (optional)
            internal_token: Internal service token (optional)
            path_quota: Override path-specific quota (optional)

        Returns:
            Tuple of (is_limited, rate_limit_info)
        """
        # Check if this is an internal service
        if internal_token and self.is_internal_service(internal_token):
            service_name = self.internal_service_tokens[internal_token]["service_name"]
            return False, {
                "limit": 0,  # Unlimited
                "remaining": 0,
                "reset": int(time.time()) + 60,
                "source": "internal_service",
                "service_name": service_name,
            }

        current_time = int(time.time())
        window_start = current_time - 60  # 1-minute window

        # Use user_id for rate limiting if available, otherwise use IP
        primary_key = f"user:{user_id}" if user_id else f"ip:{ip_address}"

        # Check if this key has a bypass
        if primary_key in self.bypass_keys:
            return False, {
                "limit": 0,  # Unlimited
                "remaining": 0,
                "reset": current_time + 60,
                "source": "bypass",
            }

        # Get appropriate rate limit based on user, path, and method
        # For now using None as user placeholder, in a real implementation we'd look up the user
        limit = self.get_rate_limit(None, path, method, path_quota)

        # Generate a request ID for tracking
        request_id = str(uuid.uuid4())

        # Use Redis for rate limiting if available
        if self.redis:
            return self._check_rate_limit_redis(
                primary_key, limit, current_time, path, method, request_id
            )
        else:
            return self._check_rate_limit_memory(
                primary_key, limit, current_time, window_start, path, method, request_id
            )

    def _check_rate_limit_redis(
        self,
        key: str,
        limit: int,
        current_time: int,
        path: Optional[str] = None,
        method: Optional[str] = None,
        request_id: Optional[str] = None,
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Check rate limit using Redis

        Args:
            key: Rate limit key
            limit: Rate limit value
            current_time: Current timestamp
            path: Request path (optional)
            method: HTTP method (optional)
            request_id: Request ID for tracking (optional)

        Returns:
            Tuple of (is_limited, rate_limit_info)
        """
        pipeline = self.redis.pipeline()

        # Add current request to sorted set with score = current timestamp
        pipeline.zadd(key, {str(current_time): current_time})

        # Remove entries older than the window
        pipeline.zremrangebyscore(key, 0, current_time - 60)

        # Count remaining entries
        pipeline.zcard(key)

        # Set key expiration (cleanup)
        pipeline.expire(key, 90)  # 1.5x window for safety

        # Execute pipeline
        _, _, count, _ = pipeline.execute()

        # Store telemetry if enabled and sampled
        if self.telemetry_enabled and path and method and request_id:
            if self.redis.random() < self.telemetry_sample_rate:
                telemetry_data = {
                    "request_id": request_id,
                    "timestamp": current_time,
                    "key": key,
                    "path": path,
                    "method": method,
                    "count": count,
                    "limit": limit,
                    "limited": count > limit,
                }

                # Store telemetry data for a short period
                telemetry_key = f"telemetry:{request_id}"
                self.redis.setex(
                    telemetry_key,
                    300,  # 5 minutes retention
                    json.dumps(telemetry_data),
                )

        # Add to path-specific counters if path is provided
        if path:
            path_key = f"path:{path}:{method if method else 'ALL'}"
            try:
                pipeline = self.redis.pipeline()
                pipeline.incr(path_key)
                pipeline.expire(path_key, 86400)  # 24 hours
                pipeline.execute()
            except Exception as e:
                logger.warning(f"Failed to update path counter: {str(e)}")

        # Check if limit is exceeded
        is_limited = count > limit

        return is_limited, {
            "limit": limit,
            "remaining": max(0, limit - count),
            "reset": current_time + 60,
            "request_id": request_id,
            "count": count,
        }

    def _check_rate_limit_memory(
        self,
        key: str,
        limit: int,
        current_time: int,
        window_start: int,
        path: Optional[str] = None,
        method: Optional[str] = None,
        request_id: Optional[str] = None,
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Check rate limit using in-memory storage

        Args:
            key: Rate limit key
            limit: Rate limit value
            current_time: Current timestamp
            window_start: Start of the rate limit window
            path: Request path (optional)
            method: HTTP method (optional)
            request_id: Request ID for tracking (optional)

        Returns:
            Tuple of (is_limited, rate_limit_info)
        """
        # Split key into type and identifier
        key_type, key_id = key.split(":", 1)

        # Initialize if not exists
        if key_id not in self.in_memory_store[key_type]:
            self.in_memory_store[key_type][key_id] = []

        # Add current request timestamp
        self.in_memory_store[key_type][key_id].append(current_time)

        # Remove timestamps outside the window
        self.in_memory_store[key_type][key_id] = [
            ts for ts in self.in_memory_store[key_type][key_id] if ts >= window_start
        ]

        # Count requests in window
        count = len(self.in_memory_store[key_type][key_id])

        # Track path-specific stats if provided
        if path:
            path_key = f"{path}:{method if method else 'ALL'}"
            if path_key not in self.in_memory_store["path"]:
                self.in_memory_store["path"][path_key] = 0
            self.in_memory_store["path"][path_key] += 1

        # Check if limit is exceeded
        is_limited = count > limit

        # Store telemetry if enabled and sampled
        if self.telemetry_enabled and path and method and request_id:
            import random

            if random.random() < self.telemetry_sample_rate:
                if not hasattr(self, "telemetry_store"):
                    self.telemetry_store = {}

                self.telemetry_store[request_id] = {
                    "request_id": request_id,
                    "timestamp": current_time,
                    "key": key,
                    "path": path,
                    "method": method,
                    "count": count,
                    "limit": limit,
                    "limited": is_limited,
                }

        return is_limited, {
            "limit": limit,
            "remaining": max(0, limit - count),
            "reset": current_time + 60,
            "request_id": request_id,
            "count": count,
        }

    def track_request(
        self,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        path: Optional[str] = None,
        method: Optional[str] = None,
        subscription_tier: Optional[str] = None,
    ) -> None:
        """
        Track a request for analytics purposes

        Args:
            user_id: User ID (optional)
            ip_address: Client IP address (optional)
            path: Request path (optional)
            method: HTTP method (optional)
            subscription_tier: User's subscription tier (optional)
        """
        current_time = int(time.time())
        day_key = datetime.fromtimestamp(current_time).strftime("%Y-%m-%d")

        # Track in Redis if available
        if self.redis:
            try:
                pipeline = self.redis.pipeline()

                # Track by user if available
                if user_id:
                    user_key = f"stats:user:{user_id}:{day_key}"
                    pipeline.hincrby(user_key, "requests", 1)
                    if path:
                        pipeline.hincrby(user_key, f"path:{path}", 1)
                    if method:
                        pipeline.hincrby(user_key, f"method:{method}", 1)
                    pipeline.expire(user_key, 86400 * 30)  # 30 days

                # Track by path if available
                if path:
                    path_key = f"stats:path:{path}:{day_key}"
                    pipeline.hincrby(path_key, "requests", 1)
                    if subscription_tier:
                        pipeline.hincrby(path_key, f"tier:{subscription_tier}", 1)
                    pipeline.expire(path_key, 86400 * 30)  # 30 days

                # Track by tier if available
                if subscription_tier:
                    tier_key = f"stats:tier:{subscription_tier}:{day_key}"
                    pipeline.hincrby(tier_key, "requests", 1)
                    pipeline.expire(tier_key, 86400 * 30)  # 30 days

                # Execute the pipeline
                pipeline.execute()
            except Exception as e:
                logger.error(f"Error tracking request in Redis: {str(e)}")
        else:
            # In-memory tracking is minimal to save memory
            pass  # We could implement simple in-memory tracking if needed

    def get_usage_report(
        self, user_id: Optional[str] = None, days: int = 7
    ) -> Dict[str, Dict[str, int]]:
        """
        Get usage report for a user

        Args:
            user_id: User ID (optional)
            days: Number of days to include in report

        Returns:
            Usage report
        """
        if not user_id:
            return {"error": "User ID required"}

        # Create time ranges for report
        now = int(time.time())
        day_seconds = 24 * 60 * 60
        ranges = {}

        for i in range(days):
            day_start = now - ((i + 1) * day_seconds)
            day_end = now - (i * day_seconds)
            date_str = datetime.fromtimestamp(day_start).strftime("%Y-%m-%d")
            ranges[date_str] = (day_start, day_end)

        report = {date: {"count": 0} for date in ranges.keys()}

        # Use Redis for report if available
        if self.redis:
            # Try new stats format first
            for date in ranges.keys():
                try:
                    user_key = f"stats:user:{user_id}:{date}"
                    if self.redis.exists(user_key):
                        report[date]["count"] = int(
                            self.redis.hget(user_key, "requests") or 0
                        )

                        # Add path breakdown if available
                        path_keys = [
                            k.decode("utf-8")
                            for k in self.redis.hkeys(user_key)
                            if k.decode("utf-8").startswith("path:")
                        ]
                        if path_keys:
                            report[date]["paths"] = {}
                            for path_key in path_keys:
                                path = path_key.split(":", 1)[1]
                                report[date]["paths"][path] = int(
                                    self.redis.hget(user_key, path_key) or 0
                                )

                        continue
                except Exception as e:
                    logger.warning(f"Error getting usage from Redis stats: {str(e)}")

            # Fall back to old format if needed
            key = f"user:{user_id}"
            for date, (start, end) in ranges.items():
                if (
                    report[date]["count"] == 0
                ):  # Only check old format if new format had no data
                    try:
                        count = self.redis.zcount(key, start, end)
                        report[date]["count"] = count
                    except Exception as e:
                        logger.error(f"Error getting usage from Redis: {str(e)}")
        else:
            # Use in-memory for report
            if user_id in self.in_memory_store["user"]:
                timestamps = self.in_memory_store["user"][user_id]

                for date, (start, end) in ranges.items():
                    report[date]["count"] = sum(
                        1 for ts in timestamps if start <= ts < end
                    )

        return report

    def get_path_usage_report(self, days: int = 1) -> Dict[str, Dict[str, int]]:
        """
        Get usage report by path

        Args:
            days: Number of days to include in report

        Returns:
            Usage report by path
        """
        report = {"paths": {}}

        # Use Redis for report if available
        if self.redis:
            try:
                # Get all path stats keys for the specified days
                now = datetime.now()
                path_keys = []

                for i in range(days):
                    date_str = (now - timedelta(days=i)).strftime("%Y-%m-%d")
                    keys = self.redis.keys(f"stats:path:*:{date_str}")
                    path_keys.extend([k.decode("utf-8") for k in keys])

                # Process each path key
                for path_key in path_keys:
                    # Extract path from key (stats:path:/api/llm/chat:2025-04-29)
                    parts = path_key.split(":")
                    if len(parts) >= 4:
                        path = parts[2]
                        if path not in report["paths"]:
                            report["paths"][path] = {"count": 0, "tiers": {}}

                        # Get request count
                        count = int(self.redis.hget(path_key, "requests") or 0)
                        report["paths"][path]["count"] += count

                        # Get tier breakdown
                        tier_keys = [
                            k.decode("utf-8")
                            for k in self.redis.hkeys(path_key)
                            if k.decode("utf-8").startswith("tier:")
                        ]
                        for tier_key in tier_keys:
                            tier = tier_key.split(":", 1)[1]
                            tier_count = int(self.redis.hget(path_key, tier_key) or 0)

                            if tier not in report["paths"][path]["tiers"]:
                                report["paths"][path]["tiers"][tier] = 0

                            report["paths"][path]["tiers"][tier] += tier_count
            except Exception as e:
                logger.error(f"Error getting path usage from Redis: {str(e)}")
        else:
            # Use in-memory for report
            for path_key, count in self.in_memory_store.get("path", {}).items():
                if ":" in path_key:
                    path = path_key.split(":", 1)[0]
                    if path not in report["paths"]:
                        report["paths"][path] = {"count": 0}
                    report["paths"][path]["count"] += count

        return report

    def clear_rate_limits(self, user_id: Optional[str] = None) -> None:
        """
        Clear rate limits for a user or all users

        Args:
            user_id: User ID (optional, clears all if None)
        """
        if self.redis:
            try:
                if user_id:
                    self.redis.delete(f"user:{user_id}")
                else:
                    # Clear all rate limits (use with caution)
                    keys = self.redis.keys("ip:*") + self.redis.keys("user:*")
                    if keys:
                        self.redis.delete(*keys)
                logger.info(
                    f"Cleared rate limits for {'all users' if user_id is None else user_id}"
                )
            except Exception as e:
                logger.error(f"Error clearing rate limits in Redis: {str(e)}")
        else:
            if user_id:
                if user_id in self.in_memory_store["user"]:
                    del self.in_memory_store["user"][user_id]
            else:
                self.in_memory_store = {"ip": {}, "user": {}, "path": {}}
            logger.info(
                f"Cleared rate limits for {'all users' if user_id is None else user_id}"
            )


# Create global instance
rate_limit_service = RateLimitService()
