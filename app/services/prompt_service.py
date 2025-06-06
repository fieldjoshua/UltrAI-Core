"""
Prompt Service Module

This module provides template management and prompt processing services.
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json
import markdown

from app.services.model_registry import ModelRegistry
from app.services.orchestration_service import OrchestrationService
from app.utils.logging import get_logger

logger = get_logger("prompt_service")


@dataclass
class Template:
    """A prompt template with variables and metadata."""

    name: str
    description: str
    template: str
    variables: List[str]
    version: str = "1.0.0"
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PromptRequest:
    """A request to process a prompt."""

    template_name: str
    variables: Dict[str, Any]
    models: List[str]
    options: Dict[str, Any] = field(default_factory=dict)
    format: str = "markdown"


class PromptService:
    """Service for managing prompt templates and processing prompts."""

    def __init__(
        self, model_registry: ModelRegistry, orchestration_service: OrchestrationService
    ):
        """Initialize the prompt service.

        Args:
            model_registry: The model registry service
            orchestration_service: The orchestration service
        """
        self.model_registry = model_registry
        self.orchestration_service = orchestration_service
        self._templates: Dict[str, Template] = {}
        self._initialize_default_templates()

    def _initialize_default_templates(self) -> None:
        """Initialize default prompt templates."""
        default_templates = {
            "analysis": Template(
                name="analysis",
                description="Standard analysis template",
                template="""Analyze the following content:

{content}

Consider these aspects:
- Key points and insights
- Potential implications
- Recommendations
- Areas for further investigation

Additional context:
{context}""",
                variables=["content", "context"],
            ),
            "comparison": Template(
                name="comparison",
                description="Comparison analysis template",
                template="""Compare and contrast the following items:

{items}

Consider these aspects:
- Similarities
- Differences
- Relative strengths
- Relative weaknesses
- Recommendations

Context:
{context}""",
                variables=["items", "context"],
            ),
            "evaluation": Template(
                name="evaluation",
                description="Evaluation template",
                template="""Evaluate the following:

{subject}

Use these criteria:
{criteria}

Consider:
- Strengths
- Weaknesses
- Opportunities
- Threats
- Recommendations

Context:
{context}""",
                variables=["subject", "criteria", "context"],
            ),
        }
        self._templates.update(default_templates)

    def register_template(self, template: Template) -> None:
        """Register a new prompt template.

        Args:
            template: The template to register
        """
        if template.name in self._templates:
            raise ValueError(f"Template {template.name} already exists")

        self._templates[template.name] = template
        logger.info(f"Registered template: {template.name}")

    def get_template(self, name: str) -> Optional[Template]:
        """Get a template by name.

        Args:
            name: The template name

        Returns:
            Optional[Template]: The template if found
        """
        return self._templates.get(name)

    def list_templates(self) -> List[Dict[str, Any]]:
        """List all registered templates.

        Returns:
            List[Dict[str, Any]]: List of template information
        """
        return [
            {
                "name": template.name,
                "description": template.description,
                "version": template.version,
                "variables": template.variables,
                "created_at": template.created_at,
                "updated_at": template.updated_at,
            }
            for template in self._templates.values()
        ]

    def update_template(self, name: str, updates: Dict[str, Any]) -> None:
        """Update a template's configuration.

        Args:
            name: Name of the template to update
            updates: Dictionary of updates to apply
        """
        if name not in self._templates:
            raise ValueError(f"Template {name} not found")

        template = self._templates[name]
        for key, value in updates.items():
            if hasattr(template, key):
                setattr(template, key, value)

        template.updated_at = datetime.now()
        logger.info(f"Updated template: {name}")

    def _format_output(self, content: str, format_type: str) -> str:
        """Format the output according to the requested format.

        Args:
            content: The content to format
            format_type: The requested output format

        Returns:
            str: Formatted content
        """
        if format_type == "plain":
            # Strip markdown formatting
            lines = content.split("\n")
            result = []
            for line in lines:
                if line.startswith("#"):
                    result.append(line.lstrip("# "))
                elif line.startswith("```"):
                    continue
                elif line.startswith("- "):
                    result.append(line[2:])
                else:
                    result.append(line)
            return "\n".join(result)

        elif format_type == "html":
            return markdown.markdown(content)

        elif format_type == "json":
            return json.dumps({"content": content})

        # Default is markdown
        return content

    def _render_template(self, template: Template, variables: Dict[str, Any]) -> str:
        """Render a template with the provided variables.

        Args:
            template: The template to render
            variables: The variables to use

        Returns:
            str: The rendered template
        """
        # Validate all required variables are provided
        missing_vars = [var for var in template.variables if var not in variables]
        if missing_vars:
            raise ValueError(f"Missing required variables: {', '.join(missing_vars)}")

        # Render the template
        try:
            return template.template.format(**variables)
        except KeyError as e:
            raise ValueError(f"Invalid variable in template: {str(e)}")

    async def process_prompt(self, request: PromptRequest) -> Dict[str, Any]:
        """Process a prompt using the specified template and models.

        Args:
            request: The prompt processing request

        Returns:
            Dict[str, Any]: The processing results
        """
        # Get the template
        template = self.get_template(request.template_name)
        if not template:
            raise ValueError(f"Template {request.template_name} not found")

        # Render the template
        prompt = self._render_template(template, request.variables)

        # Process the prompt through the orchestration service
        result = await self.orchestration_service.run_pipeline(
            input_data=prompt, options=request.options
        )

        # Format the output
        formatted_output = self._format_output(str(result), request.format)

        return {
            "template": request.template_name,
            "prompt": prompt,
            "result": formatted_output,
            "metadata": {
                "models_used": request.models,
                "format": request.format,
                "timestamp": datetime.now().isoformat(),
            },
        }


def get_prompt_service(
    model_registry: Optional[ModelRegistry] = None,
    orchestration_service: Optional[OrchestrationService] = None,
) -> "PromptService":
    """
    Dependency provider for PromptService. If dependencies are not provided, instantiate them.
    """
    if model_registry is None:
        model_registry = ModelRegistry()
    if orchestration_service is None:
        orchestration_service = OrchestrationService(model_registry=model_registry)
    return PromptService(
        model_registry=model_registry, orchestration_service=orchestration_service
    )
