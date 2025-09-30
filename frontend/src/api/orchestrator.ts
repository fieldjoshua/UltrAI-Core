// Orchestrator API implementation
import * as mockApi from './mockOrchestrator';
import type {
  OrchestrationRequest,
  OrchestrationResponse,
  AvailableModelsResponse,
  ModelHealthResponse,
  OrchestratorStatusResponse,
  Model,
} from './types';

// Safely resolve Vite env in both browser and Jest environments
const viteEnv: any = (globalThis as any).import?.meta?.env || {};
const API_BASE = (viteEnv?.VITE_API_URL as string) || '/api';
const isDemoMode =
  viteEnv?.VITE_API_MODE === 'mock' ||
  viteEnv?.VITE_DEMO_MODE === 'true';

export async function processWithFeatherOrchestration(
  request: OrchestrationRequest,
  correlationId?: string
): Promise<OrchestrationResponse> {
  // Use mock API in demo mode
  if (isDemoMode) {
    return mockApi.processWithFeatherOrchestration(request);
  }

  const { prompt, models = null, pattern = 'comparative', ultraModel = null, outputFormat = 'plain' } = request;

  try {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };
    if (correlationId) {
      headers['X-Correlation-ID'] = correlationId;
    }
    const response = await fetch(`${API_BASE}/orchestrator/demo`, {
      method: 'POST',
      headers,
      body: JSON.stringify({
        query: prompt,
        selected_models: models,
        analysis_type: pattern,
        options: {
          ultra_model: ultraModel,
          output_format: outputFormat,
        },
      }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      return {
        error: errorData.detail || `HTTP ${response.status}`,
        status: 'error',
      } as OrchestrationResponse;
    }

    const data = await response.json();

    // Transform the response to match expected format
    return {
      status: 'success',
      ultra_response:
        data.results?.ultra_synthesis?.content || data.results?.content || '',
      models_used: data.results?.models_used || models || [],
      processing_time: data.processing_time || 0,
      pattern_used: pattern,
      initial_responses: data.results?.initial_responses,
      meta_analysis: data.results?.meta_analysis,
      ultra_synthesis: data.results?.ultra_synthesis,
      correlation_id:
        correlationId || response.headers.get('X-Correlation-ID') || '',
    };
  } catch (error: any) {
    console.error('Orchestration error:', error);
    return {
      error: error.message || 'Network error',
      status: 'error',
    } as OrchestrationResponse;
  }
}

export async function getAvailableModels(healthyOnly = false): Promise<AvailableModelsResponse> {
  // Use mock API in demo mode
  if (isDemoMode) {
    return mockApi.getAvailableModels();
  }

  // Helper function to create fetch with timeout
  const fetchWithTimeout = async (url: string, timeout = 5000) => {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);
    
    try {
      const response = await fetch(url, { signal: controller.signal });
      clearTimeout(timeoutId);
      return response;
    } catch (error) {
      clearTimeout(timeoutId);
      if (error instanceof Error && error.name === 'AbortError') {
        throw new Error(`Request timeout after ${timeout}ms`);
      }
      throw error;
    }
  };

  try {
    // Prefer healthy-only models
    const response = await fetchWithTimeout(
      `${API_BASE}/available-models?healthy_only=${healthyOnly}`,
      5000
    );
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    const healthyData = await response.json();
    const healthyList = Array.isArray(healthyData?.models)
      ? healthyData.models
      : [];
    if (healthyList.length > 0) {
      return healthyData;
    }

    // Fallback: use orchestrator-reported available models if health probe is strict
    // This prevents UI from going empty while providers are otherwise usable
    console.warn(
      '[getAvailableModels] healthy_only returned empty; falling back to /orchestrator/status'
    );
    const statusRes = await fetchWithTimeout(`${API_BASE}/orchestrator/status`, 3000);
    if (statusRes.ok) {
      const statusData = await statusRes.json();
      const reported = Array.isArray(statusData?.models?.available)
        ? statusData.models.available
        : [];
      if (reported.length > 0) {
        return { models: reported };
      }
    }

    // Final fallback: return empty
    return { models: [] };
  } catch (error) {
    console.error('Error fetching available models:', error);
    return { models: [], totalCount: 0 };
  }
}

export async function getModelHealth(): Promise<ModelHealthResponse> {
  // Use mock API in demo mode
  if (isDemoMode) {
    return mockApi.getModelHealth();
  }

  try {
    const response = await fetch(`${API_BASE}/model-health`);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error fetching model health:', error);
    throw error;
  }
}

export async function getOrchestratorStatus(): Promise<OrchestratorStatusResponse> {
  // Use mock API in demo mode
  if (isDemoMode) {
    return mockApi.getOrchestratorStatus();
  }

  try {
    const response = await fetch(`${API_BASE}/orchestrator/status`);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error fetching orchestrator status:', error);
    throw error;
  }
}

export async function checkModelStatus(modelId: string): Promise<{ available: boolean; status: string; error?: string }> {
  // Use mock API in demo mode
  if (isDemoMode) {
    return mockApi.checkModelStatus(modelId);
  }

  try {
    const response = await fetch(`${API_BASE}/models/${modelId}/status`);
    if (!response.ok) {
      return { available: false, status: 'error' };
    }
    const data = await response.json();
    return {
      available: data.available || false,
      status: data.status || 'unknown',
    };
  } catch (error: any) {
    console.error('Error checking model status:', error);
    return { available: false, status: 'error', error: error.message };
  }
}

// Legacy function names for backward compatibility
export async function getOrchestratorModels(): Promise<string[]> {
  const result = await getAvailableModels();
  // Normalize to a simple array of model names (strings)
  const models =
    result && result.models
      ? result.models
      : Array.isArray(result)
        ? result
        : [];
  return Array.isArray(models)
    ? models
        .map((m: any) => (typeof m === 'string' ? m : (m && m.name) || null))
        .filter(Boolean)
    : [];
}

interface Pattern {
  id: string;
  name: string;
  description: string;
}

export async function getOrchestratorPatterns(): Promise<Pattern[]> {
  // Return available orchestration patterns
  return [
    {
      id: 'gut',
      name: 'GUT (Generalize, Unpack, Test)',
      description: 'Three-phase reasoning pattern',
    },
    {
      id: 'comparative',
      name: 'Comparative Analysis',
      description: 'Compare insights from multiple models',
    },
    {
      id: 'consensus',
      name: 'Consensus Building',
      description: 'Find agreement across models',
    },
    {
      id: 'debate',
      name: 'Structured Debate',
      description: 'Models debate different perspectives',
    },
  ];
}

export async function processWithOrchestrator(params: OrchestrationRequest): Promise<OrchestrationResponse> {
  // Legacy function that delegates to the newer processWithFeatherOrchestration
  return processWithFeatherOrchestration(params);
}