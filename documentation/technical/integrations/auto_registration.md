# Automatic LLM Provider Registration

Ultra now supports automatic registration of all LLM providers (OpenAI/GPT, Anthropic/Claude, Google/Gemini) regardless of whether API keys are provided. This document explains how this feature works and how to configure it.

## Overview

By default, Ultra will register all major LLM providers and make them available in the UI, even if you don't have API keys for them. This allows you to:

1. Explore the full Ultra interface without any API keys
2. Use all providers in mock mode for testing and development
3. Gradually add API keys as needed without reconfiguration

## Configuration

This feature is controlled by two environment variables:

```env
# Register all providers even without API keys
AUTO_REGISTER_PROVIDERS=true

# Use mock responses when API keys aren't available
USE_MOCK=true
```

Both of these are set to `true` by default in the `env.example` file.

## How It Works

### Provider Registration

When `AUTO_REGISTER_PROVIDERS=true`:

1. The `llm_config_service.py` registers all providers during initialization
2. For providers without API keys, it uses placeholder mock keys
3. Models appear in the UI but are marked as "needs_key" unless `USE_MOCK=true`

### Mock Mode

When `USE_MOCK=true`:

1. Providers with placeholder keys will return mock responses
2. All models show as "available" in the UI
3. When generating text, a mock response is returned with a note indicating it's a mock

### Real API Usage

When API keys are provided:

1. The service uses the real API keys instead of placeholders
2. Models make real API calls and return actual responses
3. All standard functionality (streaming, capabilities) works as expected

## Implementation Details

### Mock Keys

The system uses the following placeholder keys for mock mode:

- OpenAI: `sk-mock-key-for-openai`
- Anthropic: `sk-ant-mock-key-for-anthropic`
- Google: `AIza-mock-key-for-google`

### Adapter Detection

The LLM adapters detect mock mode by checking:

1. If the API key starts with the mock prefix
2. If the `USE_MOCK` environment variable is set

### Mock Responses

Mock responses are defined in `backend/mock_llm_service.py` and include responses for:

- GPT-4o, GPT-4 Turbo
- Claude 3 Opus, Claude 3 Sonnet
- Gemini 1.5 Pro, Gemini 1.5 Flash
- Docker Model Runner models

## Use Cases

### Development and Testing

During development, you can work with the full UI and all providers without needing real API keys:

```bash
export USE_MOCK=true
export AUTO_REGISTER_PROVIDERS=true
python backend/app.py
```

### Production with Partial API Access

In production, you might have some API keys but not others:

```bash
export USE_MOCK=false
export AUTO_REGISTER_PROVIDERS=true
export OPENAI_API_KEY=your_real_key
# No keys for Anthropic or Google
```

In this configuration:

- OpenAI models will work with real API calls
- Anthropic and Google models will show as "unavailable" but be visible in the UI

### Quick Start Setup

The new `scripts/setup-ultra.sh` script sets up Ultra with automatic registration and mock mode enabled, allowing new users to explore the full system without obtaining API keys first.

## Disabling Automatic Registration

If you prefer to only show providers with actual API keys:

```env
AUTO_REGISTER_PROVIDERS=false
```

With this setting, only providers with real API keys will be registered and visible in the UI.
