# Ultra Tests

This directory contains the test suite for the Ultra project, featuring a comprehensive test configuration system that supports multiple testing modes.

## Quick Start

```bash
# Run default tests (OFFLINE mode - fast, fully mocked)
make test

# Run tests with sophisticated mocks
make test-mock

# Run integration tests (requires local PostgreSQL and Redis)
make test-integration  

# Run tests against real LLM providers (requires API keys, costs money!)
make test-live

# Run tests against production endpoints
make test-production
```

## Test Organization

```
tests/
├── conftest.py                 # Pytest configuration and fixtures
├── test_config.py             # Test configuration system
├── mock_config.py             # Reusable mock implementations  
├── pytest_plugins.py          # Custom pytest plugins
├── TEST_CONFIGURATION.md      # Detailed configuration docs
│
├── unit/                      # Unit tests (isolated components)
├── integration/               # Integration tests (service interactions)
├── e2e/                       # End-to-end tests (full workflows)
├── live/                      # Live provider tests (real APIs)
├── production/                # Production smoke tests
└── scripts/                   # Test runner scripts
```

## Test Modes

The test suite supports 5 different execution modes:

| Mode | Description | External Dependencies | Use Case |
|------|-------------|----------------------|----------|
| **OFFLINE** | Fully mocked, no external calls | None | CI/CD, rapid development |
| **MOCK** | Sophisticated mocks | SQLite, Mock Redis | Complex interaction testing |
| **INTEGRATION** | Local services | PostgreSQL, Redis | Service integration |
| **LIVE** | Real LLM providers | API keys, Internet | Provider verification |
| **PRODUCTION** | Deployed endpoints | Internet | Deployment verification |

## Setting Test Mode

```bash
# Via environment variable
export TEST_MODE=INTEGRATION
pytest tests/

# Via make command  
make test-integration

# Via runner script
./scripts/run_tests_integration.sh
```

## Writing Tests

### Basic Test
```python
import pytest
from tests.test_config import TestConfig

def test_example():
    # Automatically uses mocks/real services based on TEST_MODE
    assert True
```

### Mode-Specific Test
```python
from tests.test_config import TestConfig, TestMode, skip_if_offline

@skip_if_offline()
async def test_requires_services():
    # Only runs in MOCK, INTEGRATION, LIVE, or PRODUCTION modes
    assert TestConfig.mode != TestMode.OFFLINE
```

### Using Mocks
```python
async def test_with_mocks(mock_llm_adapters):
    # Mocks are automatically injected based on TEST_MODE
    if TestConfig.should_mock["llm_responses"]:
        # Use mocks
        result = await mock_llm_adapters["openai"].generate("test")
```

## Setup

```bash
# Initial setup
./scripts/setup_test_env.sh

# This will:
# - Create .env.test with default configuration
# - Install Python dependencies
# - Optionally start Docker services for integration testing
# - Display available test commands
```

## Configuration

See [TEST_CONFIGURATION.md](./TEST_CONFIGURATION.md) for detailed documentation on:
- Test mode configuration
- Writing mode-aware tests
- Mock configuration
- Environment variables
- Best practices
- Troubleshooting

## Running Specific Tests

```bash
# Run a specific test file
TEST_MODE=MOCK pytest tests/test_orchestration_service.py -v

# Run tests matching a pattern
TEST_MODE=OFFLINE pytest tests/ -k "test_auth" -v

# Run only unit tests
pytest tests/unit/ -v -m unit

# Run with visible print output
pytest tests/ -s

# Run with specific timeout
pytest tests/ --timeout=120
```

## CI/CD Integration

The test configuration system is designed for easy CI/CD integration:

```yaml
# Example GitHub Actions workflow
test:
  strategy:
    matrix:
      test-mode: [OFFLINE, MOCK]
  steps:
    - name: Run ${{ matrix.test-mode }} tests
      env:
        TEST_MODE: ${{ matrix.test-mode }}
      run: make test
```

## Debugging Tests

```bash
# Verbose output
pytest tests/ -vv

# Show print statements
pytest tests/ -s

# Drop into debugger on failure
pytest tests/ --pdb

# Run last failed tests
pytest tests/ --lf

# Show test configuration
python -c "from tests.test_config import TestConfig; print(TestConfig.mode)"
```