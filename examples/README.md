# Ultra Examples

This directory contains example code and usage patterns for the Ultra AI Framework.

## Directory Structure

- **llm_clients/**: Examples of using different LLM providers
  - `claude_test_new.py`: Example of using Claude models
  - `search_pypi.py`: PyPI package search utility

- `debug.py`, `debug2.py`: Debugging utilities and example workflows

## Usage Examples

### Basic Example

```python
from ultra import Ultra

# Initialize the Ultra framework
ultra = Ultra()

# Run a standard analysis
result = ultra.analyze("What are the key advantages of transformers over RNNs?")
print(result)
```

### Document Processing Example

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

### Advanced Pattern Example

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

## Running Examples

To run an example:

```bash
python examples/debug.py
```

Or for LLM client examples:

```bash
python examples/llm_clients/claude_test_new.py
```
