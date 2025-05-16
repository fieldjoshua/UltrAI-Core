ICheck Rules
This document is the controlling reference for all work managed by the AICheck system in this PROJECT. These rules cannot be modified without approval from Joshua Field

1. Core Principles
   1.1 Defining the Work
   The PROJECT creates a PROGRAM with specific functions benefiting humanity, built through interrelated ACTIONS performed by EDITORS. Each ACTION is a sub-objective contributing to program functionality.
   An EDITOR's work has value when it progresses an ACTION toward completion. Efficient, quality work increases an EDITOR's value. EDITORS who understand both their current ACTION and its relationship to the PROGRAM will deliver greater value than those with a narrower perspective.
   1.2 Documentation First

PROJECT objective must be clear to all editors
All ACTIONS require their own directory with a documented PLAN before implementation
PLANs require human approval and must detail the ACTION's value to the PROGRAM
PLANs contain all implementation details including testing plans
ACTIONS must be TEST-Driven: tests must be created and approved (via the PLAN.md) before implementation and passed for completion of the ACTION.
Changes to ActiveAction must be reflected in the ACTIONS INDEX and relevant docs
Supporting documentation maintained in the ACTION's supporting_docs directory

Documentation categories:

Process Documentation: Temporary documents during ACTION lifecycle → .aicheck/actions/[action-name]/supporting_docs/
Product Documentation: Enduring documents with relevance beyond ACTION → /documentation/[CATEGORY]/
Process Testing: Tests relevant only during ACTION lifecycle → .aicheck/actions/[action-name]/supporting_docs/process-tests/
Product Testing: Tests with enduring relevance → /tests/[CATEGORY]/

When an ACTION is completed, documentation with enduring value must be migrated to the appropriate /documentation/ subdirectory.

1.3 Development Guidelines

Each team member may work on one ActiveAction at a time; complete or pause before switching
The PROJECT may have multiple concurrent ActiveActions assigned to different team members

Follow AICheck directory structure and naming conventions
Update action status and document progress regularly
Follow language-specific best practices
Implement graceful degradation for optional dependencies
Use Docker-based development when available, with documented alternatives when not available
Document all environment variables and configuration options
Implementation procedures should reside within the Action's Plan

1.4 Claude Code Integration
Claude Code functions as an AI engineer within the AICheck workflow, complementing human editors while respecting our documentation-first approach and action-based governance requirements.
Capabilities

Generate implementation code from PLAN specifications
Create comprehensive test suites following test-driven methodology
Provide code review and optimization suggestions
Enhance/generate documentation based on implementation details
Assist with migrations and refactoring
Support debugging complex issues

Integration Requirements

Start with TEST-Driven approach (generate tests before implementation)
Reference specific sections of RULES.md in prompts
Include relevant directory paths and documentation links
Provide contextual examples of existing patterns
Verify outputs against action requirements
Document all Claude interactions in ACTION's supporting_docs
Use standardized prompt templates stored in .aicheck/templates/claude/

2. Glossary and Key Concepts
   Before proceeding, it is essential to understand the following key terms as used throughout this document:
   2.1 Core Terminology

PROJECT: The overall software development initiative governed by these rules; a long-running collaborative effort with defined objectives, teams, and governance structures.
PROGRAM: The software product being built by the PROJECT; the actual executable system that will be deployed and used by end-users.
ACTION: A discrete unit of work that contributes to the PROGRAM; has clear boundaries, objectives, and completion criteria. An ACTION is the atomic unit of work assignment and tracking.
EDITOR: Any human or AI contributor who performs work on ACTIONS; includes developers, writers, designers, and Claude Code.
PLAN: A documented specification for an ACTION; includes requirements, approach, expected outcomes, and testing strategy.
ActiveAction: An ACTION that is currently being worked on by one or more EDITORs; tracked in .aicheck/current_action for individual EDITORs.
Process Documentation: Temporary documentation relevant only during an ACTION's lifecycle; stored in the ACTION's supporting_docs directory.
Product Documentation: Documentation with enduring relevance beyond ACTION completion; stored in the centralized documentation directory.

2.2 Workflow Terminology

Test-Driven Development (TDD): Development approach where tests are written before implementation code; ensures functionality is well-defined and verifiable.
Documentation-First: Principle that documentation should be created or updated before code, ensuring clear understanding of objectives.
Quick Response: Limited exception to standard processes for urgent operational issues; still requires minimal planning and test-first approach.
Action Lifecycle: The standard progression of an ACTION from creation through planning, implementation, testing, and completion.

2.3 System Components

AICheck System: The tooling, processes, and rules that govern the PROJECT's development workflow.
Claude Code: AI-powered assistant that helps implement ACTIONS following the project's guidelines.
Supporting Documents: Auxiliary files associated with an ACTION; stored in the ACTION's supporting_docs directory.
Process Tests: Tests specific to an ACTION that are not intended to be part of the long-term test suite.
Product Tests: Tests with enduring value that are maintained as part of the PROGRAM's test suite.

3. Action Management
   3.1 AI Editor Scope
   AI editors may implement without approval:

Code implementing the ActiveAction plan (after PLAN approval)
Documentation updates for ActiveAction
Bug fixes and tests within ActiveAction scope
Refactoring within ActiveAction scope

The following ALWAYS require human manager approval:

Changing the ActiveAction
Creating a new Action
Making substantive changes to any Action
Modifying any Action Plan
Creating or modifying Templates

### 3.1.1 Claude Code Boundary Examples

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

  3.2 Documentation Requirements

Action plan (PLAN.md)
Supporting documentation
Status updates (Not Started, ActiveAction, Completed, Blocked, On Hold)

### 3.2.1 Managing ACTION Dependencies

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

3.3 Claude Code Documentation
All Claude Code interactions MUST:

Be stored in .aicheck/actions/[action-name]/supporting_docs/claude-interactions/
Reference specific sections of the ACTION's PLAN
Include the complete prompts used to generate code or solutions
Document any modifications made to Claude-generated content
Include verification steps performed on Claude-generated outputs
Note iterations or refinements to prompts

### 3.3.1 Claude Interaction Documentation Format

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

4. Project Structure and Organization
   4.1 Directory Structure
   /
   ├── documentation/ # Centralized documentation (single source of truth)
   │ ├── technical/ # Technical implementation details
   │ │ ├── claude/ # Claude integration documentation
   │ │ └── maintainers.yaml # List of technical leads with approval authority
   │ ├── public/ # User-facing documentation
   │ ├── planning/ # Strategic planning documents
   │ ├── vision/ # High-level vision documents
   │ ├── architecture/ # System design documents
   │ ├── research/ # Background research
   │ ├── operations/ # Deployment & operations
   │ ├── implementation/ # Implementation details
   │ ├── deliverables/ # Completion records
   │ ├── status_updates/ # Periodic status reports
   │ ├── legal/ # Legal documents
   │ ├── governance/ # Governance documentation
   │ │ └── board.md # Project Governance Board membership
   │ └── configuration/ # Configuration documentation
   ├── src/ # Source code (primary code location)
   │ ├── frontend/ # Frontend code
   │ │ └── demos/ # Frontend demos
   │ └── backend/ # Backend services
   ├── data/ # Data resources
   │ └── images/ # Image resources
   ├── scripts/ # Utility scripts
   │ └── local/ # Local environment setup scripts
   ├── tests/ # Test suites
   │ ├── unit/ # Unit tests for product code
   │ ├── integration/ # Integration tests
   │ ├── e2e/ # End-to-end tests
   │ ├── utils/ # Shared test utilities
   │ └── fixtures/ # Test data
   └── .aicheck/ # AICheck system
   ├── actions/ # Action-specific directories
   │ └── [action-name]/
   │ ├── [action-name]-plan.md
   │ └── supporting_docs/
   │ ├── process-tests/ # Process-specific tests
   │ └── claude-interactions/ # Claude Code interaction documents
   ├── cursor/ # Cursor-specific configurations
   ├── docs/ # AICheck internal documentation
   ├── hooks/ # Git hooks
   ├── insights/ # AI-generated insights
   ├── sessions/ # AI session data
   ├── scripts/ # AICheck scripts
   ├── templates/ # Template files
   │ └── claude/ # Claude prompt templates
   └── claude/ # Claude configuration files
   4.2 Code Structure Clarification
   The /src directory is the primary location for all code in the project. Both frontend and backend code are contained within this directory, following this structure:

/src/frontend/: All client-side code
/src/backend/: All server-side code

This structure ensures all code is built, tested, and deployed using consistent tooling and processes. Teams must adhere to this structure, and CI checks will enforce this organization.
4.3 Documentation Structure Clarification
The /documentation directory is the single source of truth for all product documentation. The .aicheck/docs directory contains only AICheck system-specific internal documentation and should not be used for product documentation. After an ACTION is completed, any documentation with enduring value must be migrated from the ACTION's supporting_docs to the appropriate /documentation subdirectory.
4.4 Claude Template Structure
.aicheck/
└── templates/
└── claude/
├── README.md # Template documentation
├── action-implementation/ # Implementation templates
│ ├── basic.md # Standard implementation template
│ └── [specific-patterns].md # Templates for specific patterns
├── testing/ # Templates for test generation
│ ├── unit-tests.md # Unit test generation template
│ ├── integration-tests.md # Integration test template
│ └── e2e-tests.md # End-to-end test template
├── documentation/ # Documentation generation templates
│ ├── action-docs.md # ACTION documentation template
│ └── api-docs.md # API documentation template
├── code-review/ # Code review templates
│ ├── security-review.md # Security review template
│ └── performance-review.md # Performance review template
└── migration/ # Migration assistance templates
├── code-migration.md # Code migration template
└── test-migration.md # Test migration template

### 4.4.1 Template Version Control

All Claude templates must include:

- Version header (e.g., `<!-- Template Version: 1.2 -->`)
- Last updated date
- Change log in template directory README.md
- Backwards compatibility notes
- Migration guide for major version changes

Example:

```markdown
<!-- Template Version: 1.2 -->
<!-- Last Updated: 2025-05-16 -->
<!-- Changes: Added error handling section -->
```

4.5 Critical Files

RULES.md: This document (controlling reference)
.aicheck/docs/actions_index.md: Action tracking
.aicheck/current_action: ActiveAction tracking (currently assigned actions)
.aicheck/current_session: Current session tracking
documentation/README.md: Documentation organization reference
CLAUDE.md: Claude Code integration configuration
.aicheck/templates/claude/README.md: Claude template documentation
documentation/technical/maintainers.yaml: List of technical leads with approval authority
documentation/governance/board.md: Project Governance Board membership

5. Workflow and Processes
   5.1 Standard AICheck Workflow

Start sessions with ./ai start and end with meaningful summaries
Check status with ./ai status and generate prompts with ./ai prompt
Create, update, and audit Actions with appropriate commands
Verify context and compliance before starting work

5.2 Claude Code Workflow
Standard Claude Code workflow:

Planning: Document ACTION thoroughly in [action-name]-plan.md
Test Generation: Use Claude Code to create tests based on the PLAN
Test Approval: Get tests reviewed and approved via pull request or explicit approval tag
Implementation Planning: Use Claude Code to outline implementation approach
Implementation: Use Claude Code to assist with code implementation
Verification: Verify the implementation against the tests and PLAN
Documentation: Update documentation with implementation details
Review: Conduct human review of the completed implementation

Use Claude with ./ai claude [command]:

prompt [template]: Generate prompt from template
verify [file]: Verify generated content
document [file]: Document interactions

### 5.2.1 Optimal Claude-Human Collaboration Patterns

**Pattern 1: Test-Implementation-Document Cycle**

1. Human: Discuss needs for ACTION
2. Claude: Generate ACTION directory, propose PLAN and comprehensive tests
3. Human: Review and approve PLAN and tests
4. Claude: Implement code to pass tests
5. Human: Review implementation
6. Claude: Generate/update documentation
7. Human: Final review and approval

**Example Flow:**

```
Human: "We need error handling for LLM provider failures"
Claude: Creates:
  - .aicheck/actions/ErrorHandlingImplementation/
  - ErrorHandlingImplementation-PLAN.md (with phases, timeline, specs)
  - supporting_docs/process-tests/test_llm_failures.py
Human: "Approved with minor changes to error codes"
Claude: Updates tests, implements ErrorHandler class
Human: "Add circuit breaker pattern"
Claude: Implements circuit breaker, updates tests and docs
Human: "Approved for completion"
```

**Pattern 2: Incremental Enhancement**

1. Human: Request specific enhancement to existing code
2. Claude: Analyze current implementation
3. Claude: Propose enhancement approach with tests
4. Human: Approve approach
5. Claude: Implement enhancement
6. Human: Review and iterate
7. Claude: Update all affected documentation

**Pattern 3: Problem-First Development**

1. Human: Describe problem or bug
2. Claude: Reproduce and analyze issue
3. Claude: Propose solution with test cases
4. Human: Approve solution approach
5. Claude: Implement fix with tests
6. Human: Verify fix resolves issue
7. Claude: Document resolution

**Pattern 4: Code Review Assistant**

1. Human: Submit code for review
2. Claude: Analyze for security, performance, style
3. Human: Address concerns
4. Claude: Verify fixes
5. Document review in supporting_docs/

### 5.2.2 Security Guidelines for Claude Code

When using Claude for security-sensitive code:

1. Never include real credentials in prompts
2. Use example/mock data for sensitive scenarios
3. Request security review for authentication/authorization code
4. Document security assumptions in claude-interactions/
5. Verify generated code against OWASP guidelines
6. Add security-specific tests for all generated auth code

5.3 Quick Response (Emergency Fix) Protocol

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

5.4 Approval Process
All approvals are done by Joshua Field
5.5 Approval Authorities

All approvals must be recorded through:

GitHub/GitLab pull request approval mechanisms
Explicit approval comments referencing the relevant ACTION
Digital signatures on critical changes
Recorded votes for Governance Board decisions

5.6 Git Hook Compliance (Phased Approach)

To ensure practical adoption of AICheck standards while maintaining development velocity, git hooks are implemented in phases:

**Phase 1 (Required - Implemented)**:

- Commit message format validation (50-char subject, present tense)
- ACTION directory structure validation for new ACTIONS
- Basic security checks (existing pre-commit)
- File format validation (JSON, YAML)

**Phase 2 (Required - Implemented)**:

- Test existence verification for implementation changes
- Basic documentation completeness checks
- Status file validation (.aicheck/current_action)
- ACTION reference in commit messages

**Phase 3 (Future - Not Required)**:

- Claude interaction logging automation
- Full PLAN approval workflow integration
- Comprehensive migration tracking
- Automated documentation migration

6. Style and Documentation Standards
   6.1 Documentation Style

Use ATX-style headers, fenced code blocks with language specification
Use bullet points for lists, bold for emphasis
Use PascalCase for Action logical names in discussions, kebab-case for all file and directory names
.md extension for documentation, -plan.md suffix for action plans (e.g., feature-name-plan.md)
4-space indentation in code
Maintain descriptive names and consistent organization
Follow documentation structure in documentation/README.md
Separate technical from user-facing documentation
Document configuration files in documentation/configuration/

6.2 Claude Code Prompt Style
Claude Code prompts MUST:

Reference specific sections of RULES.md in prompts (using correct capitalization)
Include directory structure information
Reference documentation sources
Provide example output formats
Specify verification criteria
Use consistent formatting with clear sections
End with explicit output expectations

6.3 Commit and Status Practices

Write commit messages that begin with a present-tense verb
Keep commit message subject lines under 50 characters (hard limit)
Use the extended commit body for any content beyond the 50-character limit
Include action reference in a standardized format (e.g., [action-name])
For longer descriptions, use the commit body separated by a blank line
Wrap commit message body text at 72 characters
Use predefined status values with progress percentage
Document blockers clearly with timestamps
Create clear error messages with error codes, resolution steps, and appropriate logging

Example of proper commit message format:
Add user authentication module [auth-system]

- Implements JWT-based authentication
- Adds password hashing with bcrypt
- Creates login/logout endpoints
- Includes unit tests for all components

7. Testing Framework
   7.1 Test-Driven Development
   ACTIONS MUST have tests written before implementation with coverage for:

Core functionality validation (basic behavior verification)
Boundary condition tests (validating behavior at threshold values)
Integration tests with other ACTIONS
Error handling tests

Test data SHOULD be maintained in standard locations and formats.
Test fixtures SHOULD be reused across related ACTIONS when appropriate.

### 7.1.1 Performance Testing Requirements

For ACTIONS affecting system performance:

- Baseline performance tests before implementation
- Performance tests after implementation
- Document performance impact in supporting_docs/performance-impact.md
- Regression tests for critical paths
- Claude may suggest performance optimizations with benchmarks
  7.2 Testing Documentation
  Organized into:

Test Specifications: Inputs, expected outputs, validation criteria
Testing Strategies: Approaches for different ACTIONS/scenarios
Test Data Management: Guidelines for test data
Testing Tools: Documentation of utilities/frameworks
Test Coverage Reports: Analysis of coverage and gaps

7.3 Test Migration Requirements
When tests are migrated, the following requirements MUST be met:

Migration Plan must specify:

Source and destination test locations
Timeline with discrete phases (parallel testing, validation, cutover)
Verification methods for maintaining test coverage
Rollback procedures if issues are detected

Coverage Verification - Test coverage MUST NOT decrease during migration:

Pre-migration coverage metrics MUST be documented
Post-migration coverage MUST meet or exceed pre-migration levels
Any reduction in coverage MUST be explicitly justified and approved

Parallel Testing Period - During transition, both old and new test implementations MUST be maintained until:

Three consecutive successful CI runs have been completed with both test suites
All test coverage metrics show equal or improved coverage
Technical Lead has explicitly approved the retirement of legacy tests
A one-week observation period has passed with no regressions

Version Alignment - Test versions MUST align with the ACTIONS they validate, maintaining traceability

7.4 Test Location Specifications

Directory Structure:

Product functionality unit tests → tests/unit/ at the project root
Integration tests → tests/integration/ at the project root
E2E tests → tests/e2e/ at the project root
Process-specific temporary tests → .aicheck/actions/[action-name]/supporting_docs/process-tests/

Naming Conventions:

Test files MUST use the pattern [feature-name].test.[ext] where [ext] is the appropriate extension for the language (e.g., .js, .py, .go)
Integration test files MUST use the pattern [feature-name].integration.test.[ext]
E2E test files MUST use the pattern [workflow-name].e2e.test.[ext]

Organization:

Test directory structure SHOULD mirror the code structure being tested
Shared test utilities → tests/utils/
Test data → tests/fixtures/

7.5 Claude Code Test Generation
Claude Code MAY be used to generate tests for ACTIONS under the following conditions:

The ACTION PLAN must be thoroughly documented before test generation
Claude Code must be provided with:

Specific ACTION requirements and success criteria
Expected inputs and outputs
Boundary conditions and edge cases
Integration points with other ACTIONS

Generated tests MUST be validated against the ACTION PLAN
Generated tests MUST follow the project's testing standards and patterns
Any manual modifications to generated tests MUST be documented

8. Documentation Organization
   8.1 Documentation Types and Locations

ACTION Process Documentation (.aicheck/actions/[action-name]/supporting_docs/)

Implementation details specific to ACTION
Research notes, experiments, progress tracking
Design worksheets, ACTION-specific planning
Claude Code interactions in claude-interactions/ subfolder

Product Documentation (/documentation/[CATEGORY]/)

System architecture and component descriptions
User guides and API references
Standards, patterns, best practices
Configuration and deployment guides
Reusable Claude Code prompt templates

Testing Documentation and Code

Process Testing: .aicheck/actions/[action-name]/supporting_docs/process-tests/

Tests relevant only during ACTION lifecycle
Temporary test fixtures and data

Product Testing: /tests/[CATEGORY]/

Enduring tests beyond ACTION completion
Testing configuration and guides
Reusable test fixtures and utilities

### 8.1.1 Documentation Quality Checklist

All documentation must:

- [ ] Include creation date and last modified date
- [ ] Have clear purpose statement in first paragraph
- [ ] Use consistent formatting per style guide
- [ ] Include examples for complex concepts
- [ ] Define any ACTION-specific terminology
- [ ] Link to related documentation
- [ ] Pass grammar and spell check
- [ ] Be reviewed by at least one other team member

  8.2 Documentation Migration
  When an ACTION is completed:

Evaluate all documentation for enduring value
Prepare documents for migration by:

Updating ACTION-specific terminology
Ensuring completeness and accuracy
Adding appropriate metadata

Move relevant documents to appropriate /documentation/ and /tests subdirectories
Update references and documentation indexes
Note migrations in ACTION completion record

A complete Documentation Migration Checklist can be found in documentation/technical/processes/documentation_migration.md

### 8.2.1 Migration Rollback Protocol

All migrations must include:

1. Rollback procedure documentation
2. Data backup before migration
3. Validation checks post-migration
4. Automated rollback triggers
5. Communication plan for failed migrations

Store in supporting_docs/rollback-procedures.md 9. Development Environment
9.1 Development Environment Options
Docker-Based Development

Docker Compose is the recommended method for local development
All service dependencies should be defined in docker-compose.yml
Environment variables should be sourced from .env.example with secure defaults
Volume mounts should preserve data between container restarts
Development and production environments should be as similar as possible

Non-Docker Alternatives

Local development without Docker MUST be documented in documentation/technical/local_setup.md
Alternative setup instructions must include all required dependencies and configuration steps
Scripts for local environment setup should be provided in the scripts/local/ directory
Environment variable handling must be consistent across Docker and non-Docker environments

9.2 Dependency Management

Required dependencies must be documented in requirements.txt or package.json
Optional dependencies must be clearly marked in documentation
Code must implement graceful degradation for optional dependencies
Dependency version ranges should be specified to ensure compatibility
Security vulnerabilities must be regularly checked and addressed

10. AI Editor Philosophy
    YOU ARE A WORLD CLASS SOFTWARE ENGINEER WHO IS PROUD TO WORK WITH HUMAN EDITORS OF ALL ABILITIES:

Analyze Context First

Identify language, frameworks, patterns, constraints
Request missing critical context before coding
Never assume technical details

Structure Problem Solving

Restate problem to confirm understanding
Break problems into components
Consider edge cases first
Outline approach before details

Implement Robust Error Handling

Handle exceptions specifically
Validate all inputs at boundaries
Provide meaningful error messages
Ensure proper resource cleanup
Document error conditions

Code Securely By Default

Sanitize all user inputs
Parameterize queries
Avoid insecure functions
Apply authentication checks
Use secure defaults

Address Performance Proactively

Provide complexity analysis
Avoid inefficient patterns
Consider memory usage
Optimize critical paths
Document limitations

Write Self-Documenting Code

Use descriptive names
Follow language conventions
Structure with logical separation
Document public interfaces
Comment complex logic only

Explain Implementation Decisions

Justify approach selection
Describe trade-offs
State assumptions
Suggest improvements

Include Testing Approaches

Provide unit tests
Cover edge cases
Show integration examples
Explain limitations

Reference Sources Properly

Cite complex implementation sources
Reference official documentation
Distinguish standard vs. opinionated approaches

Follow Language Idioms

Use native patterns
Apply best practices
Leverage language features
Conform to style guides

Build Solutions Progressively

Start with basic implementation
Add enhancements incrementally
Explain each enhancement
Allow complexity choice

Provide Integration Context

Explain system integration
Highlight challenges
Show calling examples
List dependencies

Consider Cross-Cutting Concerns

Address logging needs
Consider monitoring
Handle internationalization
Mention deployment

Flag Limitations Clearly

Identify unhandled edge cases
Note performance constraints
Highlight security considerations
Acknowledge compromises

Match User's Expertise

Explain non-obvious patterns
Skip basics
Support learning without condescension
Provide actionable guidance

Version
Version: 2.1
Last Updated: 2025-05-16
