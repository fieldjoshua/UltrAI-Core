# Session Tracking Template

## Current Session

| Session ID | Start Time | Status | Progress |
|------------|------------|--------|----------|
| [SESSION_ID] | [START_TIME] | [STATUS] | [PROGRESS] |

## Session History

| Session ID | Start Time | End Time | Status | Progress | Notes |
|------------|------------|----------|--------|----------|-------|
| [SESSION_ID] | [START_TIME] | [END_TIME] | [STATUS] | [PROGRESS] | [NOTES] |

## Session Rules

1. Each session must be associated with exactly one action
2. Only one action can be in WORKING state at any time
3. Session status must match the action's current phase
4. Session progress must be updated when action progress changes
5. Session history is maintained for audit purposes

## Integration with Action Plans

- Each action's PLAN.md contains a reference to its current session
- Session tracking is updated automatically when action status changes
- Session history is used to track action transitions
- Session progress is synchronized with action progress

## Last Updated: [DATE]
