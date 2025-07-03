"""
Advanced Output Structure for Ultra Synthesis™

This module provides structured output formatting with confidence levels,
consensus indicators, and optional metadata for synthesis results.
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import re
from collections import Counter


class ConfidenceLevel(Enum):
    """Confidence levels for synthesis claims."""
    HIGH = "High confidence"
    MODERATE = "Moderate confidence"
    LOW = "Low confidence"
    UNCERTAIN = "Uncertain"


@dataclass
class SynthesisMetadata:
    """Metadata about the synthesis process."""
    contributing_models: List[str]
    total_models_attempted: int
    synthesis_model: str
    query_type: str
    consensus_topics: List[str]
    divergent_topics: List[str]
    key_insights: List[str]
    confidence_distribution: Dict[str, int]
    synthesis_patterns_used: List[str]


class StructuredSynthesisOutput:
    """
    Provides structured output formatting for Ultra Synthesis™ results
    with confidence indicators and metadata.
    """
    
    def __init__(self):
        self.confidence_patterns = {
            ConfidenceLevel.HIGH: [
                r"all models agree",
                r"unanimous",
                r"consistently",
                r"definitively",
                r"clearly established",
                r"strong consensus",
                r"verified across",
            ],
            ConfidenceLevel.MODERATE: [
                r"most models",
                r"generally agree",
                r"broadly consistent",
                r"some variation",
                r"mostly aligned",
                r"moderate consensus",
            ],
            ConfidenceLevel.LOW: [
                r"mixed opinions",
                r"some models suggest",
                r"limited agreement",
                r"conflicting views",
                r"uncertain",
                r"debated",
            ]
        }
    
    def analyze_synthesis_confidence(
        self,
        synthesis_text: str,
        model_responses: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Analyze confidence levels in the synthesis based on model agreement.
        
        Args:
            synthesis_text: The final synthesis text
            model_responses: Original model responses for comparison
            
        Returns:
            Dictionary with confidence analysis
        """
        # Extract sentences/claims from synthesis
        sentences = self._extract_sentences(synthesis_text)
        
        confidence_scores = []
        confidence_distribution = {
            ConfidenceLevel.HIGH.value: 0,
            ConfidenceLevel.MODERATE.value: 0,
            ConfidenceLevel.LOW.value: 0,
            ConfidenceLevel.UNCERTAIN.value: 0
        }
        
        for sentence in sentences:
            confidence = self._assess_sentence_confidence(sentence, model_responses)
            confidence_scores.append(confidence)
            confidence_distribution[confidence.value] += 1
        
        # Calculate overall confidence
        confidence_weights = {
            ConfidenceLevel.HIGH: 1.0,
            ConfidenceLevel.MODERATE: 0.7,
            ConfidenceLevel.LOW: 0.4,
            ConfidenceLevel.UNCERTAIN: 0.1
        }
        
        total_weight = sum(
            confidence_weights[level] * count 
            for level_str, count in confidence_distribution.items()
            for level in ConfidenceLevel 
            if level.value == level_str
        )
        
        overall_confidence = total_weight / len(sentences) if sentences else 0.5
        
        return {
            "overall_confidence": overall_confidence,
            "confidence_distribution": confidence_distribution,
            "total_claims": len(sentences),
            "confidence_level": self._get_overall_confidence_level(overall_confidence)
        }
    
    def calculate_consensus_degree(
        self,
        model_responses: Dict[str, str],
        synthesis_text: str
    ) -> Dict[str, Any]:
        """
        Calculate the degree of consensus among models.
        
        Args:
            model_responses: Dictionary of model responses
            synthesis_text: The final synthesis
            
        Returns:
            Dictionary with consensus metrics
        """
        # Extract key concepts from each response
        model_concepts = {}
        for model, response in model_responses.items():
            concepts = self._extract_key_concepts(response)
            model_concepts[model] = concepts
        
        # Find consensus topics (mentioned by multiple models)
        all_concepts = []
        for concepts in model_concepts.values():
            all_concepts.extend(concepts)
        
        concept_counts = Counter(all_concepts)
        total_models = len(model_responses)
        
        # Categorize consensus levels
        high_consensus = [
            concept for concept, count in concept_counts.items()
            if count >= total_models * 0.8
        ]
        
        moderate_consensus = [
            concept for concept, count in concept_counts.items()
            if total_models * 0.5 <= count < total_models * 0.8
        ]
        
        low_consensus = [
            concept for concept, count in concept_counts.items()
            if total_models * 0.2 <= count < total_models * 0.5
        ]
        
        unique_insights = [
            concept for concept, count in concept_counts.items()
            if count == 1
        ]
        
        # Calculate consensus score
        consensus_score = (
            len(high_consensus) * 1.0 + 
            len(moderate_consensus) * 0.5 + 
            len(low_consensus) * 0.2
        ) / len(set(all_concepts)) if all_concepts else 0
        
        return {
            "consensus_score": consensus_score,
            "high_consensus_topics": high_consensus[:5],  # Top 5
            "moderate_consensus_topics": moderate_consensus[:5],
            "unique_insights": unique_insights[:5],
            "total_unique_concepts": len(set(all_concepts)),
            "consensus_level": self._get_consensus_level(consensus_score)
        }
    
    def extract_key_insights(
        self,
        synthesis_text: str,
        model_responses: Dict[str, str]
    ) -> List[str]:
        """
        Extract key insights from the synthesis.
        
        Args:
            synthesis_text: The synthesis text
            model_responses: Original model responses
            
        Returns:
            List of key insights
        """
        insights = []
        
        # Look for insight indicators
        insight_patterns = [
            r"(?:key insight|important to note|significantly|notably|crucially)[:\s]+([^.!?]+[.!?])",
            r"(?:this means|this suggests|this indicates)[:\s]+([^.!?]+[.!?])",
            r"(?:the implication|the significance)[:\s]+([^.!?]+[.!?])",
            r"(?:emergent|novel|unique) (?:insight|understanding|perspective)[:\s]+([^.!?]+[.!?])",
        ]
        
        for pattern in insight_patterns:
            matches = re.findall(pattern, synthesis_text, re.IGNORECASE)
            insights.extend(matches)
        
        # Look for insights that synthesize multiple perspectives
        synthesis_patterns = [
            r"(?:combining|integrating|synthesizing) .+ reveals[:\s]+([^.!?]+[.!?])",
            r"(?:across all models|collectively|together)[,\s]+([^.!?]+[.!?])",
        ]
        
        for pattern in synthesis_patterns:
            matches = re.findall(pattern, synthesis_text, re.IGNORECASE)
            insights.extend(matches)
        
        # Deduplicate and clean
        cleaned_insights = []
        seen = set()
        for insight in insights:
            cleaned = insight.strip()
            if cleaned and cleaned.lower() not in seen:
                seen.add(cleaned.lower())
                cleaned_insights.append(cleaned)
        
        return cleaned_insights[:10]  # Top 10 insights
    
    def format_synthesis_output(
        self,
        synthesis_text: str,
        model_responses: Dict[str, str],
        metadata: Dict[str, Any],
        include_metadata: bool = False,
        include_confidence: bool = True
    ) -> Dict[str, Any]:
        """
        Format the synthesis output with optional metadata and confidence indicators.
        
        Args:
            synthesis_text: The raw synthesis text
            model_responses: Dictionary of model responses used
            metadata: Additional metadata about the synthesis
            include_metadata: Whether to include detailed metadata
            include_confidence: Whether to include confidence analysis
            
        Returns:
            Formatted output dictionary
        """
        output = {
            "synthesis": synthesis_text,
            "quality_indicators": {}
        }
        
        if include_confidence:
            # Add confidence analysis
            confidence_analysis = self.analyze_synthesis_confidence(
                synthesis_text, 
                model_responses
            )
            output["quality_indicators"]["confidence"] = confidence_analysis
            
            # Add consensus analysis
            consensus_analysis = self.calculate_consensus_degree(
                model_responses,
                synthesis_text
            )
            output["quality_indicators"]["consensus"] = consensus_analysis
            
            # Add enhanced synthesis with confidence markers
            enhanced_text = self._add_confidence_markers(
                synthesis_text,
                confidence_analysis,
                consensus_analysis
            )
            output["synthesis_enhanced"] = enhanced_text
        
        if include_metadata:
            # Extract key insights
            key_insights = self.extract_key_insights(synthesis_text, model_responses)
            
            # Build metadata
            synthesis_metadata = SynthesisMetadata(
                contributing_models=list(model_responses.keys()),
                total_models_attempted=metadata.get("models_attempted", len(model_responses)),
                synthesis_model=metadata.get("synthesis_model", "unknown"),
                query_type=metadata.get("query_type", "general"),
                consensus_topics=consensus_analysis.get("high_consensus_topics", []) if include_confidence else [],
                divergent_topics=consensus_analysis.get("unique_insights", []) if include_confidence else [],
                key_insights=key_insights,
                confidence_distribution=confidence_analysis.get("confidence_distribution", {}) if include_confidence else {},
                synthesis_patterns_used=metadata.get("synthesis_patterns", [])
            )
            
            output["metadata"] = {
                "contributing_models": synthesis_metadata.contributing_models,
                "total_models": synthesis_metadata.total_models_attempted,
                "synthesis_model": synthesis_metadata.synthesis_model,
                "query_type": synthesis_metadata.query_type,
                "consensus_topics": synthesis_metadata.consensus_topics,
                "divergent_topics": synthesis_metadata.divergent_topics,
                "key_insights": synthesis_metadata.key_insights,
                "timestamp": metadata.get("timestamp", ""),
                "processing_time": metadata.get("processing_time", "")
            }
        
        return output
    
    def _extract_sentences(self, text: str) -> List[str]:
        """Extract sentences from text for analysis."""
        # Simple sentence extraction (can be improved with NLP)
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if len(s.strip()) > 20]
    
    def _assess_sentence_confidence(
        self,
        sentence: str,
        model_responses: Dict[str, str]
    ) -> ConfidenceLevel:
        """Assess confidence level of a sentence based on patterns and model agreement."""
        sentence_lower = sentence.lower()
        
        # Check for explicit confidence patterns
        for level, patterns in self.confidence_patterns.items():
            for pattern in patterns:
                if re.search(pattern, sentence_lower):
                    return level
        
        # Check how many models mention similar content
        models_mentioning = 0
        for response in model_responses.values():
            # Simple check - can be made more sophisticated
            key_words = [w for w in sentence.split() if len(w) > 4]
            if any(word in response for word in key_words[:3]):
                models_mentioning += 1
        
        # Determine confidence based on model agreement
        total_models = len(model_responses)
        if total_models > 0:
            agreement_ratio = models_mentioning / total_models
            if agreement_ratio >= 0.8:
                return ConfidenceLevel.HIGH
            elif agreement_ratio >= 0.5:
                return ConfidenceLevel.MODERATE
            elif agreement_ratio >= 0.2:
                return ConfidenceLevel.LOW
        
        return ConfidenceLevel.UNCERTAIN
    
    def _extract_key_concepts(self, text: str) -> List[str]:
        """Extract key concepts from text (simplified version)."""
        # This is a simplified extraction - in production, use NLP
        # Extract capitalized phrases and important terms
        concepts = []
        
        # Find capitalized phrases (likely important concepts)
        cap_phrases = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        concepts.extend(cap_phrases)
        
        # Find terms after "is/are"
        definitions = re.findall(r'(?:is|are)\s+(?:a|an|the)?\s*([^.,]+)', text, re.IGNORECASE)
        concepts.extend([d.strip() for d in definitions if len(d.strip()) < 50])
        
        # Clean and deduplicate
        cleaned = []
        seen = set()
        for concept in concepts:
            clean = concept.strip().lower()
            if clean and clean not in seen and len(clean) > 3:
                seen.add(clean)
                cleaned.append(concept.strip())
        
        return cleaned
    
    def _get_overall_confidence_level(self, score: float) -> str:
        """Convert numeric confidence score to descriptive level."""
        if score >= 0.8:
            return "Very High Confidence"
        elif score >= 0.6:
            return "High Confidence"
        elif score >= 0.4:
            return "Moderate Confidence"
        elif score >= 0.2:
            return "Low Confidence"
        else:
            return "Uncertain"
    
    def _get_consensus_level(self, score: float) -> str:
        """Convert numeric consensus score to descriptive level."""
        if score >= 0.8:
            return "Strong Consensus"
        elif score >= 0.6:
            return "Good Consensus"
        elif score >= 0.4:
            return "Moderate Consensus"
        elif score >= 0.2:
            return "Limited Consensus"
        else:
            return "Minimal Consensus"
    
    def _add_confidence_markers(
        self,
        text: str,
        confidence_analysis: Dict[str, Any],
        consensus_analysis: Dict[str, Any]
    ) -> str:
        """Add confidence markers to the synthesis text."""
        # Add a header with overall metrics
        header = f"""📊 **Synthesis Quality Metrics:**
- Overall Confidence: {confidence_analysis.get('confidence_level', 'Unknown')}
- Consensus Level: {consensus_analysis.get('consensus_level', 'Unknown')}
- Contributing Models: {consensus_analysis.get('total_unique_concepts', 0)} unique perspectives integrated

---

"""
        return header + text