# Docker Model Runner Usage Examples

This document provides practical examples of how to use Docker Model Runner with Ultra for various use cases. These examples will be useful for both development and documentation purposes.

## Basic Setup and Configuration

### Installing Docker Model Runner

```bash
# Make sure you have Docker Desktop 4.40+ installed
docker --version

# Install the Docker Model Runner plugin
docker extension install docker/modelrunner-cuda:latest  # For NVIDIA GPUs
# OR
docker extension install docker/modelrunner-metal:latest  # For Apple Silicon
```

### Setting Up Environment Variables

Add these variables to your `.env` file:

```
# Docker Model Runner Configuration
ENABLE_MODEL_RUNNER=true
MODEL_RUNNER_URL=http://model-runner:8080
DEFAULT_LOCAL_MODEL=llama3:8b
AVAILABLE_LOCAL_MODELS=llama3:8b,phi3:mini,mistral:7b
USE_LOCAL_MODELS_WHEN_OFFLINE=true
LOCAL_MODEL_TIMEOUT=60000
```

### Starting Docker Compose with Model Runner

```bash
# Start Docker Compose with Model Runner
./scripts/start-docker.sh

# Check that Model Runner is working
curl http://localhost:8080/v1/models
```

## Example 1: Basic Model Comparison

This example demonstrates comparing a local model with cloud providers for a simple question.

### API Request

```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Explain quantum computing in simple terms",
    "selected_models": ["llama3:8b", "gpt4o", "claude37"],
    "pattern": "confidence"
  }'
```

### Python Code

```python
import requests

response = requests.post(
    "http://localhost:8000/api/analyze",
    json={
        "prompt": "Explain quantum computing in simple terms",
        "selected_models": ["llama3:8b", "gpt4o", "claude37"],
        "pattern": "confidence"
    }
)

print(response.json())
```

### Frontend Component

```jsx
import React, { useState } from 'react';
import { analyzePrompt } from '../services/api';

function ModelComparisonComponent() {
  const [prompt, setPrompt] = useState('');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      const response = await analyzePrompt({
        prompt,
        selected_models: ['llama3:8b', 'gpt4o', 'claude37'],
        pattern: 'confidence'
      });
      
      setResults(response.data);
    } catch (error) {
      console.error('Error analyzing prompt:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="model-comparison">
      <form onSubmit={handleSubmit}>
        <textarea
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Enter your prompt here..."
        />
        <button type="submit" disabled={loading}>
          {loading ? 'Analyzing...' : 'Compare Models'}
        </button>
      </form>
      
      {results && (
        <div className="results">
          {Object.entries(results.responses).map(([model, response]) => (
            <div key={model} className="model-response">
              <h3>{model}</h3>
              <p>{response.content}</p>
              <div className="confidence">
                Confidence: {response.metrics.confidence}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default ModelComparisonComponent;
```

## Example 2: Offline Development

This example shows how to use Ultra completely offline with Docker Model Runner.

### Environment Setup

```bash
# Modify .env file
ENABLE_MOCK_LLM=false
USE_LOCAL_MODELS_WHEN_OFFLINE=true
DEFAULT_LOCAL_MODEL=phi3:mini
```

### Test Offline Mode

```bash
# Disconnect from the internet (or simulate with network blocking)
# Then run Ultra as normal
./scripts/start-docker.sh

# Test with a simple API call
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "What is the capital of France?",
    "selected_models": ["default"],
    "pattern": "simple"
  }'
```

## Example 3: Custom Model Selection

This example demonstrates how to configure and use specific models with Docker Model Runner.

### Available Models Command

```bash
# List available models
curl http://localhost:8080/v1/models | jq
```

### Model Configuration

```yaml
# In docker-compose.yml
model-runner:
  environment:
    - MODELS=llama3:8b,phi3:mini,mistral:7b,llama3:70b-q4_K_M
```

### Python Code for Model Selection

```python
import requests

def get_available_models():
    """Get all available models from Docker Model Runner."""
    response = requests.get("http://localhost:8080/v1/models")
    return response.json().get("data", [])

def analyze_with_specific_model(prompt, model_id):
    """Analyze a prompt with a specific model."""
    response = requests.post(
        "http://localhost:8000/api/analyze",
        json={
            "prompt": prompt,
            "selected_models": [model_id],
            "pattern": "simple"
        }
    )
    return response.json()

# Example usage
available_models = get_available_models()
print("Available models:", [model["id"] for model in available_models])

result = analyze_with_specific_model(
    "Explain the theory of relativity",
    "llama3:8b"
)
print(result)
```

## Example 4: Complex Analysis Pattern

This example shows how to use Docker Model Runner with a more complex analysis pattern.

### Critique Analysis Pattern

```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Is artificial general intelligence possible within the next decade?",
    "selected_models": ["llama3:8b", "phi3:mini", "gpt4o"],
    "pattern": "critique",
    "options": {
      "criteria": ["accuracy", "reasoning", "bias", "creativity"],
      "format": "detailed"
    }
  }'
```

### Expected Response Structure

```json
{
  "responses": {
    "llama3:8b": {
      "content": "...",
      "metrics": { "response_time": 2.45 }
    },
    "phi3:mini": {
      "content": "...",
      "metrics": { "response_time": 1.21 }
    },
    "gpt4o": {
      "content": "...",
      "metrics": { "response_time": 3.12 }
    }
  },
  "analysis": {
    "critiques": [
      {
        "model": "llama3:8b",
        "critiqued_by": "phi3:mini",
        "criteria": {
          "accuracy": 7,
          "reasoning": 8,
          "bias": 6,
          "creativity": 9
        },
        "comments": "..."
      },
      // ... other critiques
    ],
    "summary": "..."
  }
}
```

## Example 5: Streaming Responses

This example demonstrates how to use streaming with Docker Model Runner models.

### API Streaming Request

```bash
curl -X POST http://localhost:8000/api/analyze/stream \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Write a story about a robot learning to paint",
    "selected_models": ["llama3:8b"],
    "pattern": "simple",
    "stream": true
  }'
```

### JavaScript Streaming Example

```javascript
async function streamResponse() {
  const response = await fetch('http://localhost:8000/api/analyze/stream', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      prompt: 'Write a story about a robot learning to paint',
      selected_models: ['llama3:8b'],
      pattern: 'simple',
      stream: true
    })
  });

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  
  const responseContainer = document.getElementById('response');
  responseContainer.textContent = '';
  
  while (true) {
    const { done, value } = await reader.read();
    
    if (done) {
      break;
    }
    
    const chunk = decoder.decode(value);
    const lines = chunk.split('\n').filter(line => line.trim() !== '');
    
    for (const line of lines) {
      if (line.startsWith('data: ')) {
        const data = JSON.parse(line.slice(6));
        
        if (data.type === 'content') {
          responseContainer.textContent += data.content;
        }
      }
    }
  }
}
```

## Example 6: Hybrid Mode with Fallbacks

This example shows how to set up Ultra to use local models first and fall back to cloud providers if needed.

### Configuration Setup

```bash
# In .env file
ENABLE_MODEL_RUNNER=true
ENABLE_FALLBACK=true
FALLBACK_STRATEGY=cloud
LOCAL_MODEL_TIMEOUT=10000  # 10 seconds
```

### Python Fallback Implementation

```python
import requests
import time

class ModelClient:
    def __init__(self, local_timeout=10):
        self.local_timeout = local_timeout  # seconds
        
    def query_with_fallback(self, prompt, preferred_model="llama3:8b", fallback_model="gpt3.5"):
        """Try local model first, fall back to cloud if timeout or error occurs."""
        try:
            # First attempt with local model
            local_start = time.time()
            
            response = requests.post(
                "http://localhost:8000/api/query",
                json={"prompt": prompt, "model": preferred_model},
                timeout=self.local_timeout
            )
            
            if response.status_code == 200:
                return {
                    "model_used": preferred_model,
                    "response": response.json(),
                    "source": "local",
                    "response_time": time.time() - local_start
                }
                
        except (requests.Timeout, requests.ConnectionError) as e:
            print(f"Local model timed out or failed: {e}")
            
        # Fallback to cloud model
        cloud_start = time.time()
        
        response = requests.post(
            "http://localhost:8000/api/query",
            json={"prompt": prompt, "model": fallback_model}
        )
        
        if response.status_code == 200:
            return {
                "model_used": fallback_model,
                "response": response.json(),
                "source": "cloud",
                "response_time": time.time() - cloud_start
            }
        
        # Both failed
        return {"error": "All models failed to respond"}
```

## Example 7: Model Performance Comparison

This example shows how to run performance tests with Docker Model Runner models.

### Performance Test Script

```python
import requests
import time
import statistics
import json

def benchmark_model(model_id, prompt, runs=3):
    """Benchmark a model with multiple runs."""
    response_times = []
    token_counts = []
    first_token_times = []
    
    for i in range(runs):
        print(f"Run {i+1}/{runs} for model {model_id}")
        
        start_time = time.time()
        response = requests.post(
            "http://localhost:8080/v1/chat/completions",
            json={
                "model": model_id,
                "messages": [{"role": "user", "content": prompt}],
                "stream": False
            }
        )
        end_time = time.time()
        
        if response.status_code == 200:
            data = response.json()
            total_time = end_time - start_time
            response_times.append(total_time)
            
            # Extract token count if available
            if "usage" in data:
                token_counts.append(data["usage"]["completion_tokens"])
            
            print(f"  Time: {total_time:.2f}s")
        else:
            print(f"  Error: {response.status_code}")
    
    return {
        "model": model_id,
        "avg_response_time": statistics.mean(response_times) if response_times else None,
        "min_response_time": min(response_times) if response_times else None,
        "max_response_time": max(response_times) if response_times else None,
        "avg_tokens": statistics.mean(token_counts) if token_counts else None,
        "tokens_per_second": statistics.mean([t/rt for t, rt in zip(token_counts, response_times)]) if token_counts else None
    }

# Example usage
test_prompt = "Explain the process of photosynthesis in detail."
models_to_test = ["llama3:8b", "phi3:mini", "mistral:7b"]

results = {}
for model in models_to_test:
    results[model] = benchmark_model(model, test_prompt)

print(json.dumps(results, indent=2))
```

## Example 8: Integration with Ultra's Mock Service

This example shows how to integrate Docker Model Runner with Ultra's existing mock services for testing.

### Mock Service Adapter Configuration

```python
# In backend/services/mock_llm_service.py

class MockLLMService:
    def __init__(self, config):
        self.use_model_runner = config.get("USE_MODEL_RUNNER_FOR_MOCK", False)
        self.model_runner_url = config.get("MODEL_RUNNER_URL", "http://model-runner:8080")
        self.default_mock_model = config.get("DEFAULT_LOCAL_MODEL", "phi3:mini")
        
    async def generate_response(self, prompt, model_config):
        if self.use_model_runner:
            # Use Docker Model Runner for more realistic mock responses
            try:
                response = await self._query_model_runner(prompt, model_config)
                return {
                    "content": response,
                    "model": model_config.get("model_id", "unknown"),
                    "source": "docker_model_runner"
                }
            except Exception as e:
                print(f"Error using Model Runner as mock: {e}")
                # Fall back to static mock response
        
        # Default static mock response
        return {
            "content": f"This is a mock response for model {model_config.get('model_id', 'unknown')}",
            "model": model_config.get("model_id", "unknown"),
            "source": "static_mock"
        }
        
    async def _query_model_runner(self, prompt, model_config):
        """Query Docker Model Runner for response."""
        import aiohttp
        
        model_id = self.default_mock_model
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.model_runner_url}/v1/chat/completions",
                json={
                    "model": model_id,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7,
                    "max_tokens": 500
                },
                timeout=30
            ) as resp:
                data = await resp.json()
                return data["choices"][0]["message"]["content"]
```

## Example 9: UI Integration for Model Selection

This example shows how to update the Ultra UI to include Docker Model Runner models.

### Frontend Model Selection Component

```jsx
import React, { useState, useEffect } from 'react';
import { getAvailableModels } from '../services/api';

function ModelSelection({ onModelSelect }) {
  const [availableModels, setAvailableModels] = useState({
    local: [],
    cloud: []
  });
  const [selectedModels, setSelectedModels] = useState([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    async function fetchModels() {
      try {
        const response = await getAvailableModels();
        
        // Separate models into local and cloud categories
        const local = response.models.filter(m => m.source === 'local');
        const cloud = response.models.filter(m => m.source === 'cloud');
        
        setAvailableModels({
          local,
          cloud
        });
      } catch (error) {
        console.error('Error fetching models:', error);
      } finally {
        setLoading(false);
      }
    }
    
    fetchModels();
  }, []);
  
  const handleModelToggle = (modelId) => {
    setSelectedModels(prev => {
      if (prev.includes(modelId)) {
        return prev.filter(id => id !== modelId);
      } else {
        return [...prev, modelId];
      }
    });
  };
  
  const handleSubmit = () => {
    onModelSelect(selectedModels);
  };
  
  if (loading) {
    return <div>Loading available models...</div>;
  }
  
  return (
    <div className="model-selection">
      <h3>Select Models to Compare</h3>
      
      <div className="model-categories">
        <div className="local-models">
          <h4>Local Models (Docker Model Runner)</h4>
          {availableModels.local.length === 0 ? (
            <p>No local models available</p>
          ) : (
            <ul>
              {availableModels.local.map(model => (
                <li key={model.id}>
                  <label>
                    <input
                      type="checkbox"
                      checked={selectedModels.includes(model.id)}
                      onChange={() => handleModelToggle(model.id)}
                    />
                    {model.name} ({model.id})
                  </label>
                </li>
              ))}
            </ul>
          )}
        </div>
        
        <div className="cloud-models">
          <h4>Cloud Models</h4>
          <ul>
            {availableModels.cloud.map(model => (
              <li key={model.id}>
                <label>
                  <input
                    type="checkbox"
                    checked={selectedModels.includes(model.id)}
                    onChange={() => handleModelToggle(model.id)}
                  />
                  {model.name} ({model.id})
                </label>
              </li>
            ))}
          </ul>
        </div>
      </div>
      
      <button 
        onClick={handleSubmit}
        disabled={selectedModels.length === 0}
      >
        Compare Selected Models
      </button>
    </div>
  );
}

export default ModelSelection;
```

## Example 10: Combined Mode with Both Local and Cloud Models

This example demonstrates how to run a combined analysis using both local and cloud models.

### API Request for Combined Analysis

```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "What are the ethical implications of artificial intelligence?",
    "selected_models": ["llama3:8b", "gpt4o", "mistral:7b", "claude37"],
    "pattern": "expertise",
    "options": {
      "combine_results": true,
      "analysis_prompt": "Compare and synthesize the responses from different models, highlighting areas of agreement and disagreement."
    }
  }'
```

### Expected Response Structure with Combined Analysis

```json
{
  "responses": {
    "llama3:8b": {
      "content": "...",
      "source": "local",
      "metrics": { "response_time": 3.21 }
    },
    "gpt4o": {
      "content": "...",
      "source": "cloud",
      "metrics": { "response_time": 2.45 }
    },
    "mistral:7b": {
      "content": "...",
      "source": "local",
      "metrics": { "response_time": 2.87 }
    },
    "claude37": {
      "content": "...",
      "source": "cloud",
      "metrics": { "response_time": 2.12 }
    }
  },
  "combined_analysis": {
    "content": "All models agree that AI ethics involves considerations of bias, transparency, and impact on employment. The local models (Llama 3 and Mistral) emphasized technical governance aspects, while cloud models (GPT-4o and Claude) focused more on philosophical and societal implications...",
    "model_used": "gpt4o",
    "metrics": {
      "response_time": 1.89
    }
  }
}
```