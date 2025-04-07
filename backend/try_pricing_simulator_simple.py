#!/usr/bin/env python3
from pricing_simulator import PricingSimulator
import json

class SimplePricingSimulator(PricingSimulator):
    """A simplified version of the PricingSimulator that skips visualization features"""
    
    def __init__(self, config_file: str = "pricing_config.json"):
        super().__init__(config_file)
    
    def generate_usage_report(self, output_dir: str = None):
        """Override to skip visualization"""
        if not self.usage_history:
            return {"status": "error", "message": "No usage history available"}
        
        return {
            "status": "success",
            "usage_count": len(self.usage_history),
            "total_cost": sum(entry["total_cost"] for entry in self.usage_history),
            "total_tokens": sum(entry["token_count"] for entry in self.usage_history)
        }
    
    def simulate_pricing(self, usage_scenarios, output_dir: str = None):
        """Override to skip visualization"""
        results = {"scenarios": {}, "summary": {}}
        total_cost = 0
        
        for scenario in usage_scenarios:
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
            "scenario_count": len(usage_scenarios)
        }
        
        return results

def main():
    # Create simplified pricing simulator instance
    simulator = SimplePricingSimulator()
    
    print("=== Ultra Framework Pricing Simulator (Simple Version) ===\n")
    
    # Example 1: Calculate cost for a single query
    print("Example 1: Calculate cost for a single query")
    cost_basic = simulator.calculate_token_cost(
        model="gpt-4", 
        token_count=5000, 
        tier="basic"
    )
    
    # This will fail because gpt-4 is not available in basic tier
    print(f"Basic tier with GPT-4 (5,000 tokens):")
    print(json.dumps(cost_basic, indent=2))
    print()
    
    # Try with a model available in basic tier
    cost_basic_valid = simulator.calculate_token_cost(
        model="gpt-3.5-turbo", 
        token_count=5000, 
        tier="basic"
    )
    print(f"Basic tier with GPT-3.5 Turbo (5,000 tokens):")
    print(json.dumps(cost_basic_valid, indent=2))
    print()
    
    # Example 2: Pro tier with more tokens
    cost_pro = simulator.calculate_token_cost(
        model="claude-3-sonnet", 
        token_count=50000, 
        tier="pro",
        features=["priority_processing"]
    )
    print(f"Pro tier with Claude 3 Sonnet (50,000 tokens) + priority:")
    print(json.dumps(cost_pro, indent=2))
    print()
    
    # Example 3: Enterprise tier with high volume
    cost_enterprise = simulator.calculate_token_cost(
        model="claude-3-opus", 
        token_count=2500000, 
        tier="enterprise",
        features=["document_processing", "custom_patterns"]
    )
    print(f"Enterprise tier with Claude 3 Opus (2.5M tokens) + features:")
    print(json.dumps(cost_enterprise, indent=2))
    print()
    
    # Example 4: Monthly cost estimation
    print("Example 4: Monthly cost estimation")
    monthly_estimate = simulator.estimate_monthly_cost(
        daily_queries=100,
        avg_tokens_per_query=2000,
        model_distribution={
            "gpt-4": 0.3,
            "claude-3-sonnet": 0.4,
            "mistral-medium": 0.3
        },
        tier="pro",
        features=["document_processing", "priority_processing"]
    )
    print(f"Monthly cost estimate for Pro tier:")
    print(json.dumps(monthly_estimate, indent=2))
    print()
    
    # Example 5: Generate a pricing simulation with different scenarios
    print("Example 5: Pricing simulation with different scenarios")
    scenarios = [
        {
            "name": "Small Business",
            "daily_queries": 50,
            "avg_tokens_per_query": 1500,
            "model_distribution": {"gpt-3.5-turbo": 0.7, "mistral-small": 0.3},
            "tier": "basic",
            "features": []
        },
        {
            "name": "Medium Business",
            "daily_queries": 200,
            "avg_tokens_per_query": 3000,
            "model_distribution": {"gpt-4": 0.4, "claude-3-sonnet": 0.6},
            "tier": "pro",
            "features": ["document_processing", "api_access"]
        },
        {
            "name": "Enterprise",
            "daily_queries": 1000,
            "avg_tokens_per_query": 5000,
            "model_distribution": {"claude-3-opus": 0.5, "mistral-large": 0.5},
            "tier": "enterprise",
            "features": ["document_processing", "api_access", "custom_patterns", "priority_processing"]
        }
    ]
    
    simulation_results = simulator.simulate_pricing(scenarios)
    print(f"Simulation results:")
    print(json.dumps(simulation_results, indent=2))

if __name__ == "__main__":
    main() 