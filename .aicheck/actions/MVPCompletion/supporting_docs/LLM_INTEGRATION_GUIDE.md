# LLM Integration Testing Guide

This guide explains how to test and verify LLM integrations for the Ultra MVP. Proper LLM integration is critical for the core functionality of comparing responses from different models.

## Prerequisites

1. API keys for the following services:
   - OpenAI (for GPT models)
   - Anthropic (for Claude models)
   - Google (for Gemini models)
   - (Optional) Mistral AI

2. (Optional) Local Ollama installation for testing local models
   - Download from [ollama.ai](https://ollama.ai/)
   - Pull a model like `ollama pull llama3`

## Setup

1. Copy the sample environment file to the project root:

   ```bash
   cp .aicheck/actions/MVPCompletion/supporting_docs/sample.env .env
   ```

2. Edit the `.env` file and add your actual API keys:

   ```
   OPENAI_API_KEY=sk-your-actual-key
   ANTHROPIC_API_KEY=sk-ant-api-your-actual-key
   GOOGLE_API_KEY=your-actual-key
   ```

3. Install required Python packages:

   ```bash
   pip install openai anthropic google-generativeai httpx python-dotenv
   ```

## Running the Integration Test Script

We've created a dedicated script that tests connections to all supported LLM providers:

```bash
cd .aicheck/actions/MVPCompletion/supporting_docs
python llm_integration_test.py
```

The script will:

1. Test connections to OpenAI, Anthropic, Google, and Ollama (if available)
2. Report success or failure for each provider
3. Show sample responses from each provider
4. List available models for each provider

## Manual Testing

If you need to test integrations manually, you can use these curl commands:

### OpenAI

```bash
curl https://api.openai.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -d '{"model": "gpt-3.5-turbo", "messages": [{"role": "user", "content": "Say hello"}]}'
```

### Anthropic

```bash
curl https://api.anthropic.com/v1/messages \
  -H "Content-Type: application/json" \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -d '{"model": "claude-3-haiku-20240307", "max_tokens": 20, "messages": [{"role": "user", "content": "Say hello"}]}'
```

### Google/Gemini

Google requires using their SDK rather than direct API calls.

### Ollama (Local)

```bash
curl http://localhost:11434/api/generate \
  -d '{"model": "llama3", "prompt": "Say hello", "stream": false}'
```

## API Endpoint Testing

Once you've verified the basic LLM integrations, test the `/api/analyze` endpoint which orchestrates requests to multiple LLMs:

```bash
curl http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What is the capital of France?", "selected_models": ["gpt-3.5-turbo", "claude-3-haiku-20240307", "gemini-pro"], "pattern": "Confidence Analysis"}'
```

## Connection Troubleshooting

If you encounter issues:

1. **API Key Problems**:
   - Verify keys are correctly formatted
   - Check for whitespace at the beginning or end of keys
   - Ensure keys have the correct permissions/scopes

2. **Rate Limiting**:
   - Some providers have strict rate limits for free or trial accounts
   - Check the error message for rate limit information

3. **Network Issues**:
   - Ensure you have internet connectivity
   - Check if any corporate firewalls are blocking API connections

4. **Authentication Errors**:
   - API keys may have expired
   - Account may be suspended or have billing issues

5. **Ollama Specific Issues**:
   - Ensure Ollama is running (`ps aux | grep ollama`)
   - Check if you've pulled the model you're trying to use

## Next Steps

After verifying LLM integrations:

1. Test the orchestrator that manages multiple LLM requests
2. Verify proper error handling when LLMs are unavailable
3. Check that responses are correctly formatted and compared in the UI

For any persistent issues, consult the provider's documentation and status pages:

- [OpenAI Status](https://status.openai.com/)
- [Anthropic Status](https://status.anthropic.com/)
- [Google AI Status](https://status.cloud.google.com/)
