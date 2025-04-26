#!/usr/bin/env python3
"""
UltraAI Session Tracker

This script helps maintain session tracking across the UltraAI project.
It ensures consistency between action plans and the central session tracking file.
"""

import os
import re
from pathlib import Path
from typing import Dict, List


class SessionTracker:
    def __init__(self, root_dir: str):
        self.root_dir = Path(root_dir)
        self.actions_dir = self.root_dir / "Actions"
        self.ultraai_dir = self.root_dir / ".ultraai"
        self.session_file = self.ultraai_dir / "session_tracking.md"
        self.template_file = (
            self.root_dir / "documentation" / "Templates" / "SESSION_TRACKING.md"
        )

    def get_current_session(self) -> Dict:
        """Get the current session information from session_tracking.md."""
        if not self.session_file.exists():
            return {}

        with open(self.session_file, "r") as f:
            content = f.read()

        # Extract current session information
        current_session_match = re.search(
            r"\|\s*(\d+)\s*\|\s*([\d-]+\s+[\d:]+)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|\s*(\d+)%",
            content,
        )

        if current_session_match:
            return {
                "session_id": current_session_match.group(1),
                "start_time": current_session_match.group(2),
                "action": current_session_match.group(3).strip(),
                "status": current_session_match.group(4).strip(),
                "progress": int(current_session_match.group(5)),
            }
        return {}

    def get_action_plans(self) -> List[Path]:
        """Get all action plan files."""
        return list(self.actions_dir.glob("*/PLAN.md"))

    def update_action_plan(self, plan_file: Path, session_info: Dict) -> None:
        """Update session tracking in an action plan."""
        if not plan_file.exists():
            return

        with open(plan_file, "r") as f:
            content = f.read()

        # Check if session tracking section exists
        if "## Session Tracking" not in content:
            # Add session tracking section after status
            status_end = content.find("## Overview")
            if status_end == -1:
                status_end = content.find("## Plan Review")

            if status_end != -1:
                session_section = f"""

## Session Tracking

### Current Session

| Session ID | Start Time | Status | Progress |
|------------|------------|--------|----------|
| {session_info['session_id']} | {session_info['start_time']} | {session_info['status']} | {session_info['progress']}% |

### Session History

| Session ID | Start Time | End Time | Status | Progress | Notes |
|------------|------------|----------|--------|----------|-------|
| {session_info['session_id']} | {session_info['start_time']} | Ongoing | {session_info['status']} | {session_info['progress']}% | {session_info['action']} |
"""
                content = content[:status_end] + session_section + content[status_end:]

                with open(plan_file, "w") as f:
                    f.write(content)

    def update_session_tracking(self) -> None:
        """Update the central session tracking file."""
        current_session = self.get_current_session()
        if not current_session:
            return

        # Update session tracking in all action plans
        for plan_file in self.get_action_plans():
            self.update_action_plan(plan_file, current_session)

    def validate_session_rules(self) -> bool:
        """Validate that session tracking follows the rules."""
        current_session = self.get_current_session()
        if not current_session:
            return False

        # Check if only one action is in WORKING state
        working_actions = 0
        for plan_file in self.get_action_plans():
            with open(plan_file, "r") as f:
                content = f.read()
                if "**Current Phase**: WORKING" in content:
                    working_actions += 1

        return working_actions == 1


def main():
    tracker = SessionTracker(os.getcwd())
    tracker.update_session_tracking()

    if not tracker.validate_session_rules():
        print("Warning: Session rules validation failed!")
        return 1

    print("Session tracking updated successfully!")
    return 0


if __name__ == "__main__":
    exit(main())
