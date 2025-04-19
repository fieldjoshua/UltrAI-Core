# UltraAI Usage Examples

This document provides example code and usage patterns for the Ultra AI Framework.

## IMPORTANT: Documentation First Approach

**BEFORE CREATING ANY NEW FEATURES OR MAKING CHANGES:**

1. **ALWAYS consult the documentation directory first**
2. **Check if the feature or pattern already exists**
3. **Review the consolidated documentation in `documentation/`**

## Available Examples

The `examples/` directory contains:

- **llm_clients/**: Examples of using different LLM providers
  - `claude_test_new.py`: Example of using Claude models
  - `search_pypi.py`: PyPI package search utility

- `debug.py`, `debug2.py`: Debugging utilities and example workflows

## Basic Example

```python
from ultra import Ultra

# Initialize the Ultra framework
ultra = Ultra()

# Run a standard analysis
result = ultra.analyze("What are the key advantages of transformers over RNNs?")
print(result)
```

## Document Processing Example

```python
from ultra import Ultra
from ultra.document_processing import Document

# Initialize
ultra = Ultra()

# Load and process document
document = Document.from_file("research_paper.pdf")
ultra.add_document(document)

# Ask question about the document
result = ultra.analyze("Summarize the methodology section of the research paper.")
print(result)
```

## Analysis Pattern Example

```python
from ultra import Ultra
from ultra.patterns import AnalysisPattern

# Initialize
ultra = Ultra()

# Use a specific pattern
result = ultra.analyze(
    "What are potential risks of deploying this system?",
    pattern=AnalysisPattern.CRITIQUE
)
print(result)
```

## Available Analysis Patterns

The framework provides several analysis patterns that you can use:

```python
# Import the analysis patterns
from ultra.patterns import AnalysisPattern

# Available patterns:
AnalysisPattern.GUT           # Gut Analysis
AnalysisPattern.CONFIDENCE    # Confidence Analysis
AnalysisPattern.CRITIQUE      # Critique Analysis
AnalysisPattern.FACT_CHECK    # Fact Check Analysis
AnalysisPattern.PERSPECTIVE   # Perspective Analysis
AnalysisPattern.SCENARIO      # Scenario Analysis
AnalysisPattern.STAKEHOLDER   # Stakeholder Vision
AnalysisPattern.SYSTEMS       # Systems Mapper
AnalysisPattern.TIME          # Time Horizon
AnalysisPattern.INNOVATION    # Innovation Bridge
```

For details on each pattern, see [INTELLIGENCE_MULTIPLICATION.md](INTELLIGENCE_MULTIPLICATION.md).

## Running Examples

To run an example:

```bash
python examples/debug.py
```

Or for LLM client examples:

```bash
python examples/llm_clients/claude_test_new.py
```

## Adding New Examples

When adding new examples:

1. **First check** if similar functionality already exists
2. Follow the existing patterns and code style
3. Include appropriate documentation and comments
4. Update this documentation to reference the new example

## Testing Examples Locally

For quick testing with the test backend:

```bash
./test_run.sh
```

This will:

1. Start a simple backend on port 8085
2. Start a frontend on port 3000
3. Allow you to test your examples against the test backend
