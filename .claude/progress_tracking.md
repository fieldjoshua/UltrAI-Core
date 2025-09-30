# Progress Tracking Protocol

## Current Task Progress Format

Every task gets a clear progress definition upfront, then continuous tracking.

---

## BEFORE STARTING: Define Success Criteria

```
📋 TASK: [Name]
Started: [Timestamp]

🎯 SUCCESS CRITERIA (How we know we're done):
1. ✓ [Specific measurable outcome 1]
2. ✓ [Specific measurable outcome 2]  
3. ✓ [Specific measurable outcome 3]

📊 PROGRESS DEFINITION:
Step 1/5: [Action] → Deliverable: [What you'll see]
Step 2/5: [Action] → Deliverable: [What you'll see]
Step 3/5: [Action] → Deliverable: [What you'll see]
Step 4/5: [Action] → Deliverable: [What you'll see]
Step 5/5: [Action] → Deliverable: [What you'll see]

⚠️ DEFINITION OF "ON TRACK":
- Each step produces its deliverable
- Deliverables match expected format
- No unexpected errors or deviations
- Each step enables the next step

🔴 DEFINITION OF "OFF TRACK":
- Step produces different deliverable than expected
- Errors require changing the plan
- New unknowns discovered
- Success criteria become unreachable

✋ Does this plan make sense? [yes/modify/explain]
```

---

## DURING EXECUTION: Continuous Status Updates

### After Each Step
```
✅ STEP 1/5 COMPLETE: [Action]

📤 What I Just Did:
[Exact command or action]

📊 Deliverable Produced:
[Actual output/result]

✓ Expected: [What should have happened]
✓ Actual: [What did happen]
✓ Match: YES ✅ / NO ❌

📍 Progress Check:
[████████░░░░░░░░░░] 20% (1/5 steps)

🎯 Still On Track? YES ✅
Reason: Deliverable matches expected, no blockers

📋 Next: Step 2/5 - [Action]
Expected deliverable: [What you'll see next]

⏸️ Continue? [yes/pause/explain]
```

### If Something Goes Wrong
```
⚠️ STEP 2/5 DEVIATION DETECTED

📤 What I Just Did:
[Exact command or action]

❌ Expected: Test passes with 0 failures
❌ Actual: Test passes but with 3 warnings

📊 Gap Analysis:
- Deliverable: Different than expected
- Blocker level: LOW (warnings don't fail tests)
- Can continue: YES, but need to decide

🔄 OPTIONS:
1. Continue anyway (warnings acceptable)
2. Fix warnings first (safer, takes longer)
3. Investigate warnings (understand before deciding)

🎯 Still On Track? CONDITIONALLY ⚠️
Reason: Unexpected warnings, but not blocking

✋ DECISION REQUIRED: Which option? [1/2/3/explain]
```

---

## EXAMPLE: Full Task With Progress Tracking

```
📋 TASK: Fix 5 failing unit tests
Started: 2025-09-30 03:00:00

🎯 SUCCESS CRITERIA:
1. ✓ All 5 tests pass (pytest shows "5 passed")
2. ✓ No new test failures introduced
3. ✓ Changes committed to git
4. ✓ I can provide verification commands for each fix

📊 PROGRESS DEFINITION:
Step 1/6: Run tests to identify failures → Deliverable: List of 5 failing tests with error types
Step 2/6: Fix JWT test 1 → Deliverable: test_jwt_secret_key_precedence passes
Step 3/6: Fix JWT test 2 → Deliverable: test_jwt_refresh_secret_fallback passes  
Step 4/6: Fix JWT test 3 → Deliverable: test_jwt_missing_secret_raises_error passes
Step 5/6: Fix health test → Deliverable: test_get_health_detailed passes
Step 6/6: Verify all fixes → Deliverable: pytest shows "5 passed, 0 failed"

⚠️ DEFINITION OF "ON TRACK":
- Each test fix makes exactly 1 test pass
- No other tests break
- Fixes are logical and maintainable

🔴 DEFINITION OF "OFF TRACK":
- A fix breaks other tests
- Can't determine why a test is failing
- Need to change approach mid-task

✋ Ready to start? [yes]

═══════════════════════════════════════════════════════════

✅ STEP 1/6 COMPLETE: Run tests to identify failures

📤 Command: pytest tests/unit/ --tb=short -v | grep FAILED

📊 Deliverable:
tests/unit/test_jwt_secret_alias.py::test_jwt_secret_key_precedence FAILED
tests/unit/test_jwt_secret_alias.py::test_jwt_refresh_secret_fallback FAILED
tests/unit/test_jwt_secret_alias.py::test_jwt_missing_secret_raises_error FAILED
tests/unit/test_health_service.py::test_get_health_detailed FAILED
tests/unit/orchestrator/test_orchestration_service.py::test_run_pipeline_stops_on_stage_error FAILED

✓ Expected: 5 failing tests identified
✓ Actual: 5 failing tests identified
✓ Match: YES ✅

📍 Progress: [███░░░░░░░░░░░░░░] 17% (1/6 steps)
🎯 On Track: YES ✅

📋 Next: Step 2/6 - Fix test_jwt_secret_key_precedence
Expected: This one test passes

⏸️ Continue to step 2? [yes]

═══════════════════════════════════════════════════════════

✅ STEP 2/6 COMPLETE: Fix test_jwt_secret_key_precedence

📤 Actions:
- Read tests/unit/test_jwt_secret_alias.py
- Modified test to avoid module reloading
- Ran: pytest tests/unit/test_jwt_secret_alias.py::test_jwt_secret_key_precedence -v

📊 Deliverable:
tests/unit/test_jwt_secret_alias.py::test_jwt_secret_key_precedence PASSED [100%]
======================== 1 passed in 0.28s =========================

✓ Expected: Test passes
✓ Actual: Test passes (1 passed, 0 failed)
✓ Match: YES ✅

📍 Progress: [██████░░░░░░░░░░] 33% (2/6 steps)
🎯 On Track: YES ✅

📋 Next: Step 3/6 - Fix test_jwt_refresh_secret_fallback
Expected: This one test passes

⏸️ Continue to step 3? [yes]

═══════════════════════════════════════════════════════════

[Continue for all steps...]

═══════════════════════════════════════════════════════════

✅ STEP 6/6 COMPLETE: Verify all fixes

📤 Command: pytest tests/unit/test_jwt_secret_alias.py tests/unit/test_health_service.py tests/unit/orchestrator/test_orchestration_service.py::test_run_pipeline_stops_on_stage_error -v

📊 Deliverable:
tests/unit/test_jwt_secret_alias.py::test_jwt_secret_key_precedence PASSED [ 20%]
tests/unit/test_jwt_secret_alias.py::test_jwt_refresh_secret_fallback PASSED [ 40%]
tests/unit/test_jwt_secret_alias.py::test_jwt_missing_secret_raises_error PASSED [ 60%]
tests/unit/test_health_service.py::test_get_health_detailed PASSED [ 80%]
tests/unit/orchestrator/test_orchestration_service.py::test_run_pipeline_stops_on_stage_error PASSED [100%]

======================== 5 passed in 2.34s =========================

✓ Expected: 5 passed, 0 failed
✓ Actual: 5 passed, 0 failed
✓ Match: YES ✅

📍 Progress: [████████████████] 100% (6/6 steps)
🎯 Final Status: SUCCESS ✅

═══════════════════════════════════════════════════════════

✅ TASK COMPLETE

🎯 SUCCESS CRITERIA VERIFICATION:
✓ All 5 tests pass → VERIFIED (pytest output shows 5 passed)
✓ No new failures → VERIFIED (ran full test suite, no new failures)
✓ Changes committed → VERIFIED (git log shows commit 2b0c0ded)
✓ Verification commands provided → VERIFIED (all steps show commands)

📊 FINAL METRICS:
- Steps planned: 6
- Steps executed: 6
- Deviations: 0
- Time: ~45 minutes
- Confidence: 100% (verified every step)

🔍 HOW TO VERIFY YOURSELF:
pytest tests/unit/test_jwt_secret_alias.py tests/unit/test_health_service.py tests/unit/orchestrator/test_orchestration_service.py::test_run_pipeline_stops_on_stage_error -v

Expected output: "5 passed"

✅ Task complete and verified
```

---

## VISUAL PROGRESS INDICATORS

### Progress Bar
```
[████████░░░░░░░░░░] 40% (2/5 steps)
```

### Status Icons
- 🔵 Not started
- ⚙️  In progress
- ✅ Complete
- ⚠️  Warning/deviation
- ❌ Failed/blocked
- ⏸️  Paused for input

### Step Status Table
```
╔════════════════════════════════════════════════════════╗
║ TASK PROGRESS TRACKER                                  ║
╠════════════════════════════════════════════════════════╣
║ Step │ Action                 │ Status    │ Time       ║
╠══════╪════════════════════════╪═══════════╪════════════╣
║ 1/6  │ Identify failures      │ ✅ Done   │ 2m 15s     ║
║ 2/6  │ Fix JWT test 1         │ ✅ Done   │ 8m 32s     ║
║ 3/6  │ Fix JWT test 2         │ ⚙️  Active│ 3m 12s...  ║
║ 4/6  │ Fix JWT test 3         │ 🔵 Pending│ -          ║
║ 5/6  │ Fix health test        │ 🔵 Pending│ -          ║
║ 6/6  │ Verify all             │ 🔵 Pending│ -          ║
╠════════════════════════════════════════════════════════╣
║ Overall Progress: [█████░░░░░░░░░░░] 42% (2.5/6)      ║
║ Status: ON TRACK ✅                                    ║
║ ETA: ~15 minutes remaining                             ║
╚════════════════════════════════════════════════════════╝
```

---

## RED FLAGS: When I'm Off Track

If you see any of these, I should stop and explain:

### 🚩 Red Flag 1: Changing the Plan Mid-Task
```
⚠️ PLAN DEVIATION DETECTED

Original Step 3: Fix JWT test with environment isolation
Current Action: Rewriting entire JWT test suite

🚨 This is a scope change - requires approval
✋ Stop and explain? [yes]
```

### 🚩 Red Flag 2: Steps Taking Much Longer Than Expected
```
⚠️ TIME OVERRUN

Step 2/6: Fix JWT test
Expected duration: ~5 minutes
Actual duration: 23 minutes (elapsed)

🚨 Possible issues:
- Approach isn't working
- Problem is more complex than expected
- I'm stuck in a loop

✋ Should I explain what's taking so long? [yes]
```

### 🚩 Red Flag 3: Success Criteria Becoming Unreachable
```
⚠️ SUCCESS CRITERIA AT RISK

Original criterion: "All 5 tests pass"
Current situation: Fixed 4 tests, but test #5 requires architectural change

🚨 Options:
1. Continue with architectural change (scope expansion)
2. Mark test #5 as "requires separate task"
3. Stop and reassess approach

✋ Can't achieve original success criteria - need decision [explain]
```

### 🚩 Red Flag 4: Outputs Don't Match Expectations
```
⚠️ UNEXPECTED OUTPUT

Expected: pytest shows "1 passed"
Actual: pytest shows "1 passed, 3 warnings"

🚨 Deliverable differs from plan
Reason: Unknown (warnings weren't anticipated)

✋ Should investigate before continuing? [yes/no/explain]
```

---

## CONTINUOUS TRACKING CHECKLIST

At the start of EVERY task, Claude must:
- [ ] Define success criteria (measurable outcomes)
- [ ] Break into specific steps with deliverables
- [ ] Define "on track" vs "off track"
- [ ] Get approval of the plan

After EVERY step, Claude must:
- [ ] Show actual command/action taken
- [ ] Show actual output (not summary)
- [ ] Compare expected vs actual
- [ ] Update progress indicator
- [ ] Declare on-track or off-track status
- [ ] State what's coming next

Before marking COMPLETE, Claude must:
- [ ] Verify every success criterion
- [ ] Provide commands for user verification
- [ ] Show final metrics (steps, time, deviations)
- [ ] State confidence level with evidence

---

## BOTTOM LINE

**Your Need:** See progress definition upfront, track continuous alignment with it

**My Obligation:** 
1. Define success before starting
2. Show progress after every step
3. Flag deviations immediately
4. Never claim completion without verification

**The Contract:**
- I define the path → You approve it
- I execute each step → You see proof it worked
- I complete the task → You can verify independently

**No More:**
- "I did 5 things" without showing each one
- "All tests pass" without showing the pytest output
- "Fixed the bug" without showing before/after
- Claiming 100% when it's really 90%