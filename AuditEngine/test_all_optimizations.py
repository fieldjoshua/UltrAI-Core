"""
Comprehensive performance test for all optimization techniques
"""

import cProfile
import io
import json
import pstats
import time
from pathlib import Path

from discovery.metrics_collector import MetricsCollector
from discovery.metrics_collector_optimized import OptimizedMetricsCollector
from discovery.orchestrator import DiscoveryOrchestrator
from discovery.orchestrator_parallel import ParallelDiscoveryOrchestrator


def profile_function(func, *args, **kwargs):
    """Profile a function and return timing and profile stats"""
    profiler = cProfile.Profile()

    start_time = time.time()
    profiler.enable()
    result = func(*args, **kwargs)
    profiler.disable()
    end_time = time.time()

    # Get profile stats
    s = io.StringIO()
    ps = pstats.Stats(profiler, stream=s)
    ps.sort_stats("cumulative")
    ps.print_stats(10)  # Top 10 functions

    return {
        "duration": end_time - start_time,
        "result": result,
        "profile": s.getvalue(),
    }


def test_serial_orchestrator(repo_path: str):
    """Test original serial orchestrator"""
    print("\n1. Testing SERIAL orchestrator...")
    output_dir = Path(repo_path) / "test_results" / "serial"
    output_dir.mkdir(parents=True, exist_ok=True)

    orchestrator = DiscoveryOrchestrator(repo_path, str(output_dir))
    return profile_function(orchestrator.run_discovery)


def test_parallel_orchestrator(repo_path: str):
    """Test parallel orchestrator"""
    print("\n2. Testing PARALLEL orchestrator...")
    output_dir = Path(repo_path) / "test_results" / "parallel"
    output_dir.mkdir(parents=True, exist_ok=True)

    orchestrator = ParallelDiscoveryOrchestrator(repo_path, str(output_dir))
    return profile_function(orchestrator.run_discovery)


def test_metrics_collector_original(repo_path: str):
    """Test original metrics collector"""
    print("\n3. Testing ORIGINAL metrics collector...")
    collector = MetricsCollector(repo_path)
    return profile_function(collector.collect)


def test_metrics_collector_optimized(repo_path: str):
    """Test optimized metrics collector with NumPy/Numba"""
    print("\n4. Testing OPTIMIZED metrics collector...")
    collector = OptimizedMetricsCollector(repo_path)
    return profile_function(collector.collect)


def analyze_results(results):
    """Analyze and display performance results"""
    print("\n" + "=" * 60)
    print("PERFORMANCE ANALYSIS SUMMARY")
    print("=" * 60)

    # Extract metrics
    serial_time = results["serial_orchestrator"]["duration"]
    parallel_time = results["parallel_orchestrator"]["duration"]
    metrics_original_time = results["metrics_original"]["duration"]
    metrics_optimized_time = results["metrics_optimized"]["duration"]

    # Calculate speedups
    orchestrator_speedup = serial_time / parallel_time
    metrics_speedup = metrics_original_time / metrics_optimized_time

    # Display results
    print(f"\nOrchestrator Performance:")
    print(f"  Serial:   {serial_time:.3f} seconds")
    print(f"  Parallel: {parallel_time:.3f} seconds")
    print(f"  Speedup:  {orchestrator_speedup:.2f}x")
    print(f"  Improvement: {((serial_time - parallel_time) / serial_time * 100):.1f}%")

    print(f"\nMetrics Collector Performance:")
    print(f"  Original:  {metrics_original_time:.3f} seconds")
    print(f"  Optimized: {metrics_optimized_time:.3f} seconds")
    print(f"  Speedup:   {metrics_speedup:.2f}x")
    print(
        f"  Improvement: {((metrics_original_time - metrics_optimized_time) / metrics_original_time * 100):.1f}%"
    )

    print(f"\nOverall Performance Gain:")
    total_original = serial_time
    total_optimized = parallel_time
    overall_speedup = total_original / total_optimized
    print(f"  Original Total:  {total_original:.3f} seconds")
    print(f"  Optimized Total: {total_optimized:.3f} seconds")
    print(f"  Overall Speedup: {overall_speedup:.2f}x")

    # Show top time-consuming functions
    print("\n" + "-" * 60)
    print("TOP TIME-CONSUMING FUNCTIONS (Serial Orchestrator)")
    print("-" * 60)
    print(results["serial_orchestrator"]["profile"].split("\n")[0:15])

    print("\n" + "-" * 60)
    print("TOP TIME-CONSUMING FUNCTIONS (Parallel Orchestrator)")
    print("-" * 60)
    print(results["parallel_orchestrator"]["profile"].split("\n")[0:15])


def create_recommendations(results):
    """Create optimization recommendations based on results"""
    print("\n" + "=" * 60)
    print("OPTIMIZATION RECOMMENDATIONS")
    print("=" * 60)

    # Calculate metrics
    serial_time = results["serial_orchestrator"]["duration"]
    parallel_time = results["parallel_orchestrator"]["duration"]
    metrics_original_time = results["metrics_original"]["duration"]
    metrics_optimized_time = results["metrics_optimized"]["duration"]

    recommendations = []

    # Parallelization recommendation
    if serial_time / parallel_time > 2:
        recommendations.append(
            {
                "priority": "HIGH",
                "type": "Parallelization",
                "impact": f"{serial_time / parallel_time:.1f}x speedup",
                "details": "Use multiprocessing for independent components",
            }
        )

    # NumPy/Numba optimization
    if metrics_original_time / metrics_optimized_time > 1.5:
        recommendations.append(
            {
                "priority": "MEDIUM",
                "type": "Numerical Optimization",
                "impact": f"{metrics_original_time / metrics_optimized_time:.1f}x speedup",
                "details": "Use NumPy vectorization and Numba JIT compilation",
            }
        )

    # Additional recommendations based on profile
    recommendations.extend(
        [
            {
                "priority": "LOW",
                "type": "Caching",
                "impact": "Variable",
                "details": "Cache git command results to avoid repeated execution",
            },
            {
                "priority": "MEDIUM",
                "type": "PyPy",
                "impact": "4-10x speedup potential",
                "details": "Consider using PyPy interpreter for CPU-bound operations",
            },
            {
                "priority": "LOW",
                "type": "Async I/O",
                "impact": "Variable",
                "details": "Use async operations for I/O-bound tasks",
            },
        ]
    )

    for rec in recommendations:
        print(f"\n[{rec['priority']}] {rec['type']}")
        print(f"  Impact: {rec['impact']}")
        print(f"  Details: {rec['details']}")


def main():
    """Run comprehensive performance analysis"""
    import argparse

    parser = argparse.ArgumentParser(description="Test all optimization techniques")
    parser.add_argument("path", help="Repository path to analyze")
    parser.add_argument("--save-report", "-s", help="Save report to file", default=None)

    args = parser.parse_args()

    print(f"COMPREHENSIVE PERFORMANCE ANALYSIS")
    print(f"Repository: {args.path}")
    print("=" * 60)

    results = {}

    # Test all implementations
    results["serial_orchestrator"] = test_serial_orchestrator(args.path)
    results["parallel_orchestrator"] = test_parallel_orchestrator(args.path)
    results["metrics_original"] = test_metrics_collector_original(args.path)
    results["metrics_optimized"] = test_metrics_collector_optimized(args.path)

    # Analyze results
    analyze_results(results)

    # Generate recommendations
    create_recommendations(results)

    # Save report if requested
    if args.save_report:
        report = {
            "repository": args.path,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "performance_metrics": {
                "serial_orchestrator": results["serial_orchestrator"]["duration"],
                "parallel_orchestrator": results["parallel_orchestrator"]["duration"],
                "metrics_original": results["metrics_original"]["duration"],
                "metrics_optimized": results["metrics_optimized"]["duration"],
            },
            "speedups": {
                "orchestrator": results["serial_orchestrator"]["duration"]
                / results["parallel_orchestrator"]["duration"],
                "metrics": results["metrics_original"]["duration"]
                / results["metrics_optimized"]["duration"],
            },
        }

        with open(args.save_report, "w") as f:
            json.dump(report, f, indent=2)

        print(f"\n\nReport saved to: {args.save_report}")


if __name__ == "__main__":
    main()
