# Ultra MVP User Guide

Welcome to Ultra, a tool for comparing responses from multiple large language models (LLMs). This guide will help you understand how to use the core features of Ultra MVP.

## Getting Started

### Accessing Ultra

You can access Ultra in one of two ways:

1. **Hosted Version**: Visit [ultra-app.vercel.app](https://ultra-app.vercel.app) (if available)
2. **Local Installation**: Follow the [setup guide](../technical/setup/local_development_guide.md) to run Ultra on your own machine

### First-time Setup

When you first use Ultra, you'll need to:

1. Configure your API keys in the settings
2. Choose your default models
3. Optionally select analysis patterns

## Core Features

### 1. Comparing Model Responses

The primary function of Ultra is to compare how different LLMs respond to the same prompt.

#### To compare model responses

1. Enter your prompt in the main text area
2. Select which models to compare from the dropdown menu
3. Click "Analyze" to submit your prompt
4. View the side-by-side responses from each model

![Compare Models Screenshot](../images/compare_models.png)

#### Supported Models

Ultra currently supports these LLM providers:

- **OpenAI**: GPT-3.5-Turbo, GPT-4, GPT-4o
- **Anthropic**: Claude 3 (Opus, Sonnet, Haiku)
- **Google**: Gemini Pro, Gemini 1.5
- **Local Models**: Via Ollama integration (e.g., Llama 3)

### 2. Analysis Patterns

Ultra offers several analysis patterns to structure the comparison:

| Pattern | Description | Best For |
|---------|-------------|----------|
| **Confidence Analysis** | Evaluates each model's confidence level | Factual questions, decisions |
| **Critique** | Models critique each other's responses | Getting balanced viewpoints |
| **Scenario Analysis** | Explores different outcomes or possibilities | Planning, risk assessment |
| **Fact Check** | Compares factual accuracy across models | Research, verification |

To use a pattern:

1. Select your desired pattern from the dropdown
2. Enter a prompt relevant to that pattern
3. Click "Analyze"

### 3. Working with Results

After receiving responses, you can:

- **Copy Individual Responses**: Click the copy icon next to any response
- **Export All Results**: Use the export button to save as JSON or markdown
- **Share Results**: Generate a shareable link (if enabled)
- **Add Notes**: Annotate responses for future reference

## Advanced Features

### Custom Prompting

For more sophisticated comparisons:

1. Click "Advanced Mode"
2. Customize system prompts for each model
3. Set response parameters (temperature, max tokens)
4. Use the prompt template library for specialized tasks

### Batch Analysis

To analyze multiple prompts at once:

1. Go to the "Batch" tab
2. Upload a CSV file with prompts (one per line)
3. Select models and other settings
4. Start batch processing

### Using Local Models

If you have Ollama installed:

1. Go to "Settings" > "Local Models"
2. Ensure Ollama is running on your machine
3. Click "Refresh Models" to see available models
4. Select local models alongside cloud models in your comparisons

## Tips and Best Practices

### Effective Prompting

- Be specific in your prompts
- Use clear instructions
- Try different phrasings if results are unclear

### Model Selection

- Use diverse models for broader perspectives
- Include at least one high-capability model (GPT-4, Claude 3 Opus) for complex tasks
- Consider specialized models for specific domains

### Performance Considerations

- Complex prompts with multiple models may take longer to process
- Local models are faster but may have lower capabilities
- Use caching for repeated queries to save time and API costs

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| **Model unavailable** | Check API key in settings, try a different model |
| **Slow responses** | Reduce number of models, simplify prompt |
| **Incomplete responses** | Increase max tokens setting, rephrase prompt |
| **Error messages** | Check API quotas, verify internet connection |

### Getting Support

If you encounter issues:

1. Check the [FAQ](./faq.md)
2. Visit the GitHub repository for known issues
3. Contact support at <support@ultra-app.com>

## Use Cases

Ultra is ideal for:

- **Research**: Compare how different models interpret the same information
- **Content Creation**: Get multiple perspectives on writing or creative tasks
- **Learning**: Understand the strengths and limitations of different LLMs
- **Decision Making**: Get diverse viewpoints before making decisions

## Privacy and Data Usage

- Prompts and responses may be sent to third-party LLM providers
- API keys are stored locally in your browser or environment
- Export or delete your data at any time from Settings

## Next Steps

As you become familiar with Ultra, explore:

- [API Documentation](../api/api_documentation.md) for programmatic access
- [Analysis Patterns Guide](./analysis_patterns.md) for deeper understanding of patterns
- [Contributing Guide](../technical/contributing.md) if you want to help improve Ultra
