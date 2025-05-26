"""
Performance Optimization Template for Ultra Project

This template provides ready-to-use patterns for common optimization scenarios.
"""

import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from functools import lru_cache
from multiprocessing import Pool, cpu_count

import psutil


class PerformanceOptimizer:
    """Universal performance optimization patterns"""

    def __init__(self, enable_profiling=False):
        self.enable_profiling = enable_profiling
        self.cpu_count = cpu_count()
        self.memory_available = psutil.virtual_memory().available

    def parallel_map(self, func, items, max_workers=None):
        """
        Parallel processing for CPU-bound tasks

        Example:
            optimizer = PerformanceOptimizer()
            results = optimizer.parallel_map(process_item, items)
        """
        workers = max_workers or min(self.cpu_count, len(items))

        # Skip parallelization for small datasets
        if len(items) < 10:
            return [func(item) for item in items]

        with Pool(processes=workers) as pool:
            return pool.map(func, items)

    def concurrent_io(self, func, items, max_workers=None):
        """
        Concurrent execution for I/O-bound tasks

        Example:
            results = optimizer.concurrent_io(fetch_url, urls)
        """
        workers = max_workers or min(32, len(items))  # More threads for I/O

        with ThreadPoolExecutor(max_workers=workers) as executor:
            return list(executor.map(func, items))

    @staticmethod
    def memoize(func):
        """
        Decorator for caching function results

        Example:
            @PerformanceOptimizer.memoize
            def expensive_calculation(x):
                return complex_math(x)
        """
        return lru_cache(maxsize=256)(func)

    def batch_process(self, func, items, batch_size=100):
        """
        Process items in batches to optimize memory usage

        Example:
            results = optimizer.batch_process(analyze_data, large_dataset)
        """
        results = []
        for i in range(0, len(items), batch_size):
            batch = items[i : i + batch_size]
            results.extend(func(batch))
        return results

    def profile_function(self, func, *args, **kwargs):
        """
        Profile a function's performance

        Example:
            result, stats = optimizer.profile_function(my_function, arg1, arg2)
        """
        if not self.enable_profiling:
            return func(*args, **kwargs), None

        import cProfile
        import io
        import pstats

        profiler = cProfile.Profile()
        profiler.enable()

        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB

        result = func(*args, **kwargs)

        end_time = time.time()
        end_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB

        profiler.disable()

        # Get profile stats
        s = io.StringIO()
        ps = pstats.Stats(profiler, stream=s)
        ps.sort_stats("cumulative")
        ps.print_stats(10)

        stats = {
            "duration": end_time - start_time,
            "memory_used": end_memory - start_memory,
            "profile": s.getvalue(),
        }

        return result, stats

    def auto_optimize(self, func, items, threshold=100):
        """
        Automatically choose optimization strategy based on data size

        Example:
            results = optimizer.auto_optimize(process_function, data_items)
        """
        item_count = len(items)

        # Small dataset: no optimization
        if item_count < threshold:
            return [func(item) for item in items]

        # Medium dataset: use threading for I/O
        if item_count < 1000:
            return self.concurrent_io(func, items)

        # Large dataset: use multiprocessing
        return self.parallel_map(func, items)


# Example Usage
if __name__ == "__main__":
    optimizer = PerformanceOptimizer(enable_profiling=True)

    # Example 1: Parallel processing
    def cpu_intensive_task(n):
        return sum(i**2 for i in range(n))

    numbers = [100000] * 20
    results = optimizer.parallel_map(cpu_intensive_task, numbers)
    print(f"Parallel results: {len(results)} items processed")

    # Example 2: Cached function
    @PerformanceOptimizer.memoize
    def fibonacci(n):
        if n < 2:
            return n
        return fibonacci(n - 1) + fibonacci(n - 2)

    result = fibonacci(35)
    print(f"Fibonacci(35) = {result}")

    # Example 3: Profiled execution
    result, stats = optimizer.profile_function(cpu_intensive_task, 1000000)
    if stats:
        print(f"Execution time: {stats['duration']:.3f} seconds")
        print(f"Memory used: {stats['memory_used']:.1f} MB")
