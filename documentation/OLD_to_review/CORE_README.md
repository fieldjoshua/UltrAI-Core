# UltraAI Framework

## IMPORTANT: Documentation First Approach

**BEFORE CREATING ANY NEW FEATURES OR MAKING CHANGES:**

1. **ALWAYS consult the documentation directory first**
2. **Check if the feature or pattern already exists**
3. **Review the consolidated documentation in `documentation/`**

## Documentation Structure

All official documentation is consolidated in the `documentation/` directory:

- For a complete overview of all documentation, see [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md)
- For technical implementation details, see the `instructions/` subdirectory
- For conceptual explanations, see the `logic/` subdirectory
- For contribution guidelines, see `guidelines/CONTRIBUTING.md`

## Analysis Patterns

UltraAI uses specialized analysis patterns ("feathers") to combine multiple LLM responses:

- **The definitive implementation** is in `src/patterns/ultra_analysis_patterns.py`
- **Technical documentation** is in `instructions/PATTERNS.md`
- **User-facing documentation** is in `logic/INTELLIGENCE_MULTIPLICATION.md`

## Contributing

To contribute to UltraAI:

1. **FIRST: Read the documentation to understand what already exists**
2. **DO NOT create new features or elements without confirming they don't already exist**
3. **ALWAYS consult `documentation/` before proposing changes**
4. **If unsure, refer to the documentation index and search for relevant information**
5. **Focus on improving and refining existing features rather than creating new ones**

We maintain a single source of truth for all functionality, and duplicate implementations cause confusion and maintenance problems.

## Running the Application

For testing the application:

```bash
./test_run.sh
```

This will start the backend on port 8085 and the frontend on port 3000.

## Next Steps

1. Review the [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md) to understand the system
2. Follow the setup instructions in the documentation
3. For developers, refer to the guidelines in the documentation directory

Remember: Documentation is the single source of truth for this project. Always check documentation before making changes.
