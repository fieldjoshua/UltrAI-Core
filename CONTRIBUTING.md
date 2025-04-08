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
