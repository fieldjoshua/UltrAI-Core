# API Integration Patterns

**Date**: 2025-05-22
**ACTION**: integrated-frontend-implementation

## Authentication Pattern

### JWT Token Management
```javascript
// JWT Storage and Retrieval
class AuthManager {
    static TOKEN_KEY = 'ultra_auth_token';
    
    static setToken(token) {
        localStorage.setItem(this.TOKEN_KEY, token);
    }
    
    static getToken() {
        return localStorage.getItem(this.TOKEN_KEY);
    }
    
    static clearToken() {
        localStorage.removeItem(this.TOKEN_KEY);
    }
    
    static isAuthenticated() {
        const token = this.getToken();
        if (!token) return false;
        
        // Check if token is expired
        try {
            const payload = JSON.parse(atob(token.split('.')[1]));
            return payload.exp > Date.now() / 1000;
        } catch {
            return false;
        }
    }
}
```

### API Request Pattern
```javascript
// Unified API Client
class APIClient {
    constructor() {
        this.baseURL = window.location.origin;
        this.retryAttempts = 3;
        this.retryDelay = 1000;
    }
    
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
        
        for (let attempt = 1; attempt <= this.retryAttempts; attempt++) {
            try {
                const response = await fetch(url, config);
                
                if (response.status === 401) {
                    AuthManager.clearToken();
                    window.location.href = '/login.html';
                    return;
                }
                
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                
                return await response.json();
            } catch (error) {
                if (attempt === this.retryAttempts) {
                    throw error;
                }
                await this.delay(this.retryDelay * attempt);
            }
        }
    }
    
    async delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}
```

## Authentication Endpoints

### Login Pattern
```javascript
async function login(email, password) {
    try {
        const response = await api.request('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ email, password })
        });
        
        AuthManager.setToken(response.access_token);
        window.location.href = '/dashboard.html';
    } catch (error) {
        showError('Login failed: ' + error.message);
    }
}
```

### Registration Pattern
```javascript
async function register(email, username, password) {
    try {
        const response = await api.request('/auth/register', {
            method: 'POST',
            body: JSON.stringify({ email, username, password })
        });
        
        showSuccess('Registration successful! Please log in.');
        // Auto-login or redirect to login form
    } catch (error) {
        showError('Registration failed: ' + error.message);
    }
}
```

## Document Management Patterns

### File Upload Pattern
```javascript
async function uploadDocument(file, onProgress) {
    const formData = new FormData();
    formData.append('file', file);
    
    return new Promise((resolve, reject) => {
        const xhr = new XMLHttpRequest();
        
        xhr.upload.addEventListener('progress', (e) => {
            if (e.lengthComputable && onProgress) {
                const percentComplete = (e.loaded / e.total) * 100;
                onProgress(percentComplete);
            }
        });
        
        xhr.onload = () => {
            if (xhr.status === 200) {
                resolve(JSON.parse(xhr.responseText));
            } else {
                reject(new Error(`Upload failed: ${xhr.statusText}`));
            }
        };
        
        xhr.onerror = () => reject(new Error('Upload failed'));
        
        xhr.open('POST', '/documents/');
        const token = AuthManager.getToken();
        if (token) {
            xhr.setRequestHeader('Authorization', `Bearer ${token}`);
        }
        xhr.send(formData);
    });
}
```

### Document List Pattern
```javascript
async function fetchDocuments() {
    try {
        const documents = await api.request('/documents/');
        return documents;
    } catch (error) {
        showError('Failed to load documents: ' + error.message);
        return [];
    }
}
```

## Analysis Patterns

### Analysis Execution Pattern
```javascript
async function createAnalysis(documentId, prompt, modelProvider = 'openai') {
    try {
        const response = await api.request('/analyses/', {
            method: 'POST',
            body: JSON.stringify({
                document_id: documentId,
                prompt: prompt,
                llm_provider: modelProvider
            })
        });
        
        return response;
    } catch (error) {
        showError('Analysis failed: ' + error.message);
        throw error;
    }
}
```

### Analysis Results Pattern
```javascript
async function fetchAnalysis(analysisId) {
    try {
        const analysis = await api.request(`/analyses/${analysisId}`);
        return analysis;
    } catch (error) {
        showError('Failed to load analysis: ' + error.message);
        return null;
    }
}
```

## Error Handling Patterns

### Global Error Handler
```javascript
class ErrorHandler {
    static show(message, type = 'error') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }
    
    static handle(error) {
        console.error('Application Error:', error);
        
        if (error.message.includes('401')) {
            this.show('Session expired. Please log in again.', 'warning');
            AuthManager.clearToken();
            window.location.href = '/login.html';
        } else if (error.message.includes('500')) {
            this.show('Server error. Please try again later.', 'error');
        } else {
            this.show(error.message, 'error');
        }
    }
}

// Global error handlers
window.addEventListener('unhandledrejection', (event) => {
    ErrorHandler.handle(event.reason);
});

window.addEventListener('error', (event) => {
    ErrorHandler.handle(event.error);
});
```

## Loading States Pattern

### Loading Indicator Management
```javascript
class LoadingManager {
    static show(element, message = 'Loading...') {
        element.classList.add('loading');
        element.disabled = true;
        element.originalText = element.textContent;
        element.textContent = message;
    }
    
    static hide(element) {
        element.classList.remove('loading');
        element.disabled = false;
        if (element.originalText) {
            element.textContent = element.originalText;
        }
    }
}
```

## Implementation Notes

### Security Considerations
- Store JWT in localStorage (consider httpOnly cookies for production)
- Validate all user inputs client-side and server-side
- Implement CSRF protection headers
- Use HTTPS in production

### Performance Optimization
- Implement request caching for static data
- Use debouncing for search/filter inputs
- Lazy load large datasets
- Compress API responses

### Error Recovery
- Implement exponential backoff for retries
- Provide offline capability indicators
- Cache critical data locally
- Graceful degradation for failed features