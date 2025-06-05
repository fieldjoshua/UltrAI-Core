#!/usr/bin/env python3
"""
Create a test API key for development testing of the orchestrator endpoints
"""

import json
import os
import sys
from datetime import datetime, timedelta

# Add parent directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../..'))

from backend.utils.api_key_manager import api_key_manager, ApiKeyScope
from backend.database import get_db

def create_test_api_key():
    """Create a test API key with full permissions"""
    try:
        # Generate a new API key
        api_key, api_key_obj = api_key_manager.generate_api_key(
            user_id="test-orchestrator-user",
            name="Test Orchestrator Key",
            scope=ApiKeyScope.READ_WRITE,
            expires_in_days=30
        )
        
        print(f"✅ Created test API key:")
        print(f"   Key: {api_key}")
        print(f"   User ID: {api_key_obj.user_id}")
        print(f"   Scope: {api_key_obj.scope}")
        print(f"   Expires: {api_key_obj.expires_at}")
        print(f"\n📋 Use this in your requests:")
        print(f'   curl -H "X-API-Key: {api_key}" http://localhost:8081/api/orchestrator/models')
        
        # Save to a file for easy reference
        with open('.test_api_key', 'w') as f:
            json.dump({
                'api_key': api_key,
                'user_id': api_key_obj.user_id,
                'created_at': datetime.utcnow().isoformat(),
                'expires_at': api_key_obj.expires_at.isoformat() if api_key_obj.expires_at else None
            }, f, indent=2)
        print(f"\n💾 Saved to .test_api_key file")
        
        return api_key
        
    except Exception as e:
        print(f"❌ Error creating API key: {e}")
        return None

if __name__ == "__main__":
    create_test_api_key()