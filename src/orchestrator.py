import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Tuple

from .models import ModelResponse, QualityMetrics, ResponseCache


class TriLLMOrchestrator:
    def __init__(
        self,
        llama_client,
        chatgpt_client,
        gemini_client,
        cache_enabled: bool = True,
        max_retries: int = 3,
    ):
        # Initialize models
        self.llama = llama_client
        self.chatgpt = chatgpt_client
        self.gemini = gemini_client

        # Setup cache and logging
        self.cache = ResponseCache() if cache_enabled else None
        self.logger = logging.getLogger(__name__)
        self.max_retries = max_retries

        # Performance tracking
        self.metrics = {
            "response_times": [],
            "success_rates": {},
            "token_usage": {},
            "quality_scores": {},
        }

    async def evaluate_quality(self, response: ModelResponse) -> QualityMetrics:
        """Evaluate response quality using ChatGPT"""
        eval_prompt = f"""
        Evaluate this response on a scale of 0-1 for:
        1. Coherence: Clear and logical flow
        2. Technical Depth: Detailed technical insights
        3. Strategic Value: Actionable strategic insights
        4. Uniqueness: Novel perspectives
        
        Response to evaluate:
        {response.content}
        
        Return scores in JSON format.
        """

        try:
            eval_response = await self.chatgpt.generate(eval_prompt)
            scores = json.loads(eval_response)
            return QualityMetrics(
                coherence_score=scores["coherence"],
                technical_depth=scores["technical_depth"],
                strategic_value=scores["strategic_value"],
                uniqueness=scores["uniqueness"],
            )
        except Exception as e:
            self.logger.error(f"Quality evaluation failed: {e}")
            return QualityMetrics()

    async def get_model_response(
        self, model, prompt: str, stage: str, use_cache: bool = True
    ) -> ModelResponse:
        """Get response with caching and retries"""
        if use_cache and self.cache:
            cache_key = f"{prompt}_{model.__class__.__name__}_{stage}"
            cached = self.cache.get(cache_key)
            if cached:
                return cached

        for attempt in range(self.max_retries):
            try:
                start_time = asyncio.get_running_loop().time()
                response = await model.generate(prompt)
                end_time = asyncio.get_running_loop().time()

                model_response = ModelResponse(
                    model_name=model.__class__.__name__,
                    content=response,
                    stage=stage,
                    timestamp=start_time,
                    tokens_used=len(response.split()),  # Simple approximation
                )

                # Evaluate quality
                model_response.quality = await self.evaluate_quality(model_response)

                # Update metrics
                self.update_metrics(model_response, end_time - start_time)

                # Cache response
                if use_cache and self.cache:
                    self.cache.set(cache_key, model_response)

                return model_response

            except Exception as e:
                self.logger.error(f"Attempt {attempt + 1} failed: {e}")
                if attempt == self.max_retries - 1:
                    raise

    def update_metrics(self, response: ModelResponse, response_time: float):
        """Update performance metrics"""
        self.metrics["response_times"].append(response_time)

        model = response.model_name
        if model not in self.metrics["success_rates"]:
            self.metrics["success_rates"][model] = {"success": 0, "total": 0}

        self.metrics["success_rates"][model]["total"] += 1
        self.metrics["success_rates"][model]["success"] += 1

        if model not in self.metrics["token_usage"]:
            self.metrics["token_usage"][model] = 0
        self.metrics["token_usage"][model] += response.tokens_used

        if model not in self.metrics["quality_scores"]:
            self.metrics["quality_scores"][model] = []
        self.metrics["quality_scores"][model].append(response.quality.average_score())

    async def process_responses(self, prompt: str) -> Dict[str, Any]:
        """Enhanced main processing pipeline"""
        try:
            # 1. Get initial responses from all models
            initial_responses = await asyncio.gather(
                *[
                    self.get_model_response(model, prompt, "initial")
                    for model in [self.llama, self.chatgpt, self.gemini]
                ],
                return_exceptions=True,
            )

            # 2. Meta analysis (using successful initial responses)
            valid_responses = [
                r for r in initial_responses if not isinstance(r, Exception)
            ]
            if not valid_responses:
                raise ValueError("No valid initial responses received")

            meta_prompt = self._create_meta_prompt(valid_responses)
            meta_responses = await asyncio.gather(
                self.get_model_response(self.chatgpt, meta_prompt, "meta"),
                self.get_model_response(self.gemini, meta_prompt, "meta"),
                return_exceptions=True,
            )

            # 3. Final synthesis (using ChatGPT for best structured output)
            synthesis_prompt = self._create_synthesis_prompt(
                valid_responses,
                [r for r in meta_responses if not isinstance(r, Exception)],
            )
            final_synthesis = await self.get_model_response(
                self.chatgpt, synthesis_prompt, "synthesis"
            )

            # Export results
            return {
                "status": "success",
                "initial_responses": [r.to_json() for r in initial_responses],
                "meta_responses": [r.to_json() for r in meta_responses],
                "final_synthesis": final_synthesis.to_json(),
                "metrics": self.metrics,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            self.logger.error(f"Pipeline error: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def _create_meta_prompt(self, responses: List[ModelResponse]) -> str:
        """Create prompt for meta analysis"""
        return f"""
        Analyze these model responses and identify:
        1. Key technical insights
        2. Strategic implications
        3. Areas of agreement/disagreement
        4. Unique perspectives from each model

        Responses to analyze:
        {[resp.content for resp in responses]}
        """

    def _create_synthesis_prompt(
        self,
        initial_responses: List[ModelResponse],
        meta_responses: List[ModelResponse],
    ) -> str:
        """Create prompt for final synthesis"""
        return f"""
        Create a comprehensive synthesis including:
        1. Technical implementation details
        2. Strategic insights
        3. Consensus points across models
        4. Key recommendations

        Initial analyses:
        {[resp.content for resp in initial_responses]}

        Meta analyses:
        {[resp.content for resp in meta_responses]}
        """
