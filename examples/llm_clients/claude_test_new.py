from anthropic import Anthropic

print("Starting test...")

# Initialize the client
client = Anthropic(
    api_key="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"
)

try:
    print("Creating message...")
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
    print("Got response!")
    print(f"Claude says: {message.content[0].text}")
except Exception as e:
    print(f"Error type: {type(e).__name__}")
    print(f"Error message: {str(e)}")
    import traceback
    traceback.print_exc()

print("Test completed") 