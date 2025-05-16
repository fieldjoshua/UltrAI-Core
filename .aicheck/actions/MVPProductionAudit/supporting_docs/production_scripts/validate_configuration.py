#!/usr/bin/env python3
"""
Configuration Validation Script for Ultra MVP
Validates all required configuration and environment variables
"""

import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple


class ConfigValidator:
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent.parent.parent.parent
        self.results = {}
        self.errors = []
        self.warnings = []

    def check_file_exists(self, file_path: str) -> bool:
        """Check if a file exists relative to base directory"""
        full_path = self.base_dir / file_path
        return full_path.exists()

    def validate_env_file(self) -> Tuple[bool, List[str]]:
        """Validate .env file contains required variables"""
        print("\n=== Validating Environment File ===")

        required_vars = [
            "ENVIRONMENT",
            "API_PORT",
            "JWT_SECRET",
            "DATABASE_URL",
            "SECRET_KEY",
            "API_KEY_ENCRYPTION_KEY",
        ]

        optional_vars = [
            "OPENAI_API_KEY",
            "ANTHROPIC_API_KEY",
            "GOOGLE_API_KEY",
            "MISTRAL_API_KEY",
            "SENTRY_DSN",
            "REDIS_URL",
        ]

        env_file = self.base_dir / ".env"
        if not env_file.exists():
            self.errors.append(".env file not found")
            return False, self.errors

        with open(env_file) as f:
            env_content = f.read()

        missing_required = []
        missing_optional = []

        for var in required_vars:
            if not re.search(f"^{var}=", env_content, re.MULTILINE):
                missing_required.append(var)

        for var in optional_vars:
            if not re.search(f"^{var}=", env_content, re.MULTILINE):
                missing_optional.append(var)

        if missing_required:
            self.errors.append(
                f"Missing required variables: {', '.join(missing_required)}"
            )

        if missing_optional:
            self.warnings.append(
                f"Missing optional variables: {', '.join(missing_optional)}"
            )

        # Check for insecure values
        insecure_patterns = [
            ("replace_with_secure_key", "Insecure placeholder key found"),
            ("your-.*-key-here", "Placeholder API key found"),
            ("development-secret", "Development secret in production"),
        ]

        for pattern, message in insecure_patterns:
            if re.search(pattern, env_content):
                self.warnings.append(message)

        return len(missing_required) == 0, self.errors

    def validate_docker_config(self) -> Tuple[bool, List[str]]:
        """Validate Docker configuration files"""
        print("\n=== Validating Docker Configuration ===")

        required_files = ["docker-compose.yml", "Dockerfile", ".dockerignore"]

        missing_files = []
        for file in required_files:
            if not self.check_file_exists(file):
                missing_files.append(file)

        if missing_files:
            self.errors.append(f"Missing Docker files: {', '.join(missing_files)}")
            return False, self.errors

        # Validate docker-compose.yml
        compose_file = self.base_dir / "docker-compose.yml"
        with open(compose_file) as f:
            compose_content = f.read()

        required_services = ["backend", "postgres", "redis"]
        for service in required_services:
            if service not in compose_content:
                self.errors.append(f"Missing service in docker-compose.yml: {service}")

        return len(self.errors) == 0, self.errors

    def validate_dependencies(self) -> Tuple[bool, List[str]]:
        """Validate Python dependencies"""
        print("\n=== Validating Dependencies ===")

        requirements_file = self.base_dir / "requirements.txt"
        if not requirements_file.exists():
            self.errors.append("requirements.txt not found")
            return False, self.errors

        with open(requirements_file) as f:
            requirements = f.read()

        critical_packages = [
            "fastapi",
            "uvicorn",
            "pydantic",
            "sqlalchemy",
            "alembic",
            "redis",
            "PyJWT",
        ]

        missing_packages = []
        for package in critical_packages:
            if package.lower() not in requirements.lower():
                missing_packages.append(package)

        if missing_packages:
            self.errors.append(
                f"Missing critical packages: {', '.join(missing_packages)}"
            )

        return len(missing_packages) == 0, self.errors

    def validate_security_config(self) -> Tuple[bool, List[str]]:
        """Validate security configuration"""
        print("\n=== Validating Security Configuration ===")

        # Check for HTTPS redirect in production
        env_file = self.base_dir / ".env"
        if env_file.exists():
            with open(env_file) as f:
                env_content = f.read()

            if "ENVIRONMENT=production" in env_content:
                if "ENABLE_HTTPS_REDIRECT=false" in env_content:
                    self.warnings.append("HTTPS redirect disabled in production")

                if "DEBUG=true" in env_content:
                    self.errors.append("Debug mode enabled in production")

        # Check for secure headers middleware
        app_file = self.base_dir / "backend" / "app.py"
        if app_file.exists():
            with open(app_file) as f:
                app_content = f.read()

            if "SecurityHeadersMiddleware" not in app_content:
                self.warnings.append("Security headers middleware not found")

        return len(self.errors) == 0, self.errors

    def validate_database_config(self) -> Tuple[bool, List[str]]:
        """Validate database configuration"""
        print("\n=== Validating Database Configuration ===")

        # Check for migration files
        migrations_dir = (
            self.base_dir / "backend" / "database" / "migrations" / "versions"
        )
        if not migrations_dir.exists():
            self.warnings.append("No database migrations found")
        else:
            migration_files = list(migrations_dir.glob("*.py"))
            if len(migration_files) == 0:
                self.warnings.append("No migration files found")
            else:
                print(f"Found {len(migration_files)} migration files")

        return True, []

    def generate_report(self):
        """Generate validation report"""
        print("\n" + "=" * 50)
        print("CONFIGURATION VALIDATION REPORT")
        print("=" * 50)

        total_errors = len(self.errors)
        total_warnings = len(self.warnings)

        if total_errors == 0:
            print("\n✅ Configuration is VALID")
        else:
            print("\n❌ Configuration has ERRORS")

        print(f"\nErrors: {total_errors}")
        print(f"Warnings: {total_warnings}")

        if self.errors:
            print("\n🔴 ERRORS (Must Fix):")
            for error in self.errors:
                print(f"  - {error}")

        if self.warnings:
            print("\n⚠️  WARNINGS (Should Review):")
            for warning in self.warnings:
                print(f"  - {warning}")

        print("\n" + "=" * 50)

        return total_errors == 0

    def run(self) -> bool:
        """Run all validation checks"""
        print("Ultra MVP Configuration Validator")
        print("================================")

        checks = [
            ("Environment File", self.validate_env_file),
            ("Docker Configuration", self.validate_docker_config),
            ("Dependencies", self.validate_dependencies),
            ("Security Configuration", self.validate_security_config),
            ("Database Configuration", self.validate_database_config),
        ]

        for name, check_func in checks:
            try:
                success, errors = check_func()
                status = "✅ PASS" if success else "❌ FAIL"
                print(f"{name}: {status}")
            except Exception as e:
                print(f"{name}: ❌ ERROR - {str(e)}")
                self.errors.append(f"{name} check failed: {str(e)}")

        return self.generate_report()


if __name__ == "__main__":
    validator = ConfigValidator()
    success = validator.run()
    sys.exit(0 if success else 1)
