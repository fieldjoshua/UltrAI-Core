# Testing Module

This module provides utilities and helpers for testing the Ultra framework in various environments.

## Overview

The testing module includes:

- Mock service implementations for testing without real APIs
- Test data generators for creating consistent test fixtures
- Environment configuration utilities for testing in different modes
- Test helpers for common operations during testing

## Usage

### Mock Services

The mock services provide simulated responses for testing without real API dependencies:

```python
from ultra.testing.mocks import MockLLMService

# Create a mock LLM service
mock_service = MockLLMService()

# Use the mock service in tests
response = mock_service.generate("Test prompt")
assert response is not None
```

### Environment Configuration

Configure testing environments easily:

```python
from ultra.testing.environment import setup_test_environment, teardown_test_environment

# Set up mock environment
setup_test_environment(mock_mode=True)

# Run tests...

# Clean up
teardown_test_environment()
```

### Test Data

Generate consistent test data:

```python
from ultra.testing.data import generate_test_prompt, generate_test_response

# Generate test data
prompt = generate_test_prompt(complexity="medium")
response = generate_test_response(prompt)
```

## Mock vs. Real Testing

The testing module supports both mock and real mode testing:

- **Mock Mode**: Uses simulated responses without real API calls
- **Real Mode**: Tests against actual API providers

To switch modes:

```python
# Test with mock services (default)
setup_test_environment(mock_mode=True)

# Test with real services
setup_test_environment(mock_mode=False)
```

For detailed information about testing in different modes, see the [Mock vs. Real Testing Guide](../../documentation/testing/mock_vs_real_testing.md).

## Test Organization

The tests in Ultra are organized into several categories:

1. **Unit Tests**: Test individual components in isolation
2. **Integration Tests**: Test interactions between components
3. **End-to-End Tests**: Test complete workflows
4. **Performance Tests**: Benchmark system performance

Each test category can be run in both mock and real modes, with appropriate configuration.

## Test Scripts

Ultra provides several test scripts for different scenarios:

- `run_tests.sh`: Run all tests with default configuration (mock mode)
- `test_real_mode.sh`: Run tests in real mode with actual API connections
- `test_api.py`: Test API endpoints with specific models

These scripts can be found in the `scripts/` directory.

## Adding New Test Mocks

When adding new services that require mocking:

1. Create a new mock implementation in `src/testing/mocks/`
2. Implement the same interface as the real service
3. Add appropriate test fixtures in `conftest.py`
4. Support both mock and real modes in the implementation
