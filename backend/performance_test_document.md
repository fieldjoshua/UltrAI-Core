# Ultra Framework Performance Test Suite

## Overview

The Ultra Framework Performance Test Suite is a comprehensive benchmarking tool designed to evaluate the performance, reliability, and scalability of the Ultra Framework under various load conditions. This tool helps monitor system performance, identify bottlenecks, and ensure optimal configuration for production deployment.

## Features

- **Load Testing**: Simulate concurrent API requests with configurable concurrency levels
- **Comprehensive Metrics**: Measure response times, throughput, success rates, and system resource usage
- **Test Suites**: Run predefined test patterns or create custom test configurations
- **Continuous Monitoring**: Track system performance over extended periods
- **Detailed Reports**: Generate JSON reports and visual charts for performance analysis
- **Configurable Parameters**: Adjust test types, prompt complexity, and model selection

## Installation

1. Ensure you have Python 3.8+ installed
2. Install the required dependencies:

```bash
pip install -r performance_test_requirements.txt
```

## Usage

The performance test suite can be run in three different modes:

1. **Single Test Mode**: Run a single performance test with custom parameters
2. **Benchmark Suite**: Run a comprehensive suite of tests with varied configurations
3. **Monitoring Mode**: Continuously monitor the system over an extended period

### Basic Commands

```bash
# Run a single test (default mode)
python performance_test.py

# Run with custom parameters
python performance_test.py --test-type standard --complexity medium --concurrency 3 --models claude,chatgpt

# Run the full benchmark suite
python performance_test.py --mode suite

# Run in monitoring mode
python performance_test.py --mode monitor --duration 12 --interval 5
```

### Command-Line Arguments

| Argument        | Description                                      | Default Value        |
|-----------------|--------------------------------------------------|----------------------|
| `--url`         | API base URL                                     | http://localhost:8080 |
| `--output`      | Output directory for test results                | performance_reports  |
| `--mode`        | Test mode (single, suite, or monitor)            | single               |
| `--test-type`   | Test duration type (quick, standard, extended)   | standard             |
| `--complexity`  | Prompt complexity (simple, medium, complex)      | medium               |
| `--concurrency` | Number of concurrent requests                    | 2                    |
| `--models`      | Comma-separated list of models to use            | claude,chatgpt       |
| `--duration`    | Duration in hours for continuous monitoring      | 24                   |
| `--interval`    | Interval in minutes between metrics collections  | 15                   |

## Test Types

- **Quick Test**: 30-second test for rapid validation
- **Standard Test**: 2-minute test for general performance assessment
- **Extended Test**: 5-minute test for in-depth analysis

## Prompt Complexity Levels

- **Simple**: Short, straightforward prompts
- **Medium**: Moderate complexity prompts requiring some analysis
- **Complex**: Detailed prompts requiring extensive processing

## Output and Reports

Test results are saved to the specified output directory (default: `performance_reports`). For each test, the following files are generated:

- `*_report.json`: Comprehensive performance metrics in JSON format
- `*_results.csv`: Raw request data for detailed analysis
- `*_metrics.csv`: System resource usage over time
- Visual charts:
  - Response time scatter plot
  - System resource usage (CPU/Memory)
  - Cumulative request count
  - Response time distribution

## Example Benchmark Suite

The benchmark suite runs a series of tests with varied configurations:

1. Quick, single-model tests with simple prompts (Claude, ChatGPT)
2. Standard tests with varying prompt complexity (simple, medium, complex)
3. Concurrency scaling tests (2, 3, and 5 concurrent requests)
4. Extended, high-load test with complex prompts and multiple models

## Continuous Monitoring

Monitoring mode continuously collects metrics at specified intervals:

```bash
# Monitor for 48 hours, collecting metrics every 10 minutes
python performance_test.py --mode monitor --duration 48 --interval 10
```

This mode is ideal for identifying performance trends and issues over longer periods, such as memory leaks or degraded performance under sustained load.

## Best Practices

1. **Baseline Testing**: Always establish a performance baseline before making changes
2. **Incremental Testing**: Test after each significant system change
3. **Realistic Concurrency**: Use concurrency levels that match your expected production load
4. **Varied Complexity**: Include tests with different prompt complexities
5. **Sufficient Duration**: Use extended tests for thorough analysis
6. **Regular Monitoring**: Set up periodic monitoring in staging environments

## Troubleshooting

If you encounter issues:

1. Ensure the Ultra Framework API is running at the specified URL
2. Verify all dependencies are installed
3. Check network connectivity
4. Ensure sufficient system resources are available
5. For visualization issues, verify matplotlib is correctly installed

## Technical Details

The test suite uses:
- `aiohttp` for asynchronous HTTP requests
- `asyncio` for concurrent request handling
- `psutil` for system resource monitoring
- `pandas` and `matplotlib` for data analysis and visualization

## Advanced Usage

### Custom Prompts

You can modify the test prompts in the script to match your specific use case:

```python
TEST_PROMPTS = {
    "simple": "Your custom simple prompt here",
    "medium": "Your custom medium complexity prompt here",
    "complex": "Your detailed, complex prompt here"
}
```

### Extending the Suite

The modular design allows for easy extension. You can add custom test functions or additional metrics collection by modifying the `PerformanceTester` class. 