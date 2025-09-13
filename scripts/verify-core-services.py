#!/usr/bin/env python3
"""
Verify that core services work without financial features.
"""

import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set environment variables before importing
os.environ["ENABLE_BILLING"] = "false"
os.environ["ENABLE_PRICING"] = "false"
os.environ["ENVIRONMENT"] = "development"
os.environ["USE_MOCK"] = "true"

from app.services.orchestration_service import OrchestrationService
from app.services.model_registry import ModelRegistry
from app.services.health_service import HealthService
from app.config import Config


def verify_config():
    """Verify configuration is set correctly."""
    print("=== Configuration Check ===")
    print(f"ENABLE_BILLING: {Config.ENABLE_BILLING}")
    print(f"ENABLE_PRICING: {Config.ENABLE_PRICING}")
    print(f"USE_MOCK: {Config.USE_MOCK}")
    print(f"ENVIRONMENT: {Config.ENVIRONMENT}")
    
    assert Config.ENABLE_BILLING is False, "Billing should be disabled"
    assert Config.ENABLE_PRICING is False, "Pricing should be disabled"
    print("✅ Financial features disabled\n")


def verify_orchestration_service():
    """Verify orchestration service works without transaction service."""
    print("=== Orchestration Service Check ===")
    
    try:
        # Create orchestration service
        model_registry = ModelRegistry()
        orchestrator = OrchestrationService(model_registry=model_registry)
        
        # Check transaction service is None
        print(f"Transaction service: {orchestrator.transaction_service}")
        assert orchestrator.transaction_service is None, "Transaction service should be None"
        
        print("✅ Orchestration service initialized without transaction service\n")
        return True
    except Exception as e:
        print(f"❌ Failed to initialize orchestration service: {e}\n")
        return False


def verify_health_service():
    """Verify health service works."""
    print("=== Health Service Check ===")
    
    try:
        health_service = HealthService()
        health_status = health_service.get_health_status()
        
        print(f"Service status: {health_status.get('status', 'unknown')}")
        print(f"Environment: {health_status.get('environment', 'unknown')}")
        print("✅ Health service working\n")
        return True
    except Exception as e:
        print(f"❌ Failed to check health service: {e}\n")
        return False


def verify_imports():
    """Verify all core imports work."""
    print("=== Import Check ===")
    
    imports_to_check = [
        ("LLM Adapters", "app.services.llm_adapters"),
        ("Cache Service", "app.services.cache_service"),
        ("Auth Service", "app.services.auth_service"),
        ("Model Registry", "app.services.model_registry"),
        ("Output Formatter", "app.services.output_formatter"),
        ("Recovery Service", "app.services.recovery_service"),
    ]
    
    all_passed = True
    for name, module_path in imports_to_check:
        try:
            __import__(module_path)
            print(f"✅ {name}")
        except Exception as e:
            print(f"❌ {name}: {e}")
            all_passed = False
    
    print()
    return all_passed


def main():
    """Run all verification checks."""
    print("\n🔍 Verifying Core Services Without Financial Features\n")
    
    results = {
        "Config": verify_config(),
        "Imports": verify_imports(),
        "Orchestration": verify_orchestration_service(),
        "Health": verify_health_service(),
    }
    
    print("=== Summary ===")
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for check, result in results.items():
        status = "✅" if result else "❌"
        print(f"{status} {check}")
    
    print(f"\nPassed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 All core services working without financial features!")
        return 0
    else:
        print("\n⚠️ Some services need attention")
        return 1


if __name__ == "__main__":
    exit(main())