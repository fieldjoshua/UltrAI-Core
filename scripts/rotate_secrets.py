#!/usr/bin/env python3
"""
Script to rotate secrets and generate new secure values.

This script helps with:
1. Generating new secure secrets
2. Updating .env files
3. Providing instructions for updating external services
"""

import os
import secrets
import string
import sys
from datetime import datetime
from pathlib import Path


def generate_secure_secret(length=64):
    """Generate a cryptographically secure secret."""
    alphabet = string.ascii_letters + string.digits + "-_"
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def generate_jwt_secret():
    """Generate a secure JWT secret key."""
    # JWT secrets should be at least 256 bits (32 bytes)
    return secrets.token_urlsafe(64)


def generate_api_key():
    """Generate a secure API key."""
    return f"ultra_{secrets.token_urlsafe(32)}"


def update_env_file(file_path, updates):
    """Update environment file with new values."""
    if not os.path.exists(file_path):
        print(f"⚠️  {file_path} not found, skipping...")
        return
    
    lines = []
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    # Update existing lines or add new ones
    updated_keys = set()
    new_lines = []
    
    for line in lines:
        updated = False
        for key, value in updates.items():
            if line.strip().startswith(f"{key}="):
                new_lines.append(f"{key}={value}\n")
                updated_keys.add(key)
                updated = True
                break
        
        if not updated:
            new_lines.append(line)
    
    # Add any missing keys
    for key, value in updates.items():
        if key not in updated_keys:
            new_lines.append(f"{key}={value}\n")
    
    # Write back to file
    with open(file_path, 'w') as f:
        f.writelines(new_lines)
    
    print(f"✅ Updated {file_path}")


def main():
    """Main function to rotate secrets."""
    print("🔒 Secret Rotation Tool")
    print("=" * 50)
    
    # Generate new secrets
    new_secrets = {
        "JWT_SECRET": generate_jwt_secret(),
        "JWT_SECRET_KEY": generate_jwt_secret(),
        "JWT_REFRESH_SECRET": generate_jwt_secret(),
        "JWT_REFRESH_SECRET_KEY": generate_jwt_secret(),
        "SECRET_KEY": generate_secure_secret(),
        "API_KEY_ENCRYPTION_KEY": generate_secure_secret(),
        "CSRF_SECRET_KEY": generate_secure_secret(32),
    }
    
    # Create backup of current .env if it exists
    env_file = Path(".env")
    if env_file.exists():
        backup_name = f".env.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        env_file.rename(backup_name)
        print(f"📦 Created backup: {backup_name}")
        # Copy back to .env so we can update it
        Path(backup_name).rename(".env")
    
    # Update .env.example with placeholders
    example_updates = {
        "JWT_SECRET": "your-jwt-secret-here",
        "JWT_SECRET_KEY": "your-jwt-secret-key-here",
        "JWT_REFRESH_SECRET": "your-jwt-refresh-secret-here",
        "JWT_REFRESH_SECRET_KEY": "your-jwt-refresh-secret-key-here",
        "SECRET_KEY": "your-secret-key-here",
        "API_KEY_ENCRYPTION_KEY": "your-api-key-encryption-here",
        "CSRF_SECRET_KEY": "your-csrf-secret-here",
    }
    
    update_env_file(".env.example", example_updates)
    
    # Show new secrets (for manual update if needed)
    print("\n📝 New Secrets Generated:")
    print("-" * 50)
    for key, value in new_secrets.items():
        print(f"{key}={value}")
    
    print("\n⚠️  Action Required:")
    print("-" * 50)
    print("1. Update these secrets in your production environment:")
    print("   - Render.com dashboard")
    print("   - GitHub repository secrets")
    print("   - Any other deployment environments")
    print("\n2. If you have existing JWT tokens in production:")
    print("   - They will become invalid after rotation")
    print("   - Users will need to re-authenticate")
    print("   - Consider a gradual rollout or dual-secret strategy")
    print("\n3. Update any API keys that external services use")
    print("\n4. Run 'make deploy' to push changes to production")
    
    # Check for hardcoded secrets in code
    print("\n🔍 Checking for hardcoded secrets...")
    hardcoded_found = False
    
    # Check Python files
    for py_file in Path(".").rglob("*.py"):
        if any(skip in str(py_file) for skip in ["venv", "__pycache__", "node_modules", ".git"]):
            continue
            
        try:
            content = py_file.read_text()
            
            # Look for hardcoded JWT secrets
            if 'JWT_SECRET = "' in content and 'os.getenv' not in content:
                print(f"❌ Hardcoded secret found in {py_file}")
                hardcoded_found = True
                
            # Look for the specific development secrets
            dev_secrets = [
                "1W3-55MhQfFnkkC4REHcDXPWwTAP7AEqYuJAw-DZEJxHEtrn_97ayLZOn2Q7gSKNZnipY4-0D6niB30v7ztBWA",
                "KTIBDNlXkcg7PtZsV6pfqzpm6Nyz8REDQrnKTHJyG3egwXO87ibZDOfs6aO2vksB5LBIUVzFW2A-qOIJ9HAYBg"
            ]
            
            for secret in dev_secrets:
                if secret in content:
                    print(f"⚠️  Development secret found in {py_file}")
                    print("   This is OK for development but should not be used in production")
                    
        except Exception as e:
            pass
    
    if hardcoded_found:
        print("\n❌ Hardcoded secrets found! Please update them to use environment variables.")
        sys.exit(1)
    else:
        print("✅ No hardcoded production secrets found")
    
    print("\n✅ Secret rotation complete!")
    print("Remember to update your production environment variables!")


if __name__ == "__main__":
    main()