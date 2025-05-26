"""
Resource monitoring tests for minimal deployment.
Ensures the application stays within resource constraints during operation.
"""

import threading
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List

import psutil
import pytest
import requests


class ResourceMonitor:
    """Monitor resource usage during tests."""

    def __init__(self):
        self.monitoring = False
        self.max_memory_mb = 0
        self.max_cpu_percent = 0
        self.measurements: List[Dict[str, float]] = []

    def start_monitoring(self):
        """Start monitoring resources in background thread."""
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.start()

    def stop_monitoring(self):
        """Stop monitoring and return results."""
        self.monitoring = False
        self.monitor_thread.join()
        return {
            "max_memory_mb": self.max_memory_mb,
            "max_cpu_percent": self.max_cpu_percent,
            "measurements": self.measurements,
        }

    def _monitor_loop(self):
        """Background monitoring loop."""
        process = psutil.Process()

        while self.monitoring:
            memory_mb = process.memory_info().rss / 1024 / 1024
            cpu_percent = process.cpu_percent(interval=0.1)

            self.max_memory_mb = max(self.max_memory_mb, memory_mb)
            self.max_cpu_percent = max(self.max_cpu_percent, cpu_percent)

            self.measurements.append(
                {
                    "timestamp": time.time(),
                    "memory_mb": memory_mb,
                    "cpu_percent": cpu_percent,
                }
            )

            time.sleep(0.5)


@pytest.fixture
def resource_monitor():
    """Create resource monitor for tests."""
    return ResourceMonitor()


class TestResourceUsageUnderLoad:
    """Test resource usage under various load scenarios."""

    def test_startup_resources(self, resource_monitor):
        """Test resource usage during startup."""
        resource_monitor.start_monitoring()

        # Import and start the app
        from backend.app_minimal import app

        client = app.test_client()

        # Make initial health check
        response = client.get("/api/health")
        assert response.status_code == 200

        results = resource_monitor.stop_monitoring()

        # Verify startup memory usage
        assert (
            results["max_memory_mb"] < 256
        ), f"Startup memory {results['max_memory_mb']}MB exceeds 256MB limit"

        # Verify CPU usage
        assert (
            results["max_cpu_percent"] < 100
        ), f"Startup CPU {results['max_cpu_percent']}% indicates CPU bottleneck"

    def test_concurrent_requests(self, resource_monitor, client):
        """Test resource usage with concurrent requests."""
        resource_monitor.start_monitoring()

        def make_request(endpoint: str):
            return client.get(endpoint)

        # Simulate concurrent load
        endpoints = [
            "/api/health",
            "/api/available-models",
            "/api/orchestrator/patterns",
            "/api/llm/status",
        ] * 10  # 40 total requests

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [
                executor.submit(make_request, endpoint) for endpoint in endpoints
            ]

            # Wait for all requests to complete
            for future in futures:
                future.result()

        results = resource_monitor.stop_monitoring()

        # Verify memory under load
        assert (
            results["max_memory_mb"] < 512
        ), f"Memory under load {results['max_memory_mb']}MB exceeds 512MB limit"

        # Verify CPU usage
        assert (
            results["max_cpu_percent"] < 200
        ), f"CPU under load {results['max_cpu_percent']}% too high for 2 cores"

    def test_llm_request_resources(self, resource_monitor, client):
        """Test resource usage during LLM requests."""
        resource_monitor.start_monitoring()

        # Make an analysis request (using mock)
        analysis_data = {
            "prompt": "Test prompt for resource monitoring",
            "models": ["gpt-4", "claude-3"],
            "pattern": "summarize",
        }

        response = client.post("/analyze", json=analysis_data)

        # Wait for processing
        time.sleep(2)

        results = resource_monitor.stop_monitoring()

        # Verify memory during LLM operations
        assert (
            results["max_memory_mb"] < 512
        ), f"Memory during LLM {results['max_memory_mb']}MB exceeds 512MB limit"

    def test_document_upload_resources(self, resource_monitor, client):
        """Test resource usage during document upload."""
        resource_monitor.start_monitoring()

        # Create a test file
        test_content = b"Test content " * 1000  # ~13KB
        files = {"file": ("test.txt", test_content, "text/plain")}

        response = client.post("/api/upload-document", files=files)

        results = resource_monitor.stop_monitoring()

        # Verify memory during upload
        assert (
            results["max_memory_mb"] < 512
        ), f"Memory during upload {results['max_memory_mb']}MB exceeds 512MB limit"

    def test_sustained_load(self, resource_monitor, client):
        """Test resource usage under sustained load."""
        resource_monitor.start_monitoring()

        # Run requests for 30 seconds
        start_time = time.time()
        request_count = 0

        while time.time() - start_time < 30:
            response = client.get("/api/health")
            assert response.status_code == 200
            request_count += 1
            time.sleep(0.1)  # 10 requests per second

        results = resource_monitor.stop_monitoring()

        # Verify sustained operation doesn't leak memory
        assert (
            results["max_memory_mb"] < 512
        ), f"Memory during sustained load {results['max_memory_mb']}MB exceeds limit"

        # Check for memory growth
        memory_measurements = [m["memory_mb"] for m in results["measurements"]]
        memory_growth = memory_measurements[-1] - memory_measurements[0]
        assert (
            memory_growth < 50
        ), f"Memory grew by {memory_growth}MB during sustained load"

    def test_memory_cleanup(self, resource_monitor, client):
        """Test that memory is properly cleaned up after operations."""
        # Initial measurement
        initial_monitor = ResourceMonitor()
        initial_monitor.start_monitoring()
        time.sleep(1)
        initial_results = initial_monitor.stop_monitoring()
        initial_memory = initial_results["max_memory_mb"]

        # Perform heavy operations
        for i in range(10):
            # Upload and analyze documents
            files = {"file": (f"test{i}.txt", b"Content" * 1000, "text/plain")}
            client.post("/api/upload-document", files=files)

            client.post(
                "/analyze",
                json={
                    "prompt": f"Test {i}",
                    "models": ["gpt-4"],
                    "pattern": "summarize",
                },
            )

        # Force garbage collection
        import gc

        gc.collect()

        # Measure after cleanup
        cleanup_monitor = ResourceMonitor()
        cleanup_monitor.start_monitoring()
        time.sleep(1)
        cleanup_results = cleanup_monitor.stop_monitoring()
        final_memory = cleanup_results["max_memory_mb"]

        # Memory should return close to initial level
        memory_increase = final_memory - initial_memory
        assert (
            memory_increase < 50
        ), f"Memory increased by {memory_increase}MB after cleanup"


class TestStartupOptimization:
    """Test startup time and optimization."""

    def test_cold_start_time(self):
        """Test cold start time is under 30 seconds."""
        start_time = time.time()

        # Import and initialize app
        from backend.app_minimal import app

        client = app.test_client()

        # Make first request
        response = client.get("/api/health")
        assert response.status_code == 200

        startup_time = time.time() - start_time
        assert startup_time < 30, f"Cold start took {startup_time}s, expected < 30s"

    def test_import_optimization(self):
        """Test that heavy imports are deferred."""
        import sys

        # Clear any existing imports
        modules_to_check = [
            "tensorflow",
            "torch",
            "numpy",
            "pandas",
            "sklearn",
            "scipy",
            "matplotlib",
        ]

        for module in modules_to_check:
            if module in sys.modules:
                del sys.modules[module]

        # Import minimal app
        from backend.app_minimal import app

        # Check that heavy modules weren't imported
        for module in modules_to_check:
            assert (
                module not in sys.modules
            ), f"Heavy module {module} was imported during startup"

    def test_lazy_initialization(self):
        """Test that expensive operations are lazy-loaded."""
        from backend.app_minimal import app

        client = app.test_client()

        # Health check shouldn't initialize everything
        response = client.get("/api/health")
        assert response.status_code == 200

        # Check that LLM clients aren't initialized yet
        from backend.services import llm_config_service

        assert not hasattr(
            llm_config_service, "_initialized_clients"
        ), "LLM clients were initialized on startup"


class TestConnectionPooling:
    """Test connection pooling and limits."""

    def test_database_connection_pool(self):
        """Test database connection pooling limits."""
        from backend.database import get_db_engine

        engine = get_db_engine()
        pool = engine.pool

        # Verify pool configuration
        assert pool.size() <= 5, f"DB pool size {pool.size()} exceeds limit"
        assert (
            pool.overflow() <= 10
        ), f"DB pool overflow {pool.overflow()} exceeds limit"

    def test_redis_connection_limit(self):
        """Test Redis connection limits."""
        try:
            from backend.services.cache_service import get_redis_client

            redis_client = get_redis_client()

            if redis_client:
                pool = redis_client.connection_pool
                assert (
                    pool.max_connections <= 10
                ), f"Redis pool {pool.max_connections} exceeds limit"
        except ImportError:
            # Redis is optional in minimal deployment
            pass


# Performance benchmarks
class TestPerformanceBenchmarks:
    """Test performance benchmarks for minimal deployment."""

    def test_response_time_health_check(self, client):
        """Test health check response time."""
        times = []

        for _ in range(10):
            start = time.time()
            response = client.get("/api/health")
            end = time.time()

            assert response.status_code == 200
            times.append(end - start)

        avg_time = sum(times) / len(times)
        assert avg_time < 0.1, f"Average response time {avg_time}s exceeds 100ms"

    def test_response_time_under_load(self, client):
        """Test response times under concurrent load."""

        def timed_request():
            start = time.time()
            response = client.get("/api/health")
            end = time.time()
            return end - start if response.status_code == 200 else None

        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(timed_request) for _ in range(100)]
            times = [f.result() for f in futures if f.result() is not None]

        avg_time = sum(times) / len(times)
        assert (
            avg_time < 0.5
        ), f"Average response time under load {avg_time}s exceeds 500ms"

        # Check 95th percentile
        sorted_times = sorted(times)
        p95_time = sorted_times[int(len(sorted_times) * 0.95)]
        assert p95_time < 1.0, f"95th percentile response time {p95_time}s exceeds 1s"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
