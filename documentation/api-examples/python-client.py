#!/usr/bin/env python3
"""
UltraAI Core Python API Client Example

This example demonstrates how to use the UltraAI Core API with Python.
"""

import os
import json
import time
from typing import Dict, List, Optional
import requests
from requests.exceptions import RequestException


class UltraAIClient:
    """Simple client for UltraAI Core API."""
    
    def __init__(self, base_url: str = "https://ultrai-core.onrender.com/api"):
        """
        Initialize the UltraAI client.
        
        Args:
            base_url: API base URL
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.token: Optional[str] = None
    
    def login(self, email: str, password: str) -> Dict:
        """
        Login and store the access token.
        
        Args:
            email: User email
            password: User password
            
        Returns:
            User information
        """
        response = self.session.post(
            f"{self.base_url}/auth/login",
            json={"email_or_username": email, "password": password}
        )
        response.raise_for_status()
        
        data = response.json()
        self.token = data["access_token"]
        self.session.headers.update({"Authorization": f"Bearer {self.token}"})
        
        return data["user"]
    
    def register(self, email: str, password: str, username: Optional[str] = None) -> Dict:
        """
        Register a new user account.
        
        Args:
            email: User email
            password: User password
            username: Optional username
            
        Returns:
            Created user information
        """
        payload = {"email": email, "password": password}
        if username:
            payload["username"] = username
        
        response = self.session.post(
            f"{self.base_url}/auth/register",
            json=payload
        )
        response.raise_for_status()
        
        return response.json()
    
    def analyze(
        self, 
        query: str, 
        models: List[str] = None,
        temperature: float = 0.7,
        include_details: bool = False
    ) -> Dict:
        """
        Analyze a query using multiple LLMs.
        
        Args:
            query: The query to analyze
            models: List of model IDs (default: ["gpt-4o", "claude-3-5-sonnet"])
            temperature: Generation temperature
            include_details: Include pipeline details in response
            
        Returns:
            Analysis results
        """
        if not self.token:
            raise ValueError("Not authenticated. Please login first.")
        
        if models is None:
            models = ["gpt-4o", "claude-3-5-sonnet-20241022"]
        
        payload = {
            "query": query,
            "selected_models": models,
            "options": {
                "temperature": temperature,
                "include_pipeline_details": include_details
            }
        }
        
        response = self.session.post(
            f"{self.base_url}/orchestrator/analyze",
            json=payload
        )
        response.raise_for_status()
        
        return response.json()
    
    def get_balance(self) -> float:
        """
        Get current account balance.
        
        Returns:
            Account balance in USD
        """
        if not self.token:
            raise ValueError("Not authenticated. Please login first.")
        
        response = self.session.get(f"{self.base_url}/user/balance")
        response.raise_for_status()
        
        return response.json()["balance"]
    
    def get_transactions(self, limit: int = 10) -> List[Dict]:
        """
        Get recent transactions.
        
        Args:
            limit: Number of transactions to retrieve
            
        Returns:
            List of transactions
        """
        if not self.token:
            raise ValueError("Not authenticated. Please login first.")
        
        response = self.session.get(
            f"{self.base_url}/user/transactions",
            params={"limit": limit}
        )
        response.raise_for_status()
        
        return response.json()["transactions"]
    
    def get_available_models(self) -> List[Dict]:
        """
        Get list of available models.
        
        Returns:
            List of available models with metadata
        """
        response = self.session.get(f"{self.base_url}/available-models")
        response.raise_for_status()
        
        return response.json()["models"]
    
    def health_check(self) -> Dict:
        """
        Check API health status.
        
        Returns:
            Health status information
        """
        response = self.session.get(f"{self.base_url.replace('/api', '')}/health")
        response.raise_for_status()
        
        return response.json()


def main():
    """Example usage of the UltraAI client."""
    
    # Initialize client
    client = UltraAIClient()
    
    # For demo purposes, use environment variables
    email = os.getenv("ULTRAI_EMAIL", "demo@ultrai.app")
    password = os.getenv("ULTRAI_PASSWORD", "demo123")
    
    try:
        # Check API health
        print("Checking API health...")
        health = client.health_check()
        print(f"API Status: {health['status']}")
        print()
        
        # Login
        print(f"Logging in as {email}...")
        user = client.login(email, password)
        print(f"Welcome, {user['email']}!")
        print(f"Account balance: ${user['account_balance']}")
        print()
        
        # Get available models
        print("Available models:")
        models = client.get_available_models()
        for model in models:
            print(f"  - {model['name']} ({model['id']})")
            print(f"    Provider: {model['provider']}")
            print(f"    Context: {model['context_window']:,} tokens")
            print(f"    Price: ${model['pricing']['input_per_1k']}/1k input, "
                  f"${model['pricing']['output_per_1k']}/1k output")
        print()
        
        # Analyze a query
        query = "Explain the benefits of quantum computing for cryptography"
        print(f"Analyzing: '{query}'")
        print("Using models: GPT-4o and Claude 3.5 Sonnet")
        
        start_time = time.time()
        result = client.analyze(query, models=["gpt-4o", "claude-3-5-sonnet-20241022"])
        elapsed = time.time() - start_time
        
        print(f"\nAnalysis completed in {elapsed:.1f} seconds")
        print(f"Cost: ${result['metadata']['estimated_cost']:.3f}")
        print(f"Tokens used: {result['metadata']['total_tokens']:,}")
        
        print("\n--- Ultra Synthesis™ Result ---")
        print(result["ultra_synthesis"][:500] + "..." if len(result["ultra_synthesis"]) > 500 else result["ultra_synthesis"])
        
        # Get recent transactions
        print("\n\nRecent transactions:")
        transactions = client.get_transactions(limit=5)
        for tx in transactions:
            sign = "-" if tx["type"] == "debit" else "+"
            print(f"  {sign}${tx['amount']:.3f} - {tx['description']}")
            print(f"    Balance after: ${tx['balance_after']:.2f}")
            print(f"    Date: {tx['created_at']}")
        
        # Check final balance
        balance = client.get_balance()
        print(f"\nCurrent balance: ${balance:.2f}")
        
    except RequestException as e:
        print(f"API Error: {e}")
        if hasattr(e.response, 'json'):
            error_data = e.response.json()
            print(f"Details: {error_data.get('message', 'Unknown error')}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()