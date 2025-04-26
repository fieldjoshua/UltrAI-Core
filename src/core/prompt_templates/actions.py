"""
Standard actions for the prompt templates system.
"""

from datetime import datetime
from typing import Any, Dict, Optional


class Action:
    """Base class for all actions."""

    def __init__(
        self, name: str, description: str, metadata: Optional[Dict[str, Any]] = None
    ):
        """Initialize an action.

        Args:
            name: Action name
            description: Action description
            metadata: Additional metadata
        """
        self.name = name
        self.description = description
        self.metadata = metadata or {}
        self.timestamp = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert action to dictionary format."""
        return {
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat(),
        }


class InitialAction(Action):
    """Action for initializing a session."""

    def __init__(self, branch: str, description: Optional[str] = None):
        """Initialize an initial action.

        Args:
            branch: Git branch name
            description: Optional description
        """
        super().__init__(
            name="Initial",
            description=description or f"Session initialized on branch: {branch}",
            metadata={"branch": branch},
        )


class TemplateAction(Action):
    """Action for creating or updating a template."""

    def __init__(
        self, template_id: str, operation: str, description: Optional[str] = None
    ):
        """Initialize a template action.

        Args:
            template_id: Template ID
            operation: Type of operation (create, update, delete)
            description: Optional description
        """
        super().__init__(
            name=f"Template {operation.capitalize()}",
            description=description or f"Template {operation}: {template_id}",
            metadata={"template_id": template_id, "operation": operation},
        )


class AnalysisAction(Action):
    """Action for performing analysis."""

    def __init__(
        self,
        analysis_type: str,
        description: str,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Initialize an analysis action.

        Args:
            analysis_type: Type of analysis
            description: Analysis description
            metadata: Additional metadata
        """
        super().__init__(
            name=f"Analysis: {analysis_type}",
            description=description,
            metadata={"analysis_type": analysis_type, **(metadata or {})},
        )


class FileAction(Action):
    """Action for file operations."""

    def __init__(
        self, file_path: str, operation: str, description: Optional[str] = None
    ):
        """Initialize a file action.

        Args:
            file_path: Path to the file
            operation: Type of operation (create, update, delete)
            description: Optional description
        """
        super().__init__(
            name=f"File {operation.capitalize()}",
            description=description or f"File {operation}: {file_path}",
            metadata={"file_path": file_path, "operation": operation},
        )


class CommitAction(Action):
    """Action for git commits."""

    def __init__(
        self, commit_hash: str, message: str, description: Optional[str] = None
    ):
        """Initialize a commit action.

        Args:
            commit_hash: Git commit hash
            message: Commit message
            description: Optional description
        """
        super().__init__(
            name="Git Commit",
            description=description or f"Commit: {message}",
            metadata={"commit_hash": commit_hash, "message": message},
        )


class ErrorAction(Action):
    """Action for error handling."""

    def __init__(
        self, error_type: str, error_message: str, description: Optional[str] = None
    ):
        """Initialize an error action.

        Args:
            error_type: Type of error
            error_message: Error message
            description: Optional description
        """
        super().__init__(
            name=f"Error: {error_type}",
            description=description or error_message,
            metadata={"error_type": error_type, "error_message": error_message},
        )


# Factory function to create actions
def create_action(action_type: str, **kwargs) -> Action:
    """Create an action based on type.

    Args:
        action_type: Type of action to create
        **kwargs: Additional arguments for the action

    Returns:
        Created Action instance

    Raises:
        ValueError: If action_type is not recognized
    """
    action_map = {
        "initial": InitialAction,
        "template": TemplateAction,
        "analysis": AnalysisAction,
        "file": FileAction,
        "commit": CommitAction,
        "error": ErrorAction,
    }

    if action_type not in action_map:
        raise ValueError(f"Unknown action type: {action_type}")

    return action_map[action_type](**kwargs)
