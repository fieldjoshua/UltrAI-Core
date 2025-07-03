"""
Enhanced Ultra Synthesis™ Prompts

This module contains sophisticated prompt templates for different query types
to achieve true intelligence multiplication in the synthesis stage.
"""

from typing import Dict, Any, Optional
from enum import Enum


class QueryType(Enum):
    """Types of queries that require different synthesis approaches."""
    TECHNICAL = "technical"
    CREATIVE = "creative"
    ANALYTICAL = "analytical"
    PROCEDURAL = "procedural"
    PHILOSOPHICAL = "philosophical"
    GENERAL = "general"


class SynthesisPromptManager:
    """Manages enhanced synthesis prompts for Ultra Synthesis™."""
    
    def __init__(self):
        self.prompts = {
            QueryType.TECHNICAL: self._get_technical_prompt(),
            QueryType.CREATIVE: self._get_creative_prompt(),
            QueryType.ANALYTICAL: self._get_analytical_prompt(),
            QueryType.PROCEDURAL: self._get_procedural_prompt(),
            QueryType.PHILOSOPHICAL: self._get_philosophical_prompt(),
            QueryType.GENERAL: self._get_general_prompt(),
        }
    
    def detect_query_type(self, query: str) -> QueryType:
        """
        Detect the type of query to select appropriate synthesis template.
        
        Args:
            query: The original user query
            
        Returns:
            QueryType: The detected query type
        """
        query_lower = query.lower()
        
        # Technical indicators
        technical_keywords = [
            'how does', 'explain', 'technical', 'algorithm', 'implement',
            'code', 'debug', 'error', 'architecture', 'system', 'api',
            'database', 'performance', 'optimize', 'security'
        ]
        
        # Creative indicators
        creative_keywords = [
            'create', 'design', 'imagine', 'story', 'write', 'compose',
            'invent', 'brainstorm', 'creative', 'innovative', 'novel',
            'artistic', 'generate ideas'
        ]
        
        # Analytical indicators
        analytical_keywords = [
            'analyze', 'compare', 'evaluate', 'assess', 'examine',
            'investigate', 'study', 'review', 'critique', 'pros and cons',
            'advantages', 'disadvantages', 'trade-offs'
        ]
        
        # Procedural indicators
        procedural_keywords = [
            'how to', 'steps', 'process', 'procedure', 'guide',
            'instructions', 'tutorial', 'walkthrough', 'method',
            'approach', 'recipe', 'plan'
        ]
        
        # Philosophical indicators
        philosophical_keywords = [
            'why', 'meaning', 'purpose', 'ethics', 'moral', 'philosophy',
            'believe', 'think about', 'implications', 'consequences',
            'should', 'ought', 'values', 'principles'
        ]
        
        # Count keyword matches
        scores = {
            QueryType.TECHNICAL: sum(1 for kw in technical_keywords if kw in query_lower),
            QueryType.CREATIVE: sum(1 for kw in creative_keywords if kw in query_lower),
            QueryType.ANALYTICAL: sum(1 for kw in analytical_keywords if kw in query_lower),
            QueryType.PROCEDURAL: sum(1 for kw in procedural_keywords if kw in query_lower),
            QueryType.PHILOSOPHICAL: sum(1 for kw in philosophical_keywords if kw in query_lower),
        }
        
        # Return the type with highest score, default to GENERAL
        max_score = max(scores.values())
        if max_score == 0:
            return QueryType.GENERAL
            
        return max(scores.items(), key=lambda x: x[1])[0]
    
    def get_synthesis_prompt(
        self, 
        original_query: str,
        model_responses: str,
        query_type: Optional[QueryType] = None
    ) -> str:
        """
        Get the appropriate synthesis prompt based on query type.
        
        Args:
            original_query: The original user query
            model_responses: The formatted model responses to synthesize
            query_type: Optional query type override
            
        Returns:
            str: The formatted synthesis prompt
        """
        if query_type is None:
            query_type = self.detect_query_type(original_query)
            
        template = self.prompts[query_type]
        
        return template.format(
            original_prompt=original_query,
            model_responses=model_responses
        )
    
    def _get_general_prompt(self) -> str:
        """General purpose synthesis prompt with enhanced intelligence multiplication."""
        return """# Ultra Synthesis™ Intelligence Multiplication Task

## Original Query
{original_prompt}

## Peer-Reviewed Model Responses
{model_responses}

## Synthesis Objectives
Create a comprehensive synthesis that achieves true intelligence multiplication by:

### 1. Convergent Truth Extraction
- Identify facts and insights that multiple models agree on (highest confidence)
- Weight agreement by relevance to the query
- Flag any critical disagreements that affect core understanding

### 2. Complementary Intelligence Integration
- Combine unique valuable insights from each model's perspective
- Identify how different analytical frameworks enhance understanding
- Create emergent insights by connecting disparate observations

### 3. Uncertainty Management
- Clearly indicate confidence levels for different claims
- Acknowledge areas of legitimate disagreement or uncertainty
- Provide balanced perspective on contentious points

### 4. Structured Knowledge Synthesis
- Organize information in the most logical flow for the query
- Use clear hierarchical structure with headers where appropriate
- Ensure smooth transitions between concepts

### 5. Meta-Cognitive Enhancement
- Identify the reasoning patterns that led to the best insights
- Synthesize not just content but analytical approaches
- Highlight particularly innovative or insightful contributions

## Output Requirements
- Begin directly with the synthesis (no preamble about the process)
- Integrate insights seamlessly rather than listing model outputs
- Include [High confidence], [Moderate confidence], or [Low confidence] markers where appropriate
- Ensure the synthesis provides MORE value than any individual response
- Focus on actionable, clear, and comprehensive information

## Synthesis:
"""

    def _get_technical_prompt(self) -> str:
        """Technical query synthesis prompt."""
        return """# Ultra Synthesis™ Technical Intelligence Multiplication

## Technical Query
{original_prompt}

## Expert Model Responses
{model_responses}

## Technical Synthesis Framework

### 1. Technical Accuracy Verification
- Cross-validate technical facts across model responses
- Identify consensus on technical specifications
- Flag any technical contradictions requiring clarification

### 2. Implementation Depth Synthesis
- Combine practical implementation details from all models
- Integrate code examples and technical specifics
- Synthesize best practices and optimization strategies

### 3. Architecture and Design Patterns
- Merge architectural insights and design considerations
- Identify common patterns and anti-patterns mentioned
- Create comprehensive technical overview

### 4. Edge Cases and Limitations
- Compile all mentioned edge cases and limitations
- Synthesize error handling strategies
- Integrate performance considerations

### 5. Technical Recommendations
- Provide clear, actionable technical guidance
- Include confidence levels: [Verified], [Best Practice], [Experimental]
- Prioritize recommendations by impact and feasibility

## Structure Requirements
- Use technical terminology precisely
- Include code snippets where valuable
- Organize by: Overview → Core Concepts → Implementation → Considerations
- Provide clear technical conclusion

## Technical Synthesis:
"""

    def _get_creative_prompt(self) -> str:
        """Creative query synthesis prompt."""
        return """# Ultra Synthesis™ Creative Intelligence Multiplication

## Creative Challenge
{original_prompt}

## Creative Model Contributions
{model_responses}

## Creative Synthesis Approach

### 1. Idea Convergence and Divergence
- Identify common creative themes across responses
- Highlight unique creative angles from each model
- Build on creative synergies between ideas

### 2. Innovation Amplification
- Combine creative elements to generate novel concepts
- Push boundaries by merging different creative approaches
- Create unexpected connections between ideas

### 3. Practical Creative Framework
- Synthesize actionable creative strategies
- Provide structured approach to creative execution
- Balance innovation with feasibility

### 4. Inspiration Integration
- Weave together inspirational elements
- Create cohesive creative narrative
- Maintain energy and enthusiasm throughout

### 5. Creative Possibilities Expansion
- Suggest variations and extensions of ideas
- Provide creative springboards for further exploration
- Include "What if..." scenarios

## Creative Output Guidelines
- Maintain creative energy and flow
- Use vivid, engaging language
- Structure as: Inspiration → Core Ideas → Variations → Next Steps
- End with creative momentum

## Creative Synthesis:
"""

    def _get_analytical_prompt(self) -> str:
        """Analytical query synthesis prompt."""
        return """# Ultra Synthesis™ Analytical Intelligence Multiplication

## Analytical Question
{original_prompt}

## Model Analyses
{model_responses}

## Analytical Synthesis Framework

### 1. Multi-Perspective Analysis Integration
- Compare analytical frameworks used by different models
- Identify complementary analytical angles
- Synthesize comprehensive analytical coverage

### 2. Evidence and Data Synthesis
- Compile all supporting evidence and data points
- Cross-reference factual claims
- Weight evidence by reliability and relevance

### 3. Comparative Insights
- Merge comparative analyses from all models
- Identify consensus on key comparisons
- Highlight unique comparative insights

### 4. Critical Evaluation Synthesis
- Integrate critical assessments
- Balance different evaluative perspectives
- Provide nuanced, multi-faceted evaluation

### 5. Analytical Conclusions
- Synthesize key findings with confidence levels
- Provide clear analytical takeaways
- Suggest areas for further analysis

## Analytical Structure
- Use clear analytical categories
- Include [Strong Evidence], [Moderate Evidence], [Limited Evidence] markers
- Organize as: Overview → Analysis → Comparison → Evaluation → Conclusions
- Maintain objectivity while acknowledging different viewpoints

## Analytical Synthesis:
"""

    def _get_procedural_prompt(self) -> str:
        """Procedural query synthesis prompt."""
        return """# Ultra Synthesis™ Procedural Intelligence Multiplication

## Procedural Request
{original_prompt}

## Model Procedures
{model_responses}

## Procedural Synthesis Method

### 1. Step Consolidation and Optimization
- Merge procedural steps from all models
- Identify optimal sequence and dependencies
- Eliminate redundancies while preserving completeness

### 2. Best Practices Integration
- Compile tips and best practices from all responses
- Highlight consensus on critical steps
- Include warnings and common pitfalls

### 3. Alternative Approaches
- Synthesize different methodological approaches
- Provide options for different contexts/constraints
- Include decision criteria for choosing approaches

### 4. Practical Considerations
- Merge practical tips and real-world considerations
- Include time estimates and difficulty indicators
- Add troubleshooting guidance

### 5. Success Criteria and Validation
- Synthesize success indicators from all models
- Provide clear validation checkpoints
- Include quality assurance steps

## Procedural Output Format
- Number steps clearly and logically
- Use action-oriented language
- Include [Required], [Recommended], [Optional] tags
- Structure as: Overview → Prerequisites → Steps → Validation → Tips
- End with clear success criteria

## Procedural Synthesis:
"""

    def _get_philosophical_prompt(self) -> str:
        """Philosophical query synthesis prompt."""
        return """# Ultra Synthesis™ Philosophical Intelligence Multiplication

## Philosophical Inquiry
{original_prompt}

## Model Perspectives
{model_responses}

## Philosophical Synthesis Approach

### 1. Perspective Integration
- Weave together different philosophical viewpoints
- Identify common ethical/philosophical threads
- Respect diversity of philosophical traditions

### 2. Depth and Nuance
- Synthesize deeper implications from all responses
- Explore nuanced arguments and counterarguments
- Build comprehensive philosophical landscape

### 3. Practical Philosophy
- Connect philosophical insights to practical implications
- Provide actionable philosophical framework
- Balance theory with real-world application

### 4. Ethical Considerations
- Integrate ethical dimensions from all perspectives
- Present balanced view of ethical implications
- Include different ethical frameworks

### 5. Wisdom Synthesis
- Distill collective wisdom from all responses
- Provide thoughtful, balanced conclusions
- Suggest paths for further reflection

## Philosophical Structure
- Use clear, accessible language for complex ideas
- Include different schools of thought
- Mark speculative ideas with [Philosophical perspective]
- Structure as: Context → Perspectives → Analysis → Implications → Reflection
- End with thought-provoking synthesis

## Philosophical Synthesis:
"""