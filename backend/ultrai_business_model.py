#!/usr/bin/env python3
from pricing_calculator import PricingCalculator
import json
import os
from datetime import datetime

class UltrAIBusinessModel:
    """Business model simulator for UltrAI's pay-as-you-go token service"""
    
    def __init__(self):
        # Initialize with enterprise costs as base
        self.calculator = PricingCalculator()
        self.base_tier = "enterprise"  # Using enterprise tier costs as baseline
        
        # UltrAI pricing strategy (markups over base enterprise costs)
        self.default_markup_strategy = {
            "standard": 15,     # 15% markup for standard pay-as-you-go
            "premium": 25,      # 25% markup for premium pay-as-you-go
            "business": 20,     # 20% markup for business accounts (with volume discounts)
            "custom": 30        # 30% markup for custom solutions
        }
        
        # Volume discounts for prepaid tokens (reserve accounts)
        self.reserve_discounts = {
            "10000": 2,        # 2% discount for $10 reserve ($10k tokens)
            "50000": 5,        # 5% discount for $50 reserve
            "100000": 8,       # 8% discount for $100 reserve
            "500000": 12,      # 12% discount for $500 reserve
            "1000000": 15      # 15% discount for $1000+ reserve
        }
        
        # Token efficiency per model (how many tokens needed to get equivalent quality)
        # Lower number means more efficient (fewer tokens needed)
        self.token_efficiency = {
            "gpt-3.5-turbo": 1.5,      # Baseline is 1.0, gpt-3.5 needs 1.5x tokens for equivalent quality
            "gpt-4": 0.8,              # GPT-4 needs fewer tokens (0.8x) for equivalent quality
            "claude-3-sonnet": 0.9,    # Claude 3 Sonnet needs 0.9x tokens
            "claude-3-opus": 0.7,      # Claude 3 Opus needs 0.7x tokens (most efficient)
            "mistral-large": 0.85,     # Mistral Large needs 0.85x tokens
            "mistral-medium": 1.1,     # Mistral Medium needs 1.1x tokens
            "mistral-small": 1.3,      # Mistral Small needs 1.3x tokens
            "gemini-pro": 1.0,         # Gemini Pro used as reference (1.0)
            "llama-70b": 1.0,          # Llama 70B similar to Gemini Pro
            "local": 1.8               # Local models need 1.8x more tokens for equivalent quality
        }
        
        # Results storage
        self.analysis_results = {}
        
    def get_base_cost(self, model, token_count):
        """Get the base cost for tokens at enterprise rates"""
        # Get the raw enterprise tier pricing
        raw_price = self.calculator.calculate_cost(
            model=model,
            token_count=token_count,
            tier=self.base_tier
        )
        
        if raw_price["status"] == "error":
            # If the model is not available in enterprise tier, use a fallback model
            fallback_model = "gpt-4"  # Fallback to GPT-4
            raw_price = self.calculator.calculate_cost(
                model=fallback_model,
                token_count=token_count,
                tier=self.base_tier
            )
        
        # Return appropriate cost details
        return {
            "base_cost": raw_price.get("base_cost", 0.0),
            "total_cost": raw_price.get("total_cost", 0.0),
            "cost_per_1k": raw_price.get("cost_per_1k_tokens", 0.0)
        }
    
    def calculate_profit_margin(self, model, token_count, markup_type="standard", reserve_amount=0):
        """
        Calculate profit margins for UltrAI's pay-as-you-go model
        
        Args:
            model: LLM model to use
            token_count: Number of tokens
            markup_type: Type of markup (standard, premium, business, custom)
            reserve_amount: Amount in reserve account (for discount calculation)
        
        Returns:
            dict: Detailed profit analysis
        """
        # Get base enterprise cost
        base_cost_info = self.get_base_cost(model, token_count)
        base_cost = base_cost_info["total_cost"]
        
        # Get markup percentage
        markup_percentage = self.default_markup_strategy.get(markup_type, 15)
        
        # Calculate marked up price (before any discounts)
        marked_up_price = base_cost * (1 + markup_percentage/100)
        
        # Apply reserve discount if applicable
        discount_percentage = 0
        for threshold, discount in sorted(self.reserve_discounts.items(), key=lambda x: int(x[0])):
            if reserve_amount >= int(threshold):
                discount_percentage = discount
                break
        
        # Apply discount
        final_price = marked_up_price * (1 - discount_percentage/100)
        
        # Calculate profit
        profit = final_price - base_cost
        profit_margin = (profit / final_price) * 100 if final_price > 0 else 0
        
        result = {
            "model": model,
            "token_count": token_count,
            "base_enterprise_cost": base_cost,
            "markup_type": markup_type,
            "markup_percentage": markup_percentage,
            "marked_up_price": marked_up_price,
            "reserve_amount": reserve_amount,
            "reserve_discount_percentage": discount_percentage,
            "final_price_to_customer": final_price,
            "profit": profit,
            "profit_margin_percentage": profit_margin,
            "cost_per_1k_tokens": {
                "enterprise_cost": base_cost_info["cost_per_1k"],
                "customer_price": (final_price / token_count) * 1000 if token_count > 0 else 0
            },
            "effective_price_adjusted_for_efficiency": self.calculate_efficiency_adjusted_price(model, final_price, token_count)
        }
        
        return result
    
    def calculate_efficiency_adjusted_price(self, model, price, token_count):
        """Calculate the effective price when token efficiency is considered"""
        efficiency_factor = self.token_efficiency.get(model, 1.0)
        
        # If efficiency factor is 1.0, the price is unchanged
        # If factor is 0.8, the model is more efficient, so effective price is lower
        # If factor is 1.5, the model is less efficient, so effective price is higher
        effective_price = price * efficiency_factor
        effective_price_per_1k = (effective_price / token_count) * 1000 if token_count > 0 else 0
        
        return {
            "efficiency_factor": efficiency_factor,
            "effective_total_price": effective_price,
            "effective_price_per_1k_tokens": effective_price_per_1k
        }
    
    def compare_pricing_strategies(self, token_counts=[1000, 10000, 100000, 1000000], 
                                  reserve_amounts=[0, 10000, 100000, 1000000]):
        """
        Compare different pricing strategies across models, token volumes, and reserve amounts
        
        Returns:
            dict: Comprehensive pricing comparison
        """
        results = {
            "models": {},
            "summary": {
                "most_profitable": {},
                "most_cost_effective": {},
                "best_value": {}
            },
            "reserve_analysis": {}
        }
        
        # Use a subset of models for faster analysis
        all_models = ["gpt-3.5-turbo", "gpt-4", "claude-3-sonnet", "claude-3-opus", "mistral-large", "local"]
        markup_types = list(self.default_markup_strategy.keys())
        
        # Calculate for all combinations
        for model in all_models:
            results["models"][model] = {}
            
            for token_count in token_counts:
                results["models"][model][token_count] = {}
                
                for markup in markup_types:
                    results["models"][model][token_count][markup] = {}
                    
                    for reserve in reserve_amounts:
                        analysis = self.calculate_profit_margin(
                            model=model,
                            token_count=token_count,
                            markup_type=markup,
                            reserve_amount=reserve
                        )
                        
                        results["models"][model][token_count][markup][reserve] = analysis
        
        # Identify most profitable combinations
        max_profit_margin = 0
        max_profit_config = None
        
        # Most cost-effective for customers (lowest price per 1k adjusted for efficiency)
        min_effective_price = float('inf')
        min_price_config = None
        
        # Best value (balancing profit and customer value)
        best_value_score = 0
        best_value_config = None
        
        # Analyze all results
        for model in all_models:
            for token_count in token_counts:
                for markup in markup_types:
                    for reserve in reserve_amounts:
                        result = results["models"][model][token_count][markup][reserve]
                        
                        # Check if most profitable
                        if result["profit_margin_percentage"] > max_profit_margin:
                            max_profit_margin = result["profit_margin_percentage"]
                            max_profit_config = {
                                "model": model,
                                "token_count": token_count,
                                "markup_type": markup,
                                "reserve_amount": reserve,
                                "profit_margin": result["profit_margin_percentage"],
                                "profit": result["profit"]
                            }
                        
                        # Check if most cost-effective
                        eff_price = result["effective_price_adjusted_for_efficiency"]["effective_price_per_1k_tokens"]
                        if eff_price < min_effective_price and eff_price > 0:
                            min_effective_price = eff_price
                            min_price_config = {
                                "model": model,
                                "token_count": token_count,
                                "markup_type": markup,
                                "reserve_amount": reserve,
                                "effective_price_per_1k": eff_price,
                                "efficiency_factor": result["effective_price_adjusted_for_efficiency"]["efficiency_factor"]
                            }
                        
                        # Calculate value score (profit margin × efficiency)
                        # Higher profit and better efficiency (lower factor) gives higher score
                        value_score = result["profit_margin_percentage"] * (1/result["effective_price_adjusted_for_efficiency"]["efficiency_factor"])
                        if value_score > best_value_score:
                            best_value_score = value_score
                            best_value_config = {
                                "model": model,
                                "token_count": token_count,
                                "markup_type": markup,
                                "reserve_amount": reserve,
                                "value_score": value_score,
                                "profit_margin": result["profit_margin_percentage"],
                                "efficiency_factor": result["effective_price_adjusted_for_efficiency"]["efficiency_factor"]
                            }
        
        # Add summary
        results["summary"]["most_profitable"] = max_profit_config
        results["summary"]["most_cost_effective"] = min_price_config
        results["summary"]["best_value"] = best_value_config
        
        # Analyze reserve account impact
        for reserve in reserve_amounts:
            avg_discount_impact = {}
            for markup in markup_types:
                total_impact = 0
                count = 0
                
                for model in all_models:
                    for token_count in token_counts:
                        no_reserve = results["models"][model][token_count][markup][0]["final_price_to_customer"]
                        with_reserve = results["models"][model][token_count][markup][reserve]["final_price_to_customer"]
                        
                        if no_reserve > 0:
                            savings_pct = 100 * (no_reserve - with_reserve) / no_reserve
                            total_impact += savings_pct
                            count += 1
                
                avg_impact = total_impact / count if count > 0 else 0
                avg_discount_impact[markup] = avg_impact
            
            results["reserve_analysis"][reserve] = {
                "avg_savings_percentage": avg_discount_impact,
                "discount_applied": self.get_discount_for_reserve(reserve)
            }
        
        self.analysis_results = results
        return results
    
    def get_discount_for_reserve(self, reserve_amount):
        """Get discount percentage for a given reserve amount"""
        discount = 0
        for threshold, disc in sorted(self.reserve_discounts.items(), key=lambda x: int(x[0])):
            if reserve_amount >= int(threshold):
                discount = disc
        return discount
    
    def generate_pricing_recommendations(self):
        """Generate pricing recommendations based on analysis results"""
        if not self.analysis_results:
            self.compare_pricing_strategies()
        
        recommendations = {
            "optimal_pricing_tiers": self.generate_optimal_tiers(),
            "reserve_account_recommendations": self.generate_reserve_recommendations(),
            "model_recommendations": self.generate_model_recommendations(),
            "marketing_positioning": self.generate_marketing_positioning()
        }
        
        return recommendations
    
    def generate_optimal_tiers(self):
        """Generate optimal pricing tier recommendations"""
        # Standard tier: Most cost-effective model with moderate markup
        standard_model = self.analysis_results["summary"]["most_cost_effective"]["model"]
        standard_price_per_1k = self.analysis_results["summary"]["most_cost_effective"]["effective_price_per_1k"]
        
        # Premium tier: Best value model with premium markup
        premium_model = self.analysis_results["summary"]["best_value"]["model"]
        premium_price_factor = 1 + (self.default_markup_strategy["premium"] / 100)
        
        # Business tier: Most profitable with business markup and volume discount
        business_model = self.analysis_results["summary"]["most_profitable"]["model"]
        business_price_factor = 1 + (self.default_markup_strategy["business"] / 100)
        
        return {
            "standard_tier": {
                "suggested_models": [standard_model],
                "pricing_strategy": "Most cost-effective pricing",
                "target_price_per_1k": standard_price_per_1k,
                "markup_percentage": self.default_markup_strategy["standard"],
                "positioning": "Affordable access to quality AI"
            },
            "premium_tier": {
                "suggested_models": [premium_model],
                "pricing_strategy": "Best value pricing (balancing quality and cost)",
                "price_factor_over_standard": premium_price_factor,
                "markup_percentage": self.default_markup_strategy["premium"],
                "positioning": "Superior quality with reasonable pricing"
            },
            "business_tier": {
                "suggested_models": [business_model],
                "pricing_strategy": "Volume-based pricing with business markup",
                "price_factor_over_standard": business_price_factor,
                "markup_percentage": self.default_markup_strategy["business"],
                "positioning": "Enterprise-grade AI with predictable pricing"
            }
        }
    
    def generate_reserve_recommendations(self):
        """Generate recommendations for reserve account levels"""
        reserve_levels = []
        
        for amount, discount in sorted(self.reserve_discounts.items(), key=lambda x: int(x[0])):
            if int(amount) in self.analysis_results["reserve_analysis"]:
                avg_savings = self.analysis_results["reserve_analysis"][int(amount)]["avg_savings_percentage"]
                max_saving = max(avg_savings.values())
                
                reserve_levels.append({
                    "amount": int(amount),
                    "discount_percentage": discount,
                    "avg_savings_percentage": max_saving,
                    "breakeven_queries": int(amount) / (int(amount) * (discount / 100))
                })
        
        return {
            "recommended_levels": reserve_levels,
            "optimal_entry_point": min(reserve_levels, key=lambda x: x["breakeven_queries"]) if reserve_levels else None,
            "best_value_point": max(reserve_levels, key=lambda x: x["avg_savings_percentage"]) if reserve_levels else None
        }
    
    def generate_model_recommendations(self):
        """Generate model selection recommendations"""
        # Extract the recommended models
        most_profitable_model = self.analysis_results["summary"]["most_profitable"]["model"]
        most_cost_effective_model = self.analysis_results["summary"]["most_cost_effective"]["model"]
        best_value_model = self.analysis_results["summary"]["best_value"]["model"]
        
        # Find models with good token efficiency
        efficient_models = sorted(
            [(model, factor) for model, factor in self.token_efficiency.items() if factor < 1.0],
            key=lambda x: x[1]
        )
        
        return {
            "profitable_models": [most_profitable_model],
            "cost_effective_models": [most_cost_effective_model],
            "value_models": [best_value_model],
            "token_efficient_models": efficient_models,
            "suggested_model_mix": {
                "standard_tier": [most_cost_effective_model],
                "premium_tier": [best_value_model],
                "business_tier": [most_profitable_model],
                "custom_solutions": [model for model, _ in efficient_models[:2]]
            }
        }
    
    def generate_marketing_positioning(self):
        """Generate marketing positioning recommendations"""
        return {
            "value_propositions": {
                "standard_tier": "Affordable AI with quality results",
                "premium_tier": "Superior AI quality with reasonable pricing",
                "business_tier": "Enterprise-grade AI with volume pricing",
                "reserve_accounts": "Pre-pay and save with predictable pricing"
            },
            "competitive_positioning": {
                "vs_direct_api": "Simplified access without technical overhead",
                "vs_flat_fee": "Pay only for what you use, no wasted resources",
                "vs_competitors": "Better performance per token with optimized models"
            },
            "key_differentiators": [
                "Token efficiency optimization",
                "Reserve account discounts",
                "Enterprise-grade models at accessible prices",
                "Pay-as-you-go flexibility"
            ]
        }
    
    def save_analysis(self, filename=None):
        """Save the analysis to a file"""
        if not self.analysis_results:
            self.compare_pricing_strategies()
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ultrai_business_analysis_{timestamp}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump({
                    "analysis_results": self.analysis_results,
                    "recommendations": self.generate_pricing_recommendations(),
                    "timestamp": datetime.now().isoformat(),
                    "parameters": {
                        "base_tier": self.base_tier,
                        "markup_strategy": self.default_markup_strategy,
                        "reserve_discounts": self.reserve_discounts,
                        "token_efficiency": self.token_efficiency
                    }
                }, f, indent=2)
            
            return {"status": "success", "filename": filename}
        except Exception as e:
            return {"status": "error", "message": str(e)}

def main():
    """Run a business model analysis for UltrAI"""
    print("=== UltrAI Business Model Analysis ===\n")
    print("Analyzing token pricing strategies for pay-as-you-go service...")
    
    # Create business model
    model = UltrAIBusinessModel()
    
    # Run analysis with a smaller dataset for faster execution
    analysis = model.compare_pricing_strategies(
        token_counts=[1000, 100000],
        reserve_amounts=[0, 10000, 100000]
    )
    
    # Generate recommendations
    recommendations = model.generate_pricing_recommendations()
    
    # Save analysis
    save_result = model.save_analysis()
    
    # Display key findings
    print("\nAnalysis complete!")
    if save_result["status"] == "success":
        print(f"Full analysis saved to: {save_result['filename']}")
    
    print("\n=== Key Findings ===")
    
    # Most profitable configuration
    most_profitable = analysis["summary"]["most_profitable"]
    print(f"\nMost profitable configuration:")
    print(f"  Model: {most_profitable['model']}")
    print(f"  Markup type: {most_profitable['markup_type']} ({model.default_markup_strategy[most_profitable['markup_type']]}%)")
    print(f"  Token volume: {most_profitable['token_count']}")
    print(f"  Reserve amount: ${most_profitable['reserve_amount']}")
    print(f"  Profit margin: {most_profitable['profit_margin']:.2f}%")
    
    # Most cost-effective configuration
    cost_effective = analysis["summary"]["most_cost_effective"]
    print(f"\nMost cost-effective configuration (for customers):")
    print(f"  Model: {cost_effective['model']}")
    print(f"  Effective price per 1K tokens: ${cost_effective['effective_price_per_1k']:.6f}")
    print(f"  Efficiency factor: {cost_effective['efficiency_factor']:.2f}")
    
    # Best value configuration
    best_value = analysis["summary"]["best_value"]
    print(f"\nBest value configuration (balance of profit and efficiency):")
    print(f"  Model: {best_value['model']}")
    print(f"  Markup type: {best_value['markup_type']}")
    print(f"  Profit margin: {best_value['profit_margin']:.2f}%")
    print(f"  Efficiency factor: {best_value['efficiency_factor']:.2f}")
    
    # Optimal pricing tiers
    print("\n=== Recommended Pricing Tiers ===")
    tiers = recommendations["optimal_pricing_tiers"]
    
    print(f"\nStandard Tier:")
    print(f"  Models: {', '.join(tiers['standard_tier']['suggested_models'])}")
    print(f"  Target price per 1K tokens: ${tiers['standard_tier']['target_price_per_1k']:.6f}")
    print(f"  Markup: {tiers['standard_tier']['markup_percentage']}%")
    
    print(f"\nPremium Tier:")
    print(f"  Models: {', '.join(tiers['premium_tier']['suggested_models'])}")
    print(f"  Price factor over standard: {tiers['premium_tier']['price_factor_over_standard']:.2f}x")
    print(f"  Markup: {tiers['premium_tier']['markup_percentage']}%")
    
    print(f"\nBusiness Tier:")
    print(f"  Models: {', '.join(tiers['business_tier']['suggested_models'])}")
    print(f"  Price factor over standard: {tiers['business_tier']['price_factor_over_standard']:.2f}x")
    print(f"  Markup: {tiers['business_tier']['markup_percentage']}%")
    
    # Reserve account recommendations
    print("\n=== Reserve Account Recommendations ===")
    reserve_recs = recommendations["reserve_account_recommendations"]
    
    if "optimal_entry_point" in reserve_recs and reserve_recs["optimal_entry_point"]:
        entry = reserve_recs["optimal_entry_point"]
        print(f"\nOptimal entry point: ${entry['amount']}")
        print(f"  Discount: {entry['discount_percentage']}%")
        print(f"  Breakeven queries: {entry['breakeven_queries']:.0f}")
    
    if "best_value_point" in reserve_recs and reserve_recs["best_value_point"]:
        best = reserve_recs["best_value_point"]
        print(f"\nBest value point: ${best['amount']}")
        print(f"  Discount: {best['discount_percentage']}%")
        print(f"  Average savings: {best['avg_savings_percentage']:.2f}%")
    
    # Marketing positioning
    print("\n=== Marketing Positioning ===")
    positioning = recommendations["marketing_positioning"]
    
    print("\nValue Propositions:")
    for tier, prop in positioning["value_propositions"].items():
        print(f"  {tier}: {prop}")
    
    print("\nKey Differentiators:")
    for diff in positioning["key_differentiators"]:
        print(f"  • {diff}")

if __name__ == "__main__":
    main() 