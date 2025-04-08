#!/usr/bin/env python3
import re
import sys

from pricing_calculator import PricingCalculator


class RealtimePricingEstimator:
    """Estimates token usage and pricing in real-time for user prompts"""

    def __init__(self, tier="basic"):
        self.calculator = PricingCalculator()
        self.tier = tier
        self.tokenizer_pattern = re.compile(r"\s+|\b")

    def estimate_tokens(self, text):
        """
        Estimate token count for a text string using a simple approximation
        Note: This is a rough estimation, not as accurate as model-specific tokenizers
        """
        # Simple approximation: split on whitespace and word boundaries
        tokens = self.tokenizer_pattern.split(text)
        return len([t for t in tokens if t])  # Count non-empty tokens

    def get_real_time_estimate(self, user_prompt, model="gpt-3.5-turbo", features=None):
        """
        Get real-time pricing estimate for a user prompt

        Args:
            user_prompt: The user's prompt text
            model: The model to use for estimation
            features: Additional features to include

        Returns:
            dict: Pricing estimate details
        """
        if features is None:
            features = []

        # Estimate token count
        estimated_tokens = self.estimate_tokens(user_prompt)

        # Add typical completion tokens (assume response is 2x the prompt)
        completion_tokens = estimated_tokens * 2
        total_tokens = estimated_tokens + completion_tokens

        # Get pricing
        pricing = self.calculator.calculate_cost(
            model, total_tokens, self.tier, features
        )

        # Add token estimates to the pricing info
        pricing.update(
            {
                "prompt_tokens": estimated_tokens,
                "estimated_completion_tokens": completion_tokens,
                "prompt_text_preview": (
                    user_prompt[:100] + "..." if len(user_prompt) > 100 else user_prompt
                ),
            }
        )

        return pricing


def main():
    """Interactive demo of real-time pricing estimation"""
    print("=== Ultra Framework Real-time Pricing Estimator ===\n")

    # Initialize with default tier
    tier = "basic"
    tier_options = {"1": "basic", "2": "pro", "3": "enterprise"}

    # Default model
    model = "gpt-3.5-turbo"
    model_options = {
        "1": "gpt-3.5-turbo",
        "2": "gpt-4",
        "3": "claude-3-sonnet",
        "4": "claude-3-opus",
        "5": "mistral-small",
        "6": "mistral-medium",
        "7": "mistral-large",
        "8": "gemini-pro",
        "9": "llama-70b",
        "10": "local",
    }

    # Create estimator
    estimator = RealtimePricingEstimator(tier)

    # Pricing configuration
    print("First, let's configure your pricing setup:")

    # Tier selection
    print("\nSelect pricing tier:")
    print("1. Basic ($10/month, 100K tokens included)")
    print("2. Pro ($30/month, 500K tokens included)")
    print("3. Enterprise ($100/month, 2M tokens included)")

    tier_choice = input("Enter tier (1-3) [1]: ").strip() or "1"
    if tier_choice in tier_options:
        tier = tier_options[tier_choice]
        estimator.tier = tier

    # Model selection
    print("\nSelect default model:")
    print("1. gpt-3.5-turbo (OpenAI GPT-3.5)")
    print("2. gpt-4 (OpenAI GPT-4)")
    print("3. claude-3-sonnet (Anthropic Claude 3 Sonnet)")
    print("4. claude-3-opus (Anthropic Claude 3 Opus)")
    print("5. mistral-small (Mistral Small)")
    print("6. mistral-medium (Mistral Medium)")
    print("7. mistral-large (Mistral Large)")
    print("8. gemini-pro (Google Gemini Pro)")
    print("9. llama-70b (Meta Llama 70B)")
    print("10. local (Local models)")

    model_choice = input("Enter model (1-10) [1]: ").strip() or "1"
    if model_choice in model_options:
        model = model_options[model_choice]

    # Feature selection
    features = []
    features_options = {
        "1": "document_processing",
        "2": "additional_iterations",
        "3": "custom_patterns",
        "4": "api_access",
        "5": "priority_processing",
    }

    print("\nSelect additional features (comma-separated numbers):")
    print("1. document_processing (Per page: $0.001)")
    print("2. additional_iterations (Per iteration: $0.01)")
    print("3. custom_patterns (Monthly fee: $5.00)")
    print("4. api_access (Monthly fee: $20.00)")
    print("5. priority_processing (Per request: $0.02)")
    print("0. None")

    features_choice = input("Enter features [0]: ").strip() or "0"
    if features_choice != "0":
        feature_numbers = [n.strip() for n in features_choice.split(",")]
        for num in feature_numbers:
            if num in features_options:
                features.append(features_options[num])

    # Interactive prompt loop
    print("\n=== Ready for real-time pricing estimation ===")
    print(f"Tier: {tier}, Model: {model}, Features: {features if features else 'None'}")
    print("Type your prompt below (or 'quit' to exit):")

    while True:
        print("\n> ", end="")
        user_input = input()

        if user_input.lower() in ("quit", "exit", "q"):
            print("Goodbye!")
            break

        if not user_input.strip():
            continue

        # Get real-time estimate
        estimate = estimator.get_real_time_estimate(user_input, model, features)

        if estimate["status"] == "error":
            print(f"\nError: {estimate['message']}")
            print(
                f"Allowed models for {tier} tier: {', '.join(estimate['allowed_models'])}"
            )
            continue

        # Display estimate in a user-friendly format
        print("\n--- Real-time Pricing Estimate ---")
        print(f"Prompt tokens: {estimate['prompt_tokens']}")
        print(f"Estimated completion tokens: {estimate['estimated_completion_tokens']}")
        print(f"Total tokens: {estimate['token_count']}")
        print(f"Tokens charged (after included tokens): {estimate['tokens_charged']}")
        print(f"Base cost: ${estimate['base_cost']:.6f}")

        if estimate["discount_amount"] > 0:
            print(
                f"Volume discount ({estimate['volume_discount_percentage']}%): -${estimate['discount_amount']:.6f}"
            )

        if estimate["feature_costs"]:
            print(f"Feature costs: ${estimate['feature_cost_total']:.6f}")
            for feature, cost in estimate["feature_costs"].items():
                print(f"  - {feature}: ${cost:.6f}")

        print(f"\nTotal cost for this request: ${estimate['total_cost']:.6f}")

        # Monthly projection (assuming this query frequency)
        QUERIES_PER_DAY = 30  # Assuming 30 similar queries per day
        monthly_tokens = estimate["token_count"] * QUERIES_PER_DAY * 30
        print(f"\nMonthly projection (at {QUERIES_PER_DAY} similar queries per day):")
        print(f"Monthly tokens: {monthly_tokens:,}")
        print(
            f"Monthly cost (excluding subscription): ${(estimate['total_cost'] * QUERIES_PER_DAY * 30):.2f}"
        )
        print(f"Monthly subscription fee: ${estimate['monthly_fee']:.2f}")
        print(
            f"Total monthly cost: ${(estimate['total_cost'] * QUERIES_PER_DAY * 30 + estimate['monthly_fee']):.2f}"
        )


if __name__ == "__main__":
    main()
