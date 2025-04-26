# Directory Structure

## Root Directory

```
.
├── .aicheck/             # AICheck system files
│   ├── actions/         # Action plans and documentation
│   │   └── [ACTION_NAME]/
│   │       ├── [ACTION_NAME]-PLAN.md
│   │       └── supporting_docs/
│   ├── docs/           # System documentation
│   └── sessions/       # Session logs
├── backend/            # Backend application
├── frontend/           # Frontend application
└── documentation/      # Project documentation
```

## Backend Structure

```
backend/
├── app.py                 # Main application entry point
├── config.py             # Configuration management
├── database/             # Database models and migrations
├── routes/              # API route handlers
├── services/            # Business logic services
└── utils/               # Utility functions
```

## Frontend Structure

```
frontend/
├── src/                # Source code
│   ├── components/     # React components
│   ├── services/      # API services
│   ├── hooks/         # Custom React hooks
│   ├── utils/         # Utility functions
│   └── types/         # TypeScript types
├── public/            # Static assets
└── tests/             # Frontend tests
```

## Documentation Structure

```
documentation/
├── api/               # API documentation
├── guides/            # User guides
└── architecture/      # Architecture documentation
```

## AICheck Structure

```
.aicheck/
├── actions/           # Action plans and documentation
│   └── [ACTION_NAME]/ # Action-specific directory
│       ├── [ACTION_NAME]-PLAN.md
│       └── supporting_docs/
├── docs/             # System documentation
└── sessions/         # Session logs
```

## Notes

- All action plans must be stored in `.aicheck/actions/[ACTION_NAME]/[ACTION_NAME]-PLAN.md`
- Supporting documentation for actions should be in `.aicheck/actions/[ACTION_NAME]/supporting_docs/`
- Each action should have its own directory with a clear naming convention
- Action directories should contain both the plan and supporting documentation
