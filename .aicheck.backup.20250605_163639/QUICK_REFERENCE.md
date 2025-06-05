# AICheck Quick Reference

## Essential Commands

```bash
aicheck create-action <name>           # Create new action (with validation)
aicheck status                         # Show comprehensive system status  
aicheck set-action <name>              # Set active action
aicheck update-status <name> <status>  # Update action status
aicheck update-progress <name> <0-100> # Update action progress
aicheck complete-action <name>         # Mark action complete
aicheck list                           # List all actions
aicheck validate                       # Validate AICheck system
aicheck test                          # Run system tests
aicheck security-check               # Check security
```

## Action Lifecycle

```
Create → Plan → Approve → Test → Implement → Document → Complete
```

## Status Indicators

- 🟡 **ActiveAction** - Currently working
- 🔴 **Not Started** - Planned
- 🟢 **Completed** - Done
- ⏸️ **Blocked** - Waiting
- ❌ **Cancelled** - Terminated

## Directory Structure

```
.aicheck/
├── actions/[name]/          # Your action
│   ├── PLAN.md             # Required plan
│   ├── todo.md             # Task tracking
│   └── supporting_docs/    # Your docs
├── current_action          # Active action
├── actions_index.md        # Dashboard
└── RULES.md               # Full rules
```

## Key Rules

1. **One ActiveAction** per editor
2. **Document first**, code second
3. **Test before** implementing
4. **Get approval** for plans
5. **Complete or cancel** - no abandonment

## AI Editor Boundaries

### ✅ Can Do Without Approval
- Implement approved plan
- Write tests
- Update docs
- Fix bugs in scope
- Manage todo.md

### ❌ Needs Approval
- Change active action
- Create new action
- Modify plans
- Add new APIs
- Change schemas

## Commit Format

```
<verb> <what> [<action-name>]
```

Example: `Add user auth [auth-system]`

## Testing Locations

- **Product tests**: `/tests/`
- **Process tests**: `supporting_docs/process-tests/`

## Documentation Types

- **Process docs**: Action-specific, temporary
- **Product docs**: `/documentation/`, permanent

## Common Workflows

### Start New Feature
```bash
aicheck create-action my-feature
# Edit .aicheck/actions/my-feature/PLAN.md
# Get approval
aicheck set-action my-feature
# Work...
```

### Complete Action
```bash
# Verify deployment
# Update docs
aicheck complete-action my-feature
# Update actions_index.md
# Move to completed/
```

## Help

- Full rules: `.aicheck/RULES.md`
- Dashboard: `.aicheck/actions_index.md`
- Timeline: `.aicheck/ACTION_TIMELINE.md`