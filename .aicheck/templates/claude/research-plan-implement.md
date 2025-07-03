# Research-Plan-Implement Template (Automated)

This template implements the proven 3-phase approach with automated progression and approval gates.

## Template

```
AUTOMATED RESEARCH-PLAN-IMPLEMENT:

**Goal:** [Describe the objective]
**Current Action:** [Will be auto-detected from ./aicheck status]

## AUTO-PHASE 1: Research (Fully Automated)
The following will happen automatically:
- ✅ Read relevant files and analyze current patterns
- ✅ Identify dependencies and constraints  
- ✅ Review existing tests and documentation
- ✅ Generate research summary
- ✅ Auto-log research findings to action documentation

**Research Scope:** [specify files/areas to analyze]

## AUTO-PHASE 2: Planning (Automated with Approval Gate)
Automated planning will:
- ✅ Design approach based on research findings
- ✅ Break down into implementation steps
- ✅ Identify required file changes
- ✅ Generate test strategy
- ⚠️ **APPROVAL REQUIRED:** Plan exceeds complexity threshold
- ⚠️ **APPROVAL REQUIRED:** Changes affect >5 files
- ⚠️ **APPROVAL REQUIRED:** New dependencies required

## AUTO-PHASE 3: Implementation (Automated with Checkpoints)
Automated implementation will:
- ✅ Follow plan step-by-step with auto-verification
- ✅ Run tests automatically after each major step
- ✅ Auto-document changes in action logs
- ✅ Auto-run ./aicheck context check for boundary violations
- ⚠️ **APPROVAL REQUIRED:** Scope creep detected
- ⚠️ **APPROVAL REQUIRED:** Test failures requiring manual intervention
- ⚠️ **APPROVAL REQUIRED:** Boundary violations detected

**Auto-Completion Triggers:**
- All steps completed successfully
- Tests passing
- No boundary violations
- Context pollution score < 30
```

## Example Usage

```
AUTOMATED RESEARCH-PLAN-IMPLEMENT:

**Goal:** Add user role-based permissions to dashboard
**Current Action:** AddRoleBasedPermissions

## AUTO-PHASE 1: Research (Fully Automated)
Please automatically:
- Read src/auth/, src/components/Dashboard.js, src/utils/permissions.js
- Analyze current user/permission patterns
- Review test patterns in tests/
- Generate research summary
- Log findings to .aicheck/actions/add-role-based-permissions/supporting_docs/

## AUTO-PHASE 2: Planning (Auto with Gates)
Auto-generate implementation plan based on research.
Alert if plan requires >5 file changes or new dependencies.

## AUTO-PHASE 3: Implementation (Auto with Checkpoints)  
Execute plan automatically with boundary checking.
Pause for approval if scope creep detected.
```

## Automation Benefits

- Reduces manual oversight while maintaining safety
- Prevents scope creep through automated boundary checking
- Maintains human control over complex/risky decisions
- Auto-logs progress for accountability
- Integrates with AICheck focus management