# Ultra Test Configuration System

## Overview

The Ultra project uses a comprehensive test configuration system that allows tests to run in different modes, from fully mocked offline tests to live production endpoint tests. This system ensures tests are reliable, fast, and can be run in various environments.

## Test Modes

### 1. OFFLINE Mode (Default)
- **Purpose**: Fast, isolated unit tests with no external dependencies
- **Characteristics**:
  - All external services are mocked (LLMs, database, Redis, APIs)
  - No network calls
  - Fastest execution
  - Suitable for CI/CD pipelines
- **Command**: `make test` or `make test-offline`

### 2. MOCK Mode
- **Purpose**: Tests with sophisticated mocks that simulate real behavior
- **Characteristics**:
  - Enhanced mocks with realistic responses
  - In-memory database (SQLite)
  - Mock Redis with memory storage
  - No external API calls
- **Command**: `make test-mock`

### 3. INTEGRATION Mode
- **Purpose**: Tests against local services
- **Characteristics**:
  - Uses local PostgreSQL and Redis
  - LLM calls are still mocked
  - Tests service integration
  - Requires local services running
- **Command**: `make test-integration`

### 4. LIVE Mode
- **Purpose**: Tests against real LLM providers
- **Characteristics**:
  - Makes real API calls to OpenAI, Anthropic, Google
  - Requires API keys
  - Incurs API costs
  - Longer execution time
- **Command**: `make test-live`

### 5. PRODUCTION Mode
- **Purpose**: Smoke tests against deployed production
- **Characteristics**:
  - Tests production endpoints
  - Limited test scope (no destructive operations)
  - Requires production to be accessible
  - Useful for deployment verification
- **Command**: `make test-production`

### 6. E2E Mode
- **Purpose**: End-to-end tests with full user flows
- **Characteristics**:
  - Tests complete user journeys
  - May include browser automation
  - Requires full stack running
- **Command**: `make e2e`

## Configuration Files

### Core Configuration
- **`tests/test_config.py`**: Central configuration system
  - Determines test mode from `TEST_MODE` environment variable
  - Configures endpoints, timeouts, and mock behavior
  - Provides decorators for conditional test execution

### Mock Configuration
- **`tests/mock_config.py`**: Reusable mock implementations
  - `MockLLMResponses`: Predefined LLM response templates
  - `MockRedisClient`: In-memory Redis implementation
  - `MockDatabase`: In-memory database implementation
  - Factory functions for creating configured mocks

### Test Runner Scripts
- **`scripts/run_tests_offline.sh`**: Run tests in OFFLINE mode
- **`scripts/run_tests_mock.sh`**: Run tests in MOCK mode
- **`scripts/run_tests_integration.sh`**: Run tests in INTEGRATION mode
- **`scripts/run_tests_live.sh`**: Run tests in LIVE mode
- **`scripts/run_tests_production.sh`**: Run tests in PRODUCTION mode

## Writing Tests

### Basic Test Structure
```python
import pytest
from tests.test_config import TestConfig, TestMode

class TestMyFeature:
    def test_basic_functionality(self):
        # This test runs in all modes
        assert True
    
    @pytest.mark.asyncio
    async def test_with_mocks(self, mock_llm_adapters):
        # Mocks are automatically injected based on test mode
        if TestConfig.should_mock["llm_responses"]:
            # Use mocks
            assert mock_llm_adapters is not None
        else:
            # Use real services
            assert mock_llm_adapters is None
```

### Conditional Test Execution
```python
from tests.test_config import skip_if_offline, skip_if_not_mode

@skip_if_offline()
async def test_requiring_services():
    # Skipped in OFFLINE mode
    pass

@skip_if_not_mode(TestMode.LIVE)
async def test_live_only():
    # Only runs in LIVE mode
    pass

@pytest.mark.production
async def test_production_only():
    # Only runs in PRODUCTION mode
    pass
```

### Using Test Configuration
```python
from tests.test_config import TestConfig

def test_configuration_aware():
    # Get current mode
    if TestConfig.mode == TestMode.OFFLINE:
        # Offline-specific logic
        pass
    
    # Check if mocking is enabled
    if TestConfig.should_mock["database"]:
        # Use mock database
        pass
    
    # Get configured endpoints
    api_url = TestConfig.endpoints.api_base_url
    
    # Get appropriate timeout
    timeout = TestConfig.get_timeout("llm_request")
```

## Pytest Markers

### Standard Markers
- `unit`: Unit tests (component isolation)
- `integration`: Integration tests (service interaction)
- `e2e`: End-to-end tests (full user flows)
- `slow`: Tests that take significant time
- `quick`: Fast tests

### Mode-Specific Markers
- `live`: Tests requiring real LLM providers
- `live_online`: Alternative marker for live tests
- `production`: Tests that run against production
- `playwright`: Tests requiring browser automation

## Environment Variables

### Required Variables
- `TEST_MODE`: Sets the test mode (OFFLINE|MOCK|INTEGRATION|LIVE|PRODUCTION)
- `JWT_SECRET_KEY`: Required for auth tests

### Mode-Specific Variables
- **INTEGRATION/LIVE modes**:
  - `DATABASE_URL`: PostgreSQL connection string
  - `REDIS_URL`: Redis connection string

- **LIVE mode**:
  - `OPENAI_API_KEY`: OpenAI API key
  - `ANTHROPIC_API_KEY`: Anthropic API key
  - `GOOGLE_API_KEY`: Google API key

- **PRODUCTION mode**:
  - `PRODUCTION_TEST_TOKEN`: Optional auth token for production tests

## Best Practices

### 1. Test Mode Selection
- Use OFFLINE mode for rapid development and CI/CD
- Use MOCK mode for testing complex interactions
- Use INTEGRATION mode for service integration testing
- Use LIVE mode sparingly (costs money)
- Use PRODUCTION mode for deployment verification

### 2. Writing Mode-Aware Tests
- Always check `TestConfig.mode` when behavior should differ
- Use provided decorators for conditional execution
- Leverage `TestConfig.should_mock` for mock decisions
- Use appropriate timeouts from `TestConfig.get_timeout()`

### 3. Mock Usage
- Import mocks from `mock_config.py` for consistency
- Use fixture injection for automatic mock configuration
- Create reusable mock responses for common scenarios

### 4. Performance Considerations
- OFFLINE tests should complete in < 1 second
- INTEGRATION tests should complete in < 5 seconds
- LIVE tests may take 30+ seconds
- Use appropriate pytest markers for test categorization

## Troubleshooting

### Common Issues

1. **Tests failing in OFFLINE mode**
   - Check if test is trying to make network calls
   - Ensure mocks are properly configured
   - Verify `TEST_MODE=OFFLINE` is set

2. **Integration tests failing**
   - Ensure PostgreSQL and Redis are running
   - Check database permissions
   - Verify connection strings

3. **Live tests skipped**
   - Ensure API keys are set in environment
   - Check for typos in environment variable names
   - Verify API keys are valid

4. **Production tests timeout**
   - Check if production is accessible
   - Increase timeout values if needed
   - Verify network connectivity

## Examples

### Running specific test categories
```bash
# Run only unit tests in OFFLINE mode
make test-offline

# Run integration tests with local services
make test-integration

# Run specific test file in MOCK mode
TEST_MODE=MOCK pytest tests/test_orchestration_service.py -v

# Run live tests for specific provider
make test-live

# Run end-to-end tests
make e2e

# Run all test suites
make test-all
```

### CI/CD Pipeline Example
```yaml
# .github/workflows/test-matrix.yml
name: Test Matrix

on:
  push:
    branches: [ main, production ]
  pull_request:
    branches: [ main, production ]

jobs:
  test-matrix:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        test-category: [unit, integration, e2e]
    
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run ${{ matrix.test-category }} tests
        run: pytest -v -m "${{ matrix.test-category }}"
```

## Migration Guide

### Updating Existing Tests
1. Remove hardcoded mock configurations
2. Import from `test_config` and `mock_config`
3. Add appropriate pytest markers
4. Use configuration-aware patterns
5. Test in multiple modes to ensure compatibility

### Example Migration
```python
# Before
def test_old_style():
    with patch("app.services.llm_adapters.OpenAIAdapter") as mock:
        mock.return_value.generate.return_value = {"text": "response"}
        # test code

# After
from tests.test_config import TestConfig

def test_new_style(mock_llm_adapters):
    if TestConfig.should_mock["llm_responses"]:
        # Mocks are automatically provided
        # test code
    else:
        # Test with real services
        # test code
```