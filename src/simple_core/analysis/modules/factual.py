"""
Factual analysis module for Simple Core Orchestrator.

This module evaluates the factual accuracy of responses.
"""

import logging
from typing import Any, Dict, List, Optional

from ..analysis_module import AnalysisModule
from ..results import create_result

logger = logging.getLogger(__name__)


class FactualAnalysis(AnalysisModule):
    """
    Factual analysis module.

    This module evaluates the factual accuracy of responses by comparing
    them against known facts or verifiable information.
    """

    async def analyze(
        self,
        prompt: str,
        responses: List[Dict[str, Any]],
        options: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Analyze the factual accuracy of responses.

        Args:
            prompt: The original prompt
            responses: List of response objects from different models
            options: Optional configuration for this analysis

        Returns:
            Dictionary containing analysis results
        """
        options = options or {}

        # Get reference facts if provided
        reference_facts = options.get("reference_facts", [])

        # Check if we have an analysis model
        analysis_model = options.get("analysis_model")
        if not analysis_model:
            logger.warning("No analysis model provided, using mock factual analysis")
            return self._mock_factual_analysis(prompt, responses, reference_facts)

        # Format the prompt for factual analysis
        factual_prompt = self._format_factual_prompt(prompt, responses, reference_facts)

        # Use the analysis model to evaluate factual accuracy
        try:
            analysis_result = await analysis_model.generate(
                factual_prompt,
                {"processing_stage": "analysis", "analysis_type": "factual"},
            )

            # Extract scores if the model provides them
            scores = self._extract_factual_scores(analysis_result, responses)

            # Extract recommendations
            recommendations = self._extract_recommendations(analysis_result)

            return create_result(
                module_name=self.name,
                summary=analysis_result,
                details={
                    "prompt": factual_prompt,
                    "reference_facts_count": len(reference_facts),
                },
                scores=scores,
                recommendations=recommendations,
            )
        except Exception as e:
            logger.error(f"Error performing factual analysis: {str(e)}")
            return create_result(
                module_name=self.name,
                summary=f"Error performing factual analysis: {str(e)}",
                details={"error": str(e)},
                metadata={"error": True},
            )

    def _format_factual_prompt(
        self, prompt: str, responses: List[Dict[str, Any]], reference_facts: List[str]
    ) -> str:
        """Format the factual analysis prompt."""
        # Format the responses
        response_text = ""
        for i, resp in enumerate(responses, 1):
            model_name = resp.get("model", f"Model {i}")
            response_content = resp.get("response", "")
            response_text += (
                f"Response {i} (from {model_name}):\n{response_content}\n\n"
            )

        # Format reference facts if available
        facts_text = ""
        if reference_facts:
            facts_text = "Reference Facts:\n"
            for i, fact in enumerate(reference_facts, 1):
                facts_text += f"{i}. {fact}\n"
        else:
            facts_text = "(No specific reference facts provided. Evaluate based on general knowledge.)"

        # Create the factual analysis prompt
        return f"""
You are a helpful assistant evaluating the factual accuracy of responses from multiple AI models.

Original Prompt:
{prompt}

{facts_text}

Responses to evaluate:
{response_text}

Your task is to analyze the factual accuracy of these responses:
1. Identify any factual claims made in each response
2. Assess whether these claims are accurate, inaccurate, or uncertain
3. If reference facts were provided, check the responses against these facts
4. Note any contradictions between different responses
5. Provide an overall factual accuracy assessment for each response

Conclude with a summary of which response(s) appear to be the most factually accurate.
"""

    def _mock_factual_analysis(
        self, prompt: str, responses: List[Dict[str, Any]], reference_facts: List[str]
    ) -> Dict[str, Any]:
        """Generate a basic mock analysis when no analysis model is available."""
        # Simple mock implementation
        summary = "Factual analysis (mock implementation):\n\n"

        if reference_facts:
            summary += f"Based on {len(reference_facts)} reference facts provided.\n\n"
        else:
            summary += "No reference facts were provided for verification.\n\n"

        for i, resp in enumerate(responses, 1):
            model_name = resp.get("model", f"Model {i}")
            summary += f"Response {i} from {model_name}: Unable to verify factual accuracy without analysis model.\n"

        summary += "\nThis is a placeholder analysis. For proper factual verification, provide an analysis model."

        # Generate mock scores (neutral scores without actual analysis)
        scores = {}
        for resp in responses:
            model_name = resp.get("model", "Unknown")
            scores[model_name] = 0.5  # Neutral score

        return create_result(
            module_name=self.name,
            summary=summary,
            details={"reference_facts_count": len(reference_facts)},
            scores=scores,
            recommendations=["Use an analysis model for proper factual verification."],
        )

    def _extract_factual_scores(
        self, analysis: str, responses: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """Extract factual accuracy scores from the analysis text."""
        # Simple mock implementation
        scores = {}
        for resp in responses:
            model_name = resp.get("model", "Unknown")
            scores[model_name] = 0.5  # Default neutral score

        return scores

    def _extract_recommendations(self, analysis: str) -> List[str]:
        """Extract recommendations from the analysis text."""
        # Simple mock implementation
        return ["Prefer responses with higher factual accuracy scores."]
