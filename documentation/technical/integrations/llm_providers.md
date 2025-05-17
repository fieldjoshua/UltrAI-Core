# LLM Provider Integrations

This document explains how to integrate and use various LLM providers with Ultra, including both cloud providers and local models.

## Supported Providers

Ultra supports the following LLM providers:

1. **Cloud Providers**:

   - **OpenAI** (GPT-4, GPT-4o, GPT-3.5 Turbo)
   - **Anthropic** (Claude 3 Opus, Claude 3 Sonnet, Claude 3 Haiku)
   - **Google** (Gemini 1.5 Pro, Gemini 1.5 Flash)
   - **Mistral AI** (Mistral Large, Mistral Medium, Mistral Small)
   - **Cohere** (Command, Command R+)

2. **Local Models**:
   - **Docker Model Runner**: Run various open-source models locally using Docker Desktop's Model Runner feature
   - Support for models like Phi-3, Llama 3, Mistral, etc.

## Configuration

### API Keys for Cloud Providers

To use cloud providers, you need to set API keys in your environment (or `.env` file):

```env
# OpenAI API keys
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxx
OPENAI_ORG_ID=org-xxxxxxxxxxxxxxxxxxxx  # Optional

# Anthropic API key
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Google API key
GOOGLE_API_KEY=AIza-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Mistral API key
MISTRAL_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxx

# Cohere API key
COHERE_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxx
```

### Alternative API Endpoints

You can configure alternative API endpoints for proxies or special deployments:

```env
# Custom API endpoints
OPENAI_API_ENDPOINT=https://custom-openai-proxy.com/v1
ANTHROPIC_API_ENDPOINT=https://custom-claude-proxy.com
GEMINI_API_ENDPOINT=https://custom-gemini-proxy.com
MISTRAL_API_ENDPOINT=https://custom-mistral-proxy.com
```

### Docker Model Runner Configuration

To use Docker Model Runner for local models:

```env
# Enable Docker Model Runner
USE_MODEL_RUNNER=true

# Use CLI-based adapter (recommended)
MODEL_RUNNER_TYPE=cli

# Default model to use
DEFAULT_MODEL=ai/smollm2

# Enable GPU acceleration if available
GPU_ENABLED=true
```

## Usage

### Basic Usage

Configure environment variables, then Ultra will automatically register available models based on your API keys and configuration.

### Testing Provider Connectivity

Use the included test script to verify your provider setup:

```bash
# Test all providers
python3 scripts/test_cloud_llms.py

# Test a specific provider
python3 scripts/test_cloud_llms.py --provider openai

# Test a specific model
python3 scripts/test_cloud_llms.py --provider anthropic --model claude-3-opus-20240229
```

### Testing Docker Model Runner

```bash
# Test Docker Model Runner connectivity
python3 scripts/test_modelrunner_cli.py

# Pull models for use with Docker Model Runner
python3 scripts/pull_modelrunner_models.py --models ai/smollm2,ai/mistral
```

## Provider-Specific Information

### OpenAI / GPT Models

- **Key Features**: Strong general reasoning, code generation, instruction following
- **Recommended Models**: GPT-4o for best performance, GPT-3.5 Turbo for cost-effectiveness
- **Context Window**: 8K-128K tokens depending on model
- **Strengths**: General reasoning, code generation, creativity
- **Limitations**: Cost for high usage, potential rate limits

### Anthropic / Claude Models

- **Key Features**: Long context window, factual accuracy, safety features
- **Recommended Models**: Claude 3 Opus for highest quality, Claude 3 Haiku for speed
- **Context Window**: 50K-200K tokens depending on model
- **Strengths**: Document analysis, nuanced explanations, safety
- **Limitations**: Higher cost for premium models

### Google / Gemini Models

- **Key Features**: Multimodal capabilities, factual knowledge
- **Recommended Models**: Gemini 1.5 Pro for quality, Gemini 1.5 Flash for speed
- **Context Window**: 8K-1M tokens depending on model
- **Strengths**: Multimodal processing, factual information
- **Limitations**: Streaming not fully supported

### Docker Model Runner / Local Models

- **Key Features**: Local execution, no API keys needed, offline support
- **Recommended Models**: ai/smollm2 for quick testing, ai/mistral for quality
- **Context Window**: Varies by model (typically 2K-8K tokens)
- **Strengths**: Privacy, no API costs, offline operation
- **Limitations**: Performance depends on hardware, larger models require more resources

## Performance Considerations

### Hardware Requirements for Local Models

| Model      | Size   | RAM   | Disk   | GPU                           |
| ---------- | ------ | ----- | ------ | ----------------------------- |
| ai/smollm2 | ~250MB | 1-2GB | ~500MB | Optional                      |
| ai/mistral | ~4GB   | 8GB+  | ~10GB  | Recommended                   |
| ai/llama3  | ~8GB   | 16GB+ | ~20GB  | Required for good performance |

### Concurrent Request Limits

Configure concurrent request limits to prevent overloading providers:

```env
MAX_CONCURRENT_OPENAI=10
MAX_CONCURRENT_ANTHROPIC=5
MAX_CONCURRENT_GOOGLE=8
```

## Fallback and Model Selection

Ultra can dynamically select appropriate models based on availability:

- Set `USE_LOCAL_MODELS_WHEN_OFFLINE=true` to fall back to local models when internet is unavailable
- Configure model preferences in orchestrator configuration
- Use tags to select models with specific capabilities

## Streaming Support

Provider streaming support:

| Provider  | Streaming |
| --------- | --------- |
| OpenAI    | Yes       |
| Anthropic | Yes       |
| Gemini    | Limited   |
| Mistral   | Yes       |
| Local     | Yes       |

## Troubleshooting

### Common Issues

1. **API Key Problems**:

   - Verify keys are correctly set in environment/`.env`
   - Check for whitespace or formatting issues

2. **Rate Limits**:

   - Implement backoff strategies
   - Distribute load across providers
   - Consider upgrading API tier

3. **Local Model Issues**:
   - Ensure Docker Desktop is running
   - Check Docker Model Runner extension is installed
   - Verify models are pulled correctly
   - Monitor system resources (RAM, disk space)

### Logs and Debugging

Enable verbose logging:

```env
LOG_LEVEL=debug
```

View Docker Model Runner logs:

```bash
docker model logs
```
