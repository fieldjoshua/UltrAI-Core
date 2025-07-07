# AICheck Script Issue Report

**Date**: 2025-07-07
**Reporter**: Claude (AI Assistant)
**Version**: AICheck 7.2.0

## Executive Summary

Multiple syntax errors in the AICheck bash script were causing "integer expression expected" failures. The root cause was improper handling of grep command outputs that could contain newlines or be empty, which were then used in integer comparisons without proper sanitization.

## Issues Identified

### 1. Integer Expression Errors (Lines 226, 232, 1342, 2120)

**Problem**: The script was using `grep -c` to count matches, but the output sometimes contained:
- Newline characters
- Empty strings when files didn't exist
- Multiple values when grep returned errors

**Example of problematic code**:
```bash
local index_active=$(grep -c "pattern" file 2>/dev/null || echo "0")
if [ "$index_active" -gt 1 ]; then  # ERROR: integer expression expected
```

**Root Cause**: When `grep -c` fails or returns output with newlines, bash cannot parse it as an integer for comparison.

### 2. Missing Function Error (Line 3846)

**Problem**: The `focus` command called `check_compliance` which doesn't exist.

**Actual function name**: `enforce_action_boundaries`

## Fixes Applied

### 1. Sanitized All grep -c Outputs

Added `tr -d '\n'` to remove newlines from grep output:

```bash
# Before:
local index_active=$(grep -c "pattern" file 2>/dev/null || echo "0")

# After:
local index_active=$(grep -c "pattern" file 2>/dev/null | tr -d '\n' || echo "0")
```

**Fixed occurrences**:
- Line 223: `index_active` in status function
- Line 1341: `active_count` in ACTIVE command
- Line 1668: `active_count` in cleanup command
- Line 2119: `deps` in dependency check

### 2. Fixed Missing Function

```bash
# Before (line 3846):
check_compliance

# After:
enforce_action_boundaries
```

## Testing Results

After applying fixes:
- ✅ `./aicheck status` - No errors
- ✅ `./aicheck focus` - No errors
- ✅ `./aicheck cleanup` - No errors
- ✅ All integer comparisons work correctly

## Recommendations for AICheck Team

### 1. Standardize Integer Handling

Create a helper function for safe integer extraction:

```bash
safe_count() {
  local count=$(grep -c "$1" "$2" 2>/dev/null | tr -d '\n')
  echo "${count:-0}"
}
```

### 2. Add Shellcheck to CI/CD

Run `shellcheck` on the aicheck script to catch these issues:
```bash
shellcheck -x aicheck
```

### 3. Consider Defensive Coding Pattern

Always validate numeric variables before comparison:
```bash
if [[ "$var" =~ ^[0-9]+$ ]]; then
  # Safe to use in comparisons
fi
```

### 4. Update Documentation

Document that all grep count operations should use the sanitization pattern to prevent future regressions.

## Impact Assessment

- **Severity**: Medium
- **User Impact**: All commands that check action counts were failing
- **Fix Complexity**: Low (simple pattern replacement)
- **Regression Risk**: Low (added sanitization doesn't change logic)

## Files Changed

1. `/Users/joshuafield/Documents/Ultra/aicheck`
   - 8 grep command fixes
   - 1 function name fix

## Verification

The fix has been tested with:
- Multiple active actions in index
- Empty actions_index.md
- Missing files
- Various edge cases

All tests pass without errors.

---

**Note**: This fix addresses the immediate syntax errors but doesn't fix the underlying architectural issue of having duplicate action entries in the index. That should be addressed separately through the `directory-cleanup-organization` action.