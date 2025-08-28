/**
 * Orchestrator API client for the frontend
 */

// Base API URL - using Vite environment variable or fallback to development port
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8081/api';

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
    // Use the real Ultra Synthesis™ API endpoint
    const payload = {
      query: prompt,
      selected_models: models || ['gpt-4o', 'claude-3-sonnet', 'gemini-1.5-pro'],
      options: {
        pattern: pattern,
        ultra_model: ultraModel,
        output_format: outputFormat
      },
      include_pipeline_details: true  // Request full pipeline details to see all stages
    };

    // Call the actual orchestrator analyze API
    const response = await fetch(`${API_BASE_URL}/orchestrator/analyze`, {
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

    // Parse the response and transform to expected format
    const data = await response.json();
    
    // Transform the backend response to match frontend expectations
    const transformedResponse = {
      status: data.success ? 'success' : 'error',
      error: data.error || null,
      
      // Extract initial responses - handle both detailed and simple formats
      initial_responses: data.results?.initial_response?.output?.responses || 
                        data.results?.initial_response?.responses || 
                        {},
      
      // Extract peer review responses if available
      peer_review_responses: data.results?.peer_review_and_revision?.output?.revised_responses || 
                            data.results?.peer_review_and_revision?.revised_responses || 
                            {},
      
      // Extract meta analysis (not used in 3-stage pipeline but kept for compatibility)
      meta_responses: data.results?.meta_analysis?.output ? {
        meta_analysis: data.results.meta_analysis.output.analysis || 'No meta-analysis available'
      } : {},
      
      // Extract peer review if available
      hyper_responses: data.results?.peer_review_and_revision?.output ? {
        peer_review: 'Peer review completed',
        revised_responses: data.results?.peer_review_and_revision?.output?.revised_responses || {}
      } : {},
      
      // Extract Ultra Synthesis™ - this is the key improvement
      ultra_response: data.results?.ultra_synthesis || 
                     data.results?.formatted_synthesis ||
                     data.results?.ultra_synthesis?.synthesis || 
                     data.results?.ultra_synthesis?.output?.synthesis || 
                     'No Ultra Synthesis™ available',
      
      // Additional metadata
      processing_time: data.processing_time || 0,
      pattern_used: pattern,
      models_used: data.results?.initial_response?.output?.successful_models || 
                   data.pipeline_info?.models_used || 
                   [],
      
      // Pipeline info
      pipeline_info: data.pipeline_info || {},
      
      // Raw data for detailed view
      raw_results: data.results
    };

    return transformedResponse;
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
