# Auto-Surgical Fix Template

Automated surgical fixes with intelligent approval gates and scope enforcement.

## Template

```
AUTO-SURGICAL FIX:

**Target Issue:** [Describe the specific issue]
**Auto-Boundary Detection:** [Will auto-detect from git changes and action scope]

## AUTOMATED EXECUTION:
✅ **Auto-Safe Operations:**
- Read and analyze target code
- Identify minimal required changes
- Implement fix if scope < 3 files and < 50 lines
- Run existing tests automatically
- Auto-verify no side effects
- Auto-log changes to action documentation
- Auto-run ./aicheck context check for boundary compliance

⚠️ **Approval Required If:**
- Changes exceed 3 files or 50 lines
- New dependencies needed
- Test failures detected
- Boundary violations found (./aicheck context check fails)
- Context pollution score > 30 after changes

## AUTO-VERIFICATION:
✅ **Automatic Checks:**
- Original issue resolved
- No new test failures
- No boundary violations detected
- Code style/patterns maintained
- Context pollution within limits

⚠️ **Human Review Triggered If:**
- Verification checks fail
- Unexpected side effects detected
- Complex logic changes required

## COMPLETION:
✅ **Auto-Complete When:**
- All verification checks pass
- Boundary compliance confirmed
- Context health maintained
- Changes logged and documented
```

## Example Usage

```
AUTO-SURGICAL FIX:

**Target Issue:** Login timeout not showing user-friendly error message

**Expected Auto-Execution:**
- Analyze src/auth/login.js handleTimeout function
- Identify error message display logic
- Implement user-friendly message if change < 3 files
- Run auth tests automatically
- Verify no login flow disruption
- Auto-complete if all checks pass

**Approval Triggers:**
- If changes require modifying multiple auth files
- If new error handling patterns needed
- If tests fail or boundary violations detected
```

## Smart Automation Features

- **Intelligent Scope Detection:** Uses git diff and action context
- **Automatic Boundary Enforcement:** Integrates with ./aicheck context check
- **Predictive Approval Gates:** Escalates before problems occur
- **Context-Aware Execution:** Considers current action and pollution score
- **Self-Documenting:** Auto-logs all changes and decisions