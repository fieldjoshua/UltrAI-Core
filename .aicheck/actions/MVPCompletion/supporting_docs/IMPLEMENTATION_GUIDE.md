# MVP Implementation Guide

This guide provides specific implementation tasks and code changes required to complete the MVP functionality. It focuses on ensuring that the core LLM comparison flow works end-to-end.

## 1. LLM Integration Verification

### 1.1 Test API Client Connections

Create a simple test script to verify connections to all supported LLM APIs:

```python
# scripts/test_llm_connections.py
import asyncio
import os
from dotenv import load_dotenv
from src.core.ultra_llm import UltraLLM

async def test_connections():
    """Test connections to all configured LLM APIs"""
    load_dotenv()

    # Get API keys from environment
    api_keys = {
        "openai": os.getenv("OPENAI_API_KEY"),
        "anthropic": os.getenv("ANTHROPIC_API_KEY"),
        "google": os.getenv("GOOGLE_API_KEY"),
        "mistral": os.getenv("MISTRAL_API_KEY"),
        "llama": os.getenv("LLAMA_API_KEY"),
    }

    # Create UltraLLM instance with all features enabled
    llm = UltraLLM(
        api_keys=api_keys,
        enabled_features=["openai", "anthropic", "gemini", "mistral", "ollama", "llama"]
    )

    # Initialize clients
    llm._initialize_clients()

    # Print available models
    print(f"Available models: {llm.available_models}")

    # Test a simple prompt with each available model
    test_prompt = "What is the capital of France?"
    for model in llm.available_models:
        print(f"\nTesting {model}...")
        try:
            if model == "openai":
                response = await llm.get_chatgpt_response(test_prompt)
            elif model == "anthropic":
                response = await llm.get_claude_response(test_prompt)
            elif model == "gemini":
                response = await llm.get_gemini_response(test_prompt)
            elif model == "mistral":
                response = await llm.get_mistral_response(test_prompt)
            elif model == "ollama":
                response = await llm.call_ollama(test_prompt)
            elif model == "llama":
                response = await llm.call_llama(test_prompt)
            else:
                print(f"No test method for {model}")
                continue

            print(f"Response: {response[:100]}...")
            print("Connection successful!")
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_connections())
```

### 1.2 Verify API Key Management

Ensure that API keys are properly handled in the configuration system:

1. Check `.env` handling in the main application
2. Verify that keys are securely stored and not exposed in logs
3. Test error handling for missing or invalid API keys

## 2. Core Endpoint Implementation

### 2.1 Standardize `/api/analyze` Endpoint

Ensure the analyze endpoint is consistent across all backend implementations:

```python
# backend/routes/analyze_routes.py
from fastapi import APIRouter, Depends, Request, Body
from sqlalchemy.orm import Session
from backend.models.analysis_models import AnalysisRequest, AnalysisResponse
from backend.services.prompt_service import prompt_service
from backend.dependencies import get_db
from backend.utils.errors import ERROR_MESSAGES
from backend.utils.cache import cached

analyze_router = APIRouter(tags=["Analysis"])

@analyze_router.post("/api/analyze", response_model=AnalysisResponse)
@cached(prefix="analyze", ttl=60*60*24)  # Cache for 24 hours
async def analyze_prompt(
    request: AnalysisRequest = Body(...),
    db: Session = Depends(get_db),
):
    """
    Analyze a prompt using multiple LLMs and an Ultra LLM
    """
    # Validate request
    if not request.prompt:
        return {
            "status": "error",
            "message": ERROR_MESSAGES["invalid_request"]
        }

    if not request.selected_models:
        return {
            "status": "error",
            "message": ERROR_MESSAGES["no_models"]
        }

    # Process the prompt
    try:
        result = await prompt_service.process_prompt(request)

        return {
            "status": "success",
            "analysis_id": f"analysis_{int(time.time())}",
            "results": {
                "model_responses": result.model_responses,
                "ultra_response": result.ultra_response,
                "performance": {
                    "total_time_seconds": result.processing_time,
                    "model_times": result.model_times,
                    "token_counts": result.token_counts,
                }
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error processing analysis: {str(e)}"
        }
```

### 2.2 Ensure Orchestrator Implementation

Make sure the `MultiLLMOrchestrator` class is properly implemented:

```python
# src/orchestrator.py
# Ensure this method works properly
async def process_responses(
    self,
    prompt: str,
    models: List[str],
    ultra_model: Optional[str] = None
) -> Dict[str, Any]:
    """Process prompt with multiple models"""
    try:
        self.logger.info(f"Processing prompt with models: {models}")

        # Get appropriate model clients
        model_clients = [self.models[name] for name in models if name in self.models]

        if not model_clients:
            raise ValueError("No valid models selected")

        # Get responses in parallel
        start_time = time.time()
        responses = await asyncio.gather(
            *[self.get_model_response(model, prompt, "initial")
              for model in model_clients],
            return_exceptions=True
        )

        # Process responses
        model_responses = {}
        for i, response in enumerate(responses):
            model_name = models[i] if i < len(models) else f"model_{i}"

            if isinstance(response, Exception):
                self.logger.error(f"Error from {model_name}: {str(response)}")
                model_responses[model_name] = {
                    "error": str(response),
                    "content": None
                }
            else:
                model_responses[model_name] = {
                    "content": response.content,
                    "tokens": response.tokens_used,
                    "processing_time": response.processing_time
                }

        # Generate synthesis if ultra model is specified
        ultra_response = None
        if ultra_model and ultra_model in self.models:
            synthesis_prompt = self._create_synthesis_prompt(
                model_responses, prompt
            )

            try:
                ultra_result = await self.get_model_response(
                    self.models[ultra_model], synthesis_prompt, "synthesis"
                )
                ultra_response = {
                    "content": ultra_result.content,
                    "tokens": ultra_result.tokens_used,
                    "processing_time": ultra_result.processing_time
                }
            except Exception as e:
                self.logger.error(f"Ultra synthesis error: {str(e)}")
                ultra_response = {
                    "error": str(e),
                    "content": None
                }

        total_time = time.time() - start_time

        return {
            "model_responses": model_responses,
            "ultra_response": ultra_response,
            "total_time": total_time
        }
    except Exception as e:
        self.logger.error(f"Process responses error: {str(e)}")
        raise
```

## 3. Frontend Implementation

### 3.1 Complete Analysis Page

Ensure the main analysis page is functional:

```jsx
// frontend/src/pages/AnalysisPage.jsx
import React, { useState } from 'react';
import { LLMSelector } from '../components/LLMSelector';
import { PromptInput } from '../components/PromptInput';
import { AnalysisResults } from '../components/AnalysisResults';
import { api } from '../services/api';

const availableModels = [
  { id: 'gpt4o', name: 'GPT-4 Omni', description: 'Latest OpenAI model' },
  { id: 'claude3opus', name: 'Claude 3 Opus', description: 'Anthropic\'s flagship model' },
  { id: 'gemini15', name: 'Gemini 1.5 Pro', description: 'Google\'s multimodal model' },
  { id: 'mistral', name: 'Mistral Large', description: 'Mistral AI\'s largest model' },
  { id: 'llama3', name: 'Llama 3 70B', description: 'Meta\'s open model' },
];

export const AnalysisPage = () => {
  const [selectedModels, setSelectedModels] = useState(['gpt4o']);
  const [ultraModel, setUltraModel] = useState('gpt4o');
  const [prompt, setPrompt] = useState('');
  const [results, setResults] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleModelChange = (modelId) => {
    if (selectedModels.includes(modelId)) {
      // Remove model if already selected
      setSelectedModels(selectedModels.filter(id => id !== modelId));

      // If this was the ultra model, reset ultra model
      if (ultraModel === modelId && selectedModels.length > 1) {
        setUltraModel(selectedModels.filter(id => id !== modelId)[0]);
      }
    } else {
      // Add model if not selected
      setSelectedModels([...selectedModels, modelId]);
    }
  };

  const handleUltraModelChange = (modelId) => {
    setUltraModel(modelId);
  };

  const handleAnalyze = async () => {
    if (!prompt) {
      setError('Please enter a prompt');
      return;
    }

    if (selectedModels.length === 0) {
      setError('Please select at least one model');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await api.analyzePrompt({
        prompt,
        selected_models: selectedModels,
        ultra_model: ultraModel,
      });

      setResults(response.results);
    } catch (err) {
      setError(err.message || 'An error occurred during analysis');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-6">Multi-LLM Analysis</h1>

      <div className="mb-6">
        <LLMSelector
          models={availableModels}
          selectedModels={selectedModels}
          ultraModel={ultraModel}
          onModelChange={handleModelChange}
          onUltraChange={handleUltraModelChange}
          disabled={isLoading}
        />
      </div>

      <div className="mb-6">
        <PromptInput
          value={prompt}
          onChange={setPrompt}
          onSubmit={handleAnalyze}
          disabled={isLoading}
        />
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6">
          {error}
        </div>
      )}

      {isLoading && (
        <div className="text-center p-4">
          <p>Analyzing with {selectedModels.length} models...</p>
          <div className="mt-2 animate-pulse">⏳</div>
        </div>
      )}

      {results && !isLoading && (
        <AnalysisResults results={results} />
      )}
    </div>
  );
};
```

### 3.2 Implement API Service

Complete the API service for frontend-to-backend communication:

```javascript
// frontend/src/services/api.js
const API_BASE_URL = process.env.REACT_APP_API_URL || '/api';

export const api = {
  /**
   * Get available LLM models
   */
  getAvailableModels: async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/llms`);

      if (!response.ok) {
        throw new Error(`Failed to fetch models: ${response.statusText}`);
      }

      const data = await response.json();
      return data.models;
    } catch (error) {
      console.error('Error fetching available models:', error);
      throw error;
    }
  },

  /**
   * Get available analysis patterns
   */
  getAnalysisPatterns: async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/patterns`);

      if (!response.ok) {
        throw new Error(`Failed to fetch patterns: ${response.statusText}`);
      }

      const data = await response.json();
      return data.patterns;
    } catch (error) {
      console.error('Error fetching analysis patterns:', error);
      throw error;
    }
  },

  /**
   * Analyze prompt with selected models
   */
  analyzePrompt: async ({ prompt, selected_models, ultra_model, pattern = 'comprehensive' }) => {
    try {
      const response = await fetch(`${API_BASE_URL}/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          prompt,
          selected_models,
          ultra_model,
          pattern,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || `Failed to analyze: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error analyzing prompt:', error);
      throw error;
    }
  },
};
```

## 4. Testing and Validation

### 4.1 Integration Test Script

Create an integration test script to verify the full flow:

```python
# scripts/test_full_flow.py
import asyncio
import requests
import json
import time

async def test_full_flow():
    """Test the full analysis flow"""
    # 1. Check if server is running
    try:
        server_response = requests.get("http://localhost:8000/api/health")
        print(f"Server status: {server_response.json()}")
    except Exception as e:
        print(f"Server not running: {e}")
        return

    # 2. Get available models
    try:
        models_response = requests.get("http://localhost:8000/api/llms")
        models_data = models_response.json()
        print(f"Available models: {[m['name'] for m in models_data['models']]}")
    except Exception as e:
        print(f"Failed to get models: {e}")
        return

    # 3. Run analysis
    try:
        analysis_request = {
            "prompt": "Explain the theory of relativity in simple terms",
            "selected_models": ["gpt4o", "claude3opus", "gemini15"],
            "ultra_model": "gpt4o",
            "pattern": "comprehensive"
        }

        print(f"Sending analysis request: {json.dumps(analysis_request, indent=2)}")

        analysis_response = requests.post(
            "http://localhost:8000/api/analyze",
            json=analysis_request
        )

        analysis_data = analysis_response.json()

        if analysis_data["status"] == "success":
            print("Analysis successful!")
            print(f"Models used: {list(analysis_data['results']['model_responses'].keys())}")

            # Print a sample of each response
            for model, response in analysis_data['results']['model_responses'].items():
                content = response.get('content', '')
                if content:
                    print(f"\n{model} response (first 100 chars): {content[:100]}...")
                else:
                    print(f"\n{model} error: {response.get('error', 'Unknown error')}")

            if analysis_data['results']['ultra_response']:
                ultra_content = analysis_data['results']['ultra_response'].get('content', '')
                if ultra_content:
                    print(f"\nUltra response (first 100 chars): {ultra_content[:100]}...")
                else:
                    print(f"\nUltra error: {analysis_data['results']['ultra_response'].get('error', 'Unknown error')}")
        else:
            print(f"Analysis failed: {analysis_data.get('message', 'Unknown error')}")

    except Exception as e:
        print(f"Analysis request failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_full_flow())
```

### 4.2 End-to-End Testing

Test the full application from frontend to backend:

1. Start the backend server
2. Start the frontend development server
3. Open the application in a browser
4. Run through the complete user flow:
   - Select multiple models
   - Enter a prompt
   - Submit for analysis
   - Verify results are displayed properly

## 5. Environment Setup

### 5.1 Create `.env.example` File

```
# API Keys
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key
GOOGLE_API_KEY=your-google-key
MISTRAL_API_KEY=your-mistral-key

# Local models
OLLAMA_BASE_URL=http://localhost:11434

# Server configuration
PORT=8000
HOST=0.0.0.0
DEBUG=True

# Frontend configuration
REACT_APP_API_URL=http://localhost:8000/api
```

### 5.2 Setup Scripts

Create a simple setup script:

```bash
#!/bin/bash
# scripts/setup.sh

# Check if .env file exists
if [ ! -f .env ]; then
  echo "Creating .env file from .env.example"
  cp .env.example .env
  echo "Please edit .env and fill in your API keys"
else
  echo ".env file already exists"
fi

# Install backend dependencies
echo "Installing backend dependencies..."
pip install -r requirements.txt

# Install frontend dependencies
echo "Installing frontend dependencies..."
cd frontend
npm install
cd ..

echo "Setup complete! Use ./scripts/run.sh to start the application"
```

Create a run script:

```bash
#!/bin/bash
# scripts/run.sh

# Start backend
echo "Starting backend server..."
python src/main.py &
BACKEND_PID=$!

# Start frontend
echo "Starting frontend development server..."
cd frontend
npm start &
FRONTEND_PID=$!

# Function to handle termination
function cleanup {
  echo "Shutting down servers..."
  kill -9 $BACKEND_PID
  kill -9 $FRONTEND_PID
  exit 0
}

# Register the cleanup function for the SIGINT signal (Ctrl+C)
trap cleanup SIGINT

echo "Ultra is running! Press Ctrl+C to stop."
wait
```

## 6. Documentation Updates

### 6.1 Update README.md

Create a clear README with setup and usage instructions:

```markdown
# Ultra MVP

Multi-LLM analysis platform that allows you to compare responses from different AI models.

## Features

- Connect to multiple LLM providers (OpenAI, Anthropic, Google)
- Compare responses side-by-side
- Generate synthesized analysis from multiple models
- Support for local models via Ollama

## Quick Start

1. Clone the repository
2. Run the setup script: `./scripts/setup.sh`
3. Edit the `.env` file with your API keys
4. Start the application: `./scripts/run.sh`
5. Open the application in your browser: http://localhost:3000

## Usage

1. Select the LLM models you want to compare
2. Enter your prompt in the text area
3. Click "Analyze" to send the prompt to all selected models
4. View the responses side-by-side
5. (Optional) Generate an Ultra synthesis from all responses

## Configuration

See the `.env.example` file for available configuration options.

## Development

- Backend: FastAPI-based Python application
- Frontend: React-based UI
- API: RESTful API for communication between frontend and backend

## License

MIT
```
