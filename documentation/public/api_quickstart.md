# Ultra API Quick Start Guide

This guide provides a quick introduction to the Ultra API with examples of common usage patterns. The Ultra API allows you to programmatically compare responses from multiple LLMs in your applications.

## Authentication

All API requests require authentication using a Bearer token:

```bash
curl -H "Authorization: Bearer YOUR_API_TOKEN" https://api.ultra-app.com/api/available-models
```

To obtain an API token, log in to the Ultra web interface and go to Settings > API.

## Core Endpoints

Ultra provides several key endpoints:

| Endpoint | Description |
|----------|-------------|
| `/api/analyze` | Compare responses from multiple LLMs |
| `/api/available-models` | List available models |
| `/api/analyze/{id}/results` | Get results of a previous analysis |

## Basic Usage Examples

### 1. Get Available Models

First, check which models are available:

```bash
curl -H "Authorization: Bearer YOUR_API_TOKEN" https://api.ultra-app.com/api/available-models
```

Response:

```json
{
  "status": "success",
  "available_models": [
    "gpt4o", "gpt4turbo", "claude37", "claude3opus", "gemini15", "llama3"
  ],
  "errors": {}
}
```

### 2. Basic Prompt Analysis

Compare responses from multiple models:

```bash
curl -X POST https://api.ultra-app.com/api/analyze \
  -H "Authorization: Bearer YOUR_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Explain quantum computing in simple terms",
    "selected_models": ["gpt4o", "claude37", "gemini15"],
    "pattern": "Confidence Analysis"
  }'
```

Response:

```json
{
  "status": "success",
  "analysis_id": "abc123xyz",
  "results": {
    "model_responses": {
      "gpt4o": "Quantum computing uses the principles of quantum mechanics...",
      "claude37": "Think of quantum computing as a new type of computing...",
      "gemini15": "Quantum computing harnesses quantum physics phenomena..."
    },
    "ultra_response": {
      "content": "All models explain that quantum computing differs from classical computing...",
      "confidence_levels": {
        "gpt4o": "high",
        "claude37": "high",
        "gemini15": "medium"
      }
    },
    "performance": {
      "total_time_seconds": 3.45,
      "model_times": {
        "gpt4o": 1.2,
        "claude37": 1.8,
        "gemini15": 1.5
      },
      "token_counts": {
        "gpt4o": 156,
        "claude37": 187,
        "gemini15": 142
      }
    }
  }
}
```

### 3. Retrieve Analysis Results Later

For long-running analyses, get the results using the analysis ID:

```bash
curl -H "Authorization: Bearer YOUR_API_TOKEN" \
  https://api.ultra-app.com/api/analyze/abc123xyz/results
```

## Common Usage Patterns

### Compare Different Approaches to a Problem

```json
{
  "prompt": "Write a function to find the longest palindromic substring in a string",
  "selected_models": ["gpt4o", "claude3opus", "gemini15"],
  "pattern": "Critique",
  "options": {
    "temperature": 0.2,
    "max_tokens": 1000
  }
}
```

### Verify Factual Information

```json
{
  "prompt": "What are the health benefits of intermittent fasting?",
  "selected_models": ["gpt4o", "claude37", "llama3"],
  "pattern": "Fact Check"
}
```

### Generate Multiple Creative Variations

```json
{
  "prompt": "Write a tagline for a new eco-friendly laundry detergent",
  "selected_models": ["gpt4o", "claude37", "gemini15"],
  "pattern": "standard",
  "options": {
    "temperature": 0.7
  }
}
```

## Using Analysis Patterns

Ultra supports different analysis patterns to structure the comparison:

| Pattern | Request Parameter | Best For |
|---------|-------------------|----------|
| Standard Comparison | `"pattern": "standard"` | Simple side-by-side comparison |
| Confidence Analysis | `"pattern": "confidence"` | Evaluating certainty across models |
| Critique | `"pattern": "critique"` | Having models evaluate each other |
| Fact Check | `"pattern": "fact_check"` | Verifying factual claims |

Example with the Critique pattern:

```bash
curl -X POST https://api.ultra-app.com/api/analyze \
  -H "Authorization: Bearer YOUR_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Describe the impact of artificial intelligence on job markets over the next decade",
    "selected_models": ["gpt4o", "claude3opus"],
    "pattern": "critique",
    "options": {
      "temperature": 0.3,
      "max_tokens": 1000
    }
  }'
```

## Batch Processing

For multiple prompts, use a batch request:

```bash
curl -X POST https://api.ultra-app.com/api/batch-analyze \
  -H "Authorization: Bearer YOUR_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "prompts": [
      "What causes climate change?",
      "How can individuals reduce their carbon footprint?",
      "What are the most effective climate policies?"
    ],
    "selected_models": ["gpt4o", "claude37"],
    "pattern": "standard"
  }'
```

## Handling Streaming Responses

For long-form content, you can stream responses:

```javascript
// JavaScript example using fetch
async function streamAnalysis() {
  const response = await fetch('https://api.ultra-app.com/api/analyze', {
    method: 'POST',
    headers: {
      'Authorization': 'Bearer YOUR_API_TOKEN',
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      prompt: 'Write a 1000-word essay about artificial intelligence',
      selected_models: ['gpt4o', 'claude37'],
      stream: true
    })
  });

  const reader = response.body.getReader();
  const decoder = new TextDecoder();

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    const chunk = decoder.decode(value);
    console.log(JSON.parse(chunk));
    // Update UI with the chunk
  }
}
```

## Error Handling

The API uses standard HTTP status codes. Common errors:

| Status Code | Meaning |
|-------------|---------|
| 400 | Bad Request - Check your request parameters |
| 401 | Unauthorized - Invalid or missing API token |
| 429 | Too Many Requests - Rate limit exceeded |
| 500 | Server Error - Something went wrong on our end |

Example error response:

```json
{
  "status": "error",
  "error": "invalid_request",
  "message": "The 'selected_models' parameter is required",
  "details": {
    "field": "selected_models",
    "required": true
  }
}
```

## Rate Limiting

The API is rate limited to prevent abuse:

- 100 requests per minute per authenticated user
- Rate limit headers included in responses:
  - `X-RateLimit-Limit`: Maximum requests allowed
  - `X-RateLimit-Remaining`: Remaining requests
  - `X-RateLimit-Reset`: Time when the limit resets

## SDK Examples

### Python

```python
import requests

API_URL = "https://api.ultra-app.com"
API_TOKEN = "YOUR_API_TOKEN"

def analyze_prompt(prompt, models, pattern="standard"):
    response = requests.post(
        f"{API_URL}/api/analyze",
        headers={"Authorization": f"Bearer {API_TOKEN}"},
        json={
            "prompt": prompt,
            "selected_models": models,
            "pattern": pattern
        }
    )
    return response.json()

# Example usage
result = analyze_prompt(
    "Explain the difference between AI and machine learning",
    ["gpt4o", "claude37"]
)
print(result)
```

### JavaScript/Node.js

```javascript
const axios = require('axios');

const API_URL = 'https://api.ultra-app.com';
const API_TOKEN = 'YOUR_API_TOKEN';

async function analyzePrompt(prompt, models, pattern = 'standard') {
  try {
    const response = await axios.post(
      `${API_URL}/api/analyze`,
      {
        prompt,
        selected_models: models,
        pattern
      },
      {
        headers: {
          'Authorization': `Bearer ${API_TOKEN}`,
          'Content-Type': 'application/json'
        }
      }
    );
    return response.data;
  } catch (error) {
    console.error('Analysis error:', error.response?.data || error.message);
    throw error;
  }
}

// Example usage
analyzePrompt(
  'What are the main differences between REST and GraphQL?',
  ['gpt4o', 'claude37']
).then(result => console.log(result))
  .catch(err => console.error('Error:', err));
```

## Next Steps

For more detailed information:

- See the [Complete API Reference](../api/api_documentation.md)
- Learn about [Advanced API Features](../api/advanced_features.md)
- Join our [Developer Community](https://github.com/ultra-org/ultra)

For API support, contact <api-support@ultra-app.com>
