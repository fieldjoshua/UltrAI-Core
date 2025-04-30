# Ultra MVP Local Development Guide

This guide provides detailed instructions for setting up the Ultra MVP for local development. Follow these steps to get the system running on your machine.

## Prerequisites

Before starting, ensure you have the following installed:

- **Python 3.11+**: Required for the backend
- **Node.js 18+**: Required for the frontend
- **npm or yarn**: For managing frontend dependencies
- **Git**: For version control

## Environment Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/Ultra.git
cd Ultra
```

### 2. Set Up Python Environment

```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Copy the example environment file and fill in your API keys:

```bash
cp env.example .env
```

Edit the `.env` file and add your actual API keys for:

- OpenAI (GPT models)
- Anthropic (Claude models)
- Google (Gemini models)
- Optional: Mistral AI

If you want to use local models via Ollama:

1. Download and install [Ollama](https://ollama.ai/)
2. Pull a model: `ollama pull llama3`

### 4. Set Up Frontend

```bash
cd frontend
npm install
# or if using yarn
yarn install
```

## Running the Application

### Start the Backend

```bash
# From the project root
python backend/run.py
```

The API server will start at <http://localhost:8000> by default.

### Start the Frontend

```bash
cd frontend
npm run dev
# or if using yarn
yarn dev
```

The frontend development server will start at <http://localhost:3000> by default.

## Testing LLM Integrations

Before starting development, verify that the LLM integrations are working correctly:

```bash
cd .aicheck/actions/MVPCompletion/supporting_docs
python llm_integration_test.py
```

This script will test connections to all configured LLM providers and report any issues.

## Development Workflow

### API Endpoints

The main API endpoints are:

- `POST /api/analyze`: Submit a prompt for analysis by multiple LLMs
- `GET /api/available-models`: Get a list of available LLM models
- `GET /api/analyze/{analysis_id}/results`: Get results of a specific analysis

### Common Tasks

#### 1. Testing a New Model

To add and test a new LLM model:

1. Update the model configuration in `backend/config/models.py`
2. Implement the client in `src/models/llm_adapter.py`
3. Test with a simple request:

```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Test prompt", "models": ["your-new-model"]}'
```

#### 2. Adding a New Analysis Pattern

To implement a new analysis pattern:

1. Add the pattern definition in `src/patterns/analysis_patterns.py`
2. Update the pattern map in the API routes
3. Test with a request specifying the new pattern

#### 3. Debugging API Responses

Enable debug logging by setting `DEBUG=True` in your `.env` file. This will provide detailed logs in the console.

For API response debugging, use the `/api/debug` endpoint which provides additional information about request processing.

## Troubleshooting

### Common Issues

#### 1. API Key Errors

If you see authorization errors, check that:

- API keys are correctly formatted in your `.env` file
- Keys have the right permissions/scopes
- Trial accounts may have restrictions on usage

#### 2. Model Availability

Some models may not be available to all users. Check:

- Your account has access to the models you're requesting
- The model spelling matches exactly what the provider expects

#### 3. Port Conflicts

If you see "Address already in use" errors:

- Change the `PORT` value in your `.env` file
- Check for existing processes using the default ports

### Logs

Check these locations for logs:

- Backend logs: `backend/logs/`
- Application errors: Check the console output

## Deployment

For deployment instructions, see [deployment_guide.md](./deployment_guide.md).

## Additional Resources

- [API Documentation](../api/api_documentation.md)
- [Frontend Architecture](../frontend/architecture.md)
- [Model Integration Guide](../models/integration_guide.md)

## Getting Help

If you encounter issues not covered in this guide:

1. Check the project issues on GitHub
2. Look for existing discussions in the project wiki
3. Contact the development team
