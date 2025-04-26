import time
from datetime import datetime
from typing import Any, Dict, List

import psutil

# Initialize performance metrics
performance_metrics = {
    "start_time": datetime.now().isoformat(),
    "requests_processed": 0,
    "documents_processed": 0,
    "total_chunks_processed": 0,
    "total_processing_time": 0,
    "avg_processing_time": 0,
    "max_memory_usage": 0,
    "cache_hits": 0,
    "current_memory_usage_mb": psutil.Process().memory_info().rss / (1024 * 1024),
}

# Initialize metrics history
metrics_history = {
    "timestamps": [],
    "memory_usage": [],
    "requests_processed": [],
    "response_times": [],
}

# Initialize processing metrics
requests_processed = 0
processing_times: List[float] = []
start_time = time.time()


def update_metrics_history() -> None:
    """Update the metrics history with current values"""
    global metrics_history, performance_metrics

    # Update current memory usage
    current_memory = psutil.Process().memory_info().rss / (1024 * 1024)  # MB
    performance_metrics["current_memory_usage_mb"] = current_memory

    # Add current values to history
    metrics_history["timestamps"].append(datetime.now().isoformat())
    metrics_history["memory_usage"].append(current_memory)
    metrics_history["requests_processed"].append(
        performance_metrics["requests_processed"]
    )

    # Calculate average processing time if we have data
    if processing_times:
        performance_metrics["avg_processing_time"] = sum(processing_times) / len(
            processing_times
        )

    # Limit history size to prevent memory issues
    max_history = 100
    if len(metrics_history["timestamps"]) > max_history:
        for key in metrics_history:
            metrics_history[key] = metrics_history[key][-max_history:]


def get_current_metrics() -> Dict[str, Any]:
    """Get the current metrics for the API status endpoint"""
    return {
        "uptime_seconds": time.time() - start_time,
        "requests_processed": performance_metrics["requests_processed"],
        "avg_processing_time": performance_metrics["avg_processing_time"],
        "memory_usage_mb": performance_metrics["current_memory_usage_mb"],
        "cache_hits": performance_metrics["cache_hits"],
    }


def get_metrics_history() -> Dict[str, Any]:
    """Get the metrics history for the API history endpoint"""
    return metrics_history
