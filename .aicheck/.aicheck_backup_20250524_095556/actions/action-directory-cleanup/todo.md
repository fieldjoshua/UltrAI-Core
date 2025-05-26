# TODO: ActionDirectoryCleanup

*This file tracks task progress for the ActionDirectoryCleanup action. Tasks are managed using Claude Code's native todo functions and should align with the action plan phases and success criteria.*

## Active Tasks

*Tasks currently in progress or pending. Use status indicators: pending, in_progress, completed*

### Phase 1: Action Audit and Classification

- [ ] **Review recent git history for MVP-relevant commits** (priority: high, status: pending)
  - Identify commits related to MVP completion (May 2025)
  - Note which actions were involved in MVP development
  - Create timeline of MVP development phases

- [ ] **Audit all 90+ action directories** (priority: high, status: pending)
  - Check each action for plan.md and progress indicators
  - Verify completion status claims against deliverables
  - Note last modification dates and relevance

- [ ] **Create action classification spreadsheet** (priority: high, status: pending)
  - Categories: Completed, Active, MVP-Critical, Legacy, Duplicate
  - Include action name, status, last update, MVP relevance
  - Document decision rationale for each classification

### Phase 2: Archive Legacy Actions

- [ ] **Create ARCHIVE/legacy-actions directory structure** (priority: medium, status: pending)
  - Set up organized archive folders by category
  - Create README.md template for archive documentation

- [ ] **Move pre-MVP and abandoned actions** (priority: medium, status: pending)
  - Preserve git history during moves
  - Document reason for archival in each case
  - Maintain reference index of archived actions

### Phase 3: Consolidate and Update

- [ ] **Update actions_index.md with accurate state** (priority: high, status: pending)
  - Remove archived actions from active lists
  - Update status of completed actions
  - Add any missing current actions

- [ ] **Create MVP action priorities document** (priority: high, status: pending)
  - List critical actions for MVP maintenance
  - Define priority order for remaining work
  - Include rationale for prioritization

### Phase 4: Documentation and Verification

- [ ] **Create action organization guidelines** (priority: medium, status: pending)
  - Document criteria for action creation
  - Define archival policies
  - Establish maintenance procedures

- [ ] **Test AICheck system with new structure** (priority: medium, status: pending)
  - Verify all commands work with cleaned structure
  - Test action switching and status updates
  - Confirm archive doesn't interfere with system

## Completed Tasks

*Tasks that have been finished successfully*

- [x] **Create ActionDirectoryCleanup action** (completed: 2025-05-22)
  - Created action plan with clear phases and deliverables
  - Established success criteria for cleanup effort

## Notes

*Additional context, dependencies, or important information for task management*

- Action plan reference: `action-directory-cleanup-plan.md`
- Dependencies: Git history analysis, AICheck system functionality
- Progress tracking: Will update as phases complete
- Special considerations: Must preserve historical context while cleaning
- Key MVP milestones to identify:
  - Production deployment (May 2025)
  - Backend API completion
  - Frontend integration
  - Testing and validation phases

## Task Management Guidelines

- Focus on identifying truly active vs. abandoned work
- Preserve any actions that contributed to MVP success
- Archive with care to maintain historical record
- Test each major change to ensure system stability