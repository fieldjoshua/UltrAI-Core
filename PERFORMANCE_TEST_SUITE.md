# Ultra Framework Performance Test Suite

## Overview

The Ultra Framework Performance Test Suite is a comprehensive collection of tools designed to evaluate and validate the performance characteristics of the Ultra Framework. This suite helps developers, QA engineers, and system administrators benchmark system performance, identify bottlenecks, and ensure optimal configuration for production deployment.

## Components

The test suite consists of two main components:

1. **General Performance Tester** (`backend/performance_test.py`)
   - General load testing and API benchmarking
   - System resource monitoring
   - Comprehensive metrics collection and visualization
   - Multiple test modes (single, suite, monitoring)

2. **Document Upload Tester** (`backend/test_document_upload.py`)
   - Specifically tests document processing capabilities
   - Evaluates scaling with document size and count
   - Generates test documents of various sizes
   - Visualizes relationships between document characteristics and performance

## Installation

To install the performance test suite:

1. Ensure you have Python 3.8+ installed
2. Install dependencies:

```bash
pip install -r backend/performance_test_requirements.txt
```

## Usage

### General Performance Testing

The general performance tester provides three main modes of operation:

1. **Single Test**: Run a single performance test with configurable parameters
2. **Benchmark Suite**: Run a comprehensive suite of tests with varied configurations
3. **Monitoring**: Continuously monitor system performance over extended periods

```bash
# Run a single performance test
python backend/performance_test.py

# Run the full benchmark suite
python backend/performance_test.py --mode suite

# Monitor the system for 12 hours, collecting metrics every 5 minutes
python backend/performance_test.py --mode monitor --duration 12 --interval 5
```

### Document Upload Testing

The document upload tester focuses specifically on evaluating the document processing capabilities:

1. **Single Test**: Test document processing with specific parameters
2. **Batch Test**: Run multiple document tests with varied configurations
3. **Size Scaling**: Test how performance scales with document size
4. **Count Scaling**: Test how performance scales with document count

```bash
# Generate and test with a single document
python backend/test_document_upload.py --generate

# Run batch tests with various document sizes and counts
python backend/test_document_upload.py --mode batch

# Test how performance scales with document size
python backend/test_document_upload.py --mode size-scaling

# Test how performance scales with number of documents
python backend/test_document_upload.py --mode count-scaling
```

## Key Metrics

The performance test suite collects and analyzes the following key metrics:

### System Metrics
- CPU usage
- Memory usage
- Disk usage

### Request Metrics
- Response time (average, median, 95th percentile)
- Requests per second
- Success rate

### Document Processing Metrics
- Document processing time
- Chunks generated and used
- Processing time vs. document size
- Processing time vs. document count

## Reports and Visualizations

Test results are saved in the specified output directory and include:

1. **JSON Reports**: Comprehensive performance data in structured format
2. **CSV Files**: Raw data for detailed analysis
3. **Visualizations**:
   - Response time distributions
   - System resource usage over time
   - Performance vs. load characteristics
   - Document size/count scaling charts

## Benchmark Suite

The benchmark suite runs a series of tests with increasing load complexity:

1. **Quick Tests**: Rapid validation with simple prompts and low concurrency
2. **Standard Tests**: Varied complexity with moderate concurrency
3. **Concurrency Tests**: Testing with increasing concurrent request counts
4. **Extended Tests**: High-load, complex scenarios for stress testing

## Continuous Monitoring

The continuous monitoring mode allows for extended observation of the system, helping identify:

- Memory leaks
- Performance degradation over time
- Resource consumption patterns
- System stability under sustained load

## Best Practices

For effective performance testing:

1. **Baseline First**: Establish performance baselines before making changes
2. **Incremental Testing**: Test after each significant system modification
3. **Realistic Scenarios**: Use test patterns that match expected production usage
4. **Regular Benchmarking**: Schedule periodic performance tests in CI/CD pipelines
5. **Monitor in Production**: Use the monitoring tools in staging/production environments
6. **Multiple Runs**: Run tests multiple times and average results for accuracy

## Test Development

The modular design of the test suite allows for easy extension:

1. **Custom Test Configurations**: Add new test configurations to the benchmark suite
2. **Additional Metrics**: Extend the metrics collection to track new performance indicators
3. **New Visualization**: Add custom visualizations for specific metrics
4. **Special Test Cases**: Develop specialized tests for specific features or edge cases

## Troubleshooting

If you encounter issues with the performance test suite:

1. **API Connectivity**: Ensure the Ultra Framework API is running at the specified URL
2. **Dependencies**: Verify all Python dependencies are correctly installed
3. **Resource Limits**: Check for system resource limitations affecting test execution
4. **Test Data**: Ensure test document directory exists and has proper permissions
5. **Log Files**: Check the application logs for errors during test execution

## Contributing

To extend the performance test suite:

1. Follow the modular design pattern of existing test components
2. Add new test modes with appropriate documentation
3. Ensure visualizations are clear and informative
4. Include appropriate error handling and user feedback
5. Update the requirements file if new dependencies are added 