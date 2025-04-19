import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';

// HARDCODED: Absolutely force the API URL to port 8000
const API_URL = 'http://localhost:8000/api';

console.log('HARDCODED API URL (ignoring env vars):', API_URL);

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
    const delay = API_CONFIG.retryDelay * Math.pow(2, (config as any).__retryCount - 1);

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
        if (!error.response && !axios.isCancel(error)) { // Added check for cancelled requests
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
        // Use actual API call to fetch models
        const response = await apiClient.get<AvailableModelsResponse>(endpoints.analysis.availableModels);

        // Properly handle the API response
        if (response.data && response.data.available_models) {
            return response.data.available_models;
        } else {
            // If the API doesn't return the expected structure, log and throw
            console.error('Unexpected response format from available-models endpoint:', response.data);
            throw new Error('Invalid response format from server');
        }
    } catch (error) {
        console.error('Failed to fetch available models:', error);

        // Fallback to default models if API fails
        console.warn('Using fallback model list');
        return [
            'gpt4o',
            'gpt4turbo',
            'gpto3mini',
            'claude37',
            'claude3opus',
            'gemini15',
            'llama3',
        ];
    }
};

// Define payload structure for analysis endpoint
interface AnalysisPayload {
    prompt: string;
    selected_models: string[];
    ultra_model: string | null;
    pattern: string;
    options?: any; // Define more specific type if possible
    output_format?: string;
    userId?: string | null;
    // Add other fields like document IDs if needed for this specific endpoint
}

// Define expected response structure for analysis endpoint
interface AnalysisResponse {
    ultra_response: string;
    model_responses?: Record<string, string>; // Add model responses field
    cached?: boolean;
    id?: string;
    timestamp?: string;
    // Add other fields returned by the API (results, performance, etc.)
}

// Function to call the analyze endpoint
export const analyzePrompt = async (payload: AnalysisPayload): Promise<AnalysisResponse> => {
    try {
        console.log('Sending analysis payload via api service:', payload);

        // Use the generic request helper or apiClient directly
        const response = await request<AnalysisResponse>({
            url: endpoints.analysis.analyze,
            method: 'POST',
            data: payload,
        });

        // Ensure we have individual model responses
        if (!response.model_responses) {
            // If the server didn't provide individual model responses, create a mock structure
            // This ensures backward compatibility with older API versions
            response.model_responses = {};

            // Add a marker to indicate these are missing from the API
            payload.selected_models.forEach(model => {
                response.model_responses![model] = `Response from ${model} not provided by the API.
                This may be a limitation of the current server implementation.`;
            });
        }

        return response;
    } catch (error) {
        console.error('Analysis API call failed:', error);
        throw error;
    }
};

export default apiClient;
