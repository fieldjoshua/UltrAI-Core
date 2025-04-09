# UltraAI Analysis Patterns - Definitive Reference

This document establishes the definitive reference for UltraAI analysis patterns (or "feathers") and provides guidelines for maintaining pattern consistency across the codebase.

## Source of Truth

The single source of truth for all pattern definitions is:

```
src/patterns/ultra_analysis_patterns.py
```

This file contains the complete implementation of all analysis patterns, including their:

- Name and description
- Stage definitions
- Template prompts
- Instruction sets

## Available Patterns

UltraAI supports the following analysis patterns:

| Pattern Key | Name | Description |
|-------------|------|-------------|
| `gut` | Gut Check Analysis | Relies on LLM intuition while considering other responses |
| `confidence` | Confidence Analysis | Analyzes responses with confidence scoring and agreement tracking |
| `critique` | Critique Analysis | Implements a structured critique and revision process |
| `fact_check` | Fact Check Analysis | Implements a rigorous fact-checking process |
| `perspective` | Perspective Analysis | Focuses on different analytical perspectives and integration |
| `scenario` | Scenario Analysis | Analyzes responses through different scenarios and conditions |
| `stakeholder` | Stakeholder Vision | Analyzes from multiple stakeholder perspectives |
| `systems` | Systems Mapper | Maps complex system dynamics with feedback loops |
| `time` | Time Horizon | Analyzes across multiple time frames |
| `innovation` | Innovation Bridge | Uses cross-domain analogies to discover non-obvious patterns |

## Pattern Structure

Each pattern follows this structure:

```python
AnalysisPattern(
    name="Pattern Name",
    description="Description of the pattern",
    stages=["initial", "meta", "hyper", "ultra"],
    templates={
        "meta": "Template for meta stage...",
        "hyper": "Template for hyper stage...",
        "ultra": "Template for ultra stage..."
    },
    instructions={
        "meta": ["Instruction 1", "Instruction 2", ...],
        "hyper": ["Instruction 1", "Instruction 2", ...],
        "ultra": ["Instruction 1", "Instruction 2", ...]
    }
)
```

## Naming Convention

To maintain consistency across the codebase:

1. **Backend Internal Key**: Use lowercase, snake_case keys (e.g., `confidence`, `fact_check`)
2. **API/Frontend Display Name**: Use proper title case (e.g., "Confidence Analysis", "Fact Check Analysis")
3. **User-Facing Documentation**: Use title case with full descriptive names

## Implementation Guidelines

### Adding a New Pattern

1. Add the pattern definition to `src/patterns/ultra_analysis_patterns.py`
2. Update the `get_pattern_mapping()` function to include your new pattern
3. Add the pattern to `PATTERN_METADATA` with a description
4. Update the mapping in `backend/routes/analyze_routes.py` for the API

### Modifying an Existing Pattern

1. Update only the definition in `src/patterns/ultra_analysis_patterns.py`
2. Run tests to ensure the changes work as expected
3. Update documentation to reflect any changes in behavior

### Deprecating a Pattern

1. Mark the pattern as deprecated in documentation
2. Keep the pattern implementation but add a deprecation notice
3. Update frontend to indicate pattern is deprecated

## Pattern Mapping in API

The backend API maps frontend-friendly names to internal pattern keys. This mapping exists in `backend/routes/analyze_routes.py`:

```python
PATTERN_NAME_MAPPING = {
    "Gut Check": "gut",
    "Confidence Analysis": "confidence",
    "Critique": "critique",
    "Fact Check Analysis": "fact_check",
    # etc.
}
```

## Implementation Files

The pattern orchestration logic is implemented in:

1. **Pattern Definitions**: `src/patterns/ultra_analysis_patterns.py`
2. **Pattern Orchestration**: `src/patterns/ultra_pattern_orchestrator.py`
3. **API Integration**: `backend/routes/analyze_routes.py`

## Common Issues

1. **Multiple Pattern Definitions**: Avoid duplicate definitions. Always use the source of truth.
2. **Inconsistent Pattern Keys**: Use the standardized keys listed in this document.
3. **Missing Mapping**: When adding patterns, update all mappings in the API layer.

## Testing Patterns

When testing patterns:

1. Create unit tests that validate each pattern stage
2. Use mock LLMs to test the orchestration flow
3. Create integration tests with real LLMs for end-to-end validation

## Documentation

Refer to `documentation/logic/INTELLIGENCE_MULTIPLICATION.md` for detailed explanations of each pattern's purpose and methodology from a user perspective.
