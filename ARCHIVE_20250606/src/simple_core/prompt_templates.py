"""
Prompt templates for multi-stage LLM processing

This module provides templates for formatting prompts for different stages
of the enhanced orchestration process:
1. Initial prompts
2. Meta-analysis prompts
3. Synthesis prompts
"""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class PromptTemplates:
    """
    Templates for different stages of the orchestration process

    Provides methods to format prompts for:
    - Initial model queries
    - Meta-analysis of responses
    - Synthesis of responses and analyses
    """

    def __init__(self, custom_templates: Optional[Dict[str, str]] = None):
        """
        Initialize prompt templates

        Args:
            custom_templates: Optional dictionary of custom templates to override defaults
        """
        self.templates = {
            # Template for initial prompts (minimal processing)
            "initial": "{prompt}",
            # Template for meta-analysis
            "meta_analysis": """
You are a helpful assistant evaluating responses from multiple AI models to the same prompt.

Original Prompt:
{prompt}

Responses to analyze:
{responses}

Your task is to analyze these responses and provide a detailed assessment of:
1. The strengths and weaknesses of each response
2. Which response is most helpful and why
3. What information is missing or could be improved in the responses
4. Any factual errors or inconsistencies between responses

Provide a comprehensive analysis that could help determine which response is best
and how the responses could be combined to create an optimal answer.
""",
            # Template for synthesizing responses and meta-analyses
            "synthesis": """
You are a helpful assistant creating an optimal response based on multiple AI models' answers to the same prompt.

Original Prompt:
{prompt}

Responses from different models:
{responses}

Analyses of these responses:
{analyses}

Your task is to synthesize an optimal response that:
1. Combines the strengths of each response
2. Addresses weaknesses identified in the analyses
3. Resolves any contradictions between responses
4. Provides the most helpful, accurate, and comprehensive answer possible

Create a response that would be better than any of the individual responses alone.
Do not mention that this is a synthesis or that you are combining multiple responses.
Simply provide the best possible answer to the original prompt.
""",
        }

        # Update with custom templates if provided
        if custom_templates:
            self.templates.update(custom_templates)

    def format_initial_prompt(self, prompt: str, request: Dict[str, Any]) -> str:
        """Format the initial prompt sent to models"""
        # Get any custom system prompt from the request
        system_prompt = request.get("system_prompt", "")

        # If a system prompt is provided, prepend it
        if system_prompt:
            formatted_prompt = f"{system_prompt}\n\n{prompt}"
        else:
            # Otherwise use the template
            formatted_prompt = self.templates["initial"].format(prompt=prompt)

        return formatted_prompt

    def format_meta_analysis_prompt(
        self, prompt: str, responses: List[Any], request: Dict[str, Any]
    ) -> str:
        """Format the meta-analysis prompt with the original prompt and model responses"""
        # Format the responses for inclusion in the meta prompt
        response_text = ""
        for i, resp in enumerate(responses, 1):
            response_text += (
                f"Response {i} (from {resp.model_name}):\n{resp.response}\n\n"
            )

        # Format the meta-analysis prompt
        return self.templates["meta_analysis"].format(
            prompt=prompt, responses=response_text
        )

    def format_synthesis_prompt(
        self,
        prompt: str,
        responses: List[Any],
        meta_analyses: List[Any],
        request: Dict[str, Any],
    ) -> str:
        """Format the synthesis prompt with the original prompt, responses, and meta-analyses"""
        # Format the responses
        response_text = ""
        for i, resp in enumerate(responses, 1):
            response_text += (
                f"Response {i} (from {resp.model_name}):\n{resp.response}\n\n"
            )

        # Format the meta-analyses
        analysis_text = ""
        if meta_analyses:
            for i, analysis in enumerate(meta_analyses, 1):
                analysis_text += f"Analysis {i} (from {analysis.model_name}):\n{analysis.meta_analysis}\n\n"
        else:
            analysis_text = "No meta-analyses available."

        # Format the synthesis prompt
        return self.templates["synthesis"].format(
            prompt=prompt, responses=response_text, analyses=analysis_text
        )
