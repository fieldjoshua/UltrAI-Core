# Directory Structure

This document defines the target directory structure for the UltraAI codebase. It provides detailed information about each directory, its purpose, and organization guidelines.

## Root-Level Structure

```
ultraai/
├── Actions/             # Action plans
│   └── CODEBASE_REORGANIZATION/
│       └── UNCLASSIFIED/    # Temporary location for unclear content
├── documentation/       # Core documentation
├── frontend/            # Frontend application
├── backend/             # Backend services
├── src/                 # Core shared code
├── tests/               # Test suite
└── scripts/             # Utility scripts
```

## Primary Directories

### Actions/

Contains all action plans and their supporting documentation. Each action has its own directory.

```
Actions/
├── API_DEVELOPMENT/
│   ├── PLAN.md
│   └── [Supporting documents]
├── BACKEND_INTEGRATION/
│   ├── PLAN.md
│   └── [Supporting documents]
└── [Other actions]/
```

### documentation/

Contains core documentation that applies to the entire project.

```
documentation/
├── Controlling_README.md       # Project overview
├── Controlling_GUIDELINES.md   # Documentation standards
├── ACTIONS_INDEX.md            # Index of all actions
├── Templates/                  # Document templates
│   ├── PLAN_TEMPLATE.md
│   └── [Other templates]
└── OLD_to_review/              # Legacy content
```

### frontend/

Contains all frontend application code.

```
frontend/
├── src/                 # Frontend source code
│   ├── components/      # Reusable UI components
│   ├── pages/           # Page definitions
│   ├── hooks/           # Custom React hooks
│   ├── context/         # React context providers
│   ├── utils/           # Frontend utilities
│   └── styles/          # Global styles
├── public/              # Static assets
├── cloud/               # Cloud-specific frontend
└── tests/               # Frontend-specific tests
```

### backend/

Contains all backend service code.

```
backend/
├── api/                 # API implementation
│   ├── routes/          # API route definitions
│   ├── controllers/     # Request handlers
│   ├── middleware/      # API middleware
│   ├── validation/      # Request validation
│   ├── mocks/           # API mocks (from mock-api/)
│   └── public/          # Public API (from public_api/)
├── services/            # Business logic services
├── db/                  # Database integration
│   ├── models/          # Data models
│   ├── migrations/      # Database migrations
│   └── seeds/           # Seed data
├── cloud/               # Cloud services (from cloud_backend/)
└── utils/               # Backend utilities
```

### src/

Contains core shared code used by both frontend and backend.

```
src/
├── core/                # Core functionality
│   ├── models/          # Shared data models
│   ├── types/           # TypeScript type definitions
│   └── constants/       # Shared constants
├── ai/                  # AI orchestration code
│   ├── models/          # AI model integrations
│   ├── patterns/        # Collaboration patterns
│   └── prompts/         # Prompt templates
├── utils/               # Shared utilities
├── config/              # Configuration (from config/)
├── data/                # Data management (from data/)
├── deployment/          # Deployment utilities (from deployment/)
├── monitoring/          # System monitoring (from monitoring/)
└── examples/            # Example code (from examples/)
```

### tests/

Contains all test code.

```
tests/
├── unit/                # Unit tests
├── integration/         # Integration tests
├── e2e/                 # End-to-end tests (from cypress/)
├── frontend/            # Frontend tests (from test_frontend/)
├── performance/         # Performance tests (from benchmarks/)
└── fixtures/            # Test fixtures
```

### scripts/

Contains utility scripts for development, building, and deployment.

```
scripts/
├── build/               # Build scripts
├── dev/                 # Development scripts
├── deploy/              # Deployment scripts
└── utils/               # Utility scripts
```

## Directory Guidelines

### Naming Conventions

- Use lowercase names for directories with single-word names (e.g., `src/`, `tests/`)
- Use camelCase for directories with multi-word names (e.g., `frontend/components/`)
- Use PascalCase for component directories in React code (e.g., `components/Button/`)

### File Organization

- Group files by feature or module, not by file type
- Keep related files close together
- Use index files to expose public API of directories
- Minimize directory nesting (aim for max 4-5 levels)

### Imports

- Use relative imports for files in the same directory or nearby
- Use absolute imports for distant modules
- Avoid complex relative paths (more than 2-3 levels)

## Directory Ownership

Each directory has a corresponding action that owns and maintains it:

| Directory | Owning Action |
|-----------|---------------|
| `frontend/` | FRONTEND_DEVELOPMENT |
| `backend/` | BACKEND_INTEGRATION |
| `src/ai/` | INTELLIGENCE_MULTIPLICATION |
| `src/data/` | DATA_MANAGEMENT |
| `backend/api/` | API_DEVELOPMENT |
| `src/deployment/` | DEPLOYMENT_ARCHITECTURE |
| `tests/` | TESTING_STRATEGY |
| `backend/cloud/` & `frontend/cloud/` | CLOUD_INTEGRATION |

## Migration Guidelines

1. When migrating a file, ensure all imports are updated
2. Maintain the same relative position of files within their module
3. Use path aliases to minimize import path changes
4. Document any structure changes in the action's documentation

## Last Updated: [Current Date]
