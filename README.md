# Ultra Framework

The Ultra Framework is a powerful orchestration system for LLMs that allows for complex, multi-stage reasoning patterns. It leverages multiple models to enhance analysis quality and reliability.

## Key Features

- **Multiple Analysis Patterns**: Gut Analysis, Confidence Analysis, Critique Analysis, Fact Check Analysis, Perspective Analysis, and Scenario Analysis
- **Multi-Model Orchestration**: Utilizes multiple LLMs (Claude, ChatGPT, Gemini, etc.) in parallel 
- **Multi-Level Processing**: Initial, meta, hyper, and ultra level analysis for thorough reasoning
- **Local Output Storage**: All outputs are saved to disk for review and analysis
- **File Attachment Support**: Analyze documents by attaching files to provide context for LLMs

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

- Supported file formats: `.pdf`, `.txt`, `.md`, `.docx`, `.doc`
- Files are processed and their content is included in the analysis
- File content is stored securely and only used for the current analysis
- Metadata about attached files is saved for reference

## Requirements

See `requirements.txt` for required Python packages.

For file attachment support:
- PyPDF2 (for PDF files)
- python-docx (for DOCX files)
- textract (for DOC files)

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
- `ultra_documents.py`: Document processing and file handling
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
