#!/usr/bin/env python3
"""
Production Readiness Check for Ultra MVP
Validates configuration and dependencies
"""
import json
import os
import sys
from pathlib import Path


class ProductionReadinessChecker:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.checks = {
            "core_files": True,
            "environment": True,
            "dependencies": True,
            "docker": True,
            "security": True,
        }

    def check_core_files(self):
        """Check if core files exist"""
        print("\n=== Checking Core Files ===")
        required_files = [
            "backend/app.py",
            "frontend/package.json",
            "docker-compose.yml",
            "requirements.txt",
            ".env.production",
            ".env.example",
        ]

        all_exist = True
        for file_path in required_files:
            full_path = self.base_dir / file_path
            exists = full_path.exists()
            status = "✅" if exists else "❌"
            print(f"{status} {file_path}")
            if not exists:
                all_exist = False

        self.checks["core_files"] = all_exist
        return all_exist

    def check_environment(self):
        """Check environment configuration"""
        print("\n=== Checking Environment Configuration ===")

        # Check for .env file
        env_file = self.base_dir / ".env"
        env_exists = env_file.exists()
        print(f"{'✅' if env_exists else '❌'} .env file exists")

        # Check for required environment variables
        required_vars = ["ENVIRONMENT", "API_PORT", "JWT_SECRET", "DATABASE_URL"]

        if env_exists:
            with open(env_file) as f:
                env_content = f.read()

            missing_vars = []
            for var in required_vars:
                if var not in env_content:
                    missing_vars.append(var)

            if missing_vars:
                print(f"❌ Missing variables: {', '.join(missing_vars)}")
                self.checks["environment"] = False
            else:
                print("✅ All required variables present")
        else:
            print("❌ No .env file found")
            self.checks["environment"] = False

        return self.checks["environment"]

    def check_dependencies(self):
        """Check Python dependencies"""
        print("\n=== Checking Dependencies ===")

        try:
            import fastapi

            print("✅ FastAPI installed")
        except ImportError:
            print("❌ FastAPI not installed")
            self.checks["dependencies"] = False

        try:
            import uvicorn

            print("✅ Uvicorn installed")
        except ImportError:
            print("❌ Uvicorn not installed")
            self.checks["dependencies"] = False

        try:
            import jwt

            print("✅ PyJWT installed")
        except ImportError:
            print("❌ PyJWT not installed")
            self.checks["dependencies"] = False

        return self.checks["dependencies"]

    def check_docker(self):
        """Check Docker configuration"""
        print("\n=== Checking Docker Configuration ===")

        docker_compose = self.base_dir / "docker-compose.yml"
        if docker_compose.exists():
            print("✅ docker-compose.yml exists")

            # Check for Dockerfile
            dockerfile = self.base_dir / "Dockerfile"
            if dockerfile.exists():
                print("✅ Dockerfile exists")
            else:
                print("❌ Dockerfile not found")
                self.checks["docker"] = False
        else:
            print("❌ docker-compose.yml not found")
            self.checks["docker"] = False

        return self.checks["docker"]

    def check_security(self):
        """Check security configuration"""
        print("\n=== Checking Security Configuration ===")

        # Check for secure defaults
        env_example = self.base_dir / ".env.example"
        if env_example.exists():
            with open(env_example) as f:
                content = f.read()

            insecure_values = [
                "replace_with_secure_key",
                "your-api-key-here",
                "development-secret",
            ]

            has_insecure = False
            for value in insecure_values:
                if value in content:
                    has_insecure = True

            if has_insecure:
                print("⚠️  Example file contains placeholder values (expected)")
            else:
                print("✅ No obvious security issues in example")

            # Check production config
            env_prod = self.base_dir / ".env.production"
            if env_prod.exists():
                print("✅ Production environment file exists")
            else:
                print("⚠️  No .env.production file (create from .env.example)")
        else:
            print("❌ No .env.example file")
            self.checks["security"] = False

        return self.checks["security"]

    def generate_report(self):
        """Generate production readiness report"""
        print("\n" + "=" * 50)
        print("PRODUCTION READINESS REPORT")
        print("=" * 50)

        all_passed = all(self.checks.values())

        for check_name, passed in self.checks.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"{check_name.replace('_', ' ').title()}: {status}")

        print("\n" + "=" * 50)
        if all_passed:
            print("✅ SYSTEM IS PRODUCTION READY")
            print("\nNext steps:")
            print("1. Configure production environment variables")
            print("2. Set up production database")
            print("3. Configure monitoring (Sentry)")
            print("4. Deploy with Docker Compose")
        else:
            print("❌ SYSTEM NEEDS CONFIGURATION")
            print("\nRequired actions:")
            if not self.checks["core_files"]:
                print("- Ensure all core files are present")
            if not self.checks["environment"]:
                print("- Create and configure .env file")
            if not self.checks["dependencies"]:
                print("- Install missing dependencies: pip install -r requirements.txt")
            if not self.checks["docker"]:
                print("- Ensure Docker files are present")
            if not self.checks["security"]:
                print("- Review security configuration")

        print("=" * 50)

    def run(self):
        """Run all checks"""
        print("Ultra MVP Production Readiness Check")
        print("==================================")

        self.check_core_files()
        self.check_environment()
        self.check_dependencies()
        self.check_docker()
        self.check_security()

        self.generate_report()


if __name__ == "__main__":
    checker = ProductionReadinessChecker()
    checker.run()
