# UltraAI Prompt Templates

This module provides a structured system for managing AI prompts and interactions in the UltraAI framework.

## Overview

The prompt templates system consists of three main components:

1. **PromptTemplate**: Represents a structured prompt with sections for context, task, requirements, and expected output.
2. **Session**: Manages the state of an AI interaction, including active files and action history.
3. **Managers**: Handle the creation, storage, and retrieval of templates and sessions.

## Usage

### Creating a Prompt Template

```python
from src.core.prompt_templates import PromptTemplateManager

# Initialize the template manager
template_manager = PromptTemplateManager()

# Create a new template
template = template_manager.create_template(
    title="AI Prompt - 2025-04-25 15:12:41",
    current_action="Initial",
    context="Add any relevant context here",
    task="Describe what you want the AI to do",
    requirements=[
        "Requirement 1",
        "Requirement 2"
    ],
    expected_output="Describe what output you expect"
)
```

### Managing Sessions

```python
from src.core.prompt_templates import SessionManager

# Initialize the session manager
session_manager = SessionManager()

# Create a new session
session = session_manager.create_session(branch="dev-mode")

# Add an action to the session
session.add_action({
    "name": "Initial",
    "description": "Created: 2025-04-25 15:08:42"
})

# Update the session
session_manager.update_session(session)

# Get a session by ID
session = session_manager.get_session("20250425150842")
```

## Directory Structure

```
.ultraai/
├── templates/           # Prompt templates
│   └── prompt_*.md     # Template files
└── sessions/           # Session data
    └── YYYYMMDDHHMMSS/ # Session directories
        ├── context.md  # Session context
        └── prompt_*.md # Session prompts
```

## Security Considerations

- The system uses absolute paths for external commands
- File operations are performed with proper error handling
- Session data is stored in a structured format
- Git branch detection is optional and falls back gracefully

## Integration

The prompt templates system is designed to integrate with:

1. The UltraAI core framework
2. Git version control
3. Markdown-based documentation
4. AI interaction workflows

## Development

To add new features or modify the system:

1. Update the models in `models.py`
2. Extend the managers in `template_manager.py` and `session_manager.py`
3. Add new functionality while maintaining the existing interface
4. Update tests and documentation accordingly
