"""
Feedback Feather Pattern for UltraAI

This module provides a specialized feather pattern for feedback-oriented analysis
that enables iterative improvement and refinement of solutions.
"""

from src.patterns.ultra_analysis_patterns import AnalysisPattern


class FeedbackFeather:
    """
    Feedback Feather pattern specialized for iterative improvement.
    This pattern facilitates structured feedback cycles to progressively
    enhance solutions through systematic evaluation and refinement.
    """

    ITERATIVE_IMPROVEMENT = AnalysisPattern(
        name="Iterative Improvement",
        description=(
            "Structures feedback cycles for progressive enhancement through "
            "systematic evaluation and refinement"
        ),
        stages=["initial", "meta", "hyper", "ultra"],
        templates={
            "initial": """Please analyze the following solution: {prompt}

Structure your feedback as follows:
1. Core strengths assessment (what's working well)
2. Identified limitations or weaknesses
3. Specific improvement suggestions with rationale
4. Potential implementation challenges
5. Metrics for evaluating improved versions""",
            "meta": """Original feedback task: $original_prompt

Your initial feedback:
$own_response

Other feedback approaches:
$other_responses

Please analyze the feedback approaches by:
1. Comparing feedback depth and specificity
2. Evaluating balance between positive and constructive elements
3. Assessing actionability of improvement suggestions
4. Comparing evaluation criteria and metrics
5. Identifying unique insights across feedback perspectives""",
            "hyper": """Original feedback task: $original_prompt

Your meta feedback analysis:
$own_meta

Other meta analyses:
$other_meta_responses

Please create an enhanced feedback framework that:
1. Categorizes feedback by impact potential and implementation difficulty
2. Prioritizes improvements for maximum system enhancement
3. Addresses potential second-order effects of changes
4. Creates implementation pathways with specific steps
5. Develops detailed evaluation criteria for success measurement
6. Anticipates future improvement cycles beyond immediate changes""",
            "ultra": """Original feedback task: $original_prompt

All hyper-level feedback frameworks:
$hyper_responses

Please create a comprehensive feedback and improvement system:
1. Present an integrated feedback model with prioritized enhancements
2. Map improvement dependencies and optimal implementation sequence
3. Include detailed implementation guidance for key improvements
4. Develop before/after evaluation methodology with specific metrics
5. Create feedback collection framework for the next iteration
6. Balance immediate wins with strategic long-term improvements""",
        },
        instructions={
            "initial": [
                "Assess core strengths",
                "Identify limitations",
                "Suggest specific improvements",
                "Anticipate implementation challenges",
                "Define evaluation metrics",
            ],
            "meta": [
                "Compare feedback depth",
                "Evaluate feedback balance",
                "Assess suggestion actionability",
                "Compare evaluation criteria",
                "Identify unique insights",
            ],
            "hyper": [
                "Categorize by impact/difficulty",
                "Prioritize improvements",
                "Address second-order effects",
                "Create implementation pathways",
                "Develop detailed criteria",
                "Anticipate future cycles",
            ],
            "ultra": [
                "Integrate and prioritize feedback",
                "Map implementation sequence",
                "Provide implementation guidance",
                "Develop evaluation methodology",
                "Create feedback framework",
                "Balance short/long-term improvements",
            ],
        },
    )

    @classmethod
    def get_pattern(cls) -> AnalysisPattern:
        """Get the Iterative Improvement pattern"""
        return cls.ITERATIVE_IMPROVEMENT
