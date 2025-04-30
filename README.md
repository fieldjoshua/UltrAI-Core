# Ultra MVP

Multi-LLM analysis platform that allows you to compare responses from different AI models. Gain insight by seeing how multiple models respond to the same prompt.

## Features

- Connect to multiple LLM providers (OpenAI, Anthropic, Google, Mistral, Llama)
- Compare responses side-by-side with intuitive UI
- Generate synthesized analysis from multiple models
- Support for local models via Ollama
- Multiple analysis patterns for specialized comparisons
- Robust error handling and fallbacks for reliability
- Full API for programmatic access

## Quick Start

1. Clone the repository

   ```bash
   git clone https://github.com/yourusername/ultra.git
   cd ultra
   ```

2. Set up Python environment and install dependencies

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Configure your environment

   ```bash
   cp env.example .env
   # Edit .env with your API keys and configuration
   ```

4. Install frontend dependencies

   ```bash
   cd frontend
   npm install
   cd ..
   ```

5. Start the backend server

   ```bash
   python backend/run.py
   ```

6. In a separate terminal, start the frontend

   ```bash
   cd frontend
   npm run dev
   ```

7. Open the application in your browser: <http://localhost:3000>

## Configuration

Ultra requires API keys for the LLM providers you want to use. At minimum, configure:

- `OPENAI_API_KEY` for GPT models (from [OpenAI](https://platform.openai.com/api-keys))
- `ANTHROPIC_API_KEY` for Claude models (from [Anthropic](https://console.anthropic.com/))
- `GOOGLE_API_KEY` for Gemini models (from [Google AI Studio](https://ai.google.dev/))

For local models, install [Ollama](https://ollama.ai/) and pull your preferred models.

See `env.example` for all available configuration options.

## LLM Integration Testing

Test your API keys and LLM connections:

```bash
cd .aicheck/actions/MVPCompletion/supporting_docs
python llm_integration_test.py
```

This will test connections to all configured LLM providers and show which ones are working correctly.

## Usage

1. Enter your prompt in the main text area
2. Select the LLM models you want to compare from the dropdown
3. (Optional) Choose an analysis pattern for structured comparison
4. Click "Analyze" to submit your prompt
5. View the side-by-side responses from each model
6. (Optional) Use tools to copy, export, or share the results

## Core Functionality

### Analysis Patterns

Ultra supports several analysis patterns:

- **Confidence Analysis**: Evaluate how confident each model is in its response
- **Critique**: Models critique each other's responses
- **Scenario Analysis**: Explore different possible outcomes
- **Fact Check**: Compare factual accuracy across models

### API Access

Ultra provides a comprehensive API for integrating with your applications. Example:

```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Explain quantum computing in simple terms",
    "selected_models": ["gpt4o", "claude37", "gemini15"],
    "pattern": "confidence"
  }'
```

See the [API Quick Start Guide](documentation/public/api_quickstart.md) for more examples.

## Project Structure

```
/
├── frontend/            # React frontend application
├── backend/             # Python backend code
│   ├── app.py           # Main FastAPI application
│   ├── routes/          # API route handlers
│   ├── services/        # Business logic services
│   └── models/          # Data models and schemas
├── src/                 # Core shared code
│   ├── core/            # Core business logic
│   ├── models/          # Data models
│   ├── patterns/        # Analysis pattern implementations
│   └── utils/           # Utility functions
├── documentation/       # Project documentation
│   ├── public/          # User-facing documentation
│   └── technical/       # Developer documentation
├── scripts/             # Utility scripts
└── tests/               # Test suite
```

## Documentation

- [User Guide](documentation/public/user_guide.md) - How to use Ultra
- [API Quick Start](documentation/public/api_quickstart.md) - API examples and patterns
- [Local Development Guide](documentation/technical/setup/local_development_guide.md) - Development setup
- [Deployment Guide](documentation/technical/setup/deployment_guide.md) - Deployment instructions

## Error Handling

Ultra implements robust error handling:

- Graceful fallbacks when models are unavailable
- Clear error messages for troubleshooting
- Timeout protection for slow API responses
- Caching to reduce duplicate requests

## Development

To contribute to Ultra:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `pytest tests/`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Performance Dashboard

The Ultra Framework includes a detailed performance monitoring dashboard that provides real-time metrics and visualizations:

### Dashboard Features
- **System Overview**: CPU, memory, and disk usage metrics with trend indicators
- **Performance Metrics**: Request counts, document processing stats, and response times
- **Efficiency Analytics**: Average processing times, cache hit rates, and resource utilization
- **System Information**: Runtime environment details, uptime, and system status

### Accessing the Dashboard
- Navigate to `/dashboard` in your browser
- Click the dashboard icon in the top-right corner of the main application
- Auto-refreshes every 5 seconds to show real-time data

For detailed information about the Performance Dashboard, see [PERFORMANCE_DASHBOARD.md](PERFORMANCE_DASHBOARD.md).

## Documentation

For a comprehensive view of all project documentation, please see [DOCUMENTATION.md](./DOCUMENTATION.md) which contains a categorized index of all documentation files along with their priority levels.

The documentation index also includes the current development priorities based on our roadmap.

## Performance Optimizations

Ultra AI has been optimized for performance in several key areas:

### Code Splitting & Lazy Loading
- Components are lazy-loaded to reduce initial bundle size
- Route-based code splitting for optimal loading
- Suspense boundaries with loading indicators

### Mobile Optimization
- Responsive design for all device sizes
- Optimized touch targets for mobile devices
- Reduced motion options for accessibility

### Asset Optimization
- Preloading of critical resources
- Optimized font loading strategies
- Inline critical CSS for faster initial render

### Build Optimization
- Vendor chunk separation for better caching
- Brotli and Gzip compression
- Bundle analysis tools for monitoring

For more details, see [PERFORMANCE_IMPROVEMENTS.md](./PERFORMANCE_IMPROVEMENTS.md)
