# Auto-Iterate Mode - Complete Guide

**Version:** 6.0.0  
**Last Updated:** 2025-06-23

Auto-iterate mode revolutionizes AI-assisted development by introducing goal-driven test-fix-test cycles with human oversight at every critical decision point.

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Workflow](#workflow)
4. [Command Reference](#command-reference)
5. [File Structure](#file-structure)
6. [Best Practices](#best-practices)
7. [Troubleshooting](#troubleshooting)
8. [Advanced Usage](#advanced-usage)

## Overview

### What is Auto-Iterate Mode?

Auto-iterate mode enables AI editors to work systematically toward specific, measurable goals through automated test-fix-test cycles. Unlike traditional development where AI might work without clear objectives, auto-iterate forces goal definition and human approval at key stages.

### Key Principles

1. **Goal-Driven**: Every session must have specific, measurable objectives
2. **Human Control**: No iteration or commits happen without explicit approval
3. **Action Integration**: Seamlessly works within your existing AICheck Actions
4. **Complete Traceability**: Comprehensive logging and documentation of all changes
5. **Safety First**: Rollback options available at every stage

### When to Use Auto-Iterate

✅ **Good Use Cases:**
- Complex test failures requiring multiple fixes
- Systematic debugging of interconnected issues  
- Refactoring with comprehensive test validation
- Dependencies updates with conflict resolution
- Performance optimization with measurement cycles

❌ **Not Suitable For:**
- Simple, single-step fixes
- Exploratory coding without clear objectives
- Initial prototyping or experimentation
- Documentation-only changes

## Prerequisites

### System Requirements

1. **Active AICheck Action**: Must have an active action (check with `./aicheck status`)
2. **Test Suite**: Project must have automated tests (Python: pytest/Poetry, Node.js: npm test)
3. **Git Repository**: Changes will be tracked and committed through git
4. **AICheck v6.0.0+**: Latest version with auto-iterate support

### Setup Verification

```bash
# Check AICheck version
./aicheck version

# Verify active action
./aicheck status

# Test your test suite
npm test  # or poetry run pytest
```

## Workflow

### Phase 1: Goal Definition

```bash
./aicheck auto-iterate
```

**What Happens:**
1. Analyzes current test failures and error patterns
2. Creates template in active action directory: `auto-iterate-session-plan.md`
3. Generates goals template: `.aicheck/auto-iterate-goals.md`
4. Displays instructions for AI editor to fill out specific goals

**AI Editor Requirements:**
- Must propose specific, measurable objectives
- Include success criteria for each goal
- Assess risks and approaches
- No vague or open-ended goals allowed

**Example Output:**
```
🎯 Auto-Iterate Goal Definition
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔍 Analyzing current test state...
Current Test State:
  Failed tests: 3
  Key issues:
    • test_login.py::test_user_auth FAILED - AssertionError
    • test_api.py::test_endpoint FAILED - ImportError: requests
    • test_utils.py::test_parse FAILED - SyntaxError

📝 Goals template created: .aicheck/auto-iterate-goals.md
📝 Auto-iterate template added: .aicheck/actions/fix-auth/auto-iterate-session-plan.md

NEXT STEPS:
1. AI Editor: Edit the goals file with specific, measurable objectives
2. Human: Review and approve goals before proceeding  
3. Run: ./aicheck auto-iterate --execute to begin approved iteration
```

### Phase 2: Human Approval

```bash
./aicheck auto-iterate --approve
```

**What Happens:**
1. Displays proposed goals for review
2. Offers options: approve, edit, or cancel
3. Must receive explicit human approval to proceed
4. Can iterate on goal refinement

**Human Options:**
- **y/yes**: Approve goals and proceed
- **e/edit**: Open goals file for editing  
- **n/no**: Cancel session

**Sample Goals for Review:**
```markdown
# Auto-Iterate Session Goals

## Proposed Goals

### GOAL 1: Fix Authentication Test Failures
- **Success Criteria:** test_login.py::test_user_auth passes
- **Approach:** Fix assertion logic and verify user model
- **Risk Assessment:** Low risk, isolated to auth module

### GOAL 2: Resolve Import Dependencies  
- **Success Criteria:** All ImportError issues resolved
- **Approach:** Update requirements.txt and verify imports
- **Risk Assessment:** Medium risk, could affect other modules
```

### Phase 3: Goal-Driven Execution

```bash
./aicheck auto-iterate --execute [max_iterations] [timeout]
```

**What Happens:**
1. Runs iteration cycles toward approved goals
2. Tests → Analyzes → Fixes → Repeats
3. Human checkpoints every iteration
4. Tracks all changes and progress

**Iteration Cycle:**
```
Iteration 1/10 (0s elapsed)
🧪 Running tests...
❌ Tests still failing
🔍 Analyzing failures against goals...
Failed tests: 3
Key errors:
  • ImportError: No module named 'requests'
  • AssertionError: Expected True, got False

Options for iteration 1:
  c - Continue to next iteration
  i - Intervene manually (pause iteration)  
  q - Quit iteration session
  s - Summary and finish

Action (auto-continuing in 10s): 
```

**Human Intervention Options:**
- **c/continue**: Proceed to next iteration
- **i/intervene**: Pause for manual changes
- **q/quit**: Stop session entirely
- **s/summary**: Skip to final summary

### Phase 4: Git Approval

**Automatic at Session End**

**What Happens:**
1. Comprehensive session summary generated
2. All changes documented and reviewed
3. Human approval required for git commits
4. Multiple commit options available

**Git Approval Options:**
- **y/yes**: Commit with auto-generated message
- **c/custom**: Commit with custom message
- **r/review**: Review diff before committing
- **n/no**: Don't commit (keep changes)
- **d/discard**: Discard all changes (DANGEROUS!)

## Command Reference

### Basic Commands

```bash
# Goal definition (start here)
./aicheck auto-iterate

# Human approval of goals  
./aicheck auto-iterate --approve

# Execute approved iteration
./aicheck auto-iterate --execute

# Manual summary generation
./aicheck auto-iterate --summary

# Help and usage
./aicheck auto-iterate --help
```

### Execution Options

```bash
# Default execution (15 iterations, 600s timeout)
./aicheck auto-iterate --execute

# Custom iterations
./aicheck auto-iterate --execute 5

# Custom iterations and timeout  
./aicheck auto-iterate --execute 10 300

# Resume from pause
./aicheck auto-iterate --execute 15 600
```

### Configuration File

Create `.aicheck/auto-iterate.conf` to customize defaults:

```bash
# Default maximum iterations
default_max_iterations=20

# Default timeout in seconds
default_timeout=900

# Auto-continue between iterations
default_auto_continue=true

# Additional delay between iterations
iteration_delay=5
```

## File Structure

### Generated Files

When auto-iterate runs, it creates several files:

```
.aicheck/actions/[action-name]/
├── auto-iterate-session-plan.md     # Template (auto-created)
└── supporting_docs/
    └── auto-iterate/                 # Session summaries (migrated)

.aicheck/
├── auto-iterate-goals.md             # Goals and approval
├── auto-iterate-session-[ID].log     # Detailed session log
├── auto-iterate-changes-[ID].md      # Change tracking
├── auto-iterate-summary-[ID].md      # Final comprehensive summary
└── auto-iterate.conf                 # Configuration (optional)
```

### File Descriptions

**Goals File** (`.aicheck/auto-iterate-goals.md`):
- Contains AI editor's proposed goals
- Includes success criteria and risk assessment
- Used for human approval process

**Session Log** (`.aicheck/auto-iterate-session-[ID].log`):
- Detailed log of every iteration
- Test outputs and error analysis
- Timestamps and progression tracking

**Changes File** (`.aicheck/auto-iterate-changes-[ID].md`):
- Tracks git changes per iteration
- Documents files modified
- Links changes to specific goals

**Summary File** (`.aicheck/auto-iterate-summary-[ID].md`):
- Comprehensive session overview
- Goal achievement analysis
- Recommendations for future work

## Best Practices

### For AI Editors

1. **Write Specific Goals**
   ```markdown
   ❌ Bad: "Fix the tests"
   ✅ Good: "Fix test_user_auth AssertionError by correcting user.is_authenticated logic"
   ```

2. **Include Success Criteria**
   ```markdown
   ✅ "Success Criteria: test_login.py passes with exit code 0, no regressions in other tests"
   ```

3. **Assess Risks Honestly**
   ```markdown
   ✅ "Risk Assessment: Medium risk - changes to auth module could affect login flow"
   ```

4. **Stay Within Action Scope**
   - Only work on issues related to the active action
   - Don't expand scope without human approval
   - Focus on approved goals only

### For Human Reviewers

1. **Review Goals Carefully**
   - Ensure goals are specific and measurable
   - Verify they align with action objectives  
   - Check that risks are properly assessed

2. **Monitor Progress**
   - Use intervention option (`i`) when needed
   - Don't let sessions run too long without oversight
   - Review summaries thoroughly

3. **Git Commit Strategy**
   - Use custom messages for important changes
   - Review diffs for complex modifications
   - Don't hesitate to discard if unsatisfied

### Project Setup

1. **Reliable Test Suite**
   - Ensure tests are deterministic
   - Fix flaky tests before auto-iterate sessions
   - Have good test coverage

2. **Clear Action Context**
   - Always have an active action before starting
   - Ensure action plan is up-to-date
   - Define action scope clearly

## Troubleshooting

### Common Issues

**"No test configuration found"**
```bash
# Ensure you have either:
ls package.json     # For Node.js projects
ls pyproject.toml   # For Python projects with Poetry
```

**"No goals file found"**
```bash
# Run goal definition first:
./aicheck auto-iterate
```

**Session hangs during test execution**
```bash
# Check if tests run independently:
npm test            # or poetry run pytest
# If they hang, fix tests before using auto-iterate
```

**Template not created in action directory**
```bash
# Verify you have an active action:
./aicheck status
# If no active action, create one:
./aicheck new YourActionName
./aicheck ACTIVE YourActionName
```

### Recovery Procedures

**Session interrupted unexpectedly:**
```bash
# Generate summary from most recent session:
./aicheck auto-iterate --summary
```

**Need to discard all changes:**
```bash
# During git approval, choose 'd' and type 'discard'
# Or manually:
git reset --hard HEAD
git clean -fd
```

**Resume paused session:**
```bash
# Make manual changes, then:
./aicheck auto-iterate --execute
```

## Advanced Usage

### Multiple Sessions per Action

You can run multiple auto-iterate sessions within the same action:

```bash
# Session 1: Fix import errors
./aicheck auto-iterate  # Define goals for imports
./aicheck auto-iterate --approve
./aicheck auto-iterate --execute

# Session 2: Fix logic errors  
./aicheck auto-iterate  # Define goals for logic
./aicheck auto-iterate --approve
./aicheck auto-iterate --execute
```

Each session will be tracked separately with unique IDs.

### Integration with AICheck Workflows

Auto-iterate integrates with all AICheck features:

```bash
# Check scope before starting
./aicheck focus

# Run auto-iterate session
./aicheck auto-iterate
./aicheck auto-iterate --approve  
./aicheck auto-iterate --execute

# Verify deployment readiness
./aicheck deploy

# Complete action
./aicheck complete
```

### Custom Templates

You can customize the auto-iterate template by editing:
`templates/claude/auto-iterate-action.md`

Changes will apply to new sessions.

### Batch Processing

For complex actions with multiple problem areas:

```bash
# Break into focused sessions
Session 1: Database connection issues
Session 2: API endpoint errors
Session 3: Frontend integration
Session 4: Performance optimization
```

Each session should have focused, achievable goals.

## Integration with AICheck Rules

Auto-iterate mode follows all AICheck RULES.md requirements:

- ✅ **Documentation-first**: Template automatically created
- ✅ **Test-driven**: Tests must exist and guide iteration
- ✅ **Human approval**: Required for goals and commits
- ✅ **Action isolation**: Works within active action scope
- ✅ **Comprehensive logging**: All sessions fully documented
- ✅ **Deployment verification**: Can trigger `./aicheck deploy`

## Version History

- **v6.0.0**: Initial auto-iterate mode implementation with comprehensive system timeout handling
- **v5.1.0**: Enhanced MCP integration foundation
- **v5.0.0**: Core AICheck system with action management

---

**Need Help?**
- Run `./aicheck auto-iterate --help` for quick reference
- Check `./aicheck stuck` for general AICheck guidance  
- Review session logs in `.aicheck/auto-iterate-session-*.log`
- Examine summaries in `.aicheck/auto-iterate-summary-*.md`