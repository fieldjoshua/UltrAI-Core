"""
Debug environment variables route for troubleshooting Render configuration.
SECURITY NOTE: This endpoint filters sensitive data and should be disabled in production.
"""

import os
import re
from typing import Dict, List
from fastapi import APIRouter

router = APIRouter(tags=["debug"])


def filter_sensitive_env_vars(env_vars: Dict[str, str]) -> Dict[str, str]:
    """
    Filter environment variables to hide sensitive information.
    
    Args:
        env_vars: Dictionary of environment variables
        
    Returns:
        Filtered dictionary with sensitive values masked
    """
    # Patterns that indicate sensitive information
    sensitive_patterns = [
        r".*API_KEY.*",
        r".*SECRET.*", 
        r".*PASSWORD.*",
        r".*TOKEN.*",
        r".*PRIVATE.*",
        r".*CREDENTIAL.*",
    ]
    
    # Compile patterns for efficiency
    sensitive_regexes = [re.compile(pattern, re.IGNORECASE) for pattern in sensitive_patterns]
    
    filtered_vars = {}
    for key, value in env_vars.items():
        # Check if this key matches any sensitive pattern
        is_sensitive = any(regex.match(key) for regex in sensitive_regexes)
        
        if is_sensitive:
            # Mask sensitive values but show they exist
            if value:
                filtered_vars[key] = f"***MASKED*** (length: {len(value)})"
            else:
                filtered_vars[key] = "***EMPTY***"
        else:
            # Show non-sensitive values
            filtered_vars[key] = value
    
    return filtered_vars


@router.get("/debug/environment-variables")
async def get_environment_variables():
    """
    Get filtered environment variables for debugging Render configuration.
    
    This endpoint is for troubleshooting multi-provider model issues.
    Sensitive values are masked for security.
    """
    # Get all environment variables
    all_env_vars = dict(os.environ)
    
    # Filter sensitive information
    filtered_env_vars = filter_sensitive_env_vars(all_env_vars)
    
    # Categorize variables for easier analysis
    categories = {
        "database_related": {},
        "llm_provider_related": {},
        "render_specific": {},
        "application_config": {},
        "system_variables": {},
        "other": {}
    }
    
    for key, value in filtered_env_vars.items():
        key_upper = key.upper()
        
        if any(keyword in key_upper for keyword in ["DB", "DATABASE", "POSTGRES", "SQL"]):
            categories["database_related"][key] = value
        elif any(keyword in key_upper for keyword in ["API_KEY", "OPENAI", "ANTHROPIC", "GOOGLE", "HUGGINGFACE"]):
            categories["llm_provider_related"][key] = value
        elif any(keyword in key_upper for keyword in ["RENDER", "PORT", "HOST"]):
            categories["render_specific"][key] = value
        elif any(keyword in key_upper for keyword in ["ENVIRONMENT", "DEBUG", "ENABLE_", "DEFAULT_", "MOCK"]):
            categories["application_config"][key] = value
        elif any(keyword in key_upper for keyword in ["PATH", "HOME", "USER", "SHELL", "LANG", "PWD"]):
            categories["system_variables"][key] = value
        else:
            categories["other"][key] = value
    
    # Count variables by category
    category_counts = {cat: len(vars_dict) for cat, vars_dict in categories.items()}
    
    return {
        "total_environment_variables": len(filtered_env_vars),
        "category_counts": category_counts,
        "categorized_variables": categories,
        "database_troubleshooting": {
            "checked_variable_names": [
                "DATABASE_URL",
                "POSTGRES_URL", 
                "POSTGRESQL_URL",
                "DATABASE_CONNECTION_STRING",
                "DB_URL"
            ],
            "found_database_vars": list(categories["database_related"].keys()),
            "analysis": "Check if any database URL variables are present"
        },
        "llm_provider_troubleshooting": {
            "expected_api_keys": [
                "OPENAI_API_KEY",
                "ANTHROPIC_API_KEY", 
                "GOOGLE_API_KEY",
                "HUGGINGFACE_API_KEY"
            ],
            "found_provider_vars": list(categories["llm_provider_related"].keys()),
            "analysis": "Verify all LLM provider API keys are available"
        }
    }


@router.get("/debug/database-config")
async def get_database_configuration():
    """
    Get specific database configuration details for troubleshooting.
    """
    # Check for various database URL environment variables
    possible_db_url_vars = [
        "DATABASE_URL",
        "POSTGRES_URL", 
        "POSTGRESQL_URL",
        "DATABASE_CONNECTION_STRING",
        "DB_URL"
    ]
    
    db_url_status = {}
    found_db_url = None
    
    for var_name in possible_db_url_vars:
        value = os.environ.get(var_name)
        if value:
            db_url_status[var_name] = {
                "present": True,
                "length": len(value),
                "starts_with": value[:20] + "..." if len(value) > 20 else value,
                "contains_localhost": "localhost" in value.lower() or "127.0.0.1" in value
            }
            if not found_db_url:
                found_db_url = var_name
        else:
            db_url_status[var_name] = {"present": False}
    
    # Check individual database variables
    individual_db_vars = {
        "DB_HOST": os.environ.get("DB_HOST", "NOT_SET"),
        "DB_PORT": os.environ.get("DB_PORT", "NOT_SET"),
        "DB_NAME": os.environ.get("DB_NAME", "NOT_SET"),
        "DB_USER": os.environ.get("DB_USER", "NOT_SET"),
        "DB_PASSWORD": "***MASKED***" if os.environ.get("DB_PASSWORD") else "NOT_SET"
    }
    
    return {
        "database_url_variables": db_url_status,
        "primary_database_url": found_db_url,
        "individual_database_variables": individual_db_vars,
        "render_yaml_configuration": {
            "expected_variable": "DATABASE_URL",
            "expected_source": "fromDatabase.ultrai-db.connectionString",
            "status": "Check if Render is providing this variable"
        }
    }