"""
Collaborative Feather Pattern for UltraAI

This module provides a specialized feather pattern for team collaboration
that enhances group analysis and decision-making processes.
"""

from src.patterns.ultra_analysis_patterns import AnalysisPattern


class CollaborativeFeather:
    """
    Collaborative Feather pattern specialized for team analysis scenarios.
    This pattern facilitates collaborative intelligence by structuring team
    interactions and synthesizing diverse inputs for better outcomes.
    """

    TEAM_ANALYSIS = AnalysisPattern(
        name="Team Analysis",
        description=(
            "Structures collaborative analysis to harness diverse perspectives "
            "and optimize team decision-making"
        ),
        stages=["initial", "meta", "hyper", "ultra"],
        templates={
            "initial": """Please analyze the following team challenge: {prompt}

Structure your response as a collaborative analysis framework with:
1. Problem decomposition into distinct analysis components
2. Clear definition of key decision points and criteria
3. Role-based analysis perspectives (technical, strategic, operational)
4. Information sharing protocols for effective collaboration
5. Methods to identify and resolve conflicting viewpoints""",
            "meta": """Original team challenge: $original_prompt

Your initial collaborative framework:
$own_response

Other collaborative approaches:
$other_responses

Please analyze the collaborative approaches by:
1. Evaluating communication efficiency and effectiveness
2. Assessing how well diverse perspectives are integrated
3. Identifying potential collaboration bottlenecks
4. Comparing knowledge-sharing mechanisms
5. Evaluating decision-making process quality""",
            "hyper": """Original team challenge: $original_prompt

Your meta collaboration analysis:
$own_meta

Other meta analyses:
$other_meta_responses

Please create an enhanced collaborative framework that:
1. Optimizes information flow between team members
2. Structures decision-making to leverage diverse expertise
3. Implements conflict resolution mechanisms
4. Balances individual contributions with group consensus
5. Creates adaptive team processes for different challenge types
6. Addresses common team cognitive biases""",
            "ultra": """Original team challenge: $original_prompt

All hyper-level collaborative frameworks:
$hyper_responses

Please synthesize a comprehensive team analysis system:
1. Present an integrated collaboration model with defined roles and workflows
2. Include balanced decision frameworks with explicit perspective integration
3. Create transparent information sharing protocols with feedback mechanisms
4. Develop contingency processes for handling unexpected inputs
5. Establish quality metrics for both the process and outcomes
6. Design review mechanisms to improve future collaborations""",
        },
        instructions={
            "initial": [
                "Decompose the problem",
                "Define decision points",
                "Structure role perspectives",
                "Create information protocols",
                "Design conflict resolution",
            ],
            "meta": [
                "Evaluate communication",
                "Assess perspective integration",
                "Identify bottlenecks",
                "Compare knowledge sharing",
                "Evaluate decision quality",
            ],
            "hyper": [
                "Optimize information flow",
                "Structure decision-making",
                "Implement conflict resolution",
                "Balance individual and group",
                "Create adaptive processes",
                "Address cognitive biases",
            ],
            "ultra": [
                "Integrate collaboration model",
                "Balance decision frameworks",
                "Create transparent protocols",
                "Develop contingency processes",
                "Establish quality metrics",
                "Design review mechanisms",
            ],
        },
    )

    @classmethod
    def get_pattern(cls) -> AnalysisPattern:
        """Get the Team Analysis pattern"""
        return cls.TEAM_ANALYSIS
