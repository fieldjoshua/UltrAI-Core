# Ultra API Reference

This document provides a comprehensive reference for all API endpoints available in the Ultra MVP.

## Base URL

All API requests should be sent to the base API URL:

```
http://localhost:8000/api
```

For production environments, this will be the deployed API URL.

## Authentication

Currently, the Ultra MVP does not require authentication for API requests. Future versions will implement authentication using bearer tokens.

## Response Format

All API responses follow a consistent format:

```json
{
  "status": "success|error|partial_success",
  "data": { /* response data specific to the endpoint */ },
  "error": "Error message (when status is error)",
  "message": "Additional information (optional)"
}
```

## Endpoints

### Model Management

#### GET /available-models

Returns a list of all available LLM models.

**Request**

```
GET /api/available-models
```

**Response**

```json
{
  "status": "success",
  "available_models": [
    "gpt4o",
    "gpt4turbo",
    "claude37",
    "claude3opus",
    "gemini15",
    "llama3"
  ],
  "errors": {}
}
```

### Analysis

#### POST /analyze

Analyzes a text prompt using multiple LLMs.

**Request**

```
POST /api/analyze
Content-Type: application/json

{
  "prompt": "What are the major challenges in quantum computing?",
  "models": ["gpt4o", "claude37", "gemini15"],
  "ultraModel": "gpt4o",
  "pattern": "confidence",
  "options": {}
}
```

**Parameters**

| Parameter | Type | Description |
|-----------|------|-------------|
| prompt | string | The text prompt to analyze |
| models | array | Array of model IDs to use for analysis |
| ultraModel | string | Primary model used for generating the combined response |
| pattern | string | Analysis pattern to use (see Pattern Reference) |
| options | object | Additional options (optional) |

**Response**

```json
{
  "status": "success",
  "model_responses": {
    "gpt4o": "GPT-4o's analysis...",
    "claude37": "Claude's analysis...",
    "gemini15": "Gemini's analysis..."
  },
  "ultra_response": "Combined analysis based on all models...",
  "pattern": "confidence",
  "performance": {
    "total_time_seconds": 4.25,
    "model_times": {
      "gpt4o": 2.1,
      "claude37": 3.4,
      "gemini15": 2.8
    },
    "token_counts": {
      "gpt4o": {
        "prompt_tokens": 15,
        "completion_tokens": 245,
        "total_tokens": 260
      },
      "claude37": {
        "prompt_tokens": 15,
        "completion_tokens": 320,
        "total_tokens": 335
      },
      "gemini15": {
        "prompt_tokens": 15,
        "completion_tokens": 210,
        "total_tokens": 225
      }
    }
  }
}
```

#### POST /analyze-with-docs

Analyzes a prompt along with uploaded documents.

**Request**

```
POST /api/analyze-with-docs
Content-Type: multipart/form-data

prompt: "Summarize the key points in these documents"
selectedModels: ["gpt4o", "claude37"]
ultraModel: "gpt4o"
pattern: "confidence"
options: {}
files: [file1, file2, ...]
```

**Response**
Similar to `/analyze` but with additional document context.

### System Status

#### GET /status

Returns the current system status.

**Request**

```
GET /api/status
```

**Response**

```json
{
  "status": "success",
  "version": "1.0.0",
  "uptime": "2 days, 4 hours",
  "services": {
    "database": "up",
    "cache": "up"
  }
}
```

#### GET /metrics

Returns system performance metrics.

**Request**

```
GET /api/metrics
```

**Response**

```json
{
  "status": "success",
  "metrics": {
    "requests_processed": 156,
    "cache_hits": 48,
    "cache_hit_ratio": 0.31,
    "avg_response_time": 2.4
  }
}
```

## Analysis Pattern Reference

Ultra supports several analysis patterns that determine how models collaborate:

| Pattern ID | Name | Description |
|------------|------|-------------|
| gut | Gut Check Analysis | Rapid evaluation of different perspectives to identify the most likely correct answer |
| confidence | Confidence Analysis | Evaluates the strength of each model response with confidence scoring |
| critique | Critique Analysis | Models critically evaluate each other's reasoning and answers |
| fact_check | Fact Check Analysis | Verifies factual accuracy and cites sources for claims |
| perspective | Perspective Analysis | Examines a question from multiple analytical perspectives |
| scenario | Scenario Analysis | Explores potential future outcomes and alternative possibilities |
| stakeholder | Stakeholder Vision | Analyzes from multiple stakeholder perspectives to reveal diverse interests |
| systems | Systems Mapper | Maps complex system dynamics with feedback loops and leverage points |
| time | Time Horizon | Analyzes across multiple time frames to balance short and long-term considerations |
| innovation | Innovation Bridge | Uses cross-domain analogies to discover non-obvious patterns and solutions |

## Error Handling

The API may return various error responses:

### 400 Bad Request

```json
{
  "status": "error",
  "error": "bad_request",
  "message": "Prompt cannot be empty"
}
```

### 404 Not Found

```json
{
  "status": "error",
  "error": "not_found",
  "message": "Requested resource not found"
}
```

### 500 Internal Server Error

```json
{
  "status": "error",
  "error": "server_error",
  "message": "An unexpected error occurred"
}
```

## Rate Limiting

The API implements rate limiting to prevent abuse. When rate limits are exceeded, you'll receive:

```json
{
  "status": "error",
  "error": "rate_limit_exceeded",
  "message": "Rate limit exceeded. Try again in 60 seconds",
  "retry_after": 60
}
```

## API Client Example

### JavaScript/TypeScript

```typescript
// Example using fetch API
async function analyzePrompt(prompt, models, ultraModel, pattern) {
  const response = await fetch('http://localhost:8000/api/analyze', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      prompt,
      models,
      ultraModel,
      pattern,
      options: {}
    }),
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.message || 'Analysis failed');
  }

  return await response.json();
}
```

### Python

```python
import requests

def analyze_prompt(prompt, models, ultra_model, pattern):
    url = "http://localhost:8000/api/analyze"

    payload = {
        "prompt": prompt,
        "models": models,
        "ultraModel": ultra_model,
        "pattern": pattern,
        "options": {}
    }

    response = requests.post(url, json=payload)

    if response.status_code != 200:
        error_data = response.json()
        raise Exception(error_data.get("message", "Analysis failed"))

    return response.json()
```

## Example Uses

### Simple Analysis

```javascript
const result = await analyzePrompt(
  "What are the ethical implications of autonomous vehicles?",
  ["gpt4o", "claude37"],
  "gpt4o",
  "perspective"
);
```

### Document Analysis

```python
import requests

url = "http://localhost:8000/api/analyze-with-docs"
files = [
    ('files', ('document1.pdf', open('document1.pdf', 'rb'), 'application/pdf')),
    ('files', ('document2.pdf', open('document2.pdf', 'rb'), 'application/pdf'))
]

data = {
    'prompt': 'Summarize the key points in these documents',
    'selectedModels': '["gpt4o", "claude37"]',
    'ultraModel': 'gpt4o',
    'pattern': 'confidence'
}

response = requests.post(url, data=data, files=files)
result = response.json()
```
