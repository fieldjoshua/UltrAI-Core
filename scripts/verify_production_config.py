#!/usr/bin/env python3
"""Verify production configuration before deployment."""

import os
import sys
from pathlib import Path

# Add backend to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))


def check_env_var(name: str, required: bool = True) -> tuple[bool, str]:
    """Check if environment variable is set."""
    value = os.environ.get(name)
    if required and not value:
        return False, f"❌ {name} is not set"
    elif not value:
        return True, f"⚠️  {name} is not set (optional)"
    else:
        # Hide sensitive values
        if any(keyword in name.lower() for keyword in ["key", "secret", "password", "token"]):
            display_value = value[:4] + "..." + value[-4:] if len(value) > 8 else "***"
        else:
            display_value = value
        return True, f"✓ {name} = {display_value}"


def verify_production_config():
    """Verify all production configuration is properly set."""
    print("Production Configuration Verification")
    print("=" * 40)
    
    # Load environment
    env_path = Path(".env.production")
    if env_path.exists():
        from dotenv import load_dotenv
        load_dotenv(env_path)
        print(f"✓ Loaded environment from {env_path}\n")
    else:
        print(f"⚠️  {env_path} not found, using system environment\n")
    
    all_good = True
    
    # Check critical environment variables
    print("Critical Settings:")
    critical_vars = [
        "ENVIRONMENT",
        "JWT_SECRET",
        "DATABASE_URL",
        "REDIS_URL",
    ]
    
    for var in critical_vars:
        ok, message = check_env_var(var)
        print(message)
        if not ok:
            all_good = False
    
    # Check API keys
    print("\nAPI Keys:")
    api_keys = [
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "GOOGLE_API_KEY",
    ]
    
    has_api_key = False
    for var in api_keys:
        ok, message = check_env_var(var, required=False)
        print(message)
        if ok and os.environ.get(var):
            has_api_key = True
    
    if not has_api_key:
        print("❌ No API keys configured - at least one is required")
        all_good = False
    
    # Check security settings
    print("\nSecurity Settings:")
    security_vars = [
        "ALLOWED_HOSTS",
        "CORS_ORIGINS",
        "HSTS_MAX_AGE",
        "CSP_POLICY",
    ]
    
    for var in security_vars:
        ok, message = check_env_var(var, required=False)
        print(message)
    
    # Check monitoring
    print("\nMonitoring Settings:")
    monitoring_vars = [
        "SENTRY_DSN",
        "LOG_LEVEL",
        "LOG_FILE_PATH",
        "ENABLE_METRICS",
    ]
    
    for var in monitoring_vars:
        ok, message = check_env_var(var, required=False)
        print(message)
    
    # Verify specific configurations
    print("\nConfiguration Validation:")
    
    # Check environment
    env = os.environ.get("ENVIRONMENT")
    if env != "production":
        print(f"❌ ENVIRONMENT is '{env}', should be 'production'")
        all_good = False
    else:
        print("✓ ENVIRONMENT is set to production")
    
    # Check debug mode
    debug = os.environ.get("DEBUG", "").lower()
    if debug in ["true", "1", "yes"]:
        print("❌ DEBUG is enabled in production!")
        all_good = False
    else:
        print("✓ DEBUG is disabled")
    
    # Check mock mode
    mock = os.environ.get("USE_MOCK", "").lower()
    if mock in ["true", "1", "yes"]:
        print("❌ USE_MOCK is enabled in production!")
        all_good = False
    else:
        print("✓ USE_MOCK is disabled")
    
    # Test database connection
    print("\nTesting Connections:")
    
    try:
        from backend.config_database import get_database_config, test_database_connection
        db_config = get_database_config()
        if test_database_connection(db_config):
            print("✓ Database connection successful")
        else:
            print("❌ Database connection failed")
            all_good = False
    except Exception as e:
        print(f"❌ Database connection error: {str(e)}")
        all_good = False
    
    # Test Redis connection
    try:
        from backend.config_redis import get_redis_config, test_redis_connection
        redis_config = get_redis_config()
        if test_redis_connection(redis_config):
            print("✓ Redis connection successful")
        else:
            print("❌ Redis connection failed")
            all_good = False
    except Exception as e:
        print(f"❌ Redis connection error: {str(e)}")
        all_good = False
    
    # Final result
    print("\n" + "=" * 40)
    if all_good:
        print("✅ Production configuration is valid!")
        print("You can proceed with deployment.")
    else:
        print("❌ Production configuration has issues!")
        print("Please fix the errors above before deploying.")
    
    return all_good


if __name__ == "__main__":
    success = verify_production_config()
    sys.exit(0 if success else 1)