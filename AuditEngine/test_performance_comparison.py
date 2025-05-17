"""
Performance comparison between serial and parallel discovery orchestrators
"""

import json
import time
from pathlib import Path

from discovery.orchestrator import DiscoveryOrchestrator
from discovery.orchestrator_parallel import ParallelDiscoveryOrchestrator


def test_serial_performance(repo_path: str):
    """Test serial orchestrator performance"""
    output_dir = Path(repo_path) / "test_results" / "serial"
    output_dir.mkdir(parents=True, exist_ok=True)

    print("Testing SERIAL orchestrator...")
    start_time = time.time()

    orchestrator = DiscoveryOrchestrator(repo_path, str(output_dir))
    results = orchestrator.run_discovery()

    end_time = time.time()
    duration = end_time - start_time

    print(f"Serial execution time: {duration:.2f} seconds")
    return duration, results


def test_parallel_performance(repo_path: str, workers: int = None):
    """Test parallel orchestrator performance"""
    output_dir = Path(repo_path) / "test_results" / "parallel"
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Testing PARALLEL orchestrator with {workers or 'auto'} workers...")
    start_time = time.time()

    orchestrator = ParallelDiscoveryOrchestrator(
        repo_path, str(output_dir), max_workers=workers
    )
    results = orchestrator.run_discovery()

    end_time = time.time()
    duration = end_time - start_time

    print(f"Parallel execution time: {duration:.2f} seconds")
    return duration, results


def compare_results(serial_results, parallel_results):
    """Verify that both approaches produce the same results"""
    # Compare key metrics
    serial_summary = serial_results.get("summary", {})
    parallel_summary = parallel_results.get("summary", {})

    print("\nResult Comparison:")
    print(
        f"Serial files found: {serial_summary.get('repository_overview', {}).get('total_files', 0)}"
    )
    print(
        f"Parallel files found: {parallel_summary.get('repository_overview', {}).get('total_files', 0)}"
    )

    print(
        f"Serial code lines: {serial_summary.get('key_metrics', {}).get('code_lines', 0)}"
    )
    print(
        f"Parallel code lines: {parallel_summary.get('key_metrics', {}).get('code_lines', 0)}"
    )

    # Check if results match
    results_match = (
        serial_summary.get("repository_overview", {}).get("total_files")
        == parallel_summary.get("repository_overview", {}).get("total_files")
    ) and (
        serial_summary.get("key_metrics", {}).get("code_lines")
        == parallel_summary.get("key_metrics", {}).get("code_lines")
    )

    print(f"\nResults match: {results_match}")
    return results_match


def main():
    """Run performance comparison"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Compare serial vs parallel discovery performance"
    )
    parser.add_argument("path", help="Repository path to analyze")
    parser.add_argument(
        "--workers", "-w", type=int, help="Number of parallel workers", default=None
    )

    args = parser.parse_args()

    print(f"Performance Comparison Test")
    print(f"Repository: {args.path}")
    print("=" * 50)

    # Test serial performance
    serial_duration, serial_results = test_serial_performance(args.path)

    print()

    # Test parallel performance
    parallel_duration, parallel_results = test_parallel_performance(
        args.path, args.workers
    )

    print("=" * 50)
    print("\nPerformance Summary:")
    print(f"Serial execution:   {serial_duration:.2f} seconds")
    print(f"Parallel execution: {parallel_duration:.2f} seconds")

    if serial_duration > 0:
        speedup = serial_duration / parallel_duration
        print(f"Speedup:            {speedup:.2f}x")
        print(f"Time saved:         {serial_duration - parallel_duration:.2f} seconds")
        print(
            f"Improvement:        {((serial_duration - parallel_duration) / serial_duration * 100):.1f}%"
        )

    # Verify results match
    compare_results(serial_results, parallel_results)


if __name__ == "__main__":
    main()
