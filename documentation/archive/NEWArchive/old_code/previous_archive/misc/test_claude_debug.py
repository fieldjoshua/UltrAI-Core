import sys
import os
from dotenv import load_dotenv

# Test basic output first
print("=== Testing basic output ===", flush=True)
sys.stdout.write("stdout test\n")
sys.stderr.write("stderr test\n")
os.write(1, b"direct stdout test\n")
os.write(2, b"direct stderr test\n")

print("\n=== Testing imports ===", flush=True)
try:
    print("Importing anthropic...", flush=True)
    import anthropic
    print(f"Anthropic version: {anthropic.__version__}", flush=True)
    
    print("\n=== Testing API ===", flush=True)
    client = anthropic.Anthropic(
        api_key=os.getenv("ANTHROPIC_API_KEY")
    )
    print("Client created", flush=True)
    
    print("Sending message...", flush=True)
    message = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": "Hello, world!"
            }
        ]
    )
    print("Message sent!", flush=True)
    print(f"Response: {message.content[0].text}", flush=True)
    
except Exception as e:
    print("\n=== Error occurred ===", flush=True)
    print(f"Error type: {type(e).__name__}", flush=True)
    print(f"Error message: {str(e)}", flush=True)
    import traceback
    traceback.print_exc()

print("\n=== Test completed ===", flush=True) 