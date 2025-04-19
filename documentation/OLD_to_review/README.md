# UltraAI Framework

Welcome to the UltraAI Framework - a powerful orchestration system for Large Language Models (LLMs) that enables complex, multi-stage reasoning patterns through intelligent model collaboration.

## IMPORTANT: Documentation-First Approach

**BEFORE creating any new features or making any changes:**

1. **ALWAYS consult the documentation directory first**
2. **Check if the feature or pattern already exists**
3. **Review the consolidated documentation in `documentation/`**

We maintain a single source of truth for all functionality. Duplicate implementations cause confusion and maintenance problems.

## Quick Start

### Running the Application

```bash
./test_run.sh
```

This will start the backend on port 8085 and the frontend on port 3000.

### Using Docker

```bash
# Build and run with Docker
docker-compose up -d

# Access the application
Frontend: http://localhost:3000
Backend API: http://localhost:8080
Performance Dashboard: http://localhost:3000/dashboard
```

## Core Components

### Analysis Patterns ("Feathers")

UltraAI uses specialized analysis patterns to combine multiple LLM responses in intelligent ways:

- **Technical Implementation**: The definitive implementation is in `src/patterns/ultra_analysis_patterns.py`
- **Technical Documentation**: See `documentation/instructions/PATTERNS.md` for pattern structure and implementation
- **Conceptual Guide**: See `documentation/logic/INTELLIGENCE_MULTIPLICATION.md` for methodology and use cases

Available patterns include:
- Gut Check Analysis
- Confidence Analysis
- Critique Analysis
- Fact Check Analysis
- Perspective Analysis
- Scenario Analysis
- Stakeholder Vision
- Systems Mapper
- Time Horizon
- Innovation Bridge

### Multi-Stage Analysis Process

Each analysis follows a multi-stage orchestration pattern:

1. **Initial Responses**: Get responses from all available models
2. **Meta Analysis**: Each model analyzes and reviews the collective responses
3. **Hyper Analysis**: Models analyze the meta-level reviews
4. **Ultra Synthesis**: A final comprehensive synthesis is produced

### Document Processing

The framework includes advanced document processing capabilities:

- Smart document chunking and semantic indexing
- Vector-based similarity search
- Multiple file format support (PDF, TXT, DOCX, etc.)
- Context optimization for LLM prompts

## Project Structure

```
project/
├── src/                    # Core source code
│   ├── models/             # LLM client integrations
│   ├── patterns/           # Analysis pattern implementations
│   └── ...                 # Other core modules
├── frontend/               # UI components and frontend code
├── backend/                # Server-side implementation
├── documentation/          # Project documentation (consolidated)
│   ├── guidelines/         # Standards and conventions
│   ├── instructions/       # How-to guides and procedures
│   ├── logic/              # Design documents and rationale
│   └── ...                 # Other documentation categories
└── ...                     # Other project directories
```

For a complete overview of all directories, see [PROJECT_OVERVIEW.md](documentation/PROJECT_OVERVIEW.md).

## Documentation Structure

All official documentation is consolidated in the `documentation/` directory:

- **implementation_plans/**: Detailed plans for building and implementing each phase of development
- **logic/**: Design documents explaining reasoning and rationale behind features
- **instructions/**: How-to guides and procedural documents
- **guidelines/**: Standards and conventions documents
- **performance/**: Performance-related documentation
- **cloud/**: Cloud deployment documentation
- **pricing/**: Pricing-related documentation

### Key Documentation Files

- [documentation/DOCUMENTATION_INDEX.md](documentation/DOCUMENTATION_INDEX.md): Complete catalog of all documentation
- [documentation/guidelines/CONTRIBUTING.md](documentation/guidelines/CONTRIBUTING.md): Contribution guidelines
- [documentation/instructions/PATTERNS.md](documentation/instructions/PATTERNS.md): Technical reference for pattern implementation
- [documentation/logic/INTELLIGENCE_MULTIPLICATION.md](documentation/logic/INTELLIGENCE_MULTIPLICATION.md): Conceptual guide to pattern methodologies
- [documentation/instructions/ANALYSIS_TROUBLESHOOTING.md](documentation/instructions/ANALYSIS_TROUBLESHOOTING.md): Troubleshooting guide for analysis issues

## Using with AI Assistants

UltraAI is designed to work seamlessly with AI coding assistants. When using AI tools with this project:

- Begin by asking the AI to review relevant documentation
- Use the prompts in [documentation/AI_USAGE_GUIDE.md](documentation/AI_USAGE_GUIDE.md)
- Provide AI with appropriate context from documentation
- Verify AI-generated code against existing patterns
- Ask AI to check for duplicate functionality before implementing features

For comprehensive guidance on using AI tools with UltraAI, see [documentation/AI_USAGE_GUIDE.md](documentation/AI_USAGE_GUIDE.md).

## Contributing

To contribute to UltraAI:

1. **Read the documentation** to understand what already exists
2. **DO NOT create new features** or elements without confirming they don't already exist
3. **ALWAYS consult `documentation/`** before proposing changes
4. **If unsure, refer to the documentation index** and search for relevant information
5. **Focus on improving and refining existing features** rather than creating new ones

For detailed contribution guidelines, see [documentation/guidelines/CONTRIBUTING.md](documentation/guidelines/CONTRIBUTING.md).

## Recent Updates

- **Port Configuration**: Backend now runs on port 8080 (changed from 11434)
- **Docker Support**: New multi-stage Dockerfile and docker-compose.yml for optimized deployment
- **Build Optimizations**: Improved build process with code splitting and minification
- **Document Processing**: Enhanced document handling with better chunking and relevance scoring
- **Performance Dashboard**: New comprehensive dashboard for real-time system monitoring and metrics
- **Documentation Consolidation**: All documentation has been consolidated in the `documentation/` directory
- **AI Assistant Support**: Added guidance for working with AI coding assistants

## Getting Started for New Users

If you're new to UltraAI, start by reading:

1. This README.md for a high-level overview
2. [documentation/logic/README_NEW_STRUCTURE.md](documentation/logic/README_NEW_STRUCTURE.md) for system architecture
3. [documentation/logic/INTELLIGENCE_MULTIPLICATION.md](documentation/logic/INTELLIGENCE_MULTIPLICATION.md) for analysis patterns
4. [documentation/DOCUMENTATION_INDEX.md](documentation/DOCUMENTATION_INDEX.md) for a complete list of documentation

## Need Help?

- **For technical questions**: See [documentation/instructions/ANALYSIS_TROUBLESHOOTING.md](documentation/instructions/ANALYSIS_TROUBLESHOOTING.md)
- **For contribution guidance**: See [documentation/guidelines/CONTRIBUTING.md](documentation/guidelines/CONTRIBUTING.md)
- **For an overview of documentation**: See [documentation/DOCUMENTATION_INDEX.md](documentation/DOCUMENTATION_INDEX.md)
- **For AI assistant usage**: See [documentation/AI_USAGE_GUIDE.md](documentation/AI_USAGE_GUIDE.md)

Remember: Documentation is the single source of truth for this project. Always check documentation before making changes.
