import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from ultra_error_handling import ErrorTracker, handle_api_error, handle_validation_error


class UltraTestSuite:
    def __init__(self, error_tracker: ErrorTracker):
        self.error_tracker = error_tracker
        self.logger = logging.getLogger(__name__)
        self.test_results = []

    async def run_test(
        self, test_name: str, test_func: callable, *args, **kwargs
    ) -> Dict[str, Any]:
        """Run a single test and track its results."""
        start_time = datetime.now()
        try:
            result = await test_func(*args, **kwargs)
            status = "success"
            error = None
        except Exception as e:
            status = "failed"
            error = str(e)
            self.error_tracker.add_error(e, {"context": f"test_{test_name}"})
            result = None

        test_result = {
            "name": test_name,
            "status": status,
            "duration": (datetime.now() - start_time).total_seconds(),
            "error": error,
            "timestamp": start_time,
        }
        self.test_results.append(test_result)
        return test_result

    async def run_test_suite(self, tests: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Run a suite of tests and return comprehensive results."""
        suite_start = datetime.now()
        results = []

        for test in tests:
            result = await self.run_test(
                test["name"],
                test["func"],
                *test.get("args", []),
                **test.get("kwargs", {}),
            )
            results.append(result)

        return {
            "suite_duration": (datetime.now() - suite_start).total_seconds(),
            "total_tests": len(results),
            "successful_tests": len([r for r in results if r["status"] == "success"]),
            "failed_tests": len([r for r in results if r["status"] == "failed"]),
            "test_results": results,
        }

    def get_test_summary(self) -> Dict[str, Any]:
        """Get a summary of all test results."""
        return {
            "total_tests_run": len(self.test_results),
            "success_rate": (
                len([r for r in self.test_results if r["status"] == "success"])
                / len(self.test_results)
                if self.test_results
                else 0
            ),
            "average_duration": (
                sum(r["duration"] for r in self.test_results) / len(self.test_results)
                if self.test_results
                else 0
            ),
            "latest_results": self.test_results[-5:] if self.test_results else [],
        }


class UniversalTestPatterns:
    """Universal test patterns for common Ultra operations."""

    @staticmethod
    @handle_api_error
    @handle_validation_error
    async def test_api_connection(api_client: Any, test_prompt: str) -> bool:
        """Test API connection with a simple prompt."""
        try:
            response = await api_client.call_api(test_prompt)
            return bool(response)
        except Exception as e:
            raise Exception(f"API connection test failed: {str(e)}")

    @staticmethod
    @handle_validation_error
    async def test_data_processing(data: Any, processing_func: callable) -> bool:
        """Test data processing functionality."""
        try:
            result = await processing_func(data)
            return bool(result)
        except Exception as e:
            raise Exception(f"Data processing test failed: {str(e)}")

    @staticmethod
    @handle_validation_error
    async def test_visualization(
        data: Any, viz_func: callable, params: Dict[str, Any]
    ) -> bool:
        """Test visualization functionality."""
        try:
            result = await viz_func(data, params)
            return bool(result)
        except Exception as e:
            raise Exception(f"Visualization test failed: {str(e)}")

    @staticmethod
    @handle_validation_error
    async def test_rate_limiting(rate_limiter: Any, num_requests: int = 5) -> bool:
        """Test rate limiting functionality."""
        try:
            for _ in range(num_requests):
                await rate_limiter.acquire()
            return True
        except Exception as e:
            raise Exception(f"Rate limiting test failed: {str(e)}")

    @staticmethod
    @handle_validation_error
    async def test_error_handling(error_tracker: ErrorTracker) -> bool:
        """Test error tracking functionality."""
        try:
            test_error = Exception("Test error")
            error_tracker.add_error(test_error, {"context": "test"})
            summary = error_tracker.get_error_summary()
            return bool(summary and summary["total_errors"] > 0)
        except Exception as e:
            raise Exception(f"Error handling test failed: {str(e)}")
