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
  timeout: 15000, // 15 seconds
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

// Request interceptor (keep existing)
apiClient.interceptors.request.use(
  (config) => {
    // Get token from storage
    const token = localStorage.getItem('authToken');

    // If token exists, add to headers
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
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
    analyze: '/analyze',
    analyzeWithDocs: '/analyze-with-docs',
    getById: (id: string) => `/analysis/${id}`,
    getHistory: '/analysis/history',
    availableModels: '/available-models', // Added endpoint definition
  },
};

// --- New Service Functions ---

// Define expected response structure for available models
interface AvailableModelsResponse {
  available_models: string[];
  // Add other fields if the API returns more
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

    // Properly handle the API response
    if (response.data && response.data.available_models) {
      console.log('Found available models:', response.data.available_models);
      return response.data.available_models;
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

    // Fallback to default models if API fails
    console.warn('Using fallback model list');
    const fallbackModels = [
      'gpt4o',
      'gpt4turbo',
      'claude37',
      'claude3opus',
      'gemini15',
      'llama3',
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

// Enhanced error handling in the analyze function
export const analyzePrompt = async (
  payload: AnalysisPayload
): Promise<AnalysisResponse> => {
  try {
    // Format the payload to match the backend's expected format
    const formattedPayload = {
      prompt: payload.prompt,
      selected_models: payload.selected_models, // CORRECT: Match backend expected field name
      ultra_model: payload.ultra_model, // CORRECT: Match backend expected field name
      pattern: payload.pattern,
      options: payload.options || {},
      output_format: payload.output_format || 'txt',
      userId: payload.userId || null,
    };

    console.log('Sending analysis request with payload:', formattedPayload);

    const response = await apiClient.post<AnalysisResponse>(
      endpoints.analysis.analyze,
      formattedPayload
    );

    console.log('Received analysis response:', response.data);

    // Handle successful but error-containing responses
    if (response.data.status === 'error') {
      throw new Error(
        response.data.message ||
          response.data.error ||
          'An error occurred during analysis'
      );
    }

    if (response.data.status === 'partial_success') {
      console.warn('Partial success in analysis:', response.data.message);
    }

    return response.data;
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
