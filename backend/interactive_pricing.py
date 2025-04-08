#!/usr/bin/env python3
import json

from pricing_calculator import PricingCalculator


def get_input(prompt, default=None, type_converter=str):
    """Get user input with a default value"""
    if default is not None:
        result = input(f"{prompt} [{default}]: ")
        if not result:
            return default
    else:
        result = input(f"{prompt}: ")

    try:
        return type_converter(result)
    except ValueError:
        print(f"Invalid input. Using default: {default}")
        return default


def get_model_distribution():
    """Get model distribution from user input"""
    models = {}

    print("\nAvailable models:")
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

    model_map = {
        1: "gpt-3.5-turbo",
        2: "gpt-4",
        3: "claude-3-sonnet",
        4: "claude-3-opus",
        5: "mistral-small",
        6: "mistral-medium",
        7: "mistral-large",
        8: "gemini-pro",
        9: "llama-70b",
        10: "local",
    }

    while True:
        try:
            count = get_input("How many different models? (1-5)", 1, int)
            if not 1 <= count <= 5:
                print("Please enter a number between 1 and 5.")
                continue

            total_percentage = 0

            for i in range(count):
                while True:
                    model_num = get_input(f"Model #{i+1} (enter number 1-10)", 1, int)
                    if not 1 <= model_num <= 10:
                        print("Please enter a number between 1 and 10.")
                        continue

                    model_name = model_map[model_num]
                    if model_name in models:
                        print(
                            f"You've already added {model_name}. Please choose a different model."
                        )
                        continue

                    percentage = get_input(
                        f"Percentage for {model_name} (1-100)",
                        100 if i == 0 else 0,
                        int,
                    )
                    if not 0 <= percentage <= 100:
                        print("Please enter a percentage between 0 and 100.")
                        continue

                    total_percentage += percentage
                    models[model_name] = percentage / 100
                    break

            # Normalize
            if total_percentage != 100:
                print(
                    f"Total percentage ({total_percentage}%) is not 100%. Normalizing values..."
                )
                for model in models:
                    models[model] = models[model] * 100 / total_percentage

            return models

        except ValueError as e:
            print(f"Error: {e}")
            print("Let's try again.")


def get_features():
    """Get features from user input"""
    features = []

    print("\nAvailable features (additional costs):")
    print("1. document_processing (Per page: $0.001)")
    print("2. additional_iterations (Per iteration: $0.01)")
    print("3. custom_patterns (Monthly fee: $5.00)")
    print("4. api_access (Monthly fee: $20.00)")
    print("5. priority_processing (Per request: $0.02)")

    feature_map = {
        1: "document_processing",
        2: "additional_iterations",
        3: "custom_patterns",
        4: "api_access",
        5: "priority_processing",
    }

    include_features = get_input("Include features? (y/n)", "n").lower()
    if include_features != "y":
        return features

    while True:
        try:
            count = get_input("How many features? (0-5)", 0, int)
            if not 0 <= count <= 5:
                print("Please enter a number between 0 and 5.")
                continue

            for i in range(count):
                while True:
                    feature_num = get_input(
                        f"Feature #{i+1} (enter number 1-5)", 1, int
                    )
                    if not 1 <= feature_num <= 5:
                        print("Please enter a number between 1 and 5.")
                        continue

                    feature_name = feature_map[feature_num]
                    if feature_name in features:
                        print(
                            f"You've already added {feature_name}. Please choose a different feature."
                        )
                        continue

                    features.append(feature_name)
                    break

            return features

        except ValueError as e:
            print(f"Error: {e}")
            print("Let's try again.")


def main():
    calculator = PricingCalculator()

    print("=== Ultra Framework Interactive Pricing Calculator ===\n")

    while True:
        print("\nWhat would you like to calculate?")
        print("1. Single query cost")
        print("2. Monthly cost estimation")
        print("3. Exit")

        choice = get_input("Enter your choice (1-3)", 1, int)

        if choice == 3:
            print("Goodbye!")
            break

        # Get pricing tier
        print("\nChoose a pricing tier:")
        print("1. Basic ($10/month, 100K tokens included)")
        print("2. Pro ($30/month, 500K tokens included)")
        print("3. Enterprise ($100/month, 2M tokens included)")

        tier_choice = get_input("Enter tier (1-3)", 1, int)
        tier_map = {1: "basic", 2: "pro", 3: "enterprise"}
        tier = tier_map.get(tier_choice, "basic")

        if choice == 1:
            # Single query
            print("\nCalculate cost for a single query")

            # Get model
            print("\nChoose a model:")
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

            model_choice = get_input("Enter model (1-10)", 1, int)
            model_map = {
                1: "gpt-3.5-turbo",
                2: "gpt-4",
                3: "claude-3-sonnet",
                4: "claude-3-opus",
                5: "mistral-small",
                6: "mistral-medium",
                7: "mistral-large",
                8: "gemini-pro",
                9: "llama-70b",
                10: "local",
            }
            model = model_map.get(model_choice, "gpt-3.5-turbo")

            # Get token count
            token_count = get_input("Enter token count", 1000, int)

            # Get features
            features = get_features()

            # Calculate
            result = calculator.calculate_cost(model, token_count, tier, features)

            print("\nCost calculation result:")
            print(json.dumps(result, indent=2))

        elif choice == 2:
            # Monthly estimation
            print("\nEstimate monthly cost")

            # Get queries per day
            daily_queries = get_input("Enter number of queries per day", 100, int)

            # Get average tokens per query
            avg_tokens = get_input("Enter average tokens per query", 2000, int)

            # Get model distribution
            model_distribution = get_model_distribution()

            # Get features
            features = get_features()

            # Calculate
            result = calculator.estimate_monthly_cost(
                daily_queries, avg_tokens, model_distribution, tier, features
            )

            print("\nMonthly cost estimation result:")
            print(json.dumps(result, indent=2))

            # Show detailed breakdown
            print("\nDetailed model cost breakdown:")
            for model, data in result["model_costs"].items():
                print(
                    f"  {model}: ${data['cost']:.2f} ({data['percentage']:.1f}% of usage)"
                )

            print(f"\nMonthly subscription fee: ${result['monthly_fee']:.2f}")
            print(f"Total cost for token usage: ${result['token_cost']:.2f}")
            print(f"Total monthly cost: ${result['total_monthly_cost']:.2f}")

        else:
            print("Invalid choice.")


if __name__ == "__main__":
    main()
