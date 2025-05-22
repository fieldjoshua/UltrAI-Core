# API Integration Guide for UI Prototype

This document outlines the integration points between the UI prototype and the backend API.

## API Endpoints

### 1. Models API

**Endpoint:** `GET /api/models`

**Purpose:** Retrieve a list of available language models for analysis.

**Response Format:**

```json
{
  "models": [
    {
      "id": "gpt-4o",
      "name": "GPT-4o",
      "provider": "OpenAI",
      "description": "Advanced multilingual model with vision capabilities",
      "capabilities": ["text", "code", "reasoning"],
      "isAvailable": true
    },
    {
      "id": "claude-3-opus",
      "name": "Claude 3 Opus",
      "provider": "Anthropic",
      "description": "Anthropic's most powerful model",
      "capabilities": ["text", "reasoning", "analysis"],
      "isAvailable": true
    }
  ]
}
```

**Integration Notes:**

- Cache this response to avoid repeated fetching
- Handle unavailable models appropriately in the UI
- Refresh data when user initiates a new session or manually refreshes

### 2. Analysis Patterns API

**Endpoint:** `GET /api/patterns`

**Purpose:** Retrieve available analysis patterns.

**Response Format:**

```json
{
  "patterns": [
    {
      "id": "fact-check",
      "name": "Fact Checking",
      "description": "Analyze content for factual accuracy",
      "useCases": [
        "News validation",
        "Research verification",
        "Source analysis"
      ],
      "configOptions": [
        {
          "id": "depth",
          "name": "Analysis Depth",
          "type": "select",
          "default": "standard",
          "options": ["basic", "standard", "deep"]
        }
      ]
    },
    {
      "id": "sentiment",
      "name": "Sentiment Analysis",
      "description": "Analyze text for emotional tone and sentiment",
      "useCases": ["Customer feedback", "Social media analysis"],
      "configOptions": []
    }
  ]
}
```

**Integration Notes:**

- Cache this response
- Support custom configuration options when present
- Display relevant usage examples for each pattern

### 3. Analysis Submission API

**Endpoint:** `POST /api/analyze`

**Request Format:**

```json
{
  "prompt": "The text to analyze",
  "modelIds": ["gpt-4o", "claude-3-opus"],
  "patternId": "fact-check",
  "config": {
    "depth": "standard"
  }
}
```

**Response Format:**

```json
{
  "analysisId": "a1b2c3d4-e5f6",
  "status": "processing",
  "estimatedCompletionTime": 15000
}
```

**Integration Notes:**

- Send proper headers (Content-Type: application/json)
- Implement request timeout handling
- Store analysisId for subsequent status checks
- Show user estimated completion time

### 4. Analysis Status API

**Endpoint:** `GET /api/status/:analysisId`

**Response Format:**

```json
{
  "analysisId": "a1b2c3d4-e5f6",
  "status": "processing",
  "progress": 65,
  "currentStep": "Analyzing with Claude 3 Opus",
  "estimatedTimeRemaining": 5000
}
```

**Possible Status Values:**

- `queued` - Analysis is in queue
- `processing` - Analysis is actively running
- `complete` - Analysis is complete
- `failed` - Analysis encountered an error

**Integration Notes:**

- Implement polling with exponential backoff
- Update progress indicators based on response
- Transition to results fetching when status is "complete"
- Show appropriate error when status is "failed"

### 5. Analysis Results API

**Endpoint:** `GET /api/results/:analysisId`

**Response Format:**

```json
{
  "analysisId": "a1b2c3d4-e5f6",
  "results": [
    {
      "modelId": "gpt-4o",
      "modelName": "GPT-4o",
      "content": "Analysis result text...",
      "timestamp": "2025-05-01T14:32:10Z",
      "processingTimeMs": 4320,
      "sections": [
        {
          "id": "summary",
          "title": "Summary",
          "content": "Summary text..."
        },
        {
          "id": "facts",
          "title": "Fact Verification",
          "content": "Fact verification results..."
        }
      ],
      "metadata": {
        "tokenCount": 1240,
        "confidenceScore": 0.87
      }
    }
  ]
}
```

**Integration Notes:**

- Handle structured and unstructured responses appropriately
- Implement proper error handling for missing results
- Support displaying different section formats (text, lists, tables)
- Enable result comparison features

## Error Handling

### Common Error Responses

```json
{
  "error": {
    "code": "invalid_request",
    "message": "Missing required field: prompt",
    "details": {
      "field": "prompt"
    }
  }
}
```

### Error Status Codes

- `400` - Bad Request (client error)
- `401` - Unauthorized (authentication required)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found (resource doesn't exist)
- `429` - Too Many Requests (rate limit exceeded)
- `500` - Internal Server Error
- `503` - Service Unavailable (temporary outage)

### Error Handling Guidelines

1. **Display user-friendly messages** - Translate technical errors into understandable messages
2. **Support retry functionality** when appropriate
3. **Log detailed errors** for debugging
4. **Handle network failures** gracefully
5. **Implement timeout handling** for long-running requests

## Authentication Integration

For this prototype, we'll use a simple API key approach:

### API Key Header

Include this header with all requests:

```
X-API-Key: your_api_key_here
```

### Error Handling for Authentication

- `401` responses should prompt for API key reauthentication
- Store API key securely (preferably in sessionStorage, not localStorage)
- Provide clear messaging when authentication fails

## Implementation Examples

### Fetching Models

```typescript
import axios from 'axios';

const API_BASE_URL = '/api';

export async function fetchAvailableModels() {
  try {
    const response = await axios.get(`${API_BASE_URL}/models`, {
      headers: {
        'X-API-Key': getApiKey(),
      },
    });
    return response.data.models;
  } catch (error) {
    console.error('Failed to fetch models:', error);
    throw new Error('Unable to load available models. Please try again later.');
  }
}
```

### Submitting Analysis

```typescript
export async function submitAnalysis(prompt, modelIds, patternId, config = {}) {
  try {
    const response = await axios.post(
      `${API_BASE_URL}/analyze`,
      {
        prompt,
        modelIds,
        patternId,
        config,
      },
      {
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': getApiKey(),
        },
      }
    );
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
}
```

### Polling for Status

```typescript
export async function pollAnalysisStatus(analysisId, onProgress) {
  let attempts = 0;
  const maxAttempts = 30;
  const initialDelay = 1000;

  const poll = async () => {
    if (attempts >= maxAttempts) {
      throw new Error('Analysis timed out');
    }

    try {
      const response = await axios.get(`${API_BASE_URL}/status/${analysisId}`, {
        headers: {
          'X-API-Key': getApiKey(),
        },
      });

      const data = response.data;
      onProgress(data);

      if (data.status === 'complete') {
        return data;
      } else if (data.status === 'failed') {
        throw new Error('Analysis failed: ' + (data.error || 'Unknown error'));
      }

      // Exponential backoff with max of 5 seconds
      const delay = Math.min(initialDelay * Math.pow(1.5, attempts), 5000);
      attempts++;

      return new Promise((resolve) => {
        setTimeout(() => resolve(poll()), delay);
      });
    } catch (error) {
      handleApiError(error);
    }
  };

  return poll();
}
```

## API Client Setup

We recommend creating a dedicated API client for consistent API interaction:

```typescript
// api/client.ts
import axios from 'axios';

const apiClient = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
apiClient.interceptors.request.use((config) => {
  const apiKey = localStorage.getItem('api_key');
  if (apiKey) {
    config.headers['X-API-Key'] = apiKey;
  }
  return config;
});

// Response interceptor
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Handle common errors
    if (error.response) {
      switch (error.response.status) {
        case 401:
          // Handle authentication error
          break;
        case 429:
          // Handle rate limiting
          break;
      }
    }
    return Promise.reject(error);
  }
);

export default apiClient;
```

## React Query Integration

For efficient data fetching and caching, we recommend using React Query:

```typescript
// hooks/useModels.ts
import { useQuery } from 'react-query';
import apiClient from '../api/client';

export function useModels() {
  return useQuery(
    'models',
    async () => {
      const { data } = await apiClient.get('/models');
      return data.models;
    },
    {
      staleTime: 5 * 60 * 1000, // Consider data fresh for 5 minutes
      retry: 3,
      refetchOnWindowFocus: false,
    }
  );
}
```

## Error Message Mapping

Map technical error codes to user-friendly messages:

```typescript
const errorMessages = {
  invalid_request:
    'There was a problem with your request. Please check and try again.',
  unauthorized: 'Your session has expired. Please log in again.',
  rate_limited: "You've reached the request limit. Please try again later.",
  service_unavailable:
    'The service is temporarily unavailable. Please try again later.',
  default: 'An unexpected error occurred. Please try again later.',
};

export function getUserFriendlyErrorMessage(errorCode) {
  return errorMessages[errorCode] || errorMessages.default;
}
```

## API Mocking for Development

When developing without a backend:

1. Use [MSW (Mock Service Worker)](https://mswjs.io/) to intercept API requests
2. Create mock responses matching the expected API formats
3. Simulate delays for realistic loading states
4. Test error scenarios by conditionally returning error responses

```javascript
// mocks/handlers.js
import { rest } from 'msw';

export const handlers = [
  rest.get('/api/models', (req, res, ctx) => {
    return res(
      ctx.delay(500),
      ctx.json({
        models: [
          {
            id: 'gpt-4o',
            name: 'GPT-4o',
            provider: 'OpenAI',
            description: 'Advanced model with vision capabilities',
            capabilities: ['text', 'code', 'reasoning'],
            isAvailable: true,
          },
          // More mock models...
        ],
      })
    );
  }),

  // More API route handlers...
];
```
