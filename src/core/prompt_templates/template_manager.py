"""
Template manager for handling prompt templates.
"""

from datetime import datetime
from pathlib import Path
from typing import List, Optional

from .models import PromptTemplate


class PromptTemplateManager:
    """Manages prompt templates and their storage."""

    def __init__(self, templates_dir: str = ".ultraai/templates"):
        """Initialize the template manager.

        Args:
            templates_dir: Directory to store templates
        """
        self.templates_dir = Path(templates_dir)
        self.templates_dir.mkdir(parents=True, exist_ok=True)

    def create_template(
        self,
        title: str,
        current_action: str,
        context: str,
        task: str,
        requirements: List[str],
        expected_output: str,
    ) -> PromptTemplate:
        """Create a new prompt template.

        Args:
            title: Template title
            current_action: Current action status
            context: Context section
            task: Task description
            requirements: List of requirements
            expected_output: Expected output description

        Returns:
            Created PromptTemplate instance
        """
        template = PromptTemplate(
            title=title,
            current_action=current_action,
            context=context,
            task=task,
            requirements=requirements,
            expected_output=expected_output,
        )

        # Save template to file
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"prompt_{timestamp}.md"
        filepath = self.templates_dir / filename

        with open(filepath, "w") as f:
            f.write(template.to_markdown())

        return template

    def get_template(self, template_id: str) -> Optional[PromptTemplate]:
        """Get a template by its ID.

        Args:
            template_id: Template ID (filename without extension)

        Returns:
            PromptTemplate instance if found, None otherwise
        """
        filepath = self.templates_dir / f"{template_id}.md"
        if not filepath.exists():
            return None

        with open(filepath, "r") as f:
            content = f.read()

        # Parse markdown content into template
        lines = content.split("\n")
        title = lines[0].replace("# ", "")
        current_action = lines[1].replace("## Current Action: ", "")

        # Find section boundaries
        context_start = content.find("## Context\n") + len("## Context\n")
        task_start = content.find("## Task\n") + len("## Task\n")
        req_start = content.find("## Requirements\n") + len("## Requirements\n")
        output_start = content.find("## Expected Output\n") + len(
            "## Expected Output\n"
        )

        context = content[context_start:task_start].strip()
        task = content[task_start:req_start].strip()
        requirements = [
            line.strip("- ")
            for line in content[req_start:output_start].strip().split("\n")
        ]
        expected_output = content[output_start:].strip()

        return PromptTemplate(
            title=title,
            current_action=current_action,
            context=context,
            task=task,
            requirements=requirements,
            expected_output=expected_output,
        )

    def list_templates(self) -> List[str]:
        """List all available template IDs.

        Returns:
            List of template IDs
        """
        return [f.stem for f in self.templates_dir.glob("*.md")]
