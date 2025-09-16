import axios from 'axios';
import MockAdapter from 'axios-mock-adapter';
import {
  processWithFeatherOrchestration,
  getAvailableModels,
  getModelHealth,
  getOrchestratorStatus,
} from '../../api/orchestrator';

// Create axios mock
const mock = new MockAdapter(axios);

describe.skip('Orchestrator API', () => {
  afterEach(() => {
    mock.reset();
  });

  describe('processWithFeatherOrchestration', () => {
    const mockRequest = {
      prompt: 'Test query',
      models: ['gpt-4', 'claude-3'],
      pattern: 'comparative' as const,
      outputFormat: 'plain' as const,
    };

    const mockResponse = {
      status: 'success',
      ultra_response: 'Synthesized response',
      models_used: ['gpt-4', 'claude-3'],
      processing_time: 4.5,
      pattern_used: 'comparative',
      initial_responses: [
        { model: 'gpt-4', content: 'GPT-4 response' },
        { model: 'claude-3', content: 'Claude response' },
      ],
      meta_analysis: {
        content: 'Meta analysis of responses',
      },
    };

    it('should successfully process orchestration request', async () => {
      mock.onPost('/api/orchestrate').reply(200, mockResponse);

      const result = await processWithFeatherOrchestration(mockRequest);

      expect(result).toEqual(mockResponse);
      expect(mock.history.post[0].data).toBe(
        JSON.stringify({
          prompt: mockRequest.prompt,
          models: mockRequest.models,
          pattern: mockRequest.pattern,
          ultra_model: null,
          output_format: mockRequest.outputFormat,
        })
      );
    });

    it('should handle null models parameter', async () => {
      const requestWithNullModels = { ...mockRequest, models: null };
      mock.onPost('/api/orchestrate').reply(200, mockResponse);

      const result = await processWithFeatherOrchestration(
        requestWithNullModels
      );

      expect(result).toEqual(mockResponse);
      expect(JSON.parse(mock.history.post[0].data).models).toBeNull();
    });

    it('should handle ultra model parameter', async () => {
      const requestWithUltraModel = {
        ...mockRequest,
        ultraModel: 'gpt-4-turbo',
      };
      mock.onPost('/api/orchestrate').reply(200, mockResponse);

      await processWithFeatherOrchestration(requestWithUltraModel);

      expect(JSON.parse(mock.history.post[0].data).ultra_model).toBe(
        'gpt-4-turbo'
      );
    });

    it('should handle API errors', async () => {
      mock.onPost('/api/orchestrate').reply(500, {
        error: 'Internal server error',
        detail: 'Database connection failed',
      });

      await expect(
        processWithFeatherOrchestration(mockRequest)
      ).rejects.toThrow();
    });

    it('should handle network errors', async () => {
      mock.onPost('/api/orchestrate').networkError();

      await expect(
        processWithFeatherOrchestration(mockRequest)
      ).rejects.toThrow('Network Error');
    });

    it('should handle timeout errors', async () => {
      mock.onPost('/api/orchestrate').timeout();

      await expect(
        processWithFeatherOrchestration(mockRequest)
      ).rejects.toThrow();
    });

    it('should validate required fields', async () => {
      const invalidRequest = { ...mockRequest, prompt: '' };
      mock.onPost('/api/orchestrate').reply(400, {
        error: 'Validation error',
        detail: 'Prompt is required',
      });

      await expect(
        processWithFeatherOrchestration(invalidRequest)
      ).rejects.toThrow();
    });
  });

  describe('getAvailableModels', () => {
    const mockModelsResponse = {
      models: [
        {
          name: 'gpt-4',
          provider: 'openai',
          cost_per_1k_tokens: 0.03,
          is_available: true,
        },
        {
          name: 'claude-3-opus',
          provider: 'anthropic',
          cost_per_1k_tokens: 0.04,
          is_available: true,
        },
        {
          name: 'gemini-1.5-pro',
          provider: 'google',
          cost_per_1k_tokens: 0.02,
          is_available: false,
        },
      ],
    };

    it('should fetch available models', async () => {
      mock.onGet('/api/available-models').reply(200, mockModelsResponse);

      const result = await getAvailableModels();

      expect(result).toEqual(mockModelsResponse);
    });

    it('should handle healthy_only parameter', async () => {
      mock.onGet('/api/available-models?healthy_only=true').reply(200, {
        models: mockModelsResponse.models.filter(m => m.is_available),
      });

      const result = await getAvailableModels(true);

      expect(result.models).toHaveLength(2);
      expect(result.models.every(m => m.is_available)).toBe(true);
    });

    it('should return empty array on error', async () => {
      mock.onGet('/api/available-models').reply(500);

      const result = await getAvailableModels();

      expect(result).toEqual({ models: [] });
    });

    it('should handle network errors gracefully', async () => {
      mock.onGet('/api/available-models').networkError();

      const result = await getAvailableModels();

      expect(result).toEqual({ models: [] });
    });
  });

  describe('getModelHealth', () => {
    const mockHealthResponse = {
      models: {
        'gpt-4': {
          status: 'healthy',
          latency_ms: 234,
          success_rate: 0.99,
          last_check: '2024-01-15T10:30:00Z',
        },
        'claude-3': {
          status: 'degraded',
          latency_ms: 1523,
          success_rate: 0.85,
          last_check: '2024-01-15T10:30:00Z',
        },
        'gemini-1.5': {
          status: 'unhealthy',
          latency_ms: null,
          success_rate: 0,
          last_check: '2024-01-15T10:30:00Z',
          error: 'API key invalid',
        },
      },
      overall_health: 'degraded',
      healthy_models: 1,
      total_models: 3,
    };

    it('should fetch model health status', async () => {
      mock.onGet('/api/model-health').reply(200, mockHealthResponse);

      const result = await getModelHealth();

      expect(result).toEqual(mockHealthResponse);
    });

    it('should handle API errors', async () => {
      mock.onGet('/api/model-health').reply(503, {
        error: 'Service unavailable',
      });

      await expect(getModelHealth()).rejects.toThrow();
    });

    it('should include model health details', async () => {
      mock.onGet('/api/model-health').reply(200, mockHealthResponse);

      const result = await getModelHealth();

      expect(result.models['gpt-4'].status).toBe('healthy');
      expect(result.models['claude-3'].status).toBe('degraded');
      expect(result.models['gemini-1.5'].status).toBe('unhealthy');
      expect(result.models['gemini-1.5'].error).toBe('API key invalid');
    });
  });

  describe('getOrchestratorStatus', () => {
    const mockStatusResponse = {
      status: 'operational',
      version: '1.0.0',
      uptime_seconds: 3600,
      total_requests: 150,
      success_rate: 0.95,
      average_latency_ms: 450,
      active_models: 5,
      queue_size: 0,
      last_error: null,
    };

    it('should fetch orchestrator status', async () => {
      mock.onGet('/api/orchestrator/status').reply(200, mockStatusResponse);

      const result = await getOrchestratorStatus();

      expect(result).toEqual(mockStatusResponse);
    });

    it('should handle degraded status', async () => {
      const degradedStatus = {
        ...mockStatusResponse,
        status: 'degraded',
        success_rate: 0.75,
        last_error: 'High error rate detected',
      };

      mock.onGet('/api/orchestrator/status').reply(200, degradedStatus);

      const result = await getOrchestratorStatus();

      expect(result.status).toBe('degraded');
      expect(result.last_error).toBe('High error rate detected');
    });

    it('should handle API errors', async () => {
      mock.onGet('/api/orchestrator/status').reply(500);

      await expect(getOrchestratorStatus()).rejects.toThrow();
    });
  });

  describe('Demo Mode', () => {
    beforeEach(() => {
      // Set demo mode
      (global as any).import.meta.env.VITE_API_MODE = 'mock';
    });

    afterEach(() => {
      // Reset demo mode
      (global as any).import.meta.env.VITE_API_MODE = undefined;
    });

    it('should return mock data in demo mode for processWithFeatherOrchestration', async () => {
      const result = await processWithFeatherOrchestration({
        prompt: 'Demo query',
        models: null,
        pattern: 'comparative',
        outputFormat: 'plain',
      });

      expect(result.status).toBe('success');
      expect(result.ultra_response).toContain('comprehensive analysis');
      expect(result.models_used).toHaveLength(3);
      expect(mock.history.post).toHaveLength(0); // No actual API call
    });

    it('should return mock models in demo mode', async () => {
      const result = await getAvailableModels();

      expect(result.models).toHaveLength(3);
      expect(result.models[0]).toMatchObject({
        name: 'gpt-4-turbo-preview',
        provider: 'openai',
        is_available: true,
      });
      expect(mock.history.get).toHaveLength(0); // No actual API call
    });

    it('should return mock health in demo mode', async () => {
      const result = await getModelHealth();

      expect(result.overall_health).toBe('healthy');
      expect(result.healthy_models).toBe(3);
      expect(mock.history.get).toHaveLength(0); // No actual API call
    });

    it('should return mock status in demo mode', async () => {
      const result = await getOrchestratorStatus();

      expect(result.status).toBe('operational');
      expect(result.success_rate).toBe(0.98);
      expect(mock.history.get).toHaveLength(0); // No actual API call
    });
  });

  describe('Request Headers', () => {
    it('should include authorization header if set', async () => {
      axios.defaults.headers.common['Authorization'] = 'Bearer test-token';
      mock.onGet('/api/available-models').reply(200, { models: [] });

      await getAvailableModels();

      expect(mock.history.get[0].headers['Authorization']).toBe(
        'Bearer test-token'
      );
    });

    it('should include content-type header for POST requests', async () => {
      mock.onPost('/api/orchestrate').reply(200, {});

      await processWithFeatherOrchestration({
        prompt: 'Test',
        models: null,
        pattern: 'comparative',
        outputFormat: 'plain',
      });

      expect(mock.history.post[0].headers['Content-Type']).toBe(
        'application/json'
      );
    });
  });
});
