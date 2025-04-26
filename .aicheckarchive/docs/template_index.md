# UltraAICheck Template Index

This document serves as a central reference for all templates available in the UltraAICheck system.

## Available Templates

| Template Name | Purpose | Location | Usage Command |
|---------------|---------|----------|---------------|
| Action | Standard structure for creating a new action | `.aicheck/templates/action.md` | `./ai new ActionName` |
| Prompt | Template for AI interaction prompts | `.aicheck/templates/prompt.md` | `./ai prompt` |
| Session Summary | Format for summarizing completed sessions | `.aicheck/templates/session_summary.md` | `./ai end "summary"` |
| Supporting Document | Template for action-specific documentation | `.aicheck/templates/supporting_doc.md` | `./ai docs ActionName document.md` |

## Action Template

The action template creates a standardized structure for all action plans:

- **Objective**: Clear statement of the action's goal
- **Context**: Background information on why the action is needed
- **Requirements**: Specific requirements that must be met
- **Implementation Plan**: Step-by-step approach to completing the action
- **Status**: Current state of the action

## Prompt Template

The prompt template structures AI interactions:

- **RULES Reference**: Reminder of the project's rules
- **Current Action**: The action being worked on
- **Context**: Relevant background information
- **Task**: Clear description of what the AI should do
- **Requirements**: Specific requirements for the task
- **Expected Output**: Description of the desired result

## Session Summary Template

The session summary template standardizes how completed work sessions are documented:

- **End Time**: When the session was completed
- **Summary**: Brief description of what was accomplished
- **Actions Worked On**: Which actions were addressed
- **Files Modified**: Which files were changed
- **Progress Made**: Specific progress made during this session
- **Next Steps**: List of next steps for this action

## Supporting Document Template

The supporting document template provides a structure for action-specific documentation:

- **Overview**: Brief overview of what the document covers
- **Content**: Main content of the document
- **Related Documents**: List of related documents
- **Last Updated**: Date of last update

## Creating New Templates

To create a new template:

1. Create a file in the `.aicheck/templates/` directory
2. Structure the template with clear sections and placeholders
3. Add the template to this index for reference
4. Update the UltraAICheck scripts to use the new template if needed

## How to Use Templates

Templates are automatically used by the UltraAICheck system when running commands like `./ai new` or `./ai prompt`. You can also manually copy templates from the `.aicheck/templates/` directory as needed.

## Last Updated: 2025-04-25
