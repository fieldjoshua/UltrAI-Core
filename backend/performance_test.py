#!/usr/bin/env python3
import asyncio
import aiohttp
import time
import json
import argparse
import statistics
import psutil
import os
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor

# Configuration
DEFAULT_API_URL = "http://localhost:8080"
DEFAULT_OUTPUT_DIR = "performance_reports"
MAX_CONCURRENT_REQUESTS = 10
TEST_DURATIONS = {
    "quick": 30,    # 30 seconds for quick tests
    "standard": 120, # 2 minutes for standard tests
    "extended": 300  # 5 minutes for extended tests
}

# Test prompts of varying complexity
TEST_PROMPTS = {
    "simple": "Explain what an LLM is in one paragraph.",
    "medium": "Compare and contrast three major machine learning approaches: supervised learning, unsupervised learning, and reinforcement learning. Include examples of each.",
    "complex": "Analyze the potential economic impacts of widespread AGI adoption on global labor markets, productivity, and income inequality. Consider both short-term disruptions and long-term structural changes."
}

class PerformanceTester:
    def __init__(self, api_url=DEFAULT_API_URL, output_dir=DEFAULT_OUTPUT_DIR):
        self.api_url = api_url
        self.output_dir = output_dir
        self.results = []
        self.system_metrics = []
        self.start_time = None
        self.end_time = None
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
    
    async def monitor_system_resources(self, interval=1.0, stop_event=None):
        """Monitor system resources during the test"""
        process = psutil.Process(os.getpid())
        
        while not stop_event.is_set():
            timestamp = time.time() - self.start_time
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory_usage = process.memory_info().rss / (1024 * 1024)  # MB
            
            self.system_metrics.append({
                "timestamp": timestamp,
                "cpu_percent": cpu_percent,
                "memory_mb": memory_usage
            })
            
            await asyncio.sleep(interval)
    
    async def fetch_metrics(self, session):
        """Fetch current performance metrics from the API"""
        try:
            async with session.get(f"{self.api_url}/api/metrics") as response:
                if response.status == 200:
                    return await response.json()
                else:
                    print(f"Error fetching metrics: {response.status}")
                    return None
        except Exception as e:
            print(f"Exception fetching metrics: {e}")
            return None
    
    async def make_request(self, session, prompt, selected_models, pattern="Confidence Analysis"):
        """Make a single request to the API"""
        start_time = time.time()
        error = None
        response_data = None
        
        try:
            payload = {
                "prompt": prompt,
                "selectedModels": selected_models,
                "ultraModel": selected_models[0] if selected_models else "claude",
                "pattern": pattern
            }
            
            async with session.post(f"{self.api_url}/api/analyze", json=payload) as response:
                response_data = await response.json()
                status_code = response.status
        except Exception as e:
            error = str(e)
            status_code = 500
        
        end_time = time.time()
        duration = end_time - start_time
        
        result = {
            "timestamp": time.time() - self.start_time,
            "duration": duration,
            "status_code": status_code,
            "prompt_length": len(prompt),
            "error": error,
            "success": status_code == 200 and error is None
        }
        
        self.results.append(result)
        return result
    
    async def run_load_test(self, test_type="standard", prompt_complexity="medium", concurrency=3, models=None):
        """Run a load test with specified parameters"""
        if models is None:
            models = ["claude", "chatgpt"]
            
        duration = TEST_DURATIONS.get(test_type, 120)
        prompt = TEST_PROMPTS.get(prompt_complexity, TEST_PROMPTS["medium"])
        
        print(f"Running {test_type} load test for {duration} seconds")
        print(f"Prompt complexity: {prompt_complexity}")
        print(f"Concurrency level: {concurrency}")
        print(f"Models: {', '.join(models)}")
        
        self.start_time = time.time()
        stop_event = asyncio.Event()
        
        # Start resource monitoring in the background
        monitor_task = asyncio.create_task(
            self.monitor_system_resources(interval=1.0, stop_event=stop_event)
        )
        
        # Create session for API requests
        async with aiohttp.ClientSession() as session:
            # Fetch initial metrics
            initial_metrics = await self.fetch_metrics(session)
            
            # Run the load test
            pending_tasks = set()
            request_count = 0
            
            while time.time() - self.start_time < duration:
                # Keep concurrency level tasks running
                while len(pending_tasks) < concurrency:
                    task = asyncio.create_task(
                        self.make_request(session, prompt, models)
                    )
                    pending_tasks.add(task)
                    request_count += 1
                
                # Wait for at least one task to complete
                done, pending_tasks = await asyncio.wait(
                    pending_tasks, 
                    return_when=asyncio.FIRST_COMPLETED
                )
                
                # Process completed tasks
                for task in done:
                    result = task.result()
                    
                # Sleep a bit to avoid tight loops
                await asyncio.sleep(0.1)
            
            # Wait for remaining tasks to complete
            if pending_tasks:
                await asyncio.wait(pending_tasks)
            
            # Fetch final metrics
            final_metrics = await self.fetch_metrics(session)
            
            # Stop the monitoring
            stop_event.set()
            await monitor_task
        
        self.end_time = time.time()
        
        # Analyze results
        return self.generate_report(initial_metrics, final_metrics, {
            "test_type": test_type,
            "prompt_complexity": prompt_complexity,
            "concurrency": concurrency,
            "models": models,
            "duration": duration,
            "request_count": request_count
        })
    
    def generate_report(self, initial_metrics, final_metrics, test_config):
        """Generate a comprehensive performance report"""
        # Calculate key metrics
        durations = [r["duration"] for r in self.results if r["success"]]
        success_rate = sum(1 for r in self.results if r["success"]) / len(self.results) if self.results else 0
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "test_configuration": test_config,
            "summary": {
                "total_requests": len(self.results),
                "successful_requests": sum(1 for r in self.results if r["success"]),
                "failed_requests": sum(1 for r in self.results if not r["success"]),
                "success_rate": success_rate,
                "total_duration": self.end_time - self.start_time,
                "requests_per_second": len(self.results) / (self.end_time - self.start_time),
                "avg_response_time": statistics.mean(durations) if durations else 0,
                "median_response_time": statistics.median(durations) if durations else 0,
                "min_response_time": min(durations) if durations else 0,
                "max_response_time": max(durations) if durations else 0,
                "p95_response_time": np.percentile(durations, 95) if durations else 0,
                "p99_response_time": np.percentile(durations, 99) if durations else 0
            },
            "system_metrics": {
                "avg_cpu_percent": statistics.mean([m["cpu_percent"] for m in self.system_metrics]) if self.system_metrics else 0,
                "max_cpu_percent": max([m["cpu_percent"] for m in self.system_metrics]) if self.system_metrics else 0,
                "avg_memory_mb": statistics.mean([m["memory_mb"] for m in self.system_metrics]) if self.system_metrics else 0,
                "max_memory_mb": max([m["memory_mb"] for m in self.system_metrics]) if self.system_metrics else 0
            },
            "backend_metrics": {
                "initial": initial_metrics,
                "final": final_metrics,
                "delta": {
                    "requests_processed": (final_metrics.get("requests_processed", 0) - 
                                           initial_metrics.get("requests_processed", 0)) if final_metrics and initial_metrics else None,
                    "avg_processing_time": final_metrics.get("avg_processing_time") if final_metrics else None,
                    "max_memory_usage": final_metrics.get("max_memory_usage") if final_metrics else None
                }
            }
        }
        
        # Save the report and raw data
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        test_name = f"{test_config['test_type']}_{test_config['prompt_complexity']}_{test_config['concurrency']}"
        
        # Save the raw results for detailed analysis
        results_df = pd.DataFrame(self.results)
        metrics_df = pd.DataFrame(self.system_metrics)
        
        # Save to CSV
        results_df.to_csv(f"{self.output_dir}/{timestamp}_{test_name}_results.csv", index=False)
        metrics_df.to_csv(f"{self.output_dir}/{timestamp}_{test_name}_metrics.csv", index=False)
        
        # Save the full report as JSON
        with open(f"{self.output_dir}/{timestamp}_{test_name}_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        # Generate visualizations
        self.generate_visualizations(results_df, metrics_df, report, f"{self.output_dir}/{timestamp}_{test_name}")
        
        return report
    
    def generate_visualizations(self, results_df, metrics_df, report, output_prefix):
        """Generate visualizations for the test results"""
        # Only generate if we have enough data
        if len(results_df) < 2 or len(metrics_df) < 2:
            return
        
        # 1. Response Time Over Test Duration
        plt.figure(figsize=(10, 6))
        plt.scatter(results_df['timestamp'], results_df['duration'], alpha=0.5)
        plt.title('Response Time During Test')
        plt.xlabel('Time (seconds)')
        plt.ylabel('Response Time (seconds)')
        plt.grid(True, linestyle='--', alpha=0.7)
        # Add percentile lines
        p95 = report['summary']['p95_response_time']
        p50 = report['summary']['median_response_time']
        plt.axhline(y=p95, color='r', linestyle='-', label=f'95th Percentile: {p95:.2f}s')
        plt.axhline(y=p50, color='g', linestyle='-', label=f'Median: {p50:.2f}s')
        plt.legend()
        plt.savefig(f"{output_prefix}_response_times.png")
        
        # 2. System Resource Usage
        fig, ax1 = plt.subplots(figsize=(10, 6))
        
        ax1.set_xlabel('Time (seconds)')
        ax1.set_ylabel('CPU Usage (%)', color='tab:blue')
        ax1.plot(metrics_df['timestamp'], metrics_df['cpu_percent'], color='tab:blue')
        ax1.tick_params(axis='y', labelcolor='tab:blue')
        
        ax2 = ax1.twinx()
        ax2.set_ylabel('Memory Usage (MB)', color='tab:red')
        ax2.plot(metrics_df['timestamp'], metrics_df['memory_mb'], color='tab:red')
        ax2.tick_params(axis='y', labelcolor='tab:red')
        
        plt.title('System Resource Usage During Test')
        fig.tight_layout()
        plt.savefig(f"{output_prefix}_system_resources.png")
        
        # 3. Cumulative Request Count and Success/Failure
        results_df['cumulative_requests'] = range(1, len(results_df) + 1)
        success_df = results_df[results_df['success'] == True]
        failure_df = results_df[results_df['success'] == False]
        
        plt.figure(figsize=(10, 6))
        plt.plot(results_df['timestamp'], results_df['cumulative_requests'], label='Total Requests')
        if not success_df.empty:
            plt.scatter(success_df['timestamp'], success_df.index + 1, color='green', alpha=0.5, label='Success')
        if not failure_df.empty:
            plt.scatter(failure_df['timestamp'], failure_df.index + 1, color='red', alpha=0.5, label='Failure')
        
        plt.title('Cumulative Requests Over Time')
        plt.xlabel('Time (seconds)')
        plt.ylabel('Number of Requests')
        plt.legend()
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.savefig(f"{output_prefix}_request_count.png")
        
        # 4. Response Time Distribution (Histogram)
        plt.figure(figsize=(10, 6))
        plt.hist(results_df['duration'], bins=20, alpha=0.7, edgecolor='black')
        plt.title('Response Time Distribution')
        plt.xlabel('Response Time (seconds)')
        plt.ylabel('Frequency')
        plt.grid(True, linestyle='--', alpha=0.7)
        # Add percentile lines
        plt.axvline(x=p95, color='r', linestyle='-', label=f'95th Percentile: {p95:.2f}s')
        plt.axvline(x=p50, color='g', linestyle='-', label=f'Median: {p50:.2f}s')
        plt.legend()
        plt.savefig(f"{output_prefix}_response_time_distribution.png")
        
        plt.close('all')
    
    def print_summary(self, report):
        """Print a summary of the test results to console"""
        print("\n" + "="*50)
        print(f"PERFORMANCE TEST SUMMARY")
        print("="*50)
        
        # Test configuration
        config = report["test_configuration"]
        print(f"Test type: {config['test_type']}")
        print(f"Prompt complexity: {config['prompt_complexity']}")
        print(f"Concurrency level: {config['concurrency']}")
        print(f"Models: {', '.join(config['models'])}")
        print(f"Duration: {config['duration']} seconds")
        
        # Summary metrics
        summary = report["summary"]
        print("\nRequest Metrics:")
        print(f"Total requests: {summary['total_requests']}")
        print(f"Success rate: {summary['success_rate']*100:.2f}%")
        print(f"Requests per second: {summary['requests_per_second']:.2f}")
        print(f"Average response time: {summary['avg_response_time']:.2f}s")
        print(f"95th percentile response time: {summary['p95_response_time']:.2f}s")
        
        # System metrics
        sys_metrics = report["system_metrics"]
        print("\nSystem Metrics:")
        print(f"Average CPU usage: {sys_metrics['avg_cpu_percent']:.2f}%")
        print(f"Maximum CPU usage: {sys_metrics['max_cpu_percent']:.2f}%")
        print(f"Average memory usage: {sys_metrics['avg_memory_mb']:.2f} MB")
        print(f"Maximum memory usage: {sys_metrics['max_memory_mb']:.2f} MB")
        
        # Backend metrics
        backend = report["backend_metrics"]["delta"]
        if backend["requests_processed"] is not None:
            print("\nBackend Metrics:")
            print(f"Requests processed by backend: {backend['requests_processed']}")
            print(f"Final average processing time: {backend['avg_processing_time']:.2f}s")
            print(f"Maximum memory usage: {backend['max_memory_usage']:.2f} MB")
        
        print("\nReport and visualizations saved to:", self.output_dir)
        print("="*50)

async def run_single_test(api_url, output_dir, test_type, prompt_complexity, concurrency, models):
    """Run a single performance test with the specified configuration"""
    tester = PerformanceTester(api_url, output_dir)
    report = await tester.run_load_test(
        test_type=test_type,
        prompt_complexity=prompt_complexity,
        concurrency=concurrency,
        models=models
    )
    tester.print_summary(report)
    return report

async def run_benchmark_suite(api_url, output_dir):
    """Run a comprehensive benchmark suite with various configurations"""
    test_configs = [
        # Quick, low-load tests
        {"test_type": "quick", "prompt_complexity": "simple", "concurrency": 1, "models": ["claude"]},
        {"test_type": "quick", "prompt_complexity": "simple", "concurrency": 1, "models": ["chatgpt"]},
        
        # Standard tests with different complexities
        {"test_type": "standard", "prompt_complexity": "simple", "concurrency": 2, "models": ["claude", "chatgpt"]},
        {"test_type": "standard", "prompt_complexity": "medium", "concurrency": 2, "models": ["claude", "chatgpt"]},
        {"test_type": "standard", "prompt_complexity": "complex", "concurrency": 2, "models": ["claude", "chatgpt"]},
        
        # Concurrency scale tests
        {"test_type": "standard", "prompt_complexity": "medium", "concurrency": 3, "models": ["claude", "chatgpt"]},
        {"test_type": "standard", "prompt_complexity": "medium", "concurrency": 5, "models": ["claude", "chatgpt"]},
        
        # Extended, high-load test
        {"test_type": "extended", "prompt_complexity": "complex", "concurrency": 4, "models": ["claude", "chatgpt", "gemini"]},
    ]
    
    results = []
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    suite_dir = f"{output_dir}/benchmark_suite_{timestamp}"
    os.makedirs(suite_dir, exist_ok=True)
    
    print(f"Running benchmark suite with {len(test_configs)} configurations")
    print(f"Results will be saved to: {suite_dir}")
    
    for i, config in enumerate(test_configs):
        print(f"\nRunning test {i+1}/{len(test_configs)}")
        tester = PerformanceTester(api_url, suite_dir)
        report = await tester.run_load_test(**config)
        tester.print_summary(report)
        results.append(report)
        
        # Save a summary of all tests
        with open(f"{suite_dir}/benchmark_summary.json", "w") as f:
            summary = {
                "timestamp": timestamp,
                "test_count": len(test_configs),
                "results": [
                    {
                        "config": r["test_configuration"],
                        "requests_per_second": r["summary"]["requests_per_second"],
                        "avg_response_time": r["summary"]["avg_response_time"],
                        "p95_response_time": r["summary"]["p95_response_time"],
                        "success_rate": r["summary"]["success_rate"]
                    } for r in results
                ]
            }
            json.dump(summary, f, indent=2)
    
    # Generate comparative visualizations
    generate_comparison_charts(results, suite_dir)
    
    print(f"\nBenchmark suite completed. Full results saved to: {suite_dir}")
    return results

def generate_comparison_charts(results, output_dir):
    """Generate charts comparing the results of multiple tests"""
    if not results:
        return
    
    # Extract key metrics for comparison
    configs = []
    rps_values = []
    avg_times = []
    p95_times = []
    success_rates = []
    
    for r in results:
        config = r["test_configuration"]
        config_str = f"{config['prompt_complexity']}\n{config['concurrency']} concurrent"
        configs.append(config_str)
        
        rps_values.append(r["summary"]["requests_per_second"])
        avg_times.append(r["summary"]["avg_response_time"])
        p95_times.append(r["summary"]["p95_response_time"])
        success_rates.append(r["summary"]["success_rate"] * 100)
    
    # Create comparison charts
    plt.figure(figsize=(12, 6))
    x = np.arange(len(configs))
    width = 0.35
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Requests per second
    bars1 = ax1.bar(x - width/2, rps_values, width, label='Requests/sec')
    ax1.set_title('Performance Comparison')
    ax1.set_xticks(x)
    ax1.set_xticklabels(configs)
    ax1.set_ylabel('Requests per Second')
    ax1.legend()
    
    # Response times
    ax2.bar(x - width/2, avg_times, width, label='Avg Response Time (s)')
    ax2.bar(x + width/2, p95_times, width, label='P95 Response Time (s)')
    ax2.set_title('Response Time Comparison')
    ax2.set_xticks(x)
    ax2.set_xticklabels(configs)
    ax2.set_ylabel('Time (seconds)')
    ax2.legend()
    
    plt.tight_layout()
    plt.savefig(f"{output_dir}/performance_comparison.png")
    
    # Success rate comparison
    plt.figure(figsize=(12, 6))
    plt.bar(x, success_rates, width=0.6)
    plt.title('Success Rate Comparison')
    plt.xlabel('Test Configuration')
    plt.ylabel('Success Rate (%)')
    plt.xticks(x, configs)
    plt.ylim(0, 105)  # Set y-axis to go from 0 to 105%
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Add percentage labels on the bars
    for i, v in enumerate(success_rates):
        plt.text(i, v + 2, f"{v:.1f}%", ha='center')
    
    plt.tight_layout()
    plt.savefig(f"{output_dir}/success_rate_comparison.png")
    
    plt.close('all')

async def run_continuous_monitoring(api_url, output_dir, duration_hours=24, interval_minutes=15):
    """Run continuous monitoring of the system for a specified duration"""
    print(f"Starting continuous monitoring for {duration_hours} hours")
    print(f"Metrics will be collected every {interval_minutes} minutes")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    monitor_dir = f"{output_dir}/monitoring_{timestamp}"
    os.makedirs(monitor_dir, exist_ok=True)
    
    start_time = time.time()
    end_time = start_time + (duration_hours * 3600)
    
    metrics_history = []
    
    try:
        while time.time() < end_time:
            collection_time = datetime.now().isoformat()
            
            # Collect metrics from the API
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.get(f"{api_url}/api/metrics") as response:
                        if response.status == 200:
                            metrics = await response.json()
                            metrics["collection_time"] = collection_time
                            metrics_history.append(metrics)
                            
                            # Save the latest metrics
                            with open(f"{monitor_dir}/metrics_history.json", "w") as f:
                                json.dump(metrics_history, f, indent=2)
                            
                            # Generate trend visualizations
                            if len(metrics_history) > 1:
                                generate_trend_charts(metrics_history, monitor_dir)
                            
                            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Metrics collected. "
                                  f"Current memory usage: {metrics.get('current_memory_usage_mb', 'N/A')} MB, "
                                  f"Requests: {metrics.get('requests_processed', 'N/A')}")
                        else:
                            print(f"Error collecting metrics: {response.status}")
                except Exception as e:
                    print(f"Exception during metric collection: {e}")
            
            # Wait until the next collection interval
            next_collection = time.time() + (interval_minutes * 60)
            sleep_time = max(0, next_collection - time.time())
            
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)
    
    except KeyboardInterrupt:
        print("\nMonitoring stopped by user")
    
    print(f"Monitoring completed. Results saved to: {monitor_dir}")
    return metrics_history

def generate_trend_charts(metrics_history, output_dir):
    """Generate trend charts for continuous monitoring"""
    # Convert to DataFrame for easier manipulation
    df = pd.DataFrame(metrics_history)
    df['collection_time'] = pd.to_datetime(df['collection_time'])
    
    # Extract key metrics
    plt.figure(figsize=(12, 8))
    plt.subplot(2, 2, 1)
    plt.plot(df['collection_time'], df['requests_processed'])
    plt.title('Total Requests Over Time')
    plt.xticks(rotation=45)
    plt.ylabel('Requests')
    plt.grid(True, linestyle='--', alpha=0.7)
    
    plt.subplot(2, 2, 2)
    plt.plot(df['collection_time'], df['avg_processing_time'])
    plt.title('Average Processing Time')
    plt.xticks(rotation=45)
    plt.ylabel('Seconds')
    plt.grid(True, linestyle='--', alpha=0.7)
    
    plt.subplot(2, 2, 3)
    plt.plot(df['collection_time'], df['current_memory_usage_mb'])
    plt.title('Current Memory Usage')
    plt.xticks(rotation=45)
    plt.ylabel('MB')
    plt.grid(True, linestyle='--', alpha=0.7)
    
    plt.subplot(2, 2, 4)
    plt.plot(df['collection_time'], df['max_memory_usage'])
    plt.title('Peak Memory Usage')
    plt.xticks(rotation=45)
    plt.ylabel('MB')
    plt.grid(True, linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    plt.savefig(f"{output_dir}/metrics_trends.png")
    plt.close()

async def main():
    parser = argparse.ArgumentParser(description='Ultra Framework Performance Tester')
    parser.add_argument('--url', type=str, default=DEFAULT_API_URL,
                      help=f'API base URL (default: {DEFAULT_API_URL})')
    parser.add_argument('--output', type=str, default=DEFAULT_OUTPUT_DIR,
                      help=f'Output directory for test results (default: {DEFAULT_OUTPUT_DIR})')
    parser.add_argument('--mode', type=str, choices=['single', 'suite', 'monitor'], default='single',
                      help='Test mode: single test, full benchmark suite, or continuous monitoring')
    
    # Single test parameters
    parser.add_argument('--test-type', type=str, choices=list(TEST_DURATIONS.keys()), default='standard',
                      help='Test duration type')
    parser.add_argument('--complexity', type=str, choices=list(TEST_PROMPTS.keys()), default='medium',
                      help='Prompt complexity')
    parser.add_argument('--concurrency', type=int, default=2,
                      help='Concurrent requests')
    parser.add_argument('--models', type=str, default='claude,chatgpt',
                      help='Comma-separated list of models to use')
    
    # Monitoring parameters
    parser.add_argument('--duration', type=float, default=24,
                      help='Duration in hours for continuous monitoring')
    parser.add_argument('--interval', type=float, default=15,
                      help='Interval in minutes between metrics collections')
    
    args = parser.parse_args()
    
    # Ensure output directory exists
    os.makedirs(args.output, exist_ok=True)
    
    if args.mode == 'single':
        models_list = args.models.split(',')
        await run_single_test(
            args.url, 
            args.output, 
            args.test_type, 
            args.complexity, 
            args.concurrency, 
            models_list
        )
    elif args.mode == 'suite':
        await run_benchmark_suite(args.url, args.output)
    elif args.mode == 'monitor':
        await run_continuous_monitoring(args.url, args.output, args.duration, args.interval)

if __name__ == "__main__":
    asyncio.run(main()) 