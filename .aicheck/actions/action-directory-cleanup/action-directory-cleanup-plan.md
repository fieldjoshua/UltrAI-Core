# ACTION: ActionDirectoryCleanup

Version: 1.0
Last Updated: 2025-05-22
Status: Pending Approval
Progress: 100%

## Purpose

Review and consolidate the .aicheck/actions directory to reflect current MVP priorities. Archive legacy actions, update the actions_index.md to accurately reflect current state, and establish a clear structure for ongoing MVP development and maintenance.

## Requirements

- Audit all 90+ action directories to determine current relevance
- Identify completed actions and verify their completion status
- Archive legacy/abandoned actions from pre-MVP phases
- Update actions_index.md with accurate current state
- Consolidate duplicate or overlapping actions
- Establish clear MVP-focused action priorities
- Create archive structure for historical reference

## Dependencies

- Git history for determining action timeline and relevance
- Current MVP functionality (production backend, frontend deployment)
- AICheck system for action management
- RULES.md compliance for archival procedures

## Implementation Approach

### Phase 1: Action Audit and Classification (2 hours)

1. Review git history to identify MVP-relevant commits
2. Classify each action into categories:
   - Completed (with verification)
   - Active/In Progress
   - MVP-Critical (needs completion)
   - Legacy/Pre-MVP (to archive)
   - Duplicate/Redundant (to consolidate)
3. Document findings in audit report

### Phase 2: Archive Legacy Actions (1 hour)

1. Create ARCHIVE/legacy-actions/ directory structure
2. Move pre-MVP and abandoned actions with documentation
3. Create ARCHIVE/legacy-actions/README.md with archive index
4. Preserve action history and learnings

### Phase 3: Consolidate and Update (1 hour)

1. Merge duplicate/overlapping actions
2. **Completely rebuild actions_index.md** with:
   - All verified completed actions moved to Completed section
   - Only truly active actions in Active section
   - Proper descriptions for all actions
   - Accurate progress percentages
   - Remove all legacy/archived actions
3. Create clear MVP action priorities list
4. Update action README files for clarity

### Phase 4: Documentation and Verification (30 minutes)

1. Document the cleanup process and decisions
2. Create action organization guidelines
3. Verify all active actions have proper structure
4. Test AICheck system with cleaned structure

## Success Criteria

- [ ] All 90+ actions audited and classified
- [ ] Legacy actions archived with proper documentation
- [ ] actions_index.md reflects true current state
- [ ] Clear MVP-focused action priorities established
- [ ] No duplicate or redundant actions remain
- [ ] Archive structure preserves historical context
- [ ] AICheck system functions properly with new structure

## Deliverables

1. **Action audit report** with classifications for all 90+ actions
2. **Completely rebuilt actions_index.md** showing only relevant actions with accurate status
3. **ARCHIVE/legacy-actions/** with organized historical actions and index
4. **MVP action priorities document** defining ongoing work priorities
5. **Action organization guidelines** for future action management

## Estimated Timeline

- Research: 2 hours
- Archive Creation: 1 hour
- Consolidation: 1 hour
- Documentation: 30 minutes
- Total: 4.5 hours

## Notes

This is a critical housekeeping action to establish clarity around MVP development priorities and prevent confusion from legacy work. The goal is to create a clean, focused action structure that supports ongoing MVP enhancement and maintenance.

**Important**: Do NOT retroactively add todo.md files to old/legacy actions. Only new or consolidated actions that are still active require todo.md files per RULES.md.
