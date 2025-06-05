"""
Resilient Client Module.

This module provides a resilient HTTP client with advanced reliability features
including circuit breakers, caching, retries, and timeouts.
"""

import asyncio
import json
import logging
import random
import time
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from urllib.parse import urlparse

import aiohttp
import backoff
from aiohttp import ClientError, ClientSession, ClientTimeout, TCPConnector

from backend.services.cache_service import cache_service
from backend.utils.logging import get_logger

# Try importing circuit breaker from various locations
try:
    from models.circuit_breaker import CircuitBreaker, CircuitBreakerRegistry
except ImportError:
    try:
        from backend.models.circuit_breaker import CircuitBreaker, CircuitBreakerRegistry
    except ImportError:
        # Provide stub implementations if circuit breaker is not available
        class CircuitBreaker:
            def __init__(self, *args, **kwargs):
                pass
            async def call(self, func):
                return await func()
        
        class CircuitBreakerRegistry:
            def get_breaker(self, name):
                return CircuitBreaker()

# Set up logger
logger = get_logger("resilient_client", "logs/http_client.log")

# Global circuit breaker registry
circuit_registry = CircuitBreakerRegistry()

# Default cache TTL
DEFAULT_CACHE_TTL = 60 * 60  # 1 hour


class ResilientClient:
    """
    Resilient HTTP client with circuit breaker, caching, and retry mechanisms.

    This client ensures reliability for external service calls by implementing:
    - Circuit breaker pattern to prevent cascading failures
    - Request retries with exponential backoff
    - Response caching for fault tolerance
    - Connection pooling for efficient resource usage
    - Configurable timeouts and timeout handling
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        circuit_name: Optional[str] = None,
        request_timeout: float = 30.0,
        connect_timeout: float = 10.0,
        pool_size: int = 10,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        retry_max_attempts: int = 3,
        retry_max_time: int = 30,
        cache_enabled: bool = True,
        cache_ttl: int = DEFAULT_CACHE_TTL,
        headers: Optional[Dict[str, str]] = None,
    ):
        """
        Initialize the resilient client.

        Args:
            base_url: Base URL for the service
            circuit_name: Name for the circuit breaker
            request_timeout: Request timeout in seconds
            connect_timeout: Connection timeout in seconds
            pool_size: Connection pool size
            failure_threshold: Circuit breaker failure threshold
            recovery_timeout: Circuit breaker recovery timeout in seconds
            retry_max_attempts: Maximum retry attempts
            retry_max_time: Maximum retry time in seconds
            cache_enabled: Whether to enable response caching
            cache_ttl: Cache TTL in seconds
            headers: Default headers for all requests
        """
        self.base_url = base_url
        self.domain = urlparse(base_url).netloc if base_url else "unknown"
        self.circuit_name = circuit_name or f"http:{self.domain}"
        self.request_timeout = request_timeout
        self.connect_timeout = connect_timeout
        self.pool_size = pool_size
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.retry_max_attempts = retry_max_attempts
        self.retry_max_time = retry_max_time
        self.cache_enabled = cache_enabled
        self.cache_ttl = cache_ttl
        self.default_headers = headers or {}

        # Create circuit breaker
        self.circuit = circuit_registry.get_or_create(
            self.circuit_name,
            failure_threshold=self.failure_threshold,
            recovery_timeout=self.recovery_timeout,
        )

        # Internal session
        self._session = None

        logger.info(f"Created resilient client for {self.domain}")

    async def _get_session(self) -> ClientSession:
        """
        Get an aiohttp session, creating it if necessary.

        Returns:
            An aiohttp ClientSession
        """
        if self._session is None or self._session.closed:
            # Create timeout configuration
            timeout = ClientTimeout(
                total=self.request_timeout,
                connect=self.connect_timeout,
                sock_connect=self.connect_timeout,
            )

            # Create connector with connection pooling
            connector = TCPConnector(
                limit=self.pool_size,
                force_close=False,  # Keep connections alive
                enable_cleanup_closed=True,
                ssl=False,  # Disable SSL verification for internal calls
            )

            # Create session
            self._session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers=self.default_headers,
                raise_for_status=False,  # Don't raise exceptions for HTTP errors
            )

        return self._session

    async def close(self) -> None:
        """Close the underlying HTTP session."""
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None

    def _get_cache_key(
        self, method: str, url: str, params: Optional[Dict] = None, data: Any = None
    ) -> str:
        """
        Generate a cache key for a request.

        Args:
            method: HTTP method
            url: Request URL
            params: Query parameters
            data: Request body

        Returns:
            Cache key string
        """
        import hashlib

        # Normalize and serialize parameters for consistent hashing
        params_str = json.dumps(params, sort_keys=True) if params else ""

        # Serialize data if it's a dict
        if isinstance(data, dict):
            data_str = json.dumps(data, sort_keys=True)
        elif data is not None:
            data_str = str(data)
        else:
            data_str = ""

        # Create composite key
        key_data = f"{method}:{url}:{params_str}:{data_str}"

        # Hash it
        return hashlib.md5(key_data.encode()).hexdigest()

    async def _get_cached_response(
        self, method: str, url: str, params: Optional[Dict] = None, data: Any = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get a cached response if available.

        Args:
            method: HTTP method
            url: Request URL
            params: Query parameters
            data: Request body

        Returns:
            Cached response or None
        """
        if not self.cache_enabled:
            return None

        try:
            cache_key = self._get_cache_key(method, url, params, data)
            cached = await cache_service.get_json("http", {"key": cache_key})

            if cached:
                logger.debug(f"Cache hit for {method} {url}")
                return cached
        except Exception as e:
            logger.warning(f"Error getting cached response: {e}")

        return None

    async def _cache_response(
        self,
        method: str,
        url: str,
        params: Optional[Dict],
        data: Any,
        response: Dict[str, Any],
    ) -> None:
        """
        Cache a response.

        Args:
            method: HTTP method
            url: Request URL
            params: Query parameters
            data: Request body
            response: Response to cache
        """
        if not self.cache_enabled:
            return

        try:
            cache_key = self._get_cache_key(method, url, params, data)
            await cache_service.set_json(
                "http", {"key": cache_key}, response, ttl=self.cache_ttl
            )
        except Exception as e:
            logger.warning(f"Error caching response: {e}")

    @backoff.on_exception(
        backoff.expo,
        (aiohttp.ClientError, asyncio.TimeoutError),
        max_tries=3,
        max_time=30,
        giveup=lambda e: isinstance(e, aiohttp.ClientResponseError)
        and e.status >= 400
        and e.status < 500,
    )
    async def request(
        self,
        method: str,
        url: str,
        params: Optional[Dict] = None,
        data: Any = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
        cache_ttl: Optional[int] = None,
        skip_cache: bool = False,
        skip_circuit_breaker: bool = False,
    ) -> Dict[str, Any]:
        """
        Send an HTTP request with resiliency features.

        Args:
            method: HTTP method (GET, POST, etc.)
            url: Request URL (relative to base_url if provided)
            params: Query parameters
            data: Request body
            headers: Request headers
            timeout: Request timeout in seconds
            cache_ttl: Cache TTL in seconds
            skip_cache: Whether to skip cache lookup
            skip_circuit_breaker: Whether to skip circuit breaker check

        Returns:
            Response data

        Raises:
            Exception: If the request fails after all retries
        """
        # Construct full URL if base_url is provided
        full_url = (
            f"{self.base_url.rstrip('/')}/{url.lstrip('/')}" if self.base_url else url
        )

        # Check circuit breaker
        if not skip_circuit_breaker and not self.circuit.allow_request():
            logger.warning(
                f"Circuit breaker open for {self.circuit_name}, request blocked"
            )
            raise ClientError(f"Circuit breaker open for {self.circuit_name}")

        # Check cache for GET requests
        if method.upper() == "GET" and not skip_cache:
            cached_response = await self._get_cached_response(
                method, full_url, params, data
            )
            if cached_response:
                return cached_response

        # Make the request
        try:
            session = await self._get_session()

            # Configure the timeout
            request_timeout = timeout or self.request_timeout

            # Merge headers
            merged_headers = {**self.default_headers}
            if headers:
                merged_headers.update(headers)

            # Send the request
            start_time = time.time()
            async with session.request(
                method=method,
                url=full_url,
                params=params,
                json=data if isinstance(data, dict) else None,
                data=data if not isinstance(data, dict) else None,
                headers=merged_headers,
                timeout=request_timeout,
                allow_redirects=True,
            ) as response:
                # Get response data
                is_json = response.headers.get("content-type", "").startswith(
                    "application/json"
                )

                if is_json:
                    response_data = await response.json()
                else:
                    response_text = await response.text()
                    response_data = {"text": response_text}

                # Add response metadata
                result = {
                    "status": response.status,
                    "headers": dict(response.headers),
                    "data": response_data,
                    "elapsed": time.time() - start_time,
                }

                # Check for errors
                if response.status >= 400:
                    logger.warning(
                        f"HTTP error {response.status} for {method} {full_url}"
                    )

                    # Record failure in circuit breaker for server errors
                    if response.status >= 500 and not skip_circuit_breaker:
                        self.circuit.record_failure()

                    # Include the error in the result
                    result["error"] = True
                    result["error_message"] = f"HTTP error {response.status}"
                else:
                    # Record success in circuit breaker
                    if not skip_circuit_breaker:
                        self.circuit.record_success()

                    # Cache successful GET responses
                    if method.upper() == "GET" and not skip_cache:
                        await self._cache_response(
                            method, full_url, params, data, result
                        )

                return result
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            # Record failure in circuit breaker
            if not skip_circuit_breaker:
                self.circuit.record_failure()

            logger.error(f"Request failed for {method} {full_url}: {e}")
            raise

    async def get(
        self,
        url: str,
        params: Optional[Dict] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
        cache_ttl: Optional[int] = None,
        skip_cache: bool = False,
        skip_circuit_breaker: bool = False,
    ) -> Dict[str, Any]:
        """
        Send a GET request.

        Args:
            url: Request URL
            params: Query parameters
            headers: Request headers
            timeout: Request timeout in seconds
            cache_ttl: Cache TTL in seconds
            skip_cache: Whether to skip cache lookup
            skip_circuit_breaker: Whether to skip circuit breaker check

        Returns:
            Response data
        """
        return await self.request(
            method="GET",
            url=url,
            params=params,
            headers=headers,
            timeout=timeout,
            cache_ttl=cache_ttl,
            skip_cache=skip_cache,
            skip_circuit_breaker=skip_circuit_breaker,
        )

    async def post(
        self,
        url: str,
        data: Any = None,
        params: Optional[Dict] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
        skip_circuit_breaker: bool = False,
    ) -> Dict[str, Any]:
        """
        Send a POST request.

        Args:
            url: Request URL
            data: Request body
            params: Query parameters
            headers: Request headers
            timeout: Request timeout in seconds
            skip_circuit_breaker: Whether to skip circuit breaker check

        Returns:
            Response data
        """
        return await self.request(
            method="POST",
            url=url,
            params=params,
            data=data,
            headers=headers,
            timeout=timeout,
            skip_cache=True,  # Always skip cache for POST
            skip_circuit_breaker=skip_circuit_breaker,
        )

    async def put(
        self,
        url: str,
        data: Any = None,
        params: Optional[Dict] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
        skip_circuit_breaker: bool = False,
    ) -> Dict[str, Any]:
        """
        Send a PUT request.

        Args:
            url: Request URL
            data: Request body
            params: Query parameters
            headers: Request headers
            timeout: Request timeout in seconds
            skip_circuit_breaker: Whether to skip circuit breaker check

        Returns:
            Response data
        """
        return await self.request(
            method="PUT",
            url=url,
            params=params,
            data=data,
            headers=headers,
            timeout=timeout,
            skip_cache=True,  # Always skip cache for PUT
            skip_circuit_breaker=skip_circuit_breaker,
        )

    async def delete(
        self,
        url: str,
        params: Optional[Dict] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
        skip_circuit_breaker: bool = False,
    ) -> Dict[str, Any]:
        """
        Send a DELETE request.

        Args:
            url: Request URL
            params: Query parameters
            headers: Request headers
            timeout: Request timeout in seconds
            skip_circuit_breaker: Whether to skip circuit breaker check

        Returns:
            Response data
        """
        return await self.request(
            method="DELETE",
            url=url,
            params=params,
            headers=headers,
            timeout=timeout,
            skip_cache=True,  # Always skip cache for DELETE
            skip_circuit_breaker=skip_circuit_breaker,
        )

    def get_circuit_status(self) -> Dict[str, str]:
        """
        Get the status of the circuit breaker.

        Returns:
            Circuit breaker status
        """
        return self.circuit.get_status()
