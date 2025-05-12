# LLM Integration Quick Start Guide

This quick start guide will help you get up and running with all supported LLM providers in Ultra. Follow these steps to configure and test your integrations.

## 1. Environment Setup

Create a `.env` file in the project root or set environment variables with your API keys and configuration.

### Cloud Provider API Keys

```env
# OpenAI/GPT
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Anthropic/Claude
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Google/Gemini
GOOGLE_API_KEY=AIza-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Optional: Mistral and Cohere
MISTRAL_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxx
COHERE_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxx
```

> **Note:** Cloud providers (OpenAI, Anthropic, Google) are automatically registered in Ultra even without API keys. They will appear in the UI and work in mock mode when `USE_MOCK=true`. This allows you to explore the interface without any API keys. To use real API calls, provide valid API keys as shown above.

### Docker Model Runner (Local Models)

```env
# Enable Docker Model Runner
USE_MODEL_RUNNER=true

# Use CLI-based adapter (recommended)
MODEL_RUNNER_TYPE=cli

# Default model to use
DEFAULT_MODEL=ai/smollm2
```

## 2. Required Python Packages

Install the required Python packages for the LLM providers you want to use:

```bash
# Base requirements
pip install -r requirements.txt

# For OpenAI
pip install openai>=1.0.0

# For Anthropic
pip install anthropic>=0.5.0

# For Google
pip install google-generativeai>=0.3.0

# For Mistral
pip install mistralai>=0.0.7

# For Cohere
pip install cohere>=4.0.0
```

## 3. Docker Model Runner Setup

To use Docker Model Runner:

1. Install Docker Desktop
2. Enable the Model Runner extension in Docker Desktop
3. Pull required models:

```bash
docker model pull ai/smollm2
docker model pull ai/mistral
```

## 4. Testing Your Setup

Run the test scripts to verify your integration:

```bash
# Test all cloud providers
python scripts/test_cloud_llms.py

# Test a specific provider
python scripts/test_cloud_llms.py --provider openai

# Test Docker Model Runner
python scripts/test_modelrunner_cli.py

# Run comprehensive verification
python scripts/verify_cloud_llm_integration.py
```

## 5. Troubleshooting Common Issues

### API Key Problems

If you see errors like "API key not found" or "Authentication error":

- Double check your API keys for typos or extra spaces
- Ensure the keys have the correct permissions
- For OpenAI, check if you need to set an organization ID

### Docker Model Runner Issues

If Docker Model Runner is not working:

- Verify Docker Desktop is running
- Check if the Model Runner extension is installed and enabled
- Run `docker model list` to verify models are installed
- Check system resources if models are failing to load

### Rate Limits

If you encounter rate limit errors:

- Implement backoff strategies by setting `ENABLE_RATE_LIMITING=true`
- Distribute load across multiple providers
- Consider upgrading your API access tier

### Proxy or Firewall Issues

If you're behind a corporate firewall:

- Configure proxy settings in your environment:
  ```env
  HTTP_PROXY=http://proxy.company.com:8080
  HTTPS_PROXY=http://proxy.company.com:8080
  ```
- Check if your firewall allows outbound connections to API endpoints

## 6. Next Steps

Once you've verified your LLM integrations are working:

1. Explore different analysis patterns in the UI
2. Try running a comparison between cloud and local models
3. Customize model weights and tags in your configuration
4. Check out the [API documentation](../api/api_reference.md) to use the API programmatically

For complete documentation on LLM providers, see [llm_providers.md](llm_providers.md).