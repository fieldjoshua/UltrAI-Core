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
    // Prefer streaming endpoint by default, aggregate SSE events into a final result
    const streamed = await streamOrchestration({
      prompt,
      models,
      pattern,
      ultraModel,
      outputFormat,
    });
    if (streamed) return streamed;

    // Fallback to non-streaming endpoint if streaming fails
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
      // Map 503 gating errors into a clear message
      if (response.status === 503) {
        const detail = errorData?.detail;
        const message = typeof detail === 'object' ? (detail?.message || 'Service temporarily unavailable') : (detail || 'Service temporarily unavailable');
        return {
          error: message,
          status: 'error',
          code: 'SERVICE_UNAVAILABLE',
        };
      }
      return {
        error: (errorData && (errorData.detail || errorData.message)) || `HTTP ${response.status}`,
        status: 'error',
      };
    }

    const data = await response.json();

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

// Internal: streaming orchestration aggregator (SSE)
async function streamOrchestration({ prompt, models, pattern, ultraModel, outputFormat }) {
  try {
    const response = await fetch(`${API_BASE}/orchestrator/analyze/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'text/event-stream',
      },
      body: JSON.stringify({
        query: prompt,
        selected_models: models,
        options: {
          ultra_model: ultraModel,
          output_format: outputFormat,
        },
        // Enable streaming of model responses and synthesis chunks
        stream_stages: ['model_responses', 'synthesis_chunks'],
        chunk_size: 80,
      }),
    });

    if (!response.ok || !response.body) {
      return null;
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder('utf-8');
    let buffer = '';

    // Accumulators
    const initialResponses = {};
    const synthesisChunks = [];
    let hadError = null;

    const flushEvents = () => {
      const events = [];
      const parts = buffer.split('\n\n');
      // Keep the last incomplete part in buffer
      buffer = parts.pop() || '';
      for (const part of parts) {
        const lines = part.split('\n');
        for (const line of lines) {
          const trimmed = line.trim();
          if (trimmed.startsWith('data:')) {
            const jsonStr = trimmed.slice(5).trim();
            if (!jsonStr) continue;
            try {
              const evt = JSON.parse(jsonStr);
              events.push(evt);
            } catch (_) {
              // ignore malformed chunks
            }
          }
        }
      }
      return events;
    };

    // Read stream
    for (;;) {
      const { value, done } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const events = flushEvents();
      for (const evt of events) {
        const type = evt?.event;
        const data = evt?.data || {};
        if (type === 'MODEL_RESPONSE') {
          if (data.model && typeof data.response_text === 'string') {
            initialResponses[data.model] = data.response_text;
          }
        } else if (type === 'synthesis_chunks' || type === 'SYNTHESIS_CHUNK') {
          if (typeof data.chunk_text === 'string') {
            synthesisChunks.push(data.chunk_text);
          }
        } else if (type === 'PIPELINE_ERROR' || type === 'STAGE_ERROR') {
          hadError = data?.error || 'Streaming pipeline error';
        } else if (type === 'PIPELINE_COMPLETE') {
          // Build final result
          const text = synthesisChunks.length > 0 ? synthesisChunks.join(' ') : '';
          if (hadError) {
            return {
              status: 'error',
              error: hadError,
              ultra_response: text,
              initial_responses: Object.keys(initialResponses).length ? initialResponses : undefined,
              meta_analysis: undefined,
              ultra_synthesis: text ? { content: text } : undefined,
            };
          }
          return {
            status: 'success',
            ultra_response: text,
            models_used: models || [],
            processing_time: 0,
            pattern_used: pattern,
            initial_responses: Object.keys(initialResponses).length ? initialResponses : undefined,
            meta_analysis: undefined,
            ultra_synthesis: text ? { content: text } : undefined,
          };
        }
      }
    }

    // If stream ended without PIPELINE_COMPLETE, return what we have or null to fallback
    if (synthesisChunks.length > 0) {
      const text = synthesisChunks.join(' ');
      return {
        status: hadError ? 'error' : 'success',
        error: hadError || undefined,
        ultra_response: text,
        models_used: models || [],
        processing_time: 0,
        pattern_used: pattern,
        initial_responses: Object.keys(initialResponses).length ? initialResponses : undefined,
        ultra_synthesis: { content: text },
      };
    }

    return hadError ? { status: 'error', error: hadError } : null;
  } catch (e) {
    // If streaming not supported or fails, fallback will be used
    return null;
  }
}

export async function getAvailableModels() {
  // Use mock API in demo mode
  if (isDemoMode) {
    return mockApi.getAvailableModels();
  }

  try {
    const response = await fetch(`${API_BASE}/available-models?healthy_only=true`);
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