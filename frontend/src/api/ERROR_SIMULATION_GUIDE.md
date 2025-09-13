# Mock Orchestrator Error Simulation Guide

This guide explains how to use the error simulation capabilities in the mock orchestrator API for testing error handling scenarios.

## Overview

The mock orchestrator now includes comprehensive error simulation capabilities for three main scenarios:

1. **Network Timeout**: Simulates slow network conditions where requests take too long
2. **No Models Available**: Simulates when all AI models are unavailable
3. **Authentication Failure**: Simulates authentication/authorization errors

## Error Scenarios

### Network Timeout (`network_timeout`)
- Waits 30 seconds before throwing a timeout error
- Simulates real network timeout conditions
- Error message: "Network timeout: Request took too long to complete"

### No Models Available (`no_models_available`)
- Returns HTTP 503 Service Unavailable
- Simulates when all LLM providers are down
- Returns empty model lists and appropriate error messages

### Authentication Failure (`authentication_failure`)
- Returns HTTP 401 Unauthorized
- Simulates expired or invalid authentication tokens
- Includes detailed error response with error codes

## Usage Methods

### 1. Browser Console (Development Mode)

When running in demo mode, you can control error simulation directly from the browser console:

```javascript
// Enable specific error scenario
window.mockOrchestratorErrors.simulateError('network_timeout');

// Enable random errors (30% probability)
window.mockOrchestratorErrors.simulateError('random');

// Enable errors for a specific duration (10 seconds)
window.mockOrchestratorErrors.simulateError('authentication_failure', 10000);

// Clear all error simulation
window.mockOrchestratorErrors.clearErrorSimulation();

// Set custom random error probability (50%)
window.mockOrchestratorErrors.setRandomErrorProbability(0.5);

// View available error scenarios
console.log(window.mockOrchestratorErrors.scenarios);
```

### 2. In Test Files

```javascript
import { 
  simulateError, 
  clearErrorSimulation, 
  ERROR_SCENARIOS 
} from './api/mockOrchestrator';

// In your test
beforeEach(() => {
  simulateError(ERROR_SCENARIOS.NETWORK_TIMEOUT);
});

afterEach(() => {
  clearErrorSimulation();
});

it('should handle network timeout gracefully', async () => {
  // Your test code
});
```

### 3. In Application Code (For Development)

```javascript
import { simulateError, ERROR_SCENARIOS } from './api/mockOrchestrator';

// Enable error simulation for development testing
if (process.env.NODE_ENV === 'development') {
  // Simulate authentication failures
  simulateError(ERROR_SCENARIOS.AUTHENTICATION_FAILURE);
  
  // Or enable random errors
  simulateError('random');
}
```

## Error Response Formats

### Network Timeout
```javascript
Error: "Network timeout: Request took too long to complete"
```

### No Models Available
```javascript
{
  status: 503,
  statusText: "Service Unavailable",
  detail: "No AI models are currently available. All providers are experiencing issues.",
  error_code: "NO_MODELS_AVAILABLE",
  available_models: []
}
```

### Authentication Failure
```javascript
{
  status: 401,
  statusText: "Unauthorized",
  detail: "Invalid or expired authentication token",
  error_code: "AUTH_FAILED"
}
```

## Testing Strategies

### 1. Manual Testing
- Open the application in demo mode
- Use browser console to enable different error scenarios
- Test UI behavior and error handling

### 2. Automated Testing
- Use the test file examples to write automated tests
- Test error boundaries and fallback UI
- Verify retry logic and error recovery

### 3. Random Error Testing
- Enable random errors to test overall application resilience
- Useful for stress testing and finding edge cases
- Adjust probability based on testing needs

## Best Practices

1. **Always clear error simulation** after testing to avoid affecting other tests
2. **Use specific scenarios** for targeted testing rather than random errors
3. **Test error recovery** by enabling and then clearing errors
4. **Combine with UI testing** to ensure proper user feedback
5. **Document expected behavior** for each error scenario in your application

## Example Test Scenarios

### Testing Retry Logic
```javascript
// Enable network timeout
window.mockOrchestratorErrors.simulateError('network_timeout');

// Trigger API call (will timeout after 30s)
// User clicks retry button

// Clear error simulation
window.mockOrchestratorErrors.clearErrorSimulation();

// Retry should now succeed
```

### Testing Fallback UI
```javascript
// Enable no models available
window.mockOrchestratorErrors.simulateError('no_models_available');

// Verify fallback UI shows appropriate message
// Verify user can't proceed with analysis
// Verify status indicators show correct state
```

### Testing Authentication Flow
```javascript
// Enable authentication failure
window.mockOrchestratorErrors.simulateError('authentication_failure');

// Verify redirect to login
// Verify error message displayed
// Verify session cleanup
```

## Integration with Real API

The error simulation only works when `VITE_API_MODE=mock` or `VITE_DEMO_MODE=true`. In production mode with real APIs, these simulation functions have no effect, ensuring they don't interfere with actual operations.