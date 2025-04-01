# Ultra - AI-Powered Content and Data Processing Platform

Ultra is a comprehensive platform that combines multiple AI language models (LLMs) with advanced data processing and visualization capabilities. It provides a unified interface for content generation, analysis, and data manipulation.

## Features

### Language Model Integration
- OpenAI's ChatGPT
- Google's Gemini
- Llama
- Configurable rate limits and API keys
- Feature-based enabling/disabling

### Data Processing
- Pandas-based data manipulation
- Advanced data scaling and transformation
- Custom filtering and aggregation
- Support for multiple data formats

### Visualization
- Matplotlib integration
- Multiple chart types (line, bar, scatter)
- Customizable plot parameters
- Automatic file saving

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ultra.git
cd ultra
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file with your API keys:
```
OPENAI_API_KEY=your_openai_key
GOOGLE_API_KEY=your_google_key
LLAMA_API_KEY=your_llama_key
```

## Usage

### Basic Usage

```python
import asyncio
from ultra_main import UltraOrchestrator

async def main():
    # Initialize orchestrator
    orchestrator = UltraOrchestrator(
        api_keys={
            'openai': 'your_openai_key',
            'google': 'your_google_key',
            'llama': 'your_llama_key'
        },
        enabled_features=["openai", "gemini", "llama", "pandas", "matplotlib"]
    )
    
    # Process with LLMs
    responses = await orchestrator.process_with_llm("Your prompt here")
    
    # Process data
    results = await orchestrator.process_with_data(
        your_data,
        processing_params={"scale": {"method": "standard"}},
        viz_params={
            "type": "line",
            "columns": ["column1", "column2"],
            "title": "Your Visualization"
        }
    )

if __name__ == "__main__":
    asyncio.run(main())
```

### Feature Configuration

You can enable or disable specific features when initializing the orchestrator:

```python
orchestrator = UltraOrchestrator(
    api_keys=api_keys,
    enabled_features=["openai", "pandas"]  # Only enable specific features
)
```

## Architecture

The platform is built with a modular architecture:

- `UltraBase`: Base class with common functionality
- `UltraLLM`: Handles language model interactions
- `UltraData`: Manages data processing and visualization
- `UltraOrchestrator`: Main class that coordinates all features

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
