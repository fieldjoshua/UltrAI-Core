# AICheck Rules

This document is the controlling reference for all work managed by the AICheck system in this PROJECT. These rules cannot be modified without approval from Joshua Field

> **Quick Navigation**: [Core Principles](#1-core-principles) | [Glossary](#2-glossary-and-key-concepts) | [Action Management](#3-action-management) | [Todo Management](#4-todo-management-integration) | [Project Structure](#5-project-structure-and-organization) | [Workflow](#6-workflow-and-processes) | [Standards](#7-style-and-documentation-standards) | [Testing](#8-testing-framework) | [Documentation](#9-documentation-organization)

## 1. Core Principles

### 1.1 Defining the Work

The PROJECT creates a PROGRAM with specific functions benefiting humanity, built through interrelated ACTIONS performed by EDITORS. Each ACTION is a sub-objective contributing to program functionality.

An EDITOR's work has value when it progresses an ACTION toward completion. Efficient, quality work increases an EDITOR's value. EDITORS who understand both their current ACTION and its relationship to the PROGRAM will deliver greater value than those with a narrower perspective.

### 1.2 Documentation First

PROJECT objective must be clear to all editors. All ACTIONS require their own directory with a documented PLAN before implementation. PLANs require human approval and must detail the ACTION's value to the PROGRAM.

PLANs contain all implementation details including testing plans. ACTIONS must be TEST-Driven: tests must be created and approved (via the PLAN.md) before implementation and passed for completion of the ACTION.

Changes to ActiveAction must be reflected in the ACTIONS INDEX and relevant docs. Supporting documentation maintained in the ACTION's supporting_docs directory.

Documentation categories:
- Process Documentation: Temporary documents during ACTION lifecycle → .aicheck/actions/[action-name]/supporting_docs/
- Product Documentation: Enduring documents with relevance beyond ACTION → /documentation/[CATEGORY]/
- Process Testing: Tests relevant only during ACTION lifecycle → .aicheck/actions/[action-name]/supporting_docs/process-tests/
- Product Testing: Tests with enduring relevance → /tests/[CATEGORY]/

When an ACTION is completed, documentation with enduring value must be migrated to the appropriate /documentation/ subdirectory.

### 1.3 Development Guidelines

Each team member may work on one ActiveAction at a time; complete or pause before switching. The PROJECT may have multiple concurrent ActiveActions assigned to different team members.

!!! YOU MAY NOT MISREPRESENT YOU HAVE COMPLETED ELEMENTS OF A PLAN WHEN YOU HAVE NOT. FOLLOWING APPROVED PLANS IS VITAL TO THIS SYSTEM!!!

Follow AICheck directory structure and naming conventions. Update action status and document progress regularly. Follow language-specific best practices. Implement graceful degradation for optional dependencies.

Use Docker-based development when available, with documented alternatives when not available. Document all environment variables and configuration options. Implementation procedures should reside within the Action's Plan.

### 1.4 Claude Code Integration

Claude Code functions as an AI engineer within the AICheck workflow, complementing human editors while respecting our documentation-first approach and action-based governance requirements.

#### Capabilities
- Generate implementation code from PLAN specifications
- Create comprehensive test suites following test-driven methodology
- Provide code review and optimization suggestions
- Enhance/generate documentation based on implementation details
- Assist with migrations and refactoring
- Support debugging complex issues

#### Integration Requirements
- Start with TEST-Driven approach (generate tests before implementation)
- Reference specific sections of RULES.md in prompts
- Include relevant directory paths and documentation links
- Provide contextual examples of existing patterns
- Verify outputs against action requirements
- Document all Claude interactions in ACTION's supporting_docs
- Use standardized prompt templates stored in .aicheck/templates/claude/

#### Vision Guardian Integration (Optional)

**On-Demand Auditing**: Project Vision Guardian consultation is available via:
- **Custom command**: `.aicheck/guardian audit [files/actions]` - Manual audit trigger
- **Git pre-push hook**: Automatic audit before code is pushed to repository
- **Explicit request**: When stakeholders request IP protection review

**Audit Triggers**:
- Major architectural changes to core systems
- Patent-protected feature modifications
- Competitive advantage implementations
- Upon explicit request for IP protection review

**Guardian Modes**:
- **ADVISORY** (default): Provides recommendations and warnings
- **REVIEW**: Requires explicit approval for flagged changes
- **VETO**: Blocks problematic changes (emergency use only)

Vision Guardian integration protects intellectual property without impeding daily development workflow.

## 2. Glossary and Key Concepts

### Core Terms
- **PROJECT**: The overall software development initiative
- **PROGRAM**: The software product being built
- **ACTION**: Discrete unit of work with clear objectives and completion criteria
- **EDITOR**: Any contributor (human or AI) working on actions
- **PLAN**: Documented specification for an ACTION
- **ActiveAction**: ACTION currently being worked on
- **Process Documentation**: Temporary, action-specific documentation
- **Product Documentation**: Documentation with enduring relevance
- **Test-Driven Development (TDD)**: Tests written before implementation
- **Documentation-First**: Documentation before code
- **Action Lifecycle**: Creation → Planning → Implementation → Testing → Completion

## 3. Action Management

### 3.1 AI Editor Scope

AI editors may implement without approval:
- Code implementing the ActiveAction plan (after PLAN approval)
- Documentation updates for ActiveAction
- Bug fixes and tests within ActiveAction scope
- Refactoring within ActiveAction scope
- Managing todo.md files within ActiveAction scope (creating, updating task status, marking complete)

The following ALWAYS require human manager approval:
- Changing the ActiveAction
- Creating a new Action
- Making substantive changes to any Action
- Modifying any Action Plan
- Creating or modifying Templates

#### 3.1.1 Approval Boundaries

**No Approval Needed**: Implementation per plan, tests, refactoring, documentation updates, bug fixes within scope

**Approval Required**: New APIs, schema changes, auth modifications, new dependencies, plan changes

### 3.2 Documentation Requirements

- Action plan (PLAN.md)
- Supporting documentation
- Status updates (Not Started, ActiveAction, Completed, Blocked, On Hold, Cancelled)

#### 3.2.1 Managing Dependencies

Document in PLAN.md under `## Dependencies` section. Track blockers in action status. Coordinate with dependent action owners.

### 3.3 Claude Code Documentation

All Claude Code interactions MUST:
- Be stored in .aicheck/actions/[action-name]/supporting_docs/claude-interactions/
- Reference specific sections of the ACTION's PLAN
- Include the complete prompts used to generate code or solutions
- Document any modifications made to Claude-generated content
- Include verification steps performed on Claude-generated outputs
- Note iterations or refinements to prompts

#### 3.3.1 Claude Documentation

Store interactions in `supporting_docs/claude-interactions/` with date, purpose, prompt, response, and any modifications.

#### 3.3.2 Claude Code Context Generation

Claude Code has built-in procedures for generating chat context and session continuity. When working with Claude:
- Claude automatically maintains context across sessions
- Claude can generate session summaries for continuity
- This functionality is inherent to Claude Code and does not require AICheck automation
- Document any specific context requirements in action supporting_docs

### 3.4 Action Consolidation and Conflict Resolution

Actions may require consolidation when they overlap in scope, duplicate functionality, or create conflicting approaches.

#### Identifying Action Conflicts

Actions may conflict when they:
- Address identical or overlapping objectives
- Duplicate functionality or scope  
- Create contradictory implementation approaches
- Compete for same resources or dependencies
- Would result in inconsistent system architecture

#### Consolidation Process

1. **Conflict Detection**: Review actions_index.md for overlapping scope and objectives
2. **Impact Analysis**: Assess which action has greater value, progress, or strategic importance
3. **Merge Strategy**: Combine valuable elements from conflicting actions into single action
4. **Cancellation**: Cancel duplicate, superseded, or lower-priority actions
5. **Documentation**: Update plans to reflect consolidated scope and approach
6. **Cross-Reference Updates**: Update any dependencies or references in other actions

#### Resolution Authority

- Joshua Field approves all action consolidations and cancellations
- Document consolidation reasoning in supporting_docs/consolidation-notes.md
- Update actions_index.md to reflect organizational changes
- Preserve cancelled action documentation in /actions/completed/ for historical reference

#### Post-Consolidation Requirements

- Update todo.md files to reflect merged scope
- Reconcile conflicting timelines and milestones
- Merge supporting documentation where appropriate
- Notify stakeholders of scope and timeline changes

## 4. Todo Management Integration

### 4.1 Todo File Requirements

- **MANDATORY**: Every ACTION directory MUST contain a todo.md file
- Todo files track task progress, priorities, and completion status
- Claude Code automatically manages todo.md files using native todo functions
- Todo items must align with ACTION plan and success criteria

### 4.2 Todo File Format

```markdown
# TODO: [Action Name]

## Active Tasks
- [ ] Task description (priority: high/medium/low, status: pending/in_progress/completed)

## Completed Tasks
- [x] Completed task description

## Notes
Additional context or dependencies for tasks
```

### 4.3 Todo Management Workflow

- Claude Code automatically creates todo.md when starting an ACTION
- Tasks are derived from ACTION plan phases and requirements
- Progress tracked in real-time as tasks complete
- Todo status integrates with overall ACTION progress tracking

### 4.4 Todo File Compliance

#### Mandatory Requirements
- Every action MUST have todo.md file
- File must follow standardized format from Section 4.2
- Tasks must align with action plan phases
- Progress must be tracked in real-time

#### Enforcement
- Non-compliant actions flagged in actions_index.md
- Automatic todo.md generation for missing files
- Integration with action progress tracking
- Regular compliance audits

## 5. Project Structure and Organization

### 5.1 Directory Structure

```text
/
├── .aicheck/
│   ├── actions/                      # All PROJECT ACTIONS
│   │   ├── [action-name]/            # Individual ACTION directory
│   │   │   ├── [action-name]-plan.md # ACTION PLAN (requires approval)
│   │   │   ├── todo.md              # ACTION TODO tracking (required)
│   │   │   └── supporting_docs/      # ACTION-specific documentation
│   │   │       ├── claude-interactions/  # Claude Code logs
│   │   │       ├── process-tests/        # Temporary tests for ACTION
│   │   │       └── research/             # Research and notes
│   │   └── completed/               # Completed/cancelled actions
│   ├── current_action                # Current ActionActivity for EDITOR
│   ├── actions_index.md              # Master list of all ACTIONS
│   ├── ACTION_TIMELINE.md            # System evolution timeline (required)
│   ├── rules.md                      # This document
│   └── session_log_[date].md         # Daily logs
├── documentation/                    # Permanent PROJECT documentation
│   ├── api/                          # API documentation
│   ├── architecture/                 # System architecture docs
│   ├── configuration/                # Configuration guides
│   ├── deployment/                   # Deployment procedures
│   ├── testing/                      # Testing strategies
│   └── user/                         # User documentation
├── tests/                            # Permanent test suite
│   ├── unit/                         # Unit tests
│   ├── integration/                  # Integration tests
│   ├── e2e/                          # End-to-end tests
│   └── fixtures/                     # Test data and fixtures
```

### 5.2 Action Directory Structure

```text
.aicheck/actions/[action-name]/
├── PLAN.md                      # ACTION plan (REQUIRED)
├── todo.md                      # Task tracking (REQUIRED)
└── supporting_docs/             # ACTION-specific docs

### 5.3 Action Lifecycle Organization

Actions progress through defined lifecycle stages with corresponding directory organization:

#### Active Actions
- Location: `.aicheck/actions/[action-name]/`
- Status: ActiveAction, Not Started, or Blocked
- Full compliance with Section 5.2 structure required

#### Completed/Cancelled Actions  
- Location: `.aicheck/actions/completed/[action-name]/`
- Organized for historical reference and knowledge preservation
- Maintains full supporting_docs structure for future reference
- Preserves all documentation for audit trail and lessons learned

#### Directory Migration Process
When actions reach completion or cancellation:
1. Move entire action directory to `.aicheck/actions/completed/`
2. Update actions_index.md with new location and status
3. Add completion/cancellation metadata to action files
4. Preserve all supporting documentation for audit trail
5. Update any cross-references in other actions

## 6. Workflow and Processes

### 6.1 Standard Action Lifecycle

1. **Creation**: ACTION directory created with initial PLAN
2. **Planning**: PLAN.md developed with requirements and approach
3. **Approval**: Human manager reviews and approves PLAN
4. **Test Development**: Tests created based on PLAN specifications
5. **Implementation**: Code written to pass tests
6. **Documentation**: Updates to relevant documentation
7. **Review**: Code review and validation
8. **Completion**: ACTION marked complete, documents migrated
9. **Timeline Update**: Update ACTION_TIMELINE.md with completion details
10. **Organization**: Move completed/cancelled actions to `/actions/completed/`
11. **Index Update**: Update actions_index.md with enhanced formatting
12. **Compliance Verification**: Ensure all required files (todo.md, supporting_docs) exist

#### 6.1.1 Deployment Verification Requirements

**CRITICAL**: Actions involving production systems MUST verify deployment before marking as COMPLETED:

1. **Code Deployment Verification**:
   - All code changes MUST be committed to git
   - Changes MUST be pushed to the remote repository (GitHub)
   - For production systems, deployment MUST be triggered and verified
   - Production functionality MUST be tested and confirmed working

2. **Completion Criteria for Deployed Systems**:
   - [ ] All changes committed with descriptive messages
   - [ ] Changes pushed to remote repository
   - [ ] Deployment triggered (if automatic) or manually deployed
   - [ ] Production system tested and functionality verified
   - [ ] Test results documented in supporting_docs
   - [ ] Any deployment issues resolved

3. **Exceptions**:
   - Local-only development tools
   - Documentation-only changes
   - Actions explicitly marked as "local development only"
   - Emergency fixes pending review (must be noted)

4. **Verification Documentation**:
   - Create `deployment-verification.md` in supporting_docs
   - Include deployment timestamps
   - Document test results from production
   - Note any discrepancies between local and production

**WARNING**: Marking an ACTION as COMPLETED without deployment verification when deployment is required constitutes a MISREPRESENTATION and violates Section 1.3 guidelines.

#### 6.1.2 ACTION Creation Checklist

1. Create directory: `.aicheck/actions/[action-name]/`
2. Create `PLAN.md` with objectives, approach, tests
3. Create `todo.md` (or let Claude auto-generate)
4. Update `actions_index.md`
5. Get approval before proceeding

### 6.2 Claude Code Workflow

**Test-First Pattern**: Human discusses → Claude proposes plan/tests → Human approves → Claude implements → Human reviews → Claude documents

**Enhancement Pattern**: Human requests → Claude analyzes → Proposes approach → Human approves → Claude implements → Review/iterate

#### 6.2.1 Security Guidelines

- No real credentials in prompts
- Use mock data for sensitive scenarios  
- Security review for auth code
- Document security assumptions
- Verify against OWASP
- Security tests required


### 6.4 Approval Process

All approvals are done by Joshua Field

#### 6.4.1 Multi-Editor Coordination

Daily sync via session logs. Co-own integration tests. Track blockers. Joint planning for conflicts.

### 6.5 AICheck Automation Features

AICheck includes comprehensive automation for system management and validation:

#### Core Automation
1. **Security Validation**: Automatic path validation, permission checks, input sanitization
2. **Action Validation**: Name format validation, status validation, progress tracking
3. **File Structure**: Automatic directory creation, template application, permission setting
4. **System Testing**: Comprehensive test suite for AICheck functionality validation

#### Git Hook Integration
- **Post-commit hooks**: Action completion verification
- **Pre-commit hooks**: Commit message validation
- **Installation**: Run `.aicheck/hooks/install-hooks.sh`

#### Enhanced CLI Commands
```bash
aicheck create-action <name>           # Creates action with validation
aicheck status                         # Comprehensive system status
aicheck update-status <name> <status>  # Update action status
aicheck update-progress <name> <num>   # Update progress (0-100)
aicheck complete-action <name>         # Complete and move to completed/
aicheck validate                       # Validate system structure
aicheck test                          # Run AICheck system tests
aicheck security-check               # Security validation
```

#### Automated Security Features
- Input sanitization for all user inputs
- Path validation preventing directory traversal
- Secure file creation with proper permissions
- Security event logging
- Action name format enforcement (kebab-case)

#### System Testing
- Validates AICheck functionality (not project code)
- Tests action management, security, file structure
- Generates test reports in `.aicheck/test_reports/`
- Run via `aicheck test`

### 6.6 Process Documentation Versioning

PLANs must include version, date, status, and progress. Major changes require version increment.

### 6.7 Actions Index Management

#### Enhanced Formatting Standards
The actions_index.md must include:
- Visual formatting with emojis for status identification
- Progress bars using Unicode block characters (░█)
- Collapsible sections for completed/cancelled actions
- ASCII art headers for visual organization
- Terminal-friendly layout for CLI environments

#### Status Standardization
Use only these approved status values:
- `ActiveAction` - Currently being worked on
- `Not Started` - Planned but not yet begun  
- `Completed` - Successfully finished
- `Cancelled` - Terminated without completion
- `Blocked` - Waiting on dependencies

#### Progress Tracking
- Progress represented as percentage (0-100%)
- Visual progress bars in index: `██░░░░░░░░` format
- Updated in real-time as work progresses

## 7. Style and Documentation Standards

### 7.1 Documentation Style

Use ATX-style headers, fenced code blocks with language specification. Use bullet points for lists, bold for emphasis. Use PascalCase for Action logical names in discussions, kebab-case for all file and directory names.

.md extension for documentation, -plan.md suffix for action plans (e.g., feature-name-plan.md). 4-space indentation in code. Maintain descriptive names and consistent organization.

Follow documentation structure in documentation/README.md. Separate technical from user-facing documentation. Document configuration files in documentation/configuration/.

### 7.2 Claude Code Prompt Style

Claude Code prompts MUST:
- Reference specific sections of RULES.md in prompts (using correct capitalization)
- Include directory structure information
- Reference documentation sources
- Provide example output formats
- Specify verification criteria
- Use consistent formatting with clear sections
- End with explicit output expectations

### 7.3 Commit and Status Practices

Write commit messages that begin with a present-tense verb. Keep commit message subject lines under 50 characters (hard limit). Use the extended commit body for any content beyond the 50-character limit.

Include action reference in a standardized format (e.g., [action-name]). For longer descriptions, use the commit body separated by a blank line. Wrap commit message body text at 72 characters.

Use predefined status values with progress percentage. Document blockers clearly with timestamps. Create clear error messages with error codes, resolution steps, and appropriate logging.

Example:
```
Add user authentication [auth-system]
```

### 7.4 Visual Formatting Standards

#### Status Indicators
- 🟡 ActiveAction - Currently being worked on
- 🔴 Not Started - Planned but not begun  
- 🟢 Completed - Successfully finished
- ❌ Cancelled - Terminated
- ⏸️ Blocked - Waiting on dependencies

#### Progress Bars
Format: `██░░░░░░░░` (10 characters, filled=complete)

Must be terminal-compatible and maintain alignment in monospace fonts.

## 8. Testing Framework

### 8.1 Test-Driven Development

ACTIONS MUST have tests written before implementation with coverage for:
- Core functionality validation (basic behavior verification)
- Boundary condition tests (validating behavior at threshold values)
- Integration tests with other ACTIONS
- Error handling tests

Test data SHOULD be maintained in standard locations and formats. Test fixtures SHOULD be reused across related ACTIONS when appropriate.

#### 8.1.1 Performance Testing

For performance-critical actions: baseline before, test after, document impact, regression tests for critical paths.

### 8.2 Testing Documentation

Organized into:
- Test Specifications: Inputs, expected outputs, validation criteria
- Testing Strategies: Approaches for different ACTIONS/scenarios
- Test Data Management: Guidelines for test data
- Testing Tools: Documentation of utilities/frameworks
- Test Coverage Reports: Analysis of coverage and gaps

### 8.3 Test Migration Requirements

When tests are migrated, the following requirements MUST be met:

**Migration Plan must specify:**
- Source and destination test locations
- Timeline with discrete phases (parallel testing, validation, cutover)
- Verification methods for maintaining test coverage
- Rollback procedures if issues are detected

**Coverage Verification** - Test coverage MUST NOT decrease during migration:
- Pre-migration coverage metrics MUST be documented
- Post-migration coverage MUST meet or exceed pre-migration levels
- Any reduction in coverage MUST be explicitly justified and approved

**Parallel Testing Period** - During transition, both old and new test implementations MUST be maintained until:
- Three consecutive successful CI runs have been completed with both test suites
- All test coverage metrics show equal or improved coverage
- Technical Lead has explicitly approved the retirement of legacy tests
- A one-week observation period has passed with no regressions

**Version Alignment** - Test versions MUST align with the ACTIONS they validate, maintaining traceability

### 8.4 Test Location Specifications

**Directory Structure:**
- Product functionality unit tests → tests/unit/ at the project root
- Integration tests → tests/integration/ at the project root
- E2E tests → tests/e2e/ at the project root
- Process-specific temporary tests → .aicheck/actions/[action-name]/supporting_docs/process-tests/

**Naming Conventions:**
- Test files MUST use the pattern [feature-name].test.[ext] where [ext] is the appropriate extension for the language (e.g., .js, .py, .go)
- Integration test files MUST use the pattern [feature-name].integration.test.[ext]
- E2E test files MUST use the pattern [workflow-name].e2e.test.[ext]

**Organization:**
- Test directory structure SHOULD mirror the code structure being tested
- Shared test utilities → tests/utils/
- Test data → tests/fixtures/

### 8.5 Claude Code Test Generation

Claude may generate tests when provided with:
- ACTION requirements and success criteria
- Expected inputs/outputs
- Boundary conditions
- Integration points

Validate all generated tests against PLAN.

## 9. Documentation Organization

### 9.1 Documentation Types and Locations

**ACTION Process Documentation (.aicheck/actions/[action-name]/supporting_docs/)**
- Implementation details specific to ACTION
- Research notes, experiments, progress tracking
- Design worksheets, ACTION-specific planning
- Claude Code interactions in claude-interactions/ subfolder

**Product Documentation (/documentation/[CATEGORY]/)**
- System architecture and component descriptions
- Deployment and environment configuration guides
- API references and specifications
- User guides and end-user documentation

ACTION documentation SHOULD be migrated to product documentation directories:
- WHEN the ACTION is completed, OR
- WHEN documentation has value beyond the ACTION's scope, AND
- WHEN approved by the technical lead

### 9.2 Documentation Migration Requirements

Migration from ACTION to product documentation MUST:
- Create a migration ticket in the originating ACTION
- Map source files to destination locations
- Preserve version history (git history preferred)
- Update all internal references and links
- Obtain approval from documentation owner
- Leave forwarding references in ACTION directory
- Add migration notice to ACTION's README

## 10. Language-Specific Standards

### 10.1 Language Standards

**Python**: PEP 8 (120 char lines), type hints, Black formatter
**JavaScript/TypeScript**: ESLint, prefer TypeScript, Jest for tests
**Documentation**: Clear English, active voice, consistent terminology

## 11. Implementation Standards

### 11.1 Configuration
- No hard-coded credentials
- Use environment variables
- Provide .env.example

### 11.2 Error Handling
- Error codes
- Human-readable messages
- Resolution steps
- Appropriate logging

### 11.3 Dependencies
- Document in manifest
- Pin major versions
- Security audits
- Clear install instructions

## 12. Version Control

### 12.1 Branches
- Main always deployable
- Feature branches per ACTION
- Pull requests required

### 12.2 Commits
- Atomic changes
- Present-tense imperative
- Reference ACTION
- Clean history

## 13. Review and Approval Process

### 13.1 Pre-Implementation Review

- ACTION PLAN must be reviewed
- Test specifications approved
- Architecture decisions documented
- Security implications considered
- Performance impact assessed

### 13.2 Code Review Focus Areas

- Correctness and functionality
- Security vulnerabilities
- Performance implications
- Code maintainability
- Documentation completeness
- Test coverage

### 13.3 Post-Implementation Review

- All tests passing
- Documentation updated
- Dependencies documented
- Deployment instructions clear
- Monitoring in place

## 14. Continuous Improvement

- Regular retrospectives
- Track metrics (completion time, coverage, quality)
- Develop automation tools
- Update RULES based on experience

## 15. Compliance and Governance

### 15.1 Audit Trail

- All ACTIONS tracked in index
- Decisions documented in PLANs
- Changes tracked in version control
- Reviews recorded in PRs
- Approvals logged appropriately

### 15.2 Security Compliance

- Regular security assessments
- Dependency vulnerability scanning
- Access control reviews
- Incident response procedures
- Compliance reporting

### 15.3 Quality Assurance

- Code quality metrics
- Test coverage requirements
- Documentation standards
- Performance benchmarks
- Accessibility compliance

## 16. Exceptions and Technical Debt

### 16.1 Rule Exceptions
Require Joshua Field approval, documentation, and regular review.

### 16.2 Technical Debt
Tracked as ACTIONS, prioritized quarterly, addressed systematically.

---

**Document Version**: 3.1
**Last Updated**: 2025-05-26
**Owner**: Joshua Field
**Next Review**: Quarterly