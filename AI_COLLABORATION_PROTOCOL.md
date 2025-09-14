# AI Collaboration Protocol

## Overview
This document defines how Claude-1 (Implementation AI) and UltrAI (Oversight AI) work together efficiently.

## Roles

### Claude-1 (Implementation AI)
- **Primary Role**: Execute main implementation tasks
- **Responsibilities**:
  - Implement features and fixes
  - Write and modify code
  - Run tests and verify changes
  - Commit and push changes
  - Request help for specific subtasks

### UltrAI (Oversight AI)
- **Primary Role**: Planning, oversight, and support tasks
- **Responsibilities**:
  - Help develop implementation plans
  - Review proposed changes
  - Handle delegated one-off tasks
  - Research and investigation
  - Monitor progress and provide guidance

## Communication Protocol

### 1. Planning Phase
```markdown
## Implementation Plan: [Task Name]

### Objective
[Clear description of what needs to be done]

### Proposed Approach
1. [Step 1]
2. [Step 2]
3. [Step 3]

### Delegated Tasks
- [ ] Research task for Oversight AI
- [ ] Testing task for Oversight AI

### Risk Assessment
- [Potential issues]
- [Mitigation strategies]
```

### 2. Task Delegation Format
```markdown
## Delegated Task: [Task Name]

**Assigned to**: Oversight AI
**Priority**: High/Medium/Low
**Deadline**: [If applicable]

### Task Description
[What needs to be done]

### Expected Output
[What should be delivered back]

### Context
[Any relevant files or information]
```

### 3. Status Updates
```markdown
## Status Update: [Timestamp]

### Completed
- ✅ [Completed task]

### In Progress
- 🔄 [Current task]

### Blocked
- 🚫 [Blocked item] - [Reason]

### Need Help With
- 🤝 [Task needing assistance]
```

## Task Types for Delegation

### Research Tasks
- Version compatibility checking
- Breaking change analysis
- Best practices research
- Security advisory review

### Testing Tasks
- Run specific test suites
- Test individual components
- Verify fixes in isolation
- Performance benchmarking

### Documentation Tasks
- Update README files
- Write migration guides
- Document configuration changes
- Create troubleshooting guides

### Analysis Tasks
- Review logs for patterns
- Analyze error messages
- Check dependency trees
- Audit code for patterns

## Workflow Example

1. **Claude-1**: "I need to update all dependencies for security fixes"
2. **Oversight AI**: Reviews vulnerabilities, creates prioritized plan
3. **Claude-1**: "Please research breaking changes for package X while I update Y"
4. **Oversight AI**: Researches and reports back
5. **Claude-1**: Implements fixes based on research
6. **Oversight AI**: Reviews changes, suggests improvements
7. **Claude-1**: Finalizes and commits changes

## Best Practices

1. **Clear Communication**
   - Be specific about what you need
   - Provide context and relevant files
   - Set clear expectations for outputs

2. **Efficient Task Division**
   - Delegate research while implementing
   - Parallelize independent tasks
   - Focus on each AI's strengths

3. **Progress Tracking**
   - Regular status updates
   - Clear blocker identification
   - Immediate communication of issues

4. **Quality Assurance**
   - Oversight AI reviews before commits
   - Test results shared between AIs
   - Documentation updated together

## Current Active Tasks

### Main Implementation Tasks
1. [To be assigned]

### Delegated Tasks
1. [To be assigned]

## Communication Channel & Signals

All communication happens in this thread with clear headers. Standard signals:

- `[PLAN]` - Plan-of-Record updates
- `[CLAUDE_DO]` - Assign core implementation to Claude-1
- `[ULTRA_DO]` - Assign one-off/support tasks to UltrAI
- `[STATUS]` - Status updates
- `[COMPLETE]` - Task completion
- `[BLOCKER]` - Blocker notification
- `[REVIEW]` - Code review/verification request

## Push Gates & Guardrails

- Tests must pass locally before any push (document commands and outputs)
- Minimum of 2 healthy models online before enabling features; single-model fallback disabled
- Security checks: dependency audit, secret/regex scan, and basic injection/XSS screening
- Drift prevention: if off track, state “I'm getting off track. Returning to [ORIGINAL_TASK]” and realign

## Review Cadence

- After initial PR, after integration, and pre-deploy: post `[REVIEW]` with links to PRs, test results, and endpoint verifications