#!/usr/bin/env python3
import json
import os
from datetime import datetime


class PricingCalculator:
    """
    A simple pricing calculator for the Ultra Framework that doesn't rely on external libraries
    """

    def __init__(self):
        """Initialize the pricing calculator with default values"""

        # Default pricing model
        self.pricing = {
            # Base costs per 1K tokens for common models (USD)
            "base_costs": {
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
            },
            # Markup percentages for different tiers
            "markup_percentages": {
                "basic": 20,  # 20% markup for basic tier
                "pro": 35,  # 35% markup for pro tier
                "enterprise": 50,  # 50% markup for enterprise tier
            },
            # Tiered pricing model
            "tiers": {
                "basic": {
                    "monthly_fee": 10.00,  # Base monthly subscription fee
                    "included_tokens": 100000,  # Free tokens included per month
                    "model_access": ["gpt-3.5-turbo", "mistral-small", "local"],
                },
                "pro": {
                    "monthly_fee": 30.00,
                    "included_tokens": 500000,
                    "model_access": [
                        "gpt-3.5-turbo",
                        "gpt-4",
                        "claude-3-sonnet",
                        "mistral-medium",
                        "gemini-pro",
                        "local",
                    ],
                },
                "enterprise": {
                    "monthly_fee": 100.00,
                    "included_tokens": 2000000,
                    "model_access": [
                        "gpt-4",
                        "claude-3-opus",
                        "claude-3-sonnet",
                        "mistral-large",
                        "gemini-pro",
                        "local",
                    ],
                },
            },
            # Volume discounts (applied after basic markup)
            "volume_discounts": {
                "1000000": 5,  # 5% discount for >1M tokens
                "5000000": 10,  # 10% discount for >5M tokens
                "10000000": 15,  # 15% discount for >10M tokens
                "50000000": 20,  # 20% discount for >50M tokens
            },
            # Feature pricing (additional costs)
            "feature_costs": {
                "document_processing": 0.001,  # Per page
                "additional_iterations": 0.01,  # Per additional iteration
                "custom_patterns": 5.00,  # Monthly fee for custom patterns
                "api_access": 20.00,  # Monthly fee for API access
                "priority_processing": 0.02,  # Per request
            },
        }

        # Usage history
        self.usage_history = []

    def calculate_cost(self, model, token_count, tier="basic", features=None):
        """
        Calculate the cost for a specific token usage with a model

        Args:
            model: The model used (e.g., "gpt-4", "claude-3-opus")
            token_count: Number of tokens used
            tier: Service tier (basic, pro, enterprise)
            features: List of additional features used

        Returns:
            dict: Detailed cost breakdown
        """
        if features is None:
            features = []

        # Validate inputs
        if model not in self.pricing["base_costs"]:
            model = "gpt-3.5-turbo"  # Default to a standard model

        if tier not in self.pricing["markup_percentages"]:
            tier = "basic"  # Default to basic tier

        # Calculate base cost (per 1000 tokens)
        base_cost_per_1k = self.pricing["base_costs"][model]
        base_cost = (token_count / 1000) * base_cost_per_1k

        # Apply markup based on tier
        markup_percentage = self.pricing["markup_percentages"][tier]
        markup_cost = base_cost * (markup_percentage / 100)

        # Check allowed models for the tier
        tier_models = self.pricing["tiers"][tier]["model_access"]
        if model not in tier_models:
            return {
                "status": "error",
                "message": f"Model {model} is not available in the {tier} tier",
                "allowed_models": tier_models,
                "cost": 0.0,
            }

        # Apply volume discount if applicable
        volume_discount = 0
        for threshold, discount in sorted(
            self.pricing["volume_discounts"].items(), key=lambda x: int(x[0])
        ):
            if token_count > int(threshold):
                volume_discount = discount / 100
                break

        discount_amount = (base_cost + markup_cost) * volume_discount

        # Calculate included tokens
        included_tokens = self.pricing["tiers"][tier]["included_tokens"]
        tokens_charged = max(0, token_count - included_tokens)

        # Recalculate costs with included tokens
        adjusted_base_cost = (tokens_charged / 1000) * base_cost_per_1k
        adjusted_markup_cost = adjusted_base_cost * (markup_percentage / 100)
        adjusted_discount = (
            adjusted_base_cost + adjusted_markup_cost
        ) * volume_discount

        # Add feature costs
        feature_cost = 0
        feature_breakdown = {}

        for feature in features:
            if feature in self.pricing["feature_costs"]:
                feature_price = self.pricing["feature_costs"][feature]
                feature_cost += feature_price
                feature_breakdown[feature] = feature_price

        # Calculate final cost
        subtotal = adjusted_base_cost + adjusted_markup_cost - adjusted_discount
        total_cost = subtotal + feature_cost

        # Round to 4 decimal places
        total_cost = round(total_cost, 4)

        # Record this calculation in usage history
        self.usage_history.append(
            {
                "timestamp": datetime.now().isoformat(),
                "model": model,
                "token_count": token_count,
                "tokens_charged": tokens_charged,
                "tier": tier,
                "features": features,
                "base_cost": adjusted_base_cost,
                "markup_cost": adjusted_markup_cost,
                "discount": adjusted_discount,
                "feature_cost": feature_cost,
                "total_cost": total_cost,
            }
        )

        # Add monthly fee
        monthly_fee = self.pricing["tiers"][tier]["monthly_fee"]

        # Return detailed cost breakdown
        return {
            "status": "success",
            "model": model,
            "token_count": token_count,
            "tokens_charged": tokens_charged,
            "included_tokens": included_tokens,
            "tier": tier,
            "base_cost": round(adjusted_base_cost, 6),
            "markup_percentage": markup_percentage,
            "markup_cost": round(adjusted_markup_cost, 6),
            "volume_discount_percentage": volume_discount * 100,
            "discount_amount": round(adjusted_discount, 6),
            "feature_costs": feature_breakdown,
            "feature_cost_total": round(feature_cost, 6),
            "total_cost": total_cost,
            "monthly_fee": monthly_fee,
            "cost_per_1k_tokens": (
                round(total_cost / (token_count / 1000), 6) if token_count > 0 else 0
            ),
        }

    def estimate_monthly_cost(
        self, daily_queries, avg_tokens, model_distribution, tier="basic", features=None
    ):
        """
        Estimate monthly cost based on usage patterns

        Args:
            daily_queries: Number of queries per day
            avg_tokens: Average number of tokens per query
            model_distribution: Dictionary mapping model names to usage percentages
            tier: Service tier (basic, pro, enterprise)
            features: List of additional features used

        Returns:
            dict: Monthly cost estimate
        """
        if features is None:
            features = []

        # Normalize model distribution
        total_percentage = sum(model_distribution.values())
        if total_percentage != 1.0:
            model_distribution = {
                k: v / total_percentage for k, v in model_distribution.items()
            }

        monthly_days = 30  # Average month length
        monthly_queries = daily_queries * monthly_days
        monthly_tokens = monthly_queries * avg_tokens

        # Calculate cost for each model based on distribution
        model_costs = {}
        total_cost = 0

        for model, percentage in model_distribution.items():
            model_tokens = monthly_tokens * percentage
            cost_result = self.calculate_cost(model, model_tokens, tier, features)

            if cost_result["status"] == "success":
                model_costs[model] = {
                    "tokens": model_tokens,
                    "percentage": percentage * 100,
                    "cost": cost_result["total_cost"],
                }
                total_cost += cost_result["total_cost"]
            else:
                # If model not available in this tier, exclude it
                model_costs[model] = {
                    "tokens": model_tokens,
                    "percentage": percentage * 100,
                    "cost": 0,
                    "error": cost_result["message"],
                }

        # Add monthly subscription fee
        monthly_fee = self.pricing["tiers"][tier]["monthly_fee"]
        total_cost_with_fee = total_cost + monthly_fee

        return {
            "daily_queries": daily_queries,
            "monthly_queries": monthly_queries,
            "avg_tokens_per_query": avg_tokens,
            "total_monthly_tokens": monthly_tokens,
            "tier": tier,
            "monthly_fee": monthly_fee,
            "model_costs": model_costs,
            "token_cost": total_cost,
            "total_monthly_cost": total_cost_with_fee,
            "features": features,
        }

    def simulate_pricing(self, scenarios):
        """
        Simulate pricing across different scenarios

        Args:
            scenarios: List of scenario dictionaries

        Returns:
            dict: Simulation results
        """
        results = {"scenarios": {}, "summary": {}}
        total_cost = 0

        for scenario in scenarios:
            name = scenario.get("name", "Unnamed")
            daily_queries = scenario.get("daily_queries", 10)
            avg_tokens = scenario.get("avg_tokens_per_query", 1000)
            models = scenario.get("model_distribution", {"gpt-3.5-turbo": 1.0})
            tier = scenario.get("tier", "basic")
            features = scenario.get("features", [])

            monthly_cost = self.estimate_monthly_cost(
                daily_queries, avg_tokens, models, tier, features
            )

            results["scenarios"][name] = monthly_cost
            total_cost += monthly_cost.get("total_monthly_cost", 0)

        results["summary"] = {
            "total_monthly_cost": total_cost,
            "scenario_count": len(scenarios),
            "timestamp": datetime.now().isoformat(),
        }

        return results


def main():
    # Create pricing calculator
    calculator = PricingCalculator()

    print("=== Ultra Framework Pricing Calculator ===\n")

    # Example 1: Calculate cost for a single query
    print("Example 1: Calculate cost for a single query")
    cost_basic = calculator.calculate_cost(
        model="gpt-4", token_count=5000, tier="basic"
    )

    # This will fail because gpt-4 is not available in basic tier
    print(f"Basic tier with GPT-4 (5,000 tokens):")
    print(json.dumps(cost_basic, indent=2))
    print()

    # Try with a model available in basic tier
    cost_basic_valid = calculator.calculate_cost(
        model="gpt-3.5-turbo", token_count=5000, tier="basic"
    )
    print(f"Basic tier with GPT-3.5 Turbo (5,000 tokens):")
    print(json.dumps(cost_basic_valid, indent=2))
    print()

    # Example 2: Pro tier with more tokens
    cost_pro = calculator.calculate_cost(
        model="claude-3-sonnet",
        token_count=50000,
        tier="pro",
        features=["priority_processing"],
    )
    print(f"Pro tier with Claude 3 Sonnet (50,000 tokens) + priority:")
    print(json.dumps(cost_pro, indent=2))
    print()

    # Example 3: Enterprise tier with high volume
    cost_enterprise = calculator.calculate_cost(
        model="claude-3-opus",
        token_count=2500000,
        tier="enterprise",
        features=["document_processing", "custom_patterns"],
    )
    print(f"Enterprise tier with Claude 3 Opus (2.5M tokens) + features:")
    print(json.dumps(cost_enterprise, indent=2))
    print()

    # Example 4: Monthly cost estimation
    print("Example 4: Monthly cost estimation")
    monthly_estimate = calculator.estimate_monthly_cost(
        daily_queries=100,
        avg_tokens=2000,
        model_distribution={
            "gpt-4": 0.3,
            "claude-3-sonnet": 0.4,
            "mistral-medium": 0.3,
        },
        tier="pro",
        features=["document_processing", "priority_processing"],
    )
    print(f"Monthly cost estimate for Pro tier:")
    print(json.dumps(monthly_estimate, indent=2))
    print()

    # Example 5: Pricing simulation
    print("Example 5: Pricing simulation across different scenarios")
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

    simulation_results = calculator.simulate_pricing(scenarios)
    print(f"Simulation results:")
    print(json.dumps(simulation_results, indent=2))


if __name__ == "__main__":
    main()
