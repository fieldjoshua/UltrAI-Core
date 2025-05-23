import os
from anthropic import Anthropic
from anthropic.types import TextBlock
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("Starting Claude test...")

# Initialize the client with API key from environment
api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    print("Error: ANTHROPIC_API_KEY not found in environment variables")
    print(
        "Please add your API key to a .env file or export it as an environment variable"
    )
    exit(1)

client = Anthropic(api_key=api_key)

try:
    print("Creating message...")
    # Use the modern messages API instead of deprecated completions API
    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",  # Use Claude 3.5 Sonnet (latest)
        max_tokens=1024,
        messages=[{"role": "user", "content": "Hello, world!"}],
    )
    print("Got response!")
    # Handle different content types properly
    content = message.content[0]
    if isinstance(content, TextBlock):
        print(f"Claude says: {content.text}")
    else:
        print(f"Claude says: {str(content)}")
except Exception as e:
    print(f"Error type: {type(e).__name__}")
    print(f"Error message: {str(e)}")
    import traceback

    traceback.print_exc()

print("Test completed")
