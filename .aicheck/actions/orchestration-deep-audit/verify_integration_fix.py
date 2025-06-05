"""
Verify that the integration fix is actually working
"""

import os
import sys

# Add backend to path
sys.path.insert(0, 'backend')

from integrations.pattern_orchestrator_integration_fixed import PatternOrchestrator

# Create a test instance
api_keys = {
    "anthropic": "test-key",
    "openai": "test-key", 
    "google": "test-key"
}

print("Creating PatternOrchestrator instance...")
orchestrator = PatternOrchestrator(api_keys=api_keys, pattern="gut")

print(f"\nAvailable models: {orchestrator.available_models}")
print(f"Expected: ['claude', 'chatgpt', 'gemini']")
print(f"Match: {orchestrator.available_models == ['claude', 'chatgpt', 'gemini']}")

# Check if the fix was applied
if 'anthropic' in orchestrator.available_models:
    print("\nERROR: Fix not applied! Still using provider names.")
elif 'claude' in orchestrator.available_models:
    print("\nSUCCESS: Fix applied! Using model names.")
else:
    print("\nERROR: No models found!")

# Test individual checks
print("\nTesting individual model checks:")
print(f"'claude' in available_models: {'claude' in orchestrator.available_models}")
print(f"'chatgpt' in available_models: {'chatgpt' in orchestrator.available_models}")
print(f"'gemini' in available_models: {'gemini' in orchestrator.available_models}")
print(f"'anthropic' in available_models: {'anthropic' in orchestrator.available_models}")
print(f"'openai' in available_models: {'openai' in orchestrator.available_models}")