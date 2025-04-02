from dataclasses import dataclass
from typing import Dict, List, Optional
from string import Template

@dataclass
class AnalysisPattern:
    name: str
    description: str
    stages: List[str]
    templates: Dict[str, str]
    instructions: Dict[str, List[str]]

class AnalysisPatterns:
    GUT_ANALYSIS = AnalysisPattern(
        name="Gut Analysis",
        description="Relies on LLM intuition while considering other responses without assuming factual correctness",
        stages=["initial", "meta", "hyper", "ultra"],
        templates={
            "meta": """Original prompt: $original_prompt

Your initial response:
$own_response

Other LLM responses:
$other_responses

Please provide an edited version of your original response that:
1. Maintains your core insights
2. Incorporates any valuable perspectives from other responses
3. Addresses any potential gaps or limitations
4. Does not assume factual correctness of other responses
5. Preserves your unique analytical approach""",

            "hyper": """Original prompt: $original_prompt

Your meta response:
$own_meta

Other LLM meta responses:
$other_meta_responses

Please provide a refined version of your meta response that:
1. Strengthens your key arguments
2. Addresses any valid points from other responses
3. Maintains your analytical perspective
4. Highlights unique insights
5. Preserves your original reasoning""",

            "ultra": """Original prompt: $original_prompt

All hyper-level responses:
$hyper_responses

Please create a final synthesis that:
1. Preserves the unique analytical approaches
2. Highlights the most compelling insights
3. Maintains distinct perspectives
4. Emphasizes original reasoning
5. Presents a balanced view of different approaches"""
        },
        instructions={
            "meta": [
                "Maintain core insights",
                "Consider alternative perspectives",
                "Address potential gaps",
                "Preserve unique approach",
                "Question assumptions"
            ],
            "hyper": [
                "Strengthen arguments",
                "Address valid points",
                "Maintain perspective",
                "Highlight unique insights",
                "Preserve reasoning"
            ],
            "ultra": [
                "Preserve unique approaches",
                "Highlight compelling insights",
                "Maintain distinct perspectives",
                "Emphasize original reasoning",
                "Present balanced view"
            ]
        }
    )

    CONFIDENCE_ANALYSIS = AnalysisPattern(
        name="Confidence Analysis",
        description="Analyzes responses with confidence scoring and agreement tracking",
        stages=["initial", "meta", "hyper", "ultra"],
        templates={
            "meta": """Original prompt: $original_prompt

Your initial response:
$own_response

Other LLM responses:
$other_responses

Please analyze the responses and:
1. Identify key concepts and themes
2. Note areas of agreement/disagreement
3. Highlight unique perspectives
4. Identify consensus points
5. Evaluate the strength of different arguments""",

            "hyper": """Original prompt: $original_prompt

Your meta analysis:
$own_meta

Other LLM meta analyses:
$other_meta_responses

Please provide a refined analysis that:
1. Highlights consensus points
2. Identifies unique insights
3. Notes areas of disagreement
4. Evaluates argument strength
5. Suggests potential synthesis approaches""",

            "ultra": """Original prompt: $original_prompt

All hyper-level analyses:
$hyper_responses

Please create a final synthesis with:
1. Key points with confidence scores:
   - ⭐ Very High: Mentioned by all models with strong agreement
   - 🟢 High: Mentioned by all models
   - 🟡 Medium: Mentioned by 2-3 models
   - 🔴 Low: Mentioned by only 1 model
2. For each major point:
   - List which models mentioned it
   - Show the exact number of models in agreement
   - Explain why it received its confidence score
   - Note any variations in how different models presented it
3. Unique insights from each model
4. Areas of consensus
5. Summary of confidence distribution:
   - Number of points at each confidence level
   - Most common confidence level
   - Distribution of model agreement
6. Visualization suggestions:
   - Confidence Distribution Bar Chart:
     * X-axis: Confidence levels (Very High to Low)
     * Y-axis: Number of points
     * Color-coded bars matching confidence indicators
   - Model Agreement Matrix:
     * Rows: Key points
     * Columns: Models (Claude, ChatGPT, Gemini)
     * Checkmarks (✓) for agreement
     * Color-coded based on confidence level
   - Consensus Venn Diagram:
     * Three overlapping circles for each model
     * Numbered points in each section
     * Color-coded based on confidence level
   - Agreement Timeline:
     * X-axis: Analysis stages (Initial → Meta → Hyper)
     * Y-axis: Number of agreeing models
     * Lines for each major point
     * Color-coded based on final confidence level"""
        },
        instructions={
            "meta": [
                "Identify key concepts",
                "Note agreement/disagreement",
                "Highlight unique perspectives",
                "Identify consensus",
                "Evaluate arguments"
            ],
            "hyper": [
                "Highlight consensus",
                "Identify unique insights",
                "Note disagreements",
                "Evaluate arguments",
                "Suggest synthesis"
            ],
            "ultra": [
                "Score based on model agreement",
                "Attribute points to models",
                "Highlight unique insights",
                "Note consensus areas",
                "Provide scoring distribution",
                "Suggest visualizations"
            ]
        }
    )

    CRITIQUE_ANALYSIS = AnalysisPattern(
        name="Critique Analysis",
        description="Implements a structured critique and revision process",
        stages=["initial", "meta", "hyper", "ultra"],
        templates={
            "meta": """Original prompt: $original_prompt

Your initial response:
$own_response

Other LLM responses to critique:
$other_responses

Please provide a detailed critique that:
1. Identifies strengths and weaknesses
2. Notes similarities and differences
3. Suggests potential improvements
4. Highlights unique insights
5. Evaluates analytical approach""",

            "hyper": """Original prompt: $original_prompt

Your initial response:
$own_response

Critiques received:
$critiques

Please revise your response to:
1. Address valid critique points
2. Strengthen identified weaknesses
3. Maintain valuable unique elements
4. Incorporate helpful suggestions
5. Preserve core insights""",

            "ultra": """Original prompt: $original_prompt

All hyper-level revised responses:
$hyper_responses

Please create a final synthesis that:
1. Incorporates the best elements from all responses
2. Maintains unique valuable insights
3. Addresses key critique points
4. Presents balanced perspectives
5. Highlights the strongest arguments"""
        },
        instructions={
            "meta": [
                "Identify strengths/weaknesses",
                "Note similarities/differences",
                "Suggest improvements",
                "Highlight unique insights",
                "Evaluate approach"
            ],
            "hyper": [
                "Address valid critiques",
                "Strengthen weaknesses",
                "Maintain unique elements",
                "Incorporate suggestions",
                "Preserve core insights"
            ],
            "ultra": [
                "Incorporate best elements",
                "Maintain unique insights",
                "Address key critiques",
                "Present balanced view",
                "Highlight strong arguments"
            ]
        }
    )

    FACT_CHECK_ANALYSIS = AnalysisPattern(
        name="Fact Check Analysis",
        description="Implements a rigorous fact-checking process",
        stages=["initial", "meta", "hyper", "ultra"],
        templates={
            "meta": """Original prompt: $original_prompt

Your initial response:
$own_response

Other LLM responses to fact-check:
$other_responses

Please provide a detailed fact-check that:
1. Verifies factual claims
2. Identifies potential errors
3. Notes inconsistencies
4. Highlights supported claims
5. Evaluates evidence quality""",

            "hyper": """Original prompt: $original_prompt

Your initial response:
$own_response

Fact-check results:
$fact_checks

Please revise your response to:
1. Correct any factual errors
2. Strengthen evidence
3. Address inconsistencies
4. Support claims better
5. Maintain valid insights""",

            "ultra": """Original prompt: $original_prompt

All hyper-level fact-checked responses:
$hyper_responses

Please create a final synthesis that:
1. Ensures factual accuracy
2. Maintains strong evidence
3. Presents verified insights
4. Highlights well-supported claims
5. Notes confidence levels"""
        },
        instructions={
            "meta": [
                "Verify factual claims",
                "Identify potential errors",
                "Note inconsistencies",
                "Highlight supported claims",
                "Evaluate evidence"
            ],
            "hyper": [
                "Correct factual errors",
                "Strengthen evidence",
                "Address inconsistencies",
                "Support claims better",
                "Maintain valid insights"
            ],
            "ultra": [
                "Ensure factual accuracy",
                "Maintain strong evidence",
                "Present verified insights",
                "Highlight supported claims",
                "Note confidence levels"
            ]
        }
    )

    # Additional Analysis Patterns

    PERSPECTIVE_ANALYSIS = AnalysisPattern(
        name="Perspective Analysis",
        description="Focuses on different analytical perspectives and their integration",
        stages=["initial", "meta", "hyper", "ultra"],
        templates={
            "meta": """Original prompt: $original_prompt

Your initial response:
$own_response

Other LLM responses:
$other_responses

Please analyze the responses from different perspectives:
1. Technical vs. Strategic
2. Short-term vs. Long-term
3. Theoretical vs. Practical
4. Local vs. Global
5. Qualitative vs. Quantitative""",

            "hyper": """Original prompt: $original_prompt

Your meta analysis:
$own_meta

Other LLM meta analyses:
$other_meta_responses

Please provide a multi-perspective analysis that:
1. Integrates different viewpoints
2. Balances competing priorities
3. Highlights perspective-specific insights
4. Identifies perspective gaps
5. Suggests perspective combinations""",

            "ultra": """Original prompt: $original_prompt

All hyper-level analyses:
$hyper_responses

Please create a final synthesis that:
1. Integrates all perspectives
2. Highlights key insights from each
3. Identifies optimal combinations
4. Addresses perspective gaps
5. Provides balanced recommendations"""
        },
        instructions={
            "meta": [
                "Analyze technical/strategic",
                "Consider timeframes",
                "Evaluate theory/practice",
                "Assess scope",
                "Balance qualitative/quantitative"
            ],
            "hyper": [
                "Integrate viewpoints",
                "Balance priorities",
                "Highlight perspective insights",
                "Identify gaps",
                "Suggest combinations"
            ],
            "ultra": [
                "Integrate all perspectives",
                "Highlight key insights",
                "Identify optimal combinations",
                "Address gaps",
                "Provide balanced recommendations"
            ]
        }
    )

    SCENARIO_ANALYSIS = AnalysisPattern(
        name="Scenario Analysis",
        description="Analyzes responses through different scenarios and conditions",
        stages=["initial", "meta", "hyper", "ultra"],
        templates={
            "meta": """Original prompt: $original_prompt

Your initial response:
$own_response

Other LLM responses:
$other_responses

Please analyze the responses through scenarios:
1. Best case
2. Worst case
3. Most likely case
4. Edge cases
5. Alternative scenarios""",

            "hyper": """Original prompt: $original_prompt

Your meta analysis:
$own_meta

Other LLM meta analyses:
$other_meta_responses

Please provide a scenario-based analysis that:
1. Evaluates scenario robustness
2. Identifies scenario-specific insights
3. Highlights scenario dependencies
4. Notes scenario limitations
5. Suggests scenario combinations""",

            "ultra": """Original prompt: $original_prompt

All hyper-level analyses:
$hyper_responses

Please create a final synthesis that:
1. Integrates scenario insights
2. Highlights robust solutions
3. Identifies scenario dependencies
4. Addresses limitations
5. Provides scenario-based recommendations"""
        },
        instructions={
            "meta": [
                "Analyze best case",
                "Consider worst case",
                "Evaluate most likely case",
                "Assess edge cases",
                "Explore alternatives"
            ],
            "hyper": [
                "Evaluate robustness",
                "Identify scenario insights",
                "Highlight dependencies",
                "Note limitations",
                "Suggest combinations"
            ],
            "ultra": [
                "Integrate scenario insights",
                "Highlight robust solutions",
                "Identify dependencies",
                "Address limitations",
                "Provide scenario recommendations"
            ]
        }
    )

    @classmethod
    def get_pattern(cls, pattern_name: str) -> Optional[AnalysisPattern]:
        """Get an analysis pattern by name"""
        patterns = {
            "gut": cls.GUT_ANALYSIS,
            "confidence": cls.CONFIDENCE_ANALYSIS,
            "critique": cls.CRITIQUE_ANALYSIS,
            "fact_check": cls.FACT_CHECK_ANALYSIS,
            "perspective": cls.PERSPECTIVE_ANALYSIS,
            "scenario": cls.SCENARIO_ANALYSIS
        }
        return patterns.get(pattern_name.lower()) 