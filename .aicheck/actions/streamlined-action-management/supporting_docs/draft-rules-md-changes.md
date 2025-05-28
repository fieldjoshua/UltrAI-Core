# Draft Changes to RULES.md for Streamlined Action Management

## New Section 4: Enhanced Action Management System

### 4.1 Action Definition and Structure

Each ACTION uses a hybrid approach combining traditional AICheck files with a new companion `action.yaml` file for enhanced automation and verification. This preserves existing workflows while adding deployment verification and automated tracking capabilities.

#### 4.1.1 Required Action Files

Every ACTION maintains the traditional file structure PLUS a new companion file:

**Traditional Files (Required)**:
- `.aicheck/actions/[action-name]/[action-name]-plan.md` - Action plan (human-readable)
- `.aicheck/actions/[action-name]/status.txt` - Current status
- `.aicheck/actions/[action-name]/progress.md` - Progress tracking
- `.aicheck/actions/[action-name]/todo.md` - Task list (managed by Claude's TodoRead/TodoWrite)

**New Companion File (Required for new actions)**:
- `.aicheck/actions/[action-name]/action.yaml` - Machine-readable companion for automation

**Generated Files (Automatic)**:
- Timeline entries → Updated from both traditional files and action.yaml
- Index entries → Generated from all action metadata
- Dependency tracking → Synced between dependency_index.md and action.yaml

#### 4.1.2 Action Lifecycle States

Actions progress through defined states, enforced by tooling:

1. **not_started** - Action created but work not begun
2. **in_progress** - Active development
3. **deployed** - Code deployed to production (if applicable)
4. **verified** - Deployment tested and confirmed working
5. **completed** - All criteria met and verified
6. **blocked** - Work stopped due to dependencies or issues

State transitions are enforced:
- `not_started` → `in_progress` (work begins)
- `in_progress` → `deployed` (code pushed and deployed)
- `deployed` → `verified` (tests pass in production)
- `verified` → `completed` (all criteria met)
- Any state → `blocked` (issues discovered)

### 4.2 Automated Workflow Commands

All ACTION management is performed through the `aicheck` CLI tool:

#### 4.2.1 Action Creation
```bash
aicheck action new [action-name]
```
This command:
- Creates action directory structure
- Generates action.yaml from template
- Updates actions_index.md automatically
- Creates git branch (optional)
- Opens editor for plan details

#### 4.2.2 Task Management
```bash
aicheck task complete [task-id]
```
This command:
- Updates task status in action.yaml
- Records completion timestamp
- Updates progress percentage
- Commits changes with standard message

#### 4.2.3 Deployment Verification
```bash
aicheck deploy verify
```
This command:
- Runs test_command specified in action.yaml
- Records verification results
- Updates deployment status
- Blocks completion if tests fail

#### 4.2.4 Action Completion
```bash
aicheck action complete
```
This command performs ALL verification:
- ✓ All tasks marked complete
- ✓ No unresolved blockers
- ✓ Deployment verified (if required)
- ✓ All success criteria met
- ✓ Dependencies documented
- ✓ Issues resolved or documented

Only after ALL checks pass:
- Updates ACTION_TIMELINE.md
- Moves action to completed/
- Updates all indexes
- Commits with completion message

### 4.3 Issue and Dependency Integration

#### 4.3.1 Issue Tracking
Issues discovered during any ACTION are tracked in action.yaml and automatically synchronized to ISSUE_MATRIX.yaml:

```bash
aicheck issue add [description] --severity=[critical|high|medium|low]
```

#### 4.3.2 Dependency Management
Dependencies are declared in action.yaml and automatically synchronized to DEPENDENCY_INDEX.yaml:

```bash
# External dependencies
aicheck dep add [package] [version] [justification]

# Internal dependencies
aicheck dep link [target-action] [type] [description]
```

### 4.4 Enforcement and Validation

#### 4.4.1 Git Hook Enforcement
Pre-commit hooks validate:
- action.yaml syntax is valid
- Status transitions are legal
- Required fields are present
- Deployment verification for production changes

#### 4.4.2 Completion Requirements
Actions CANNOT be marked completed without:
1. All tasks status = done
2. All blockers resolved
3. Deployment verified = true (if required)
4. All success criteria addressed
5. No open critical issues

### 4.5 Migration from Legacy System

#### 4.5.1 Migration Process
Existing actions using the old multi-document system can be migrated:

```bash
aicheck migrate [action-name]
```

This preserves all information while consolidating into action.yaml format.

#### 4.5.2 Transition Period
- Legacy actions continue to function
- New actions MUST use streamlined system
- Migration deadline: 30 days from implementation
- Automated migration available

### 4.6 Benefits of Streamlined System

1. **Single Source of Truth** - One file contains everything
2. **Automated Updates** - Indexes and timelines update automatically
3. **Enforced Verification** - Cannot claim completion without proof
4. **Integrated Tracking** - Issues and dependencies linked automatically
5. **Reduced Errors** - Automation prevents manual mistakes
6. **Faster Workflow** - Common tasks are one command

## Updates to Other Sections

### Section 3.1 AI Editor Scope

REPLACE the manual todo.md management with:

```
AI editors may implement without approval:
- Code implementing the ActiveAction plan (after PLAN approval)
- Documentation updates for ActiveAction
- Bug fixes and tests within ActiveAction scope
- Refactoring within ActiveAction scope
- Using aicheck CLI commands to update task status
```

### Section 6.1 Standard Action Lifecycle

REPLACE steps 1-12 with:

1. **Creation**: `aicheck action new [name]` creates action.yaml
2. **Planning**: Edit action.yaml plan section
3. **Approval**: Human manager reviews plan in action.yaml
4. **Implementation**: Update task status via `aicheck task complete`
5. **Deployment**: Code deployed and `aicheck deploy verify` run
6. **Completion**: `aicheck action complete` performs all checks
7. **Archival**: Automatically moved to completed/ with indexes updated

### Section 6.1.1 Deployment Verification Requirements

UPDATE to reference:

"Deployment verification is now ENFORCED through the `aicheck deploy verify` command, which must pass before any action can be marked completed. See Section 4.2.3 for details."

## Templates to Include

### 1. action-template.yaml
[See full template in action plan]

### 2. verification-template.py
```python
#!/usr/bin/env python3
"""
Deployment verification script for [action-name]
This script is run by 'aicheck deploy verify'
"""

import sys
import requests
import json

def verify_deployment():
    """
    Verify that [specific functionality] is working in production.
    Returns: True if all tests pass, False otherwise
    """
    results = {
        "timestamp": "2025-05-26T10:00:00Z",
        "tests": [],
        "passed": False
    }
    
    # Test 1: Check endpoint accessibility
    try:
        response = requests.get("https://production.url/health")
        results["tests"].append({
            "name": "health_check",
            "passed": response.status_code == 200,
            "details": f"Status: {response.status_code}"
        })
    except Exception as e:
        results["tests"].append({
            "name": "health_check",
            "passed": False,
            "details": str(e)
        })
    
    # Add more specific tests here
    
    # Determine overall pass/fail
    results["passed"] = all(test["passed"] for test in results["tests"])
    
    # Output results
    print(json.dumps(results, indent=2))
    return 0 if results["passed"] else 1

if __name__ == "__main__":
    sys.exit(verify_deployment())
```

## Transition Timeline

1. **Immediate**: New actions use streamlined system
2. **Week 1**: CLI tools available for testing
3. **Week 2**: Begin migration of active actions
4. **Week 4**: All actions migrated
5. **Week 5**: Legacy system deprecated