import os
import sys

import anthropic
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key
api_key = os.getenv("ANTHROPIC_API_KEY")
print(f"API key found: {bool(api_key)}", flush=True)

try:
    print("Creating client...", flush=True)
    client = anthropic.Anthropic(api_key=api_key)

    print("Sending message...", flush=True)
    message = client.messages.create(
        model="claude-3-sonnet-20240229",
        messages=[{"role": "user", "content": "Hello"}],
    )

    print("Response received!", flush=True)
    print(f"Claude says: {message.content[0].text}", flush=True)

except Exception as e:
    print(f"Error type: {type(e).__name__}", flush=True)
    print(f"Error message: {str(e)}", flush=True)
    import traceback

    print("Traceback:", flush=True)
    traceback.print_exc()

print("Script completed", flush=True)
