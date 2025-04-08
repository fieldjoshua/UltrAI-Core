import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';

// Define API base URL
const API_URL = import.meta.env?.VITE_API_URL || 'http://localhost:8000/api';

// Create and configure axios instance
const apiClient: AxiosInstance = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
    timeout: 15000, // 15 seconds
});

// Request interceptor
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

// Response interceptor
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
                window.location.href = '/login';
            }
        }

        // Handle network errors
        if (!error.response) {
            console.error('Network error:', error);
            // You could dispatch an action to show a network error toast here
        }

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
    },
};

export default apiClient;