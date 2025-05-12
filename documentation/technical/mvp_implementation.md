# Ultra MVP Implementation Guide

This document provides an overview of the Ultra MVP implementation, including architecture, configuration, and usage instructions.

## Architecture Overview

Ultra MVP is built with a modular architecture that enables comparison between multiple LLM providers:

```
┌─────────────────┐      ┌───────────────────┐      ┌─────────────────┐
│                 │      │                   │      │                 │
│  Frontend UI    │──────│  Backend API      │──────│  LLM Providers  │
│  (React)        │      │  (FastAPI)        │      │                 │
│                 │      │                   │      │                 │
└─────────────────┘      └───────────────────┘      └─────────────────┘
                                  │
                                  │
                         ┌────────┴────────┐
                         │                 │
                         │  Cache Service  │
                         │  (Redis)        │
                         │                 │
                         └─────────────────┘
```

### Core Components

1. **Frontend UI**: React-based user interface for entering prompts, selecting models, and viewing results
2. **Backend API**: FastAPI service that processes analysis requests and orchestrates LLM calls
3. **LLM Providers**: Adapters for various LLM services (OpenAI, Anthropic, Google, etc.)
4. **Cache Service**: Redis-based caching for improved performance

## Setup and Configuration

### Environment Variables

The following environment variables are required:

```
# Core Configuration
PORT=8000
NODE_ENV=development

# LLM API Keys
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
GOOGLE_API_KEY=your_google_key

# Cache Configuration
ENABLE_CACHE=true
REDIS_URL=redis://localhost:6379/0

# Feature Flags
USE_MOCK=false
```

For a complete list of environment variables, see the `env.example` file.

### Installation Steps

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-org/ultra.git
   cd ultra
   ```

2. **Backend setup**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Frontend setup**:
   ```bash
   cd frontend
   npm install
   ```

4. **Start the backend**:
   ```bash
   python -m uvicorn backend.app:app --reload
   ```

5. **Start the frontend**:
   ```bash
   cd frontend
   npm run dev
   ```

## API Documentation

### Primary Endpoints

#### `POST /api/analyze`

Analyze a prompt using multiple LLMs.

**Request Body**:
```json
{
  "prompt": "What is artificial intelligence?",
  "selected_models": ["gpt4o", "claude37", "gemini15"],
  "ultra_model": "gpt4o",
  "pattern": "comparison",
  "options": {}
}
```

**Response**:
```json
{
  "status": "success",
  "analysis_id": "analysis_12345",
  "results": {
    "model_responses": {
      "gpt4o": "GPT-4o's response...",
      "claude37": "Claude 3.7's response...",
      "gemini15": "Gemini 1.5's response..."
    },
    "ultra_response": "Combined analysis...",
    "performance": {
      "total_time_seconds": 2.5,
      "model_times": {
        "gpt4o": 1.2,
        "claude37": 1.8,
        "gemini15": 1.5
      }
    }
  }
}
```

#### `GET /api/available-models`

Get the list of available models.

**Response**:
```json
{
  "available_models": [
    "gpt4o",
    "gpt4turbo",
    "claude37",
    "claude3opus",
    "gemini15",
    "llama3"
  ]
}
```

## Analysis Patterns

Ultra supports different analysis patterns to compare model responses:

1. **Confidence Analysis**: Evaluates the strength of each model response with confidence scoring
2. **Critique Analysis**: Models critically evaluate each other's reasoning
3. **Fact Check Analysis**: Verifies factual accuracy and cites sources for claims
4. **Perspective Analysis**: Examines a question from multiple analytical perspectives
5. **Gut Check Analysis**: Rapid evaluation of different perspectives

## Usage Examples

### Basic Comparison

```javascript
// Frontend example
const response = await analyzePrompt({
  prompt: "Explain the concept of blockchain",
  selected_models: ["gpt4o", "claude37"],
  ultra_model: "gpt4o",
  pattern: "comparison"
});

// Display the results
console.log(response.results.ultra_response);
```

### Python Client Example

```python
import requests

response = requests.post(
    "http://localhost:8000/api/analyze",
    json={
        "prompt": "Explain the concept of blockchain",
        "selected_models": ["gpt4o", "claude37"],
        "ultra_model": "gpt4o",
        "pattern": "comparison"
    }
)

results = response.json()
print(results["results"]["ultra_response"])
```

## Best Practices

1. **Prompt Design**: Be clear and specific with your prompts for best results
2. **Model Selection**: Choose diverse models for more varied perspectives
3. **Analysis Patterns**: Select appropriate patterns based on your query type
4. **Performance**: Use caching for repeated queries
5. **Local Development**: Use mock mode when developing without API keys

## Troubleshooting

### Common Issues

1. **API Key Errors**: Ensure all required API keys are set in environment variables
2. **Timeout Errors**: For complex queries, increase the request timeout
3. **Cache Issues**: Verify Redis connection if caching isn't working
4. **Model Unavailability**: Check if selected models are supported and available

## Next Steps

After setting up the MVP, consider:

1. **Adding User Authentication**: For personalized history and settings
2. **Implementing Document Analysis**: For analyzing documents with LLMs
3. **Creating Custom Patterns**: For specialized analysis needs
4. **Extending Model Support**: Adding more LLM providers