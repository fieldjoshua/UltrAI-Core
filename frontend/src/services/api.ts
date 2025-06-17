import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';

// Use the environment variable for the API base URL
// In the browser, this will be set to http://localhost:8000/api
// console.log to aid debugging
console.log('API URL from env:', import.meta.env.VITE_API_URL);
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'; // Fallback just in case
console.log('Using API URL:', API_URL);

// Configuration for API calls (moved from component)
const API_CONFIG = {
  baseURL: API_URL,
  maxRetries: 3,
  retryDelay: 1000, // 1 second initial delay
  retryStatusCodes: [408, 429, 500, 502, 503, 504], // Status codes to retry on
};

// Create and configure axios instance (moved from component)
const apiClient: AxiosInstance = axios.create({
  baseURL: API_CONFIG.baseURL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 60000, // 60 seconds for LLM analysis
});

// Add retry interceptor (moved from component)
apiClient.interceptors.response.use(undefined, async (error) => {
  const { config, response = {} } = error;

  // Skip retry for specific error status codes or if we've already retried the maximum times
  if (
    !config ||
    !API_CONFIG.retryStatusCodes.includes(response.status) ||
    (config as any).__retryCount >= API_CONFIG.maxRetries // Added type assertion for __retryCount
  ) {
    return Promise.reject(error);
  }

  // Set retry count
  (config as any).__retryCount = (config as any).__retryCount || 0;
  (config as any).__retryCount++;

  // Exponential backoff delay
  const delay =
    API_CONFIG.retryDelay * Math.pow(2, (config as any).__retryCount - 1);

  // Wait for the delay
  await new Promise((resolve) => setTimeout(resolve, delay));

  // Retry the request
  return apiClient(config);
});

// List of public endpoints that don't need authentication
const PUBLIC_ENDPOINTS = [
  '/available-models',
  '/health',
  '/orchestrator/feather' // Updated to use Feather orchestration
];

// Request interceptor (keep existing)
apiClient.interceptors.request.use(
  (config) => {
    // Check if this is a public endpoint
    const isPublicEndpoint = PUBLIC_ENDPOINTS.some(endpoint => 
      config.url?.includes(endpoint)
    );

    // Only add auth token for non-public endpoints
    if (!isPublicEndpoint) {
      const token = localStorage.getItem('authToken');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }

    return config;
  },
  (error) => {
    console.error('Request error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor (keep existing token refresh logic, merge retry logic)
// Note: Retry logic moved above to avoid duplication
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Handle token refresh for 401 errors
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        // Attempt to refresh token
        const refreshToken = localStorage.getItem('refreshToken');

        if (refreshToken) {
          const response = await axios.post(`${API_URL}/auth/refresh`, {
            refreshToken,
          });

          const { token } = response.data;

          // Update token in storage
          localStorage.setItem('authToken', token);

          // Update authorization header
          originalRequest.headers.Authorization = `Bearer ${token}`;

          // Retry the original request
          return apiClient(originalRequest);
        }
      } catch (refreshError) {
        console.error('Token refresh failed:', refreshError);

        // Clear auth tokens and redirect to login
        localStorage.removeItem('authToken');
        localStorage.removeItem('refreshToken');
        // window.location.href = '/login'; // Consider alternative non-redirecting error handling
        return Promise.reject(refreshError); // Reject after failed refresh
      }
    }

    // Handle network errors
    if (!error.response && !axios.isCancel(error)) {
      // Added check for cancelled requests
      console.error('Network error:', error);
      // You could dispatch an action to show a network error toast here
    }

    // Reject error if it wasn't handled by retry or refresh logic
    return Promise.reject(error);
  }
);

// Generic request method with typed response
export const request = async <T>(config: AxiosRequestConfig): Promise<T> => {
  try {
    const response: AxiosResponse<T> = await apiClient(config);
    return response.data;
  } catch (error) {
    console.error('API request failed:', error);
    throw error;
  }
};

// Define API endpoints
export const endpoints = {
  // Auth endpoints
  auth: {
    login: '/auth/login',
    register: '/auth/register',
    refresh: '/auth/refresh',
    logout: '/auth/logout',
  },

  // Document endpoints
  documents: {
    getAll: '/documents',
    getById: (id: string) => `/documents/${id}`,
    upload: '/upload-document',
    delete: (id: string) => `/documents/${id}`,
  },

  // Analysis endpoints
  analysis: {
    analyze: '/analyze', // Simple analysis endpoint
    orchestrator: '/orchestrator/analyze', // Multi-stage orchestrator endpoint  
    analyzeWithDocs: '/analyze-with-docs',
    getById: (id: string) => `/analysis/${id}`,
    getHistory: '/analysis/history',
    availableModels: '/available-models', // Our working models endpoint
  },
};

// --- New Service Functions ---

// Define expected response structure for available models (matches our API)
interface AvailableModelsResponse {
  models: Array<{
    name: string;
    provider: string;
    status: string;
    max_tokens: number;
    cost_per_1k_tokens: number;
  }>;
  total_count: number;
  healthy_count: number;
}

// Function to fetch available models
export const fetchAvailableModels = async (): Promise<string[]> => {
  try {
    console.log(
      'Fetching available models from:',
      endpoints.analysis.availableModels
    );

    // Use actual API call to fetch models
    const response = await apiClient.get<AvailableModelsResponse>(
      endpoints.analysis.availableModels
    );

    console.log('Response from available-models endpoint:', response.data);

    // Parse our new API response format
    if (response.data && response.data.models) {
      const modelNames = response.data.models.map(model => model.name);
      console.log('Found available models:', modelNames);
      return modelNames;
    } else {
      // If the API doesn't return the expected structure, log and throw
      console.error(
        'Unexpected response format from available-models endpoint:',
        response.data
      );
      throw new Error('Invalid response format from server');
    }
  } catch (error) {
    console.error('Failed to fetch available models:', error);

    // Log more details about the error
    if (error.response) {
      console.error('Error response:', error.response.data);
      console.error('Error status:', error.response.status);
    } else if (error.request) {
      console.error('No response received:', error.request);
    } else {
      console.error('Error message:', error.message);
    }

    // Fallback to default models if API fails (matches our API models)
    console.warn('Using fallback model list');
    const fallbackModels = [
      'gpt-4',
      'gpt-4-turbo', 
      'claude-3-sonnet',
      'claude-3-haiku',
      'gemini-pro',
    ];
    console.log('Using fallback models:', fallbackModels);
    return fallbackModels;
  }
};

// Enhanced interface for AnalysisPayload with more specific types
interface AnalysisPayload {
  prompt: string;
  selected_models: string[];
  ultra_model: string;
  pattern: string;
  options?: Record<string, any>;
  output_format?: string;
  userId?: string;
}

// Enhanced response types for more accurate type checking
interface ModelResponse {
  [model: string]: string | any;
}

interface TokenCount {
  prompt_tokens: number;
  completion_tokens: number;
  total_tokens: number;
}

interface AnalysisPerformance {
  total_time_seconds: number;
  model_times: Record<string, number>;
  token_counts: Record<string, TokenCount>;
}

interface AnalysisResponse {
  status: 'success' | 'error' | 'partial_success';
  message?: string;
  error?: string;
  debug_info?: string;
  model_responses?: ModelResponse;
  ultra_response: string;
  performance?: AnalysisPerformance;
  cached?: boolean;
  id?: string;
  timestamp?: string;
}

// Enhanced multimodal analysis function
export const analyzePrompt = async (
  payload: AnalysisPayload
): Promise<AnalysisResponse> => {
  try {
    // Use orchestrator for multimodal analysis when multiple models selected
    const useOrchestrator = payload.selected_models.length > 1;
    
    let response;
    
    if (useOrchestrator) {
      // Use orchestrator for multi-model analysis
      const orchestratorPayload = {
        query: payload.prompt,
        analysis_type: payload.pattern || 'comprehensive',
        options: payload.options || {},
        selected_models: payload.selected_models
      };

      console.log('Sending orchestrator request with payload:', orchestratorPayload);
      
      response = await apiClient.post<any>(
        endpoints.analysis.orchestrator,
        orchestratorPayload
      );
      
      console.log('Received orchestrator response:', response.data);
      
      if (!response.data.success) {
        throw new Error(response.data.error || 'Orchestrator analysis failed');
      }

      // Transform orchestrator response to expected format
      const modelResponses: any = {};
      const results = response.data.results;
      
      // Check if initial_response stage has output with responses
      if (results.initial_response && results.initial_response.output && results.initial_response.output.responses) {
        Object.entries(results.initial_response.output.responses).forEach(([model, content]: [string, any]) => {
          modelResponses[model] = {
            response: typeof content === 'string' ? content : JSON.stringify(content),
            model: model,
            status: 'success'
          };
        });
      } else {
        // Fallback: check if there are any stage results we can use
        console.log('Orchestrator response structure:', results);
        for (const [stageName, stageResult] of Object.entries(results)) {
          if (stageResult && typeof stageResult === 'object' && (stageResult as any).output) {
            const output = (stageResult as any).output;
            if (output && typeof output === 'object' && output.responses) {
              Object.entries(output.responses).forEach(([model, content]: [string, any]) => {
                modelResponses[model] = {
                  response: typeof content === 'string' ? content : JSON.stringify(content),
                  model: model,
                  status: 'success'
                };
              });
              break; // Use the first stage with responses
            }
          }
        }
      }

      // Create a more readable combined response
      let combinedResponse = 'Multimodal Analysis Results:\n\n';
      
      // Add individual model responses
      if (Object.keys(modelResponses).length > 0) {
        combinedResponse += '=== Individual Model Responses ===\n\n';
        for (const [model, response] of Object.entries(modelResponses)) {
          combinedResponse += `${model}:\n${(response as any).response}\n\n`;
        }
      }
      
      // Add meta-analysis if available
      if (results.meta_analysis && results.meta_analysis.output) {
        combinedResponse += '=== Meta-Analysis ===\n\n';
        combinedResponse += typeof results.meta_analysis.output === 'string' 
          ? results.meta_analysis.output 
          : JSON.stringify(results.meta_analysis.output, null, 2);
        combinedResponse += '\n\n';
      }
      
      // Add ultra-synthesis if available
      if (results.ultra_synthesis && results.ultra_synthesis.output) {
        combinedResponse += '=== Ultra-Synthesis ===\n\n';
        combinedResponse += typeof results.ultra_synthesis.output === 'string' 
          ? results.ultra_synthesis.output 
          : JSON.stringify(results.ultra_synthesis.output, null, 2);
        combinedResponse += '\n\n';
      }
      
      // Add hyper-level analysis if available
      if (results.hyper_level_analysis && results.hyper_level_analysis.output) {
        combinedResponse += '=== Hyper-Level Analysis ===\n\n';
        combinedResponse += typeof results.hyper_level_analysis.output === 'string' 
          ? results.hyper_level_analysis.output 
          : JSON.stringify(results.hyper_level_analysis.output, null, 2);
      }
      
      // Fallback if no structured content
      if (combinedResponse === 'Multimodal Analysis Results:\n\n') {
        combinedResponse = JSON.stringify(results, null, 2);
      }

      return {
        status: 'success',
        message: 'Multimodal analysis completed successfully',
        model_responses: modelResponses,
        combined_response: combinedResponse,
        timestamp: new Date().toISOString(),
        processing_time: response.data.processing_time
      };
      
    } else {
      // Use simple analysis for single model
      const simplePayload = {
        text: payload.prompt,
        model: payload.selected_models[0] || 'gpt-4',
        temperature: 0.7
      };

      console.log('Sending simple analysis request with payload:', simplePayload);

      response = await apiClient.post<any>(
        endpoints.analysis.analyze,
        simplePayload
      );

      console.log('Received simple analysis response:', response.data);

      if (!response.data.success) {
        throw new Error(response.data.error || 'Analysis failed');
      }

      // Transform simple response to expected format
      return {
        status: 'success',
        message: 'Analysis completed successfully',
        model_responses: {
          [response.data.model_used]: {
            response: response.data.analysis,
            model: response.data.model_used,
            status: 'success'
          }
        },
        combined_response: response.data.analysis,
        timestamp: new Date().toISOString()
      };
    }
  } catch (error: any) {
    console.error('API analyzePrompt error:', error);

    // Handle different error types
    if (error.response) {
      // The request was made and the server responded with a status code
      // that falls out of the range of 2xx
      console.error('Response error data:', error.response.data);
      console.error('Response error status:', error.response.status);

      const errorMessage =
        (error.response.data && error.response.data.message) ||
        (error.response.data && error.response.data.error) ||
        `Server error: ${error.response.status}`;

      throw new Error(errorMessage);
    } else if (error.request) {
      // The request was made but no response was received
      console.error('Request error:', error.request);
      throw new Error(
        'No response from server. Please check your network connection.'
      );
    } else {
      // Something happened in setting up the request that triggered an Error
      console.error('Error message:', error.message);
      throw error;
    }
  }
};

export default apiClient;
