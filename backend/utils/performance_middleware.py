"""
Performance monitoring middleware for the Ultra backend.

This module provides performance monitoring functionality for API endpoints.
"""

import time
from typing import Dict, Any
from fastapi import Request
from fastapi.responses import Response

# Performance thresholds (in seconds)
THRESHOLD_WARNING = 1.0
THRESHOLD_ERROR = 3.0


class PerformanceMetrics:
    """Performance metrics storage and analysis."""

    def __init__(self):
        self.metrics: Dict[str, Dict[str, Any]] = {}

    def record_request(self, path: str, method: str, duration: float):
        """Record a request's performance metrics."""
        if path not in self.metrics:
            self.metrics[path] = {
                "total_requests": 0,
                "total_duration": 0.0,
                "methods": {},
            }

        self.metrics[path]["total_requests"] += 1
        self.metrics[path]["total_duration"] += duration

        if method not in self.metrics[path]["methods"]:
            self.metrics[path]["methods"][method] = {"count": 0, "total_duration": 0.0}

        self.metrics[path]["methods"][method]["count"] += 1
        self.metrics[path]["methods"][method]["total_duration"] += duration

    def get_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Get all recorded metrics."""
        return self.metrics

    def get_path_metrics(self, path: str) -> Dict[str, Any]:
        """Get metrics for a specific path."""
        return self.metrics.get(path, {})

    def get_method_metrics(self, path: str, method: str) -> Dict[str, Any]:
        """Get metrics for a specific path and method."""
        return self.metrics.get(path, {}).get("methods", {}).get(method, {})


# Global metrics instance
metrics = PerformanceMetrics()


class PerformanceMiddleware:
    """Middleware for tracking API performance metrics."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, request: Request, call_next) -> Response:
        start_time = time.time()

        # Process the request
        response = await call_next(request)

        # Calculate duration
        duration = time.time() - start_time

        # Record metrics
        metrics.record_request(
            path=request.url.path, method=request.method, duration=duration
        )

        return response


def get_performance_metrics() -> Dict[str, Dict[str, float]]:
    """
    Get current performance metrics

    Returns:
        Performance metrics
    """
    return metrics.get_metrics()
