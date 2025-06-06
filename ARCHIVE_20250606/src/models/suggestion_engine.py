"""
Suggestion Engine for UltraAI

This module provides intelligent recommendations for feather pattern selection,
prompt refinements, and feature discovery based on user inputs and historical usage patterns.
"""

import json
import logging
import re
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple

from ..patterns.ultra_analysis_patterns import AnalysisPatterns
from .pattern_optimizer import PatternOptimizer


class SuggestionType(Enum):
    """Types of suggestions the engine can generate"""

    FEATHER_PATTERN = "feather_pattern"
    PROMPT_REFINEMENT = "prompt_refinement"
    MODEL_SELECTION = "model_selection"
    FEATURE_DISCOVERY = "feature_discovery"


class ConfidenceLevel(Enum):
    """Confidence levels for suggestions"""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class Suggestion:
    """Represents a single suggestion from the engine"""

    type: SuggestionType
    content: str
    title: str
    description: str
    confidence: ConfidenceLevel
    timestamp: datetime = datetime.now()
    action_url: Optional[str] = None
    dismissed: bool = False
    metadata: Dict = None

    def to_dict(self) -> Dict:
        """Convert suggestion to dictionary for serialization"""
        return {
            "type": self.type.value,
            "content": self.content,
            "title": self.title,
            "description": self.description,
            "confidence": self.confidence.value,
            "timestamp": self.timestamp.isoformat(),
            "action_url": self.action_url,
            "dismissed": self.dismissed,
            "metadata": self.metadata or {},
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Suggestion":
        """Create suggestion from dictionary"""
        return cls(
            type=SuggestionType(data["type"]),
            content=data["content"],
            title=data["title"],
            description=data["description"],
            confidence=ConfidenceLevel(data["confidence"]),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            action_url=data.get("action_url"),
            dismissed=data.get("dismissed", False),
            metadata=data.get("metadata", {}),
        )


class UserContext:
    """Represents the current user context for generating personalized suggestions"""

    def __init__(self):
        self.current_prompt: Optional[str] = None
        self.selected_pattern: Optional[str] = None
        self.selected_models: List[str] = []
        self.recent_patterns: List[str] = []
        self.feature_usage_count: Dict[str, int] = {}
        self.prompt_history: List[str] = []
        self.successful_completions: List[Dict] = []
        self.domain_keywords: Set[str] = set()

    def update_from_request(self, request_data: Dict) -> None:
        """Update context from incoming request data"""
        if "prompt" in request_data:
            self.current_prompt = request_data["prompt"]
            self.prompt_history.append(request_data["prompt"])

        if "pattern" in request_data:
            self.selected_pattern = request_data["pattern"]
            self.recent_patterns.append(request_data["pattern"])
            if len(self.recent_patterns) > 10:
                self.recent_patterns.pop(0)

        if "models" in request_data:
            self.selected_models = request_data["models"]

        # Extract domain keywords from prompt
        if self.current_prompt:
            # Simple keyword extraction - in a real implementation,
            # this would use NLP techniques
            words = re.findall(r"\b\w{4,}\b", self.current_prompt.lower())
            self.domain_keywords.update(words)

    def to_dict(self) -> Dict:
        """Convert context to dictionary for serialization"""
        return {
            "current_prompt": self.current_prompt,
            "selected_pattern": self.selected_pattern,
            "selected_models": self.selected_models,
            "recent_patterns": self.recent_patterns,
            "feature_usage_count": self.feature_usage_count,
            "prompt_history": self.prompt_history,
            "domain_keywords": list(self.domain_keywords),
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "UserContext":
        """Create context from dictionary"""
        context = cls()
        context.current_prompt = data.get("current_prompt")
        context.selected_pattern = data.get("selected_pattern")
        context.selected_models = data.get("selected_models", [])
        context.recent_patterns = data.get("recent_patterns", [])
        context.feature_usage_count = data.get("feature_usage_count", {})
        context.prompt_history = data.get("prompt_history", [])
        context.domain_keywords = set(data.get("domain_keywords", []))
        return context


class SuggestionEngine:
    """
    Intelligent engine that generates contextual suggestions for users.

    This engine analyzes user input, patterns, and historical data to provide:
    - Feather pattern recommendations
    - Prompt refinement suggestions
    - Model selection guidance
    - Feature discovery tips
    """

    def __init__(self, storage_path: Optional[str] = None):
        self.logger = logging.getLogger(__name__)
        self.user_context = UserContext()
        self.all_patterns = self._load_patterns()
        self.patterns_by_category = self._categorize_patterns()
        self.storage_path = storage_path
        self.suggestion_history: List[Suggestion] = []
        self.pattern_optimizer = PatternOptimizer()

        # Pattern selection heuristics
        self.pattern_keywords = {
            "Gut Analysis": ["intuition", "gut", "instinct", "feeling", "impression"],
            "Confidence Analysis": [
                "confidence",
                "certain",
                "uncertain",
                "consensus",
                "agreement",
                "disagreement",
            ],
            "Critique Analysis": [
                "critique",
                "criticize",
                "assess",
                "evaluate",
                "review",
                "feedback",
            ],
            "Fact Check Analysis": [
                "fact",
                "accuracy",
                "correct",
                "verify",
                "check",
                "evidence",
                "source",
            ],
            "Perspective Analysis": [
                "perspective",
                "viewpoint",
                "angle",
                "lens",
                "different",
                "diverse",
            ],
            "Scenario Analysis": [
                "scenario",
                "situation",
                "case",
                "possibility",
                "what if",
                "alternative",
            ],
            "Stakeholder Vision": [
                "stakeholder",
                "audience",
                "user",
                "customer",
                "client",
                "group",
                "organization",
            ],
            "Systems Mapper": [
                "system",
                "process",
                "workflow",
                "interconnection",
                "dynamic",
                "feedback",
                "loop",
            ],
            "Time Horizon": [
                "time",
                "future",
                "present",
                "past",
                "short-term",
                "long-term",
                "timeline",
            ],
            "Innovation Bridge": [
                "innovation",
                "creative",
                "novel",
                "new",
                "breakthrough",
                "original",
            ],
        }

        # Load previous context if available
        if storage_path:
            try:
                self._load_state()
            except Exception as e:
                self.logger.warning(f"Could not load suggestion engine state: {e}")

    def _load_patterns(self) -> Dict[str, Dict]:
        """Load all available analysis patterns"""
        patterns = {}
        for name, pattern in vars(AnalysisPatterns).items():
            if name.startswith("_"):
                continue
            if hasattr(pattern, "name") and hasattr(pattern, "description"):
                patterns[pattern.name] = {
                    "name": pattern.name,
                    "description": pattern.description,
                    "stages": pattern.stages if hasattr(pattern, "stages") else [],
                }
        return patterns

    def _categorize_patterns(self) -> Dict[str, List[str]]:
        """Categorize patterns by their primary focus"""
        categories = {
            "Analytical": [
                "Gut Analysis",
                "Confidence Analysis",
                "Critique Analysis",
                "Fact Check Analysis",
            ],
            "Perspective": ["Perspective Analysis", "Stakeholder Vision"],
            "Strategic": ["Scenario Analysis", "Time Horizon", "Systems Mapper"],
            "Innovation": ["Innovation Bridge"],
        }
        return categories

    def _match_pattern_to_prompt(self, prompt: str) -> List[Tuple[str, float]]:
        """
        Match prompt to appropriate patterns based on content analysis.
        Returns list of (pattern_name, score) tuples.
        """
        # Use the pattern optimizer for enhanced matching
        return self.pattern_optimizer.match_pattern_to_prompt(prompt)

    def _generate_prompt_refinements(self, prompt: str) -> List[Suggestion]:
        """Generate suggestions for prompt refinements"""
        suggestions = []

        if not prompt or len(prompt) < 10:
            return suggestions

        # Check for vague language
        vague_terms = ["thing", "stuff", "etc", "and so on"]
        for term in vague_terms:
            if f" {term} " in f" {prompt} ":
                suggestions.append(
                    Suggestion(
                        type=SuggestionType.PROMPT_REFINEMENT,
                        content=f"Replace vague term '{term}' with more specific details",
                        title="Be More Specific",
                        description=f"Your prompt contains the vague term '{term}'. Being more specific will help models give better answers.",
                        confidence=ConfidenceLevel.MEDIUM,
                    )
                )

        # Check prompt length
        if len(prompt) < 30:
            suggestions.append(
                Suggestion(
                    type=SuggestionType.PROMPT_REFINEMENT,
                    content="Add more context or details to your prompt",
                    title="Expand Your Prompt",
                    description="Short prompts often lead to generic responses. Adding more context can improve results.",
                    confidence=ConfidenceLevel.HIGH,
                )
            )

        # Suggest adding specific perspective if appropriate
        if not any(
            kw in prompt.lower()
            for kw in ["perspective", "viewpoint", "angle", "consider"]
        ):
            suggestions.append(
                Suggestion(
                    type=SuggestionType.PROMPT_REFINEMENT,
                    content="Consider asking for multiple perspectives",
                    title="Request Multiple Viewpoints",
                    description="You might get more comprehensive results by asking for analysis from different perspectives.",
                    confidence=ConfidenceLevel.LOW,
                )
            )

        return suggestions

    def _suggest_features_to_discover(self) -> List[Suggestion]:
        """Generate suggestions for feature discovery based on usage patterns"""
        suggestions = []

        # Suggest model selection feature if not used much
        if self.user_context.feature_usage_count.get("model_selection", 0) < 3:
            suggestions.append(
                Suggestion(
                    type=SuggestionType.FEATURE_DISCOVERY,
                    content="Click 'Select Models' to customize which AI models analyze your query",
                    title="Try Model Selection",
                    description="You can choose specific AI models to include in your analysis for more customized results.",
                    confidence=ConfidenceLevel.HIGH,
                    action_url="/features/model-selection",
                )
            )

        # Suggest custom patterns if user always uses the same pattern
        if (
            len(set(self.user_context.recent_patterns)) <= 1
            and len(self.user_context.recent_patterns) >= 3
        ):
            suggestions.append(
                Suggestion(
                    type=SuggestionType.FEATURE_DISCOVERY,
                    content="Try different analysis patterns to get varied perspectives",
                    title="Explore Other Patterns",
                    description="You've been using the same pattern repeatedly. Try others to see different analytical approaches.",
                    confidence=ConfidenceLevel.MEDIUM,
                    action_url="/features/pattern-explorer",
                )
            )

        return suggestions

    def _suggest_model_selection(self) -> List[Suggestion]:
        """Generate suggestions for model selection based on prompt content"""
        suggestions = []

        # If no specific models selected, suggest relevant ones
        if not self.user_context.selected_models:
            suggestions.append(
                Suggestion(
                    type=SuggestionType.MODEL_SELECTION,
                    content="Consider including Claude for complex reasoning tasks",
                    title="Add Claude to Your Models",
                    description="Claude excels at nuanced analysis and long-form content, which may help with your current task.",
                    confidence=ConfidenceLevel.MEDIUM,
                )
            )

        # If domain suggests code, recommend code-specialized models
        if any(
            kw in self.user_context.domain_keywords
            for kw in ["code", "program", "function", "algorithm", "bug"]
        ):
            if "codellama" not in self.user_context.selected_models:
                suggestions.append(
                    Suggestion(
                        type=SuggestionType.MODEL_SELECTION,
                        content="Add CodeLlama for code-related tasks",
                        title="Try CodeLlama",
                        description="Your query appears to involve code. CodeLlama is specialized for programming tasks.",
                        confidence=ConfidenceLevel.HIGH,
                    )
                )

        return suggestions

    def generate_suggestions(
        self, request_data: Optional[Dict] = None
    ) -> List[Suggestion]:
        """
        Generate contextual suggestions based on user context and current request

        Args:
            request_data: Optional request data to update context

        Returns:
            List of Suggestion objects
        """
        # Update context if new request data provided
        if request_data:
            self.user_context.update_from_request(request_data)

        suggestions = []

        # 1. Generate feather pattern suggestions based on prompt
        if self.user_context.current_prompt and not self.user_context.selected_pattern:
            # Use the enhanced pattern matcher
            pattern_matches = self._match_pattern_to_prompt(
                self.user_context.current_prompt
            )

            # Add top 2 pattern matches as suggestions
            for pattern_name, score in pattern_matches[:2]:
                pattern_info = self.all_patterns.get(pattern_name, {})
                description = pattern_info.get("description", "")

                confidence = ConfidenceLevel.LOW
                if score > 0.5:
                    confidence = ConfidenceLevel.HIGH
                elif score > 0.2:
                    confidence = ConfidenceLevel.MEDIUM

                suggestions.append(
                    Suggestion(
                        type=SuggestionType.FEATHER_PATTERN,
                        content=pattern_name,
                        title=f"Try {pattern_name}",
                        description=description,
                        confidence=confidence,
                        metadata={"score": score},
                    )
                )

        # 2. Generate prompt refinement suggestions
        if self.user_context.current_prompt:
            prompt_suggestions = self._generate_prompt_refinements(
                self.user_context.current_prompt
            )
            suggestions.extend(prompt_suggestions)

        # 3. Generate model selection suggestions
        model_suggestions = self._suggest_model_selection()
        suggestions.extend(model_suggestions)

        # 4. Generate feature discovery suggestions
        feature_suggestions = self._suggest_features_to_discover()
        suggestions.extend(feature_suggestions)

        # Keep track of generated suggestions
        self.suggestion_history.extend(suggestions)

        # Persist state if storage path is set
        if self.storage_path:
            try:
                self._save_state()
            except Exception as e:
                self.logger.warning(f"Could not save suggestion engine state: {e}")

        return suggestions

    def mark_suggestion_dismissed(self, suggestion_id: int) -> None:
        """Mark a suggestion as dismissed by its index"""
        if 0 <= suggestion_id < len(self.suggestion_history):
            self.suggestion_history[suggestion_id].dismissed = True

            # If it was a pattern suggestion, record this for the optimizer
            suggestion = self.suggestion_history[suggestion_id]
            if suggestion.type == SuggestionType.FEATHER_PATTERN:
                # Negative feedback for optimizer - pattern was dismissed
                pattern_name = suggestion.content
                if pattern_name and self.user_context.current_prompt:
                    # We don't call record_pattern_success as this wasn't successful
                    pass

    def track_feature_usage(self, feature_name: str) -> None:
        """Track usage of features to improve suggestions"""
        if feature_name not in self.user_context.feature_usage_count:
            self.user_context.feature_usage_count[feature_name] = 0
        self.user_context.feature_usage_count[feature_name] += 1

        # If it's a pattern being used, record the success for the optimizer
        if feature_name in self.all_patterns and self.user_context.current_prompt:
            self.pattern_optimizer.record_pattern_success(
                feature_name, self.user_context.current_prompt
            )

    def _save_state(self) -> None:
        """Save engine state to persistent storage"""
        if not self.storage_path:
            return

        state = {
            "user_context": self.user_context.to_dict(),
            "suggestion_history": [s.to_dict() for s in self.suggestion_history],
        }

        with open(self.storage_path, "w") as f:
            json.dump(state, f, indent=2)

    def _load_state(self) -> None:
        """Load engine state from persistent storage"""
        if not self.storage_path:
            return

        try:
            with open(self.storage_path, "r") as f:
                state = json.load(f)

            self.user_context = UserContext.from_dict(state.get("user_context", {}))
            self.suggestion_history = [
                Suggestion.from_dict(s) for s in state.get("suggestion_history", [])
            ]
        except FileNotFoundError:
            self.logger.info(f"No existing state file found at {self.storage_path}")
