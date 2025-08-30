"""
Rate limiting service for the Ultra backend.

This module provides rate limiting functionality using Redis as the storage backend.
It implements different rate limits based on user subscription tier.
"""

import os
import time
from enum import Enum
from typing import Dict, Optional, Tuple

import redis
from fastapi import Request

from app.database.models.user import SubscriptionTier, User
from app.utils.logging import get_logger

# Set up logger
logger = get_logger("rate_limit_service", "logs/rate_limit.log")

# Redis configuration
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)

# Rate limit configuration
DEFAULT_WINDOW_SECONDS = 60  # 1 minute window


class RateLimitInterval(str, Enum):
    """Rate limit time intervals"""

    SECOND = "second"
    MINUTE = "minute"
    HOUR = "hour"
    DAY = "day"


class RateLimitTier:
    """Rate limit configuration for a subscription tier"""

    def __init__(
        self,
        tier: SubscriptionTier,
        general_limit: int,
        general_interval: RateLimitInterval,
        analyze_limit: int,
        analyze_interval: RateLimitInterval,
        document_limit: int,
        document_interval: RateLimitInterval,
    ):
        """
        Initialize rate limit tier configuration

        Args:
            tier: Subscription tier
            general_limit: General request limit
            general_interval: General request interval
            analyze_limit: Analyze endpoint limit
            analyze_interval: Analyze endpoint interval
            document_limit: Document endpoint limit
            document_interval: Document endpoint interval
        """
        self.tier = tier
        self.general_limit = general_limit
        self.general_interval = general_interval
        self.analyze_limit = analyze_limit
        self.analyze_interval = analyze_interval
        self.document_limit = document_limit
        self.document_interval = document_interval

    def get_window_seconds(self, interval: RateLimitInterval) -> int:
        """
        Get the window size in seconds based on the interval

        Args:
            interval: Rate limit interval

        Returns:
            Window size in seconds
        """
        if interval == RateLimitInterval.SECOND:
            return 1
        elif interval == RateLimitInterval.MINUTE:
            return 60
        elif interval == RateLimitInterval.HOUR:
            return 3600
        elif interval == RateLimitInterval.DAY:
            return 86400
        else:
            return DEFAULT_WINDOW_SECONDS


# Define rate limits for each subscription tier
TIER_LIMITS = {
    SubscriptionTier.FREE: RateLimitTier(
        tier=SubscriptionTier.FREE,
        general_limit=60,  # 60 requests per minute for general API
        general_interval=RateLimitInterval.MINUTE,
        analyze_limit=10,  # 10 requests per minute for /analyze
        analyze_interval=RateLimitInterval.MINUTE,
        document_limit=5,  # 5 requests per minute for document operations
        document_interval=RateLimitInterval.MINUTE,
    ),
    SubscriptionTier.BASIC: RateLimitTier(
        tier=SubscriptionTier.BASIC,
        general_limit=300,  # 300 requests per minute for general API
        general_interval=RateLimitInterval.MINUTE,
        analyze_limit=60,  # 60 requests per minute for /analyze
        analyze_interval=RateLimitInterval.MINUTE,
        document_limit=30,  # 30 requests per minute for document operations
        document_interval=RateLimitInterval.MINUTE,
    ),
    SubscriptionTier.PREMIUM: RateLimitTier(
        tier=SubscriptionTier.PREMIUM,
        general_limit=1000,  # 1000 requests per minute for general API
        general_interval=RateLimitInterval.MINUTE,
        analyze_limit=120,  # 120 requests per minute for /analyze
        analyze_interval=RateLimitInterval.MINUTE,
        document_limit=60,  # 60 requests per minute for document operations
        document_interval=RateLimitInterval.MINUTE,
    ),
    SubscriptionTier.ENTERPRISE: RateLimitTier(
        tier=SubscriptionTier.ENTERPRISE,
        general_limit=5000,  # 5000 requests per minute for general API
        general_interval=RateLimitInterval.MINUTE,
        analyze_limit=600,  # 600 requests per minute for /analyze (10 per second)
        analyze_interval=RateLimitInterval.MINUTE,
        document_limit=300,  # 300 requests per minute for document operations
        document_interval=RateLimitInterval.MINUTE,
    ),
}

# Default tier for unauthenticated requests
DEFAULT_TIER = SubscriptionTier.FREE


class RateLimitCategory(str, Enum):
    """Categories of rate limits"""

    GENERAL = "general"
    ANALYZE = "analyze"
    DOCUMENT = "document"


class RateLimitResult:
    """Result of a rate limit check"""

    def __init__(
        self,
        is_allowed: bool,
        limit: int,
        remaining: int,
        reset_at: int,
        retry_after: Optional[int] = None,
    ):
        """
        Initialize rate limit result

        Args:
            is_allowed: Whether the request is allowed
            limit: The maximum number of requests allowed
            remaining: The number of requests remaining
            reset_at: The time when the rate limit window resets (Unix timestamp)
            retry_after: Seconds to wait before retrying (if rate limited)
        """
        self.is_allowed = is_allowed
        self.limit = limit
        self.remaining = remaining
        self.reset_at = reset_at
        self.retry_after = retry_after


class RateLimitService:
    """Service for rate limiting API requests"""

    def __init__(self):
        """Initialize rate limit service with Redis connection"""
        try:
            self.redis = redis.Redis(
                host=REDIS_HOST,
                port=REDIS_PORT,
                db=REDIS_DB,
                password=REDIS_PASSWORD,
                decode_responses=True,
            )
            # Test connection
            self.redis.ping()
            logger.info("Connected to Redis for rate limiting")
        except redis.RedisError as e:
            logger.error(f"Error connecting to Redis: {str(e)}")
            logger.warning("Rate limiting will be disabled")
            self.redis = None

    def is_enabled(self) -> bool:
        """
        Check if rate limiting is enabled

        Returns:
            True if rate limiting is enabled, False otherwise
        """
        return self.redis is not None

    def categorize_request(self, request: Request) -> RateLimitCategory:
        """
        Categorize a request based on its path

        Args:
            request: FastAPI request object

        Returns:
            Rate limit category
        """
        path = request.url.path.lower()

        if "/api/analyze" in path:
            return RateLimitCategory.ANALYZE
        elif "/api/document" in path:
            return RateLimitCategory.DOCUMENT
        else:
            return RateLimitCategory.GENERAL

    def get_limit_for_category(
        self, tier: SubscriptionTier, category: RateLimitCategory
    ) -> Tuple[int, RateLimitInterval]:
        """
        Get the rate limit for a category and tier

        Args:
            tier: Subscription tier
            category: Rate limit category

        Returns:
            Tuple of (limit, interval)
        """
        tier_config = TIER_LIMITS.get(tier, TIER_LIMITS[DEFAULT_TIER])

        if category == RateLimitCategory.ANALYZE:
            return tier_config.analyze_limit, tier_config.analyze_interval
        elif category == RateLimitCategory.DOCUMENT:
            return tier_config.document_limit, tier_config.document_interval
        else:
            return tier_config.general_limit, tier_config.general_interval

    def get_client_identifier(
        self, request: Request, user: Optional[User] = None
    ) -> str:
        """
        Get a unique identifier for the client

        Args:
            request: FastAPI request object
            user: User object, if authenticated

        Returns:
            Client identifier string
        """
        # If user is authenticated, use user ID
        if user is not None:
            return f"user:{user.id}"

        # Otherwise, use IP address
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Get the first IP if multiple are provided
            ip = forwarded_for.split(",")[0].strip()
        else:
            ip = request.client.host if request.client else "unknown"

        return f"ip:{ip}"

    def build_key(
        self, identifier: str, category: RateLimitCategory, window_timestamp: int
    ) -> str:
        """
        Build a Redis key for rate limiting

        Args:
            identifier: Client identifier
            category: Rate limit category
            window_timestamp: Current window timestamp

        Returns:
            Redis key string
        """
        return f"ratelimit:{identifier}:{category}:{window_timestamp}"

    def check_rate_limit(
        self,
        request: Request,
        user: Optional[User] = None,
        override_category: Optional[RateLimitCategory] = None,
    ) -> RateLimitResult:
        """
        Check if a request is allowed based on rate limits

        Args:
            request: FastAPI request object
            user: Authenticated user, if any
            override_category: Override the auto-detected category

        Returns:
            RateLimitResult with limit details
        """
        # Determine tier based on user
        tier = user.subscription_tier if user else DEFAULT_TIER
        
        # Check for test tier override (only applies to unauthenticated requests)
        if user is None and os.getenv("TESTING") == "true" and os.getenv("TEST_RATE_LIMIT_TIER"):
            test_tier = os.getenv("TEST_RATE_LIMIT_TIER", "FREE").upper()
            if hasattr(SubscriptionTier, test_tier):
                tier = getattr(SubscriptionTier, test_tier)
        
        # Get the appropriate category
        category = override_category or self.categorize_request(request)
        
        # Get limit and interval for this tier and category
        limit, interval = self.get_limit_for_category(tier, category)
        
        # If rate limiting is disabled, return headers but always allow
        if not self.is_enabled():
            return RateLimitResult(
                is_allowed=True, 
                limit=limit, 
                remaining=limit, 
                reset_at=int(time.time()) + 60
            )

        window_seconds = TIER_LIMITS[tier].get_window_seconds(interval)

        # Calculate the current window timestamp
        current_time = int(time.time())
        window_timestamp = current_time - (current_time % window_seconds)
        reset_at = window_timestamp + window_seconds

        # Get a unique identifier for the client
        identifier = self.get_client_identifier(request, user)

        # Build the Redis key
        key = self.build_key(identifier, category, window_timestamp)

        try:
            # Increment the counter and get the current count
            current_count = self.redis.incr(key)

            # Set the expiry if this is a new key
            if current_count == 1:
                self.redis.expire(key, window_seconds * 2)  # 2x window to be safe

            # Check if the limit is exceeded
            is_allowed = current_count <= limit
            remaining = max(0, limit - current_count)

            # Calculate retry after time if rate limited
            retry_after = reset_at - current_time if not is_allowed else None

            return RateLimitResult(
                is_allowed=is_allowed,
                limit=limit,
                remaining=remaining,
                reset_at=reset_at,
                retry_after=retry_after,
            )

        except redis.RedisError as e:
            # Log error and allow the request in case of Redis failure
            logger.error(f"Redis error during rate limiting: {str(e)}")
            return RateLimitResult(
                is_allowed=True, limit=limit, remaining=limit, reset_at=reset_at
            )

    def add_rate_limit_headers(self, response: Dict, result: RateLimitResult) -> Dict:
        """
        Add rate limit headers to a response

        Args:
            response: Response dictionary
            result: Rate limit result

        Returns:
            Updated response dictionary with headers
        """
        headers = response.get("headers", {})

        # Add rate limit headers
        headers["X-RateLimit-Limit"] = str(result.limit)
        headers["X-RateLimit-Remaining"] = str(result.remaining)
        headers["X-RateLimit-Reset"] = str(result.reset_at)

        if not result.is_allowed and result.retry_after is not None:
            headers["Retry-After"] = str(result.retry_after)

        response["headers"] = headers
        return response


# Create a global instance
rate_limit_service = RateLimitService()
