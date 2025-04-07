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

# Add pattern metadata that can be exported
PATTERN_METADATA = {
    "gut": "Relies on LLM intuition while considering other responses without assuming factual correctness",
    "confidence": "Analyzes responses with confidence scoring and agreement tracking",
    "critique": "Implements a structured critique and revision process",
    "fact_check": "Implements a rigorous fact-checking process",
    "perspective": "Focuses on different analytical perspectives and their integration",
    "scenario": "Analyzes responses through different scenarios and conditions",
    "stakeholder": "Analyzes from multiple stakeholder perspectives to reveal diverse interests and needs",
    "systems": "Maps complex system dynamics with feedback loops and leverage points",
    "time": "Analyzes across multiple time frames to balance short and long-term considerations",
    "innovation": "Uses cross-domain analogies to discover non-obvious patterns and solutions"
}

# Add these functions to expose pattern mapping
def get_pattern_mapping() -> Dict[str, AnalysisPattern]:
    """Get a mapping of pattern names to AnalysisPattern objects"""
    patterns = AnalysisPatterns()
    return {
        "gut": patterns.GUT_ANALYSIS,
        "confidence": patterns.CONFIDENCE_ANALYSIS,
        "critique": patterns.CRITIQUE_ANALYSIS,
        "fact_check": patterns.FACT_CHECK_ANALYSIS,
        "perspective": patterns.PERSPECTIVE_ANALYSIS,
        "scenario": patterns.SCENARIO_ANALYSIS,
        "stakeholder": patterns.STAKEHOLDER_VISION,
        "systems": patterns.SYSTEMS_MAPPER,
        "time": patterns.TIME_HORIZON,
        "innovation": patterns.INNOVATION_BRIDGE
    }

def get_pattern_config(pattern: str) -> Optional[Dict]:
    """Get configuration for a specific pattern"""
    patterns = get_pattern_mapping()
    if pattern not in patterns:
        return None

    pattern_obj = patterns[pattern]
    return {
        "name": pattern_obj.name,
        "description": pattern_obj.description,
        "stages": pattern_obj.stages,
        "templates": pattern_obj.templates,
        "instructions": pattern_obj.instructions
    }

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

    # New Intelligence Multiplication Methods

    STAKEHOLDER_VISION = AnalysisPattern(
        name="Stakeholder Vision",
        description="Analyzes from multiple stakeholder perspectives to reveal diverse interests and needs",
        stages=["initial", "meta", "hyper", "ultra"],
        templates={
            "initial": """Please analyze the following: {prompt}

Then re-analyze from the distinct perspectives of all key stakeholders:
1. List all significant stakeholders affected
2. For each stakeholder, describe their unique:
   a) Goals and success metrics
   b) Constraints and limitations
   c) Risks and concerns
   d) Likely reactions to various approaches""",

            "meta": """Original prompt: $original_prompt

Your initial stakeholder analysis:
$own_response

Other LLM stakeholder analyses:
$other_responses

Please map the stakeholder analyses by:
1. Identifying stakeholders present in all analyses vs. those missed by some
2. Noting consistent vs. contradictory stakeholder motivations
3. Analyzing potential coalition patterns and power dynamics
4. Creating a holistic ecosystem view of interconnected stakeholder relationships""",

            "hyper": """Original prompt: $original_prompt

Your meta stakeholder mapping:
$own_meta

Other LLM meta analyses:
$other_meta_responses

Please provide a refined stakeholder-based analysis that:
1. Identifies key stakeholder alignments and conflicts
2. Presents a comprehensive power and interest matrix
3. Suggests coalition-building opportunities
4. Reveals hidden stakeholder dependencies
5. Maps the full stakeholder ecosystem""",

            "ultra": """Original prompt: $original_prompt

All hyper-level stakeholder analyses:
$hyper_responses

Please create a stakeholder-integrated synthesis:
1. Present a comprehensive stakeholder map with interest alignment/conflicts
2. Suggest multi-win strategies addressing core stakeholder needs
3. Outline an implementation approach accounting for stakeholder dynamics
4. Provide a communication strategy tailored to each stakeholder group
5. Identify success metrics from multiple stakeholder perspectives"""
        },
        instructions={
            "initial": [
                "Identify all stakeholders",
                "Map stakeholder goals",
                "Assess constraints and limitations",
                "Evaluate risks and concerns",
                "Predict likely reactions"
            ],
            "meta": [
                "Compare stakeholder identification",
                "Analyze motivation consistency",
                "Map coalition patterns",
                "Create ecosystem view"
            ],
            "hyper": [
                "Identify alignments/conflicts",
                "Create power/interest matrix",
                "Suggest coalition opportunities",
                "Reveal hidden dependencies",
                "Map stakeholder ecosystem"
            ],
            "ultra": [
                "Create comprehensive stakeholder map",
                "Suggest multi-win strategies",
                "Design implementation approach",
                "Tailor communication strategy",
                "Identify multi-stakeholder metrics"
            ]
        }
    )

    SYSTEMS_MAPPER = AnalysisPattern(
        name="Systems Mapper",
        description="Maps complex system dynamics with feedback loops and leverage points",
        stages=["initial", "meta", "hyper", "ultra"],
        templates={
            "initial": """Please analyze the following: {prompt}

Using systems thinking methodology:
1. Map the system components and their interconnections
2. Identify key feedback loops (reinforcing and balancing)
3. Locate potential leverage points where small changes yield large effects
4. Anticipate emergent properties and second-order consequences""",

            "meta": """Original prompt: $original_prompt

Your initial systems analysis:
$own_response

Other LLM systems analyses:
$other_responses

Please integrate the system models by:
1. Creating a composite system map incorporating all identified elements
2. Analyzing feedback dynamics identified by multiple models
3. Comparing consensus vs. disputed leverage points
4. Developing a comprehensive view of potential unintended consequences""",

            "hyper": """Original prompt: $original_prompt

Your meta systems integration:
$own_meta

Other LLM meta analyses:
$other_meta_responses

Please provide a refined systems analysis that:
1. Presents a fully integrated causal loop diagram
2. Quantifies relative impact of different leverage points
3. Models system behavior under different intervention scenarios
4. Anticipates emergent properties and non-linear effects
5. Identifies critical thresholds and tipping points""",

            "ultra": """Original prompt: $original_prompt

All hyper-level systems analyses:
$hyper_responses

Please create a systems-based synthesis:
1. Present an integrated system model with causal loop diagrams
2. Identify high-leverage intervention points with expected system effects
3. Outline an implementation strategy accounting for feedback dynamics
4. Develop a monitoring framework for system behavior and emergent properties
5. Provide a timeline of expected system changes with key indicators"""
        },
        instructions={
            "initial": [
                "Map system components",
                "Identify feedback loops",
                "Locate leverage points",
                "Anticipate emergent properties"
            ],
            "meta": [
                "Create composite system map",
                "Analyze feedback dynamics",
                "Compare leverage points",
                "Assess unintended consequences"
            ],
            "hyper": [
                "Create causal loop diagram",
                "Quantify leverage impacts",
                "Model intervention scenarios",
                "Anticipate non-linear effects",
                "Identify critical thresholds"
            ],
            "ultra": [
                "Present integrated system model",
                "Identify high-leverage points",
                "Design feedback-aware strategy",
                "Develop monitoring framework",
                "Map system change timeline"
            ]
        }
    )

    TIME_HORIZON = AnalysisPattern(
        name="Time Horizon",
        description="Analyzes across multiple time frames to balance short and long-term considerations",
        stages=["initial", "meta", "hyper", "ultra"],
        templates={
            "initial": """Please analyze the following: {prompt}

Then reframe your analysis across three time horizons:
1. IMMEDIATE (0-1 year): Short-term actions and consequences
2. TRANSITIONAL (1-5 years): Medium-term developments and adaptations
3. HORIZON (5-20+ years): Long-term transformational possibilities

For each timeframe, consider what differs in your analysis and recommendations.""",

            "meta": """Original prompt: $original_prompt

Your initial temporal analysis:
$own_response

Other LLM temporal analyses:
$other_responses

Please compare the temporal analyses by:
1. Identifying temporal consistency vs. divergence across models
2. Analyzing short-term vs. long-term tradeoffs identified
3. Mapping critical transition points where futures diverge
4. Evaluating time-horizon biases in different models' thinking""",

            "hyper": """Original prompt: $original_prompt

Your meta temporal comparison:
$own_meta

Other LLM meta analyses:
$other_meta_responses

Please provide a refined temporal analysis that:
1. Creates a coherent timeline across all time horizons
2. Identifies key decision points that affect future trajectories
3. Analyzes dependencies between short and long-term actions
4. Evaluates opportunity costs across different time horizons
5. Outlines a temporal decision framework""",

            "ultra": """Original prompt: $original_prompt

All hyper-level temporal analyses:
$hyper_responses

Please create a temporally-integrated synthesis:
1. Present a time-coherent roadmap linking immediate actions to long-term goals
2. Design an adaptive strategy with explicit time-based decision points
3. Balance present vs. future capability investments with optimal sequencing
4. Stratify recommendations by time-criticality and time-horizon
5. Identify temporal flexibility areas vs. time-sensitive commitments"""
        },
        instructions={
            "initial": [
                "Analyze immediate impacts",
                "Explore transitional developments",
                "Project long-term possibilities",
                "Compare across timeframes"
            ],
            "meta": [
                "Identify temporal consistency",
                "Analyze time-based tradeoffs",
                "Map transition points",
                "Evaluate time biases"
            ],
            "hyper": [
                "Create coherent timeline",
                "Identify key decision points",
                "Analyze temporal dependencies",
                "Evaluate opportunity costs",
                "Design decision framework"
            ],
            "ultra": [
                "Present time-coherent roadmap",
                "Design adaptive strategy",
                "Balance capability investments",
                "Stratify by time-criticality",
                "Identify temporal flexibility"
            ]
        }
    )

    INNOVATION_BRIDGE = AnalysisPattern(
        name="Innovation Bridge",
        description="Uses cross-domain analogies to discover non-obvious patterns and solutions",
        stages=["initial", "meta", "hyper", "ultra"],
        templates={
            "initial": """Please analyze the following: {prompt}

Then identify at least 3 analogies from different domains (e.g., biology, physics, history, other industries) that offer insight into this situation. For each analogy explain:
1. The pattern similarity
2. Insights derived from the analogy
3. Limitations of the analogy""",

            "meta": """Original prompt: $original_prompt

Your initial analogical analysis:
$own_response

Other LLM analogical analyses:
$other_responses

Please analyze the analogies across all models by:
1. Identifying the most powerful recurring analogical patterns
2. Highlighting novel cross-domain insights unique to specific models
3. Exploring potential new analogies by combining elements
4. Evaluating which insights are revealed only through analogical thinking""",

            "hyper": """Original prompt: $original_prompt

Your meta analogical mapping:
$own_meta

Other LLM meta analyses:
$other_meta_responses

Please provide a refined analogical analysis that:
1. Develops composite analogies building on multiple domains
2. Creates a unified analogical framework across domains
3. Extracts key principles that transcend specific analogies
4. Maps novel solution approaches directly from analogical insights
5. Evaluates limitations of the analogical approach""",

            "ultra": """Original prompt: $original_prompt

All hyper-level analogical analyses:
$hyper_responses

Please create an analogical synthesis:
1. Present the most illuminating cross-domain patterns with implementation implications
2. Develop a composite analogical model drawing best elements from each analogy
3. Outline novel solution approaches inspired by analogical reasoning
4. Translate analogical insights into practical applications
5. Create an innovation framework based on cross-domain knowledge transfer"""
        },
        instructions={
            "initial": [
                "Identify domain analogies",
                "Extract pattern similarities",
                "Derive analogical insights",
                "Acknowledge limitations"
            ],
            "meta": [
                "Map recurring patterns",
                "Highlight unique insights",
                "Explore combined analogies",
                "Evaluate analogical discoveries"
            ],
            "hyper": [
                "Develop composite analogies",
                "Create unified framework",
                "Extract transcendent principles",
                "Map novel solutions",
                "Evaluate approach limitations"
            ],
            "ultra": [
                "Present illuminating patterns",
                "Develop composite model",
                "Outline novel approaches",
                "Translate to applications",
                "Create innovation framework"
            ]
        }
    )

    @classmethod
    def get_pattern(cls, pattern_name: str) -> Optional[AnalysisPattern]:
        """Legacy method to get a pattern by name (kept for backwards compatibility)"""
        patterns_map = get_pattern_mapping()
        return patterns_map.get(pattern_name)