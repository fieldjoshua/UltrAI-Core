import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from .models import ModelResponse, QualityMetrics, ResponseCache


class MultiLLMOrchestrator:
    """
    Orchestrator for multiple LLMs with dynamic model registration and flexible pipeline.
    Usage:
        orchestrator = MultiLLMOrchestrator()
        orchestrator.register_model('llama', llama_client)
        orchestrator.register_model('chatgpt', chatgpt_client)
        orchestrator.register_model('gemini', gemini_client)
        ...
    """

    def __init__(self, cache_enabled: bool = True, max_retries: int = 3):
        self.models = {}
        self.model_weights = {}  # Store weights for model prioritization
        self.cache = ResponseCache() if cache_enabled else None
        self.logger = logging.getLogger(__name__)
        self.max_retries = max_retries
        self.metrics = {
            "response_times": [],
            "success_rates": {},
            "token_usage": {},
            "quality_scores": {},
        }

    def register_model(self, name: str, client, weight: float = 1.0):
        """
        Register a new model client by name with optional weight.

        Args:
            name: Unique string identifier for the model
            client: Client that implements a .generate(prompt) async method
            weight: Weight for prioritizing model responses (higher = more important)
        """
        self.models[name] = client
        self.model_weights[name] = weight
        self.logger.info(f"Registered model '{name}' with weight {weight}")

    def set_model_weight(self, name: str, weight: float):
        """
        Set or update the weight for a registered model.

        Args:
            name: The name of the registered model
            weight: New weight value (higher = more important)

        Raises:
            ValueError: If the model is not registered
        """
        if name not in self.models:
            raise ValueError(f"Model '{name}' is not registered")

        self.model_weights[name] = weight
        self.logger.info(f"Updated weight for model '{name}' to {weight}")

    def get_prioritized_models(
        self, required_models: Optional[List[str]] = None
    ) -> List[str]:
        """
        Get a list of model names sorted by their weights (highest first).

        Args:
            required_models: Optional list of specific models to include

        Returns:
            List of model names sorted by weight
        """
        if required_models:
            model_subset = {
                k: v for k, v in self.model_weights.items() if k in required_models
            }
        else:
            model_subset = self.model_weights

        return sorted(model_subset.keys(), key=lambda m: model_subset[m], reverse=True)

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
            eval_response = await self.models["chatgpt"].generate(eval_prompt)
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
                self.logger.info(f"Cache hit for {cache_key}")
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

                self.logger.info(
                    f"Response successfully obtained from {model.__class__.__name__} on attempt {attempt + 1}"
                )
                return model_response

            except Exception as e:
                self.logger.error(
                    f"Attempt {attempt + 1} failed for model {model.__class__.__name__}: {e}"
                )
        # If all retries fail, raise an error (never return None)
        error_message = f"All attempts failed for model {model.__class__.__name__}"
        self.logger.critical(error_message)
        raise RuntimeError(error_message)

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

    async def process_responses(
        self,
        prompt: str,
        stages: Optional[List[str]] = None,
        models: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Flexible processing pipeline. Stages can be ["initial", "meta", "synthesis", ...]

        Args:
            prompt: The prompt to process
            stages: List of pipeline stages to run (default: ["initial", "meta", "synthesis"])
            models: Specific models to use (default: all registered models)

        Returns:
            Dictionary with results from each stage

        Raises:
            ValueError: If no valid responses are received
        """
        if stages is None:
            stages = ["initial", "meta", "synthesis"]

        # If models is specified, validate that they exist
        if models:
            invalid_models = [m for m in models if m not in self.models]
            if invalid_models:
                raise ValueError(f"Invalid model(s) specified: {invalid_models}")

        # Get prioritized list of models
        prioritized_models = self.get_prioritized_models(models)

        try:
            self.logger.info(
                f"Starting process_responses with stages: {stages}, models: {prioritized_models}"
            )

            # 1. Initial responses from selected models
            initial_model_clients = [self.models[name] for name in prioritized_models]

            initial_responses = await asyncio.gather(
                *[
                    self.get_model_response(model, prompt, stages[0])
                    for model in initial_model_clients
                ],
                return_exceptions=True,
            )
            valid_responses = [
                r for r in initial_responses if isinstance(r, ModelResponse)
            ]
            if not valid_responses:
                error_message = "No valid initial responses received"
                self.logger.error(error_message)
                raise ValueError(error_message)

            # 2. Meta analysis (if requested)
            meta_responses = []
            if "meta" in stages:
                # Prioritize specific models for meta analysis if they exist
                meta_model_names = [
                    m for m in prioritized_models if m in ["chatgpt", "gemini"]
                ]

                # If we don't have preferred meta models, use the highest weighted model
                if not meta_model_names and prioritized_models:
                    meta_model_names = [prioritized_models[0]]

                if meta_model_names:
                    meta_prompt = self._create_meta_prompt(valid_responses)
                    meta_results = await asyncio.gather(
                        *[
                            self.get_model_response(
                                self.models[name], meta_prompt, "meta"
                            )
                            for name in meta_model_names
                        ],
                        return_exceptions=True,
                    )
                    meta_responses = [
                        r for r in meta_results if isinstance(r, ModelResponse)
                    ]

            # 3. Synthesis (if requested)
            final_synthesis = None
            if "synthesis" in stages:
                synthesis_prompt = self._create_synthesis_prompt(
                    valid_responses,
                    meta_responses,
                )

                # Select the best model for synthesis (prefer chatgpt, then highest weighted)
                synthesis_model_name = None
                if "chatgpt" in self.models and (
                    "chatgpt" in models if models else True
                ):
                    synthesis_model_name = "chatgpt"
                elif prioritized_models:
                    synthesis_model_name = prioritized_models[0]

                if synthesis_model_name:
                    try:
                        final_synthesis = await self.get_model_response(
                            self.models[synthesis_model_name],
                            synthesis_prompt,
                            "synthesis",
                        )
                    except Exception as e:
                        self.logger.error(
                            f"Synthesis failed with model {synthesis_model_name}: {e}"
                        )
                        final_synthesis = None

            self.logger.info("process_responses completed successfully")
            return {
                "status": "success",
                "initial_responses": [r.to_json() for r in valid_responses],
                "meta_responses": [r.to_json() for r in meta_responses],
                "final_synthesis": (
                    final_synthesis.to_json() if final_synthesis else None
                ),
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
