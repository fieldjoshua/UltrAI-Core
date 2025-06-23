# Auto-Iterate Session Template

This template is automatically added to the active action's directory when auto-iterate mode is initiated. No new action needs to be created - auto-iterate integrates with your existing active action.

## Integration Workflow

1. **Have Active Action**: Ensure you have an active action: `./aicheck status`
2. **Begin Auto-Iterate**: `./aicheck auto-iterate` (this template auto-added to action directory)
3. **Follow Goal-Driven Process**: Goals → Approval → Execution → Git Approval

---

# ACTION: [ACTION-NAME]

**Type:** Auto-Iterate Session  
**Priority:** [High/Medium/Low]  
**Estimated Duration:** [Hours/Days]  
**Created:** [DATE]  
**Status:** ActiveAction

## Problem Statement

### Current Issue
<!-- Describe the specific problem that needs iterative solving -->
- What is broken or not working?
- What tests are failing?
- What is the desired end state?

### Root Cause Analysis
<!-- Initial hypothesis about why this needs iterative fixing -->
- Suspected causes:
- Areas of uncertainty:
- Dependencies that might be involved:

## Auto-Iterate Goals

### Primary Goals
<!-- These will be refined during ./aicheck auto-iterate goal definition -->

**GOAL 1:** [Specific, measurable objective]
- **Success Criteria:** [How to verify this goal is complete]
- **Approach:** [High-level strategy to achieve this goal]
- **Risk Assessment:** [What could go wrong]

**GOAL 2:** [Another specific objective]  
- **Success Criteria:** [How to verify this goal is complete]
- **Approach:** [High-level strategy to achieve this goal]
- **Risk Assessment:** [What could go wrong]

### Constraints and Boundaries
- **Max Iterations:** [Number] (default: 15)
- **Time Limit:** [Seconds] (default: 600s)
- **Scope Boundaries:** [What should NOT be changed]
- **Safety Limits:** [Rollback procedures]

## Test Strategy

### Initial Test State
<!-- Run tests before starting auto-iterate -->
```bash
# Document current test results
[Test command and current output]
```

### Success Metrics
- [ ] All tests pass (exit code 0)
- [ ] No regressions introduced
- [ ] Specific functionality verified: [describe]
- [ ] Performance acceptable: [criteria]

### Rollback Plan
If auto-iterate fails or causes regressions:
1. [Specific rollback steps]
2. [How to revert changes]
3. [How to restore working state]

## AI Editor Instructions

### Goal Refinement Process
1. **Analyze** current test failures and error patterns
2. **Propose** specific, measurable goals in `.aicheck/auto-iterate-goals.md`
3. **Wait** for human approval before proceeding
4. **Execute** approved iteration cycles
5. **Report** progress and request commit approval

### Focus Areas
<!-- Guide the AI editor's attention -->
- Files most likely to need changes: [list]
- Areas to avoid changing: [list]
- Testing patterns to follow: [describe]
- Code style requirements: [reference]

### Human Checkpoints
- [ ] Goal definition approval required
- [ ] Manual intervention allowed every [N] iterations
- [ ] Final commit approval required
- [ ] Summary and review required

## Documentation Requirements

### Session Tracking
All auto-iterate sessions must create:
- `.aicheck/auto-iterate-goals.md` (goals and approval)
- `.aicheck/auto-iterate-session-[ID].log` (detailed log)
- `.aicheck/auto-iterate-changes-[ID].md` (change summary)
- `.aicheck/auto-iterate-summary-[ID].md` (final report)

### Action Integration
- [ ] Document session results in `supporting_docs/auto-iterate/`
- [ ] Update action progress after each session
- [ ] Include session summaries in action completion report

## Success Criteria

### Technical Requirements
- [ ] All primary goals achieved
- [ ] Test suite passes completely
- [ ] No regressions in existing functionality
- [ ] Code quality maintained or improved
- [ ] Documentation updated appropriately

### Process Requirements
- [ ] Human approval obtained for goals
- [ ] Proper git commit workflow followed
- [ ] Session results documented
- [ ] Rollback procedures tested if needed

## Post-Iteration Tasks

### Immediate (After Each Session)
- [ ] Review auto-iterate summary
- [ ] Approve or reject git commits
- [ ] Update action progress
- [ ] Document lessons learned

### Action Completion
- [ ] Migrate successful sessions to `supporting_docs/`
- [ ] Update project documentation if needed
- [ ] Create final action report including all auto-iterate sessions
- [ ] Archive session logs and summaries

## Notes and Observations

### Session History
<!-- Track multiple auto-iterate sessions -->

**Session 1:** [Date]
- Duration: [time]
- Goals: [brief description]
- Result: [success/partial/failed]
- Commits: [git hashes if applicable]

**Session 2:** [Date]  
- Duration: [time]
- Goals: [brief description] 
- Result: [success/partial/failed]
- Commits: [git hashes if applicable]

### Learnings
<!-- Capture insights for future auto-iterate sessions -->
- What worked well:
- What didn't work:
- Improvements for next time:
- AI editor effectiveness:

---

## Auto-Iterate Workflow Reference

```bash
# Step 1: Goal Definition
./aicheck auto-iterate

# Step 2: Review and approve goals
./aicheck auto-iterate --approve

# Step 3: Execute iteration
./aicheck auto-iterate --execute [max_iterations] [timeout]

# Step 4: Manual summary if needed
./aicheck auto-iterate --summary
```

## Integration with AICheck Rules

This action follows AICheck RULES.md requirements:
- ✅ Documentation-first approach (this plan)
- ✅ Test-driven development (auto-iterate tests first)
- ✅ Human approval gates (goals and commits)
- ✅ Comprehensive logging and tracking
- ✅ Deployment verification (where applicable)
- ✅ Action isolation and scope management