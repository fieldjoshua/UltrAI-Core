#!/usr/bin/env python3
"""Generate a secure JWT secret for production use."""

import secrets
import sys
import base64


def generate_jwt_secret(length: int = 64) -> str:
    """Generate a cryptographically secure JWT secret.
    
    Args:
        length: The number of random bytes to generate (default: 64)
    
    Returns:
        A base64-encoded string suitable for use as a JWT secret
    """
    # Generate random bytes
    random_bytes = secrets.token_bytes(length)
    
    # Encode to base64 for use as a string
    secret = base64.b64encode(random_bytes).decode('utf-8')
    
    return secret


def main():
    """Generate and display a JWT secret."""
    # Generate the secret
    secret = generate_jwt_secret()
    
    print("Generated JWT Secret:")
    print("=" * 50)
    print(secret)
    print("=" * 50)
    print()
    print("To use this secret:")
    print("1. Add to your .env.production file:")
    print(f"   JWT_SECRET={secret}")
    print()
    print("2. Or export as environment variable:")
    print(f"   export JWT_SECRET='{secret}'")
    print()
    print("IMPORTANT: Keep this secret secure and never commit it to version control!")
    
    # Also write to a file
    with open("jwt_secret.txt", "w") as f:
        f.write(f"JWT_SECRET={secret}\n")
    
    print()
    print("Secret also saved to: jwt_secret.txt")
    print("Remember to delete this file after copying the secret to your secure configuration!")


if __name__ == "__main__":
    main()