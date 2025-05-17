"""Mock LLM Service for Integration Testing"""

import os
import random
import time
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

# Configuration from environment
RESPONSE_DELAY = float(os.getenv("RESPONSE_DELAY", "0.5"))
ERROR_RATE = float(os.getenv("ERROR_RATE", "0.05"))


class LLMRequest(BaseModel):
    model: str
    messages: List[Dict[str, str]]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 1000


class LLMResponse(BaseModel):
    id: str
    model: str
    choices: List[Dict]
    usage: Dict[str, int]


# Mock responses for different models
MOCK_RESPONSES = {
    "gpt-4": "This is a mock GPT-4 response for testing purposes.",
    "claude-3": "This is a mock Claude-3 response for testing purposes.",
    "llama-2": "This is a mock LLaMA-2 response for testing purposes.",
}


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "service": "mock-llm"}


@app.post("/v1/chat/completions")
async def chat_completion(request: LLMRequest) -> LLMResponse:
    """Mock chat completion endpoint"""

    # Simulate random errors
    if random.random() < ERROR_RATE:
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")

    # Simulate processing delay
    time.sleep(RESPONSE_DELAY)

    # Get mock response based on model
    content = MOCK_RESPONSES.get(request.model, "This is a generic mock response.")

    response = LLMResponse(
        id=f"mock-{random.randint(1000, 9999)}",
        model=request.model,
        choices=[
            {
                "index": 0,
                "message": {"role": "assistant", "content": content},
                "finish_reason": "stop",
            }
        ],
        usage={
            "prompt_tokens": sum(
                len(msg["content"].split()) for msg in request.messages
            ),
            "completion_tokens": len(content.split()),
            "total_tokens": sum(len(msg["content"].split()) for msg in request.messages)
            + len(content.split()),
        },
    )

    return response


@app.post("/v1/embeddings")
async def create_embedding(request: Dict) -> Dict:
    """Mock embeddings endpoint"""

    # Simulate random errors
    if random.random() < ERROR_RATE:
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")

    # Generate mock embeddings
    dimension = 1536  # Standard embedding dimension
    embeddings = []

    for text in request.get("input", []):
        # Generate random embedding vector
        embedding = [random.random() for _ in range(dimension)]
        embeddings.append(embedding)

    return {
        "object": "list",
        "data": [
            {"object": "embedding", "embedding": emb, "index": i}
            for i, emb in enumerate(embeddings)
        ],
        "model": request.get("model", "text-embedding-ada-002"),
        "usage": {
            "prompt_tokens": sum(
                len(text.split()) for text in request.get("input", [])
            ),
            "total_tokens": sum(len(text.split()) for text in request.get("input", [])),
        },
    }


@app.get("/models")
async def list_models() -> Dict:
    """List available models"""
    return {
        "object": "list",
        "data": [
            {"id": "gpt-4", "object": "model", "owned_by": "openai"},
            {"id": "claude-3", "object": "model", "owned_by": "anthropic"},
            {"id": "llama-2", "object": "model", "owned_by": "meta"},
        ],
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8086)
