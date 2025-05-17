"""Async Test Helpers for Integration Testing"""

import asyncio
import time
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

import aiohttp


class AsyncAPIClient:
    """Async API client for integration testing"""

    def __init__(self, base_url: str = "http://localhost:8087/api"):
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None
        self.headers = {}

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    def set_auth_token(self, token: str):
        """Set authentication token"""
        self.headers["Authorization"] = f"Bearer {token}"

    def clear_auth(self):
        """Clear authentication"""
        self.headers.pop("Authorization", None)

    async def request(
        self, method: str, endpoint: str, **kwargs
    ) -> aiohttp.ClientResponse:
        """Make an async API request"""
        url = f"{self.base_url}{endpoint}"
        headers = {**self.headers, **kwargs.get("headers", {})}
        kwargs["headers"] = headers

        async with self.session.request(method, url, **kwargs) as response:
            return response

    async def get(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Async GET request"""
        response = await self.request("GET", endpoint, **kwargs)
        return await response.json()

    async def post(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Async POST request"""
        response = await self.request("POST", endpoint, **kwargs)
        return await response.json()

    async def put(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Async PUT request"""
        response = await self.request("PUT", endpoint, **kwargs)
        return await response.json()

    async def delete(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Async DELETE request"""
        response = await self.request("DELETE", endpoint, **kwargs)
        if response.status == 204:
            return {}
        return await response.json()


class ConcurrentTester:
    """Helper for concurrent testing scenarios"""

    def __init__(self, max_concurrent: int = 10):
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.results = []

    async def run_concurrent(
        self,
        func: Callable,
        args_list: List[tuple],
        progress_callback: Optional[Callable] = None,
    ):
        """Run function concurrently with arguments"""
        tasks = []
        for i, args in enumerate(args_list):
            task = self._run_with_semaphore(func, args, i, progress_callback)
            tasks.append(task)

        self.results = await asyncio.gather(*tasks, return_exceptions=True)
        return self.results

    async def _run_with_semaphore(
        self,
        func: Callable,
        args: tuple,
        index: int,
        progress_callback: Optional[Callable],
    ):
        """Run function with semaphore control"""
        async with self.semaphore:
            start_time = time.time()
            try:
                result = await func(*args)
                duration = time.time() - start_time
                success = True
            except Exception as e:
                result = e
                duration = time.time() - start_time
                success = False

            if progress_callback:
                await progress_callback(index, success, duration)

            return {
                "index": index,
                "success": success,
                "result": result,
                "duration": duration,
            }

    def get_summary(self) -> Dict[str, Any]:
        """Get summary of concurrent test results"""
        successful = [r for r in self.results if r["success"]]
        failed = [r for r in self.results if not r["success"]]

        durations = [r["duration"] for r in self.results]

        return {
            "total": len(self.results),
            "successful": len(successful),
            "failed": len(failed),
            "success_rate": len(successful) / len(self.results) if self.results else 0,
            "avg_duration": sum(durations) / len(durations) if durations else 0,
            "min_duration": min(durations) if durations else 0,
            "max_duration": max(durations) if durations else 0,
            "failures": [
                {"index": r["index"], "error": str(r["result"])} for r in failed
            ],
        }


class AsyncLoadTester:
    """Async load testing helper"""

    def __init__(self, client: AsyncAPIClient):
        self.client = client
        self.metrics = []

    async def ramp_up(
        self,
        endpoint: str,
        method: str = "GET",
        start_users: int = 1,
        end_users: int = 100,
        duration: int = 60,
        **kwargs,
    ):
        """Perform ramp-up load test"""
        start_time = time.time()
        current_users = start_users

        while time.time() - start_time < duration:
            # Calculate current user count based on linear ramp
            elapsed = time.time() - start_time
            progress = elapsed / duration
            current_users = int(start_users + (end_users - start_users) * progress)

            # Run concurrent requests
            tester = ConcurrentTester(max_concurrent=current_users)
            args_list = [(endpoint, method, kwargs) for _ in range(current_users)]

            await tester.run_concurrent(self._make_request, args_list)

            # Collect metrics
            self.metrics.append(
                {
                    "timestamp": datetime.utcnow().isoformat(),
                    "concurrent_users": current_users,
                    "results": tester.get_summary(),
                }
            )

            # Wait before next iteration
            await asyncio.sleep(1)

    async def sustained_load(
        self,
        endpoint: str,
        method: str = "GET",
        users: int = 50,
        duration: int = 300,
        requests_per_second: int = 10,
        **kwargs,
    ):
        """Perform sustained load test"""
        start_time = time.time()
        request_interval = 1.0 / requests_per_second

        while time.time() - start_time < duration:
            # Run batch of concurrent requests
            tester = ConcurrentTester(max_concurrent=users)
            args_list = [(endpoint, method, kwargs) for _ in range(users)]

            batch_start = time.time()
            await tester.run_concurrent(self._make_request, args_list)
            batch_duration = time.time() - batch_start

            # Collect metrics
            self.metrics.append(
                {
                    "timestamp": datetime.utcnow().isoformat(),
                    "concurrent_users": users,
                    "batch_duration": batch_duration,
                    "results": tester.get_summary(),
                }
            )

            # Rate limiting
            sleep_time = max(0, request_interval - batch_duration)
            await asyncio.sleep(sleep_time)

    async def _make_request(self, endpoint: str, method: str, kwargs: Dict):
        """Make a single request"""
        method_func = getattr(self.client, method.lower())
        return await method_func(endpoint, **kwargs)

    def get_report(self) -> Dict[str, Any]:
        """Generate load test report"""
        if not self.metrics:
            return {}

        # Aggregate metrics
        total_requests = sum(m["results"]["total"] for m in self.metrics)
        total_failures = sum(m["results"]["failed"] for m in self.metrics)

        response_times = []
        for metric in self.metrics:
            response_times.extend([r["duration"] for r in metric["results"]["results"]])

        return {
            "total_requests": total_requests,
            "total_failures": total_failures,
            "failure_rate": total_failures / total_requests if total_requests else 0,
            "avg_response_time": (
                sum(response_times) / len(response_times) if response_times else 0
            ),
            "min_response_time": min(response_times) if response_times else 0,
            "max_response_time": max(response_times) if response_times else 0,
            "p95_response_time": (
                sorted(response_times)[int(len(response_times) * 0.95)]
                if response_times
                else 0
            ),
            "p99_response_time": (
                sorted(response_times)[int(len(response_times) * 0.99)]
                if response_times
                else 0
            ),
            "timeline": self.metrics,
        }


class WebSocketTester:
    """WebSocket testing helper"""

    def __init__(self, ws_url: str = "ws://localhost:8087/ws"):
        self.ws_url = ws_url
        self.messages_received = []
        self.connected = False

    @asynccontextmanager
    async def connect(self):
        """Connect to WebSocket"""
        async with aiohttp.ClientSession() as session:
            async with session.ws_connect(self.ws_url) as ws:
                self.connected = True
                yield ws
                self.connected = False

    async def test_message_flow(self, messages: List[Dict], timeout: int = 30):
        """Test WebSocket message flow"""
        async with self.connect() as ws:
            # Send messages
            for message in messages:
                await ws.send_json(message)

            # Receive responses
            start_time = time.time()
            while time.time() - start_time < timeout:
                try:
                    msg = await asyncio.wait_for(ws.receive(), timeout=1.0)
                    if msg.type == aiohttp.WSMsgType.TEXT:
                        self.messages_received.append(msg.json())
                    elif msg.type == aiohttp.WSMsgType.ERROR:
                        break
                except asyncio.TimeoutError:
                    continue

            return self.messages_received


# Async pytest fixtures
@pytest.fixture
async def async_client():
    """Async API client fixture"""
    async with AsyncAPIClient() as client:
        yield client


@pytest.fixture
async def load_tester(async_client):
    """Load tester fixture"""
    tester = AsyncLoadTester(async_client)
    yield tester


@pytest.fixture
async def ws_tester():
    """WebSocket tester fixture"""
    tester = WebSocketTester()
    yield tester
