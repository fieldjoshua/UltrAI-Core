#!/usr/bin/env python3
"""Quick environment check script"""
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

print("=== Environment Check ===")
print(f"ENVIRONMENT: {os.getenv('ENVIRONMENT', 'not set')}")
print(f"MINIMUM_MODELS_REQUIRED: {os.getenv('MINIMUM_MODELS_REQUIRED', 'not set')}")
print(f"ENABLE_SINGLE_MODEL_FALLBACK: {os.getenv('ENABLE_SINGLE_MODEL_FALLBACK', 'not set')}")
print("\n=== API Keys Status ===")
print(f"OPENAI_API_KEY: {'✓ Set' if os.getenv('OPENAI_API_KEY') else '✗ Not set'}")
print(f"ANTHROPIC_API_KEY: {'✓ Set' if os.getenv('ANTHROPIC_API_KEY') else '✗ Not set'}")
print(f"GOOGLE_API_KEY: {'✓ Set' if os.getenv('GOOGLE_API_KEY') else '✗ Not set'}")
print(f"HUGGINGFACE_API_KEY: {'✓ Set' if os.getenv('HUGGINGFACE_API_KEY') else '✗ Not set'}")

# Show masked API key prefixes for debugging
for key_name in ['OPENAI_API_KEY', 'ANTHROPIC_API_KEY', 'GOOGLE_API_KEY']:
    key_val = os.getenv(key_name)
    if key_val:
        print(f"{key_name} starts with: {key_val[:8]}...")