#!/usr/bin/env python3
"""Setup production configuration helper script."""

import os
import sys
import shutil
from pathlib import Path
import secrets
import base64


def generate_secret(length: int = 64) -> str:
    """Generate a cryptographically secure secret."""
    random_bytes = secrets.token_bytes(length)
    return base64.b64encode(random_bytes).decode('utf-8')


def setup_production_config():
    """Help set up production configuration."""
    print("Ultra Production Configuration Setup")
    print("=" * 40)
    
    # Check if template exists
    template_path = Path(".env.production.template")
    if not template_path.exists():
        print("ERROR: .env.production.template not found!")
        return
    
    # Check if production config already exists
    prod_path = Path(".env.production")
    if prod_path.exists():
        response = input(".env.production already exists. Overwrite? (y/N): ")
        if response.lower() != 'y':
            print("Aborting...")
            return
        
        # Backup existing file
        backup_path = Path(f".env.production.backup.{int(Path.ctime(prod_path))}")
        shutil.copy(prod_path, backup_path)
        print(f"Backed up existing config to: {backup_path}")
    
    # Copy template
    shutil.copy(template_path, prod_path)
    
    # Read the file
    with open(prod_path, 'r') as f:
        content = f.read()
    
    # Generate secrets
    jwt_secret = generate_secret()
    session_secret = generate_secret(32)
    
    # Replace placeholders
    content = content.replace("<REPLACE_WITH_GENERATED_SECRET>", jwt_secret)
    content = content.replace("<REPLACE_WITH_GENERATED_SECRET>", session_secret)
    
    # Write back
    with open(prod_path, 'w') as f:
        f.write(content)
    
    print("\nGenerated secrets:")
    print(f"JWT_SECRET: {jwt_secret[:20]}... (truncated)")
    print(f"SESSION_SECRET: {session_secret[:20]}... (truncated)")
    
    print("\nNext steps:")
    print("1. Edit .env.production and replace placeholder values")
    print("2. Add your database connection string")
    print("3. Add your Redis connection string")
    print("4. Add API keys for LLM providers")
    print("5. Configure your domain and CORS settings")
    print("6. Set up SMTP credentials for email")
    print("\nIMPORTANT: Never commit .env.production to version control!")
    
    # Add to .gitignore if not already there
    gitignore_path = Path(".gitignore")
    if gitignore_path.exists():
        with open(gitignore_path, 'r') as f:
            if ".env.production" not in f.read():
                with open(gitignore_path, 'a') as f:
                    f.write("\n# Production environment\n.env.production\njwt_secret.txt\n")
                print("\nAdded .env.production to .gitignore")


if __name__ == "__main__":
    setup_production_config()