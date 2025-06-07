# AICheck Rules

This document is the controlling reference for all work managed by the AICheck system in this PROJECT. These rules cannot be modified without approval from Joshua Field

> **Quick Navigation**: [DEPLOYMENT REQUIREMENTS](#deployment-requirements-critical) | [Core Principles](#1-core-principles) | [Glossary](#2-glossary-and-key-concepts) | [Action Management](#3-action-management) | [Todo Management](#4-todo-management-integration) | [Project Structure](#5-project-structure-and-organization) | [Workflow](#6-workflow-and-processes) | [Standards](#7-style-and-documentation-standards) | [Testing](#8-testing-framework) | [Documentation](#9-documentation-organization)

---

# DEPLOYMENT REQUIREMENTS (CRITICAL)

## ⚠️ MANDATORY: NO ACTION IS COMPLETE WITHOUT DEPLOYMENT VERIFICATION

**"CODE COMPLETE" ≠ "DEPLOYED AND WORKING"**

### Definition of Done for Production Systems

| Status | Requirement | Verification |
|--------|------------|-------------|
| ❌ Code Complete | Changes written and committed locally | NOT sufficient for completion |
| ❌ Build Passing | Tests pass in development environment | NOT sufficient for completion |
| ✅ **DEPLOYED AND WORKING** | **Production system tested and verified functional** | **REQUIRED for completion** |

### MANDATORY Production Verification Steps

1. **Test the ACTUAL production URL** (not localhost)
2. **Document the production URL and timestamp tested**
3. **Capture response/output as evidence**
4. **Verify all critical endpoints work end-to-end**
5. **Test error handling in production context**
6. **Confirm deployment platform settings match expectations**

### Deployment Verification Checklist

**Before marking ANY ACTION as COMPLETED:**

- [ ] Code pushed to correct branch
- [ ] Deployment triggered successfully  
- [ ] Build completed without errors
- [ ] Service shows "Live" status
- [ ] **Production URL responds correctly**
- [ ] **All endpoints tested and documented**
- [ ] Performance acceptable
- [ ] Logs show no critical errors
- [ ] Create `deployment-verification.md` in supporting_docs
- [ ] Document test results from production

**Platform-Specific Checks:**
- [ ] Verify deployment configuration (render.yaml vs dashboard settings)
- [ ] Check for cached/stale deployments
- [ ] Confirm environment variables are properly set
- [ ] Test build and start commands are correct

### ⚠️ WARNING: Deployment Verification Violations

**Marking an ACTION as COMPLETED without deployment verification when deployment is required constitutes a MISREPRESENTATION and violates Section 1.3 guidelines.**

**This includes:**
- Claiming production deployment without testing production URLs
- Assuming deployment worked based on local testing
- Skipping verification due to "time pressure"
- Not documenting actual production test results

---

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

!!! DEPLOYMENT VERIFICATION IS MANDATORY. YOU MAY NOT MARK AN ACTION AS COMPLETED WITHOUT VERIFYING PRODUCTION FUNCTIONALITY. "CODE COMPLETE" DOES NOT EQUAL "DEPLOYED AND WORKING"!!!

**Production System Requirements**:
- Test actual production URLs, not localhost
- Document all production endpoints tested  
- Capture evidence of working functionality
- Verify deployment configuration matches code
- Check platform-specific settings (e.g., Render dashboard vs blueprint)

Follow AICheck directory structure and naming conventions. Update action status and document progress regularly. Follow language-specific best practices. Implement graceful degradation for optional dependencies.

Use Docker-based development when available, with documented alternatives when not available. Document all environment variables and configuration options. Implementation procedures should reside within the Action's Plan.

### 1.4 AI Assistant Integration

AI assistants function as AI engineers within the AICheck workflow, complementing human editors while respecting our documentation-first approach and action-based governance requirements.

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
- Document all AI assistant interactions in ACTION's supporting_docs
- Use standardized prompt templates stored in .aicheck/templates/ai-prompts/

## 2. Glossary and Key Concepts

Before proceeding, it is essential to understand the following key terms as used throughout this document:

### 2.1 Core Terminology

**PROJECT**: The overall software development initiative governed by these rules; a long-running collaborative effort with defined objectives, teams, and governance structures.

**PROGRAM**: The software product being built by the PROJECT; the actual executable system that will be deployed and used by end-users.

**ACTION**: A discrete unit of work that contributes to the PROGRAM; has clear boundaries, objectives, and completion criteria. An ACTION is the atomic unit of work assignment and tracking.

**EDITOR**: Any human or AI contributor who performs work on ACTIONS; includes developers, writers, designers, and AI assistants.

**PLAN**: A documented specification for an ACTION; includes requirements, approach, expected outcomes, and testing strategy.

**ActiveAction**: An ACTION that is currently being worked on by one or more EDITORs; tracked in .aicheck/current_action for individual EDITORs. Only ONE ACTION can be active per EDITOR at any time. All work performed by an EDITOR is automatically associated with their ActiveAction.

**Process Documentation**: Temporary documentation relevant only during an ACTION's lifecycle; stored in the ACTION's supporting_docs directory.

**Product Documentation**: Documentation with enduring relevance beyond ACTION completion; stored in the centralized documentation directory.

### 2.2 Workflow Terminology

**Test-Driven Development (TDD)**: Development approach where tests are written before implementation code; ensures functionality is well-defined and verifiable.

**Documentation-First**: Principle that documentation should be created or updated before code, ensuring clear understanding of objectives.

**Quick Response**: Limited exception to standard processes for urgent operational issues; still requires minimal planning and test-first approach.

**Action Lifecycle**: The standard progression of an ACTION from creation through planning, implementation, testing, and completion.

### 2.3 System Components

**AICheck System**: The tooling, processes, and rules that govern the PROJECT's development workflow.

**AI Assistant**: AI-powered tools (Claude, GPT, Copilot, etc.) that help implement ACTIONS following the project's guidelines.

**Supporting Documents**: Auxiliary files associated with an ACTION; stored in the ACTION's supporting_docs directory.

**Process Tests**: Tests specific to an ACTION that are not intended to be part of the long-term test suite.

**Product Tests**: Tests with enduring value that are maintained as part of the PROGRAM's test suite.

## 3. Action Management

### 3.0 Action Completion Requirements

**Every Action MUST have a `deployment-verification.md` file** in its supporting_docs directory before being marked COMPLETE. This file must include:
- Production URL tested
- Timestamp of testing
- Sample request/response data
- List of all endpoints verified
- Any issues encountered and resolutions
- Screenshots or logs as evidence

### 3.1 Understanding Actions vs ActiveAction

**Critical Distinction**:
- **ACTION**: A defined unit of work (task, feature, bugfix) that exists in the project
- **ActiveAction**: The ONE ACTION currently selected for work by an EDITOR

**Key Rules**:
1. An EDITOR can only have ONE ActiveAction at a time
2. All code changes, commits, and documentation are attributed to the ActiveAction
3. To work on a different ACTION, you must first change your ActiveAction using `./aicheck action set`
4. Completing an ACTION (`./aicheck action complete`) automatically clears your ActiveAction

### 3.2 AI Editor Scope

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

#### 3.2.1 AI Assistant Boundary Examples

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

### 3.3 Documentation Requirements

Action plan (PLAN.md)
Supporting documentation
Status updates (Not Started, ActiveAction, Completed, Blocked, On Hold)

#### 3.3.1 Managing ACTION Dependencies

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

### 3.4 AI Assistant Documentation

All AI assistant interactions MUST:
- Be stored in .aicheck/actions/[action-name]/supporting_docs/claude-interactions/
- Reference specific sections of the ACTION's PLAN
- Include the complete prompts used to generate code or solutions
- Document any modifications made to AI-generated content
- Include verification steps performed on AI-generated outputs
- Note iterations or refinements to prompts

#### 3.4.1 AI Interaction Documentation Format

Each interaction must include:

```markdown
# AI Assistant Interaction Log

**Date**: 2025-05-28
**ACTION**: ErrorHandlingImplementation
**Purpose**: Generate error handler base classes
**Template Used**: action-implementation/basic.md v1.2
**Prompt Hash**: abc123def456

## Prompt

[Full prompt text]

## Response

[AI Assistant's response]

## Modifications

[Any manual changes made]

## Verification

[How output was verified]

## Iterations

[Number of attempts: 2]
[Reason for iterations: Added security constraints]
```

## 4. Todo Management Integration

### 4.1 Todo File Requirements

- **MANDATORY**: Every ACTION directory MUST contain a todo.md file
- Todo files track task progress, priorities, and completion status
- AI assistants automatically manage todo.md files using native todo functions
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

- AI assistants automatically create todo.md when starting an ACTION
- Tasks are derived from ACTION plan phases and requirements
- Progress tracked in real-time as tasks complete
- Todo status integrates with overall ACTION progress tracking

## 5. Project Structure and Organization

### 5.1 Directory Structure

```text
/
├── .aicheck/
│   ├── actions/                      # All PROJECT ACTIONS
│   │   └── [action-name]/            # Individual ACTION directory
│   │       ├── [action-name]-plan.md # ACTION PLAN (requires approval)
│   │       ├── todo.md              # ACTION TODO tracking (required)
│   │       └── supporting_docs/      # ACTION-specific documentation
│   │           ├── ai-interactions/      # AI assistant logs
│   │           ├── process-tests/        # Temporary tests for ACTION
│   │           └── research/             # Research notes
│   ├── current_action                # Current ActionActivity for EDITOR
│   ├── actions_index.md              # Master list of all ACTIONS
│   ├── rules.md                      # This document
│   └── templates/                    # Templates for prompts and actions
├── documentation/                    # Permanent PROJECT documentation
│   ├── api/                          # API documentation
│   ├── architecture/                 # System architecture docs
│   ├── configuration/                # Configuration guides
│   ├── dependencies/                 # Dependency documentation
│   ├── deployment/                   # Deployment procedures
│   ├── testing/                      # Testing strategies
│   └── user/                         # User documentation
├── tests/                            # Product tests with enduring value
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
├── status.txt                   # Current status
└── supporting_docs/             # Supporting documentation
    ├── ai-interactions/         # AI assistant interaction logs
    ├── process-tests/          # Tests specific to this ACTION
    ├── research/               # Research and analysis
    ├── integration-points.md   # Integration with other ACTIONS
    └── deployment-verification.md  # Production deployment verification
```

## 6. Workflow and Processes

### 6.1 Standard Action Lifecycle

1. **ACTION Creation**: Define objectives, scope, and success criteria
2. **PLAN Development**: Create detailed plan with approach and tests
3. **PLAN Approval**: Human review and approval of approach
4. **Test Implementation**: Write tests before implementation
5. **Code Implementation**: Develop according to approved plan
6. **Testing and Validation**: Ensure all tests pass
7. **Documentation**: Update relevant documentation
8. **Deployment Verification**: Verify production functionality (if applicable)
9. **Review and Integration**: Final review before completion
10. **ACTION Completion**: Mark complete with dependency verification
11. **Documentation Migration**: Move relevant docs to permanent locations
12. **Compliance Verification**: Ensure all required files exist:
    - todo.md in action directory
    - supporting_docs directory
    - deployment-verification.md (for deployable Actions)
    - Test results documentation
    - Migration of enduring documentation to /documentation/

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

3. **Enhanced Production Testing Requirements**:
   - [ ] Test actual production URLs (not localhost)
   - [ ] Document production URL and timestamp tested
   - [ ] Capture response/output as evidence
   - [ ] Verify all critical endpoints work end-to-end
   - [ ] Test error handling in production context
   - [ ] Confirm deployment platform settings match expectations
   - [ ] Performance acceptable in production environment
   - [ ] Logs show no critical errors

4. **Exceptions**:
   - Local-only development tools
   - Documentation-only changes
   - Actions explicitly marked as "local development only"

5. **Verification Documentation**:
   - Create `deployment-verification.md` in supporting_docs
   - Include deployment timestamps
   - Document test results from production
   - Note any discrepancies between local and production
   - Include evidence (screenshots, logs, response data)

**WARNING**: Marking an ACTION as COMPLETED without deployment verification when deployment is required constitutes a MISREPRESENTATION and violates Section 1.3 guidelines.

#### 6.1.2 Deployment Verification Requirements

**Before marking an Action COMPLETE, CI must run the full test suite and verify all routers/endpoints are properly mounted:**

1. **Python Projects**: Run `poetry run pytest -q` (zero failures required)
2. **Node.js Projects**: Run `npm test` or `yarn test` (zero failures required)
3. **API Projects**: Verify all routers are mounted via automated script
4. **Production deployment must be verified with actual URL testing**

**CI Pipeline Requirements**:
- Test suite must run automatically on every push
- Router/endpoint verification must be automated
- Build must fail if any tests fail
- Deployment verification must include production URL testing

#### 6.1.3 ACTION Creation Checklist

1. Create directory: `.aicheck/actions/[action-name]/`
2. Create `PLAN.md` with objectives, approach, tests
3. Create `todo.md` (or let AI assistant auto-generate)
4. Update `actions_index.md`
5. Get approval before proceeding

### 6.2 AI Assistant Workflow

**Test-First Pattern**: Human discusses → AI proposes plan/tests → Human approves → AI implements → Human reviews → AI documents

#### 6.2.1 Optimal AI-Human Collaboration Patterns

**Pattern 1: Test-Implementation-Document Cycle**
1. Human defines requirements in ACTION PLAN
2. AI assistant generates comprehensive test suite
3. Human reviews and approves tests
4. AI assistant implements code to pass tests
5. AI assistant updates documentation
6. Human reviews final implementation

**Pattern 2: Incremental Enhancement**
1. Human identifies improvement opportunity
2. AI assistant analyzes current state and proposes enhancement plan
3. Human approves approach
4. AI assistant implements enhancement with tests
5. AI assistant documents changes and integration points

**Pattern 3: Problem-First Development**
1. Human describes problem within ACTION scope
2. AI assistant researches and proposes solution approaches
3. Human selects preferred approach
4. AI assistant develops solution with comprehensive testing
5. AI assistant documents solution and lessons learned

**Pattern 4: Code Review Assistant**
1. Human requests code review for ACTION
2. AI assistant analyzes code against ACTION requirements
3. AI assistant suggests improvements, optimizations, security enhancements
4. Human prioritizes suggestions
5. AI assistant implements approved improvements

#### 6.2.2 Security Guidelines for AI Assistants

When generating security-sensitive code:

1. Never include real credentials in prompts
2. Use example/mock data for sensitive scenarios
3. Request security review for authentication/authorization code
4. Document security assumptions in ai-interactions/
5. Verify generated code against OWASP guidelines
6. Add security-specific tests for all generated auth code

### 6.3 Exec Mode (System Maintenance)

AICheck exec mode provides a special context for system maintenance tasks that don't fit within normal ACTION workflows.

**Purpose**: Handle system maintenance, tooling updates, and administrative tasks without disrupting active ACTION work.

**Usage**:
```bash
./aicheck exec  # Enter exec mode
./aicheck exec  # Exit exec mode (returns to previous action)
```

**Exec Mode Behavior**:
- Saves current active ACTION
- Sets action context to "AICheckExec" 
- Provides clear indication you're in maintenance mode
- Restores previous ACTION when exiting

**Exec Mode Guidelines**:
- Use ONLY for system maintenance, tooling, and administrative tasks
- No substantive code changes should be made in exec mode
- Keep exec mode sessions brief and focused
- Document any significant system changes made
- Exit back to ACTION-based work as soon as maintenance is complete

**Appropriate Exec Mode Tasks**:
- Updating AICheck rules (`./aicheck update`)
- Repository cleanup and organization
- Tooling configuration and setup
- System dependency management
- Administrative documentation updates

**Not Appropriate for Exec Mode**:
- Feature development
- Bug fixes affecting application code
- User-facing functionality changes
- Business logic implementation

### 6.4 Approval Process

All approvals are done by Joshua Field.

### 6.5 Approval Authorities

Joshua Field: Approves all ACTION PLANs and significant changes

#### 6.5.1 Multi-Editor Coordination

When multiple EDITORs work on related ACTIONS:
- Daily sync via shared `.aicheck/session_log_[date].md`
- Integration tests must be co-owned
- Blocking dependencies tracked in `.aicheck/blockers.md`
- Resolution requires joint planning sessions

### 6.6 Git Hook Compliance (Phased Approach)

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

### 6.7 Process Documentation Versioning

All PLANs must include version information:

```markdown
# ACTION: [name]

Version: 1.0
Last Updated: 2025-05-28
Status: ActiveAction
Progress: 45%
```

Major changes require version increment and changelog.

### 6.8 AI-Assisted Migration Process

When migrating documentation or tests:

1. AI: Analyze current location and content
2. AI: Propose migration plan with mappings
3. Human: Review and approve migration plan
4. AI: Execute migration with verification
5. Human: Validate migrated content
6. AI: Update all references

### 6.9 Feature Flag Management

For gradual rollouts:
- Document feature flags in ACTION PLAN
- Test both enabled/disabled states
- Migration plan for flag removal
- Performance impact analysis

### 6.10 Dependency Management

#### 6.10.1 External Dependencies

External dependencies require:
- Security audit documentation
- License compatibility check
- Performance impact assessment
- Fallback plan if dependency fails
- Proper installation documentation

#### 6.10.2 Python Dependency Management

**Poetry Required for Python Projects**:
- All Python projects MUST use Poetry for dependency management
- `pyproject.toml` must specify all dependencies with version constraints
- `poetry.lock` must be committed to ensure reproducible builds
- CI/CD must use `poetry install` to ensure exact dependency versions
- Development dependencies must be separated from production dependencies

**Poetry Setup Requirements**:
```bash
# Install Poetry if not present
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
poetry install

# Run tests
poetry run pytest
```

#### 6.10.3 Node.js Dependency Management

**NPM/Yarn Requirements**:
- `package-lock.json` (npm) or `yarn.lock` must be committed
- CI/CD must use `npm ci` or `yarn install --frozen-lockfile`
- Dev dependencies must be properly categorized

### 6.11 Definition of Done - Production Systems

**CRITICAL**: An ACTION is NOT COMPLETE until production functionality is verified working.

**"Code Complete" vs "Deployed and Working"**:
- ❌ "Code Complete" = Changes written and committed locally
- ❌ "Build Passing" = Tests pass in development environment  
- ✅ "Deployed and Working" = Production system tested and verified functional

**Mandatory Production Verification**:
1. Test the ACTUAL production URL (not localhost)
2. Document the production URL and timestamp tested
3. Capture response/output as evidence
4. Verify all critical endpoints work end-to-end
5. Test error handling in production context
6. Confirm deployment platform settings match expectations

### 6.12 Deployment Verification Checklist

**Deployment Verification Checklist**:
- [ ] Code pushed to correct branch
- [ ] Deployment triggered successfully
- [ ] Build completed without errors
- [ ] Service shows "Live" status
- [ ] Production URL responds correctly
- [ ] All endpoints tested and documented
- [ ] Performance acceptable
- [ ] Logs show no critical errors

**Blueprint vs Manual Deployments**:
- Verify deployment configuration (render.yaml vs dashboard settings)
- Check for cached/stale deployments
- Confirm environment variables are properly set
- Test build and start commands are correct

## 7. Style and Documentation Standards

### 7.1 Documentation Style

Use ATX-style headers, fenced code blocks with language specification. Use bullet points for lists, bold for emphasis. Use PascalCase for Action logical names in discussions, kebab-case for all file and directory names.

.md extension for documentation, -plan.md suffix for action plans (e.g., feature-name-plan.md). 4-space indentation in code. Maintain descriptive names and consistent organization.

Follow documentation structure in documentation/README.md. Separate technical from user-facing documentation. Document configuration files in documentation/configuration/.

### 7.2 AI Assistant Prompt Style

AI assistant prompts MUST:
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

#### 7.3.1 Git Hook Requirements

**Pre-push Hook (MANDATORY)**:
A pre-push hook must be installed in `.aicheck/hooks/` that:
1. Runs the full test suite (`poetry run pytest -q` for Python, `npm test` for Node.js)
2. Verifies all routers/endpoints are properly registered
3. Checks for uncommitted dependency changes
4. Fails the push if any check fails

**Hook Installation**:
```bash
# Install AICheck git hooks
./aicheck hooks install
```

Use predefined status values with progress percentage. Document blockers clearly with timestamps. Create clear error messages with error codes, resolution steps, and appropriate logging.

Example of proper commit message format:
```
Add user authentication module [auth-system]

- Implements JWT-based authentication
- Adds password hashing with bcrypt
- Creates login/logout endpoints
- Includes unit tests for all components
```

## 8. Testing Framework

### 8.1 Test-Driven Development

ACTIONS MUST have tests written before implementation with coverage for:
- Core functionality validation (basic behavior verification)
- Boundary condition tests (validating behavior at threshold values)
- Integration tests with other ACTIONS
- Error handling tests
- Production deployment verification tests

**CI Pipeline Requirements**:
- CI pipelines MUST include a 'Run test suite' step immediately after any build/setup steps
- No Action may skip the test suite execution
- Test failures must block deployment
- Router/endpoint verification must be included in CI

Test data SHOULD be maintained in standard locations and formats. Test fixtures SHOULD be reused across related ACTIONS when appropriate.

#### 8.1.1 Performance Testing Requirements

For ACTIONS affecting system performance:
- Baseline performance tests before implementation
- Performance tests after implementation
- Document performance impact in supporting_docs/performance-impact.md
- Regression tests for critical paths
- AI assistants may suggest performance optimizations with benchmarks

### 8.2 Testing Documentation

Organized into:
- Test Specifications: Inputs, expected outputs, validation criteria
- Testing Strategies: Approaches for different ACTIONS/scenarios
- Test Data Management: Guidelines for test data
- Testing Tools: Documentation of utilities/frameworks
- Test Coverage Reports: Analysis of coverage and gaps

### 8.3 Test Migration Requirements

When tests are migrated, the following requirements MUST be met:

**Migration Plan** must specify:
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

**Directory Structure**:
- Product functionality unit tests → tests/unit/ at the project root
- Integration tests → tests/integration/ at the project root
- E2E tests → tests/e2e/ at the project root
- Process-specific temporary tests → .aicheck/actions/[action-name]/supporting_docs/process-tests/

**Naming Conventions**:
- Test files MUST use the pattern [feature-name].test.[ext] where [ext] is the appropriate extension for the language (e.g., .js, .py, .go)
- Integration test files MUST use the pattern [feature-name].integration.test.[ext]
- E2E test files MUST use the pattern [workflow-name].e2e.test.[ext]

**Organization**:
- Test directory structure SHOULD mirror the code structure being tested
- Shared test utilities → tests/utils/
- Test data → tests/fixtures/

### 8.5 AI Assistant Test Generation

AI assistants MAY be used to generate tests for ACTIONS under the following conditions:

The ACTION PLAN must be thoroughly documented before test generation. AI assistants must be provided with:
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
- AI assistant interactions in ai-interactions/ subfolder
- **MANDATORY: deployment-verification.md for all deployable Actions**

**Product Documentation (/documentation/[CATEGORY]/)**
- System architecture and component descriptions
- Deployment and environment configuration guides
- API references and specifications
- User guides and end-user documentation

**MANDATORY Migration Requirement**:
As part of Action completion, ANY supporting documentation with enduring value (especially deployment-verification.md) MUST be migrated from `.aicheck/` to `/documentation/` to ensure nothing lives only under `.aicheck/` forever.

ACTION documentation MUST be migrated to product documentation directories:
- WHEN the ACTION is completed (MANDATORY for deployment-verification.md)
- WHEN documentation has value beyond the ACTION's scope
- Migration is part of the Action completion checklist

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

Use ESLint with the project's configuration. Prefer TypeScript for new files. Use Jest for testing. Follow Airbnb style guide with modifications. Async/await over promises. Functional programming patterns where appropriate.

### 10.3 Documentation Language

Write in clear, concise English. Use active voice. Avoid jargon without explanation. Include examples for complex concepts. Maintain consistent terminology.

## 11. Implementation Standards

### 11.1 Environment Configuration

Never hard-code credentials or secrets. Use environment variables for configuration. Document all required environment variables. Provide example .env.example file. Support multiple deployment environments.

### 11.2 Error Handling

All errors must include:
- Error code for programmatic handling
- Human-readable message
- Suggested resolution steps
- Context about where the error occurred
- Logging at appropriate level

### 11.3 Dependency Management

Document all dependencies in appropriate manifest. Pin major versions for production dependencies. Regular security audits of dependencies. Graceful degradation for optional dependencies. Clear installation instructions.

## 12. Version Control Best Practices

### 12.1 Branching Strategy

Main branch is always deployable. Feature branches for new ACTIONS. Hotfix branches for urgent fixes. No direct commits to main. All changes through pull requests.

### 12.2 Pull Request Requirements

Reference ACTION in PR title. Tests must pass before merge. Code review required. Update documentation if needed. Clean commit history.

### 12.3 Commit Best Practices

Atomic commits (one logical change). Present-tense imperative mood. Reference ACTION and issue numbers. Explain why, not just what. Sign commits when required.

## 13. Review and Approval Process

### 13.1 Pre-Implementation Review

ACTION PLAN must be reviewed. Test specifications approved. Architecture decisions documented. Security implications considered. Performance impact assessed.

### 13.2 Code Review Focus Areas

Correctness and functionality. Security vulnerabilities. Performance implications. Code maintainability. Documentation completeness. Test coverage.

### 13.3 Post-Implementation Review

All tests passing. Documentation updated. Dependencies documented. Deployment instructions clear. Monitoring in place. **Production verification completed**.

## 14. Continuous Improvement

### 14.1 Retrospectives

Regular ACTION retrospectives. Document lessons learned. Update RULES based on experience. Share knowledge across team. Improve tooling and processes.

### 14.2 Metrics and Monitoring

Track ACTION completion times. Monitor test coverage trends. Measure documentation quality. Analyze error rates. Review performance metrics. **Track deployment verification compliance**.

### 14.3 Tool Development

Create tools to enforce RULES. Automate repetitive tasks. Improve developer experience. Enhance AI assistant integration. Streamline approval processes. **Automate deployment verification checks**.

## 15. Compliance and Governance

### 15.1 Audit Trail

All ACTIONS tracked in index. Decisions documented in PLANs. Changes tracked in version control. Reviews recorded in PRs. Approvals logged appropriately. **Deployment verification documented**.

### 15.2 Security Compliance

Regular security assessments. Dependency vulnerability scanning. Access control reviews. Incident response procedures. Compliance reporting.

### 15.3 Quality Assurance

Code quality metrics. Test coverage requirements. Documentation standards. Performance benchmarks. Accessibility compliance. **Production deployment verification**.

## 16. Exception Handling

### 16.1 Rule Exceptions

Must be documented. Require approval from Joshua Field. Time-limited when possible. Reviewed regularly. Lessons learned captured.

### 16.2 Incident Response

Clear escalation path. Documented in runbooks. Tested regularly. Post-incident reviews. Process improvements. Production verification protocols for urgent fixes.

### 16.3 Technical Debt

Tracked as ACTIONS. Prioritized quarterly. Addressed systematically. Documented thoroughly. Reviewed quarterly.

---

**Document Version**: 5.0
**Last Updated**: 2025-06-07
**Owner**: Joshua Field
**Next Review**: Quarterly

**Version 5.0 Changes**:
- Enhanced ActiveAction definition to clarify only ONE per EDITOR
- Added Section 3.1 "Understanding Actions vs ActiveAction" 
- Renumbered subsequent sections (3.1→3.2, 3.2→3.3, etc.)
- Added deployment verification requirements in multiple sections
- Made language AI-assistant agnostic (not Claude-specific)

**Version 4.0 Changes**:
- Added prominent DEPLOYMENT REQUIREMENTS section at top
- Enhanced deployment verification with comprehensive checklist
- Strengthened "Code Complete" vs "Deployed and Working" distinction
- Added production testing requirements to all relevant sections
- Integrated deployment verification into standard workflows
- Added exec mode documentation for system maintenance
- Enhanced audit and compliance sections with deployment tracking
