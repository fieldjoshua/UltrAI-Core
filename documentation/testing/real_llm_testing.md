# Testing with Real LLM Providers

This guide explains how to test Ultra with real LLM providers (OpenAI, Anthropic, and Google) in a production environment.

## Overview

The production testing framework provides support for testing with real LLM provider APIs, allowing you to validate that the system can properly connect to and receive responses from actual LLM services. This is a critical step in validating production readiness.

## Requirements

To test with real LLM providers, you need:

1. Valid API keys for one or more of:

   - OpenAI (for GPT models)
   - Anthropic (for Claude models)
   - Google (for Gemini models)

2. The production test script (`scripts/test_production.sh`)

3. A running Ultra backend server

## Setting Up API Keys

The test script looks for API keys in a file called `.env.api_keys` in the project root directory. To set up your API keys:

1. Create or edit the `.env.api_keys` file:

   ```bash
   # Use the template created by the test script or create it manually
   nano .env.api_keys
   ```

2. Add your API keys:

   ```
   # OpenAI (GPT-4, etc.)
   OPENAI_API_KEY="sk-youropenaikey"

   # Anthropic (Claude)
   ANTHROPIC_API_KEY="sk-ant-youranthropic-key"

   # Google (Gemini)
   GOOGLE_API_KEY="your-google-api-key"
   ```

3. Set secure permissions:
   ```bash
   chmod 600 .env.api_keys
   ```

> **Important**: Never commit API keys to version control. The `.env.api_keys` file is included in `.gitignore` by default.

## Running Tests with Real LLM Providers

Once your API keys are configured, you can run the production test script:

```bash
./scripts/test_production.sh
```

The script will:

1. Detect available API keys
2. Run tests using the real LLM providers corresponding to your API keys
3. Report on the results of these tests

If you have API keys for multiple providers, the script will test them all simultaneously, allowing you to validate multi-provider functionality.

## Understanding Test Results

The test script will show detailed results for each provider:

- **Success**: If a provider responds correctly with a valid answer, that provider passes the test.
- **Failure**: If a provider fails to respond or returns an error, the test will show details about the failure.

## Cost Considerations

Testing with real LLM providers will incur costs based on your provider's pricing:

- The test sends a simple, short prompt ("What is the capital of France? Answer in one word.") to minimize costs.
- The timeout is set to 120 seconds to allow adequate time for responses.
- The script indicates which providers will be tested before making API calls.

## Troubleshooting

If tests with real providers fail:

1. **API Key Issues**:

   - Verify that your API keys are valid and active
   - Check that your account has sufficient credits/quota

2. **Network Issues**:

   - Ensure your network allows connections to the provider APIs
   - Check firewall settings

3. **Provider Status**:

   - Check the status pages for the providers you're using

4. **Environment Issues**:
   - Make sure `USE_MOCK=false` and `MOCK_MODE=false` in your environment

## Adding Support for New Providers

To add support for additional LLM providers:

1. Add the API key to `.env.api_keys`:

   ```
   NEW_PROVIDER_API_KEY="your-new-provider-key"
   ```

2. Update the test script to check for the new provider:

   ```bash
   if grep -q "NEW_PROVIDER_API_KEY=\"[^\"]*\"" "$API_KEYS_FILE" && grep -v "NEW_PROVIDER_API_KEY=\"\"" "$API_KEYS_FILE" > /dev/null; then
       AVAILABLE_PROVIDERS+=("new-provider-model")
       echo -e "${GREEN}✓ Found New Provider API key${NC}"
   fi
   ```

3. Ensure the Ultra system supports the new provider in the main application code.
