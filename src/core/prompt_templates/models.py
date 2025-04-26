"""
Models for the prompt template system.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any

from .actions import Action


@dataclass
class PromptTemplate:
    """Represents a prompt template with its sections."""

    title: str
    current_action: str
    context: str
    task: str
    requirements: List[str]
    expected_output: str
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def to_markdown(self) -> str:
        """Convert the template to markdown format."""
        return f"""# {self.title}
## Current Action: {self.current_action}

## Context
{self.context}

## Task
{self.task}

## Requirements
{chr(10).join(f'- {req}' for req in self.requirements)}

## Expected Output
{self.expected_output}
"""


@dataclass
class Session:
    """Represents an AI interaction session."""

    session_id: str
    branch: str
    current_action: str
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    context: Dict[str, Any] = field(default_factory=dict)
    active_files: List[str] = field(default_factory=list)
    action_history: List[Action] = field(default_factory=list)

    def add_action(self, action: Action):
        """Add an action to the session history.

        Args:
            action: Action instance to add
        """
        self.action_history.append(action)
        self.updated_at = datetime.now()
        self.current_action = action.name

    def to_markdown(self) -> str:
        """Convert the session to markdown format."""
        return f"""# Session Context: {self.session_id}
- Branch: {self.branch}
- Current Action: {self.current_action}
- Created: {self.created_at}
- Updated: {self.updated_at}

## Active Files
{chr(10).join(f'- {file}' for file in self.active_files)}

## Action History
{chr(10).join(f'# Action: {action.name}\n{action.description}\n\nMetadata: {action.metadata}' for action in self.action_history)}
"""
