"""
Educational Feather Pattern for UltraAI

This module provides a specialized feather pattern for educational purposes
that helps optimize learning experiences and knowledge acquisition.
"""

from src.patterns.ultra_analysis_patterns import AnalysisPattern


class EducationalFeather:
    """
    Educational Feather pattern specialized for learning optimization scenarios.
    This pattern helps users learn more effectively by structuring information
    in pedagogically sound ways and adapting to different learning styles.
    """

    LEARNING_OPTIMIZATION = AnalysisPattern(
        name="Learning Optimization",
        description=(
            "Structures information for optimal educational outcomes "
            "with multi-modal approach"
        ),
        stages=["initial", "meta", "hyper", "ultra"],
        templates={
            "initial": """Please analyze the following learning topic: {prompt}

Structure your response as an optimized learning module with:
1. Core concepts clearly defined (with visual metaphors where applicable)
2. Conceptual framework showing how ideas interconnect
3. Progressive difficulty levels (beginner to advanced)
4. Common misconceptions and clarifications
5. Practical applications and examples""",
            "meta": """Original learning topic: $original_prompt

Your initial learning module:
$own_response

Other learning approaches:
$other_responses

Please analyze these learning approaches by:
1. Identifying strengths and weaknesses of each approach
2. Comparing conceptual frameworks and organization
3. Evaluating clarity, accessibility, and engagement potential
4. Noting unique insights or explanations across approaches
5. Assessing alignment with different learning styles
   (visual, auditory, kinesthetic, reading/writing)""",
            "hyper": """Original learning topic: $original_prompt

Your meta learning analysis:
$own_meta

Other meta analyses:
$other_meta_responses

Please create an enhanced learning module that:
1. Integrates the most effective explanatory approaches
2. Structures information for optimal retention and recall
3. Addresses diverse learning styles
4. Incorporates formative assessment opportunities
5. Builds connections to related knowledge domains
6. Creates learning pathways based on different prior knowledge levels""",
            "ultra": """Original learning topic: $original_prompt

All hyper-level learning modules:
$hyper_responses

Please synthesize a comprehensive learning experience:
1. Present a multi-modal learning structure with clear pathways
2. Include conceptual frameworks, practical applications, and assessments
3. Create scaffolded learning progression with difficulty indicators
4. Integrate visual, textual, and interactive elements
5. Develop a knowledge map showing prerequisite and advanced concepts
6. Design learning milestones with self-assessment checkpoints""",
        },
        instructions={
            "initial": [
                "Define core concepts",
                "Create conceptual framework",
                "Structure progressive difficulty",
                "Address misconceptions",
                "Provide practical applications",
            ],
            "meta": [
                "Analyze teaching approaches",
                "Compare conceptual frameworks",
                "Evaluate clarity and engagement",
                "Note unique explanations",
                "Assess learning style alignment",
            ],
            "hyper": [
                "Integrate effective approaches",
                "Structure for retention",
                "Address learning styles",
                "Include assessment opportunities",
                "Build knowledge connections",
                "Create personalized pathways",
            ],
            "ultra": [
                "Create multi-modal structure",
                "Balance theory and application",
                "Develop scaffolded progression",
                "Integrate diverse elements",
                "Map knowledge relationships",
                "Design assessment checkpoints",
            ],
        },
    )

    @classmethod
    def get_pattern(cls) -> AnalysisPattern:
        """Get the Learning Optimization pattern"""
        return cls.LEARNING_OPTIMIZATION
