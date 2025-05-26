# AICheck Rules

This document is the controlling reference for all work managed by the AICheck system in this PROJECT. These rules cannot be modified without approval from Joshua Field

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

Before proceeding, it is essential to understand the following key terms as used throughout this document:

### 2.1 Core Terminology

- **PROJECT**: The overall software development initiative governed by these rules; a long-running collaborative effort with defined objectives, teams, and governance structures.
- **PROGRAM**: The software product being built by the PROJECT; the actual executable system that will be deployed and used by end-users.
- **ACTION**: A discrete unit of work that contributes to the PROGRAM; has clear boundaries, objectives, and completion criteria. An ACTION is the atomic unit of work assignment and tracking.
- **EDITOR**: Any human or AI contributor who performs work on ACTIONS; includes developers, writers, designers, and Claude Code.
- **PLAN**: A documented specification for an ACTION; includes requirements, approach, expected outcomes, and testing strategy.
- **ActiveAction**: An ACTION that is currently being worked on by one or more EDITORs; tracked in .aicheck/current_action for individual EDITORs.
- **Process Documentation**: Temporary documentation relevant only during an ACTION's lifecycle; stored in the ACTION's supporting_docs directory.
- **Product Documentation**: Documentation with enduring relevance beyond ACTION completion; stored in the centralized documentation directory.

### 2.2 Workflow Terminology

- **Test-Driven Development (TDD)**: Development approach where tests are written before implementation code; ensures functionality is well-defined and verifiable.
- **Documentation-First**: Principle that documentation should be created or updated before code, ensuring clear understanding of objectives.
- **Quick Response**: Limited exception to standard processes for urgent operational issues; still requires minimal planning and test-first approach.
- **Action Lifecycle**: The standard progression of an ACTION from creation through planning, implementation, testing, and completion.

### 2.3 System Components

- **AICheck System**: The tooling, processes, and rules that govern the PROJECT's development workflow.
- **Claude Code**: AI-powered assistant that helps implement ACTIONS following the project's guidelines.
- **Supporting Documents**: Auxiliary files associated with an ACTION; stored in  the ACTION's supporting_docs directory.
- **Process Tests**: Tests specific to an ACTION that are not intended to be part of the long-term test suite.
- **Product Tests**: Tests with enduring value that are maintained as part of the PROGRAM's test suite.

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

#### 3.1.1 Claude Code Boundary Examples

**ALLOWED without approval:**
- Implementing error handler based on approved PLAN
- Writing unit tests for defined functionality
- Refactoring code for readability (same functionality)
- Adding logging statements
- Updating comments and docstrings
- Creating helper functions within ACTION scope

**REQUIRES approval:**
- Adding new API endpoints
- Changing database schema
- Modifying authentication flow
- Integrating new third-party services
- Changing public interfaces
- Adding new dependencies

### 3.2 Documentation Requirements

- Action plan (PLAN.md)
- Supporting documentation
- Status updates (Not Started, ActiveAction, Completed, Blocked, On Hold, Cancelled)

#### 3.2.1 Managing ACTION Dependencies

When an ACTION depends on another:

1. List dependencies in PLAN.md `## Dependencies` section
2. Document integration points in supporting_docs/integration-points.md
3. Create integration tests spanning both ACTIONS
4. Coordinate with owners of dependent ACTIONS
5. Document any blocking issues in the ACTION status

Example dependency declaration:

```markdown
## Dependencies

- APIIntegration: Requires error response format (v2.1)
- AuthSystem: Uses JWT tokens from auth service
- Database: Needs user table migration (migration_003)
```

### 3.3 Claude Code Documentation

All Claude Code interactions MUST:
- Be stored in .aicheck/actions/[action-name]/supporting_docs/claude-interactions/
- Reference specific sections of the ACTION's PLAN
- Include the complete prompts used to generate code or solutions
- Document any modifications made to Claude-generated content
- Include verification steps performed on Claude-generated outputs
- Note iterations or refinements to prompts

#### 3.3.1 Claude Interaction Documentation Format

Each interaction must include:

```markdown
# Claude Interaction Log

**Date**: 2025-05-16
**ACTION**: ErrorHandlingImplementation
**Purpose**: Generate error handler base classes
**Template Used**: action-implementation/basic.md v1.2
**Prompt Hash**: abc123def456

## Prompt

[Full prompt text]

## Response

[Claude's response]

## Modifications

[Any manual changes made]

## Verification

[How output was verified]

## Iterations

[Number of attempts: 2]
[Reason for iterations: Added security constraints]
```

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

Each ACTION must follow this structure:

```text
.aicheck/actions/[action-name]/
├── [action-name]-plan.md        # ACTION plan (REQUIRED)
├── todo.md                      # ACTION TODO tracking (REQUIRED)
├── progress.md                  # Progress tracking
├── status.txt                   # Current status and percentage
└── supporting_docs/             # All ACTION-specific docs
    ├── claude-interactions/     # Claude Code interactions
    ├── process-tests/           # ACTION-specific tests
    ├── research/                # Research and experiments
    └── diagrams/                # Visual documentation
```

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

#### 6.1.1 ACTION Creation Checklist

When creating a new ACTION:

- [ ] Create directory: `.aicheck/actions/[action-name]/`
- [ ] Create PLAN file: `[action-name]-plan.md`
- [ ] Create todo.md file (Claude Code will auto-generate from PLAN)
- [ ] Add to actions index: `.aicheck/actions_index.md`
- [ ] Create supporting_docs directory
- [ ] Define success criteria in PLAN
- [ ] Specify test requirements
- [ ] Get PLAN approval

### 6.2 Claude Code Enhanced Workflow

#### Optimal Claude-Human Collaboration Patterns

**Pattern 1: Test-Implementation-Document Cycle**

1. Human: Discuss needs for ACTION
2. Claude: Generate ACTION directory, propose PLAN and comprehensive tests
3. Human: Review and approve PLAN and tests
4. Claude: Implement code to pass tests
5. Human: Review implementation
6. Claude: Generate/update documentation
7. Human: Final review and approval

**Pattern 2: Incremental Enhancement**

1. Human: Request specific enhancement to existing code
2. Claude: Analyze current implementation
3. Claude: Propose enhancement approach with tests
4. Human: Approve approach
5. Claude: Implement enhancement
6. Human: Review and iterate
7. Claude: Update all affected documentation

#### 6.2.1 Security Guidelines for Claude Code

When using Claude for security-sensitive code:

1. Never include real credentials in prompts
2. Use example/mock data for sensitive scenarios
3. Request security review for authentication/authorization code
4. Document security assumptions in claude-interactions/
5. Verify generated code against OWASP guidelines
6. Add security-specific tests for all generated auth code

### 6.3 Quick Response (Emergency Fix) Protocol

For urgent production issues requiring immediate resolution:

1. **Eligibility Criteria**:
   - Production service is down or severely degraded
   - Security vulnerability requires immediate patching
   - Data corruption is actively occurring
   - Critical business function is blocked

2. **Quick Response Process**:
   - Create ACTION with `-emergency` suffix (e.g., `critical-auth-fix-emergency`)
   - Document issue, root cause, and proposed fix in emergency-plan.md
   - Write minimal tests covering the critical fix
   - Implement fix with continuous monitoring
   - Create full ACTION for proper implementation within 48 hours
   - Emergency fixes must be replaced by proper implementations within 7 days

3. **Documentation Requirements**:
   - Incident report in supporting_docs/incident-report.md
   - Root cause analysis
   - Emergency fix details
   - Follow-up ACTION reference

### 6.4 Approval Process

All approvals are done by Joshua Field

#### 6.4.1 Multi-Editor Coordination

When multiple EDITORs work on related ACTIONS:

- Daily sync via shared `.aicheck/session_log_[date].md`
- Integration tests must be co-owned
- Blocking dependencies tracked in `.aicheck/blockers.md`
- Resolution requires joint planning sessions

### 6.5 Git Hook Compliance (Phased Approach)

Commit message enforcement is implemented progressively to maintain workflow efficiency while improving compliance:

#### Phase 1: Commit Message Validation (Current)

1. Enforce character limit (50 chars max)
2. Present-tense imperative mood
3. Optional: Warn about missing ACTION references

#### Phase 2: ACTION Reference Requirements (Future)

1. Require ACTION references in commits
2. Validate ACTION exists in index
3. Update ACTION progress automatically

#### Phase 3: Full Integration (Planned)

1. Pre-commit test validation
2. Documentation checks
3. Automated documentation migration

#### Action Completion Hook (Implemented)

The post-commit hook automatically checks completion requirements when actions are marked complete:

1. **Documentation Migration Check**: Identifies universal docs in supporting_docs/ requiring migration
2. **Actions Index Update**: Verifies action is marked as Completed in actions_index.md
3. **Timeline Update**: Ensures ACTION_TIMELINE.md includes completion entry
4. **Dependency Documentation**: Reminds about dependency documentation requirements
5. **Directory Migration**: Checks if action directory needs moving to completed/

**Installation**: Run `.aicheck/hooks/install-hooks.sh` to install git hooks

**Manual Check**: `.aicheck/hooks/post-action-complete.sh action complete <action-name>`

### 6.6 Process Documentation Versioning

All PLANs must include version information:

```markdown
# ACTION: [name]

Version: 1.0
Last Updated: 2025-05-16
Status: ActiveAction
Progress: 45%
```

Major changes require version increment and changelog.

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

Example of proper commit message format:
```
Add user authentication module [auth-system]

- Implements JWT-based authentication
- Adds password hashing with bcrypt
- Creates login/logout endpoints
- Includes unit tests for all components
```

### 7.4 Enhanced Visual Formatting Standards

These standards apply specifically to actions_index.md and other dashboard documentation.

#### Actions Index Formatting Requirements

The actions_index.md must include:
- Visual formatting with emojis for status identification (🟡🟢🔴❌)
- Progress bars using Unicode block characters (`░█`)
- Collapsible HTML sections for completed/cancelled actions
- ASCII art headers using Unicode box drawing characters
- Terminal-friendly layout optimized for CLI environments
- Consistent emoji categorization system for action types

#### Status Standardization

Use only these approved status values with corresponding visual indicators:
- `ActiveAction` (🟡) - Currently being worked on
- `Not Started` (🔴) - Planned but not yet begun  
- `Completed` (🟢) - Successfully finished
- `Cancelled` (❌) - Terminated without completion
- `Blocked` (⏸️) - Waiting on dependencies

#### Progress Visualization Standards

- Progress represented as percentage (0-100%) with visual bars
- Visual progress bars format: `██░░░░░░░░` (filled=completed, empty=remaining)
- Updated in real-time as work progresses in action plans
- Consistent 10-character width for alignment in tables

#### Terminal Compatibility Requirements

All enhanced formatting must:
- Display correctly in standard terminal environments
- Use Unicode characters supported by common terminal emulators
- Maintain readability when viewed via `cat`, `less`, `head`, `tail` commands
- Preserve table alignment and visual hierarchy in monospace fonts

## 8. Testing Framework

### 8.1 Test-Driven Development

ACTIONS MUST have tests written before implementation with coverage for:
- Core functionality validation (basic behavior verification)
- Boundary condition tests (validating behavior at threshold values)
- Integration tests with other ACTIONS
- Error handling tests

Test data SHOULD be maintained in standard locations and formats. Test fixtures SHOULD be reused across related ACTIONS when appropriate.

#### 8.1.1 Performance Testing Requirements

For ACTIONS affecting system performance:
- Baseline performance tests before implementation
- Performance tests after implementation
- Document performance impact in supporting_docs/performance-impact.md
- Regression tests for critical paths
- Claude may suggest performance optimizations with benchmarks

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

Claude Code MAY be used to generate tests for ACTIONS under the following conditions:

The ACTION PLAN must be thoroughly documented before test generation. Claude Code must be provided with:
- Specific ACTION requirements and success criteria
- Expected inputs and outputs
- Boundary conditions and edge cases
- Integration points with other ACTIONS

Generated tests MUST be validated against the ACTION PLAN. Generated tests MUST follow the project's testing standards and patterns. Any manual modifications to generated tests MUST be documented.

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

### 10.1 Python Standards

Follow PEP 8 style guide with these specific exceptions:
- Line length: 120 characters (not 79)
- Use type hints for all new functions
- Docstrings required for all public functions
- Use Black for code formatting

Import order:
1. Standard library imports
2. Third-party imports
3. Local application imports

### 10.2 JavaScript/TypeScript Standards

- Use ESLint with the project's configuration
- Prefer TypeScript for new files
- Use Jest for testing
- Follow Airbnb style guide with modifications
- Async/await over promises
- Functional programming patterns where appropriate

### 10.3 Documentation Language

- Write in clear, concise English
- Use active voice
- Avoid jargon without explanation
- Include examples for complex concepts
- Maintain consistent terminology

## 11. Implementation Standards

### 11.1 Environment Configuration

- Never hard-code credentials or secrets
- Use environment variables for configuration
- Document all required environment variables
- Provide example .env.example file
- Support multiple deployment environments

### 11.2 Error Handling

All errors must include:
- Error code for programmatic handling
- Human-readable message
- Suggested resolution steps
- Context about where the error occurred
- Logging at appropriate level

### 11.3 Dependency Management

- Document all dependencies in appropriate manifest
- Pin major versions for production dependencies
- Regular security audits of dependencies
- Graceful degradation for optional dependencies
- Clear installation instructions

## 12. Version Control Best Practices

### 12.1 Branching Strategy

- Main branch is always deployable
- Feature branches for new ACTIONS
- Hotfix branches for emergency fixes
- No direct commits to main
- All changes through pull requests

### 12.2 Pull Request Requirements

- Reference ACTION in PR title
- Tests must pass before merge
- Code review required
- Update documentation if needed
- Clean commit history

### 12.3 Commit Best Practices

- Atomic commits (one logical change)
- Present-tense imperative mood
- Reference ACTION and issue numbers
- Explain why, not just what
- Sign commits when required

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

### 14.1 Retrospectives

- Regular ACTION retrospectives
- Document lessons learned
- Update RULES based on experience
- Share knowledge across team
- Improve tooling and processes

### 14.2 Metrics and Monitoring

- Track ACTION completion times
- Monitor test coverage trends
- Measure documentation quality
- Analyze error rates
- Review performance metrics

### 14.3 Tool Development

- Create tools to enforce RULES
- Automate repetitive tasks
- Improve developer experience
- Enhance Claude Code integration
- Streamline approval processes

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

## 16. Exception Handling

### 16.1 Rule Exceptions

- Must be documented
- Require approval from Joshua Field
- Time-limited when possible
- Reviewed regularly
- Lessons learned captured

### 16.2 Emergency Procedures

- Clear escalation path
- Documented in runbooks
- Tested regularly
- Post-incident reviews
- Process improvements

### 16.3 Technical Debt

- Tracked as ACTIONS
- Prioritized regularly
- Addressed systematically
- Documented thoroughly
- Reviewed quarterly

---

**Document Version**: 3.0
**Last Updated**: 2025-05-24
**Owner**: Joshua Field
**Next Review**: Quarterly