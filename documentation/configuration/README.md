# Configuration Files

This document provides an overview of the configuration files used in the UltrAI project.

## Language and Linting Configuration

| File | Purpose |
|------|---------|
| `.pylintrc` | Python linting rules for code quality checks |
| `.flake8` | Configuration for the Flake8 Python linter |
| `.bandit` | Security-focused linting for Python |
| `.bandit.yaml` | YAML configuration for Bandit security scanner |
| `.pre-commit-config.yaml` | Pre-commit hooks for automated checks before commits |
| `.editorconfig` | Editor-agnostic coding style settings |
| `.prettierrc` | Configuration for Prettier code formatter (JS/CSS/HTML) |
| `.babelrc` | Babel JavaScript/TypeScript transpiler settings |
| `.cursorrc` | Configuration for Cursor IDE |
| `setup.cfg` | Python package configuration and tool settings |

## Deployment Configuration

| File | Purpose |
|------|---------|
| `Dockerfile` | Instructions for building Docker containers |
| `docker-compose.yml` | Multi-container Docker application orchestration |
| `.dockerignore` | Files to exclude from Docker builds |
| `vercel.json` | Vercel deployment configuration |
| `.vercelignore` | Files to exclude from Vercel deployments |
| `alembic.ini` | Database migration configuration |
| `Makefile` | Build automation and task execution |

## Package Management

| File | Purpose |
|------|---------|
| `package.json` | Node.js dependencies and scripts |
| `package-lock.json` | Exact versions of Node.js dependencies |
| `requirements.txt` | Python dependencies |

## Version Control

| File | Purpose |
|------|---------|
| `.gitignore` | Files to exclude from Git version control |
| `CODEOWNERS` | Specifies owners for different parts of the codebase |

## Notes on Configuration Management

1. **Configuration Updates**
   - When updating configuration files, document changes in commit messages
   - Test configuration changes in development before applying to production

2. **Configuration Precedence**
   - Local configurations take precedence over global configurations
   - Environment-specific configurations override default configurations

3. **Configuration Security**
   - Never commit sensitive information like API keys or passwords
   - Use environment variables or secure storage for sensitive values
