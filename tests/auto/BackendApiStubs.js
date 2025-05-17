/**
 * Backend API Stubs for Integration Tests
 *
 * This file provides mock implementations of the API endpoints
 * for testing the AUTO and RANDOM selection features.
 */

// Mock LLM response data
const mockLLMResponses = {
  'gpt4o': 'This is a simulated response from GPT-4o.',
  'claude37': 'Claude 3.7 Sonnet analysis indicates the following perspectives...',
  'gemini15': 'Gemini 1.5 has analyzed the prompt and found these key insights...',
  'gpt4turbo': 'GPT-4 Turbo offers the following detailed analysis...',
  'claude3opus': 'Claude 3 Opus has performed a comprehensive evaluation...',
  'gpto1': 'GPT-o1 provides this advanced analysis with high confidence...',
  'gpto3mini': 'GPT-o3 mini has processed your request and found that...',
  'llama3': 'Llama 3 has analyzed your query locally and determined...'
};

// Mock analysis patterns responses
const mockPatternResponses = {
  'confidence': 'Confidence Analysis: The models agree with high confidence that...',
  'critique': 'Critique Analysis: The models have identified these potential issues...',
  'gut': 'Gut Check Analysis: The models\' intuitive responses suggest...',
  'fact_check': 'Fact Check Analysis: The models have verified the following claims...',
  'scenario': 'Scenario Analysis: The models have explored different outcomes...',
  'stakeholder': 'Stakeholder Vision: The models have considered various stakeholder perspectives...',
  'systems': 'Systems Mapper: The models have mapped the interconnected systems involved...',
  'time_horizon': 'Time Horizon Analysis: The models have projected short and long-term implications...',
  'innovation': 'Innovation Bridge: The models have generated novel connections between...'
};

/**
 * Mock implementation of the analyze API endpoint
 * @param {Object} request - The analysis request object
 * @returns {Promise<Object>} - Simulated API response
 */
const mockAnalyzeAPI = (request) => {
  return new Promise((resolve) => {
    // Simulate network delay
    setTimeout(() => {
      // Generate model responses
      const modelResponses = {};
      request.selectedModels.forEach(model => {
        modelResponses[model] = mockLLMResponses[model] ||
          `Model ${model} has analyzed your prompt and found interesting insights.`;
      });

      // Map from frontend pattern name to backend pattern key
      const patternMap = {
        'Confidence Analysis': 'confidence',
        'Critique': 'critique',
        'Gut Check': 'gut',
        'Fact Check': 'fact_check',
        'Scenario Analysis': 'scenario',
        'Stakeholder Vision': 'stakeholder',
        'Systems Mapper': 'systems',
        'Time Horizon': 'time_horizon',
        'Innovation Bridge': 'innovation'
      };

      const patternKey = patternMap[request.pattern] || 'confidence';

      // Generate result
      resolve({
        result: mockPatternResponses[patternKey],
        model_responses: modelResponses,
        processing_time_ms: Math.floor(Math.random() * 2000) + 500,
        session_id: `test-${Date.now()}`
      });
    }, 1000); // 1 second delay
  });
};

/**
 * Mock implementation of the document upload API endpoint
 * @param {File[]} files - The files to upload
 * @returns {Promise<Object>} - Simulated API response
 */
const mockUploadDocumentsAPI = (files) => {
  return new Promise((resolve) => {
    // Simulate network delay
    setTimeout(() => {
      const processedDocuments = files.map((file, index) => ({
        id: `doc-${index}`,
        name: file.name,
        chunks: [
          { text: `Content from ${file.name}, chunk 1...`, relevance: 0.95, page: 1 },
          { text: `Content from ${file.name}, chunk 2...`, relevance: 0.87, page: 2 }
        ],
        totalChunks: 2,
        type: file.type
      }));

      resolve({
        documents: processedDocuments,
        status: 'success'
      });
    }, 1500); // 1.5 second delay
  });
};

/**
 * Mock implementation of the error handling for API failures
 * @returns {Promise<Object>} - Simulated API error
 */
const mockAPIError = () => {
  return new Promise((_, reject) => {
    setTimeout(() => {
      reject({
        status: 500,
        message: 'Simulated API error for testing error handling'
      });
    }, 500);
  });
};

module.exports = {
  mockAnalyzeAPI,
  mockUploadDocumentsAPI,
  mockAPIError
};
