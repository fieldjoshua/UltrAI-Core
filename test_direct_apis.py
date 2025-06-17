#!/usr/bin/env python3
"""
Direct API testing script to verify LLM provider configurations.
This script tests each provider's API directly to identify issues with model names,
authentication, and request formats.
"""

import asyncio
import httpx
import json
import os

async def test_anthropic_api():
    """Test Anthropic Claude API directly."""
    print("Testing Anthropic Claude API...")
    
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not found")
        return False
    
    print(f"✅ API key present (length: {len(api_key)})")
    
    # Test with different model names
    model_names = [
        "claude-3-sonnet",
        "claude-3-sonnet-20240229", 
        "claude-3-5-sonnet-20241022"
    ]
    
    for model in model_names:
        print(f"\n  Testing model: {model}")
        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }
        payload = {
            "model": model,
            "max_tokens": 100,
            "messages": [{"role": "user", "content": "Hello, respond with just 'Test successful'"}],
        }
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    "https://api.anthropic.com/v1/messages", 
                    headers=headers, 
                    json=payload
                )
                
                if response.status_code == 200:
                    data = response.json()
                    text = data["content"][0]["text"]
                    print(f"  ✅ SUCCESS: {text}")
                    return True
                else:
                    print(f"  ❌ HTTP {response.status_code}: {response.text}")
                    
        except Exception as e:
            print(f"  ❌ Exception: {e}")
    
    return False


async def test_google_gemini_api():
    """Test Google Gemini API directly."""
    print("\nTesting Google Gemini API...")
    
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("❌ GOOGLE_API_KEY not found")
        return False
    
    print(f"✅ API key present (length: {len(api_key)})")
    
    # Test with different model names
    model_names = [
        "gemini-pro",
        "gemini-1.5-pro",
        "gemini-1.0-pro"
    ]
    
    for model in model_names:
        print(f"\n  Testing model: {model}")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        headers = {"Content-Type": "application/json"}
        payload = {"contents": [{"parts": [{"text": "Hello, respond with just 'Test successful'"}]}]}
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(url, headers=headers, json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    text = data["candidates"][0]["content"]["parts"][0]["text"]
                    print(f"  ✅ SUCCESS: {text}")
                    return True
                else:
                    print(f"  ❌ HTTP {response.status_code}: {response.text}")
                    
        except Exception as e:
            print(f"  ❌ Exception: {e}")
    
    return False


async def test_openai_api():
    """Test OpenAI API as a control."""
    print("\nTesting OpenAI API (control)...")
    
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY not found")
        return False
    
    print(f"✅ API key present (length: {len(api_key)})")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "gpt-4",
        "messages": [{"role": "user", "content": "Hello, respond with just 'Test successful'"}],
        "max_tokens": 100
    }
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload,
            )
            
            if response.status_code == 200:
                data = response.json()
                text = data["choices"][0]["message"]["content"]
                print(f"  ✅ SUCCESS: {text}")
                return True
            else:
                print(f"  ❌ HTTP {response.status_code}: {response.text}")
                
    except Exception as e:
        print(f"  ❌ Exception: {e}")
    
    return False


async def main():
    """Run all API tests."""
    print("🔍 Direct LLM Provider API Testing")
    print("=" * 50)
    
    results = {}
    
    # Test each provider
    results["openai"] = await test_openai_api()
    results["anthropic"] = await test_anthropic_api()
    results["google"] = await test_google_gemini_api()
    
    print("\n" + "=" * 50)
    print("📊 RESULTS SUMMARY:")
    for provider, success in results.items():
        status = "✅ WORKING" if success else "❌ FAILED"
        print(f"  {provider.upper()}: {status}")
    
    working_count = sum(results.values())
    total_count = len(results)
    print(f"\n🎯 Overall: {working_count}/{total_count} providers working")
    
    return results


if __name__ == "__main__":
    # Note: This should be run with the production environment variables
    asyncio.run(main())