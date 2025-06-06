import json
import os

import requests
from dotenv import load_dotenv


def main():
    print("Script starting...")
    print("Running main...")
    print("Main function starting...")

    # Print current directory and check if .env exists
    current_dir = os.getcwd()
    print(f"Current directory: {current_dir}")
    env_exists = os.path.exists(os.path.join(current_dir, ".env"))
    print(f"Env file exists: {env_exists}")

    # Load environment variables
    load_dotenv()

    print("\nChecking API Keys:")
    api_keys = {
        "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY"),
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "GOOGLE_API_KEY": os.getenv("GOOGLE_API_KEY"),
    }

    for key, value in api_keys.items():
        if value:
            print(f"{key}: {value[:2]}...{value[-4:]}")
        else:
            print(f"{key}: Not found")

    print("\nTesting Ollama...")
    test_result = test_ollama()
    print(f"Ollama test result: {test_result}")


def test_ollama():
    try:
        print("Sending message to Ollama...")

        # First, let's see what models we have available
        models_response = requests.get("http://localhost:11434/api/tags")
        print("Available models:", models_response.json())

        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "mistral",  # Try mistral if available
                "prompt": "2+2=",  # Super simple prompt
                "stream": False,
                "raw": True,  # Get raw output
            },
        )

        if response.status_code == 200:
            data = response.json()
            print("Ollama response:", data["response"].strip())
            return "✓"

        return "✗"

    except Exception as e:
        print(f"Ollama error: {type(e).__name__}: {str(e)}")
        return "✗"


def chat():
    print("\nStarting chat (type 'quit' to exit)...")
    print("Initializing Ollama...")

    while True:
        try:
            # Get user input
            user_input = input("\nYou: ").strip()

            # Check for quit command
            if user_input.lower() in ["quit", "exit", "q"]:
                print("Goodbye!")
                break

            # Send to Ollama
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={"model": "llama2", "prompt": user_input, "stream": False},
            )

            # Print response
            if response.status_code == 200:
                bot_response = response.json()["response"]
                print("\nBot:", bot_response.strip())
            else:
                print("Error getting response")

        except Exception as e:
            print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()
    chat()
