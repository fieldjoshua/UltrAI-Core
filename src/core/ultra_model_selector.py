import argparse
from typing import List, Dict, Any
from ultra_models import UltraModels, ModelCategory
import json
import asyncio
import os
from dotenv import load_dotenv

class ModelSelector:
    def __init__(self):
        self.models = UltraModels()
        load_dotenv()  # Load environment variables
    
    def display_model_summary(self):
        """Display a summary of all available models."""
        summary = self.models.get_model_summary()
        
        print("\n=== Ultra Model Selection ===\n")
        
        for category, models in summary.items():
            print(f"\n{category.upper()} MODELS:")
            print("-" * 50)
            for model in models:
                status = "✓" if model['is_enabled'] else "✗"
                cost = f"${model['cost']}/1k tokens" if model['cost'] is not None else "Free"
                print(f"{status} {model['name']} ({model['id']})")
                print(f"   Description: {model['description']}")
                print(f"   Cost: {cost}")
                print()
    
    def display_model_details(self, model_id: str):
        """Display detailed information about a specific model."""
        info = self.models.get_model_info(model_id)
        if info:
            print(f"\n=== {info['name']} Details ===\n")
            print(f"Category: {info['category']}")
            print(f"Provider: {info['provider']}")
            print(f"API Key Required: {'Yes' if info['api_key_required'] else 'No'}")
            print(f"Base URL: {info['base_url'] or 'N/A'}")
            print(f"Available Models: {', '.join(info['models'])}")
            print(f"Description: {info['description']}")
            print(f"Max Tokens: {info['max_tokens']}")
            print(f"Temperature: {info['temperature']}")
            print(f"Cost per 1k tokens: ${info['cost_per_1k_tokens']}" if info['cost_per_1k_tokens'] else "Cost per 1k tokens: Free")
            print(f"Status: {'Enabled' if info['is_enabled'] else 'Disabled'}")
            if info.get('strengths'):
                print(f"Strengths: {', '.join(info['strengths'])}")
            if info.get('limitations'):
                print(f"Limitations: {', '.join(info['limitations'])}")
        else:
            print(f"Model {model_id} not found.")
    
    def toggle_model(self, model_id: str, enable: bool) -> bool:
        """Enable or disable a specific model."""
        if enable:
            success = self.models.enable_model(model_id)
            action = "enabled"
        else:
            success = self.models.disable_model(model_id)
            action = "disabled"
        
        if success:
            print(f"Model {model_id} has been {action}.")
            return True
        else:
            print(f"Failed to {action} model {model_id}.")
            return False
    
    def save_configuration(self):
        """Save the current model configuration."""
        self.models.save_configuration()
        print("Model configuration saved.")
    
    def get_enabled_models(self) -> List[str]:
        """Get list of currently enabled models."""
        return self.models.get_enabled_models()

    async def select_best_models(self, inquiry: str):
        """Select the best models for a given inquiry."""
        # Get API keys from environment variables
        api_keys = {
            "openai": os.getenv("OPENAI_API_KEY"),
            "anthropic": os.getenv("ANTHROPIC_API_KEY"),
            "mistral": os.getenv("MISTRAL_API_KEY"),
            "deepseek": os.getenv("DEEPSEEK_API_KEY"),
            "google": os.getenv("GOOGLE_API_KEY")
        }
        
        print(f"\nAnalyzing inquiry: {inquiry}")
        print("Selecting best models...\n")
        
        selected_models = await self.models.select_best_models(inquiry, api_keys)
        
        print("Recommended Models:")
        print("-" * 50)
        for model_id, reason in selected_models:
            info = self.models.get_model_info(model_id)
            if info:
                print(f"\n{info['name']} ({model_id})")
                print(f"Reason: {reason}")
                print(f"Category: {info['category']}")
                print(f"Cost: {'Free' if info['cost_per_1k_tokens'] is None else f'${info['cost_per_1k_tokens']}/1k tokens'}")
                print(f"Strengths: {', '.join(info.get('strengths', []))}")

def main():
    parser = argparse.ArgumentParser(description="Ultra Model Selection Tool")
    parser.add_argument("--list", action="store_true", help="List all available models")
    parser.add_argument("--details", type=str, help="Show details for a specific model")
    parser.add_argument("--enable", type=str, help="Enable a specific model")
    parser.add_argument("--disable", type=str, help="Disable a specific model")
    parser.add_argument("--save", action="store_true", help="Save current configuration")
    parser.add_argument("--enabled", action="store_true", help="Show currently enabled models")
    parser.add_argument("--select", type=str, help="Select best models for a given inquiry")
    
    args = parser.parse_args()
    selector = ModelSelector()
    
    if args.list:
        selector.display_model_summary()
    elif args.details:
        selector.display_model_details(args.details)
    elif args.enable:
        selector.toggle_model(args.enable, True)
    elif args.disable:
        selector.toggle_model(args.disable, False)
    elif args.save:
        selector.save_configuration()
    elif args.enabled:
        enabled = selector.get_enabled_models()
        print("\nCurrently enabled models:")
        for model_id in enabled:
            info = selector.models.get_model_info(model_id)
            print(f"- {info['name']} ({model_id})")
    elif args.select:
        asyncio.run(selector.select_best_models(args.select))
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 