"""
Synthesis Feather Pattern for UltraAI

This module provides a specialized feather pattern for advanced synthesis
that enables multi-document analysis and complex information integration.
"""

from src.patterns.ultra_analysis_patterns import AnalysisPattern


class SynthesisFeather:
    """
    Synthesis Feather pattern specialized for multi-document analysis.
    This pattern excels at integrating complex information from multiple sources
    and distilling it into coherent, actionable insights.
    """

    ADVANCED_SYNTHESIS = AnalysisPattern(
        name="Advanced Synthesis",
        description=(
            "Integrates complex information from multiple documents into coherent "
            "insights and frameworks"
        ),
        stages=["initial", "meta", "hyper", "ultra"],
        templates={
            "initial": """Please analyze the following documents: {prompt}

Structure your synthesis as follows:
1. Document information inventory (key facts, assertions, evidence)
2. Cross-document thematic mapping
3. Identification of consensus vs. contradictions
4. Gap analysis for missing or incomplete information
5. Integration of key insights into a unified framework""",
            "meta": """Original synthesis task: $original_prompt

Your initial synthesis:
$own_response

Other synthesis approaches:
$other_responses

Please analyze the synthesis approaches by:
1. Evaluating information capture completeness
2. Assessing thematic organization effectiveness
3. Comparing contradiction handling methodologies
4. Evaluating framework coherence and utility
5. Identifying unique perspectives or insights across approaches""",
            "hyper": """Original synthesis task: $original_prompt

Your meta synthesis analysis:
$own_meta

Other meta analyses:
$other_meta_responses

Please create an enhanced synthesis that:
1. Captures all significant information with optimal organization
2. Resolves apparent contradictions with contextual explanation
3. Addresses identified gaps with explicit uncertainty markers
4. Creates a multi-level framework from granular to holistic views
5. Balances factual reporting with insightful interpretation
6. Preserves nuance while enabling actionable understanding""",
            "ultra": """Original synthesis task: $original_prompt

All hyper-level syntheses:
$hyper_responses

Please create a comprehensive synthesis system:
1. Present an integrated information model with clear provenance
2. Create multi-dimensional frameworks showing relationships and patterns
3. Include confidence assessments for key conclusions and interpretations
4. Develop actionable insights derived from the comprehensive synthesis
5. Provide navigable structure from executive summary to detailed analysis
6. Identify high-value areas for further investigation or clarification""",
        },
        instructions={
            "initial": [
                "Create information inventory",
                "Map cross-document themes",
                "Identify consensus/contradictions",
                "Analyze information gaps",
                "Integrate key insights",
            ],
            "meta": [
                "Evaluate information capture",
                "Assess thematic organization",
                "Compare contradiction handling",
                "Evaluate framework utility",
                "Identify unique insights",
            ],
            "hyper": [
                "Optimize information organization",
                "Resolve apparent contradictions",
                "Address identified gaps",
                "Create multi-level framework",
                "Balance reporting and interpretation",
                "Preserve nuance with clarity",
            ],
            "ultra": [
                "Create integrated information model",
                "Develop multi-dimensional frameworks",
                "Include confidence assessments",
                "Extract actionable insights",
                "Structure for multiple audiences",
                "Identify high-value investigation areas",
            ],
        },
    )

    @classmethod
    def get_pattern(cls) -> AnalysisPattern:
        """Get the Advanced Synthesis pattern"""
        return cls.ADVANCED_SYNTHESIS
