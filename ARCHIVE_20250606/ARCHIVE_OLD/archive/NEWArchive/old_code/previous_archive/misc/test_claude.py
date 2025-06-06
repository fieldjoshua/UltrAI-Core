from anthropic import AI_PROMPT, HUMAN_PROMPT, Anthropic

# Initialize the client
client = Anthropic(
    api_key="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"
)

# Create a completion instead of a message
completion = client.completions.create(
    model="claude-2.1",
    max_tokens_to_sample=1024,
    prompt=f"{HUMAN_PROMPT} Hello, world! {AI_PROMPT}",
)

print(completion.completion)
