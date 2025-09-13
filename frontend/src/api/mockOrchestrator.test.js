// Test file demonstrating error simulation capabilities in mockOrchestrator
import { 
  processWithFeatherOrchestration, 
  getAvailableModels,
  checkModelStatus,
  simulateError,
  clearErrorSimulation,
  ERROR_SCENARIOS 
} from './mockOrchestrator';

describe('Mock Orchestrator Error Simulation', () => {
  afterEach(() => {
    // Clear error simulation after each test
    clearErrorSimulation();
  });

  describe('Network Timeout Scenarios', () => {
    it('should simulate network timeout in processWithFeatherOrchestration', async () => {
      simulateError(ERROR_SCENARIOS.NETWORK_TIMEOUT);
      
      const startTime = Date.now();
      await expect(
        processWithFeatherOrchestration({
          prompt: 'Test query',
          models: ['gpt-4', 'claude-3']
        })
      ).rejects.toThrow('Network timeout: Request took too long to complete');
      
      const elapsedTime = Date.now() - startTime;
      expect(elapsedTime).toBeGreaterThanOrEqual(30000); // Should wait 30 seconds
    }, 35000); // Increase test timeout

    it('should simulate network timeout in getAvailableModels', async () => {
      simulateError(ERROR_SCENARIOS.NETWORK_TIMEOUT);
      
      await expect(getAvailableModels()).rejects.toThrow('Network timeout');
    }, 35000);

    it('should simulate network timeout in checkModelStatus', async () => {
      simulateError(ERROR_SCENARIOS.NETWORK_TIMEOUT);
      
      await expect(checkModelStatus('gpt-4')).rejects.toThrow('Network timeout');
    }, 35000);
  });

  describe('No Models Available Scenarios', () => {
    it('should simulate no models available in processWithFeatherOrchestration', async () => {
      simulateError(ERROR_SCENARIOS.NO_MODELS_AVAILABLE);
      
      await expect(
        processWithFeatherOrchestration({
          prompt: 'Test query'
        })
      ).rejects.toMatchObject({
        message: 'No models available',
        status: 503,
        response: expect.objectContaining({
          status: 503,
          statusText: 'Service Unavailable'
        })
      });
    });

    it('should return empty models list in getAvailableModels', async () => {
      simulateError(ERROR_SCENARIOS.NO_MODELS_AVAILABLE);
      
      const result = await getAvailableModels();
      expect(result).toEqual({
        models: [],
        totalCount: 0,
        providers: {
          openai: [],
          anthropic: [],
          google: [],
          groq: []
        },
        modelInfos: {},
        error: 'No models available'
      });
    });

    it('should return unavailable status in checkModelStatus', async () => {
      simulateError(ERROR_SCENARIOS.NO_MODELS_AVAILABLE);
      
      const result = await checkModelStatus('gpt-4');
      expect(result).toEqual({
        available: false,
        status: 'all_models_unavailable',
        lastChecked: expect.any(String),
        error: 'No models are currently available'
      });
    });
  });

  describe('Authentication Failure Scenarios', () => {
    it('should simulate authentication failure in processWithFeatherOrchestration', async () => {
      simulateError(ERROR_SCENARIOS.AUTHENTICATION_FAILURE);
      
      await expect(
        processWithFeatherOrchestration({
          prompt: 'Test query'
        })
      ).rejects.toMatchObject({
        message: 'Authentication failed',
        status: 401,
        response: expect.objectContaining({
          status: 401,
          statusText: 'Unauthorized'
        })
      });
    });

    it('should simulate authentication failure in getAvailableModels', async () => {
      simulateError(ERROR_SCENARIOS.AUTHENTICATION_FAILURE);
      
      await expect(getAvailableModels()).rejects.toMatchObject({
        message: 'Authentication failed',
        status: 401
      });
    });

    it('should simulate authentication failure in checkModelStatus', async () => {
      simulateError(ERROR_SCENARIOS.AUTHENTICATION_FAILURE);
      
      await expect(checkModelStatus('gpt-4')).rejects.toMatchObject({
        message: 'Authentication failed',
        status: 401
      });
    });
  });

  describe('Random Error Simulation', () => {
    it('should randomly simulate errors when enabled', async () => {
      simulateError('random');
      
      // Run multiple requests to test random errors
      const results = [];
      for (let i = 0; i < 10; i++) {
        try {
          const result = await getAvailableModels();
          results.push({ success: true, result });
        } catch (error) {
          results.push({ success: false, error: error.message });
        }
      }
      
      // Should have some successes and some failures
      const successes = results.filter(r => r.success).length;
      const failures = results.filter(r => !r.success).length;
      
      expect(successes).toBeGreaterThan(0);
      expect(failures).toBeGreaterThan(0);
      console.log(`Random error test: ${successes} successes, ${failures} failures out of 10 attempts`);
    });
  });

  describe('Timed Error Simulation', () => {
    it('should simulate errors for a specific duration', async () => {
      // Simulate errors for 2 seconds
      simulateError(ERROR_SCENARIOS.AUTHENTICATION_FAILURE, 2000);
      
      // Should fail immediately
      await expect(getAvailableModels()).rejects.toThrow('Authentication failed');
      
      // Wait for simulation to end
      await new Promise(resolve => setTimeout(resolve, 2500));
      
      // Should succeed after timeout
      const result = await getAvailableModels();
      expect(result.models.length).toBeGreaterThan(0);
    });
  });
});

// Example usage in browser console:
/*
// Enable network timeout errors
window.mockOrchestratorErrors.simulateError('network_timeout');

// Enable random errors (30% probability)
window.mockOrchestratorErrors.simulateError('random');

// Enable authentication failures for 10 seconds
window.mockOrchestratorErrors.simulateError('authentication_failure', 10000);

// Clear all error simulation
window.mockOrchestratorErrors.clearErrorSimulation();

// Set custom random error probability (50%)
window.mockOrchestratorErrors.setRandomErrorProbability(0.5);

// View available error scenarios
console.log(window.mockOrchestratorErrors.scenarios);
*/