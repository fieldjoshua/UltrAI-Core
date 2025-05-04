"""
Comparative analysis module for Simple Core Orchestrator.

This module compares responses from different models and identifies
strengths, weaknesses, and optimal responses.
"""

import logging
from typing import Any, Dict, List, Optional

from ..analysis_module import AnalysisModule
from ..results import create_result

logger = logging.getLogger(__name__)


class ComparativeAnalysis(AnalysisModule):
    """
    Comparative analysis module.

    This module compares responses from different models and produces
    an analysis of their relative strengths and weaknesses.
    """

    async def analyze(
        self,
        prompt: str,
        responses: List[Dict[str, Any]],
        options: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Analyze a set of responses by comparing them to each other.

        Args:
            prompt: The original prompt
            responses: List of response objects from different models
            options: Optional configuration for this analysis

        Returns:
            Dictionary containing analysis results
        """
        options = options or {}

        # If there are fewer than 2 responses, there's nothing to compare
        if len(responses) < 2:
            return create_result(
                module_name=self.name,
                summary="Not enough responses to perform comparative analysis.",
                details={"responses_count": len(responses)},
                scores={},
                recommendations=["Add more models to enable comparative analysis."],
            )

        # Use the same prompt template as in enhanced_orchestrator.py
        meta_prompt = self._format_comparative_prompt(prompt, responses)

        # Check if we have a model to use for the analysis
        analysis_model = options.get("analysis_model")
        if not analysis_model:
            # Log warning but continue with mock analysis
            logger.warning(
                "No analysis model provided, using mock comparative analysis"
            )
            return self._mock_comparative_analysis(prompt, responses)

        # Use the analysis model to generate the comparison
        try:
            analysis_result = await analysis_model.generate(
                meta_prompt,
                {"processing_stage": "analysis", "analysis_type": "comparative"},
            )

            # Extract scores if the model provides them
            scores = self._extract_scores(analysis_result, responses)

            # Extract recommendations if available
            recommendations = self._extract_recommendations(analysis_result)

            return create_result(
                module_name=self.name,
                summary=analysis_result,
                details={"prompt": meta_prompt, "response_count": len(responses)},
                scores=scores,
                recommendations=recommendations,
            )
        except Exception as e:
            logger.error(f"Error performing comparative analysis: {str(e)}")
            return create_result(
                module_name=self.name,
                summary=f"Error performing comparative analysis: {str(e)}",
                details={"error": str(e)},
                metadata={"error": True},
            )

    def _format_comparative_prompt(
        self, prompt: str, responses: List[Dict[str, Any]]
    ) -> str:
        """Format the comparative analysis prompt."""
        # Format the responses for inclusion in the meta prompt
        response_text = ""
        for i, resp in enumerate(responses, 1):
            model_name = resp.get("model", f"Model {i}")
            response_content = resp.get("response", "")
            response_text += (
                f"Response {i} (from {model_name}):\n{response_content}\n\n"
            )

        # Format the meta-analysis prompt (same as in enhanced_orchestrator.py)
        return f"""
You are a helpful assistant evaluating responses from multiple AI models to the same prompt.

Original Prompt:
{prompt}

Responses to analyze:
{response_text}

Your task is to analyze these responses and provide a detailed assessment of:
1. The strengths and weaknesses of each response
2. Which response is most helpful and why
3. What information is missing or could be improved in the responses
4. Any factual errors or inconsistencies between responses

Provide a comprehensive analysis that could help determine which response is best
and how the responses could be combined to create an optimal answer.
"""

    def _mock_comparative_analysis(
        self, prompt: str, responses: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate a basic mock analysis when no analysis model is available."""
        # Generate a simple comparative summary
        response_summaries = []
        for i, resp in enumerate(responses, 1):
            model_name = resp.get("model", f"Model {i}")
            response_length = len(resp.get("response", ""))
            response_summaries.append(
                f"Response {i} from {model_name}: {response_length} characters"
            )

        summary = "Simple comparative analysis:\n\n" + "\n".join(response_summaries)
        summary += "\n\nWithout an analysis model, only basic metrics are available."

        # Create basic scores based on length
        scores = {}
        for i, resp in enumerate(responses, 1):
            model_name = resp.get("model", f"Model {i}")
            response_length = len(resp.get("response", ""))
            # Simple normalized score based on length (0.5-1.0 range)
            max_length = max(len(r.get("response", "")) for r in responses)
            if max_length > 0:
                score = 0.5 + (response_length / max_length) * 0.5
            else:
                score = 0.5
            scores[model_name] = score

        return create_result(
            module_name=self.name,
            summary=summary,
            details={"response_count": len(responses)},
            scores=scores,
            recommendations=[
                "Use an analysis model for more detailed comparative analysis."
            ],
        )

    def _extract_scores(
        self, analysis: str, responses: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """Extract scores from the analysis text if possible."""
        # Simple mock implementation
        scores = {}
        for i, resp in enumerate(responses, 1):
            model_name = resp.get("model", f"Model {i}")
            # Assign a default score based on model priority or position
            scores[model_name] = 1.0 - (i - 1) * 0.1  # Simple decreasing scores

        return scores

    def _extract_recommendations(self, analysis: str) -> List[str]:
        """Extract recommendations from the analysis text if possible."""
        # Simple mock implementation
        return [
            "Combine elements from the highest-rated responses for an optimal answer."
        ]
