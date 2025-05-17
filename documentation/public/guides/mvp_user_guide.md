# Ultra MVP User Guide

This guide walks you through using Ultra's MVP functionality to compare responses from multiple large language models (LLMs).

## Getting Started

Ultra provides a simple interface to compare how different AI models respond to the same prompt.

### Accessing the Interface

1. Open your web browser and navigate to:

   - Local development: http://localhost:3009
   - Production deployment: https://your-ultra-deployment.com

2. You'll see the main Ultra interface with an analysis form.

## Step-by-Step Guide

### Step 1: Enter Your Prompt

1. Click on the "Start Analysis" button on the home page
2. In the prompt text area, enter your question or instruction
3. Be as specific as possible for best results
4. Click "Next" to proceed

Example prompts that work well:

- "Compare the environmental impact of electric vehicles vs. gasoline vehicles"
- "Explain quantum computing to a high school student"
- "What are the ethical considerations for AI in healthcare?"

### Step 2: Select AI Models

1. You'll see a list of available AI models
2. Check the boxes next to the models you want to include in your analysis
3. Select a "Primary" model (used for synthesizing the final response)
4. Click "Next" to proceed

Available models typically include:

- GPT-4o (OpenAI)
- Claude 3.7 (Anthropic)
- Gemini 1.5 Pro (Google)
- Llama 3 (Local model via Docker Model Runner)

### Step 3: Choose an Analysis Pattern

1. Select an analysis pattern that matches your needs
2. Each pattern represents a different approach to intelligence multiplication
3. Click "Run Analysis" to start the process

Available patterns:

- **Gut Check Analysis**: Rapid evaluation of different perspectives
- **Confidence Analysis**: Evaluates response strength with confidence scoring
- **Critique Analysis**: Models critically evaluate each other's reasoning
- **Fact Check Analysis**: Verifies factual accuracy and cites sources
- **Perspective Analysis**: Examines a question from multiple angles

### Step 4: View and Explore Results

Once the analysis completes, you'll see:

1. **Performance Metrics**: Time taken, models used, token counts
2. **Individual Model Responses**: Each model's response to your prompt
3. **Ultra Analysis**: A synthesized response that combines insights

Available views:

- **Side by Side**: View all model responses next to each other
- **Combined View**: Stack model responses vertically

## Features and Tips

### Response Comparison

- Use the side-by-side view to directly compare how different models approach the same prompt
- Look for areas of agreement and disagreement between models
- The Ultra analysis highlights key differences and synthesizes the most valuable insights

### Copying and Sharing

- Use the copy button next to any response to copy it to your clipboard
- You can share individual model responses or the combined analysis

### Analysis Patterns

Choose the right pattern for your needs:

- **Gut Check**: Best for quick, decisive answers
- **Confidence Analysis**: Ideal for factual questions with potential uncertainty
- **Critique Analysis**: Great for complex reasoning tasks
- **Fact Check**: Useful for verifying factual claims
- **Perspective**: Excellent for multi-faceted questions

### Performance Considerations

- Adding more models increases processing time
- Some models are significantly faster than others
- The cache system will speed up repeated identical requests

## Troubleshooting

### Common Issues

1. **No models available**:

   - Check if the backend server is running
   - Verify API keys are configured correctly

2. **Analysis timeouts**:

   - Try reducing the number of models in your analysis
   - Break complex prompts into simpler ones

3. **Inconsistent results**:

   - Different models have different training cutoff dates
   - Models may have varying levels of knowledge in specific domains

4. **Error messages**:
   - "No valid models selected" - Select at least one model
   - "Invalid request parameters" - Check your prompt format

### Getting Help

If you encounter issues:

1. Check the logs in the developer console
2. Verify your environment configuration
3. Refer to the API documentation for proper request formats

## Next Steps

After mastering the basic analysis:

1. Try different combinations of models to find your preferred set
2. Experiment with various analysis patterns for different types of queries
3. Use the insights to improve your prompting techniques

## Feedback

We welcome your feedback on the Ultra MVP! Please share your experience and suggestions via:

- GitHub Issues: [github.com/your-org/ultra/issues](https://github.com/your-org/ultra/issues)
- Email: feedback@ultraai.example.com
