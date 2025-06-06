# Ultra Source Code

This directory contains the core source code for the Ultra AI Framework.

## Directory Structure

- **models/**: LLM client integrations and model definitions
  - `ultra_llm.py`: Low-level LLM client implementations
  - `ultra_models.py`: Model configuration and specifications
  - `ultra_model_selector.py`: Model selection and fallback logic

- **patterns/**: Analysis pattern implementations
  - `ultra_pattern_orchestrator.py`: Orchestration of multiple analysis patterns
  - `ultra_analysis_patterns.py`: Individual analysis pattern definitions

- **document_processing/**: Document handling functionality
  - `ultra_documents.py`: Document processing and embedding
  - `ultra_documents_optimized.py`: Optimized document handling for large files

- **utils/**: Shared utilities and helpers
  - `ultra_error_handling.py`: Error handling and logging
  - `ultra_config.py`: Configuration management
  - `ultra_security.py`: Security and authentication

- **config/**: Configuration files and data
  - `ultra_data.py`: Data structures and constants
  - `analysis_patterns_prompts.csv`: Prompt templates for analysis patterns

## Core Files

- `ultra_main.py`: Main entry point and application logic
- `ultra.py`: High-level API for the Ultra framework
- `ultra_base.py`: Base classes and abstract interfaces
- `ultra_hyper.py`: Hyper-level analysis implementations
