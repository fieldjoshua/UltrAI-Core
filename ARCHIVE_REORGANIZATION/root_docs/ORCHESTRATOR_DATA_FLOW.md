# UltrAI Orchestrator Data Flow

This document provides a comprehensive overview of the UltrAI Orchestrator system, including data flow, script organization, modules, and dependencies.

## System Architecture Overview

```
┌───────────────────┐     ┌───────────────────┐     ┌───────────────────┐
│                   │     │                   │     │                   │
│  User Interfaces  │────▶│   Orchestrators   │────▶│  LLM Providers    │
│                   │     │                   │     │                   │
└───────────────────┘     └───────────────────┘     └───────────────────┘
         │                        │                          ▲
         │                        │                          │
         │                        ▼                          │
         │               ┌───────────────────┐               │
         └──────────────▶│   Core Services   │───────────────┘
                         │                   │
                         └───────────────────┘
                                  │
                                  ▼
                         ┌───────────────────┐
                         │                   │
                         │  Analysis Modules │
                         │                   │
                         └───────────────────┘
```

## 1. User Interface Layer

### CLI Scripts

- `ultra_cli.py`: Main command-line interface
- `menu_ultra.sh`: Menu-based launcher with interactive options
- `simple_ultra.sh`: Simplified interface for quick usage
- `ultimate.sh`: Enhanced interface with progress visualization
- `interactive_ultra.sh`: Interactive launcher with model selection dialog
- `real_api_menu.sh`: Menu interface specifically for using real API keys
- `fixed_with_analysis.sh`: Launcher that includes runtime analysis fixes
- `launch_ultra.sh`: Simple launcher that sources environment variables
- `wrapper.py`: Progress bar and error suppression wrapper

### Environment Setup

- `setup_env.sh`: Creates template .env file for API configuration

## 2. Orchestrator Layer

### Orchestrator Implementations

- `src/simple_core/orchestrator.py`: Base orchestrator implementation
- `src/simple_core/enhanced_orchestrator.py`: Second iteration with advanced features
- `src/simple_core/modular_orchestrator.py`: Third iteration with pluggable components

### Configuration

- `src/simple_core/config.py`: Core configuration components
- `src/simple_core/config/request_config.py`: Request configuration models
- `src/simple_core/config/analysis_config.py`: Analysis configuration models
- `src/simple_core/config/factory_helpers.py`: Factory helper functions

### Factory System

- `src/simple_core/factory.py`: Factory for creating orchestrator instances from environment

## 3. Adapter Layer

### Adapter Framework

- `src/simple_core/adapter.py`: Base adapter interface and core implementations
- `src/simple_core/adapter_extensions.py`: Extended adapters for additional providers

### Supported Providers

1. OpenAI (GPT-4, GPT-3.5)
2. Anthropic (Claude)
3. Google (Gemini)
4. Deepseek
5. Ollama (local models)
6. Local Llama (via shell execution)
7. Mock providers (for testing)

## 4. Analysis Layer

### Analysis Framework

- `src/simple_core/analysis/analysis_module.py`: Base analysis module interface
- `src/simple_core/analysis/analysis_manager.py`: Manager for analysis modules
- `src/simple_core/analysis/results.py`: Analysis result models

### Analysis Modules

- `src/simple_core/analysis/modules/comparative.py`: Comparative analysis of multiple responses
- `src/simple_core/analysis/modules/factual.py`: Factual accuracy analysis

### Runtime Fixes

- `src/simple_core/analysis_fix.py`: Patch for analysis module configuration
- `apply_fix.py`: Runtime application of analysis fixes
- `direct_analysis_fix.py`: Direct fixes for analysis module issues

## 5. Services Layer

### Caching

- `src/simple_core/cache_service.py`: Response caching service

### Quality Assessment

- `src/simple_core/quality_metrics.py`: Response quality assessment

### Prompt Management

- `src/simple_core/prompt_templates.py`: Template management for system prompts

## 6. Testing Layer

### Test Scripts

- `test_basic_orchestrator.py`: Tests for basic orchestrator
- `test_orchestrator.py`: General orchestrator tests
- `test_real_orchestrator.py`: Tests with real LLM adapters
- `test_orchestrator_with_real_apis.py`: Tests using actual API keys
- `run_enhanced_test.py`: Tests for enhanced orchestrator
- `run_modular_test.py`: Tests for modular orchestrator with comparative analysis
- `run_factual_test.py`: Tests for modular orchestrator with factual analysis
- `run_specific_prompt.py`: Test with specific angel investor prompt

## 7. Example Layer

### Example Scripts

- `src/simple_core/examples/basic_usage.py`: Basic usage examples
- `src/simple_core/examples/enhanced_interactive.py`: Enhanced orchestrator examples
- `src/simple_core/examples/interactive.py`: Interactive session examples
- `src/simple_core/examples/modular_example.py`: Modular orchestrator examples

## Data Flow Sequence

### Request Flow

1. User interacts with one of the shell interface scripts
2. Interface collects configuration and creates a request
3. Request is passed to `ultra_cli.py` (main entry point)
4. CLI processes request and forwards to appropriate orchestrator via factory
5. Orchestrator processes request through multiple phases:
   - Request validation and preparation
   - LLM provider selection
   - Parallel execution across providers
   - Response collection
   - Analysis (if configured)
   - Synthesis (for enhanced/modular orchestrator)
6. Results are formatted and returned to the user interface
7. Interface presents results based on configuration

### Response Flow

```
┌───────────┐     ┌───────────┐     ┌───────────┐     ┌───────────┐
│           │     │           │     │           │     │           │
│  Request  │────▶│ Providers │────▶│ Analysis  │────▶│ Synthesis │
│           │     │           │     │           │     │           │
└───────────┘     └───────────┘     └───────────┘     └───────────┘
      ▲                 │                 │                 │
      │                 │                 │                 │
      │                 ▼                 ▼                 ▼
      │           ┌──────────────────────────────────────────┐
      │           │                                          │
      └───────────│               Cache                      │
                  │                                          │
                  └──────────────────────────────────────────┘
```

## External Dependencies

### Required Python Packages

- Core dependencies:

  - `aiohttp`: Async HTTP requests
  - `asyncio`: Asynchronous I/O
  - `pydantic`: Data validation
  - `python-dotenv`: Environment variable management
  - `tenacity`: Retry logic
  - `tqdm`: Progress bars

- Provider-specific dependencies:
  - `openai`: OpenAI API
  - `anthropic`: Anthropic API
  - `google-generativeai`: Google Gemini API

### Optional Dependencies

- `colorama`: Terminal color support
- `rich`: Enhanced terminal formatting
- `uvloop`: Faster event loop (Unix only)

## Environment Variables

The orchestrator system uses the following environment variables for configuration:

```
# OpenAI API Key and Organization ID
OPENAI_API_KEY="your_openai_api_key_here"
OPENAI_ORG_ID="your_openai_org_id_here"

# Anthropic API Key
ANTHROPIC_API_KEY="your_anthropic_api_key_here"

# Google API Key (for Gemini)
GOOGLE_API_KEY="your_google_api_key_here"

# Deepseek API Key and Base URL
DEEPSEEK_API_KEY="your_deepseek_api_key_here"
DEEPSEEK_API_BASE="https://api.deepseek.com"

# Ollama Configuration
OLLAMA_BASE_URL="http://localhost:11434"
OLLAMA_MODEL="llama3"

# Optional: Path to a local Llama model
LLAMA_MODEL_PATH="/path/to/llama/model"
LLAMA_COMMAND="llama"

# Mock mode for testing
USE_MOCK=true|false
```

## File Structure Summary

```
/
├── scripts/                                 # Launch scripts
│   ├── ultra_cli.py                         # Main CLI interface
│   ├── menu_ultra.sh                        # Menu-based launcher
│   ├── simple_ultra.sh                      # Simplified launcher
│   ├── ultimate.sh                          # Enhanced launcher
│   └── ...
│
├── src/
│   └── simple_core/                         # Core orchestration system
│       ├── __init__.py
│       ├── adapter.py                       # LLM adapters
│       ├── adapter_extensions.py            # Additional adapters
│       ├── orchestrator.py                  # Base orchestrator
│       ├── enhanced_orchestrator.py         # Enhanced orchestrator
│       ├── modular_orchestrator.py          # Modular orchestrator
│       ├── factory.py                       # Factory system
│       ├── cache_service.py                 # Caching service
│       ├── quality_metrics.py               # Quality assessment
│       ├── prompt_templates.py              # Prompt management
│       ├── analysis_fix.py                  # Analysis fixes
│       │
│       ├── config/                          # Configuration
│       │   ├── __init__.py
│       │   ├── request_config.py            # Request configuration
│       │   ├── analysis_config.py           # Analysis configuration
│       │   └── factory_helpers.py           # Factory helpers
│       │
│       ├── analysis/                        # Analysis system
│       │   ├── __init__.py
│       │   ├── analysis_module.py           # Base interface
│       │   ├── analysis_manager.py          # Management
│       │   ├── results.py                   # Result models
│       │   │
│       │   └── modules/                     # Analysis modules
│       │       ├── __init__.py
│       │       ├── comparative.py           # Comparative analysis
│       │       └── factual.py               # Factual analysis
│       │
│       └── examples/                        # Example usage
│           ├── basic_usage.py
│           ├── enhanced_interactive.py
│           ├── interactive.py
│           └── modular_example.py
│
├── tests/                                   # Test scripts
│   ├── test_basic_orchestrator.py
│   ├── test_orchestrator.py
│   ├── test_real_orchestrator.py
│   └── test_orchestrator_with_real_apis.py
│
├── .env                                     # Environment variables
└── setup_env.sh                             # Environment setup
```

## Detailed Script Descriptions

### CLI Scripts

1. **ultra_cli.py**

   - Main entry point for the orchestrator
   - Processes command-line arguments
   - Creates and configures orchestrator instance
   - Manages response formatting and display

2. **menu_ultra.sh**

   - Interactive menu for configuration
   - Supports model selection, analysis type, display options
   - Builds appropriate command for ultra_cli.py

3. **simple_ultra.sh**

   - Simplified interface for quick usage
   - Focuses on common options
   - Uses mock mode for demonstration

4. **ultimate.sh**
   - Enhanced interface with visual elements
   - Progress bars and spinners
   - Error suppression
   - Colorized output

### Orchestrators

1. **BaseOrchestrator** (orchestrator.py)

   - Handles basic request processing
   - Manages provider connection
   - Executes requests against a single model
   - Provides caching (if enabled)

2. **EnhancedOrchestrator** (enhanced_orchestrator.py)

   - Extends BaseOrchestrator
   - Supports multiple models
   - Adds quality assessment
   - Implements multi-stage processing

3. **ModularOrchestrator** (modular_orchestrator.py)
   - Fully modular architecture
   - Pluggable analysis modules
   - Advanced request configuration
   - Support for sophisticated synthesis

### Dependency Chain

```
┌─────────────┐
│             │
│  User CLI   │
│             │
└─────────────┘
       │
       ▼
┌─────────────┐     ┌─────────────┐
│             │     │             │
│   Factory   │────▶│  Orchestrator│
│             │     │             │
└─────────────┘     └─────────────┘
                         │
                         ▼
                   ┌─────────────┐
                   │             │
                   │   Adapters  │
                   │             │
                   └─────────────┘
                         │
                         ▼
                   ┌─────────────┐
                   │             │
                   │ LLM Services│
                   │             │
                   └─────────────┘
```

This data flow summary provides a comprehensive overview of the UltrAI Orchestrator system architecture, components, and relationships.
