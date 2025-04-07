#!/usr/bin/env python3
from pricing_calculator import PricingCalculator
import re
import sys
import argparse

class TokenEstimator:
    """Simple token estimation and pricing tool"""
    
    def __init__(self):
        self.calculator = PricingCalculator()
        self.tokenizer_pattern = re.compile(r'\s+|\b')
    
    def estimate_tokens(self, text):
        """Simple token count estimator"""
        tokens = self.tokenizer_pattern.split(text)
        return len([t for t in tokens if t])
    
    def calculate_price(self, text, model="gpt-3.5-turbo", tier="basic", features=None, completion_ratio=2.0):
        """
        Calculate the estimated price for a given text
        
        Args:
            text: The input text
            model: The model to use
            tier: Pricing tier (basic, pro, enterprise)
            features: List of additional features
            completion_ratio: Ratio of completion tokens to prompt tokens
        
        Returns:
            dict: Price estimation details
        """
        if features is None:
            features = []
            
        # Count tokens
        prompt_tokens = self.estimate_tokens(text)
        completion_tokens = int(prompt_tokens * completion_ratio)
        total_tokens = prompt_tokens + completion_tokens
        
        # Calculate price
        price_info = self.calculator.calculate_cost(model, total_tokens, tier, features)
        
        # Add token estimates
        price_info.update({
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "prompt_text_preview": text[:50] + "..." if len(text) > 50 else text
        })
        
        return price_info

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Quick token price estimator for Ultra Framework')
    
    parser.add_argument('--text', type=str, help='Input text to estimate (wrap in quotes)')
    parser.add_argument('--file', type=str, help='Input file to estimate')
    parser.add_argument('--model', type=str, default='gpt-3.5-turbo', 
                        choices=['gpt-3.5-turbo', 'gpt-4', 'claude-3-sonnet', 'claude-3-opus', 
                                'mistral-small', 'mistral-medium', 'mistral-large', 
                                'gemini-pro', 'llama-70b', 'local'],
                        help='Model to use for estimation')
    parser.add_argument('--tier', type=str, default='basic', 
                        choices=['basic', 'pro', 'enterprise'],
                        help='Pricing tier')
    parser.add_argument('--features', type=str, nargs='*', 
                        choices=['document_processing', 'additional_iterations', 
                                'custom_patterns', 'api_access', 'priority_processing'],
                        help='Additional features to include')
    parser.add_argument('--ratio', type=float, default=2.0,
                        help='Completion to prompt token ratio (default: 2.0)')
    
    args = parser.parse_args()
    
    # Get input text
    text = ""
    if args.text:
        text = args.text
    elif args.file:
        try:
            with open(args.file, 'r') as f:
                text = f.read()
        except Exception as e:
            print(f"Error reading file: {e}")
            return
    else:
        # If no text or file provided, read from stdin
        print("Enter or paste your text (Ctrl+D to finish):")
        try:
            text = sys.stdin.read().strip()
        except KeyboardInterrupt:
            print("\nCancelled.")
            return
    
    if not text:
        print("No input text provided.")
        return
    
    # Calculate price
    estimator = TokenEstimator()
    result = estimator.calculate_price(
        text=text,
        model=args.model,
        tier=args.tier,
        features=args.features,
        completion_ratio=args.ratio
    )
    
    # Check for errors
    if result["status"] == "error":
        print(f"Error: {result['message']}")
        print(f"Allowed models for {args.tier} tier: {', '.join(result['allowed_models'])}")
        return
    
    # Display results
    print("\n=== Token and Price Estimate ===")
    print(f"Pricing tier: {args.tier}")
    print(f"Model: {args.model}")
    
    if args.features:
        print(f"Features: {', '.join(args.features)}")
    
    print(f"\nPrompt tokens: {result['prompt_tokens']}")
    print(f"Estimated completion tokens: {result['completion_tokens']}")
    print(f"Total tokens: {result['token_count']}")
    
    if result['tokens_charged'] > 0:
        print(f"Tokens charged (after {result['included_tokens']} included): {result['tokens_charged']}")
    else:
        print(f"Tokens charged: 0 (under the {result['included_tokens']} included tokens)")
    
    print(f"\nBase cost: ${result['base_cost']:.6f}")
    
    if result['markup_cost'] > 0:
        print(f"Markup ({result['markup_percentage']}%): ${result['markup_cost']:.6f}")
    
    if result['discount_amount'] > 0:
        print(f"Volume discount ({result['volume_discount_percentage']}%): -${result['discount_amount']:.6f}")
    
    if result['feature_costs']:
        print(f"\nFeature costs: ${result['feature_cost_total']:.6f}")
        for feature, cost in result['feature_costs'].items():
            print(f"  - {feature}: ${cost:.6f}")
    
    print(f"\nTotal cost for this request: ${result['total_cost']:.6f}")
    print(f"Cost per 1K tokens: ${result['cost_per_1k_tokens']:.6f}")
    
    # Monthly projection
    queries_per_day = 30
    monthly_tokens = result['token_count'] * queries_per_day * 30
    monthly_cost = result['total_cost'] * queries_per_day * 30
    
    print(f"\nMonthly projection (assuming {queries_per_day} similar queries per day):")
    print(f"Monthly tokens: {monthly_tokens:,}")
    print(f"Monthly token cost: ${monthly_cost:.2f}")
    print(f"Monthly subscription fee: ${result['monthly_fee']:.2f}")
    print(f"Total monthly cost: ${monthly_cost + result['monthly_fee']:.2f}")

if __name__ == "__main__":
    main() 