# Ultra Testing Guide

This guide provides information on how to run tests for the Ultra project, including test categories, tools, and best practices.

## Quick Start

### Run Core Tests

To run core tests with progress monitoring:

```bash
cd /path/to/Ultra
chmod +x tests/run_with_progress.sh
./tests/run_with_progress.sh
```

### Run Backend API Tests

To run only backend API tests:

```bash
cd /path/to/Ultra
python -m pytest backend/tests/test_api.py -v
```

### Run Tests with Coverage

To run tests with coverage reporting:

```bash
cd /path/to/Ultra
python -m pytest --cov=backend backend/tests/ -v
```

## Test Structure

The Ultra test suite is organized into several categories:

1. **Backend API Tests** - Tests for the backend API endpoints and services
2. **Authentication Tests** - Tests for authentication and authorization
3. **Rate Limiting Tests** - Tests for rate limiting functionality
4. **Orchestrator Tests** - Tests for the LLM orchestration system
5. **Integration Tests** - End-to-end integration tests

See `TEST_INDEX.md` for a comprehensive list of all tests and their status.

## Test Tools

### Test Runners

Ultra provides several test runners:

- `tests/run_with_progress.sh` - Run tests with progress monitoring
- `backend/tests/run_tests.sh` - Run backend tests with basic reporting
- `scripts/run_tests.sh` - Run project-wide tests with CI configuration

### Progress Monitor

The `tests/test_progress.py` script provides a visual progress bar and status display for test runs:

```bash
# Run in demo mode to see how it works
python tests/test_progress.py --demo

# Use with a test runner
./tests/run_with_progress.sh --report my_test_report.json
```

### Test Fixtures

Common test fixtures are defined in `backend/tests/conftest.py`, including:

- `client()` - FastAPI test client
- `test_document_file()` - Sample document for testing
- `mock_environment()` - Mock environment for testing
- `mock_llm_service()` - Mock LLM service for testing

## Writing New Tests

When writing new tests:

1. Add the test to the appropriate directory based on its category
2. Follow the naming convention: `test_*_.py` for file names
3. Use fixtures from `conftest.py` whenever possible
4. Add the test to the appropriate test runner
5. Update `TEST_INDEX.md` with information about your new test

### Example Test

```python
import pytest
from fastapi.testclient import TestClient

def test_my_new_feature(client):
    """Test that my new feature works correctly."""
    # Setup test data
    test_data = {"key": "value"}
    
    # Make request to the endpoint
    response = client.post("/api/my-endpoint", json=test_data)
    
    # Verify response
    assert response.status_code == 200
    assert "result" in response.json()
    assert response.json()["result"] == "expected_value"
```

## Configuring Test Environment

Tests use environment variables for configuration:

- `MOCK_MODE=true` - Run tests with mock services
- `ENVIRONMENT=test` - Set environment to test
- `DEBUG=true` - Enable debug mode
- `SENTRY_DSN=""` - Disable Sentry during tests

These are typically set by the test runners, but you can override them if needed.

## Best Practices

1. **Test Independence**: Each test should be independent and not rely on the state from other tests
2. **Mock External Services**: Always mock external services like LLM providers in tests
3. **Clear Assertions**: Use clear, specific assertions to make test failures easy to understand
4. **Test Critical Paths**: Focus on testing critical user flows and edge cases
5. **Maintain Test Index**: Keep `TEST_INDEX.md` updated with new tests and status changes

## CI Integration

Tests are integrated with the CI pipeline:

1. Each PR triggers a GitHub Actions workflow that runs the test suite
2. Core tests must pass for a PR to be merged
3. Test results are reported in the PR comments
4. Test coverage is tracked and must not decrease with new PRs

## Troubleshooting

### Common Issues

1. **Missing Dependencies**: Ensure all test dependencies are installed with `pip install -r requirements-test.txt`
2. **Environment Variables**: Check that environment variables are set correctly
3. **Test Isolation**: If tests work individually but fail when run together, there may be isolation issues
4. **Mock Mode**: Ensure `MOCK_MODE=true` is set for tests that require mock services

### Getting Help

If you encounter issues with tests:

1. Check the test logs in `logs/test.log`
2. Look for error messages in the test output
3. Reach out to the development team for assistance