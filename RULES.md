# AICheck Development Rules

This document serves as the controlling reference for all development work managed by the AICheck system.

## Core Principles

1. **Documentation First**: All Actions must be documented before implementation begins
2. **Single Action Focus**: Work on one Action at a time to maintain focus and clarity
3. **Explicit Context Switching**: When changing focus, explicitly document the context switch
4. **Structured AI Interactions**: Use the provided templates for all AI interactions
5. **Regular Session Logging**: Document all AI sessions with clear summaries

## General AI Editor Guidelines

**Approval Assumption**: AI editors DO NOT need to ask for approval for any work that:
1. Complies with the rules in this document
2. Falls within the scope of the currently active Action as defined in the action index
3. Follows established patterns and conventions for the project

AI editors can proceed directly with implementation for:
- Code that implements the current Action plan
- Documentation updates related to the Action
- Bug fixes within the Action scope
- Tests for current Action functionality
- Refactoring within the current Action scope

This rule is designed to streamline the development process by eliminating the need for explicit approval of compliant work.

## Directory Structure Note

In this implementation, each action has its own directory structure:
```
.aicheck/actions/
└── [ACTION_NAME]/
    ├── [ACTION_NAME]-PLAN.md  # Main plan document
    └── supporting_docs/       # Action-specific documentation
```

## Reference Paths

- **Actions Index**: `.aicheck/docs/actions_index.md` (source of truth for Action status)
- **Session Logs**: `.aicheck/sessions/session_log.txt`
- **Current Action**: Check with `./ai status`
- **Documentation**: `.aicheck/docs/README.md`

## Workflow Requirements

1. Start every development session with `./ai start`
2. Check your current focus with `./ai status`
3. Create new Actions for new work with `./ai new ActionName`
4. End sessions with meaningful summaries using `./ai end "summary"`
5. Review insights regularly with `./ai insights`

## Cursor Integration Guidelines

1. Generate context before starting Cursor AI interactions
2. Log all significant Cursor interactions after completion
3. Maintain focus on the current Action in all Cursor sessions

Remember: The AICheck system is designed to improve focus and documentation quality in AI-assisted development. Follow these rules to maximize its benefits.
