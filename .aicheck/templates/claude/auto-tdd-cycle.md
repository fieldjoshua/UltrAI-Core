# Auto-TDD Cycle Template

Automated Test-Driven Development with intelligent approval gates and focus management.

## Template

```
AUTO-TDD CYCLE:

**Feature:** [Describe the feature to implement]
**Auto-Context:** [Will use ./aicheck status and current action]

## AUTOMATED RED-GREEN-REFACTOR:

### 🔴 AUTO-RED PHASE (Automated with Gates)
✅ **Auto-Safe Operations:**
- Analyze existing test patterns in project
- Generate failing tests based on requirements
- Run tests to confirm they fail appropriately
- Auto-log test creation to action documentation

⚠️ **Approval Required If:**
- No existing test patterns found (need to establish testing approach)
- Tests require new testing frameworks/dependencies
- Test complexity score > 30 (very complex test logic needed)

### 🟢 AUTO-GREEN PHASE (Automated with Boundaries)
✅ **Auto-Safe Operations:**
- Implement minimal code to make tests pass
- Auto-verify test success
- Auto-run ./aicheck context check for scope compliance
- Keep implementation focused and minimal

⚠️ **Approval Required If:**
- Implementation exceeds test scope significantly
- Boundary violations detected (scope creep)
- Implementation requires >5 files or >100 lines
- New dependencies needed for implementation

### 🔵 AUTO-REFACTOR PHASE (Automated with Safety)
✅ **Auto-Safe Operations:**
- Improve code structure while maintaining test success
- Auto-verify all tests still pass
- Auto-check for code quality improvements
- Auto-document refactoring decisions

⚠️ **Approval Required If:**
- Refactoring changes public interfaces
- Performance implications detected
- Major architectural changes suggested

## AUTO-COMPLETION:
✅ **Completes Automatically When:**
- All tests pass
- Code quality metrics met
- No boundary violations
- Context pollution score < 25
- Feature fully implemented per requirements
```

## Example Usage

```
AUTO-TDD CYCLE:

**Feature:** Add user profile image upload functionality
**Auto-Context:** Current action "AddUserProfileImages"

### Expected Auto-Execution:
1. **RED:** Auto-generate tests for image upload, validation, storage
2. **GREEN:** Auto-implement minimal upload functionality to pass tests  
3. **REFACTOR:** Auto-improve code structure while maintaining test success

### Approval Gates:
- If image processing libraries needed (new dependencies)
- If file storage strategy affects multiple components
- If security considerations require manual review
```

## Intelligent Automation Features

- **Pattern Recognition:** Learns from existing test patterns
- **Scope Awareness:** Uses action boundaries to guide implementation
- **Context Integration:** Leverages ./aicheck focus management
- **Quality Gates:** Automatic code quality and performance checks
- **Progressive Complexity:** Starts simple, escalates for complex scenarios
- **Self-Documenting:** Auto-logs TDD decisions and trade-offs