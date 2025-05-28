# Enhanced AICheck Quick Reference

## Essential Commands

### Action Management
```bash
aicheck action new <name>          # Create new action (with YAML)
aicheck action set <name>          # Set current action
aicheck action complete [name]     # Complete (with verification)
aicheck action list                # List all actions
aicheck status                     # Enhanced status display
```

### Deployment Verification (NEW)
```bash
aicheck verify deployment          # Verify current action deployment
aicheck verify deployment <name>   # Verify specific action
```

### Issue Tracking (NEW)
```bash
aicheck issue report "<desc>" <severity>   # Report issue
aicheck issue update <id> <status>         # Update issue
aicheck issue list                         # List issues
```

### Dependencies
```bash
aicheck dependency add <pkg> <ver> "<reason>"              # External
aicheck dependency internal <from> <to> <type> "<desc>"   # Internal
aicheck dependency check                                   # Check conflicts
```

### Sync & Migration (NEW)
```bash
aicheck sync                       # Sync current action
aicheck sync --all                 # Sync all actions
./migration-tools.sh migrate <name>       # Migrate single action
./migration-tools.sh migrate-all          # Migrate all actions
```

## Key Features

### 🚫 Deployment Verification
- Blocks completion without verification
- Configure in action.yaml:
```yaml
deployment:
  required: true
  environments:
    production:
      url: https://app.com
      test_command: "curl -f https://app.com/health"
```

### 🐛 Issue Management
- Critical issues block completion
- Severities: critical, high, medium, low
- Statuses: open, in_progress, resolved, closed

### 📝 Todo Integration
- Continue using TodoRead/TodoWrite
- Managed in todo.md (not YAML)
- YAML just references todo.md

### 🔄 Bi-directional Sync
- Traditional files ↔️ YAML
- Automatic with git hooks
- Manual with `aicheck sync`

## Important Changes

1. **Completion Requires Verification**
   - If `deployment.required: true`, must verify first
   - Run `aicheck verify deployment` before completing

2. **Critical Issues Block**
   - Can't complete with open critical issues
   - Resolve with `aicheck issue update <id> resolved`

3. **Enhanced Status**
   - Shows deployment status
   - Lists open issues
   - Displays dependencies

## Git Integration

With hooks installed:
- Commits logged to action.yaml
- Pre-push verifies deployment
- Status validated on commit

## Common Workflows

### Start New Action
```bash
aicheck action new my-feature
aicheck action set my-feature
# Work on implementation...
```

### Before Completing
```bash
# Check for issues
aicheck issue list

# Verify deployment (if required)
aicheck verify deployment

# Then complete
aicheck action complete
```

### Fix Sync Issues
```bash
# If YAML out of sync
aicheck sync

# Force sync all
aicheck sync --all --force
```

## File Locations

- Enhanced script: `aicheck-enhanced.sh`
- Git hooks: `git-hooks.sh`
- Migration: `migration-tools.sh`
- Tests: `test-*.sh`
- This guide: `QUICK_REFERENCE.md`