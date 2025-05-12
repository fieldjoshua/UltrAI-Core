/**
 * API client for UltrAI Orchestrator
 * 
 * This module provides functions to interact with the 
 * modular orchestration system that was developed in the CLI.
 */

// Base API URL - adjusted to use port 8085
const API_BASE_URL = 'http://localhost:8085';

/**
 * Get available models for orchestration
 * @returns {Promise<Array<string>>} List of available model names
 */
const getOrchestratorModels = async () => {
  try {
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
        'deepseek-chat'
      ];
    }
  } catch (error) {
    console.error('Error fetching orchestrator models:', error);
    // Return fallback models
    return [
      'openai-gpt4o',
      'anthropic-claude',
      'google-gemini',
      'deepseek-chat'
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
const processWithOrchestrator = async ({
  prompt,
  models = null,
  leadModel = null,
  analysisType = 'comparative',
  options = {}
}) => {
  try {
    // Prepare the request payload
    const payload = {
      prompt,
      models,
      lead_model: leadModel,
      analysis_type: analysisType,
      options
    };

    // Call the API
    const response = await fetch(`${API_BASE_URL}/api/orchestrator/process`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
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
        summary: 'Error occurred during analysis'
      },
      synthesis: {
        model: leadModel || 'unknown',
        provider: 'error',
        response: 'Failed to generate a response due to an error.'
      }
    };
  }
};

// Export the API functions
module.exports = {
  getOrchestratorModels,
  processWithOrchestrator
};