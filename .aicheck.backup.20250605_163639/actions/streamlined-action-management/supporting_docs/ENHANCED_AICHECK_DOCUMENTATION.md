# Enhanced AICheck Documentation

## Overview

The Enhanced AICheck system introduces a hybrid approach that combines the simplicity of traditional text files with the power of structured YAML data. This enhancement was created to address the critical issue of actions being marked complete without proper deployment verification.

## Key Features

### 1. Hybrid Action Management

Each action now has both traditional files AND an `action.yaml` companion file that provides:
- Structured data for better tooling
- Deployment verification tracking
- Issue management integration
- Enhanced dependency tracking
- Git integration for better traceability

### 2. Deployment Verification Framework

**Problem Solved**: Actions were being marked complete without verifying actual deployment to production.

**Solution**: 
- Actions can now require deployment verification before completion
- Automated testing of deployment endpoints
- Blocked completion until verification passes

### 3. Backward Compatibility

All existing AICheck commands continue to work exactly as before. The enhancement layer adds new capabilities without breaking existing workflows.

## Installation

### For New Projects

1. Copy the enhanced aicheck script:
```bash
cp supporting_docs/aicheck-enhanced.sh /usr/local/bin/aicheck
chmod +x /usr/local/bin/aicheck
```

2. Install git hooks (optional but recommended):
```bash
./supporting_docs/git-hooks.sh install
```

### For Existing Projects

1. Install the enhanced script as above

2. Migrate existing actions (optional):
```bash
./supporting_docs/migration-tools.sh migrate-all
```

## Enhanced Commands

### Core Commands (Unchanged)

- `aicheck action new <name>` - Create new action
- `aicheck action set <name>` - Set current action
- `aicheck action complete [name]` - Complete action (now with verification)
- `aicheck action list` - List all actions (now shows YAML data)
- `aicheck status` - Show current status (enhanced output)

### New Commands

#### Deployment Verification
```bash
# Verify deployment for current action
aicheck verify deployment

# Verify specific action
aicheck verify deployment <action-name>
```

#### Issue Management
```bash
# Report an issue
aicheck issue report "<description>" <severity>
# Severity: critical, high, medium, low

# Update issue status
aicheck issue update <issue-id> <status>
# Status: open, in_progress, resolved, closed

# List issues for current action
aicheck issue list
```

#### Sync Commands
```bash
# Sync YAML with traditional files
aicheck sync [action-name]

# Sync all actions
aicheck sync --all
```

## Action YAML Structure

Each action now has an `action.yaml` file with this structure:

```yaml
name: action-name
status: pending|in_progress|completed
created: 2025-05-26 10:00:00
updated: 2025-05-26 11:00:00

description: |
  Multi-line description of the action

phases:
  - name: "Phase 1: Planning"
    status: completed
    tasks:
      - "Design solution"
      - "Create documentation"
  
  - name: "Phase 2: Implementation"
    status: in_progress
    tasks:
      - "Write code"
      - "Test implementation"

dependencies:
  external:
    - name: pytest
      version: "7.0.0"
      justification: "Testing framework"
  
  internal:
    - action: prerequisite-action
      type: data
      description: "Provides configuration"

issues:
  - id: ISS-001
    description: "Test failures on CI"
    severity: high
    status: open
    created: 2025-05-26 10:30:00

deployment:
  required: true
  environments:
    production:
      url: https://example.com
      verified: false
      test_command: "python verify_deployment.py"
      last_check: null

testing:
  unit_tests:
    status: pending
    coverage: 0
  integration_tests:
    status: pending

documentation:
  readme: true
  api_docs: false
  user_guide: false

git:
  branch: feature/action-name
  commits:
    - hash: abc123
      message: "Initial implementation"
      timestamp: 2025-05-26 10:15:00
  pull_request: null

todos:
  source: "todo.md"
  note: "Managed via Claude's TodoRead/TodoWrite"
```

## Deployment Verification

### Configuring Deployment Verification

1. Set `deployment.required: true` in action.yaml
2. Define environments with test commands:

```yaml
deployment:
  required: true
  environments:
    production:
      url: https://your-app.com
      test_command: "curl -f https://your-app.com/health"
    staging:
      url: https://staging.your-app.com
      test_command: "python scripts/verify_staging.py"
```

### Verification Process

1. Run `aicheck verify deployment`
2. System executes test commands for each environment
3. Updates `verified` status in YAML
4. Blocks completion if verification fails

## Issue Management

### Critical Issues Block Completion

Issues with severity "critical" will prevent action completion:

```bash
# This will block completion
aicheck issue report "Production API returns 500 errors" critical

# Must resolve before completing
aicheck issue update ISS-001 resolved
```

### Issue Workflow

1. Report issues during development
2. Track status changes
3. Resolve critical issues before completion
4. Non-critical issues are warnings only

## Git Integration

### Automatic Tracking

With git hooks installed:
- Commits are automatically logged to action.yaml
- Pre-push hook verifies deployment if required
- Action status is validated before commits

### Manual Git Commands

```bash
# Link action to PR
aicheck git link-pr <pr-number>

# Update branch info
aicheck git update-branch
```

## Migration Guide

### Migrating Single Action

```bash
./supporting_docs/migration-tools.sh migrate <action-name>
```

### Migrating All Actions

```bash
./supporting_docs/migration-tools.sh migrate-all
```

### Validation

```bash
# Validate migration success
./supporting_docs/migration-tools.sh validate <action-name>
```

### Rollback

```bash
# Remove action.yaml (preserves traditional files)
./supporting_docs/migration-tools.sh rollback <action-name>
```

## Best Practices

### 1. Deployment Verification

Always configure deployment verification for production-related actions:
- Set clear test commands
- Use health check endpoints
- Verify actual functionality, not just connectivity

### 2. Issue Tracking

- Report issues as you discover them
- Use appropriate severity levels
- Resolve critical issues before marking complete

### 3. Dependencies

- Document all external dependencies with versions
- Track internal dependencies between actions
- Check for conflicts before adding new dependencies

### 4. Todo Management

Continue using Claude's TodoRead/TodoWrite for task management. The YAML file references todo.md but doesn't duplicate its content.

## Troubleshooting

### YAML Parsing Without yq

The system works without yq installed, using bash/sed/awk for parsing. For better performance, install yq:

```bash
# macOS
brew install yq

# Linux
snap install yq
```

### Sync Issues

If traditional files and YAML get out of sync:

```bash
# Force sync from traditional files to YAML
aicheck sync <action-name> --force
```

### Git Hook Problems

If git hooks interfere with your workflow:

```bash
# Temporarily disable
git commit --no-verify

# Uninstall hooks
./supporting_docs/git-hooks.sh uninstall
```

## Testing

Run the test suites to verify functionality:

```bash
# Test enhanced commands
./supporting_docs/test-enhanced-commands.sh

# Test migration tools
./supporting_docs/test-migration.sh
```

## Summary

The Enhanced AICheck system provides powerful new capabilities while maintaining full backward compatibility. It specifically addresses the deployment verification gap that led to false completion claims, ensuring that actions marked as complete have actually been deployed and verified in production.