/**
 * API client for UltrAI Orchestrator
 *
 * This module provides functions to interact with the
 * modular orchestration system that was developed in the CLI.
 */

import { getApiBaseUrl, reportApiError } from './config';

// Base API URL - will be discovered dynamically
let API_BASE_URL = 'http://localhost:8085';

/**
 * Get available models for orchestration
 * @returns {Promise<Array<string>>} List of available model names
 */
export const getOrchestratorModels = async () => {
  try {
    // Ensure API discovery has completed
    if (!API_BASE_URL.includes('localhost')) {
      API_BASE_URL = await getApiBaseUrl();
    }

    const response = await fetch(`${API_BASE_URL}/api/orchestrator/models`);
    const data = await response.json();

    if (data.status === 'success') {
      return data.models;
    } else {
      console.warn('Failed to get orchestrator models, using fallback models');
      return [
        'openai-gpt4o',
        'anthropic-claude',
        'google-gemini',
        'deepseek-chat',
      ];
    }
  } catch (error) {
    const errorMessage = `Error fetching orchestrator models: ${error.message}`;
    reportApiError(errorMessage, 'get-orchestrator-models');
    console.error(errorMessage);

    // Return fallback models
    return [
      'openai-gpt4o',
      'anthropic-claude',
      'google-gemini',
      'deepseek-chat',
    ];
  }
};

/**
 * Process a prompt using the orchestration system
 * @param {Object} params - Processing parameters
 * @param {string} params.prompt - The prompt to process
 * @param {Array<string>} [params.models] - Models to use (optional, uses all available if omitted)
 * @param {string} [params.leadModel] - Primary model for synthesis (optional)
 * @param {string} [params.analysisType] - Type of analysis (comparative or factual, default: comparative)
 * @param {Object} [params.options] - Additional options
 * @returns {Promise<Object>} Orchestration results
 */
export const processWithOrchestrator = async ({
  prompt,
  models = null,
  leadModel = null,
  analysisType = 'comparative',
  options = {},
}) => {
  try {
    // Ensure API discovery has completed
    if (!API_BASE_URL.includes('localhost')) {
      API_BASE_URL = await getApiBaseUrl();
    }

    // Prepare the request payload
    const payload = {
      prompt,
      models,
      lead_model: leadModel,
      analysis_type: analysisType,
      options,
    };

    // Call the API
    const response = await fetch(`${API_BASE_URL}/api/orchestrator/process`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    // Check for response errors
    if (!response.ok) {
      const errorText = await response.text();
      const errorMessage = `API error: ${response.status} - ${errorText}`;
      reportApiError(errorMessage, 'process-with-orchestrator');
      throw new Error(errorMessage);
    }

    // Parse the response
    return await response.json();
  } catch (error) {
    const errorMessage = `Error processing with orchestrator: ${error.message}`;
    reportApiError(errorMessage, 'process-with-orchestrator-error');
    console.error(errorMessage);

    // Create a fallback response
    return {
      status: 'error',
      error: error.message || 'Unknown error occurred',
      initial_responses: [],
      analysis_results: {
        type: analysisType,
        summary: 'Error occurred during analysis',
      },
      synthesis: {
        model: leadModel || 'unknown',
        provider: 'error',
        response: 'Failed to generate a response due to an error.',
      },
    };
  }
};

// Default export for compatibility
export default {
  getOrchestratorModels,
  processWithOrchestrator,
};
