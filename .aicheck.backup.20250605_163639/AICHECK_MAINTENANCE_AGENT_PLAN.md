# AICheck Maintenance Agent Plan

## Overview

Design for an autonomous agent that handles proper file placement, AICheck compliance, and git workflow management. This agent ensures all AICheck rules are followed, files are properly organized, and git commits/hooks are properly maintained.

## Agent Responsibilities

### 1. File Organization & Placement
- Monitor action directories for proper structure
- Ensure todo.md files exist in all actions
- Move completed action documentation to appropriate locations
- Maintain supporting_docs organization
- Migrate enduring documentation from process to product directories

### 2. AICheck Compliance
- Verify action plans follow required format
- Check for missing required files (plan.md, todo.md, status.txt)
- Ensure single ActiveAction principle is maintained
- Validate action status transitions
- Monitor dependency documentation

### 3. Git Workflow Management
- Enforce commit message standards (50 char limit, present tense)
- Run pre-commit validation checks
- Verify deployment before allowing completion
- Manage git hooks installation and updates
- Track action references in commits

### 4. Automated Index Management
- Update actions_index.md automatically
- Maintain ACTION_TIMELINE.md chronologically
- Update dependency_index.md
- Generate progress statistics
- Apply visual formatting standards

## Technical Architecture

### Core Components

```yaml
aicheck-maintenance-agent:
  version: "1.0"
  
  monitors:
    - file_system_watcher:
        paths:
          - .aicheck/actions/
          - .aicheck/current_action
          - documentation/
        events:
          - create
          - modify
          - delete
          - move
    
    - git_hook_manager:
        hooks:
          - pre-commit
          - post-commit
          - pre-push
          - prepare-commit-msg
    
    - compliance_validator:
        rules:
          - action_structure
          - documentation_standards
          - status_transitions
          - dependency_tracking
  
  actions:
    - auto_organize_files:
        triggers:
          - new_file_created
          - action_completed
        operations:
          - validate_location
          - move_if_needed
          - update_indexes
    
    - enforce_standards:
        triggers:
          - pre_commit
          - manual_audit
        operations:
          - check_commit_message
          - validate_action_status
          - verify_dependencies
          - check_deployment_status
    
    - update_indexes:
        triggers:
          - action_status_change
          - file_migration
          - dependency_update
        operations:
          - update_actions_index
          - update_timeline
          - regenerate_statistics
          - apply_formatting
```

### Implementation Approach

#### Phase 1: File System Monitor
```python
class AICheckFileMonitor:
    """Monitors AICheck directories for compliance"""
    
    def __init__(self):
        self.action_dir = ".aicheck/actions/"
        self.doc_dir = "documentation/"
        self.rules = self.load_rules()
    
    def validate_action_structure(self, action_name):
        """Ensure action has all required files"""
        required_files = [
            f"{action_name}-plan.md",
            "todo.md",
            "status.txt",
            "supporting_docs/"
        ]
        # Validation logic
    
    def migrate_completed_docs(self, action_name):
        """Move enduring docs to product documentation"""
        # Migration logic with git tracking
```

#### Phase 2: Git Integration
```bash
#!/bin/bash
# aicheck-git-guardian.sh

# Pre-commit validation
validate_commit() {
    # Check commit message format
    # Verify action references
    # Validate file locations
    # Check deployment status if completing
}

# Auto-update indexes
update_indexes() {
    # Update actions_index.md
    # Update ACTION_TIMELINE.md
    # Apply visual formatting
}
```

#### Phase 3: Compliance Engine
```python
class ComplianceEngine:
    """Enforces AICheck rules automatically"""
    
    def validate_action_transition(self, action, old_status, new_status):
        """Ensure valid status transitions"""
        if new_status == "completed":
            return self.verify_completion_requirements(action)
    
    def verify_completion_requirements(self, action):
        """Check all completion criteria"""
        checks = {
            "deployment_verified": self.check_deployment(action),
            "dependencies_documented": self.check_dependencies(action),
            "tests_passing": self.check_tests(action),
            "documentation_complete": self.check_docs(action),
            "no_critical_issues": self.check_issues(action)
        }
        return all(checks.values()), checks
```

### Integration Points

1. **VS Code Extension**
   - Real-time validation in editor
   - Quick fixes for common issues
   - Action status viewer
   - Todo management integration

2. **CLI Commands**
   ```bash
   aicheck-agent status        # Show current compliance status
   aicheck-agent fix          # Auto-fix common issues
   aicheck-agent audit        # Full system audit
   aicheck-agent migrate      # Migrate completed docs
   ```

3. **CI/CD Integration**
   - GitHub Actions workflow
   - Pre-merge validation
   - Automatic index updates
   - Deployment verification

## Benefits

### For Developers
- Automatic file organization
- No manual index updates needed
- Clear validation messages
- Automated compliance fixes

### For Project Management
- Always up-to-date indexes
- Guaranteed rule compliance
- Audit trail maintenance
- Consistent documentation

### For System Integrity
- Prevents false completion claims
- Ensures deployment verification
- Maintains file organization
- Enforces standards automatically

## Implementation Timeline

### Week 1: Core File Monitor
- File system watching
- Basic validation rules
- Manual trigger commands

### Week 2: Git Integration
- Hook management
- Commit validation
- Auto-index updates

### Week 3: Compliance Engine
- Status transition validation
- Deployment verification
- Dependency tracking

### Week 4: UI/UX Polish
- VS Code extension
- Clear error messages
- Quick fix suggestions
- Documentation

## Success Criteria

1. **Zero Manual Index Updates**: All indexes update automatically
2. **100% Rule Compliance**: No violations slip through
3. **Deployment Verification**: No false completion claims
4. **Developer Happiness**: Less manual work, more coding

## Next Steps

1. Prototype file system monitor
2. Test git hook integration
3. Design VS Code extension
4. Create compliance rule engine
5. Build automated test suite

## Notes

This agent should be:
- **Non-intrusive**: Works in background
- **Helpful**: Provides clear guidance
- **Reliable**: Never breaks workflow
- **Smart**: Learns from patterns
- **Fast**: Near-instant validation

The goal is to make AICheck compliance automatic and invisible to developers while ensuring perfect adherence to project standards.