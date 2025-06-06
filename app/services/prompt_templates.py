"""
Prompt template system for managing and rendering prompts.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import json
import logging
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

logger = logging.getLogger(__name__)


@dataclass
class PromptTemplate:
    """Represents a prompt template with its metadata."""

    name: str
    template: str
    description: str
    variables: List[str]
    metadata: Dict[str, Any]


class PromptTemplateManager:
    """Manages prompt templates and their rendering."""

    def __init__(self, template_dir: Optional[str] = None):
        """
        Initialize the prompt template manager.

        Args:
            template_dir: Optional directory containing template files
        """
        self.templates: Dict[str, PromptTemplate] = {}
        self.env = Environment(
            loader=FileSystemLoader(template_dir) if template_dir else None,
            autoescape=True,
            trim_blocks=True,
            lstrip_blocks=True,
        )
        logger.info("Initialized PromptTemplateManager")

    def register_template(
        self,
        name: str,
        template: str,
        description: str,
        variables: List[str],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Register a new prompt template.

        Args:
            name: Unique name for the template
            template: The template string
            description: Description of the template's purpose
            variables: List of variables used in the template
            metadata: Optional metadata about the template
        """
        self.templates[name] = PromptTemplate(
            name=name,
            template=template,
            description=description,
            variables=variables,
            metadata=metadata or {},
        )
        logger.info(f"Registered template: {name}")

    def load_templates_from_file(self, file_path: str) -> None:
        """
        Load templates from a JSON file.

        Args:
            file_path: Path to the JSON file containing templates
        """
        try:
            with open(file_path, "r") as f:
                templates_data = json.load(f)

            for template_data in templates_data:
                self.register_template(
                    name=template_data["name"],
                    template=template_data["template"],
                    description=template_data["description"],
                    variables=template_data["variables"],
                    metadata=template_data.get("metadata", {}),
                )
            logger.info(f"Loaded templates from: {file_path}")
        except Exception as e:
            logger.error(f"Error loading templates from {file_path}: {str(e)}")
            raise

    def load_templates_from_directory(self, directory: str) -> None:
        """
        Load templates from a directory of JSON files.

        Args:
            directory: Path to directory containing template JSON files
        """
        try:
            template_files = Path(directory).glob("*.json")
            for file_path in template_files:
                self.load_templates_from_file(str(file_path))
            logger.info(f"Loaded templates from directory: {directory}")
        except Exception as e:
            logger.error(
                f"Error loading templates from directory {directory}: {str(e)}"
            )
            raise

    def render_template(
        self,
        name: str,
        variables: Dict[str, Any],
        strict: bool = True,
    ) -> str:
        """
        Render a template with the given variables.

        Args:
            name: Name of the template to render
            variables: Dictionary of variables to use in rendering
            strict: Whether to raise an error for missing variables

        Returns:
            str: The rendered template
        """
        if name not in self.templates:
            raise ValueError(f"Template not found: {name}")

        template = self.templates[name]

        # Validate required variables
        missing_vars = set(template.variables) - set(variables.keys())
        if missing_vars and strict:
            raise ValueError(f"Missing required variables: {missing_vars}")

        try:
            jinja_template = self.env.from_string(template.template)
            return jinja_template.render(**variables)
        except Exception as e:
            logger.error(f"Error rendering template {name}: {str(e)}")
            raise

    def get_template(self, name: str) -> Optional[PromptTemplate]:
        """
        Get a template by name.

        Args:
            name: Name of the template

        Returns:
            Optional[PromptTemplate]: The template if found, None otherwise
        """
        return self.templates.get(name)

    def list_templates(self) -> List[Dict[str, Any]]:
        """
        List all registered templates with their metadata.

        Returns:
            List[Dict[str, Any]]: List of template information
        """
        return [
            {
                "name": template.name,
                "description": template.description,
                "variables": template.variables,
                "metadata": template.metadata,
            }
            for template in self.templates.values()
        ]
