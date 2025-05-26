"""Test minimal requirements work correctly"""

import sys


def test_imports():
    """Test that all required imports work"""
    errors = []

    required_imports = [
        ("fastapi", "FastAPI"),
        ("uvicorn", None),
        ("gunicorn", None),
        ("pydantic", "BaseModel"),
        ("sqlalchemy", "create_engine"),
        ("alembic", None),
        ("psycopg2", None),
        ("jwt", None),
        ("passlib.context", "CryptContext"),
        ("jose", "jwt"),
        ("bcrypt", None),
        ("email_validator", "validate_email"),
        ("openai", None),
        ("anthropic", None),
        ("google.generativeai", None),
        ("httpx", None),
        ("aiohttp", None),
        ("sse_starlette", "EventSourceResponse"),
        ("dotenv", "load_dotenv"),
        ("yaml", None),
        ("tenacity", "retry"),
        ("backoff", None),
        ("cryptography", None),
        ("redis", None),
        ("diskcache", None),
        ("magic", None),
        ("chardet", None),
    ]

    for module_name, attr in required_imports:
        try:
            if "." in module_name:
                parts = module_name.split(".")
                module = __import__(parts[0])
                for part in parts[1:]:
                    module = getattr(module, part)
            else:
                module = __import__(module_name)

            if attr:
                getattr(module, attr)

            print(f"✓ {module_name}")
        except ImportError as e:
            errors.append(f"✗ {module_name}: {str(e)}")
            print(f"✗ {module_name}: {str(e)}")

    return errors


if __name__ == "__main__":
    print("Testing minimal requirements...")
    print("-" * 40)

    errors = test_imports()

    print("-" * 40)
    if errors:
        print(f"\nFailed {len(errors)} imports:")
        for error in errors:
            print(error)
        sys.exit(1)
    else:
        print("\nAll imports successful! ✓")
        print("Minimal requirements are complete.")
