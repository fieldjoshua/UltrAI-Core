#!/usr/bin/env python3
from typing import Dict, List, Optional, Any, Tuple, Union
import json
import os
import logging
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("ultra_pricing")

class PricingSimulator:
    def __init__(self, config_file: str = "pricing_config.json"):
        """
        Initialize the pricing simulator with default values or from a config file
        
        Args:
            config_file: Path to the pricing configuration file
        """
        self.config_file = config_file
        
        # Default pricing model
        self.default_pricing = {
            # Base costs per 1K tokens for common models (USD)
            "base_costs": {
                "claude-3-opus": 0.015,       # Anthropic Claude 3 Opus
                "claude-3-sonnet": 0.008,     # Anthropic Claude 3 Sonnet
                "gpt-4": 0.03,                # OpenAI GPT-4
                "gpt-3.5-turbo": 0.001,       # OpenAI GPT-3.5 Turbo
                "mistral-large": 0.008,       # Mistral Large
                "mistral-medium": 0.002,      # Mistral Medium
                "mistral-small": 0.0006,      # Mistral Small
                "gemini-pro": 0.0005,         # Google Gemini Pro
                "llama-70b": 0.0001,          # Meta Llama 70B (self-hosted)
                "local": 0.00005              # Local models (estimated electricity/compute cost)
            },
            
            # Markup percentages for different tiers
            "markup_percentages": {
                "basic": 20,      # 20% markup for basic tier
                "pro": 35,        # 35% markup for pro tier
                "enterprise": 50  # 50% markup for enterprise tier
            },
            
            # Tiered pricing model
            "tiers": {
                "basic": {
                    "monthly_fee": 10.00,        # Base monthly subscription fee
                    "included_tokens": 100000,   # Free tokens included per month
                    "model_access": ["gpt-3.5-turbo", "mistral-small", "local"]
                },
                "pro": {
                    "monthly_fee": 30.00,
                    "included_tokens": 500000,
                    "model_access": ["gpt-3.5-turbo", "gpt-4", "claude-3-sonnet", "mistral-medium", "gemini-pro", "local"]
                },
                "enterprise": {
                    "monthly_fee": 100.00,
                    "included_tokens": 2000000,
                    "model_access": ["gpt-4", "claude-3-opus", "claude-3-sonnet", "mistral-large", "gemini-pro", "local"]
                }
            },
            
            # Volume discounts (applied after basic markup)
            "volume_discounts": {
                "1000000": 5,     # 5% discount for >1M tokens
                "5000000": 10,    # 10% discount for >5M tokens
                "10000000": 15,   # 15% discount for >10M tokens
                "50000000": 20    # 20% discount for >50M tokens
            },
            
            # Feature pricing (additional costs)
            "feature_costs": {
                "document_processing": 0.001,    # Per page
                "additional_iterations": 0.01,   # Per additional iteration
                "custom_patterns": 5.00,         # Monthly fee for custom patterns
                "api_access": 20.00,             # Monthly fee for API access
                "priority_processing": 0.02      # Per request
            }
        }
        
        # Usage history for simulation
        self.usage_history = []
        
        # Load config if exists
        self.load_config()
    
    def load_config(self) -> None:
        """Load pricing configuration from file if it exists"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    # Update only the keys that exist in the config file
                    for key, value in config.items():
                        if key in self.default_pricing:
                            self.default_pricing[key] = value
                logger.info(f"Loaded pricing configuration from {self.config_file}")
            except Exception as e:
                logger.error(f"Error loading pricing configuration: {e}")
        else:
            # Save the default configuration
            self.save_config()
    
    def save_config(self) -> None:
        """Save current pricing configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.default_pricing, f, indent=2)
            logger.info(f"Pricing configuration saved to {self.config_file}")
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
                if key in self.default_pricing:
                    self.default_pricing[key] = value
            self.save_config()
            return True
        except Exception as e:
            logger.error(f"Error updating pricing: {e}")
            return False
    
    def calculate_token_cost(self, 
                          model: str, 
                          token_count: int, 
                          tier: str = "basic", 
                          features: List[str] = None) -> Dict[str, Union[float, str]]:
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
        if model not in self.default_pricing["base_costs"]:
            model = "gpt-3.5-turbo"  # Default to a standard model
            
        if tier not in self.default_pricing["markup_percentages"]:
            tier = "basic"  # Default to basic tier
            
        # Calculate base cost (per 1000 tokens)
        base_cost_per_1k = self.default_pricing["base_costs"][model]
        base_cost = (token_count / 1000) * base_cost_per_1k
        
        # Apply markup based on tier
        markup_percentage = self.default_pricing["markup_percentages"][tier]
        markup_cost = base_cost * (markup_percentage / 100)
        
        # Check allowed models for the tier
        tier_models = self.default_pricing["tiers"][tier]["model_access"]
        if model not in tier_models:
            return {
                "status": "error",
                "message": f"Model {model} is not available in the {tier} tier",
                "allowed_models": tier_models,
                "cost": 0.0
            }
        
        # Apply volume discount if applicable
        volume_discount = 0
        for threshold, discount in sorted(self.default_pricing["volume_discounts"].items(), key=lambda x: int(x[0])):
            if token_count > int(threshold):
                volume_discount = discount / 100
                break
        
        discount_amount = (base_cost + markup_cost) * volume_discount
        
        # Calculate included tokens
        included_tokens = self.default_pricing["tiers"][tier]["included_tokens"]
        tokens_charged = max(0, token_count - included_tokens)
        
        # Recalculate costs with included tokens
        adjusted_base_cost = (tokens_charged / 1000) * base_cost_per_1k
        adjusted_markup_cost = adjusted_base_cost * (markup_percentage / 100)
        adjusted_discount = (adjusted_base_cost + adjusted_markup_cost) * volume_discount
        
        # Add feature costs
        feature_cost = 0
        feature_breakdown = {}
        
        for feature in features:
            if feature in self.default_pricing["feature_costs"]:
                feature_price = self.default_pricing["feature_costs"][feature]
                feature_cost += feature_price
                feature_breakdown[feature] = feature_price
        
        # Calculate final cost
        subtotal = adjusted_base_cost + adjusted_markup_cost - adjusted_discount
        total_cost = subtotal + feature_cost
        
        # Round to 4 decimal places
        total_cost = round(total_cost, 4)
        
        # Record this calculation in usage history
        self.usage_history.append({
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
            "total_cost": total_cost
        })
        
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
            "cost_per_1k_tokens": round(total_cost / (token_count / 1000), 6) if token_count > 0 else 0
        }
    
    def estimate_monthly_cost(self, 
                           daily_queries: int, 
                           avg_tokens_per_query: int, 
                           model_distribution: Dict[str, float], 
                           tier: str = "basic",
                           features: List[str] = None) -> Dict[str, Any]:
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
        monthly_subscription = self.default_pricing["tiers"][tier]["monthly_fee"]
        
        # Calculate model usage costs
        model_costs = {}
        total_model_cost = 0
        
        for model, percentage in model_distribution.items():
            # Check if model is available in this tier
            if model not in self.default_pricing["tiers"][tier]["model_access"]:
                continue
                
            model_token_count = monthly_tokens * percentage
            cost_result = self.calculate_token_cost(model, model_token_count, tier)
            
            if cost_result["status"] == "success":
                model_costs[model] = {
                    "percentage": percentage * 100,
                    "tokens": model_token_count,
                    "cost": cost_result["total_cost"]
                }
                total_model_cost += cost_result["total_cost"]
        
        # Calculate feature costs
        feature_costs = {}
        total_feature_cost = 0
        
        for feature in features:
            if feature in self.default_pricing["feature_costs"]:
                if feature in ["custom_patterns", "api_access"]:
                    # These are monthly fixed costs
                    feature_costs[feature] = self.default_pricing["feature_costs"][feature]
                    total_feature_cost += self.default_pricing["feature_costs"][feature]
                elif feature == "document_processing":
                    # Assume 5 pages per query on average
                    pages = monthly_queries * 5
                    cost = pages * self.default_pricing["feature_costs"][feature]
                    feature_costs[feature] = cost
                    total_feature_cost += cost
                elif feature == "additional_iterations":
                    # Assume 2 additional iterations per query on average
                    iterations = monthly_queries * 2
                    cost = iterations * self.default_pricing["feature_costs"][feature]
                    feature_costs[feature] = cost
                    total_feature_cost += cost
                elif feature == "priority_processing":
                    # Assume 30% of queries are priority
                    priority_queries = monthly_queries * 0.3
                    cost = priority_queries * self.default_pricing["feature_costs"][feature]
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
            "cost_per_query": total_cost / monthly_queries if monthly_queries > 0 else 0
        }
    
    def generate_usage_report(self, output_dir: str = "pricing_reports") -> Dict[str, Any]:
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
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['date'] = df['timestamp'].dt.date
        
        # Aggregate daily usage
        daily_usage = df.groupby('date').agg({
            'token_count': 'sum',
            'total_cost': 'sum'
        }).reset_index()
        
        # Model usage breakdown
        model_usage = df.groupby('model').agg({
            'token_count': 'sum',
            'total_cost': 'sum',
            'timestamp': 'count'
        }).reset_index()
        model_usage = model_usage.rename(columns={'timestamp': 'query_count'})
        
        # Feature usage
        feature_usage = {}
        for row in df.iterrows():
            for feature in row[1]['features']:
                if feature not in feature_usage:
                    feature_usage[feature] = 0
                feature_usage[feature] += 1
        
        # Generate visualizations
        self._create_usage_visualizations(df, daily_usage, model_usage, feature_usage, output_dir)
        
        # Save detailed usage data
        df.to_csv(f"{output_dir}/detailed_usage.csv", index=False)
        daily_usage.to_csv(f"{output_dir}/daily_usage.csv", index=False)
        model_usage.to_csv(f"{output_dir}/model_usage.csv", index=False)
        
        # Generate summary report
        report = {
            "period": {
                "start": df['timestamp'].min().isoformat(),
                "end": df['timestamp'].max().isoformat(),
                "days": (df['timestamp'].max() - df['timestamp'].min()).days + 1
            },
            "total_queries": len(df),
            "total_tokens": int(df['token_count'].sum()),
            "total_cost": float(df['total_cost'].sum()),
            "average_daily_queries": len(df) / ((df['timestamp'].max() - df['timestamp'].min()).days + 1),
            "average_tokens_per_query": float(df['token_count'].mean()),
            "average_cost_per_query": float(df['total_cost'].mean()),
            "model_breakdown": model_usage.to_dict('records'),
            "feature_usage": feature_usage,
            "report_generated": datetime.now().isoformat(),
            "report_files": {
                "detailed_usage": f"{output_dir}/detailed_usage.csv",
                "daily_usage": f"{output_dir}/daily_usage.csv",
                "model_usage": f"{output_dir}/model_usage.csv",
                "visualizations": {
                    "daily_cost": f"{output_dir}/daily_cost.png",
                    "model_usage": f"{output_dir}/model_usage.png",
                    "cost_distribution": f"{output_dir}/cost_distribution.png"
                }
            }
        }
        
        # Save summary report
        with open(f"{output_dir}/usage_report.json", 'w') as f:
            json.dump(report, f, indent=2)
        
        return report
    
    def _create_usage_visualizations(self, df, daily_usage, model_usage, feature_usage, output_dir):
        """Create visualizations for the usage report"""
        plt.style.use('ggplot')
        
        # Daily cost chart
        plt.figure(figsize=(10, 6))
        plt.plot(daily_usage['date'], daily_usage['total_cost'], marker='o', linewidth=2)
        plt.title('Daily Cost')
        plt.xlabel('Date')
        plt.ylabel('Cost (USD)')
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.savefig(f"{output_dir}/daily_cost.png")
        plt.close()
        
        # Model usage chart
        plt.figure(figsize=(12, 6))
        ax = plt.subplot(1, 2, 1)
        model_usage.plot(kind='bar', x='model', y='token_count', ax=ax, color='skyblue')
        plt.title('Token Usage by Model')
        plt.ylabel('Token Count')
        plt.xticks(rotation=45)
        
        ax = plt.subplot(1, 2, 2)
        model_usage.plot(kind='bar', x='model', y='total_cost', ax=ax, color='salmon')
        plt.title('Cost by Model')
        plt.ylabel('Cost (USD)')
        plt.xticks(rotation=45)
        
        plt.tight_layout()
        plt.savefig(f"{output_dir}/model_usage.png")
        plt.close()
        
        # Cost distribution pie chart
        plt.figure(figsize=(10, 6))
        cost_distribution = model_usage[['model', 'total_cost']]
        plt.pie(cost_distribution['total_cost'], labels=cost_distribution['model'], autopct='%1.1f%%', startangle=90)
        plt.axis('equal')
        plt.title('Cost Distribution by Model')
        plt.tight_layout()
        plt.savefig(f"{output_dir}/cost_distribution.png")
        plt.close()
        
        # Feature usage if available
        if feature_usage:
            plt.figure(figsize=(10, 6))
            features = list(feature_usage.keys())
            counts = list(feature_usage.values())
            plt.bar(features, counts, color='lightgreen')
            plt.title('Feature Usage')
            plt.xlabel('Feature')
            plt.ylabel('Usage Count')
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig(f"{output_dir}/feature_usage.png")
            plt.close()
    
    def simulate_pricing(self, 
                       usage_scenarios: List[Dict[str, Any]], 
                       output_dir: str = "pricing_simulations") -> Dict[str, Any]:
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
            model_distribution = scenario.get("model_distribution", {"gpt-3.5-turbo": 1.0})
            tier = scenario.get("tier", "basic")
            features = scenario.get("features", [])
            
            # Estimate monthly cost for this scenario
            estimate = self.estimate_monthly_cost(
                daily_queries=daily_queries,
                avg_tokens_per_query=avg_tokens,
                model_distribution=model_distribution,
                tier=tier,
                features=features
            )
            
            # Store result
            simulation_results[scenario_name] = estimate
        
        # Generate comparative visualization
        self._create_simulation_visualizations(simulation_results, output_dir)
        
        # Save simulation results
        with open(f"{output_dir}/simulation_results.json", 'w') as f:
            json.dump(simulation_results, f, indent=2)
        
        # Calculate summary statistics
        summary = {
            "scenarios_count": len(simulation_results),
            "scenarios": list(simulation_results.keys()),
            "cost_range": {
                "min": min(scenario["total_monthly_cost"] for scenario in simulation_results.values()),
                "max": max(scenario["total_monthly_cost"] for scenario in simulation_results.values()),
                "avg": sum(scenario["total_monthly_cost"] for scenario in simulation_results.values()) / len(simulation_results)
            },
            "simulation_date": datetime.now().isoformat(),
            "output_files": {
                "detailed_results": f"{output_dir}/simulation_results.json",
                "visualizations": {
                    "cost_comparison": f"{output_dir}/cost_comparison.png",
                    "cost_breakdown": f"{output_dir}/cost_breakdown.png"
                }
            }
        }
        
        return summary
    
    def _create_simulation_visualizations(self, simulation_results, output_dir):
        """Create visualizations for pricing simulations"""
        scenario_names = list(simulation_results.keys())
        total_costs = [scenario["total_monthly_cost"] for scenario in simulation_results.values()]
        
        # Create cost comparison bar chart
        plt.figure(figsize=(12, 6))
        plt.bar(scenario_names, total_costs, color='lightblue')
        plt.title('Monthly Cost Comparison Across Scenarios')
        plt.xlabel('Scenario')
        plt.ylabel('Monthly Cost (USD)')
        plt.xticks(rotation=45, ha='right')
        plt.grid(True, linestyle='--', alpha=0.7, axis='y')
        plt.tight_layout()
        plt.savefig(f"{output_dir}/cost_comparison.png")
        plt.close()
        
        # Create cost breakdown stacked bar chart
        subscription_costs = [scenario["monthly_subscription"] for scenario in simulation_results.values()]
        model_costs = [scenario["total_model_cost"] for scenario in simulation_results.values()]
        feature_costs = [scenario["total_feature_cost"] for scenario in simulation_results.values()]
        
        plt.figure(figsize=(12, 6))
        width = 0.5
        
        plt.bar(scenario_names, subscription_costs, width, label='Subscription', color='skyblue')
        plt.bar(scenario_names, model_costs, width, bottom=subscription_costs, label='Model Usage', color='salmon')
        
        # Add feature costs if they exist
        bottoms = [a + b for a, b in zip(subscription_costs, model_costs)]
        plt.bar(scenario_names, feature_costs, width, bottom=bottoms, label='Features', color='lightgreen')
        
        plt.title('Cost Breakdown by Category')
        plt.xlabel('Scenario')
        plt.ylabel('Cost (USD)')
        plt.legend(loc='upper left')
        plt.xticks(rotation=45, ha='right')
        plt.grid(True, linestyle='--', alpha=0.7, axis='y')
        plt.tight_layout()
        plt.savefig(f"{output_dir}/cost_breakdown.png")
        plt.close()
        
        # Create per-query cost comparison
        per_query_costs = [scenario["cost_per_query"] for scenario in simulation_results.values()]
        
        plt.figure(figsize=(12, 6))
        plt.bar(scenario_names, per_query_costs, color='lightcoral')
        plt.title('Cost per Query Comparison')
        plt.xlabel('Scenario')
        plt.ylabel('Cost per Query (USD)')
        plt.xticks(rotation=45, ha='right')
        plt.grid(True, linestyle='--', alpha=0.7, axis='y')
        plt.tight_layout()
        plt.savefig(f"{output_dir}/per_query_cost.png")
        plt.close()

# Example usage
if __name__ == "__main__":
    # Initialize simulator
    simulator = PricingSimulator()
    
    # Example: Calculate cost for a single query
    cost = simulator.calculate_token_cost(
        model="gpt-4",
        token_count=2500,
        tier="pro",
        features=["priority_processing"]
    )
    print(f"Single query cost: ${cost['total_cost']}")
    
    # Example: Estimate monthly cost
    monthly = simulator.estimate_monthly_cost(
        daily_queries=20,
        avg_tokens_per_query=2000,
        model_distribution={"gpt-4": 0.3, "claude-3-sonnet": 0.7},
        tier="pro",
        features=["document_processing", "priority_processing"]
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
            "features": []
        },
        {
            "name": "Medium Usage - Pro",
            "daily_queries": 20,
            "avg_tokens_per_query": 2000,
            "model_distribution": {"gpt-4": 0.3, "claude-3-sonnet": 0.7},
            "tier": "pro",
            "features": ["document_processing", "priority_processing"]
        },
        {
            "name": "High Usage - Enterprise",
            "daily_queries": 100,
            "avg_tokens_per_query": 3000,
            "model_distribution": {"claude-3-opus": 0.5, "gpt-4": 0.5},
            "tier": "enterprise",
            "features": ["document_processing", "api_access", "custom_patterns"]
        }
    ]
    
    simulation = simulator.simulate_pricing(scenarios)
    print(f"Simulation complete. Results saved to {simulation['output_files']['detailed_results']}") 