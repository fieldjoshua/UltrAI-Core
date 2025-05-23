// API Client for UltraAI Backend

class APIClient {
    constructor() {
        this.baseURL = window.location.origin;
        this.retryAttempts = 3;
        this.retryDelay = 1000;
        this.timeout = 15000; // 15 seconds
    }

    /**
     * Make HTTP request with retry logic
     */
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const token = AuthManager.getToken();
        
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...(token && { 'Authorization': `Bearer ${token}` }),
                ...options.headers
            },
            ...options
        };

        // Remove Content-Type for FormData
        if (options.body instanceof FormData) {
            delete config.headers['Content-Type'];
        }

        for (let attempt = 1; attempt <= this.retryAttempts; attempt++) {
            try {
                const controller = new AbortController();
                const timeoutId = setTimeout(() => controller.abort(), this.timeout);
                
                const response = await fetch(url, {
                    ...config,
                    signal: controller.signal
                });
                
                clearTimeout(timeoutId);

                // Handle authentication errors
                if (response.status === 401) {
                    AuthManager.clearToken();
                    NotificationManager.show('Session expired. Please log in again.', 'warning');
                    AppRouter.showAuth();
                    throw new Error('Authentication required');
                }

                // Handle other HTTP errors
                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({}));
                    throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
                }

                // Return response based on content type
                const contentType = response.headers.get('content-type');
                if (contentType && contentType.includes('application/json')) {
                    return await response.json();
                } else {
                    return await response.text();
                }

            } catch (error) {
                console.warn(`API request attempt ${attempt} failed:`, error);
                
                // Don't retry on authentication errors or client errors
                if (error.message.includes('Authentication required') || 
                    error.message.includes('HTTP 4')) {
                    throw error;
                }
                
                // Retry on network errors or server errors
                if (attempt === this.retryAttempts) {
                    throw new Error(`Request failed after ${this.retryAttempts} attempts: ${error.message}`);
                }
                
                // Wait before retrying with exponential backoff
                await this.delay(this.retryDelay * Math.pow(2, attempt - 1));
            }
        }
    }

    /**
     * Delay helper for retry logic
     */
    async delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    /**
     * GET request
     */
    async get(endpoint, params = {}) {
        const url = new URL(endpoint, this.baseURL);
        Object.keys(params).forEach(key => 
            url.searchParams.append(key, params[key])
        );
        
        return this.request(url.pathname + url.search, {
            method: 'GET'
        });
    }

    /**
     * POST request
     */
    async post(endpoint, data = {}) {
        return this.request(endpoint, {
            method: 'POST',
            body: data instanceof FormData ? data : JSON.stringify(data)
        });
    }

    /**
     * PUT request
     */
    async put(endpoint, data = {}) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }

    /**
     * DELETE request
     */
    async delete(endpoint) {
        return this.request(endpoint, {
            method: 'DELETE'
        });
    }

    /**
     * File upload with progress tracking
     */
    async uploadFile(file, onProgress = null) {
        return new Promise((resolve, reject) => {
            const formData = new FormData();
            formData.append('file', file);
            
            const xhr = new XMLHttpRequest();
            
            // Track upload progress
            if (onProgress) {
                xhr.upload.addEventListener('progress', (e) => {
                    if (e.lengthComputable) {
                        const percentComplete = (e.loaded / e.total) * 100;
                        onProgress(percentComplete);
                    }
                });
            }
            
            xhr.onload = () => {
                if (xhr.status >= 200 && xhr.status < 300) {
                    try {
                        const response = JSON.parse(xhr.responseText);
                        resolve(response);
                    } catch (error) {
                        resolve(xhr.responseText);
                    }
                } else if (xhr.status === 401) {
                    AuthManager.clearToken();
                    NotificationManager.show('Session expired. Please log in again.', 'warning');
                    AppRouter.showAuth();
                    reject(new Error('Authentication required'));
                } else {
                    try {
                        const errorData = JSON.parse(xhr.responseText);
                        reject(new Error(errorData.detail || `Upload failed: ${xhr.statusText}`));
                    } catch {
                        reject(new Error(`Upload failed: ${xhr.statusText}`));
                    }
                }
            };
            
            xhr.onerror = () => reject(new Error('Upload failed: Network error'));
            xhr.ontimeout = () => reject(new Error('Upload failed: Timeout'));
            
            xhr.open('POST', `${this.baseURL}/documents/`);
            xhr.timeout = 30000; // 30 seconds for file uploads
            
            const token = AuthManager.getToken();
            if (token) {
                xhr.setRequestHeader('Authorization', `Bearer ${token}`);
            }
            
            xhr.send(formData);
        });
    }
}

/**
 * API Service Methods
 */
class APIService {
    constructor() {
        this.client = new APIClient();
    }

    // Health Check
    async checkHealth() {
        return this.client.get('/health');
    }

    // Authentication
    async login(email, password) {
        return this.client.post('/auth/login', { email, password });
    }

    async register(email, username, password) {
        return this.client.post('/auth/register', { email, username, password });
    }

    async verifyAuth() {
        return this.client.get('/auth/verify');
    }

    // Documents
    async uploadDocument(file, onProgress = null) {
        return this.client.uploadFile(file, onProgress);
    }

    async getDocuments() {
        return this.client.get('/documents/');
    }

    async getDocument(documentId) {
        return this.client.get(`/documents/${documentId}`);
    }

    async deleteDocument(documentId) {
        return this.client.delete(`/documents/${documentId}`);
    }

    // Analyses
    async createAnalysis(documentId, prompt, llmProvider = 'openai') {
        return this.client.post('/analyses/', {
            document_id: documentId,
            prompt: prompt,
            llm_provider: llmProvider
        });
    }

    async getAnalyses() {
        return this.client.get('/analyses/');
    }

    async getAnalysis(analysisId) {
        return this.client.get(`/analyses/${analysisId}`);
    }

    async deleteAnalysis(analysisId) {
        return this.client.delete(`/analyses/${analysisId}`);
    }
}

/**
 * Error Handler for API calls
 */
class APIErrorHandler {
    static handle(error, context = 'API call') {
        console.error(`${context} failed:`, error);
        
        let message = 'An unexpected error occurred';
        let type = 'error';
        
        if (error.message.includes('Authentication required')) {
            message = 'Please log in to continue';
            type = 'warning';
        } else if (error.message.includes('Network error')) {
            message = 'Network connection error. Please check your internet connection.';
        } else if (error.message.includes('Timeout')) {
            message = 'Request timed out. Please try again.';
        } else if (error.message.includes('HTTP 400')) {
            message = 'Invalid request. Please check your input.';
        } else if (error.message.includes('HTTP 403')) {
            message = 'Access denied. You do not have permission to perform this action.';
        } else if (error.message.includes('HTTP 404')) {
            message = 'Resource not found.';
        } else if (error.message.includes('HTTP 429')) {
            message = 'Too many requests. Please wait a moment and try again.';
        } else if (error.message.includes('HTTP 5')) {
            message = 'Server error. Please try again later.';
        } else {
            message = error.message;
        }
        
        NotificationManager.show(message, type);
        return { message, type };
    }
}

// Create global API instance
window.api = new APIService();
window.APIErrorHandler = APIErrorHandler;