# AICheck Rules

This document is the controlling reference for all work managed by the AICheck system in this PROJECT.

## 1. Core Principles

### 1.1 Documentation-First Approach
- Write clear docstrings for all functions and classes
- Include explanatory comments for complex code blocks
- Update README.md with relevant project information
- Create/update API documentation when adding endpoints
- All ACTIONS require their own directory with a documented PLAN before implementation
- PLANs require approval and must detail the ACTION's value to the PROGRAM
- ACTIONS must be TEST-Driven: tests must be created before implementation

### 1.2 Language-Specific Best Practices
- Python: Follow PEP 8 style guidelines with 150 max line length
- JavaScript/TypeScript: Use ESLint and Prettier standards
- Follow language idioms and patterns (pythonic, modern JS/TS)

### 1.3 Quality Standards
- Write unit tests for new functionality
- Maintain test coverage above 80%
- Handle errors explicitly with proper logging
- Use typed interfaces where possible

### 1.4 Security Practices
- Validate all user inputs
- Use parameterized queries for database operations
- Store secrets in environment variables, never in code
- Apply proper authentication and authorization

## 2. Action Management

### 2.1 AI Editor Scope
AI editors may implement without approval:
- Code implementing the ActiveAction plan (after PLAN approval)
- Documentation updates for ActiveAction
- Bug fixes and tests within ActiveAction scope
- Refactoring within ActiveAction scope

The following ALWAYS require human manager approval:
- Changing the ActiveAction
- Creating a new Action
- Making substantive changes to any Action
- Modifying any Action Plan

### 2.2 Failure Pattern Recognition and Critical Analysis

#### 2.2.1 Three-Strike Rule
- If the same action is attempted 3 times with variable changes but no improvement, **STOP immediately**
- Do not proceed with further iterations of the same approach
- Document the failure pattern and underlying assumptions

#### 2.2.2 Mandatory Root Cause Analysis
When the three-strike rule is triggered:
1. **Identify the core problem** - What is actually failing vs. what appears to be failing?
2. **Challenge assumptions** - Are we solving the right problem?
3. **Research thoroughly** - Use documentation, code analysis, or external resources
4. **Propose alternative approaches** - Don't just vary the same solution

#### 2.2.3 System Compatibility Analysis
Before attempting integrations:
- **Verify API contracts** - Do request/response formats match?
- **Check authentication requirements** - Are security models compatible?
- **Validate data flows** - Does the data transformation make sense?
- **Document incompatibilities** - Clearly state what needs to change where

#### 2.2.4 Documentation Requirement
- Log all failed approaches with reasons for failure
- Document the decision-making process for switching approaches
- Provide clear justification for the chosen solution path

## 3. Project Structure and Organization

### 3.1 Directory Structure
```text
/
├── .aicheck/
│   ├── actions/                      # All PROJECT ACTIONS
│   │   └── [action-name]/            # Individual ACTION directory
│   │       ├── [action-name]-plan.md # ACTION PLAN (requires approval)
│   │       └── supporting_docs/      # ACTION-specific documentation
│   │           ├── claude-interactions/  # Claude Code logs
│   │           ├── process-tests/        # Temporary tests for ACTION
│   │           └── research/             # Research and notes
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
├── tests/                            # Permanent test suite
│   ├── unit/                         # Unit tests
│   ├── integration/                  # Integration tests
│   ├── e2e/                          # End-to-end tests
│   └── fixtures/                     # Test data and fixtures
```

## 4. Dependency Management

### 4.1 External Dependencies
- All external dependencies must be documented in /documentation/dependencies/dependency_index.md
- Include justification for every new dependency added
- Document specific version requirements
- Note which ACTIONS depend on each dependency

### 4.2 Internal Dependencies
- Document dependencies between ACTIONS
- Track which ACTIONS depend on others' functionality
- Document the type of dependency (data, function, service)
- Always verify dependencies before completing an ACTION

## 5. AICheck Commands

Claude Code supports these AICheck slash commands:
- `./aicheck status` - Show current action status
- `./aicheck action new ActionName` - Create a new action
- `./aicheck action set ActionName` - Set current active action
- `./aicheck action complete [ActionName]` - Complete action
- `./aicheck dependency add NAME VERSION JUSTIFICATION [ACTION]` - Add external dependency
- `./aicheck dependency internal DEP_ACTION ACTION TYPE [DESCRIPTION]` - Add internal dependency
- `./aicheck exec` - Toggle exec mode for system maintenance
