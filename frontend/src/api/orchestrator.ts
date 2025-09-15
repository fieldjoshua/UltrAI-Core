import axios from 'axios';

// @ts-ignore
const API_URL = (globalThis.import?.meta?.env?.VITE_API_URL) || 'http://localhost:8000/api';
// @ts-ignore
const API_MODE = (globalThis.import?.meta?.env?.VITE_API_MODE) || null;

export interface Model {
  name: string;
  provider: string;
  cost_per_1k_tokens: number;
  is_available: boolean;
}

export interface OrchestratorRequest {
  prompt: string;
  models: string[] | null;
  pattern: 'comparative' | 'consensus' | 'creative' | 'analytical';
  ultraModel?: string | null;
  outputFormat: 'plain' | 'json' | 'markdown';
}

export interface OrchestratorResponse {
  status: 'success' | 'partial' | 'error';
  ultra_response: string;
  models_used: string[];
  processing_time: number;
  pattern_used: string;
  initial_responses: Array<{
    model: string;
    content: string;
  }>;
  meta_analysis?: {
    content: string;
  };
}

export interface ModelHealthResponse {
  models: {
    [key: string]: {
      status: 'healthy' | 'degraded' | 'unhealthy';
      latency_ms: number | null;
      success_rate: number;
      last_check: string;
      error?: string;
    };
  };
  overall_health: 'healthy' | 'degraded' | 'unhealthy';
  healthy_models: number;
  total_models: number;
}

export interface OrchestratorStatusResponse {
  status: 'operational' | 'degraded' | 'down';
  version: string;
  uptime_seconds: number;
  total_requests: number;
  success_rate: number;
  average_latency_ms: number;
  active_models: number;
  queue_size: number;
  last_error: string | null;
}

// Mock data for demo mode
const mockOrchestratorResponse: OrchestratorResponse = {
  status: 'success',
  ultra_response: `Based on my comprehensive analysis across multiple AI models, I can provide you with a synthesized perspective that leverages the unique strengths of each model:

**Key Insights:**
1. The consensus across models indicates a strong alignment on the core aspects of your query
2. Each model contributed unique perspectives that enhance the overall analysis
3. The synthesis reveals patterns that individual models might have missed

**Detailed Analysis:**
The multi-model approach has identified several critical factors that warrant consideration. By combining the analytical precision of GPT-4, the creative insights of Claude, and the comprehensive knowledge of Gemini, we've developed a nuanced understanding that surpasses what any single model could provide.

**Recommendations:**
- Consider implementing the suggested approach in phases to minimize risk
- Monitor the key metrics identified by our consensus analysis
- Leverage the diverse perspectives to inform strategic decision-making

This ultra-synthesis represents the collective intelligence of leading AI models, providing you with a robust foundation for your next steps.`,
  models_used: ['gpt-4-turbo-preview', 'claude-3-opus', 'gemini-1.5-pro'],
  processing_time: 8.234,
  pattern_used: 'comparative',
  initial_responses: [
    {
      model: 'gpt-4-turbo-preview',
      content: 'GPT-4 analysis focusing on structured reasoning and comprehensive coverage...'
    },
    {
      model: 'claude-3-opus',
      content: 'Claude-3 perspective emphasizing nuanced understanding and ethical considerations...'
    },
    {
      model: 'gemini-1.5-pro',
      content: 'Gemini analysis providing broad context and innovative solutions...'
    }
  ],
  meta_analysis: {
    content: 'Meta-analysis reveals strong convergence on key themes with complementary insights...'
  }
};

const mockModels: Model[] = [
  { name: 'gpt-4-turbo-preview', provider: 'openai', cost_per_1k_tokens: 0.03, is_available: true },
  { name: 'claude-3-opus', provider: 'anthropic', cost_per_1k_tokens: 0.04, is_available: true },
  { name: 'gemini-1.5-pro', provider: 'google', cost_per_1k_tokens: 0.02, is_available: true }
];

export async function processWithFeatherOrchestration(request: OrchestratorRequest): Promise<OrchestratorResponse> {
  if (API_MODE === 'mock') {
    // Simulate processing delay
    await new Promise(resolve => setTimeout(resolve, 2000));
    return mockOrchestratorResponse;
  }

  const response = await axios.post(`${API_URL}/orchestrate`, {
    prompt: request.prompt,
    models: request.models,
    pattern: request.pattern,
    ultra_model: request.ultraModel || null,
    output_format: request.outputFormat,
  });

  return response.data;
}

export async function getAvailableModels(healthyOnly = false): Promise<{ models: Model[] }> {
  if (API_MODE === 'mock') {
    return { models: mockModels };
  }

  try {
    const url = healthyOnly 
      ? `${API_URL}/available-models?healthy_only=true`
      : `${API_URL}/available-models`;
    const response = await axios.get(url);
    return response.data;
  } catch (error) {
    console.error('Error fetching models:', error);
    return { models: [] };
  }
}

export async function getModelHealth(): Promise<ModelHealthResponse> {
  if (API_MODE === 'mock') {
    return {
      models: {
        'gpt-4-turbo-preview': {
          status: 'healthy',
          latency_ms: 234,
          success_rate: 0.99,
          last_check: new Date().toISOString()
        },
        'claude-3-opus': {
          status: 'healthy',
          latency_ms: 189,
          success_rate: 0.98,
          last_check: new Date().toISOString()
        },
        'gemini-1.5-pro': {
          status: 'healthy',
          latency_ms: 256,
          success_rate: 0.97,
          last_check: new Date().toISOString()
        }
      },
      overall_health: 'healthy',
      healthy_models: 3,
      total_models: 3
    };
  }

  const response = await axios.get(`${API_URL}/model-health`);
  return response.data;
}

export async function getOrchestratorStatus(): Promise<OrchestratorStatusResponse> {
  if (API_MODE === 'mock') {
    return {
      status: 'operational',
      version: '1.0.0',
      uptime_seconds: 86400,
      total_requests: 1234,
      success_rate: 0.98,
      average_latency_ms: 450,
      active_models: 3,
      queue_size: 0,
      last_error: null
    };
  }

  const response = await axios.get(`${API_URL}/orchestrator/status`);
  return response.data;
}