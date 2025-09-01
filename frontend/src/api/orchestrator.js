// Orchestrator API implementation
import * as mockApi from './mockOrchestrator';

const API_BASE = import.meta.env.VITE_API_URL || '/api';
const isDemoMode = import.meta.env.VITE_API_MODE === 'mock' || import.meta.env.VITE_DEMO_MODE === 'true';

export async function processWithFeatherOrchestration({
  prompt,
  models = null,
  pattern = 'comparative',
  ultraModel = null,
  outputFormat = 'plain'
}) {
  // Use mock API in demo mode
  if (isDemoMode) {
    return mockApi.processWithFeatherOrchestration({
      prompt,
      models,
      pattern,
      ultraModel,
      outputFormat
    });
  }

  try {
    const response = await fetch(`${API_BASE}/orchestrator/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
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
      };
    }

    const data = await response.json();
    
    // Transform the response to match expected format
    return {
      status: 'success',
      ultra_response: data.results?.ultra_synthesis?.content || data.results?.content || '',
      models_used: data.results?.models_used || models || [],
      processing_time: data.processing_time || 0,
      pattern_used: pattern,
      initial_responses: data.results?.initial_responses,
      meta_analysis: data.results?.meta_analysis,
      ultra_synthesis: data.results?.ultra_synthesis,
    };
  } catch (error) {
    console.error('Orchestration error:', error);
    return {
      error: error.message || 'Network error',
      status: 'error',
    };
  }
}

export async function getAvailableModels() {
  // Use mock API in demo mode
  if (isDemoMode) {
    return mockApi.getAvailableModels();
  }

  try {
    const response = await fetch(`${API_BASE}/available-models`);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error fetching available models:', error);
    return { models: [], totalCount: 0 };
  }
}

export async function checkModelStatus(modelId) {
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
  } catch (error) {
    console.error('Error checking model status:', error);
    return { available: false, status: 'error', error: error.message };
  }
}

// Legacy function names for backward compatibility
export async function getOrchestratorModels() {
  const result = await getAvailableModels();
  return result.models || [];
}

export async function getOrchestratorPatterns() {
  // Return available orchestration patterns
  return [
    { id: 'gut', name: 'GUT (Generalize, Unpack, Test)', description: 'Three-phase reasoning pattern' },
    { id: 'comparative', name: 'Comparative Analysis', description: 'Compare insights from multiple models' },
    { id: 'consensus', name: 'Consensus Building', description: 'Find agreement across models' },
    { id: 'debate', name: 'Structured Debate', description: 'Models debate different perspectives' },
  ];
}

export async function processWithOrchestrator(params) {
  // Legacy function that delegates to the newer processWithFeatherOrchestration
  return processWithFeatherOrchestration(params);
}