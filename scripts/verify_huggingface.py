#!/usr/bin/env python3
"""
Verify HuggingFace configuration and model availability.
"""

import os
import asyncio
import httpx


async def check_huggingface():
    """Check HuggingFace configuration."""
    print("🔍 Checking HuggingFace configuration...")
    
    # Check environment variable
    hf_key = os.getenv("HUGGINGFACE_API_KEY")
    if hf_key:
        print(f"✅ HUGGINGFACE_API_KEY is set (length: {len(hf_key)})")
    else:
        print("❌ HUGGINGFACE_API_KEY is not set")
    
    # Check production API
    print("\n📡 Checking production API...")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get("https://ultrai-core.onrender.com/api/available-models")
            data = response.json()
            
            # Count models by provider
            model_count = {}
            if data.get("models"):
                for model in data["models"]:
                    provider = model.get("provider", "unknown")
                    model_count[provider] = model_count.get(provider, 0) + 1
            
            print(f"📊 Model counts by provider:")
            for provider, count in model_count.items():
                print(f"  - {provider}: {count} models")
            
            # Check for HuggingFace models
            if "huggingface" in model_count:
                print(f"✅ HuggingFace models are available in production")
            else:
                print("❌ No HuggingFace models found in production")
                
        except Exception as e:
            print(f"❌ Error checking production API: {e}")


if __name__ == "__main__":
    asyncio.run(check_huggingface())