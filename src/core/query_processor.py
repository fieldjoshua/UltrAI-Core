from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
import logging
from enum import Enum
import time
from src.core.model_client import ModelClientFactory

# Set up logging
logger = logging.getLogger(__name__)


class AnalysisType(str, Enum):
    """Types of analysis available"""

    CONFIDENCE = "confidence"
    COMPARISON = "comparison"
    SUMMARY = "summary"
    DETAILED = "detailed"


class LLMModel(str, Enum):
    """Available LLM models"""

    GPT4 = "gpt-4"
    GPT35 = "gpt-3.5-turbo"
    CLAUDE = "claude-3-opus"
    MISTRAL = "mistral-large"


class QueryRequest(BaseModel):
    """Query request model"""

    query: str = Field(..., min_length=1, max_length=1000)
    selected_models: List[LLMModel] = Field(default_factory=list)
    analysis_type: AnalysisType = Field(default=AnalysisType.CONFIDENCE)
    context: Optional[str] = None
    max_tokens: Optional[int] = Field(default=1000, ge=1, le=4000)


class QueryResponse(BaseModel):
    """Query response model"""

    query: str
    results: Dict[str, Any]
    analysis: Dict[str, Any]
    processing_time: float
    models_used: List[str]


class QueryProcessor:
    """Handles query processing, LLM selection, and analysis"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.available_models = {
            LLMModel.GPT4: {"max_tokens": 4000, "cost_per_token": 0.03},
            LLMModel.GPT35: {"max_tokens": 2000, "cost_per_token": 0.002},
            LLMModel.CLAUDE: {"max_tokens": 4000, "cost_per_token": 0.015},
            LLMModel.MISTRAL: {"max_tokens": 2000, "cost_per_token": 0.007},
        }
        self.model_factory = ModelClientFactory()

    def validate_query(self, query: str) -> bool:
        """Validate the query"""
        if not query or len(query.strip()) == 0:
            return False
        if len(query) > 1000:
            return False
        return True

    def select_models(self, request: QueryRequest) -> List[LLMModel]:
        """Select appropriate models based on the request"""
        if not request.selected_models:
            # Default to GPT-4 if no models specified
            return [LLMModel.GPT4]

        # Validate selected models
        valid_models = []
        for model in request.selected_models:
            if model in self.available_models:
                valid_models.append(model)

        return valid_models if valid_models else [LLMModel.GPT4]

    async def process_query(self, request: QueryRequest) -> QueryResponse:
        """Process a query with selected models and analysis type"""
        try:
            start_time = time.time()

            # Validate query
            if not self.validate_query(request.query):
                raise ValueError("Invalid query")

            # Select models
            selected_models = self.select_models(request)

            # Process with each model
            results = {}
            for model in selected_models:
                model_result = await self._process_with_model(model, request)
                results[model.value] = model_result

            # Perform analysis
            analysis = self._analyze_results(results, request.analysis_type)

            processing_time = time.time() - start_time

            return QueryResponse(
                query=request.query,
                results=results,
                analysis=analysis,
                processing_time=processing_time,
                models_used=[model.value for model in selected_models],
            )

        except Exception as e:
            self.logger.error(f"Error processing query: {str(e)}")
            raise

    async def _process_with_model(
        self, model: LLMModel, request: QueryRequest
    ) -> Dict[str, Any]:
        """Process query with a specific model"""
        try:
            # Create model client
            client = self.model_factory.create_client(model)

            # Prepare prompt
            prompt = request.query
            if request.context:
                prompt = f"Context: {request.context}\n\nQuery: {request.query}"

            # Generate response
            max_tokens = min(
                request.max_tokens or 1000, self.available_models[model]["max_tokens"]
            )

            result = await client.generate_response(prompt, max_tokens)
            return result

        except Exception as e:
            self.logger.error(f"Error processing with model {model}: {str(e)}")
            raise

    def _analyze_results(
        self, results: Dict[str, Any], analysis_type: AnalysisType
    ) -> Dict[str, Any]:
        """Analyze results based on the selected analysis type"""
        if analysis_type == AnalysisType.CONFIDENCE:
            return self._analyze_confidence(results)
        elif analysis_type == AnalysisType.COMPARISON:
            return self._analyze_comparison(results)
        elif analysis_type == AnalysisType.SUMMARY:
            return self._analyze_summary(results)
        else:
            return self._analyze_detailed(results)

    def _analyze_confidence(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze confidence scores across models"""
        confidence_scores = {
            model: result["confidence"] for model, result in results.items()
        }
        return {
            "type": "confidence",
            "scores": confidence_scores,
            "average_confidence": sum(confidence_scores.values())
            / len(confidence_scores),
        }

    def _analyze_comparison(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Compare responses across models"""
        return {
            "type": "comparison",
            "model_responses": {
                model: result["response"] for model, result in results.items()
            },
        }

    def _analyze_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a summary of the results"""
        return {
            "type": "summary",
            "summary": "Summary of model responses",
            "key_points": ["Point 1", "Point 2", "Point 3"],
        }

    def _analyze_detailed(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate detailed analysis of the results"""
        return {
            "type": "detailed",
            "model_analysis": {
                model: {
                    "response": result["response"],
                    "confidence": result["confidence"],
                    "tokens_used": result["tokens_used"],
                }
                for model, result in results.items()
            },
        }
