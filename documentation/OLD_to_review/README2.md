# Ultra Framework

The Ultra Framework is a powerful orchestration system for LLMs that allows for complex, multi-stage reasoning patterns. It leverages multiple models to enhance analysis quality and reliability.

## Important Updates

- **Port Configuration**: Backend now runs on port 8080 (changed from 11434)
- **Docker Support**: New multi-stage Dockerfile and docker-compose.yml for optimized deployment
- **Build Optimizations**: Improved build process with code splitting and minification
- **Document Processing**: Enhanced document handling with better chunking and relevance scoring
- **Performance Dashboard**: New comprehensive dashboard for real-time system monitoring and metrics
- **Project Organization**: All documentation has been moved to the `docs/` directory and tests to the `tests/` directory
- **New Directory Structure**: Reorganized project into a more modular structure with separate directories for each concern

### Quick Start with Docker

```bash
# Build and run with Docker
docker-compose up -d

# Access the application
Frontend: http://localhost:3000
Backend API: http://localhost:8080
Performance Dashboard: http://localhost:3000/dashboard
```

## Project Structure

The project is organized into the following directories:

- **src/**: Core source code
  - `models/`: LLM client integrations and model definitions
  - `patterns/`: Analysis pattern implementations
  - `document_processing/`: Document handling functionality
  - `utils/`: Shared utilities and helpers
  - `config/`: Configuration files and data

- **frontend/**: UI components and frontend code
  - `components/`: React components
  - `pages/`: Page definitions
  - `styles/`: CSS/SCSS files
  - `api/`: Frontend API clients

- **backend/**: Server-side implementation
  - `api/`: API endpoints
  - `services/`: Business logic
  - `middleware/`: Request processing middleware
  - `db/`: Database models and connections

- **data/**: Persistent data storage
  - `embeddings/`: Vector embeddings for documents and queries
  - `cache/`: Cached responses and API results
  - `results/`: Analysis results and outputs

- **deployment/**: Deployment configurations and scripts
  - `docker/`: Docker configurations
  - `kubernetes/`: Kubernetes manifests
  - `ci_cd/`: CI/CD pipeline configurations
  - `environments/`: Environment-specific settings

- **benchmarks/**: Performance testing and benchmarking
  - `models/`: LLM model comparison benchmarks
  - `performance/`: Application performance benchmarks
  - `load_testing/`: System load testing configurations

- **public_api/**: Public API documentation and SDKs
  - `docs/`: API documentation
  - `spec/`: OpenAPI specifications
  - `sdks/`: Client SDK implementations

- **examples/**: Sample usage patterns and demonstrations

- **scripts/**: Utility scripts, deployment helpers

- **monitoring/**: Performance monitoring, dashboard components

- **docs/**: Project documentation
  - `development/`: Developer guides and setup instructions
  - See [docs/README.md](./docs/README.md) for documentation index

- **tests/**: Test files and test utilities
  - See [tests/README.md](./tests/README.md) for testing information

## Key Features

- **Multiple Analysis Patterns**: Gut Analysis, Confidence Analysis, Critique Analysis, Fact Check Analysis, Perspective Analysis, and Scenario Analysis
- **Multi-Model Orchestration**: Utilizes multiple LLMs (Claude, ChatGPT, Gemini, etc.) in parallel
- **Multi-Level Processing**: Initial, meta, hyper, and ultra level analysis for thorough reasoning
- **Local Output Storage**: All outputs are saved to disk for review and analysis
- **File Attachment Support**: Analyze documents by attaching files to provide context for LLMs
- **Advanced RAG Capabilities**: Semantic search, document chunking, and embedding-based retrieval

## Output Structure

Each Ultra analysis run creates a timestamped directory in the `outputs/` folder. The directory name includes the timestamp and a snippet of the user's prompt.

Each output directory contains:

- `prompt.txt`: The original user prompt
- `enhanced_prompt.txt`: Prompt with file content (when files are attached)
- `initial_*.txt`: Initial responses from each LLM (e.g., `initial_claude.txt`, `initial_chatgpt.txt`)
- `meta_*.txt`: Meta-level responses from each LLM
- `hyper_*.txt`: Hyper-level responses from each LLM
- `ultra.txt`: The final synthesized ultra-level response
- `metadata.json`: Information about the run, including timestamp, pattern used, models used, and system info
- `performance.txt`: Performance metrics in JSON format
- `attachments.json`: Information about attached files (when files are attached)

## Usage

Run the pattern orchestrator:

```bash
python ultra_pattern_orchestrator.py
```

Then follow the prompts to:

1. Select an analysis pattern
2. Choose an ultra synthesis model
3. Optionally attach files for analysis
4. Enter your query

### Attaching Files

The framework supports attaching files to provide context for your analysis:

- **Supported file formats**: `.pdf`, `.txt`, `.md`, `.docx`, `.doc`
- **Smart document processing**: Files are processed, chunked, and semantically indexed
- **Relevance-based retrieval**: Only the most relevant parts of documents are included in the prompt
- **Memory efficient**: Large documents are handled without exceeding LLM context limits

## Document Processing Features

The Ultra framework implements advanced document processing capabilities:

- **Smart chunking**: Documents are split into semantic chunks with proper overlap
- **Vector embeddings**: Document chunks are converted to vector embeddings for semantic search
- **Relevance scoring**: Chunks are ranked by relevance to the query
- **Context optimization**: Only the most relevant chunks are included in the prompt
- **Performance optimization**: Document processing results are cached for faster repeat analysis
- **Multiple format support**: PDF, TXT, DOCX, DOC, and Markdown files are supported

## Requirements

See `requirements.txt` for required Python packages.

For file attachment support:

- PyPDF2 and PyMuPDF (for PDF files)
- python-docx (for DOCX files)
- textract (for DOC files)
- sentence-transformers (for embedding generation)
- faiss-cpu (for similarity search)
- langchain (for text processing)

## Architecture

The Ultra framework follows a multi-stage orchestration pattern:

1. **Initial Responses**: Get responses from all available models (includes file context if attached)
2. **Meta Analysis**: Each model analyzes and reviews the collective responses
3. **Hyper Analysis**: Models analyze the meta-level reviews
4. **Ultra Synthesis**: A final comprehensive synthesis is produced

## Core Components

- `ultra_pattern_orchestrator.py`: Main orchestrator for the multi-stage pattern
- `ultra_analysis_patterns.py`: Definitions of various analysis patterns
- `ultra_llm.py`: LLM client integration
- `ultra_models.py`: Model definitions and configurations
- `ultra_documents.py`: Document processing and file handling with RAG capabilities
- `ultra_error_handling.py`: Error handling mechanisms
- `ultra_config.py`: Configuration management
- `ultra_base.py`: Base classes and utilities

## Setup and Usage

### Prerequisites

- Python 3.11+
- API keys for Claude, ChatGPT/OpenAI, Google (Gemini)
- Optional: Ollama for local Llama integration

### Environment Variables

Create a `.env` file with your API keys:

```
ANTHROPIC_API_KEY=your_anthropic_key_here
OPENAI_API_KEY=your_openai_key_here
GOOGLE_API_KEY=your_google_key_here
```

Optional API keys:

```
MISTRAL_API_KEY=your_mistral_key_here
PERPLEXITY_API_KEY=your_perplexity_key_here
COHERE_API_KEY=your_cohere_key_here
```

## Analysis Patterns

- **Gut Analysis**: Intuitive analysis without assuming factual correctness
- **Confidence Analysis**: Analysis with confidence scoring and agreement tracking
- **Critique Analysis**: Structured critique and revision process
- **Fact Check Analysis**: Focus on factual accuracy
- **Perspective Analysis**: Analysis from multiple perspectives and viewpoints
- **Scenario Analysis**: Analysis under different scenarios and conditions

## Contributing

To contribute to the Ultra framework:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -m 'Add some feature'`
4. Push to the branch: `git push origin feature-name`
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

For detailed information about the Performance Dashboard, see [PERFORMANCE_DASHBOARD.md](../documentation/performance/PERFORMANCE_DASHBOARD.md).

## Documentation

For a comprehensive view of all project documentation, please see [docs/README.md](./docs/README.md) which contains a categorized index of all documentation files along with their priority levels.

The documentation index also includes the current development priorities based on our roadmap.

## Testing

All tests have been consolidated in the `tests/` directory. See [tests/README.md](./tests/README.md) for information on running tests and adding new ones.

# Documentation Has Moved

## IMPORTANT: Documentation First Approach

**The documentation for this project has been consolidated in the `documentation/` directory.**

Please refer to the following files:

- [PROJECT_OVERVIEW.md](../documentation/PROJECT_OVERVIEW.md) - Complete project overview
- [DOCUMENTATION_INDEX.md](../documentation/DOCUMENTATION_INDEX.md) - Index of all documentation

## DO NOT UPDATE THIS FILE

This directory is deprecated and maintained only for backwards compatibility.
Please update and refer to the documentation in the `documentation/` directory.

All future documentation updates should be made in the consolidated documentation structure.
