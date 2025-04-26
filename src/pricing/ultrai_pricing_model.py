#!/usr/bin/env python3
"""
UltrAI Pricing Model Calculator

This script provides a simplified analysis of UltrAI's business model, where:
1. UltrAI purchases tokens at enterprise-level costs
2. UltrAI offers users pay-as-you-go access with markup pricing
3. Users receive benefits from token optimization and reserve accounts

The calculator helps determine optimal token pricing, markups, and discount structures.
"""

import json
from datetime import datetime


class UltrAIPricingModel:
    """A simplified model for UltrAI's pay-as-you-go pricing strategy"""

    def __init__(self):
        # Enterprise costs for various models ($ per 1K tokens)
        self.base_costs = {
            "claude-3-opus": 0.015,  # Anthropic Claude 3 Opus
            "claude-3-sonnet": 0.008,  # Anthropic Claude 3 Sonnet
            "gpt-4": 0.03,  # OpenAI GPT-4
            "gpt-3.5-turbo": 0.001,  # OpenAI GPT-3.5 Turbo
            "mistral-large": 0.008,  # Mistral Large
            "mistral-medium": 0.002,  # Mistral Medium
            "mistral-small": 0.0006,  # Mistral Small
            "gemini-pro": 0.0005,  # Google Gemini Pro
            "llama-70b": 0.0001,  # Meta Llama 70B (self-hosted)
            "local": 0.00005,  # Local models (estimated electricity/compute cost)
        }

        # Token efficiency for each model (lower is better)
        self.token_efficiency = {
            "gpt-3.5-turbo": 1.5,  # Baseline 1.0, GPT-3.5 needs 1.5x tokens for equivalent quality
            "gpt-4": 0.8,  # GPT-4 needs 0.8x tokens (more efficient)
            "claude-3-sonnet": 0.9,  # Claude 3 Sonnet is efficient
            "claude-3-opus": 0.7,  # Claude 3 Opus is most efficient
            "mistral-large": 0.85,  # Mistral large is very efficient
            "mistral-medium": 1.1,  # Mistral medium is moderately efficient
            "mistral-small": 1.3,  # Mistral small is less efficient
            "gemini-pro": 1.0,  # Gemini pro is the baseline reference
            "llama-70b": 1.0,  # Llama is similar to Gemini
            "local": 1.8,  # Local models need more tokens for equivalent quality
        }

        # Default markup percentages to test
        self.markup_percentages = [10, 15, 20, 25, 30]

        # Reserve account discounts (reserve amount: discount percentage)
        self.reserve_discounts = {
            10000: 2,  # $10 reserve gets 2% discount
            50000: 5,  # $50 reserve gets 5% discount
            100000: 8,  # $100 reserve gets 8% discount
            500000: 12,  # $500 reserve gets 12% discount
            1000000: 15,  # $1000+ reserve gets 15% discount
        }

    def calculate_effective_cost(
        self, model, tokens, markup_percentage=15, reserve_amount=0
    ):
        """
        Calculate the effective cost of tokens with markup and discounts

        Args:
            model: The LLM model to use
            tokens: Number of tokens
            markup_percentage: UltrAI's markup percentage over enterprise costs
            reserve_amount: User's reserve account amount for discount calculation

        Returns:
            dict: Cost analysis
        """
        # Get base costs
        base_cost_per_1k = self.base_costs.get(
            model, 0.001
        )  # Default to GPT-3.5 if model not found
        base_cost = (tokens / 1000) * base_cost_per_1k

        # Apply markup
        marked_up_cost = base_cost * (1 + markup_percentage / 100)

        # Calculate any reserve discount
        discount_percentage = 0
        for amount, discount in sorted(self.reserve_discounts.items()):
            if reserve_amount >= amount:
                discount_percentage = discount

        # Apply reserve discount
        final_cost = marked_up_cost * (1 - discount_percentage / 100)

        # Calculate profit
        profit = final_cost - base_cost
        profit_margin = (profit / final_cost) * 100 if final_cost > 0 else 0

        # Calculate effective cost considering token efficiency
        efficiency_factor = self.token_efficiency.get(model, 1.0)
        effective_cost = final_cost * efficiency_factor
        effective_cost_per_1k = (effective_cost / tokens) * 1000 if tokens > 0 else 0

        return {
            "model": model,
            "tokens": tokens,
            "base_cost_per_1k": base_cost_per_1k,
            "base_cost_total": base_cost,
            "markup_percentage": markup_percentage,
            "marked_up_cost": marked_up_cost,
            "reserve_amount": reserve_amount,
            "discount_percentage": discount_percentage,
            "final_cost": final_cost,
            "final_cost_per_1k": (final_cost / tokens) * 1000 if tokens > 0 else 0,
            "profit": profit,
            "profit_margin": profit_margin,
            "efficiency_factor": efficiency_factor,
            "effective_cost": effective_cost,
            "effective_cost_per_1k": effective_cost_per_1k,
            "enterprise_savings": self.calculate_enterprise_savings(
                model, tokens, markup_percentage
            ),
        }

    def calculate_enterprise_savings(self, model, tokens, markup_percentage):
        """Calculate how much a customer saves vs direct enterprise API access"""
        # Calculate what it would cost for the customer to access the API directly
        direct_api_cost = None

        if model == "claude-3-opus":
            # Claude 3 Opus is expensive for direct users
            direct_api_cost = (tokens / 1000) * 0.03  # Higher direct API cost
        elif model == "claude-3-sonnet":
            direct_api_cost = (tokens / 1000) * 0.015
        elif model == "gpt-4":
            direct_api_cost = (tokens / 1000) * 0.06
        elif model == "gpt-3.5-turbo":
            direct_api_cost = (tokens / 1000) * 0.002
        elif "mistral" in model:
            direct_api_cost = (tokens / 1000) * (
                self.base_costs[model] * 1.8
            )  # Mistral has higher direct costs
        else:
            # For other models, assume 80% more expensive for direct access
            direct_api_cost = (tokens / 1000) * (self.base_costs[model] * 1.8)

        # Calculate cost through UltrAI
        ultrai_cost = (
            (tokens / 1000) * self.base_costs[model] * (1 + markup_percentage / 100)
        )

        # Calculate savings
        savings = direct_api_cost - ultrai_cost if direct_api_cost else 0
        savings_percentage = (
            (savings / direct_api_cost) * 100
            if direct_api_cost and direct_api_cost > 0
            else 0
        )

        return {
            "direct_api_cost": direct_api_cost,
            "ultrai_cost": ultrai_cost,
            "savings": savings,
            "savings_percentage": savings_percentage,
        }

    def find_optimal_markup(
        self, models=None, token_amounts=None, min_profit_margin=10
    ):
        """
        Find the optimal markup for different models and token amounts

        Args:
            models: List of models to analyze (None for all)
            token_amounts: List of token amounts to test
            min_profit_margin: Minimum acceptable profit margin

        Returns:
            dict: Optimal markups for different scenarios
        """
        if models is None:
            models = list(self.base_costs.keys())

        if token_amounts is None:
            token_amounts = [1000, 10000, 100000, 1000000]

        results = {
            "models": {},
            "summary": {"optimal_markups": {}, "best_models": {}, "reserve_impact": {}},
        }

        # Analyze each model
        for model in models:
            results["models"][model] = {}

            for tokens in token_amounts:
                results["models"][model][tokens] = {}

                for markup in self.markup_percentages:
                    # Calculate with no reserve
                    base_analysis = self.calculate_effective_cost(
                        model=model,
                        tokens=tokens,
                        markup_percentage=markup,
                        reserve_amount=0,
                    )

                    # Skip if profit margin is below minimum
                    if base_analysis["profit_margin"] < min_profit_margin:
                        continue

                    results["models"][model][tokens][markup] = {
                        "base": base_analysis,
                        "with_reserve": {},
                    }

                    # Calculate with different reserve amounts
                    for reserve, discount in self.reserve_discounts.items():
                        reserve_analysis = self.calculate_effective_cost(
                            model=model,
                            tokens=tokens,
                            markup_percentage=markup,
                            reserve_amount=reserve,
                        )

                        results["models"][model][tokens][markup]["with_reserve"][
                            reserve
                        ] = reserve_analysis

        # Find the optimal markup for each model that maintains profit margin
        optimal_markups = {}
        for model in models:
            valid_markups = []

            for tokens in token_amounts:
                if tokens in results["models"][model]:
                    for markup in sorted(results["models"][model][tokens].keys()):
                        analysis = results["models"][model][tokens][markup]["base"]
                        if analysis["profit_margin"] >= min_profit_margin:
                            valid_markups.append((markup, analysis["profit_margin"]))

            if valid_markups:
                # Find lowest markup that meets min profit margin
                optimal_markups[model] = sorted(valid_markups)[0][0]
            else:
                optimal_markups[model] = None

        results["summary"]["optimal_markups"] = optimal_markups

        # Find best models for different token volumes
        best_models = {}
        for tokens in token_amounts:
            best_model = None
            best_price = float("inf")

            for model in models:
                if tokens in results["models"][model]:
                    for markup in results["models"][model][tokens]:
                        analysis = results["models"][model][tokens][markup]["base"]
                        if (
                            analysis["effective_cost_per_1k"] < best_price
                            and analysis["profit_margin"] >= min_profit_margin
                        ):
                            best_price = analysis["effective_cost_per_1k"]
                            best_model = model

            best_models[tokens] = best_model

        results["summary"]["best_models"] = best_models

        # Analyze reserve account impact
        reserve_impact = {}
        for reserve in self.reserve_discounts:
            avg_savings = 0
            count = 0

            for model in models:
                for tokens in token_amounts:
                    for markup in self.markup_percentages:
                        if (
                            tokens in results["models"][model]
                            and markup in results["models"][model][tokens]
                            and reserve
                            in results["models"][model][tokens][markup]["with_reserve"]
                        ):
                            base_cost = results["models"][model][tokens][markup][
                                "base"
                            ]["final_cost"]
                            reserve_cost = results["models"][model][tokens][markup][
                                "with_reserve"
                            ][reserve]["final_cost"]

                            if base_cost > 0:
                                savings_pct = (
                                    (base_cost - reserve_cost) / base_cost * 100
                                )
                                avg_savings += savings_pct
                                count += 1

            if count > 0:
                reserve_impact[reserve] = avg_savings / count
            else:
                reserve_impact[reserve] = 0

        results["summary"]["reserve_impact"] = reserve_impact

        return results

    def generate_pricing_recommendations(self, min_profit_margin=15):
        """
        Generate pricing recommendations based on analysis

        Args:
            min_profit_margin: Minimum profit margin to maintain

        Returns:
            dict: Pricing recommendations
        """
        # Run analysis
        analysis = self.find_optimal_markup(min_profit_margin=min_profit_margin)

        # Generate tiered pricing recommendations
        standard_tier_models = ["gpt-3.5-turbo", "mistral-small", "local"]
        premium_tier_models = ["claude-3-sonnet", "mistral-medium", "gpt-4"]
        enterprise_tier_models = ["claude-3-opus", "mistral-large"]

        # Find the lowest viable markup for each tier
        standard_markups = [
            analysis["summary"]["optimal_markups"].get(m)
            for m in standard_tier_models
            if analysis["summary"]["optimal_markups"].get(m)
        ]
        premium_markups = [
            analysis["summary"]["optimal_markups"].get(m)
            for m in premium_tier_models
            if analysis["summary"]["optimal_markups"].get(m)
        ]
        enterprise_markups = [
            analysis["summary"]["optimal_markups"].get(m)
            for m in enterprise_tier_models
            if analysis["summary"]["optimal_markups"].get(m)
        ]

        # Use default markups if no viable ones were found
        standard_markup = min(standard_markups) if standard_markups else 15
        premium_markup = min(premium_markups) if premium_markups else 20
        enterprise_markup = min(enterprise_markups) if enterprise_markups else 25

        # Find optimal reserve amounts
        reserve_impact = analysis["summary"]["reserve_impact"]
        optimal_reserve = (
            max(
                reserve_impact.items(),
                key=lambda x: x[1] / self.reserve_discounts[x[0]],
            )[0]
            if reserve_impact
            else 10000
        )

        # Generate recommendations
        recommendations = {
            "pricing_tiers": {
                "standard": {
                    "models": standard_tier_models,
                    "markup_percentage": standard_markup,
                    "target_audience": "Individual users and small teams",
                    "positioning": "Affordable access to quality AI",
                    "sample_pricing": {},
                },
                "premium": {
                    "models": premium_tier_models,
                    "markup_percentage": premium_markup,
                    "target_audience": "Professionals and medium-sized businesses",
                    "positioning": "High-quality AI with excellent performance",
                    "sample_pricing": {},
                },
                "enterprise": {
                    "models": enterprise_tier_models,
                    "markup_percentage": enterprise_markup,
                    "target_audience": "Large organizations with high-volume needs",
                    "positioning": "Top-tier AI for mission-critical applications",
                    "sample_pricing": {},
                },
            },
            "reserve_accounts": {
                "optimal_entry_point": optimal_reserve,
                "discount_structure": self.reserve_discounts,
                "breakeven_calculations": {
                    amount: {
                        "amount": amount,
                        "discount": discount,
                        "breakeven_queries": (
                            amount / (amount * discount / 100)
                            if discount > 0
                            else float("inf")
                        ),
                    }
                    for amount, discount in self.reserve_discounts.items()
                },
            },
            "model_recommendations": {
                "efficiency_leaders": sorted(
                    [(m, f) for m, f in self.token_efficiency.items() if f < 1.0],
                    key=lambda x: x[1],
                )[:3],
                "cost_effectiveness_leaders": sorted(
                    [(m, c) for m, c in self.base_costs.items()],
                    key=lambda x: x[1] * self.token_efficiency.get(x[0], 1.0),
                )[:3],
                "best_models_by_volume": analysis["summary"]["best_models"],
            },
            "marketing_messaging": {
                "value_proposition": "Enterprise-grade AI at affordable prices with pay-as-you-go flexibility",
                "key_differentiators": [
                    "Token efficiency optimization saves money",
                    "Reserve account discounts for predictable pricing",
                    "No technical overhead or API management",
                    "Access to premium models with enterprise features",
                ],
                "customer_benefits": [
                    f"Save up to {max(reserve_impact.values()):.1f}% with reserve accounts",
                    "Pay only for what you use",
                    "Access multiple AI models through one interface",
                    "Predictable pricing without fluctuations",
                ],
            },
        }

        # Add sample pricing for each tier
        for tier_name, tier_info in recommendations["pricing_tiers"].items():
            for model in tier_info["models"][
                :2
            ]:  # Just use first two models for examples
                for tokens in [1000, 10000, 100000]:
                    analysis = self.calculate_effective_cost(
                        model=model,
                        tokens=tokens,
                        markup_percentage=tier_info["markup_percentage"],
                    )

                    key = f"{model}_{tokens}"
                    tier_info["sample_pricing"][key] = {
                        "model": model,
                        "tokens": tokens,
                        "cost": analysis["final_cost"],
                        "cost_per_1k": analysis["final_cost_per_1k"],
                        "effective_cost_per_1k": analysis["effective_cost_per_1k"],
                        "savings_vs_direct": analysis["enterprise_savings"][
                            "savings_percentage"
                        ],
                    }

        return recommendations

    def print_recommendations(self, recommendations=None):
        """Print pricing recommendations in a readable format"""
        if recommendations is None:
            recommendations = self.generate_pricing_recommendations()

        print("\n=== UltrAI Pricing Recommendations ===")

        # Print pricing tiers
        print("\n-- Recommended Pricing Tiers --")
        for tier_name, tier_info in recommendations["pricing_tiers"].items():
            print(f"\n{tier_name.upper()} TIER:")
            print(f"  Markup: {tier_info['markup_percentage']}%")
            print(f"  Models: {', '.join(tier_info['models'])}")
            print(f"  Target: {tier_info['target_audience']}")
            print(f"  Positioning: {tier_info['positioning']}")

            print("  Sample Pricing:")
            for key, pricing in tier_info["sample_pricing"].items():
                print(
                    f"    • {pricing['model']} ({pricing['tokens']:,} tokens): ${pricing['cost']:.4f} "
                    + f"(${pricing['cost_per_1k']:.4f}/1K, effective: ${pricing['effective_cost_per_1k']:.4f}/1K)"
                )
                if pricing["savings_vs_direct"] > 0:
                    print(
                        f"      Saves {pricing['savings_vs_direct']:.1f}% vs. direct API access"
                    )

        # Print reserve account recommendations
        print("\n-- Reserve Account Recommendations --")
        print(
            f"Optimal entry point: ${recommendations['reserve_accounts']['optimal_entry_point']:,}"
        )

        print("\nDiscount structure:")
        for amount, discount in recommendations["reserve_accounts"][
            "discount_structure"
        ].items():
            breakeven = recommendations["reserve_accounts"]["breakeven_calculations"][
                amount
            ]["breakeven_queries"]
            print(
                f"  ${amount:,}: {discount}% discount (breakeven at {breakeven:.0f} queries)"
            )

        # Print model recommendations
        print("\n-- Model Recommendations --")

        print("\nEfficiency leaders (fewest tokens for equivalent quality):")
        for model, factor in recommendations["model_recommendations"][
            "efficiency_leaders"
        ]:
            print(f"  • {model}: {factor:.2f}x tokens needed (lower is better)")

        print("\nCost-effectiveness leaders:")
        for model, cost in recommendations["model_recommendations"][
            "cost_effectiveness_leaders"
        ]:
            efficiency = self.token_efficiency.get(model, 1.0)
            print(f"  • {model}: ${cost:.6f}/1K tokens (efficiency: {efficiency:.2f}x)")

        print("\nBest models by token volume:")
        for tokens, model in recommendations["model_recommendations"][
            "best_models_by_volume"
        ].items():
            if model:
                print(f"  • {tokens:,} tokens: {model}")

        # Print marketing messaging
        print("\n-- Marketing Messaging --")
        print(
            f"Value proposition: {recommendations['marketing_messaging']['value_proposition']}"
        )

        print("\nKey differentiators:")
        for point in recommendations["marketing_messaging"]["key_differentiators"]:
            print(f"  • {point}")

        print("\nCustomer benefits:")
        for benefit in recommendations["marketing_messaging"]["customer_benefits"]:
            print(f"  • {benefit}")


def main():
    """Run the UltrAI pricing model analysis"""
    print("=== UltrAI Pay-as-you-go Pricing Model ===")
    print("Analyzing optimal pricing strategy for UltrAI's token service...")

    model = UltrAIPricingModel()
    recommendations = model.generate_pricing_recommendations(min_profit_margin=15)
    model.print_recommendations(recommendations)

    # Save recommendations to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"ultrai_pricing_recommendations_{timestamp}.json"

    try:
        with open(filename, "w") as f:
            json.dump(recommendations, f, indent=2)
        print(f"\nDetailed recommendations saved to: {filename}")
    except Exception as e:
        print(f"\nError saving recommendations: {e}")


if __name__ == "__main__":
    main()
