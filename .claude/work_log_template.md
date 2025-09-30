# Work Log Template

## Task: [TASK NAME]
**Started:** [TIMESTAMP]
**Status:** [in_progress | completed | blocked]

---

## What I'm About To Do
**Plain English Summary:**
[Write in 1-2 sentences what I'm going to do]

**Verification Method:**
[How you can verify this worked]

**Expected Outcome:**
[What you should see if this succeeds]

---

## Step-by-Step Execution

### Step 1: [ACTION NAME]
**Command/Action:** 
```
[Exact command or file being modified]
```

**Why:** [Brief explanation]

**Output:**
```
[Paste actual output here - NOT summarized]
```

**My Interpretation:** [What I think this means]
**Verification Question:** [What should you check to confirm I'm right?]

---

### Step 2: [ACTION NAME]
[Repeat structure]

---

## Claims I'm Making

| Claim | Evidence | How You Can Verify |
|-------|----------|-------------------|
| "Tests pass" | `pytest output shows PASSED` | Run: `pytest [path] -v` and check output yourself |
| "Bug fixed" | `Error X no longer appears` | Check: `[specific file:line]` |
| "Performance improved" | `Metric changed from X to Y` | Run: `[command]` and compare |

---

## What Could Go Wrong

**Risk 1:** [Potential issue]
- **How to detect:** [What to look for]
- **How to rollback:** [Exact commands]

**Risk 2:** [Another potential issue]
- **How to detect:** [What to look for]
- **How to rollback:** [Exact commands]

---

## Final Verification Checklist

Before marking this task complete, you should verify:
- [ ] [Specific check #1 with command]
- [ ] [Specific check #2 with command]
- [ ] [Specific check #3 with command]

**If any check fails, the task is NOT complete.**

---

## Actual Results

**What Actually Happened:**
[Paste real output, real numbers, real evidence]

**Discrepancies from Expected:**
[Any differences between what I said would happen and what actually happened]

**My Confidence Level:**
- [ ] 100% - I verified every claim personally
- [ ] 90% - I verified most claims, some inferred
- [ ] 80% - I verified key claims, others assumed
- [ ] <80% - I should not be claiming completion

---

## Questions for You

1. [Specific question about what you want me to verify]
2. [Specific question about acceptable tradeoffs]
3. [Specific question about next steps]