# ACTION: streamlined-action-management

Version: 1.0
Last Updated: 2025-05-26
Status: Not Started
Progress: 100%

## Purpose

Implement a consolidated, automated action management system to prevent deployment verification failures and reduce documentation overhead. This system will replace multiple documents with a single `action.yaml` file and provide CLI tools for automated workflow management.

## Problem Statement

Current issues with the action system:
1. **Too many documents** - 10+ files to track per action leads to inconsistencies
2. **Manual updates** - Timeline, indexes, and status updates are manual and error-prone
3. **No deployment verification** - Actions marked complete without production verification
4. **Disconnected systems** - Issues, dependencies, and timelines are not integrated
5. **Human error** - Easy to forget steps or misrepresent completion status

## Success Criteria

- [ ] Single `action.yaml` file contains all action information
- [ ] CLI tools automate all common workflows
- [ ] Deployment verification is enforced programmatically
- [ ] All indexes and timelines update automatically
- [ ] Issue tracking integrated with action lifecycle
- [ ] Dependency management automated
- [ ] Git hooks prevent incomplete actions
- [ ] Migration path for existing actions

## Requirements

### Core System Components

1. **action.yaml Schema** - Single source of truth
2. **AICheck CLI Enhancement** - New commands for streamlined workflow
3. **Automated Index Generation** - Timeline, actions index, dependencies
4. **Git Hook Integration** - Enforce verification before completion
5. **Issue Matrix Integration** - Link issues to actions
6. **Deployment Verification** - Automated testing and verification

### Backward Compatibility

- Existing actions continue to work
- Migration tool to convert old format to new
- Gradual transition period supported

## Implementation Approach

### Phase 1: Design and Templates
1. Create `action.yaml` schema and template that coexists with existing files
2. Enhance existing CLI command structure (preserve current functionality)
3. Draft RULES.md updates preserving Claude's todo management
4. Create migration strategy that's non-destructive

### Phase 2: Core Implementation
1. Enhance existing `aicheck` bash script with new commands
2. Add YAML support while keeping existing text file support
3. Build automated generators that update existing indexes
4. Implement deployment verification as new command

### Phase 3: Integration
1. Enhance existing git hooks without breaking current workflow
2. Integrate issue tracking using existing patterns
3. Extend dependency management already in aicheck
4. Create migration tools that preserve all data

### Phase 4: Testing and Rollout
1. Test with new actions while old ones continue working
2. Gradual migration with fallback support
3. Update documentation with both systems documented
4. Preserve Claude's native todo functionality throughout

## Deliverables

### 1. Templates
- `action-template.yaml` - Standard action template
- `verification-template.py` - Deployment verification script template

### 2. CLI Tools
- `aicheck action new [name]` - Create new action
- `aicheck task complete [task-id]` - Mark task complete
- `aicheck deploy verify` - Run deployment verification
- `aicheck action complete` - Complete action with all checks
- `aicheck action migrate [name]` - Migrate old format to new

### 3. Documentation Updates
- RULES.md Section 4.0 - Streamlined Action Management
- Updated workflow diagrams
- CLI command reference
- Migration guide

### 4. Automated Systems
- Index generators (timeline, actions, dependencies)
- Git hooks for enforcement
- Issue tracking integration
- Deployment verification framework

## Technical Details

### action.yaml Schema
```yaml
version: "1.0"
action:
  name: string (required)
  status: enum [not_started, in_progress, deployed, verified, completed, blocked]
  created: date
  completed: date (optional)
  
plan:
  purpose: string
  problem: string
  success_criteria: array of strings
  
tasks:
  - id: string
    desc: string
    status: enum [pending, in_progress, done, blocked]
    completed: date (optional)
    blockers: array of strings (optional)
    
deployment:
  required: boolean
  environments:
    production:
      url: string
      last_deployed: date
      verified: boolean
      test_command: string
      verification_results: object (optional)
      
dependencies:
  external:
    - name: string
      version: string
      justification: string
  internal:
    - action: string
      type: enum [prerequisite, blocks, related]
      description: string
      
issues:
  - id: string
    desc: string
    severity: enum [low, medium, high, critical]
    status: enum [open, in_progress, resolved]
    discovered: date
    resolved: date (optional)
    
notes:
  string (optional, for additional context)
```

### CLI Command Structure
```bash
# Action lifecycle
aicheck action new [name]                  # Create new action
aicheck action list                        # List all actions
aicheck action status [name]               # Show action status
aicheck action complete [name]             # Complete action with checks
aicheck action block [name] [reason]       # Mark action as blocked
aicheck action archive [name]              # Archive completed action

# Task management
aicheck task add [action] [desc]           # Add task to action
aicheck task list [action]                 # List tasks for action
aicheck task complete [action] [task-id]   # Mark task complete
aicheck task block [action] [task-id]      # Mark task blocked

# Deployment
aicheck deploy verify [action]             # Run deployment verification
aicheck deploy status [action]             # Show deployment status

# Dependencies
aicheck dep add [action] [name] [version]  # Add external dependency
aicheck dep link [from] [to] [type]        # Link internal dependency

# Issues
aicheck issue add [action] [desc]          # Add issue to action
aicheck issue resolve [action] [issue-id]  # Resolve issue

# Migration
aicheck migrate [action]                   # Migrate old format to new
aicheck migrate all                        # Migrate all actions
```

## Risk Mitigation

1. **Migration Risks**
   - Provide both manual and automated migration
   - Keep backup of original files
   - Gradual rollout with pilot actions

2. **Tool Adoption**
   - Comprehensive documentation
   - Video tutorials
   - Phased introduction

3. **Technical Risks**
   - Extensive testing before rollout
   - Rollback procedures
   - Version control for action.yaml files

## Dependencies

- Python 3.8+ for CLI tools
- PyYAML for YAML parsing
- Click for CLI framework
- GitPython for git integration
- Existing AICheck infrastructure

## Estimated Timeline

- Phase 1: 2 days (Design and Templates)
- Phase 2: 3 days (Core Implementation)
- Phase 3: 2 days (Integration)
- Phase 4: 2 days (Testing and Rollout)
- Total: 9 days

## Notes

This action addresses the root cause of the orchestration-integration-fix failure where local completion was confused with production deployment. By consolidating documents and automating verification, we make it structurally difficult to misrepresent completion status.