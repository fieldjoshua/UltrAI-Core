import asyncio
import logging
import time
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any, Dict, List, Optional

import psutil
from ultra_config import UltraConfig


class UltraMetrics:
    """Track and store performance metrics."""

    def __init__(self):
        self.metrics = {
            "api_calls": 0,
            "api_errors": 0,
            "processing_time": [],
            "memory_usage": [],
            "cpu_usage": [],
            "disk_usage": [],
            "timestamp": [],
        }

    def record_api_call(self, success: bool = True):
        """Record an API call."""
        self.metrics["api_calls"] += 1
        if not success:
            self.metrics["api_errors"] += 1

    def record_processing_time(self, duration: float):
        """Record processing time."""
        self.metrics["processing_time"].append(duration)
        self.metrics["timestamp"].append(datetime.now())

    def record_system_metrics(self):
        """Record current system metrics."""
        process = psutil.Process()
        self.metrics["memory_usage"].append(
            process.memory_info().rss / 1024 / 1024
        )  # MB
        self.metrics["cpu_usage"].append(process.cpu_percent())
        self.metrics["disk_usage"].append(psutil.disk_usage("/").percent)

    def get_summary(self) -> Dict[str, Any]:
        """Get summary of metrics."""
        return {
            "total_api_calls": self.metrics["api_calls"],
            "api_error_rate": (
                self.metrics["api_errors"] / self.metrics["api_calls"]
                if self.metrics["api_calls"] > 0
                else 0
            ),
            "avg_processing_time": (
                sum(self.metrics["processing_time"])
                / len(self.metrics["processing_time"])
                if self.metrics["processing_time"]
                else 0
            ),
            "current_memory_usage": (
                self.metrics["memory_usage"][-1] if self.metrics["memory_usage"] else 0
            ),
            "current_cpu_usage": (
                self.metrics["cpu_usage"][-1] if self.metrics["cpu_usage"] else 0
            ),
            "current_disk_usage": (
                self.metrics["disk_usage"][-1] if self.metrics["disk_usage"] else 0
            ),
        }


class UltraLogger:
    """Enhanced logging with metrics tracking."""

    def __init__(self, config: UltraConfig):
        self.config = config
        self.metrics = UltraMetrics()
        self.logger = self._setup_logger()

    def _setup_logger(self) -> logging.Logger:
        """Setup logging configuration."""
        logger = logging.getLogger("Ultra")
        logger.setLevel(getattr(logging, self.config.log_level))

        # Create formatters
        file_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        console_formatter = logging.Formatter("%(levelname)s: %(message)s")

        # File handler with rotation
        file_handler = RotatingFileHandler(
            self.config.log_file,
            maxBytes=self.config.max_log_size,
            backupCount=self.config.backup_count,
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

        return logger

    def log_api_call(self, endpoint: str, success: bool, duration: float):
        """Log API call details."""
        self.metrics.record_api_call(success)
        self.metrics.record_processing_time(duration)
        self.metrics.record_system_metrics()

        level = logging.INFO if success else logging.ERROR
        self.logger.log(
            level,
            f"API Call to {endpoint} - Duration: {duration:.2f}s - Status: {'Success' if success else 'Failed'}",
        )

    def log_data_processing(self, operation: str, data_size: int, duration: float):
        """Log data processing details."""
        self.metrics.record_processing_time(duration)
        self.metrics.record_system_metrics()

        self.logger.info(
            f"Data Processing: {operation} - Size: {data_size} bytes - Duration: {duration:.2f}s"
        )

    def log_error(self, error: Exception, context: Dict[str, Any]):
        """Log error details."""
        self.logger.error(f"Error: {str(error)} - Context: {context}")

    def log_warning(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Log warning message."""
        context_str = f" - Context: {context}" if context else ""
        self.logger.warning(f"Warning: {message}{context_str}")

    def log_info(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Log info message."""
        context_str = f" - Context: {context}" if context else ""
        self.logger.info(f"Info: {message}{context_str}")

    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of all metrics."""
        return self.metrics.get_summary()


class SystemMonitor:
    """Monitor system resources and performance."""

    def __init__(self, config: UltraConfig):
        self.config = config
        self.metrics = UltraMetrics()
        self.start_time = datetime.now()

    async def monitor_system(self):
        """Continuously monitor system resources."""
        while True:
            self.metrics.record_system_metrics()
            await asyncio.sleep(60)  # Check every minute

    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status."""
        return {
            "uptime": (datetime.now() - self.start_time).total_seconds(),
            "memory_usage": (
                self.metrics.metrics["memory_usage"][-1]
                if self.metrics.metrics["memory_usage"]
                else 0
            ),
            "cpu_usage": (
                self.metrics.metrics["cpu_usage"][-1]
                if self.metrics.metrics["cpu_usage"]
                else 0
            ),
            "disk_usage": (
                self.metrics.metrics["disk_usage"][-1]
                if self.metrics.metrics["disk_usage"]
                else 0
            ),
        }

    def check_system_health(self) -> bool:
        """Check if system is healthy."""
        try:
            # Check memory usage
            memory_usage = (
                self.metrics.metrics["memory_usage"][-1]
                if self.metrics.metrics["memory_usage"]
                else 0
            )
            if memory_usage > 90:  # 90% memory usage threshold
                return False

            # Check CPU usage
            cpu_usage = (
                self.metrics.metrics["cpu_usage"][-1]
                if self.metrics.metrics["cpu_usage"]
                else 0
            )
            if cpu_usage > 90:  # 90% CPU usage threshold
                return False

            # Check disk usage
            disk_usage = (
                self.metrics.metrics["disk_usage"][-1]
                if self.metrics.metrics["disk_usage"]
                else 0
            )
            if disk_usage > 90:  # 90% disk usage threshold
                return False

            return True
        except Exception:
            return False
