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

# Run end-to-end browser tests (starts all services automatically)
./scripts/test-e2e.sh

# Generate HTML test report
make test-report

# Run all tests with coverage
make test-coverage
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

### Test Coverage Summary
- **Total Tests**: 512+ test functions
- **Code Coverage**: ~31% (10,447 of 15,053 lines)
- **Service Coverage**: 52% (28 of 54 services have tests)
- **Test Files**: 51 test modules

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

## Test Reports and Coverage

```bash
# Generate HTML test report with coverage
make test-report

# This creates:
# - report.html - Test results with pass/fail details
# - htmlcov/index.html - Code coverage report
# - allure-report/ - Detailed test analytics (if Allure is installed)

# View coverage in terminal
pytest tests/ --cov=app --cov-report=term

# Coverage with missing lines
pytest tests/ --cov=app --cov-report=term-missing
```

## Browser Testing with Playwright

The test suite includes Playwright for end-to-end browser testing:

```bash
# Install Playwright browsers (one-time setup)
playwright install

# Easy way: Use the E2E test runner script
./scripts/test-e2e.sh          # Run tests with browser hidden
./scripts/test-e2e.sh --headed  # Run tests with browser visible

# Manual way: Start services and run tests separately
# 1. Start frontend: cd frontend && npm run dev
# 2. Start backend: python app.py
# 3. Run tests: pytest tests/live/test_live_online_ui.py -v

# Run with specific browser
pytest tests/live/test_live_online_ui.py --browser chromium
pytest tests/live/test_live_online_ui.py --browser firefox
pytest tests/live/test_live_online_ui.py --browser webkit

# Set custom frontend URL
WEB_APP_URL=http://localhost:5173 pytest tests/live/test_live_online_ui.py -v
```

### E2E Test Script Features

The `scripts/test-e2e.sh` script automates the entire E2E testing process:

- ✅ Automatically starts frontend and backend servers
- ✅ Configures frontend to connect to local backend
- ✅ Waits for services to be ready before running tests
- ✅ Loads API keys from `.env` file
- ✅ Runs browser tests with Playwright
- ✅ Runs additional live provider tests
- ✅ Provides detailed logging and error reporting
- ✅ Cleans up processes on exit
- ✅ Supports headed mode to see browser interactions

### Complete E2E Testing Workflow

1. **Initial Setup** (one-time):
   ```bash
   # Install Playwright browsers
   playwright install
   
   # Ensure API keys are in .env file
   echo "OPENAI_API_KEY=your-key" >> .env
   echo "ANTHROPIC_API_KEY=your-key" >> .env
   ```

2. **Run E2E Tests**:
   ```bash
   # Run all E2E tests (browser hidden)
   ./scripts/test-e2e.sh
   
   # Run with browser visible
   ./scripts/test-e2e.sh --headed
   
   # Skip frontend reconfiguration
   ./scripts/test-e2e.sh --skip-setup
   ```

3. **Restore Production Settings**:
   ```bash
   # After testing, restore frontend to production API
   ./scripts/restore-production.sh
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

# Set test timeout (useful for debugging)
pytest tests/ --timeout=300  # 5 minutes

# Disable timeout for debugging
pytest tests/ --timeout=0
```

## Known Issues

### E2E Cache Tests
Some e2e cache tests may timeout. If this happens, exclude them:
```bash
pytest tests/ -k "not (test_cache and e2e)"
```

### Live Test Requirements
Live tests require API keys to be set:
- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`
- `GOOGLE_API_KEY`
- `HUGGINGFACE_API_KEY` (optional)

Set these in your `.env` file or export them before running:
```bash
export $(grep -E "API_KEY" .env | xargs)
TEST_MODE=live pytest tests/live/
```