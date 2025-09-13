#!/usr/bin/env python3
"""Test the new API keys directly."""

import os
import asyncio
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_anthropic():
    """Test Anthropic API key."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ Anthropic: No API key found")
        return
    
    print(f"Testing Anthropic API key: {api_key[:10]}...{api_key[-4:]}")
    
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    
    data = {
        "model": "claude-3-haiku-20240307",
        "messages": [{"role": "user", "content": "Say 'test'"}],
        "max_tokens": 10
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=data,
                timeout=10.0
            )
            if response.status_code == 200:
                print("✅ Anthropic: API key is valid!")
                print(f"   Response: {response.json()}")
            else:
                print(f"❌ Anthropic: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ Anthropic: {str(e)}")

async def test_google():
    """Test Google API key."""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ Google: No API key found")
        return
    
    print(f"\nTesting Google API key: {api_key[:10]}...{api_key[-4:]}")
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    data = {
        "contents": [{
            "parts": [{"text": "Say 'test'"}]
        }]
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=data, timeout=10.0)
            if response.status_code == 200:
                print("✅ Google: API key is valid!")
                print(f"   Response: {response.json()}")
            else:
                print(f"❌ Google: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ Google: {str(e)}")

async def test_openai():
    """Test OpenAI API key status."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OpenAI: No API key found")
        return
    
    print(f"\nTesting OpenAI API key: {api_key[:10]}...{api_key[-4:]}")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Test with a simple completion
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": "Say 'test'"}],
        "max_tokens": 10
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=10.0
            )
            if response.status_code == 200:
                print("✅ OpenAI: API key is valid!")
                print(f"   Response: {response.json()}")
            elif response.status_code == 429:
                print("⚠️  OpenAI: Rate limited but key is valid")
                print(f"   Response: {response.text}")
            else:
                print(f"❌ OpenAI: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ OpenAI: {str(e)}")

async def main():
    """Run all tests."""
    print("Testing API Keys...\n")
    await test_anthropic()
    await test_google()
    await test_openai()

if __name__ == "__main__":
    asyncio.run(main())