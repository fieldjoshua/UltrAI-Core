#!/usr/bin/env python3
from pricing_simulator import PricingSimulator


def main():
    # Create pricing simulator instance
    simulator = PricingSimulator()

    print("=== Ultra Framework Pricing Simulator ===\n")

    # Example 1: Calculate cost for a single query
    print("Example 1: Calculate cost for a single query")
    cost_basic = simulator.calculate_token_cost(
        model="gpt-4", token_count=5000, tier="basic"
    )

    # This will fail because gpt-4 is not available in basic tier
    print(f"Basic tier with GPT-4 (5,000 tokens): {cost_basic}\n")

    # Try with a model available in basic tier
    cost_basic_valid = simulator.calculate_token_cost(
        model="gpt-3.5-turbo", token_count=5000, tier="basic"
    )
    print(f"Basic tier with GPT-3.5 Turbo (5,000 tokens): {cost_basic_valid}\n")

    # Example 2: Pro tier with more tokens
    cost_pro = simulator.calculate_token_cost(
        model="claude-3-sonnet",
        token_count=50000,
        tier="pro",
        features=["priority_processing"],
    )
    print(f"Pro tier with Claude 3 Sonnet (50,000 tokens) + priority: {cost_pro}\n")

    # Example 3: Enterprise tier with high volume
    cost_enterprise = simulator.calculate_token_cost(
        model="claude-3-opus",
        token_count=2500000,
        tier="enterprise",
        features=["document_processing", "custom_patterns"],
    )
    print(
        f"Enterprise tier with Claude 3 Opus (2.5M tokens) + features: {cost_enterprise}\n"
    )

    # Example 4: Monthly cost estimation
    print("Example 4: Monthly cost estimation")
    monthly_estimate = simulator.estimate_monthly_cost(
        daily_queries=100,
        avg_tokens_per_query=2000,
        model_distribution={
            "gpt-4": 0.3,
            "claude-3-sonnet": 0.4,
            "mistral-medium": 0.3,
        },
        tier="pro",
        features=["document_processing", "priority_processing"],
    )
    print(f"Monthly cost estimate for Pro tier: {monthly_estimate}\n")

    # Example 5: Generate a pricing simulation with different scenarios
    print("Example 5: Pricing simulation with different scenarios")
    scenarios = [
        {
            "name": "Small Business",
            "daily_queries": 50,
            "avg_tokens_per_query": 1500,
            "model_distribution": {"gpt-3.5-turbo": 0.7, "mistral-small": 0.3},
            "tier": "basic",
            "features": [],
        },
        {
            "name": "Medium Business",
            "daily_queries": 200,
            "avg_tokens_per_query": 3000,
            "model_distribution": {"gpt-4": 0.4, "claude-3-sonnet": 0.6},
            "tier": "pro",
            "features": ["document_processing", "api_access"],
        },
        {
            "name": "Enterprise",
            "daily_queries": 1000,
            "avg_tokens_per_query": 5000,
            "model_distribution": {"claude-3-opus": 0.5, "mistral-large": 0.5},
            "tier": "enterprise",
            "features": [
                "document_processing",
                "api_access",
                "custom_patterns",
                "priority_processing",
            ],
        },
    ]

    simulation_results = simulator.simulate_pricing(
        scenarios, output_dir="pricing_results"
    )
    print(f"Simulation results: {simulation_results['summary']}\n")
    print(
        f"Detailed reports and visualizations saved to: {simulation_results['output_dir']}"
    )


if __name__ == "__main__":
    main()
