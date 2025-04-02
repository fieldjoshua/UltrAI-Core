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
    cost_per_1k_tokens: Optional[float] = None
    is_enabled: bool = True
    strengths: List[str] = None  # List of task types this model excels at
    limitations: List[str] = None  # List of task types this model is less suitable for

class UltraModels:
    def __init__(self):
        self.available_models: Dict[str, ModelConfig] = {
            # Commercial Models
            "openai": ModelConfig(
                name="OpenAI",
                category=ModelCategory.COMMERCIAL,
                provider="openai",
                api_key_required=True,
                base_url="https://api.openai.com/v1",
                models=["gpt-4", "gpt-3.5-turbo"],
                description="OpenAI's powerful language models",
                cost_per_1k_tokens=0.03,
                strengths=["general reasoning", "complex analysis", "creative writing", "code generation"],
                limitations=["cost", "API rate limits"]
            ),
            "anthropic": ModelConfig(
                name="Anthropic Claude",
                category=ModelCategory.COMMERCIAL,
                provider="anthropic",
                api_key_required=True,
                base_url="https://api.anthropic.com/v1",
                models=["claude-3-opus-20240229", "claude-3-sonnet-20240229"],
                description="Anthropic's Claude models with strong reasoning capabilities",
                cost_per_1k_tokens=0.015,
                strengths=["detailed analysis", "ethical reasoning", "long-form content", "research"],
                limitations=["cost", "API rate limits"]
            ),
            "mistral": ModelConfig(
                name="Mistral AI",
                category=ModelCategory.COMMERCIAL,
                provider="mistral",
                api_key_required=True,
                base_url="https://api.mistral.ai/v1",
                models=["mistral-tiny", "mistral-small", "mistral-medium", "mistral-large"],
                description="Mistral's efficient and powerful models",
                cost_per_1k_tokens=0.0002,
                strengths=["efficiency", "multilingual", "code generation", "reasoning"],
                limitations=["API rate limits"]
            ),
            "deepseek": ModelConfig(
                name="DeepSeek",
                category=ModelCategory.COMMERCIAL,
                provider="deepseek",
                api_key_required=True,
                base_url="https://api.deepseek.com/v1",
                models=["deepseek-chat", "deepseek-coder"],
                description="DeepSeek's specialized models for chat and code",
                cost_per_1k_tokens=0.0001,
                strengths=["code generation", "technical analysis", "chat", "efficiency"],
                limitations=["API rate limits"]
            ),
            
            # Open Source Models (API)
            "google": ModelConfig(
                name="Google Gemini",
                category=ModelCategory.OPEN_SOURCE,
                provider="google",
                api_key_required=True,
                models=["gemini-pro"],
                description="Google's open source language model",
                cost_per_1k_tokens=0.00025,
                strengths=["multimodal", "general knowledge", "creative tasks"],
                limitations=["API rate limits"]
            ),
            
            # Local Models
            "ollama": ModelConfig(
                name="Ollama",
                category=ModelCategory.LOCAL,
                provider="ollama",
                api_key_required=False,
                base_url="http://localhost:11434",
                models=["mixtral", "llama2", "codellama", "mistral", "neural-chat"],
                description="Local models running through Ollama",
                cost_per_1k_tokens=0,
                strengths=["privacy", "no rate limits", "offline use", "customization"],
                limitations=["hardware requirements", "model size"]
            ),
            "llama": ModelConfig(
                name="Llama",
                category=ModelCategory.LOCAL,
                provider="llama",
                api_key_required=False,
                base_url="http://localhost:5000",
                models=["llama2-7b", "llama2-13b", "llama2-70b"],
                description="Meta's Llama models running locally",
                cost_per_1k_tokens=0,
                strengths=["privacy", "no rate limits", "offline use"],
                limitations=["hardware requirements", "model size"]
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
                'cost_per_1k_tokens': config.cost_per_1k_tokens,
                'is_enabled': config.is_enabled
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