#!/usr/bin/env python3
"""
Test API keys for OpenAI, Anthropic, and Google directly.
This script makes simple requests to each provider to verify API key validity.
"""

import os
import sys
import asyncio
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ANSI color codes for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'

async def test_openai():
    """Test OpenAI API key"""
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        return f"{RED}❌ OpenAI: No API key found in environment{RESET}"
    
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": "Say 'test successful'"}],
        "max_tokens": 10,
        "temperature": 0
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, headers=headers, json=data)
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                return f"{GREEN}✓ OpenAI: Working! Response: {content}{RESET}"
            elif response.status_code == 401:
                return f"{RED}❌ OpenAI: Invalid API key (401 Unauthorized){RESET}"
            elif response.status_code == 429:
                return f"{YELLOW}⚠ OpenAI: Rate limited (429) - API key is valid{RESET}"
            else:
                return f"{RED}❌ OpenAI: Failed with status {response.status_code}: {response.text[:200]}{RESET}"
                
    except Exception as e:
        return f"{RED}❌ OpenAI: Exception: {type(e).__name__}: {str(e)}{RESET}"

async def test_anthropic():
    """Test Anthropic API key"""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    
    if not api_key:
        return f"{RED}❌ Anthropic: No API key found in environment{RESET}"
    
    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "claude-3-haiku-20240307",
        "messages": [{"role": "user", "content": "Say 'test successful'"}],
        "max_tokens": 10,
        "temperature": 0
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, headers=headers, json=data)
            
            if response.status_code == 200:
                result = response.json()
                content = result['content'][0]['text']
                return f"{GREEN}✓ Anthropic: Working! Response: {content}{RESET}"
            elif response.status_code == 401:
                return f"{RED}❌ Anthropic: Invalid API key (401 Unauthorized){RESET}"
            elif response.status_code == 429:
                return f"{YELLOW}⚠ Anthropic: Rate limited (429) - API key is valid{RESET}"
            else:
                return f"{RED}❌ Anthropic: Failed with status {response.status_code}: {response.text[:200]}{RESET}"
                
    except Exception as e:
        return f"{RED}❌ Anthropic: Exception: {type(e).__name__}: {str(e)}{RESET}"

async def test_google():
    """Test Google API key"""
    api_key = os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        return f"{RED}❌ Google: No API key found in environment{RESET}"
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}"
    headers = {
        "Content-Type": "application/json"
    }
    
    data = {
        "contents": [{
            "parts": [{
                "text": "Say 'test successful'"
            }]
        }],
        "generationConfig": {
            "temperature": 0,
            "maxOutputTokens": 10
        }
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, headers=headers, json=data)
            
            if response.status_code == 200:
                result = response.json()
                content = result['candidates'][0]['content']['parts'][0]['text']
                return f"{GREEN}✓ Google: Working! Response: {content}{RESET}"
            elif response.status_code == 403:
                error_text = response.text
                if "API key not valid" in error_text:
                    return f"{RED}❌ Google: Invalid API key (403 Forbidden){RESET}"
                else:
                    return f"{RED}❌ Google: Access forbidden (403) - Check API key permissions{RESET}"
            elif response.status_code == 429:
                return f"{YELLOW}⚠ Google: Rate limited (429) - API key is valid{RESET}"
            else:
                return f"{RED}❌ Google: Failed with status {response.status_code}: {response.text[:200]}{RESET}"
                
    except Exception as e:
        return f"{RED}❌ Google: Exception: {type(e).__name__}: {str(e)}{RESET}"

async def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("Testing API Keys Directly")
    print("="*60 + "\n")
    
    # Show which .env file is being used
    env_path = os.path.join(os.getcwd(), '.env')
    if os.path.exists(env_path):
        print(f"Using .env file: {env_path}")
    else:
        print(f"{YELLOW}Warning: No .env file found at {env_path}{RESET}")
    
    print(f"\nCurrent working directory: {os.getcwd()}")
    print(f"Python executable: {sys.executable}\n")
    
    # Run tests concurrently
    results = await asyncio.gather(
        test_openai(),
        test_anthropic(),
        test_google()
    )
    
    # Print results
    for result in results:
        print(result)
    
    print("\n" + "="*60)
    
    # Summary
    working_count = sum(1 for r in results if "✓" in r)
    total_count = len(results)
    
    if working_count == total_count:
        print(f"{GREEN}All {total_count} API keys are working!{RESET}")
    elif working_count > 0:
        print(f"{YELLOW}{working_count}/{total_count} API keys are working{RESET}")
    else:
        print(f"{RED}No API keys are working!{RESET}")
    
    print("="*60 + "\n")

if __name__ == "__main__":
    asyncio.run(main())