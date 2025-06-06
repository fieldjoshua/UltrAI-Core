#!/usr/bin/env python3
import json
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("ultra_pricing")

BASELINE_MODEL_PRICING = {
    # OpenAI GPT-4 variants
    "gpt-4-8k": {"input": 0.03, "output": 0.06, "context": 8000},
    "gpt-4-32k": {"input": 0.06, "output": 0.12, "context": 32000},
    "gpt-4.5-128k": {"input": 0.075, "output": 0.15, "context": 128000},
    "gpt-4-turbo": {"input": 0.01, "output": 0.03, "context": 128000},
    "gpt-4o": {"input": 0.005, "output": 0.015, "context": 128000},
    "gpt-4o-mini": {"input": 0.00015, "output": 0.00060, "context": 128000},
    "gpt-3.5-4k": {"input": 0.0015, "output": 0.002, "context": 4000},
    "gpt-3.5-16k": {"input": 0.0005, "output": 0.0015, "context": 16000},
    # Anthropic Claude variants
    "claude-instant": {"input": 0.0008, "output": 0.0024, "context": 9000},
    "claude-2-100k": {"input": 0.008, "output": 0.024, "context": 100000},
    "claude-3.5-sonnet": {"input": 0.003, "output": 0.015, "context": 128000},
    "claude-3-opus": {"input": 0.015, "output": 0.075, "context": 128000},
    # Google models
    "gemini-1.0-pro": {"input": 0.0005, "output": 0.0015, "context": 128000},
    "gemini-1.5-pro": {"input": 0.0035, "output": 0.0105, "context": 128000},
    "gemini-2.0-flash": {"input": 0.0001, "output": 0.0004, "context": 1000000},
    # Our UI mappings
    "chatgpt": {"input": 0.01, "output": 0.03, "context": 128000},  # GPT-4 Turbo
    "claude": {"input": 0.003, "output": 0.015, "context": 128000},  # Claude 3.5 Sonnet
    "gemini": {"input": 0.0035, "output": 0.0105, "context": 128000},  # Gemini 1.5 Pro
    "llama": {"input": 0.0001, "output": 0.0004, "context": 128000},  # Lowest tier
}


class PricingSimulator:
    def __init__(self, config_path=None):
        # Default model pricing based on 2025 pricing data
        self.model_pricing = {
            # OpenAI models
            "gpt4o": {
                "input_cost_per_1k": 0.0025,
                "output_cost_per_1k": 0.01,
                "total_cost_per_1k": 0.0125,
                "context_window": 128000,
                "is_thinking_model": True,
            },
            "gpt4o_mini": {
                "input_cost_per_1k": 0.00015,
                "output_cost_per_1k": 0.00060,
                "total_cost_per_1k": 0.00075,
                "context_window": 128000,
                "is_thinking_model": False,
            },
            "gpt4_turbo": {
                "input_cost_per_1k": 0.01,
                "output_cost_per_1k": 0.03,
                "total_cost_per_1k": 0.04,
                "context_window": 128000,
                "is_thinking_model": True,
            },
            "gpt35_turbo": {
                "input_cost_per_1k": 0.0005,
                "output_cost_per_1k": 0.0015,
                "total_cost_per_1k": 0.0020,
                "context_window": 4000,
                "is_thinking_model": False,
            },
            # Anthropic models
            "claude37": {
                "input_cost_per_1k": 0.003,
                "output_cost_per_1k": 0.015,
                "total_cost_per_1k": 0.018,
                "context_window": 200000,
                "is_thinking_model": True,
            },
            "claude3_opus": {
                "input_cost_per_1k": 0.015,
                "output_cost_per_1k": 0.075,
                "total_cost_per_1k": 0.090,
                "context_window": 200000,
                "is_thinking_model": True,
            },
            "claude35_haiku": {
                "input_cost_per_1k": 0.0008,
                "output_cost_per_1k": 0.0040,
                "total_cost_per_1k": 0.0048,
                "context_window": 200000,
                "is_thinking_model": False,
            },
            # Google models
            "gemini15": {
                "input_cost_per_1k": 0.000075,
                "output_cost_per_1k": 0.000300,
                "total_cost_per_1k": 0.000375,
                "context_window": 128000,
                "is_thinking_model": False,
            },
            "gemini25_pro_max": {
                "input_cost_per_1k": 0.003,
                "output_cost_per_1k": 0.015,
                "total_cost_per_1k": 0.018,
                "context_window": 1000000,
                "is_thinking_model": True,
            },
            # Local models
            "llama3": {
                "input_cost_per_1k": 0.0,
                "output_cost_per_1k": 0.0,
                "total_cost_per_1k": 0.0,
                "context_window": 8192,
                "is_thinking_model": False,
            },
            "mistral": {
                "input_cost_per_1k": 0.0,
                "output_cost_per_1k": 0.0,
                "total_cost_per_1k": 0.0,
                "context_window": 8192,
                "is_thinking_model": False,
            },
        }

        # Pricing tiers with percentage markup
        self.pricing_tiers = {
            "basic": {
                "markup_percentage": 20,  # 20% markup
                "minimum_charge": 0.01,  # Minimum $0.01 per query
                "thinking_model_surcharge": 5,  # Additional 5% for thinking models
            },
            "pro": {
                "markup_percentage": 15,  # 15% markup
                "minimum_charge": 0.005,  # Minimum $0.005 per query
                "thinking_model_surcharge": 3,  # Additional 3% for thinking models
            },
            "enterprise": {
                "markup_percentage": 10,  # 10% markup
                "minimum_charge": 0.00,  # No minimum charge
                "thinking_model_surcharge": 0,  # No additional charge for thinking models
            },
        }

        # Volume discounts - amount to subtract from markup percentage
        self.volume_discounts = {
            1000: 0,  # No discount for under 1000 queries
            10000: 2,  # 2% discount for 1000-10000 queries
            100000: 5,  # 5% discount for 10000-100000 queries
            1000000: 10,  # 10% discount for over 100000 queries
        }

        # Feature costs (add-ons)
        self.feature_costs = {
            "private": 0.05,  # $0.05 for private data processing
            "anti_ai_detect": 0.05,  # $0.05 for AI detection prevention
            "citation": 0.05,  # $0.05 for including citations
            "express": 0.03,  # $0.03 for express processing
        }

        # Usage tracking
        self.usage_history = []

        # Load configuration from file if provided
        if config_path:
            self.load_config(config_path)

        # Could store usage or other config here
        self.model_configs = BASELINE_MODEL_PRICING

    def load_config(self, config_path: str) -> None:
        """Load pricing configuration from file if it exists"""
        if os.path.exists(config_path):
            try:
                with open(config_path, "r") as f:
                    config = json.load(f)
                    # Update only the keys that exist in the config file
                    for key, value in config.items():
                        if key in self.model_pricing:
                            self.model_pricing[key] = value
                logger.info(f"Loaded pricing configuration from {config_path}")
            except Exception as e:
                logger.error(f"Error loading pricing configuration: {e}")
        else:
            # Save the default configuration
            self.save_config()

    def save_config(self) -> None:
        """Save current pricing configuration to file"""
        try:
            with open("pricing_config.json", "w") as f:
                json.dump(self.model_pricing, f, indent=2)
            logger.info(f"Pricing configuration saved to pricing_config.json")
        except Exception as e:
            logger.error(f"Error saving pricing configuration: {e}")

    def update_pricing(self, pricing_data: Dict[str, Any]) -> bool:
        """
        Update pricing configuration

        Args:
            pricing_data: Dictionary containing pricing configuration updates

        Returns:
            bool: True if pricing was updated successfully
        """
        try:
            for key, value in pricing_data.items():
                if key in self.model_pricing:
                    self.model_pricing[key] = value
            self.save_config()
            return True
        except Exception as e:
            logger.error(f"Error updating pricing: {e}")
            return False

    def calculate_token_cost(
        self,
        model_id,
        input_tokens,
        output_tokens,
        tier="basic",
        features=None,
        apply_markup=True,
    ):
        """
        Calculate the cost for token usage

        Args:
            model_id (str): The model identifier
            input_tokens (int): Number of input tokens
            output_tokens (int): Number of output tokens
            tier (str): Pricing tier (basic, pro, enterprise)
            features (list): List of add-on features
            apply_markup (bool): Whether to apply markup percentage

        Returns:
            dict: Cost breakdown
        """
        if model_id not in self.model_pricing:
            raise ValueError(f"Unknown model: {model_id}")

        # Get base costs from pricing data
        pricing = self.model_pricing[model_id]

        # Calculate raw token costs
        input_cost = (input_tokens / 1000) * pricing["input_cost_per_1k"]
        output_cost = (output_tokens / 1000) * pricing["output_cost_per_1k"]
        total_raw_cost = input_cost + output_cost

        # Initialize cost breakdown
        cost_breakdown = {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "input_cost": input_cost,
            "output_cost": output_cost,
            "raw_cost": total_raw_cost,
            "features_cost": 0,
            "thinking_model_surcharge": 0,
            "markup_cost": 0,
            "total_cost": total_raw_cost,
        }

        # Add feature costs
        if features:
            feature_cost = 0
            for feature in features:
                if feature in self.feature_costs:
                    feature_cost += self.feature_costs[feature]
            cost_breakdown["features_cost"] = feature_cost
            cost_breakdown["total_cost"] += feature_cost

        # Apply markup if specified
        if apply_markup and tier in self.pricing_tiers:
            # Get markup percentage
            markup_pct = self.pricing_tiers[tier]["markup_percentage"]

            # Calculate markup amount
            markup_amount = (total_raw_cost * markup_pct) / 100
            cost_breakdown["markup_cost"] = markup_amount
            cost_breakdown["total_cost"] += markup_amount

            # Add thinking model surcharge if applicable
            if pricing.get("is_thinking_model", False):
                thinking_surcharge_pct = self.pricing_tiers[tier][
                    "thinking_model_surcharge"
                ]
                thinking_surcharge = (total_raw_cost * thinking_surcharge_pct) / 100
                cost_breakdown["thinking_model_surcharge"] = thinking_surcharge
                cost_breakdown["total_cost"] += thinking_surcharge

            # Apply minimum charge if needed
            min_charge = self.pricing_tiers[tier]["minimum_charge"]
            if cost_breakdown["total_cost"] < min_charge and total_raw_cost > 0:
                cost_breakdown["total_cost"] = min_charge

        # Track usage for reporting
        self._track_usage(
            model_id, input_tokens, output_tokens, cost_breakdown["total_cost"]
        )

        return cost_breakdown

    def estimate_monthly_cost(
        self,
        daily_queries: int,
        avg_tokens_per_query: int,
        model_distribution: Dict[str, float],
        tier: str = "basic",
        features: List[str] = None,
    ) -> Dict[str, Any]:
        """
        Estimate monthly costs based on usage patterns

        Args:
            daily_queries: Average number of queries per day
            avg_tokens_per_query: Average tokens per query
            model_distribution: Distribution of models used (e.g., {"gpt-4": 0.3, "claude-3-sonnet": 0.7})
            tier: Service tier
            features: List of additional features used

        Returns:
            dict: Monthly cost estimate with breakdown
        """
        if features is None:
            features = []

        # Calculate monthly queries and tokens
        monthly_queries = daily_queries * 30
        monthly_tokens = monthly_queries * avg_tokens_per_query

        # Calculate base subscription cost
        monthly_subscription = self.model_pricing["tiers"][tier]["monthly_fee"]

        # Calculate model usage costs
        model_costs = {}
        total_model_cost = 0

        for model, percentage in model_distribution.items():
            # Check if model is available in this tier
            if model not in self.model_pricing["tiers"][tier]["model_access"]:
                continue

            model_token_count = monthly_tokens * percentage
            cost_result = self.calculate_token_cost(model, model_token_count, tier)

            if cost_result["status"] == "success":
                model_costs[model] = {
                    "percentage": percentage * 100,
                    "tokens": model_token_count,
                    "cost": cost_result["total_cost"],
                }
                total_model_cost += cost_result["total_cost"]

        # Calculate feature costs
        feature_costs = {}
        total_feature_cost = 0

        for feature in features:
            if feature in self.feature_costs:
                if feature in ["custom_patterns", "api_access"]:
                    # These are monthly fixed costs
                    feature_costs[feature] = self.feature_costs[feature]
                    total_feature_cost += self.feature_costs[feature]
                elif feature == "document_processing":
                    # Assume 5 pages per query on average
                    pages = monthly_queries * 5
                    cost = pages * self.feature_costs[feature]
                    feature_costs[feature] = cost
                    total_feature_cost += cost
                elif feature == "additional_iterations":
                    # Assume 2 additional iterations per query on average
                    iterations = monthly_queries * 2
                    cost = iterations * self.feature_costs[feature]
                    feature_costs[feature] = cost
                    total_feature_cost += cost
                elif feature == "priority_processing":
                    # Assume 30% of queries are priority
                    priority_queries = monthly_queries * 0.3
                    cost = priority_queries * self.feature_costs[feature]
                    feature_costs[feature] = cost
                    total_feature_cost += cost

        # Calculate total cost
        total_cost = monthly_subscription + total_model_cost + total_feature_cost

        return {
            "daily_queries": daily_queries,
            "monthly_queries": monthly_queries,
            "avg_tokens_per_query": avg_tokens_per_query,
            "monthly_tokens": monthly_tokens,
            "tier": tier,
            "monthly_subscription": monthly_subscription,
            "model_costs": model_costs,
            "total_model_cost": total_model_cost,
            "feature_costs": feature_costs,
            "total_feature_cost": total_feature_cost,
            "total_monthly_cost": total_cost,
            "cost_per_query": (
                total_cost / monthly_queries if monthly_queries > 0 else 0
            ),
        }

    def generate_usage_report(
        self, output_dir: str = "pricing_reports"
    ) -> Dict[str, Any]:
        """
        Generate a usage and cost report based on recorded history

        Args:
            output_dir: Directory to save reports and visualizations

        Returns:
            dict: Usage report summary
        """
        if not self.usage_history:
            return {"status": "error", "message": "No usage history available"}

        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Convert usage history to DataFrame for analysis
        df = pd.DataFrame(self.usage_history)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df["date"] = df["timestamp"].dt.date

        # Aggregate daily usage
        daily_usage = (
            df.groupby("date")
            .agg({"token_count": "sum", "total_cost": "sum"})
            .reset_index()
        )

        # Model usage breakdown
        model_usage = (
            df.groupby("model")
            .agg({"token_count": "sum", "total_cost": "sum", "timestamp": "count"})
            .reset_index()
        )
        model_usage = model_usage.rename(columns={"timestamp": "query_count"})

        # Feature usage
        feature_usage = {}
        for row in df.iterrows():
            for feature in row[1]["features"]:
                if feature not in feature_usage:
                    feature_usage[feature] = 0
                feature_usage[feature] += 1

        # Generate visualizations
        self._create_usage_visualizations(
            df, daily_usage, model_usage, feature_usage, output_dir
        )

        # Save detailed usage data
        df.to_csv(f"{output_dir}/detailed_usage.csv", index=False)
        daily_usage.to_csv(f"{output_dir}/daily_usage.csv", index=False)
        model_usage.to_csv(f"{output_dir}/model_usage.csv", index=False)

        # Generate summary report
        report = {
            "period": {
                "start": df["timestamp"].min().isoformat(),
                "end": df["timestamp"].max().isoformat(),
                "days": (df["timestamp"].max() - df["timestamp"].min()).days + 1,
            },
            "total_queries": len(df),
            "total_tokens": int(df["token_count"].sum()),
            "total_cost": float(df["total_cost"].sum()),
            "average_daily_queries": len(df)
            / ((df["timestamp"].max() - df["timestamp"].min()).days + 1),
            "average_tokens_per_query": float(df["token_count"].mean()),
            "average_cost_per_query": float(df["total_cost"].mean()),
            "model_breakdown": model_usage.to_dict("records"),
            "feature_usage": feature_usage,
            "report_generated": datetime.now().isoformat(),
            "report_files": {
                "detailed_usage": f"{output_dir}/detailed_usage.csv",
                "daily_usage": f"{output_dir}/daily_usage.csv",
                "model_usage": f"{output_dir}/model_usage.csv",
                "visualizations": {
                    "daily_cost": f"{output_dir}/daily_cost.png",
                    "model_usage": f"{output_dir}/model_usage.png",
                    "cost_distribution": f"{output_dir}/cost_distribution.png",
                },
            },
        }

        # Save summary report
        with open(f"{output_dir}/usage_report.json", "w") as f:
            json.dump(report, f, indent=2)

        return report

    def _create_usage_visualizations(
        self, df, daily_usage, model_usage, feature_usage, output_dir
    ):
        """Create visualizations for the usage report"""
        plt.style.use("ggplot")

        # Daily cost chart
        plt.figure(figsize=(10, 6))
        plt.plot(
            daily_usage["date"], daily_usage["total_cost"], marker="o", linewidth=2
        )
        plt.title("Daily Cost")
        plt.xlabel("Date")
        plt.ylabel("Cost (USD)")
        plt.grid(True, linestyle="--", alpha=0.7)
        plt.tight_layout()
        plt.savefig(f"{output_dir}/daily_cost.png")
        plt.close()

        # Model usage chart
        plt.figure(figsize=(12, 6))
        ax = plt.subplot(1, 2, 1)
        model_usage.plot(kind="bar", x="model", y="token_count", ax=ax, color="skyblue")
        plt.title("Token Usage by Model")
        plt.ylabel("Token Count")
        plt.xticks(rotation=45)

        ax = plt.subplot(1, 2, 2)
        model_usage.plot(kind="bar", x="model", y="total_cost", ax=ax, color="salmon")
        plt.title("Cost by Model")
        plt.ylabel("Cost (USD)")
        plt.xticks(rotation=45)

        plt.tight_layout()
        plt.savefig(f"{output_dir}/model_usage.png")
        plt.close()

        # Cost distribution pie chart
        plt.figure(figsize=(10, 6))
        cost_distribution = model_usage[["model", "total_cost"]]
        plt.pie(
            cost_distribution["total_cost"],
            labels=cost_distribution["model"],
            autopct="%1.1f%%",
            startangle=90,
        )
        plt.axis("equal")
        plt.title("Cost Distribution by Model")
        plt.tight_layout()
        plt.savefig(f"{output_dir}/cost_distribution.png")
        plt.close()

        # Feature usage if available
        if feature_usage:
            plt.figure(figsize=(10, 6))
            features = list(feature_usage.keys())
            counts = list(feature_usage.values())
            plt.bar(features, counts, color="lightgreen")
            plt.title("Feature Usage")
            plt.xlabel("Feature")
            plt.ylabel("Usage Count")
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig(f"{output_dir}/feature_usage.png")
            plt.close()

    def simulate_pricing(
        self,
        usage_scenarios: List[Dict[str, Any]],
        output_dir: str = "pricing_simulations",
    ) -> Dict[str, Any]:
        """
        Simulate different pricing models across various usage scenarios

        Args:
            usage_scenarios: List of usage scenarios to simulate
            output_dir: Directory to save simulation results

        Returns:
            dict: Simulation results summary
        """
        os.makedirs(output_dir, exist_ok=True)

        # Dictionary to store simulation results
        simulation_results = {}

        for i, scenario in enumerate(usage_scenarios):
            scenario_name = scenario.get("name", f"Scenario {i+1}")
            daily_queries = scenario.get("daily_queries", 10)
            avg_tokens = scenario.get("avg_tokens_per_query", 1000)
            model_distribution = scenario.get(
                "model_distribution", {"gpt-3.5-turbo": 1.0}
            )
            tier = scenario.get("tier", "basic")
            features = scenario.get("features", [])

            # Estimate monthly cost for this scenario
            estimate = self.estimate_monthly_cost(
                daily_queries=daily_queries,
                avg_tokens_per_query=avg_tokens,
                model_distribution=model_distribution,
                tier=tier,
                features=features,
            )

            # Store result
            simulation_results[scenario_name] = estimate

        # Generate comparative visualization
        self._create_simulation_visualizations(simulation_results, output_dir)

        # Save simulation results
        with open(f"{output_dir}/simulation_results.json", "w") as f:
            json.dump(simulation_results, f, indent=2)

        # Calculate summary statistics
        summary = {
            "scenarios_count": len(simulation_results),
            "scenarios": list(simulation_results.keys()),
            "cost_range": {
                "min": min(
                    scenario["total_monthly_cost"]
                    for scenario in simulation_results.values()
                ),
                "max": max(
                    scenario["total_monthly_cost"]
                    for scenario in simulation_results.values()
                ),
                "avg": sum(
                    scenario["total_monthly_cost"]
                    for scenario in simulation_results.values()
                )
                / len(simulation_results),
            },
            "simulation_date": datetime.now().isoformat(),
            "output_files": {
                "detailed_results": f"{output_dir}/simulation_results.json",
                "visualizations": {
                    "cost_comparison": f"{output_dir}/cost_comparison.png",
                    "cost_breakdown": f"{output_dir}/cost_breakdown.png",
                },
            },
        }

        return summary

    def _create_simulation_visualizations(self, simulation_results, output_dir):
        """Create visualizations for pricing simulations"""
        scenario_names = list(simulation_results.keys())
        total_costs = [
            scenario["total_monthly_cost"] for scenario in simulation_results.values()
        ]

        # Create cost comparison bar chart
        plt.figure(figsize=(12, 6))
        plt.bar(scenario_names, total_costs, color="lightblue")
        plt.title("Monthly Cost Comparison Across Scenarios")
        plt.xlabel("Scenario")
        plt.ylabel("Monthly Cost (USD)")
        plt.xticks(rotation=45, ha="right")
        plt.grid(True, linestyle="--", alpha=0.7, axis="y")
        plt.tight_layout()
        plt.savefig(f"{output_dir}/cost_comparison.png")
        plt.close()

        # Create cost breakdown stacked bar chart
        subscription_costs = [
            scenario["monthly_subscription"] for scenario in simulation_results.values()
        ]
        model_costs = [
            scenario["total_model_cost"] for scenario in simulation_results.values()
        ]
        feature_costs = [
            scenario["total_feature_cost"] for scenario in simulation_results.values()
        ]

        plt.figure(figsize=(12, 6))
        width = 0.5

        plt.bar(
            scenario_names,
            subscription_costs,
            width,
            label="Subscription",
            color="skyblue",
        )
        plt.bar(
            scenario_names,
            model_costs,
            width,
            bottom=subscription_costs,
            label="Model Usage",
            color="salmon",
        )

        # Add feature costs if they exist
        bottoms = [a + b for a, b in zip(subscription_costs, model_costs)]
        plt.bar(
            scenario_names,
            feature_costs,
            width,
            bottom=bottoms,
            label="Features",
            color="lightgreen",
        )

        plt.title("Cost Breakdown by Category")
        plt.xlabel("Scenario")
        plt.ylabel("Cost (USD)")
        plt.legend(loc="upper left")
        plt.xticks(rotation=45, ha="right")
        plt.grid(True, linestyle="--", alpha=0.7, axis="y")
        plt.tight_layout()
        plt.savefig(f"{output_dir}/cost_breakdown.png")
        plt.close()

        # Create per-query cost comparison
        per_query_costs = [
            scenario["cost_per_query"] for scenario in simulation_results.values()
        ]

        plt.figure(figsize=(12, 6))
        plt.bar(scenario_names, per_query_costs, color="lightcoral")
        plt.title("Cost per Query Comparison")
        plt.xlabel("Scenario")
        plt.ylabel("Cost per Query (USD)")
        plt.xticks(rotation=45, ha="right")
        plt.grid(True, linestyle="--", alpha=0.7, axis="y")
        plt.tight_layout()
        plt.savefig(f"{output_dir}/per_query_cost.png")
        plt.close()

    def estimate_query_cost(
        self, model_name: str, input_tokens: float, output_tokens: float
    ) -> float:
        """
        Return the total cost (USD) for a single query,
        based on input and output token usage for a chosen model.
        """
        if model_name not in self.model_configs:
            raise ValueError(
                f"Model '{model_name}' not found in baseline pricing data."
            )

        pricing = self.model_configs[model_name]
        input_price = pricing["input"] * (input_tokens / 1000.0)
        output_price = pricing["output"] * (output_tokens / 1000.0)
        total_cost = input_price + output_price

        return total_cost


# Example usage
if __name__ == "__main__":
    # Initialize simulator
    simulator = PricingSimulator()

    # Example: Calculate cost for a single query
    cost = simulator.calculate_token_cost(
        model="gpt-4", token_count=2500, tier="pro", features=["priority_processing"]
    )
    print(f"Single query cost: ${cost['total_cost']}")

    # Example: Estimate monthly cost
    monthly = simulator.estimate_monthly_cost(
        daily_queries=20,
        avg_tokens_per_query=2000,
        model_distribution={"gpt-4": 0.3, "claude-3-sonnet": 0.7},
        tier="pro",
        features=["document_processing", "priority_processing"],
    )
    print(f"Estimated monthly cost: ${monthly['total_monthly_cost']:.2f}")

    # Example: Run pricing simulation for different scenarios
    scenarios = [
        {
            "name": "Low Usage - Basic",
            "daily_queries": 5,
            "avg_tokens_per_query": 1500,
            "model_distribution": {"gpt-3.5-turbo": 1.0},
            "tier": "basic",
            "features": [],
        },
        {
            "name": "Medium Usage - Pro",
            "daily_queries": 20,
            "avg_tokens_per_query": 2000,
            "model_distribution": {"gpt-4": 0.3, "claude-3-sonnet": 0.7},
            "tier": "pro",
            "features": ["document_processing", "priority_processing"],
        },
        {
            "name": "High Usage - Enterprise",
            "daily_queries": 100,
            "avg_tokens_per_query": 3000,
            "model_distribution": {"claude-3-opus": 0.5, "gpt-4": 0.5},
            "tier": "enterprise",
            "features": ["document_processing", "api_access", "custom_patterns"],
        },
    ]

    simulation = simulator.simulate_pricing(scenarios)
    print(
        f"Simulation complete. Results saved to {simulation['output_files']['detailed_results']}"
    )
