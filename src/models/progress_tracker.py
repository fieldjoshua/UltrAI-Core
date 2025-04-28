"""
Progress Tracking Module.

This module provides utilities for tracking and reporting progress of model operations.
"""

import enum
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional


class ProgressStatus(enum.Enum):
    """Status of a model operation."""

    NOT_STARTED = "not_started"
    STARTED = "started"
    IN_PROGRESS = "in_progress"
    RETRYING = "retrying"
    COMPLETED = "completed"
    ERROR = "error"
    FAILED = "failed"


@dataclass
class ProgressUpdate:
    """
    Update about the progress of a model operation.

    Attributes:
        model: The model being used
        stage: The processing stage
        status: The current status
        message: Optional message about the progress
    """

    model: str
    stage: str
    status: ProgressStatus
    message: str = ""


class ProgressTracker:
    """
    Tracks progress across multiple models and stages.

    This class maintains the state of progress for all models and stages,
    and allows registering callbacks for progress updates.
    """

    def __init__(self, stages: List[str]):
        """
        Initialize the progress tracker.

        Args:
            stages: The list of stages to track
        """
        self.stages = stages
        self.model_progress: Dict[str, Dict[str, Dict[str, Any]]] = {}
        self.callbacks: List[Callable[[ProgressUpdate], None]] = []

    def add_callback(self, callback: Callable[[ProgressUpdate], None]) -> None:
        """
        Add a callback for progress updates.

        Args:
            callback: The callback to add
        """
        self.callbacks.append(callback)

    def update(
        self,
        model: str,
        stage: str,
        status: ProgressStatus,
        message: str = "",
    ) -> None:
        """
        Update the progress for a model and stage.

        Args:
            model: The model being used
            stage: The processing stage
            status: The current status
            message: Optional message about the progress
        """
        # Initialize model if not present
        if model not in self.model_progress:
            self.model_progress[model] = {}

        # Initialize stage if not present
        if stage not in self.model_progress[model]:
            self.model_progress[model][stage] = {
                "status": ProgressStatus.NOT_STARTED.value,
                "message": "",
                "timestamp": 0,
            }

        # Update progress
        self.model_progress[model][stage] = {
            "status": status.value,
            "message": message,
            "timestamp": import_time(),
        }

        # Call callbacks
        update = ProgressUpdate(
            model=model,
            stage=stage,
            status=status,
            message=message,
        )
        for callback in self.callbacks:
            callback(update)

    def get_status(self, model: str, stage: str) -> Optional[str]:
        """
        Get the status for a model and stage.

        Args:
            model: The model
            stage: The stage

        Returns:
            The status, or None if not found
        """
        if model in self.model_progress and stage in self.model_progress[model]:
            return self.model_progress[model][stage]["status"]
        return None

    def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of all progress.

        Returns:
            Dictionary with progress summary
        """
        # Calculate overall progress
        completed_stages = sum(
            1
            for model_data in self.model_progress.values()
            for stage_data in model_data.values()
            if stage_data["status"] == ProgressStatus.COMPLETED.value
        )

        total_stages = len(self.stages) * len(self.model_progress)
        if total_stages == 0:
            progress_percent = 0
        else:
            progress_percent = int((completed_stages / total_stages) * 100)

        return {
            "progress_percent": progress_percent,
            "completed_stages": completed_stages,
            "total_stages": total_stages,
            "models": list(self.model_progress.keys()),
            "stages": self.stages,
            "details": self.model_progress,
        }


def import_time() -> float:
    """
    Get the current time.

    Returns:
        The current time as a float
    """
    import time

    return time.time()
