"""
Pattern Optimizer for UltraAI

This module enhances the feather pattern selection process by
implementing optimized matching algorithms and usage analytics.
"""

import logging
from collections import Counter
from typing import Dict, List, Tuple
import re
import math

# These imports are for loading the patterns when needed
from src.patterns.ultra_analysis_patterns import get_pattern_mapping
from src.patterns.educational_feather import EducationalFeather
from src.patterns.collaborative_feather import CollaborativeFeather
from src.patterns.synthesis_feather import SynthesisFeather
from src.patterns.feedback_feather import FeedbackFeather


class PatternOptimizer:
    """
    Optimizes feather pattern selection using advanced matching algorithms
    and historical usage data to provide the best pattern recommendations.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.usage_stats = Counter()
        self.successful_matches = {}
        self.domain_keywords = {}
        self.specialized_matchers = {
            "learning_optimization": self._match_educational_pattern,
            "team_analysis": self._match_collaborative_pattern,
            "advanced_synthesis": self._match_synthesis_pattern,
            "iterative_improvement": self._match_feedback_pattern,
        }

        # Enhanced pattern keywords with expanded vocabulary
        self.pattern_keywords = {
            "Gut Analysis": [
                "intuition",
                "gut",
                "instinct",
                "feeling",
                "impression",
                "immediate",
                "initial",
                "first impression",
                "quick take",
                "intuitive",
                "instant",
                "rapid",
                "swift",
                "prompt",
                "spontaneous",
                "unreflected",
            ],
            "Confidence Analysis": [
                "confidence",
                "certain",
                "uncertain",
                "consensus",
                "agreement",
                "disagreement",
                "assurance",
                "certainty",
                "uncertainty",
                "conviction",
                "probability",
                "likelihood",
                "credibility",
                "reliability",
                "trust",
                "doubt",
                "skepticism",
                "evidence strength",
                "confidence interval",
            ],
            "Critique Analysis": [
                "critique",
                "criticize",
                "assess",
                "evaluate",
                "review",
                "feedback",
                "appraisal",
                "judgment",
                "analysis",
                "examination",
                "scrutiny",
                "appraise",
                "examine",
                "inspect",
                "probe",
                "investigate",
                "strengths",
                "weaknesses",
                "pros",
                "cons",
                "merits",
                "flaws",
                "limitations",
            ],
            "Fact Check Analysis": [
                "fact",
                "accuracy",
                "correct",
                "verify",
                "check",
                "evidence",
                "source",
                "validation",
                "confirmation",
                "authenticate",
                "substantiate",
                "proof",
                "verification",
                "corroboration",
                "confirmation",
                "factual",
                "accurate",
                "precise",
                "exact",
                "authentic",
                "credible",
                "reliable",
            ],
            "Perspective Analysis": [
                "perspective",
                "viewpoint",
                "angle",
                "lens",
                "different",
                "diverse",
                "point of view",
                "outlook",
                "standpoint",
                "position",
                "stance",
                "opinion",
                "view",
                "perception",
                "interpretation",
                "framework",
                "paradigm",
                "ideology",
                "worldview",
                "mindset",
                "orientation",
            ],
            "Scenario Analysis": [
                "scenario",
                "situation",
                "case",
                "possibility",
                "what if",
                "alternative",
                "hypothetical",
                "projection",
                "forecast",
                "prediction",
                "future",
                "outcome",
                "prospect",
                "contingency",
                "eventualities",
                "circumstances",
                "conditions",
                "variables",
                "factors",
                "parameters",
            ],
            "Stakeholder Vision": [
                "stakeholder",
                "audience",
                "user",
                "customer",
                "client",
                "group",
                "organization",
                "party",
                "participant",
                "player",
                "member",
                "partner",
                "associate",
                "collaborator",
                "constituent",
                "interest group",
                "shareholder",
                "investor",
                "beneficiary",
                "recipient",
                "community",
            ],
            "Systems Mapper": [
                "system",
                "process",
                "workflow",
                "interconnection",
                "dynamic",
                "feedback",
                "loop",
                "network",
                "structure",
                "framework",
                "mechanism",
                "organization",
                "arrangement",
                "configuration",
                "architecture",
                "ecosystem",
                "environment",
                "interface",
                "relationship",
                "connection",
            ],
            "Time Horizon": [
                "time",
                "future",
                "present",
                "past",
                "short-term",
                "long-term",
                "timeline",
                "period",
                "duration",
                "interval",
                "era",
                "epoch",
                "age",
                "phase",
                "stage",
                "cycle",
                "generation",
                "decade",
                "century",
                "immediate",
                "intermediate",
                "distant",
                "historical",
                "current",
            ],
            "Innovation Bridge": [
                "innovation",
                "creative",
                "novel",
                "new",
                "breakthrough",
                "original",
                "inventive",
                "groundbreaking",
                "pioneering",
                "revolutionary",
                "cutting-edge",
                "state-of-the-art",
                "advanced",
                "progressive",
                "modern",
                "fresh",
                "imaginative",
                "ingenious",
                "resourceful",
            ],
            "Learning Optimization": [
                "learn",
                "education",
                "teaching",
                "instructor",
                "student",
                "pupil",
                "knowledge",
                "comprehension",
                "understanding",
                "insight",
                "grasp",
                "pedagogy",
                "curriculum",
                "lesson",
                "course",
                "training",
                "skill",
                "ability",
                "competence",
                "proficiency",
                "mastery",
                "expertise",
            ],
            "Team Analysis": [
                "team",
                "group",
                "collaborate",
                "cooperation",
                "coordination",
                "collective",
                "joint",
                "partnership",
                "alliance",
                "coalition",
                "together",
                "mutual",
                "shared",
                "combined",
                "united",
                "integrated",
                "coordinated",
                "synergy",
                "teamwork",
                "collaboration",
                "consensus",
            ],
            "Advanced Synthesis": [
                "synthesis",
                "integrate",
                "combine",
                "merge",
                "unify",
                "consolidate",
                "amalgamate",
                "blend",
                "fusion",
                "incorporation",
                "assimilation",
                "connection",
                "relation",
                "association",
                "correlation",
                "junction",
                "multi-document",
                "cross-reference",
                "compilation",
                "aggregation",
            ],
            "Iterative Improvement": [
                "feedback",
                "iteration",
                "improve",
                "enhance",
                "refine",
                "optimize",
                "upgrade",
                "advance",
                "progress",
                "develop",
                "evolve",
                "mature",
                "growth",
                "expansion",
                "elaboration",
                "revision",
                "modification",
                "adjustment",
                "alteration",
                "correction",
                "reformation",
                "cycle",
            ],
        }

    def match_pattern_to_prompt(self, prompt: str) -> List[Tuple[str, float]]:
        """
        Match prompt to appropriate patterns using advanced matching techniques.
        Returns a list of (pattern_name, score) tuples.

        This enhanced matcher uses:
        1. TF-IDF scoring for keyword relevance
        2. Context-sensitive matching
        3. Domain-specific keyword weighting
        4. Historical success rate adjustments
        """
        if not prompt:
            return []

        prompt_lower = prompt.lower()

        # Get specialized pattern matches first (domain-specific matchers)
        specialized_matches = []
        for pattern_key, matcher_func in self.specialized_matchers.items():
            score = matcher_func(prompt_lower)
            if score > 0.2:  # Only consider specialized matches above threshold
                pattern_name = self._get_specialized_pattern_name(pattern_key)
                specialized_matches.append((pattern_name, score))

        # Get general pattern matches
        general_matches = self._get_general_pattern_matches(prompt_lower)

        # Combine and adjust scores
        all_matches = specialized_matches + general_matches

        # Apply usage statistics adjustment if we have sufficient data
        if sum(self.usage_stats.values()) > 5:
            all_matches = self._adjust_scores_by_usage(all_matches)

        # Sort by score descending
        all_matches.sort(key=lambda x: x[1], reverse=True)

        # Update usage statistics
        if all_matches:
            self.usage_stats[all_matches[0][0]] += 1

        return all_matches

    def _get_general_pattern_matches(
        self, prompt_lower: str
    ) -> List[Tuple[str, float]]:
        """Get matches for general analysis patterns using TF-IDF weighting"""
        matches = []

        # Count total keyword occurrences for normalization
        total_keyword_occurrences = 0
        keyword_counts = {}

        # First pass: count keywords
        for pattern_name, keywords in self.pattern_keywords.items():
            keyword_counts[pattern_name] = 0
            for keyword in keywords:
                occurrences = self._count_keyword_occurrences(prompt_lower, keyword)
                keyword_counts[pattern_name] += occurrences
                total_keyword_occurrences += occurrences

        # Second pass: calculate normalized scores with TF-IDF weighting
        for pattern_name, keywords in self.pattern_keywords.items():
            if keyword_counts[pattern_name] > 0:
                # Calculate inverse document frequency factor
                # (keywords that appear in fewer patterns get higher weight)
                patterns_with_keyword = sum(
                    1
                    for p in self.pattern_keywords.values()
                    if any(k in keywords for k in p)
                )
                idf = math.log(len(self.pattern_keywords) / (1 + patterns_with_keyword))

                # Calculate TF factor (term frequency)
                tf = keyword_counts[pattern_name] / max(1, total_keyword_occurrences)

                # Combined TF-IDF score
                score = tf * idf

                # Apply context multiplier for keyword combinations
                context_multiplier = self._calculate_context_multiplier(
                    prompt_lower, keywords
                )

                # Final score
                final_score = min(1.0, score * context_multiplier)

                matches.append((pattern_name, final_score))

        return matches

    def _count_keyword_occurrences(self, text: str, keyword: str) -> int:
        """Count occurrences of a keyword in text, handling word boundaries"""
        pattern = r"\b" + re.escape(keyword) + r"\b"
        return len(re.findall(pattern, text))

    def _calculate_context_multiplier(self, text: str, keywords: List[str]) -> float:
        """
        Calculate a context multiplier based on keyword combinations.
        Multiple keywords from the same pattern appearing together
        increases the confidence in the pattern match.
        """
        # Count how many distinct keywords from the list appear in the text
        distinct_keywords = sum(1 for k in keywords if k in text)

        # No keywords found
        if distinct_keywords == 0:
            return 0

        # Base multiplier is 1.0
        multiplier = 1.0

        # If multiple distinct keywords are found, apply a bonus
        if distinct_keywords > 1:
            # Bonus increases with the number of distinct keywords
            # but with diminishing returns
            keyword_bonus = 1.0 + (0.3 * math.log(distinct_keywords))
            multiplier *= keyword_bonus

        # Apply a proximity bonus if keywords appear close to each other
        if distinct_keywords > 1:
            proximity_bonus = self._calculate_proximity_bonus(text, keywords)
            multiplier *= proximity_bonus

        return multiplier

    def _calculate_proximity_bonus(self, text: str, keywords: List[str]) -> float:
        """
        Calculate a bonus based on the proximity of keywords in the text.
        Keywords appearing closer together get a higher bonus.
        """
        # Find positions of all keyword occurrences
        positions = []
        present_keywords = [k for k in keywords if k in text]

        for keyword in present_keywords:
            pattern = r"\b" + re.escape(keyword) + r"\b"
            for match in re.finditer(pattern, text):
                positions.append((match.start(), match.end(), keyword))

        if len(positions) <= 1:
            return 1.0  # No proximity bonus with 0 or 1 occurrences

        # Sort positions by start position
        positions.sort(key=lambda x: x[0])

        # Calculate average distance between consecutive keywords
        distances = [
            positions[i + 1][0] - positions[i][1] for i in range(len(positions) - 1)
        ]
        avg_distance = sum(distances) / len(distances) if distances else float("inf")

        # Normalize the distance into a bonus factor
        # Lower distances give higher bonuses
        if avg_distance < 20:  # Very close
            return 1.5
        elif avg_distance < 50:  # Moderately close
            return 1.3
        elif avg_distance < 100:  # Somewhat close
            return 1.1
        else:  # Not particularly close
            return 1.0

    def _adjust_scores_by_usage(
        self, matches: List[Tuple[str, float]]
    ) -> List[Tuple[str, float]]:
        """
        Adjust scores based on usage statistics.
        Patterns that have been successfully used get a small boost.
        """
        total_usage = sum(self.usage_stats.values())
        adjusted_matches = []

        for pattern_name, score in matches:
            usage_count = self.usage_stats.get(pattern_name, 0)

            # Calculate usage ratio (0 to 1)
            usage_ratio = usage_count / total_usage if total_usage > 0 else 0

            # Small adjustment based on usage (max 10% boost)
            adjustment = 1.0 + (usage_ratio * 0.1)

            # Apply adjustment
            adjusted_score = min(1.0, score * adjustment)
            adjusted_matches.append((pattern_name, adjusted_score))

        return adjusted_matches

    def _match_educational_pattern(self, prompt: str) -> float:
        """Specialized matcher for the Learning Optimization pattern"""
        educational_indicators = [
            r"\blearn\b",
            r"\bteach\b",
            r"\beducat\w+\b",
            r"\bstudent\b",
            r"\bcourse\b",
            r"\btraining\b",
            r"\bunderstand\w+\b",
            r"\bknowledge\b",
            r"\bcurriculum\b",
            r"\blessons?\b",
            r"\bcomprehension\b",
            r"\bmastery\b",
            r"\blearn\w+ style\b",
            r"\bpedagog\w+\b",
            r"\binstructi\w+\b",
        ]

        educational_phrases = [
            "how to learn",
            "learning process",
            "educational method",
            "teaching technique",
            "instructional design",
            "learning curve",
            "knowledge acquisition",
            "skill development",
            "understanding concepts",
        ]

        # Check for regex patterns
        pattern_matches = sum(
            1 for pattern in educational_indicators if re.search(pattern, prompt)
        )

        # Check for phrases
        phrase_matches = sum(1 for phrase in educational_phrases if phrase in prompt)

        # Combined score
        base_score = (pattern_matches * 0.1) + (phrase_matches * 0.15)

        # Apply multiplicative bonus for strong educational context
        if "best way to learn" in prompt or "optimal learning" in prompt:
            base_score *= 1.5

        return min(1.0, base_score)

    def _match_collaborative_pattern(self, prompt: str) -> float:
        """Specialized matcher for the Team Analysis pattern"""
        collaboration_indicators = [
            r"\bteam\b",
            r"\bcollaborat\w+\b",
            r"\bgroup\b",
            r"\bjoint\b",
            r"\btogether\b",
            r"\bcooperat\w+\b",
            r"\bpartner\w+\b",
            r"\balliance\b",
            r"\bcoalition\b",
            r"\bsynergy\b",
            r"\bcollective\b",
            r"\bshared\b",
        ]

        collaboration_phrases = [
            "team decision",
            "group analysis",
            "collaborative approach",
            "working together",
            "joint effort",
            "team dynamics",
            "shared decision",
            "collective intelligence",
            "team coordination",
            "team communication",
        ]

        # Check for regex patterns
        pattern_matches = sum(
            1 for pattern in collaboration_indicators if re.search(pattern, prompt)
        )

        # Check for phrases
        phrase_matches = sum(1 for phrase in collaboration_phrases if phrase in prompt)

        # Combined score
        base_score = (pattern_matches * 0.1) + (phrase_matches * 0.15)

        # Apply multiplicative bonus for strong collaborative context
        if (
            "team decision-making" in prompt
            or "collaborative problem-solving" in prompt
        ):
            base_score *= 1.5

        return min(1.0, base_score)

    def _match_synthesis_pattern(self, prompt: str) -> float:
        """Specialized matcher for the Advanced Synthesis pattern"""
        synthesis_indicators = [
            r"\bsynthe\w+\b",
            r"\bintegrat\w+\b",
            r"\bcombine\b",
            r"\bmerge\b",
            r"\bconsolidat\w+\b",
            r"\bamalgamat\w+\b",
            r"\bblend\w+\b",
            r"\bfusion\b",
            r"\bmultiple\s+documents?\b",
            r"\bmultiple\s+sources\b",
            r"\bcross-reference\b",
        ]

        synthesis_phrases = [
            "bring together",
            "multiple perspectives",
            "diverse sources",
            "different documents",
            "various inputs",
            "combine information",
            "information synthesis",
            "knowledge integration",
            "connect ideas",
        ]

        # Check for regex patterns
        pattern_matches = sum(
            1 for pattern in synthesis_indicators if re.search(pattern, prompt)
        )

        # Check for phrases
        phrase_matches = sum(1 for phrase in synthesis_phrases if phrase in prompt)

        # Combined score
        base_score = (pattern_matches * 0.1) + (phrase_matches * 0.15)

        # Apply multiplicative bonus for strong synthesis context
        if (
            "synthesize information from" in prompt
            or "integrate multiple sources" in prompt
        ):
            base_score *= 1.5

        return min(1.0, base_score)

    def _match_feedback_pattern(self, prompt: str) -> float:
        """Specialized matcher for the Iterative Improvement pattern"""
        feedback_indicators = [
            r"\bfeedback\b",
            r"\biterat\w+\b",
            r"\bimprove\w+\b",
            r"\benhance\w+\b",
            r"\brefine\w+\b",
            r"\boptimiz\w+\b",
            r"\bupgrade\b",
            r"\brevision\b",
            r"\brevis\w+\b",
            r"\bcycle\b",
            r"\bloop\b",
            r"\biteration\b",
        ]

        feedback_phrases = [
            "continuous improvement",
            "iterative process",
            "feedback loop",
            "refine approach",
            "improvement cycle",
            "progressive enhancement",
            "incremental improvement",
            "systematic feedback",
            "improvement process",
        ]

        # Check for regex patterns
        pattern_matches = sum(
            1 for pattern in feedback_indicators if re.search(pattern, prompt)
        )

        # Check for phrases
        phrase_matches = sum(1 for phrase in feedback_phrases if phrase in prompt)

        # Combined score
        base_score = (pattern_matches * 0.1) + (phrase_matches * 0.15)

        # Apply multiplicative bonus for strong feedback context
        if "iterative improvement" in prompt or "feedback-driven" in prompt:
            base_score *= 1.5

        return min(1.0, base_score)

    def _get_specialized_pattern_name(self, pattern_key: str) -> str:
        """Convert pattern key to full pattern name"""
        pattern_map = {
            "learning_optimization": "Learning Optimization",
            "team_analysis": "Team Analysis",
            "advanced_synthesis": "Advanced Synthesis",
            "iterative_improvement": "Iterative Improvement",
        }
        return pattern_map.get(pattern_key, pattern_key)

    def record_pattern_success(self, pattern_name: str, prompt: str) -> None:
        """
        Record a successful pattern application to improve future recommendations.

        Args:
            pattern_name: The name of the successfully applied pattern
            prompt: The prompt that was analyzed
        """
        # Update success counter for this pattern
        if pattern_name not in self.successful_matches:
            self.successful_matches[pattern_name] = 0
        self.successful_matches[pattern_name] += 1

        # Extract domain keywords from the successful prompt
        words = set(re.findall(r"\b\w{4,}\b", prompt.lower()))

        # Update domain keyword associations
        if pattern_name not in self.domain_keywords:
            self.domain_keywords[pattern_name] = Counter()

        for word in words:
            self.domain_keywords[pattern_name][word] += 1

    def get_pattern_success_metrics(self) -> Dict[str, Dict]:
        """
        Get metrics on pattern success rates for reporting.

        Returns:
            Dictionary with pattern usage statistics
        """
        total_usage = sum(self.usage_stats.values())
        total_success = sum(self.successful_matches.values())

        metrics = {
            "overview": {
                "total_usage": total_usage,
                "total_success": total_success,
                "overall_success_rate": (
                    total_success / total_usage if total_usage > 0 else 0
                ),
            },
            "patterns": {},
        }

        # Calculate per-pattern metrics
        for pattern_name, usage_count in self.usage_stats.items():
            success_count = self.successful_matches.get(pattern_name, 0)
            success_rate = success_count / usage_count if usage_count > 0 else 0

            metrics["patterns"][pattern_name] = {
                "usage_count": usage_count,
                "success_count": success_count,
                "success_rate": success_rate,
                "usage_percentage": (
                    usage_count / total_usage if total_usage > 0 else 0
                ),
                "top_keywords": self._get_top_keywords_for_pattern(pattern_name, 5),
            }

        return metrics

    def _get_top_keywords_for_pattern(
        self, pattern_name: str, limit: int = 5
    ) -> List[str]:
        """Get the top keywords associated with successful uses of a pattern"""
        if pattern_name not in self.domain_keywords:
            return []

        return [kw for kw, _ in self.domain_keywords[pattern_name].most_common(limit)]
