# UltraAI Documentation Guidelines

This document establishes the core standards and rules for all UltraAI Framework documentation. These guidelines ensure consistency, clarity, and maintainability across our documentation.

## Documentation Authority Hierarchy

### Controlling Documents

The UltraAI Framework is governed by two controlling documents that have ultimate authority over all aspects of the project:

1. **Controlling_README.md** - Serves as the authoritative source for:
   - Project overview and purpose
   - High-level architecture
   - Core functionality
   - Getting started instructions
   - All statements in this document take precedence over any conflicting information in other documents

2. **Controlling_GUIDELINES.md** (this document) - Serves as the authoritative source for:
   - All documentation standards and rules
   - Project process requirements
   - Implementation approach
   - Plan governance
   - All rules in this document must be followed without exception

### Authority Enforcement

- Any content that conflicts with these controlling documents must be updated to align with them
- Proposed changes to the controlling documents require special approval
- When in doubt about any project aspect, these controlling documents should be consulted first
- Plans and other documentation derive their authority from these controlling documents

## Documentation Philosophy

UltraAI follows a **documentation-first** approach where:

1. Documentation serves as the single source of truth
2. Implementation follows documentation, not vice versa
3. Documentation changes precede code changes
4. All documentation is organized around plans

## Plan-Centric Organization

### Core Principle

All documentation is organized around **plans**, which represent discrete areas of functionality or development initiatives. This structure ensures that all documentation related to a specific feature or component is co-located and comprehensive.

### Structure Rules

```
project_root/
├── Actions/                     # Action plans and implementation
│   ├── API_DEVELOPMENT/         # Implementation plan for API Development
│   ├── BACKEND_INTEGRATION/     # Implementation plan for Backend Integration
│   └── [Other Actions]/         # Other action plans
├── documentation/               # Core documentation
│   ├── Controlling_README.md    # Project overview
│   ├── Controlling_GUIDELINES.md # This file - documentation standards and rules
│   ├── ACTIONS_INDEX.md         # Dashboard of all actions
│   ├── Templates/               # Templates for documentation
│   └── OLD_to_review/           # Legacy content to be migrated
├── frontend/                    # Frontend application code
├── backend/                     # Backend application code
├── src/                         # Core application code
└── tests/                       # Test suite
```

### Implementation Plan Directory Structure

Each implementation plan directory must contain:

1. **PLAN.md** - The main plan document following the PLAN_TEMPLATE
2. Additional documentation specific to that action, which may include:
   - Technical specifications
   - API documentation
   - Implementation guides
   - Workflow documents
   - Reference materials

### Supporting Documents Within Plans

Supporting documents within plan directories must adhere to these rules:

1. Each supporting document must follow an appropriate template from the Templates directory
2. If the document is implementing a specific activity outlined in the plan, it should reference the relevant section of the PLAN.md
3. Supporting documents should be named according to their purpose and the appropriate template (e.g., TECHNICAL_SPECIFICATION.md, API_REFERENCE.md)
4. Documents that don't match an existing template should follow the general formatting guidelines and clearly indicate their purpose
5. All supporting documents must be referenced from the main PLAN.md file in the "Plan Documents" section

### Plan-Attached Resources

Plans may include additional resources to support implementation, research, and development in the following structured manner:

1. **Research Materials**
   - Create a `Research/` subdirectory within the plan directory
   - Include research findings, market analysis, competitive reviews, etc.
   - Follow the RESEARCH_FINDINGS_TEMPLATE.md when applicable
   - All research must be referenced from the main PLAN.md

2. **Draft Code and Prototypes**
   - Create a `Prototypes/` subdirectory within the plan directory
   - Include proof-of-concept code, prototypes, and draft implementations
   - Include a README.md explaining the purpose and status of each prototype
   - Prototypes must be clearly marked as non-production code
   - All prototype code must be referenced from the main PLAN.md

3. **Design Resources**
   - Create a `Design/` subdirectory within the plan directory
   - Include wireframes, mockups, diagrams, and other design artifacts
   - Use descriptive filenames and include a README.md explaining the design resources
   - All design resources must be referenced from the main PLAN.md

## Document Types and Templates

All UltraAI documentation falls into these primary categories:

1. **Plans** - Core organizing documents (PLAN_TEMPLATE.md)
   - All substantive work must be documented as a plan
   - Plans include objectives, approach, timeline, and success criteria
   - Each plan has its own directory containing all related supporting documents

2. **Guidelines** - Rules and standards (GUIDELINE_TEMPLATE.md)
   - Establish rules for project operations
   - Define standards for development and documentation

3. **Plan-Specific Supporting Documents**
   - Documents that support specific plans only
   - Located in the plan's directory
   - May include:
     - Comparisons - For evaluating options (uses COMPARISON_TEMPLATE.md)
     - Reports - Analysis and findings
     - Implementation details
     - Technical specifications
   - Named to indicate the parent plan (e.g., PLAN_NAME_comparison.md)

4. **Templates** - Format definitions for creating documents
   - Used to ensure consistency across documentation
   - Each template defines required sections and formatting

5. **Controlling Documents**
   - Controlling_README.md - Single source of truth for project overview
   - Controlling_GUIDELINES.md - Authoritative rules for documentation
   - ACTIONS_INDEX.md - Master index of all active actions

6. **Additional Documentation Elements**
   - Must be stored within the relevant action directory
   - **Reference Materials** - API references, data dictionaries
   - **Assets** - Diagrams, images, and other media (stored in action-specific `/assets` subdirectory)
   - **Configuration** - Documentation-related configuration files (if needed)
   - Example: `Actions/API_DEVELOPMENT/assets/architecture_diagram.png`

All documentation must be categorized into one of these types and follow the appropriate template and location guidelines. No documentation should exist outside of this structure except for the Controlling Documents at the root level and archived content in the OLD_to_review directory.

## Documentation Structure Options

The UltraAI project uses a distributed documentation organization approach:

### Distributed Documentation Structure

```
project_root/
├── Actions/                       # Action plans and implementation
│   ├── ACTION_NAME/               # Directory for each action
│   │   ├── PLAN.md                # The plan document
│   │   ├── assets/                # Action-specific assets
│   │   └── [Supporting documents] # All action-specific documentation
├── documentation/
│   ├── Controlling_README.md      # Comprehensive project overview
│   ├── Controlling_GUIDELINES.md  # Documentation standards and rules
│   ├── ACTIONS_INDEX.md           # Dashboard for all actions
│   ├── Templates/                 # Templates for documentation
│   └── OLD_to_review/             # Legacy content to be migrated
├── frontend/                      # Frontend application code
├── backend/                       # Backend application code
├── src/                           # Core application code
└── tests/                         # Test suite
```

### Plan Location Requirements

Regardless of which structure is chosen:

1. All plans must be listed in the central ACTIONS_INDEX.md
2. Each plan must have its own directory containing the PLAN.md file and all supporting documentation
3. All plans must follow the same template and organizational structure
4. Supporting documentation must still be stored within its plan directory

## Naming Conventions

### File Names

- All documentation file names should be in UPPER_SNAKE_CASE
- File extensions should be `.md` for all documentation
- File names should clearly indicate content (e.g., `API_REFERENCE.md`, not `DOCS.md`)

### Directory Names

- Action directories should be in UPPER_SNAKE_CASE
- Action names should reflect the functional area (e.g., `API_DEVELOPMENT`)

## Formatting Standards

### Markdown Usage

- Use standard Markdown for all documentation
- Top-level heading (# Title) should be used only once per document
- Sections should start at level 2 (## Section)
- Maximum nesting to level 4 (#### Subsection)
- Use inline code formatting for code references, commands, and file paths
- Use code blocks with language specifiers for multi-line code examples

### Style Guidelines

- Use clear, concise language
- Write in the present tense
- Use active voice when possible
- Define acronyms on first use
- Include example code when applicable
- Use numbered lists for sequential steps
- Use bullet points for non-sequential items

## Cross-Referencing

- Use relative links when referencing other documents within the repository
- Begin all relative links from the location of the current document
- Always use the format `[descriptive text](path/to/file.md)`
- Include section references where appropriate: `[descriptive text](path/to/file.md#section-id)`

## Documentation Review Process

All documentation changes should follow this review process:

1. **Self-review**: Ensure the document follows these guidelines
2. **Peer review**: Another team member reviews for clarity and correctness
3. **Integration check**: Verify all cross-references and links
4. **Approval**: Final approval from documentation owner
5. **Publication**: Merge into the main branch

## Templates Usage

Templates are located in the Templates/ directory and serve as the foundation for creating consistent documentation. To use a template:

1. Copy the template to the appropriate location
2. Rename according to the naming conventions
3. Fill in all sections marked with [PLACEHOLDER]
4. Remove any template instructions (usually in italics or comments)
5. Update the table of contents if present

## Plan Development and Approval Process

### Mandatory Plan-Based Implementation

1. **All project work must follow the plan-based approach**
   - Any significant action, feature implementation, or system change requires a formal plan
   - Ad-hoc changes or implementations without an approved plan are prohibited
   - Emergencies may have expedited plan approval but still require documentation

2. **Plan Approval Requirements**
   - All plans must be documented using the PLAN_TEMPLATE
   - Plans must be reviewed and approved before implementation begins
   - Approval must include sign-off from the plan owner, technical reviewer, and stakeholder
   - Approved plans must be added to the ACTIONS_INDEX.md

### Initial Plan Review Process

The first mandatory step when creating any new plan is to conduct a thorough review to:

1. **Verify Plan Novelty**
   - Confirm the plan doesn't duplicate existing or completed work
   - Review ACTIONS_INDEX.md to identify potentially similar initiatives
   - Check the archive for previously completed related work

2. **Evaluate Impact on Active Plans**
   - Identify any overlap with currently active plans
   - Assess dependencies and potential conflicts
   - Consult with owners of potentially affected plans
   - Document all identified relationships in the "Related Documentation" section

3. **Resolution of Conflicts**
   - If conflicts are found, they must be resolved before plan approval
   - Options include: merging plans, redefining scope, or establishing clear interfaces
   - For unresolvable conflicts, escalate to project leadership

## Code Changes and Implementation Process

### Relationship Between Plans and Code

All code changes must be tied to an approved plan following these principles:

1. **Plan-First Development**
   - No code changes should be made without a corresponding approved plan
   - Plans must describe the intended code changes at an appropriate level of detail
   - Code changes must align with the technical specifications in the plan

2. **Code Implementation Documentation**
   - Create an `Implementation/` subdirectory within the plan directory
   - Document the actual implementation details using CODE_IMPLEMENTATION.md template
   - Track deviations from the original plan and their justifications
   - Document testing approaches and results

### Managing Changes to Active Code

When making changes to active code, follow this process:

1. **Code Change Scope**
   - Create a CODE_CHANGE_SCOPE.md document in the plan's Implementation directory
   - Clearly identify all files and components that will be modified
   - Define the boundaries of the change to prevent scope creep
   - Reference existing code structure and dependencies

2. **Implementation Tracking**
   - Document each significant code change in the Implementation directory
   - Use the format: `IMPLEMENTATION_[component]_[date].md`
   - Include before/after code snippets for critical changes
   - Reference commit IDs or pull requests where changes were implemented

3. **Review and Validation**
   - Document the review process for code changes
   - Include test results and validation approaches
   - Reference the criteria from the plan used to evaluate success
   - Note any follow-up actions or issues discovered during implementation

### Post-Implementation Documentation

After code changes are complete:

1. Update the plan status to reflect completion
2. Create a LESSONS_LEARNED.md document in the Implementation directory
3. Update relevant technical documentation to reflect the new code state
4. Create or update relevant API documentation if interfaces were changed
5. Update the plan's success criteria evaluation

## Additional Governed Actions

### Deprecation and Removal Procedures

When removing or deprecating features, APIs, or components:

1. **Deprecation Plan Requirement**
   - Create a formal DEPRECATION_PLAN.md in the relevant plan directory
   - Document the rationale for deprecation
   - Define the timeline for deprecation and eventual removal
   - Identify all affected components and documentation

2. **Notification Requirements**
   - Document the process for notifying users of deprecation
   - Create migration guides for affected users
   - Update all relevant documentation to indicate deprecation status

3. **Code and Documentation Cleanup**
   - Document the process for removing deprecated features
   - Require updates to all affected documentation
   - Define testing requirements to ensure removal doesn't break functionality

### Emergency and Hotfix Procedures

For urgent changes that cannot wait for the standard plan approval process:

1. **Emergency Authorization**
   - Define the criteria that constitute an emergency
   - Document the expedited approval process
   - Identify authorized approvers for emergency changes
   - Require post-implementation documentation

2. **Hotfix Documentation**
   - Create a HOTFIX.md document in the affected plan directory
   - Document the issue, solution, and implementation
   - Reference all affected code and documentation
   - Include validation and verification steps

3. **Post-Emergency Review**
   - Require a review of emergency changes within one week
   - Document lessons learned to prevent future emergencies
   - Update plans and documentation to reflect changes
   - Ensure proper testing and validation after the fact

### Cross-Plan Coordination

When changes span multiple plan areas:

1. **Coordination Requirements**
   - Create a COORDINATION_PLAN.md in each affected plan directory
   - Designate a primary plan with coordination authority
   - Define interfaces and boundaries between plans
   - Document dependencies and sequencing requirements

2. **Joint Reviews**
   - Require joint review sessions with stakeholders from all affected plans
   - Document decisions in a shared JOINT_DECISIONS.md file
   - Ensure consistent implementation across plans
   - Define a dispute resolution process for conflicting requirements

3. **Integrated Testing**
   - Define integrated testing requirements across plan boundaries
   - Document test scenarios that cross plan boundaries
   - Assign responsibility for integration tests
   - Require sign-off from all affected plan owners

### API and Interface Management

For changes to public or internal APIs and interfaces:

1. **Interface Change Control**
   - Require an API_CHANGE_PLAN.md for any interface modifications
   - Document backward compatibility considerations
   - Define versioning strategy for APIs
   - Include migration guidance for API consumers

2. **API Documentation Standards**
   - Follow the API_DOCUMENTATION_TEMPLATE.md for all interfaces
   - Include example usage, parameter definitions, and response formats
   - Document error cases and handling
   - Maintain a changelog of API modifications

3. **Breaking Change Management**
   - Explicitly identify breaking vs. non-breaking changes
   - Require higher level of approval for breaking changes
   - Define minimum notification period for breaking changes
   - Document migration paths and compatibility shims

### External Dependency Management

When adding or updating third-party dependencies:

1. **Dependency Approval Process**
   - Create a DEPENDENCY_REQUEST.md document
   - Include evaluation of license, support, security, and maintenance
   - Require security review for external dependencies
   - Document the business justification for the dependency

2. **Dependency Documentation**
   - Maintain a DEPENDENCIES.md file in the relevant plan
   - Document version requirements and compatibility constraints
   - Include upgrade and downgrade procedures
   - Document known issues and workarounds

3. **Vendor Documentation Integration**
   - Define how external vendor documentation should be referenced
   - Establish archiving requirements for referenced external docs
   - Document how to handle vendor documentation changes
   - Define ownership for tracking vendor updates

### User-Facing Documentation

For documentation intended for end-users:

1. **User Documentation Requirements**
   - Create a USER_DOCUMENTATION/ subdirectory in relevant plans
   - Follow the USER_GUIDE_TEMPLATE.md for consistency
   - Distinguish between different user roles and knowledge levels
   - Require peer review by non-technical reviewers

2. **Documentation Testing**
   - Require usability testing for user documentation
   - Document test results and user feedback
   - Update documentation based on user testing
   - Include screenshots and walkthrough guides for complex features

## Project Structure and Organization

### Plan and Code Organization

The UltraAI project follows a structured separation between planning/documentation and implementation code:

1. **Documentation and Actions Structure**
   - Core documentation resides in the `documentation/` directory
   - All action plans reside in the `Actions/` directory at the project root
   - Each action has its own subdirectory: `Actions/ACTION_NAME/`
   - Each action directory contains a PLAN.md file and all supporting materials
   - This keeps implementation plans separate from both documentation and code

2. **Implementation Code Structure**
   - Active production code resides in designated directories in the project root
   - The primary code directories are:
     - `src/` - Source code for the core application
     - `frontend/` - Frontend application code
     - `backend/` - Backend application code
     - `tests/` - Test code and testing utilities
     - `scripts/` - Utility scripts and tools

3. **Cross-Referencing Between Actions and Code**
   - Each action plan must reference the specific code directories it affects
   - Code files should include comments linking back to their authorizing action
   - The relationship between actions and code implementations must be explicitly documented

### Action Directory Structure

Each action directory within `Actions/` should follow this structure:

```
ACTION_NAME/
├── PLAN.md                      # The main plan document
├── Research/                    # Research materials
│   ├── RESEARCH_FINDINGS.md     # Research findings
│   └── ...                      # Other research documents
├── Design/                      # Design artifacts
│   ├── DESIGN_SPEC.md           # Design specifications
│   └── ...                      # Wireframes, diagrams, etc.
├── Implementation/              # Implementation documentation
│   ├── CODE_CHANGE_SCOPE.md     # Documentation of code changes
│   └── ...                      # Other implementation docs
├── Prototypes/                  # Prototype code (non-production)
│   ├── README.md                # Explanation of prototypes
│   └── ...                      # Prototype code files
└── ...                          # Other action-specific documents
```

### Code Directory Structure

Active production code must be organized according to these principles:

1. **Logical Component Separation**
   - Code should be organized by functional component or module
   - Each component should have a clearly defined purpose and interface
   - Components should have minimal dependencies on each other

2. **Consistent Naming and Structure**
   - All code directories and files should follow the naming conventions for their language
   - Each code directory should include a README.md explaining its purpose
   - Directory structures should be consistent across similar components

3. **Source Control Management**
   - Code changes must be traceable to their authorizing plan
   - Commit messages should reference plan IDs when applicable
   - Branches should be named to reflect the plan they implement

### Documentation-to-Code Traceability

To maintain clear traceability between documentation and code:

1. **Plan References in Code**
   - Include a comment at the top of modified files referencing the authorizing plan
   - Example: `// Implemented as part of PLAN_NAME - see documentation/Plans/PLAN_NAME/PLAN.md`

## Action and Plan Relationship

### Fundamental Principle

The UltraAI Framework operates on a fundamental principle: **Every action must have a plan**.

1. **Actions** are substantive work efforts that the project undertakes:
   - Feature development
   - System architecture changes
   - Infrastructure implementation
   - Process improvements
   - User experience enhancements
   - Any other significant work

2. **Plans** are the formal documentation of how actions will be implemented:
   - Each plan describes a single coherent action
   - No substantive action can begin without an approved plan
   - All plans must follow the PLAN_TEMPLATE.md format
   - Plans must be listed in the ACTIONS_INDEX.md

### Action Reuse Principle

Before proposing a new action, always consider:

1. **Reactivating Archived Actions**: Check if an archived action exists that could be reactivated to address the current need
2. **Extending Active Actions**: Determine if the work could be incorporated into an existing active action
3. **Creating New Actions**: Only create a new action when the work represents a distinct functional area not covered by existing actions

This approach ensures efficient use of resources, maintains clear ownership of functional areas, and prevents fragmentation of related work.

### Implementation Flow

The correct sequence for any work in the UltraAI project is:

1. **Identify Action Need**: Recognize that substantive work is required
2. **Document the Action**: Add the action to ACTIONS_INDEX.md
3. **Create Implementation Plan**: Document how the action will be implemented
4. **Approve Plan**: Get necessary stakeholder approval
5. **Update Action Status**: Update the action's status in ACTIONS_INDEX.md
6. **Execute Plan**: Implement the action according to the plan
7. **Document Results**: Update action status and plan with implementation results

### Plan Naming Convention

To ensure clarity about what action each plan addresses, action directories should be named to reflect their purpose using clear, descriptive names:

```
ACTION_NAME
```

Examples:

- API_DEVELOPMENT
- FRONTEND_DEVELOPMENT
- DATABASE_MIGRATION
