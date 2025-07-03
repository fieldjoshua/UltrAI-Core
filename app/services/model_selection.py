"""
Smart Model Selection for Ultra Synthesis™

This module implements intelligent model selection based on performance metrics,
availability, and suitability for synthesis tasks.
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import asyncio
import json
from pathlib import Path


@dataclass
class ModelPerformanceMetrics:
    """Track performance metrics for a model."""
    model_name: str
    successful_syntheses: int = 0
    failed_syntheses: int = 0
    average_quality_score: float = 0.0
    average_response_time: float = 0.0
    last_used: Optional[datetime] = None
    expertise_areas: List[str] = field(default_factory=list)
    availability_score: float = 1.0  # 0-1, where 1 is always available


class SmartModelSelector:
    """
    Intelligent model selection for Ultra Synthesis based on performance,
    availability, and task suitability.
    """
    
    def __init__(self, metrics_file: Optional[str] = None):
        """
        Initialize the model selector.
        
        Args:
            metrics_file: Optional path to persist metrics
        """
        self.metrics_file = metrics_file or "model_performance_metrics.json"
        self.model_metrics: Dict[str, ModelPerformanceMetrics] = {}
        self._load_metrics()
        
        # Model expertise mapping (can be expanded/learned over time)
        self.model_expertise = {
            "gpt-4": ["reasoning", "technical", "comprehensive", "code"],
            "gpt-4-turbo": ["fast", "technical", "comprehensive"],
            "gpt-4o": ["multimodal", "technical", "reasoning"],
            "o1-preview": ["complex_reasoning", "mathematical", "strategic"],
            "claude-3-5-sonnet-20241022": ["nuanced", "ethical", "analytical", "writing"],
            "claude-3-5-haiku-20241022": ["fast", "concise", "efficient"],
            "claude-3-opus": ["comprehensive", "creative", "philosophical"],
            "gemini-1.5-pro": ["factual", "structured", "multimodal", "research"],
            "gemini-1.5-flash": ["fast", "efficient", "factual"],
            "gemini-2.0-flash-exp": ["experimental", "fast", "innovative"],
        }
        
        # Initialize metrics for known models
        for model in self.model_expertise.keys():
            if model not in self.model_metrics:
                self.model_metrics[model] = ModelPerformanceMetrics(
                    model_name=model,
                    expertise_areas=self.model_expertise.get(model, [])
                )
    
    def _load_metrics(self):
        """Load persisted metrics from file."""
        try:
            if Path(self.metrics_file).exists():
                with open(self.metrics_file, 'r') as f:
                    data = json.load(f)
                    for model_name, metrics_data in data.items():
                        # Convert datetime strings back to datetime objects
                        if metrics_data.get('last_used'):
                            metrics_data['last_used'] = datetime.fromisoformat(
                                metrics_data['last_used']
                            )
                        self.model_metrics[model_name] = ModelPerformanceMetrics(
                            **metrics_data
                        )
        except Exception as e:
            # If loading fails, start fresh
            print(f"Could not load metrics: {e}")
    
    def _save_metrics(self):
        """Persist metrics to file."""
        try:
            data = {}
            for model_name, metrics in self.model_metrics.items():
                metrics_dict = {
                    'model_name': metrics.model_name,
                    'successful_syntheses': metrics.successful_syntheses,
                    'failed_syntheses': metrics.failed_syntheses,
                    'average_quality_score': metrics.average_quality_score,
                    'average_response_time': metrics.average_response_time,
                    'last_used': metrics.last_used.isoformat() if metrics.last_used else None,
                    'expertise_areas': metrics.expertise_areas,
                    'availability_score': metrics.availability_score
                }
                data[model_name] = metrics_dict
            
            with open(self.metrics_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Could not save metrics: {e}")
    
    async def select_best_synthesis_model(
        self,
        available_models: List[str],
        query_type: Optional[str] = None,
        recent_performers: Optional[List[str]] = None
    ) -> List[str]:
        """
        Select the best models for synthesis based on performance metrics.
        
        Args:
            available_models: List of currently available models
            query_type: Type of query (technical, creative, etc.)
            recent_performers: Models that performed well in recent stages
            
        Returns:
            Ranked list of models, best first
        """
        model_scores = {}
        
        for model in available_models:
            score = await self._calculate_model_score(
                model, 
                query_type, 
                recent_performers
            )
            model_scores[model] = score
        
        # Sort by score descending
        ranked_models = sorted(
            available_models, 
            key=lambda m: model_scores.get(m, 0), 
            reverse=True
        )
        
        return ranked_models
    
    async def _calculate_model_score(
        self,
        model: str,
        query_type: Optional[str] = None,
        recent_performers: Optional[List[str]] = None
    ) -> float:
        """
        Calculate a score for a model based on various factors.
        
        Args:
            model: Model name
            query_type: Type of query
            recent_performers: Models that performed well recently
            
        Returns:
            float: Score for the model (higher is better)
        """
        metrics = self.model_metrics.get(model)
        if not metrics:
            # Unknown model, give baseline score
            return 1.0
        
        score = 0.0
        
        # Factor 1: Success rate (0-3 points)
        total_attempts = metrics.successful_syntheses + metrics.failed_syntheses
        if total_attempts > 0:
            success_rate = metrics.successful_syntheses / total_attempts
            score += success_rate * 3
        else:
            # No history, neutral score
            score += 1.5
        
        # Factor 2: Quality score (0-3 points)
        if metrics.average_quality_score > 0:
            normalized_quality = min(metrics.average_quality_score / 10, 1.0)
            score += normalized_quality * 3
        else:
            score += 1.5
        
        # Factor 3: Recent performance (0-2 points)
        if recent_performers and model in recent_performers:
            # Performed well in earlier stages
            score += 2
        
        # Factor 4: Expertise match (0-2 points)
        if query_type and query_type in metrics.expertise_areas:
            score += 2
        elif query_type and any(exp in query_type for exp in metrics.expertise_areas):
            score += 1
        
        # Factor 5: Availability (0-1 point)
        score += metrics.availability_score
        
        # Factor 6: Recency penalty (0 to -1 point)
        if metrics.last_used:
            time_since_use = datetime.now() - metrics.last_used
            if time_since_use < timedelta(seconds=5):
                # Very recently used, might be rate limited
                score -= 1
            elif time_since_use < timedelta(seconds=30):
                # Recently used, small penalty
                score -= 0.5
        
        # Factor 7: Response time bonus (0-1 point)
        if metrics.average_response_time > 0:
            if metrics.average_response_time < 5:
                score += 1  # Fast responder
            elif metrics.average_response_time < 10:
                score += 0.5  # Moderate speed
        
        return max(score, 0)  # Ensure non-negative
    
    def update_model_performance(
        self,
        model: str,
        success: bool,
        quality_score: Optional[float] = None,
        response_time: Optional[float] = None
    ):
        """
        Update performance metrics for a model after synthesis.
        
        Args:
            model: Model name
            success: Whether synthesis was successful
            quality_score: Optional quality score (0-10)
            response_time: Optional response time in seconds
        """
        if model not in self.model_metrics:
            self.model_metrics[model] = ModelPerformanceMetrics(
                model_name=model,
                expertise_areas=self.model_expertise.get(model, [])
            )
        
        metrics = self.model_metrics[model]
        
        # Update success/failure counts
        if success:
            metrics.successful_syntheses += 1
        else:
            metrics.failed_syntheses += 1
        
        # Update quality score (rolling average)
        if quality_score is not None:
            if metrics.average_quality_score == 0:
                metrics.average_quality_score = quality_score
            else:
                # Rolling average with more weight on recent
                metrics.average_quality_score = (
                    metrics.average_quality_score * 0.7 + quality_score * 0.3
                )
        
        # Update response time (rolling average)
        if response_time is not None:
            if metrics.average_response_time == 0:
                metrics.average_response_time = response_time
            else:
                metrics.average_response_time = (
                    metrics.average_response_time * 0.7 + response_time * 0.3
                )
        
        # Update last used timestamp
        metrics.last_used = datetime.now()
        
        # Save updated metrics
        self._save_metrics()
    
    def update_model_availability(self, model: str, available: bool):
        """
        Update model availability score.
        
        Args:
            model: Model name
            available: Whether model is currently available
        """
        if model not in self.model_metrics:
            self.model_metrics[model] = ModelPerformanceMetrics(
                model_name=model,
                expertise_areas=self.model_expertise.get(model, [])
            )
        
        metrics = self.model_metrics[model]
        
        if available:
            # Gradually increase availability score
            metrics.availability_score = min(1.0, metrics.availability_score + 0.1)
        else:
            # Sharply decrease availability score
            metrics.availability_score = max(0.0, metrics.availability_score - 0.3)
        
        self._save_metrics()
    
    def get_model_stats(self, model: str) -> Dict[str, Any]:
        """
        Get current statistics for a model.
        
        Args:
            model: Model name
            
        Returns:
            Dictionary of model statistics
        """
        metrics = self.model_metrics.get(model)
        if not metrics:
            return {"error": "No metrics available for model"}
        
        total_attempts = metrics.successful_syntheses + metrics.failed_syntheses
        success_rate = (
            metrics.successful_syntheses / total_attempts 
            if total_attempts > 0 else 0
        )
        
        return {
            "model": model,
            "total_syntheses": total_attempts,
            "success_rate": f"{success_rate * 100:.1f}%",
            "average_quality": f"{metrics.average_quality_score:.1f}/10",
            "average_response_time": f"{metrics.average_response_time:.1f}s",
            "availability": f"{metrics.availability_score * 100:.0f}%",
            "expertise_areas": metrics.expertise_areas,
            "last_used": metrics.last_used.isoformat() if metrics.last_used else "Never"
        }
    
    def get_all_model_stats(self) -> List[Dict[str, Any]]:
        """Get statistics for all tracked models."""
        return [
            self.get_model_stats(model) 
            for model in sorted(self.model_metrics.keys())
        ]