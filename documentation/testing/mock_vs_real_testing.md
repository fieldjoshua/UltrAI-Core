# Development vs. Production Environment Testing

This document outlines the approach to testing Ultra in both development and production environments, ensuring that the system can seamlessly switch between these environments.

## Overview

Ultra operates in two primary environments:

1. **Development Environment**: Uses simulated LLM responses via mock services for faster, cost-effective development and testing
2. **Production Environment**: Connects to actual LLM providers (OpenAI, Anthropic, Google) for real-world usage

Testing in both environments is critical to ensure the system works correctly across all deployment scenarios.

## Environment Variables

The following environment variables control the environment:

- `ENVIRONMENT`: The current environment (`development`, `testing`, `production`)
- `USE_MOCK`: When `true`, the system uses mock LLM services (typically in development)
- `MOCK_MODE`: When `true`, the system operates with fully mocked dependencies (for development and testing)

## Testing Strategies

### Development Environment Testing

Development environment testing (with mock services) is ideal for:

- Rapid development and debugging
- Deterministic testing with consistent responses
- Testing without incurring API costs
- CI/CD pipeline integration

To run tests in the development environment:

```bash
# Using environment variables directly
export ENVIRONMENT=development
export TESTING=true
export USE_MOCK=true
export MOCK_MODE=true
python -m pytest backend/tests/

# Using the development test script
./scripts/run_tests.sh
```

### Production Environment Testing

Production environment testing (with real services) is essential for:

- Validating actual integrations with LLM providers
- Testing authentication and API key management
- Verifying the system's behavior with real responses
- Pre-deployment validation

To run tests in the production environment:

```bash
# Using environment variables directly
export ENVIRONMENT=production
export TESTING=true
export USE_MOCK=false
export MOCK_MODE=false
export API_KEY_ENCRYPTION_KEY="your-encryption-key"
python -m pytest backend/tests/

# Using the production test script
./scripts/test_real_mode.sh
```

## Testing Tools

### `run_tests.sh`

The standard test script that runs tests in mock mode. This is ideal for development and CI/CD pipelines.

### `test_real_mode.sh`

A specialized script for testing in real mode with actual LLM providers. This should be run before deploying to production to validate the system's ability to work with real services.

Key features:

- Creates a temporary test environment
- Configures necessary settings for real mode
- Runs critical tests against real services
- Validates authentication and middleware
- Optionally tests with real API keys

### `test_api.py`

A standalone script for testing the API endpoints with either mock or real LLMs.

```bash
# Test with specific models (mock or real depending on env variables)
python test_api.py --base-url http://localhost:8085 --models gpt4o,claude3opus
```

## Recommended Testing Workflow

1. **Development Testing**:

   - Use mock mode for rapid iteration
   - Run `./scripts/run_tests.sh` regularly

2. **Integration Testing**:

   - Use real mode with test API keys
   - Run `./scripts/test_real_mode.sh` to validate real service integration

3. **Pre-Production Validation**:

   - Use real mode with production API keys
   - Test critical workflows with actual LLM responses
   - Validate performance and reliability

4. **Production Monitoring**:
   - Regularly check health endpoints
   - Monitor API provider connectivity
   - Track error rates and response times

## Troubleshooting

### Mock Mode Issues

If tests fail in mock mode:

1. Verify `USE_MOCK` and `MOCK_MODE` are set to `true`
2. Check that all mock services are properly configured
3. Ensure the test environment is properly isolated

### Real Mode Issues

If tests fail in real mode:

1. Verify API keys are valid and properly configured
2. Check network connectivity to LLM providers
3. Ensure authentication middleware is correctly configured
4. Verify rate limiting is appropriate for testing
5. Check for proper error handling of real API responses

## Adding New Tests

When adding new tests:

1. Design tests to work in both mock and real modes
2. Use conditional logic based on `Config.USE_MOCK` for mode-specific behavior
3. Include appropriate mocks for external services
4. Add the test to both test scripts as appropriate
5. Document any special requirements for running the test in real mode

## Environment Setup

Use the environment templates as a starting point:

- `.env.development`: For development environment (typically mock mode)
- `.env.testing`: For test environment (configurable for mock or real)
- `.env.production`: For production environment (real mode)

You can switch between environments using:

```bash
./scripts/set-env.sh [environment]
```

## Security Considerations

When testing in real mode:

- Never commit real API keys to the repository
- Use the minimum permission level required for testing
- Consider using testing-specific API keys with usage limits
- Rotate API keys regularly
- Use the secure encryption for API key storage
