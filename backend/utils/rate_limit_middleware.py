"""
Rate limiting middleware for the Ultra backend.

This module provides rate limiting functionality for API endpoints.
"""

import time
from typing import Dict, Optional, Tuple
from fastapi import Request
from fastapi.responses import JSONResponse

from backend.utils.logging_config import rate_limit_logger

# Rate limit configuration
RATE_LIMIT_WINDOW = 60  # 1 minute window
RATE_LIMIT_MAX_REQUESTS = 100  # Maximum requests per window
RATE_LIMIT_BY_IP = True  # Whether to rate limit by IP
RATE_LIMIT_BY_USER = True  # Whether to rate limit by user

# Rate limit headers
RATE_LIMIT_HEADERS = {
    "X-RateLimit-Limit": "Maximum requests allowed",
    "X-RateLimit-Remaining": "Remaining requests",
    "X-RateLimit-Reset": "Time when the limit resets",
    "Retry-After": "Seconds to wait before retrying",
}

# Error messages
ERROR_MESSAGES = {
    "rate_limit_exceeded": "Rate limit exceeded. Please try again later.",
    "invalid_client": "Invalid client identifier",
    "invalid_user": "Invalid user identifier",
    "internal_error": "An internal error occurred",
}

# Store rate limit data
rate_limit_data: Dict[str, Dict[str, int]] = {
    "ip": {},  # IP-based rate limiting
    "user": {},  # User-based rate limiting
}


def get_client_identifier(request: Request) -> str:
    """
    Get a unique identifier for the client

    Args:
        request: FastAPI request

    Returns:
        Client identifier

    Raises:
        ValueError: If client identifier cannot be determined
    """
    if not RATE_LIMIT_BY_IP:
        return "default"

    if not request.client:
        rate_limit_logger.warning("No client information available")
        return "default"

    try:
        return request.client.host
    except Exception as e:
        rate_limit_logger.error(f"Error getting client identifier: {str(e)}")
        raise ValueError(ERROR_MESSAGES["invalid_client"])


def get_user_identifier(request: Request) -> Optional[str]:
    """
    Get a unique identifier for the user

    Args:
        request: FastAPI request

    Returns:
        User identifier if available

    Raises:
        ValueError: If user identifier is invalid
    """
    if not RATE_LIMIT_BY_USER:
        return None

    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return None

    try:
        scheme, token = auth_header.split()
        if scheme.lower() != "bearer":
            return None
        return token
    except Exception as e:
        rate_limit_logger.error(f"Error getting user identifier: {str(e)}")
        raise ValueError(ERROR_MESSAGES["invalid_user"])


def check_rate_limit(request: Request) -> Tuple[bool, Dict[str, int]]:
    """
    Check if the request exceeds rate limits

    Args:
        request: FastAPI request

    Returns:
        Tuple of (is_rate_limited, rate_limit_info)

    Raises:
        ValueError: If client or user identifier is invalid
    """
    current_time = int(time.time())
    window_start = current_time - RATE_LIMIT_WINDOW
    rate_limit_info = {
        "limit": RATE_LIMIT_MAX_REQUESTS,
        "remaining": RATE_LIMIT_MAX_REQUESTS,
        "reset": current_time + RATE_LIMIT_WINDOW,
    }

    try:
        # Check IP-based rate limit
        if RATE_LIMIT_BY_IP:
            client_id = get_client_identifier(request)
            if client_id not in rate_limit_data["ip"]:
                rate_limit_data["ip"][client_id] = 1
                rate_limit_info["remaining"] -= 1
                rate_limit_logger.debug(
                    f"New IP rate limit entry: {client_id}, "
                    f"remaining: {rate_limit_info['remaining']}"
                )
            else:
                # Clean up old entries
                rate_limit_data["ip"] = {
                    k: v for k, v in rate_limit_data["ip"].items() if v > window_start
                }
                rate_limit_data["ip"][client_id] = current_time
                rate_limit_info["remaining"] = RATE_LIMIT_MAX_REQUESTS - len(
                    rate_limit_data["ip"]
                )
                rate_limit_logger.debug(
                    f"Updated IP rate limit: {client_id}, "
                    f"remaining: {rate_limit_info['remaining']}"
                )

                # Check if limit is exceeded
                if len(rate_limit_data["ip"]) > RATE_LIMIT_MAX_REQUESTS:
                    rate_limit_logger.warning(
                        f"IP rate limit exceeded: {client_id}, "
                        f"limit: {RATE_LIMIT_MAX_REQUESTS}"
                    )
                    return True, rate_limit_info

        # Check user-based rate limit
        if RATE_LIMIT_BY_USER:
            user_id = get_user_identifier(request)
            if user_id:
                if user_id not in rate_limit_data["user"]:
                    rate_limit_data["user"][user_id] = 1
                    rate_limit_info["remaining"] -= 1
                    rate_limit_logger.debug(
                        f"New user rate limit entry: {user_id}, "
                        f"remaining: {rate_limit_info['remaining']}"
                    )
                else:
                    # Clean up old entries
                    rate_limit_data["user"] = {
                        k: v
                        for k, v in rate_limit_data["user"].items()
                        if v > window_start
                    }
                    rate_limit_data["user"][user_id] = current_time
                    rate_limit_info["remaining"] = min(
                        rate_limit_info["remaining"],
                        RATE_LIMIT_MAX_REQUESTS - len(rate_limit_data["user"]),
                    )
                    rate_limit_logger.debug(
                        f"Updated user rate limit: {user_id}, "
                        f"remaining: {rate_limit_info['remaining']}"
                    )

                    # Check if limit is exceeded
                    if len(rate_limit_data["user"]) > RATE_LIMIT_MAX_REQUESTS:
                        rate_limit_logger.warning(
                            f"User rate limit exceeded: {user_id}, "
                            f"limit: {RATE_LIMIT_MAX_REQUESTS}"
                        )
                        return True, rate_limit_info

        return False, rate_limit_info

    except ValueError as e:
        rate_limit_logger.error(f"Rate limit check failed: {str(e)}")
        raise
    except Exception as e:
        rate_limit_logger.error(f"Unexpected error in rate limit check: {str(e)}")
        raise ValueError(ERROR_MESSAGES["internal_error"])


async def rate_limit_middleware(request: Request, call_next):
    """
    Rate limiting middleware

    Args:
        request: FastAPI request
        call_next: Next middleware or route handler

    Returns:
        Response from next middleware or route handler
    """
    try:
        is_rate_limited, rate_limit_info = check_rate_limit(request)

        if is_rate_limited:
            rate_limit_logger.info(
                f"Rate limit exceeded for request: {request.url.path}, "
                f"client: {get_client_identifier(request)}, "
                f"user: {get_user_identifier(request)}"
            )
            response = JSONResponse(
                status_code=429,
                content={
                    "status": "error",
                    "message": ERROR_MESSAGES["rate_limit_exceeded"],
                    "limit": rate_limit_info["limit"],
                    "reset": rate_limit_info["reset"],
                },
            )
        else:
            response = await call_next(request)

        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(rate_limit_info["limit"])
        response.headers["X-RateLimit-Remaining"] = str(rate_limit_info["remaining"])
        response.headers["X-RateLimit-Reset"] = str(rate_limit_info["reset"])

        if is_rate_limited:
            response.headers["Retry-After"] = str(RATE_LIMIT_WINDOW)

        return response

    except ValueError as e:
        rate_limit_logger.error(f"Rate limit middleware error: {str(e)}")
        return JSONResponse(
            status_code=500, content={"status": "error", "message": str(e)}
        )
    except Exception as e:
        rate_limit_logger.error(f"Unexpected error in rate limit middleware: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": ERROR_MESSAGES["internal_error"]},
        )
