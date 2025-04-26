# AICheck Complete Package Documentation

## Overview
AICheck is a comprehensive system for AI-assisted development that helps maintain focus, documentation, and productivity in your development workflow.

## Core Components

### 1. Core Rule Enforcement
- Pre-commit hooks that enforce documentation-first approach
- Single Action working state enforcement
- Template verification and structure checking

### 2. AI Session Management
- Context loading for AI sessions with previous conversations
- Time tracking and automated session logging
- Structured prompt generation

### 3. Documentation Automation
- Auto-generated indexes of all Actions
- Knowledge base built from session patterns
- Consolidated decision log
- Real-time dashboard

### 4. Focus Protocol
- AI stays focused on current Action
- Context-switching requires explicit Action identification
- New Action creation guidance

### 5. Analytics and Insights
- Session productivity metrics
- Common blockers identification
- Topic analysis and word frequency
- Automated recommendations

### 6. Cursor Integration
- Keyboard shortcuts for AI commands
- Code snippets for all document types
- Context generation and clipboard support
- Session logging from Cursor

## Getting Started

1. Start a new AI session: `./ai start`
2. Create a new Action: `./ai new ActionName`
3. Generate a prompt template: `./ai prompt`
4. Check status: `./ai status`
5. End session: `./ai end "summary"`

For Cursor integration:
1. Generate context: `./cursor-ai context`
2. Log session: `./cursor-ai log "summary"`

## Best Practices

1. Create an Action for each distinct task
2. Keep actions focused and single-purpose
3. Document AI sessions with clear summaries
4. Use the Focus Protocol to maintain productivity
5. Review insights regularly to improve workflow
