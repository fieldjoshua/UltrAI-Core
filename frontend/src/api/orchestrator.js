/**
 * Orchestrator API client for the frontend
 */

// Base API URL - using environment variable or fallback to development port
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8081/api';

/**
 * Get available models for orchestration
 * @returns {Promise<Array<string>>} List of available model names
 */
export async function getOrchestratorModels() {
  try {
    // Try to fetch available models from the API
    const response = await fetch(`${API_BASE_URL}/orchestrator/models`);
    const data = await response.json();

    if (data.status === 'success') {
      return data.models;
    } else {
      console.warn('Failed to get orchestrator models, using fallback models');
      return [
        'openai-gpt4o',
        'anthropic-claude',
        'google-gemini',
        'local-hybrid',
      ];
    }
  } catch (error) {
    console.error('Error fetching orchestrator models:', error);
    // Return fallback models if API call fails
    return [
      'openai-gpt4o',
      'anthropic-claude',
      'google-gemini',
      'local-hybrid',
    ];
  }
}

/**
 * Get available analysis patterns for orchestration
 * @returns {Promise<Array<Object>>} List of available analysis patterns
 */
export async function getOrchestratorPatterns() {
  try {
    // Try to fetch available patterns from the API
    const response = await fetch(`${API_BASE_URL}/orchestrator/patterns`);
    const data = await response.json();

    if (data.status === 'success') {
      return data.patterns;
    } else {
      console.warn('Failed to get orchestrator patterns, using fallback patterns');
      return [
        { name: 'gut', description: 'Gut-based intuitive analysis' },
        { name: 'confidence', description: 'Confidence scoring and agreement tracking' },
        { name: 'critique', description: 'Structured critique and revision process' },
        { name: 'fact_check', description: 'Rigorous fact-checking process' },
        { name: 'perspective', description: 'Multi-perspective analysis' },
        { name: 'scenario', description: 'Scenario-based analysis' }
      ];
    }
  } catch (error) {
    console.error('Error fetching orchestrator patterns:', error);
    // Return fallback patterns if API call fails
    return [
      { name: 'gut', description: 'Gut-based intuitive analysis' },
      { name: 'confidence', description: 'Confidence scoring and agreement tracking' },
      { name: 'critique', description: 'Structured critique and revision process' },
      { name: 'fact_check', description: 'Rigorous fact-checking process' },
      { name: 'perspective', description: 'Multi-perspective analysis' },
      { name: 'scenario', description: 'Scenario-based analysis' }
    ];
  }
}

/**
 * Process a prompt using the sophisticated 4-stage Feather orchestration
 * @param {Object} params - Processing parameters
 * @param {string} params.prompt - The prompt to process
 * @param {Array<string>} [params.models] - Models to use (optional, uses all available if omitted)
 * @param {string} [params.pattern] - Analysis pattern to use (gut, confidence, critique, etc.)
 * @param {string} [params.ultraModel] - The model to use for ultra synthesis (optional)
 * @param {string} [params.outputFormat] - Output format (plain, markdown, json)
 * @returns {Promise<Object>} 4-stage Feather orchestration results
 */
export async function processWithFeatherOrchestration({
  prompt,
  models = null,
  pattern = 'gut',
  ultraModel = null,
  outputFormat = 'plain'
}) {
  try {
    // Prepare the request payload for sophisticated orchestration
    const payload = {
      prompt,
      models,
      pattern,
      ultra_model: ultraModel,
      output_format: outputFormat
    };

    // Call the sophisticated Feather orchestration API
    const response = await fetch(`${API_BASE_URL}/orchestrator/feather`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    // Check for response errors
    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`API error: ${response.status} - ${errorText}`);
    }

    // Parse the response
    return await response.json();
  } catch (error) {
    console.error('Error processing with Feather orchestration:', error);

    // Create a fallback response
    return {
      status: 'error',
      error: error.message || 'Unknown error occurred',
      initial_responses: {},
      meta_responses: {},
      hyper_responses: {},
      ultra_response: 'Failed to generate a response due to an error.',
      processing_time: 0,
      pattern_used: pattern,
      models_used: []
    };
  }
}

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
export async function processWithOrchestrator({
  prompt,
  models = null,
  leadModel = null,
  analysisType = 'comparative',
  options = {},
}) {
  try {
    // Prepare the request payload
    const payload = {
      prompt,
      models,
      lead_model: leadModel,
      analysis_type: analysisType,
      options,
    };

    // Call the legacy API (kept for backward compatibility)
    const response = await fetch(`${API_BASE_URL}/orchestrator/process`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    // Check for response errors
    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`API error: ${response.status} - ${errorText}`);
    }

    // Parse the response
    return await response.json();
  } catch (error) {
    console.error('Error processing with orchestrator:', error);

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
}

// Default export
export default {
  getOrchestratorModels,
  getOrchestratorPatterns,
  processWithFeatherOrchestration,
  processWithOrchestrator,
};
