# Ultra Testing Suite

This directory contains all tests for the Ultra AI framework. The tests are organized by type and component.

## Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run with verbose output
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_specific_file.py

# Run with coverage report
python -m pytest tests/ --cov=ultra
```

## Test Files

### API Tests

- `test_api.py` - Tests for the API endpoints
- `test_document_upload.py` - Tests for document upload functionality

### Core Component Tests

- `test_clients.py` - Tests for API client implementations
- `test_config.py` - Tests for configuration management
- `test_orchestrator.py` - Tests for the pattern orchestrator

### Performance Tests

- `performance_test.py` - Performance benchmarking tests

## Adding New Tests

When adding new tests:

1. Follow the naming convention `test_*.py` for test files
2. Use descriptive test function names that express what's being tested
3. Group related tests in the same file or class
4. Add proper assertions to verify expected behavior
5. Consider adding tests for both success and failure cases

## Test Fixtures

Common test fixtures are available in `conftest.py` files. These provide reusable components for tests such as:

- Mock LLM services
- Test prompts and responses
- Sample documents for testing
