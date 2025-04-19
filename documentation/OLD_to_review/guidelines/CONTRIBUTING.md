# Contributing to UltrAI

This document outlines the coding standards, tools, and workflows for contributing to the UltrAI project.

## Code Style & Linting

### Python Code Style

We use the following tools for Python code quality:

1. **Black** - For code formatting
   - Line length: 88 characters
   - Black is non-negotiable - it formats your code automatically

2. **isort** - For import sorting
   - Compatible with Black formatting

3. **flake8** - For code linting
   - With additional plugins: flake8-bandit, flake8-bugbear
   - Max line length: 88 characters (matching Black)

**Note:** While there is a `.pylintrc` file in the repository, we prefer **flake8** as our primary linter. Pylint is only used for additional checks not covered by flake8.

### JavaScript/TypeScript Code Style

For frontend code:

1. **ESLint** - For linting
   - Primary configuration is in `.eslintrc.json` (`.eslintrc.js` is deprecated)
   - React-specific rules are enabled

2. **Prettier** - For code formatting
   - Configuration in `.prettierrc`
   - Integrated with ESLint via eslint-config-prettier

## Code Organization Guidelines

When creating or modifying code structure:

1. **Avoid superfluous code files and directories** - Before creating new files or directories:
   - Check if the functionality can fit within existing files or modules
   - Ensure new files serve a unique purpose that can't be accomplished with existing ones
   - Follow the established project structure and organization patterns

2. **Keep related code together** - Group related functionality in the same modules or directories
   - Place code that changes together in the same file/module when appropriate
   - Break down large files into logical modules when they exceed 300-400 lines

3. **Use clear, consistent naming** - Name files and directories to clearly reflect their purpose
   - Follow existing naming conventions in the project
   - Prefer specific names over generic ones (e.g., `user_authentication.py` over `utils2.py`)

4. **Minimize module dependencies** - Design code to minimize tight coupling between modules
   - Consider interface boundaries and what truly needs to be exposed

## Documentation Guidelines

When creating or updating documentation:

1. **Avoid superfluous documents** - Before creating a new document, check if:
   - The information can be added to an existing document
   - The document serves a unique purpose not already covered
   - The creation follows project conventions

2. **Keep documentation updated** - When making code changes, update related documentation
   - The documentation/implementation_plans/ROADMAP.md file should be updated when completing tasks
   - README files should reflect the current state of the codebase

3. **Use consistent formatting** - Follow Markdown standards for all documentation

## Documentation First Approach

**CRITICAL: Before creating any new features or making changes:**

1. **ALWAYS consult the documentation directory first**
2. **Check if the feature or pattern already exists**
3. **Review all relevant documentation in `documentation/`**

We maintain a single source of truth for all functionality, and duplicate implementations cause confusion and maintenance problems.

### Why This Is Important

- **Prevent Duplication**: Many features and patterns are already implemented
- **Maintain Consistency**: Follow established patterns and conventions
- **Single Source of Truth**: We strictly follow the documentation as our guide
- **Reduce Technical Debt**: Duplicated code and features lead to maintenance issues

### What to Do Instead

- **Improve Existing Features**: Focus on enhancing what already exists
- **Fix Bugs**: Prioritize fixing issues over adding new functionality
- **Refactor**: Improve code quality while maintaining functionality
- **Document**: Enhance documentation for existing features
- **Test**: Add or improve tests for existing functionality

## Mandatory Code Review Process

### Pre-Submission Review Checklist

**ALL code changes require a thorough self-review and documentation check before requesting review from others.**

Before submitting code for review, ensure you:

1. **✓ Documentation First Check**
   - Have you consulted all relevant documentation in the `documentation/` directory?
   - Have you verified that your feature/change aligns with existing patterns?
   - Have you checked `documentation/CORE_README.md` for project principles?
   - If adding a new analysis pattern, have you verified it doesn't exist in `instructions/PATTERNS.md`?

2. **✓ Code Quality Check**
   - Have linting and formatting tools been run on your code?
   - Have all duplicate identifiers been removed?
   - Have you checked for typos and clear naming?
   - Have you used proper TypeScript types/interfaces?

3. **✓ Documentation Update Check**
   - Have you updated relevant documentation to reflect your changes?
   - Have you added any necessary new documentation?
   - Have you cross-referenced documentation with implementation?

4. **✓ Test Coverage Check**
   - Have you added or updated tests for your changes?
   - Have you manually tested the functionality?

### Required Peer Review

**ALL code changes require review by at least one authorized reviewer before merging.**

- No code may be merged without explicit approval
- Reviewers must verify compliance with documentation standards
- Reviewers must check that no duplicate implementations exist
- All comments must be resolved before merging

### Reviewer Responsibilities

Reviewers must verify:

1. **Documentation Compliance**
   - Changes align with existing documentation
   - No duplicate patterns or implementations
   - All relevant documentation updated

2. **Code Quality**
   - No obvious bugs or errors
   - No duplicate code/identifiers
   - Follows project style and conventions

3. **Feature Alignment**
   - Implements what's described in documentation
   - Doesn't recreate existing functionality

### Branch Protection

All main branches are protected:

- Direct pushes to main/master are prohibited
- All changes must go through pull requests
- Required reviews must be approved before merging
- Status checks (tests, linting) must pass

## Setting Up Your Environment

### Pre-commit Hooks

We use pre-commit hooks to automatically check and format code before committing:

```bash
# Install pre-commit
pip install pre-commit

# Install the hooks
pre-commit install
```

### IDE Configuration

#### VS Code

1. Install the following extensions:
   - Python
   - ESLint
   - Prettier
   - EditorConfig

2. Add these settings to your workspace settings.json:

```json
{
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true
  },
  "python.formatting.provider": "black",
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.linting.pylintEnabled": false,
  "[python]": {
    "editor.formatOnSave": true,
    "editor.defaultFormatter": "ms-python.python"
  },
  "[javascript]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "[typescript]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "[typescriptreact]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  }
}
```

## Commit Guidelines

- Use clear, descriptive commit messages
- Reference issue numbers when applicable
- Run tests before committing

## Pull Request Process

1. Branch from `main` with a descriptive branch name
2. Make your changes with appropriate tests
3. Ensure all linting and formatting rules pass
4. Create a pull request with a clear description
5. Address any review comments

## Questions?

If you have questions about the contribution process or code style, please open an issue for discussion.
