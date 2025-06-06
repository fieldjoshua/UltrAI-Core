"""
Stub implementation of prometheus_client for when the real module is not installed.
This provides the minimum functionality to allow the application to start without errors.
"""

import logging
import time
from typing import Any, Callable, Dict, List, Optional, Union

logger = logging.getLogger(__name__)
logger.warning("Using stub prometheus_client module. Metrics will not be collected.")


# Registry for tracking metrics
class CollectorRegistry:
    def __init__(self, auto_describe=False):
        self._collectors = {}

    def register(self, collector):
        self._collectors[collector.name] = collector

    def unregister(self, collector):
        if collector.name in self._collectors:
            del self._collectors[collector.name]

    def collect(self):
        # Return empty iterable
        return []


# Global registry
REGISTRY = CollectorRegistry()


# Metric types
class Counter:
    def __init__(
        self,
        name,
        documentation,
        labelnames=(),
        namespace="",
        subsystem="",
        registry=None,
        **kwargs,
    ):
        self.name = name
        self.documentation = documentation
        self.labelnames = labelnames
        self.namespace = namespace
        self.subsystem = subsystem
        self._value = 0
        logger.debug(f"Created stub Counter: {name}")

        # Register with registry if provided
        if registry:
            registry.register(self)

    def inc(self, amount=1):
        self._value += amount

    def labels(self, *args, **kwargs):
        # Return a counter that does nothing
        return self

    def collect(self):
        return []


class Gauge:
    def __init__(
        self,
        name,
        documentation,
        labelnames=(),
        namespace="",
        subsystem="",
        registry=None,
        **kwargs,
    ):
        self.name = name
        self.documentation = documentation
        self.labelnames = labelnames
        self.namespace = namespace
        self.subsystem = subsystem
        self._value = 0
        logger.debug(f"Created stub Gauge: {name}")

        # Register with registry if provided
        if registry:
            registry.register(self)

    def inc(self, amount=1):
        self._value += amount

    def dec(self, amount=1):
        self._value -= amount

    def set(self, value):
        self._value = value

    def labels(self, *args, **kwargs):
        # Return a gauge that does nothing
        return self

    def collect(self):
        return []


class Histogram:
    def __init__(
        self,
        name,
        documentation,
        labelnames=(),
        buckets=(),
        namespace="",
        subsystem="",
        registry=None,
        **kwargs,
    ):
        self.name = name
        self.documentation = documentation
        self.labelnames = labelnames
        self.buckets = buckets or (
            0.005,
            0.01,
            0.025,
            0.05,
            0.1,
            0.25,
            0.5,
            1.0,
            2.5,
            5.0,
            10.0,
        )
        self.namespace = namespace
        self.subsystem = subsystem
        logger.debug(f"Created stub Histogram: {name}")

        # Register with registry if provided
        if registry:
            registry.register(self)

    def observe(self, amount):
        # Do nothing
        pass

    def labels(self, *args, **kwargs):
        # Return a histogram that does nothing
        return self

    def time(self):
        class Timer:
            def __enter__(self):
                self.start = time.time()
                return self

            def __exit__(self, exc_type, exc_val, exc_tb):
                # Do nothing with the elapsed time
                pass

        return Timer()

    def collect(self):
        return []


class Summary:
    def __init__(
        self,
        name,
        documentation,
        labelnames=(),
        namespace="",
        subsystem="",
        registry=None,
        **kwargs,
    ):
        self.name = name
        self.documentation = documentation
        self.labelnames = labelnames
        self.namespace = namespace
        self.subsystem = subsystem
        logger.debug(f"Created stub Summary: {name}")

        # Register with registry if provided
        if registry:
            registry.register(self)

    def observe(self, amount):
        # Do nothing
        pass

    def labels(self, *args, **kwargs):
        # Return a summary that does nothing
        return self

    def time(self):
        class Timer:
            def __enter__(self):
                self.start = time.time()
                return self

            def __exit__(self, exc_type, exc_val, exc_tb):
                # Do nothing with the elapsed time
                pass

        return Timer()

    def collect(self):
        return []


class Info:
    def __init__(
        self,
        name,
        documentation,
        labelnames=(),
        namespace="",
        subsystem="",
        registry=None,
        **kwargs,
    ):
        self.name = name
        self.documentation = documentation
        self.labelnames = labelnames
        self.namespace = namespace
        self.subsystem = subsystem
        self._value = {}
        logger.debug(f"Created stub Info: {name}")

        # Register with registry if provided
        if registry:
            registry.register(self)

    def info(self, value):
        self._value = value

    def labels(self, *args, **kwargs):
        # Return an info that does nothing
        return self

    def collect(self):
        return []


# HTTP exposition
CONTENT_TYPE_LATEST = "text/plain; version=0.0.4"


def generate_latest(registry=REGISTRY):
    """Generate an empty metrics response text"""
    return b"# Empty metrics (using stub prometheus_client)"


def start_http_server(port, addr="", registry=REGISTRY):
    """Stub for starting an HTTP server for metrics"""
    logger.warning(f"Stub prometheus_client: Not starting HTTP server on {addr}:{port}")


# Exposition module
class exposition:
    @staticmethod
    def choose_encoder(accept_header):
        """Return a no-op encoder"""

        def encoder(registry):
            return b"# Empty metrics (using stub prometheus_client)"

        return encoder
