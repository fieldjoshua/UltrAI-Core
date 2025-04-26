"""
Session manager for handling AI interaction sessions.
"""

import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from .models import Session


class SessionManager:
    """Manages AI interaction sessions."""

    def __init__(self, sessions_dir: str = ".ultraai/sessions"):
        """Initialize the session manager.

        Args:
            sessions_dir: Directory to store sessions
        """
        self.sessions_dir = Path(sessions_dir)
        self.sessions_dir.mkdir(parents=True, exist_ok=True)

    def create_session(self, branch: str = "main") -> Session:
        """Create a new session.

        Args:
            branch: Git branch name

        Returns:
            Created Session instance
        """
        # Get current git branch if not specified
        if branch == "main":
            try:
                # Using absolute path to git executable for security
                git_path = os.path.abspath(
                    subprocess.check_output(["which", "git"], text=True).strip()
                )
                if not os.path.exists(git_path):
                    raise FileNotFoundError("Git executable not found")

                branch = subprocess.check_output(
                    [git_path, "rev-parse", "--abbrev-ref", "HEAD"], text=True
                ).strip()
            except (subprocess.CalledProcessError, FileNotFoundError):
                branch = "main"

        # Create session ID from timestamp
        session_id = datetime.now().strftime("%Y%m%d%H%M%S")

        # Create session directory
        session_dir = self.sessions_dir / session_id
        session_dir.mkdir(parents=True, exist_ok=True)

        # Create session instance
        session = Session(
            session_id=session_id, branch=branch, current_action="Initial"
        )

        # Save session context
        self._save_session(session)

        return session

    def get_session(self, session_id: str) -> Optional[Session]:
        """Get a session by its ID.

        Args:
            session_id: Session ID

        Returns:
            Session instance if found, None otherwise
        """
        session_dir = self.sessions_dir / session_id
        if not session_dir.exists():
            return None

        # Read session context
        context_file = session_dir / "context.md"
        if not context_file.exists():
            return None

        with open(context_file, "r") as f:
            content = f.read()

        # Parse markdown content into session
        lines = content.split("\n")
        session_id = lines[0].replace("# Session Context: ", "")
        branch = lines[1].replace("- Branch: ", "")
        current_action = lines[2].replace("- Current Action: ", "")

        # Find section boundaries
        files_start = content.find("## Active Files\n") + len("## Active Files\n")
        history_start = content.find("## Action History\n") + len("## Action History\n")

        active_files = [
            line.strip("- ")
            for line in content[files_start:history_start].strip().split("\n")
        ]
        action_history = []

        # Parse action history
        history_lines = content[history_start:].strip().split("\n")
        current_action_name = None
        current_description = []

        for line in history_lines:
            if line.startswith("# Action: "):
                if current_action_name:
                    action_history.append(
                        {
                            "name": current_action_name,
                            "description": "\n".join(current_description),
                        }
                    )
                current_action_name = line.replace("# Action: ", "")
                current_description = []
            else:
                current_description.append(line)

        if current_action_name:
            action_history.append(
                {
                    "name": current_action_name,
                    "description": "\n".join(current_description),
                }
            )

        return Session(
            session_id=session_id,
            branch=branch,
            current_action=current_action,
            active_files=active_files,
            action_history=action_history,
        )

    def update_session(self, session: Session):
        """Update a session.

        Args:
            session: Session instance to update
        """
        self._save_session(session)

    def list_sessions(self) -> List[str]:
        """List all available session IDs.

        Returns:
            List of session IDs
        """
        return [d.name for d in self.sessions_dir.iterdir() if d.is_dir()]

    def _save_session(self, session: Session):
        """Save session context to file.

        Args:
            session: Session instance to save
        """
        session_dir = self.sessions_dir / session.session_id
        session_dir.mkdir(parents=True, exist_ok=True)

        with open(session_dir / "context.md", "w") as f:
            f.write(session.to_markdown())
