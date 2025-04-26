# Development Setup Guide

## AICheck Development Rules

Before starting development, please review the [AICheck Development Rules](../../RULES.md). Key principles include:

1. **Documentation First**: All Actions must be documented before implementation
2. **Single Action Focus**: Work on one Action at a time
3. **Explicit Context Switching**: Document context switches
4. **Structured AI Interactions**: Use provided templates
5. **Regular Session Logging**: Document all AI sessions

## Development Environment Setup

### Prerequisites

- Python 3.8 or higher
- Git
- Docker (optional)
- AICheck CLI installed

### Initial Setup

1. Clone the repository:

```bash
git clone https://github.com/yourusername/ultra.git
cd ultra
```

2. Install AICheck CLI:

```bash
pip install aicheck-cli
```

3. Initialize AICheck:

```bash
aicheck init
```

### Development Workflow

1. Start a development session:

```bash
./ai start
```

2. Check current focus:

```bash
./ai status
```

3. Create a new Action:

```bash
./ai new ActionName
```

4. End session with summary:

```bash
./ai end "summary of work completed"
```

## Directory Structure

```
.aicheck/
├── actions/
│   └── [ACTION_NAME]/
│       ├── [ACTION_NAME]-PLAN.md
│       └── supporting_docs/
├── docs/
│   ├── actions_index.md
│   └── README.md
└── sessions/
    └── session_log.txt
```

## Development Guidelines

### Action Management

1. Each Action must have:
   - A clear plan document
   - Supporting documentation
   - Defined scope and objectives

2. Action Documentation:
   - Located in `.aicheck/actions/[ACTION_NAME]/`
   - Must be completed before implementation
   - Should include success criteria

### Code Development

1. Follow the current Action plan
2. Maintain single Action focus
3. Document context switches
4. Use provided AI interaction templates
5. Log all significant Cursor interactions

### Testing Requirements

1. Unit tests for all new functionality
2. Integration tests for Action components
3. End-to-end tests for complete features
4. Test documentation in Action plan

### Documentation Requirements

1. Update Action documentation as needed
2. Maintain session logs
3. Document all significant decisions
4. Keep README files current

## Best Practices

1. **Code Organization**
   - Follow project structure
   - Maintain clear separation of concerns
   - Use consistent naming conventions

2. **Version Control**
   - Create feature branches
   - Write clear commit messages
   - Follow branching strategy

3. **Code Review**
   - Review against Action plan
   - Check documentation completeness
   - Verify test coverage

4. **AI Integration**
   - Use Cursor AI effectively
   - Document AI interactions
   - Follow AI guidelines

## Troubleshooting

1. **Common Issues**
   - Action documentation missing
   - Context switching not documented
   - Incomplete session logs

2. **Resolution Steps**
   - Check Action documentation
   - Review session logs
   - Consult AICheck rules

## Additional Resources

- [AICheck Documentation](../../.aicheck/docs/README.md)
- [Actions Index](../../.aicheck/docs/actions_index.md)
- [Session Logs](../../.aicheck/sessions/session_log.txt)
