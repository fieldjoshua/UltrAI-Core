from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import json
import os
import asyncio
from openai import AsyncOpenAI

class ModelCategory(Enum):
    COMMERCIAL = "commercial"  # Paid API models
    OPEN_SOURCE = "open_source"  # Free/open source models
    LOCAL = "local"  # Models that run locally

@dataclass
class ModelConfig:
    name: str
    category: ModelCategory
    provider: str
    api_key_required: bool
    base_url: Optional[str] = None
    models: List[str] = None
    description: str = ""
    max_tokens: int = 2000
    temperature: float = 0.7
    input_cost_per_1k_tokens: Optional[float] = None
    output_cost_per_1k_tokens: Optional[float] = None
    cost_per_1k_tokens: Optional[float] = None
    context_window: Optional[int] = None
    is_enabled: bool = True
    is_thinking_model: bool = False
    strengths: List[str] = None  # List of task types this model excels at
    limitations: List[str] = None  # List of task types this model is less suitable for

class UltraModels:
    def __init__(self):
        self.available_models: Dict[str, ModelConfig] = {
            # OpenAI Models
            "gpt4o": ModelConfig(
                name="GPT-4o",
                category=ModelCategory.COMMERCIAL,
                provider="openai",
                api_key_required=True,
                base_url="https://api.openai.com/v1",
                models=["gpt-4o-2024-05-13"],
                description="OpenAI's balanced model optimized for reasoning and instruction following",
                input_cost_per_1k_tokens=0.0025,
                output_cost_per_1k_tokens=0.0100,
                cost_per_1k_tokens=0.0125,
                context_window=128000,
                is_thinking_model=True,
                strengths=["reasoning", "complex analysis", "synthesizing information", "balanced outputs"],
                limitations=["cost", "API rate limits"]
            ),
            "gpto1": ModelConfig(
                name="GPT-o1",
                category=ModelCategory.COMMERCIAL,
                provider="openai",
                api_key_required=True,
                base_url="https://api.openai.com/v1",
                models=["gpt-o1"],
                description="OpenAI's most powerful model with exceptional reasoning and analysis",
                input_cost_per_1k_tokens=0.015,
                output_cost_per_1k_tokens=0.060,
                cost_per_1k_tokens=0.075,
                context_window=200000,
                is_thinking_model=True,
                strengths=["advanced reasoning", "complex problem solving", "nuanced understanding", "largest context awareness"],
                limitations=["highest cost", "API rate limits"]
            ),
            "gpto3mini": ModelConfig(
                name="GPT-o3 mini",
                category=ModelCategory.COMMERCIAL,
                provider="openai",
                api_key_required=True,
                base_url="https://api.openai.com/v1",
                models=["gpt-o3-mini"],
                description="Efficient OpenAI model with large context window and good performance",
                input_cost_per_1k_tokens=0.00110,
                output_cost_per_1k_tokens=0.00440,
                cost_per_1k_tokens=0.00550,
                context_window=200000,
                strengths=["efficiency", "large context window", "good reasoning", "affordable"],
                limitations=["less powerful than GPT-o1"]
            ),
            "gpt4o_mini": ModelConfig(
                name="GPT-4o Mini",
                category=ModelCategory.COMMERCIAL,
                provider="openai",
                api_key_required=True,
                base_url="https://api.openai.com/v1",
                models=["gpt-4o-mini"],
                description="More affordable version of GPT-4o with very good performance",
                input_cost_per_1k_tokens=0.00015,
                output_cost_per_1k_tokens=0.00060,
                cost_per_1k_tokens=0.00075,
                context_window=128000,
                strengths=["efficiency", "good reasoning", "fast responses", "affordable"],
                limitations=["less powerful than GPT-4o"]
            ),
            "gpt4_turbo": ModelConfig(
                name="GPT-4 Turbo",
                category=ModelCategory.COMMERCIAL,
                provider="openai",
                api_key_required=True, 
                base_url="https://api.openai.com/v1",
                models=["gpt-4-turbo"],
                description="OpenAI's powerful GPT-4 model with optimized performance",
                input_cost_per_1k_tokens=0.01,
                output_cost_per_1k_tokens=0.03,
                cost_per_1k_tokens=0.04,
                context_window=128000,
                is_thinking_model=True,
                strengths=["reasoning", "complex analysis", "synthesizing information"],
                limitations=["cost", "API rate limits"]
            ),
            "gpt35_turbo": ModelConfig(
                name="GPT-3.5 Turbo",
                category=ModelCategory.COMMERCIAL,
                provider="openai",
                api_key_required=True,
                base_url="https://api.openai.com/v1",
                models=["gpt-3.5-turbo"],
                description="OpenAI's fast and cost-effective model",
                input_cost_per_1k_tokens=0.0005,
                output_cost_per_1k_tokens=0.0015,
                cost_per_1k_tokens=0.0020,
                context_window=4096,
                strengths=["speed", "cost", "good for simple tasks"],
                limitations=["limited reasoning", "smaller context window"]
            ),
            
            # Anthropic Models
            "claude37": ModelConfig(
                name="Claude 3.7 Sonnet",
                category=ModelCategory.COMMERCIAL,
                provider="anthropic",
                api_key_required=True,
                base_url="https://api.anthropic.com/v1",
                models=["claude-3-7-sonnet-20240620"],
                description="Anthropic's latest model with excellent reasoning capabilities",
                input_cost_per_1k_tokens=0.003,
                output_cost_per_1k_tokens=0.015,
                cost_per_1k_tokens=0.018,
                context_window=200000,
                is_thinking_model=True,
                strengths=["detailed analysis", "synthesis", "long-form content", "research"],
                limitations=["cost", "API rate limits"]
            ),
            "claude3_opus": ModelConfig(
                name="Claude 3 Opus",
                category=ModelCategory.COMMERCIAL,
                provider="anthropic",
                api_key_required=True,
                base_url="https://api.anthropic.com/v1",
                models=["claude-3-opus-20240229"],
                description="Anthropic's most capable model with exceptional reasoning",
                input_cost_per_1k_tokens=0.015,
                output_cost_per_1k_tokens=0.075,
                cost_per_1k_tokens=0.090,
                context_window=200000,
                is_thinking_model=True,
                strengths=["complex reasoning", "nuanced understanding", "comprehensive analysis"],
                limitations=["highest cost", "API rate limits"]
            ),
            "claude35_haiku": ModelConfig(
                name="Claude 3.5 Haiku",
                category=ModelCategory.COMMERCIAL,
                provider="anthropic",
                api_key_required=True,
                base_url="https://api.anthropic.com/v1",
                models=["claude-3-5-haiku-20240307"],
                description="Anthropic's fast, cost-effective model with good capabilities",
                input_cost_per_1k_tokens=0.0008,
                output_cost_per_1k_tokens=0.0040,
                cost_per_1k_tokens=0.0048,
                context_window=200000,
                strengths=["speed", "efficiency", "good balance of capabilities and cost"],
                limitations=["less capable than larger Claude models"]
            ),
            
            # Google Models
            "gemini15": ModelConfig(
                name="Google Gemini 1.5",
                category=ModelCategory.COMMERCIAL,
                provider="google",
                api_key_required=True,
                models=["gemini-1.5-pro"],
                description="Google's efficient model with excellent capabilities",
                input_cost_per_1k_tokens=0.000075,
                output_cost_per_1k_tokens=0.000300,
                cost_per_1k_tokens=0.000375,
                context_window=128000,
                strengths=["efficiency", "multimodal capabilities", "cost-effectiveness"],
                limitations=["API rate limits"]
            ),
            "gemini25_pro_max": ModelConfig(
                name="Google Gemini 2.5 Pro Max",
                category=ModelCategory.COMMERCIAL,
                provider="google",
                api_key_required=True,
                models=["gemini-2.5-pro-max"],
                description="Google's latest flagship model with massive context window",
                input_cost_per_1k_tokens=0.003,
                output_cost_per_1k_tokens=0.015,
                cost_per_1k_tokens=0.018,
                context_window=1000000,
                is_thinking_model=True,
                strengths=["massive context window", "complex analysis", "advanced reasoning"],
                limitations=["cost", "API rate limits"]
            ),
            
            # Local Models            
            "llama3": ModelConfig(
                name="Llama 3",
                category=ModelCategory.LOCAL,
                provider="meta",
                api_key_required=False,
                base_url="http://localhost:5000",
                models=["llama3-70b", "llama3-8b"],
                description="Meta's Llama 3 model running locally",
                input_cost_per_1k_tokens=0,
                output_cost_per_1k_tokens=0,
                cost_per_1k_tokens=0,
                context_window=8192,
                strengths=["privacy", "no rate limits", "offline use"],
                limitations=["hardware requirements", "model size"]
            ),
            "mistral": ModelConfig(
                name="Mistral",
                category=ModelCategory.LOCAL,
                provider="mistral",
                api_key_required=False,
                base_url="http://localhost:11434",
                models=["mistral-small", "mistral-medium", "mistral-large"],
                description="Mistral models running locally",
                input_cost_per_1k_tokens=0,
                output_cost_per_1k_tokens=0,
                cost_per_1k_tokens=0,
                context_window=8192,
                strengths=["privacy", "no rate limits", "offline use", "efficiency"],
                limitations=["hardware requirements"]
            )
        }
        
        # Load saved configuration if exists
        self.config_file = "ultra_models_config.json"
        self.load_configuration()
    
    def load_configuration(self):
        """Load saved model configuration from file."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    saved_config = json.load(f)
                    for model_id, config in saved_config.items():
                        if model_id in self.available_models:
                            self.available_models[model_id].is_enabled = config.get('is_enabled', True)
            except Exception as e:
                print(f"Error loading model configuration: {e}")
    
    def save_configuration(self):
        """Save current model configuration to file."""
        try:
            config = {
                model_id: {
                    'is_enabled': model_config.is_enabled
                }
                for model_id, model_config in self.available_models.items()
            }
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Error saving model configuration: {e}")
    
    def get_enabled_models(self) -> List[str]:
        """Get list of enabled model providers."""
        return [
            model_id for model_id, config in self.available_models.items()
            if config.is_enabled
        ]
    
    def get_models_by_category(self, category: ModelCategory) -> List[str]:
        """Get list of models in a specific category."""
        return [
            model_id for model_id, config in self.available_models.items()
            if config.category == category
        ]
    
    def get_thinking_models(self) -> List[str]:
        """Get list of models designated as thinking models."""
        return [
            model_id for model_id, config in self.available_models.items()
            if config.is_thinking_model
        ]
    
    def enable_model(self, model_id: str) -> bool:
        """Enable a specific model."""
        if model_id in self.available_models:
            self.available_models[model_id].is_enabled = True
            self.save_configuration()
            return True
        return False
    
    def disable_model(self, model_id: str) -> bool:
        """Disable a specific model."""
        if model_id in self.available_models:
            self.available_models[model_id].is_enabled = False
            self.save_configuration()
            return True
        return False
    
    def get_model_info(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific model."""
        if model_id in self.available_models:
            config = self.available_models[model_id]
            return {
                'name': config.name,
                'category': config.category.value,
                'provider': config.provider,
                'api_key_required': config.api_key_required,
                'base_url': config.base_url,
                'models': config.models,
                'description': config.description,
                'max_tokens': config.max_tokens,
                'temperature': config.temperature,
                'input_cost_per_1k_tokens': config.input_cost_per_1k_tokens,
                'output_cost_per_1k_tokens': config.output_cost_per_1k_tokens,
                'cost_per_1k_tokens': config.cost_per_1k_tokens,
                'context_window': config.context_window,
                'is_enabled': config.is_enabled,
                'is_thinking_model': config.is_thinking_model,
                'strengths': config.strengths,
                'limitations': config.limitations
            }
        return None
    
    def get_model_summary(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get a summary of all models grouped by category."""
        summary = {
            category.value: []
            for category in ModelCategory
        }
        
        for model_id, config in self.available_models.items():
            summary[config.category.value].append({
                'id': model_id,
                'name': config.name,
                'description': config.description,
                'is_enabled': config.is_enabled,
                'cost': config.cost_per_1k_tokens
            })
        
        return summary 

    async def select_best_models(self, inquiry: str, api_keys: Dict[str, str]) -> List[Tuple[str, str]]:
        """
        Use an LLM to analyze the inquiry and select the best three models for the task.
        Returns a list of tuples containing (model_id, reason_for_selection).
        """
        # Create a prompt that describes the available models and their strengths
        model_descriptions = []
        for model_id, config in self.available_models.items():
            if config.is_enabled:
                model_descriptions.append(
                    f"{config.name} ({model_id}):\n"
                    f"Strengths: {', '.join(config.strengths)}\n"
                    f"Limitations: {', '.join(config.limitations)}\n"
                    f"Cost: {'Free' if config.cost_per_1k_tokens is None else f'${config.cost_per_1k_tokens}/1k tokens'}"
                )

        prompt = f"""Analyze the following inquiry and select the three most appropriate models from the available options.
Consider the models' strengths, limitations, and cost when making your selection.

Inquiry: {inquiry}

Available Models:
{chr(10).join(model_descriptions)}

Please select exactly three models and provide a brief reason for each selection.
Format your response as a JSON array of objects with 'model_id' and 'reason' fields.
Example:
[
    {{"model_id": "openai", "reason": "Best for complex reasoning tasks"}},
    {{"model_id": "ollama", "reason": "Good for privacy-sensitive tasks"}},
    {{"model_id": "mistral", "reason": "Efficient for multilingual tasks"}}
]"""

        try:
            # Use OpenAI's GPT-4 for the analysis (most capable for this task)
            client = AsyncOpenAI(api_key=api_keys.get("openai"))
            response = await client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a model selection expert. Select exactly three models that best suit the given inquiry."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            # Parse the response
            selected_models = json.loads(response.choices[0].message.content)
            
            # Validate the selections
            valid_selections = []
            for selection in selected_models:
                model_id = selection.get("model_id")
                if model_id in self.available_models and self.available_models[model_id].is_enabled:
                    valid_selections.append((model_id, selection.get("reason", "No reason provided")))
            
            return valid_selections[:3]  # Ensure we return at most 3 models
            
        except Exception as e:
            print(f"Error in model selection: {e}")
            # Fallback to a simple selection based on enabled models
            enabled_models = self.get_enabled_models()
            return [(model_id, "Fallback selection") for model_id in enabled_models[:3]] 