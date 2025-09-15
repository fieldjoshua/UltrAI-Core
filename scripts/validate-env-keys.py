#!/usr/bin/env python3
"""
Validate environment-specific API key configuration.

This script checks that API keys are properly configured for the current environment
and that they appear to be different from other environments.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv


def load_env_file(env_file):
    """Load environment variables from a specific file."""
    env_vars = {}
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
    return env_vars


def check_api_keys():
    """Check API key configuration for current environment."""
    current_env = os.getenv("ENVIRONMENT", "development")
    print(f"Checking API keys for environment: {current_env}")
    print("-" * 50)

    # API key prefixes to check
    api_keys = [
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY", 
        "GOOGLE_API_KEY",
        "HUGGINGFACE_API_KEY"
    ]

    # Load current environment
    current_keys = {}
    missing_keys = []

    for key in api_keys:
        value = os.getenv(key)
        if value and value not in ["your-api-key-here", "CHANGE_ME", "TODO"]:
            # Mask the key for security
            masked = value[:8] + "..." + value[-4:] if len(value) > 12 else "***"
            current_keys[key] = {
                "value": value,
                "masked": masked,
                "length": len(value)
            }
        else:
            missing_keys.append(key)

    # Check other environment files
    env_files = {
        "development": Path(".env.development"),
        "staging": Path(".env.staging"),
        "production": Path(".env.production"),
        "local": Path(".env")
    }

    # Load keys from other environments
    other_envs = {}
    for env_name, env_file in env_files.items():
        if env_name != current_env and env_file.exists():
            other_envs[env_name] = load_env_file(env_file)

    # Report findings
    print("\n✅ Configured API Keys:")
    for key, info in current_keys.items():
        print(f"  {key}: {info['masked']} (length: {info['length']})")

    if missing_keys:
        print("\n❌ Missing API Keys:")
        for key in missing_keys:
            print(f"  {key}: Not configured or using placeholder")

    # Check for key reuse across environments
    print("\n🔍 Checking for key reuse across environments...")
    reused_keys = []

    for key, info in current_keys.items():
        for env_name, env_vars in other_envs.items():
            if key in env_vars and env_vars[key] == info["value"]:
                reused_keys.append((key, env_name))

    if reused_keys:
        print("\n⚠️  WARNING: The following keys are reused in other environments:")
        for key, env_name in reused_keys:
            print(f"  {key} is also used in {env_name}")
        print("\n  This can cause rate limit collisions!")
    else:
        print("  ✅ No key reuse detected")

    # Check health cache configuration
    print("\n🏥 Health Check Configuration:")
    cache_ttl = os.getenv("MODEL_HEALTH_CACHE_TTL_MINUTES", "5")
    recovery_window = os.getenv("PROVIDER_RECOVERY_WINDOW_MINUTES", "5")
    print(f"  Model Health Cache TTL: {cache_ttl} minutes")
    print(f"  Provider Recovery Window: {recovery_window} minutes")

    # Environment-specific recommendations
    print(f"\n📋 Recommendations for {current_env}:")
    if current_env == "development":
        print("  - Use separate development API keys with lower rate limits")
        print("  - Consider shorter health check TTLs for testing (2-3 minutes)")
    elif current_env == "staging":
        print("  - Use staging-specific API keys")
        print("  - Test rate limit handling without affecting production")
    elif current_env == "production":
        print("  - Ensure production API keys have sufficient rate limits")
        print("  - Use longer health check TTLs for stability (5-10 minutes)")
        print("  - Set up monitoring and alerts for API usage")

    # Return status
    if missing_keys or reused_keys:
        return False
    return True


if __name__ == "__main__":
    # Load current environment
    load_dotenv()

    # Run validation
    success = check_api_keys()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ Environment API key configuration looks good!")
        sys.exit(0)
    else:
        print("❌ Issues found with API key configuration")
        sys.exit(1)
