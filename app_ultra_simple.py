"""Ultra simple FastAPI app - no backend imports at all"""

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Ultra Minimal")

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"status": "running", "service": "ultra-minimal"}


@app.get("/api/health")
def health():
    return {"status": "ok", "environment": os.getenv("ENV", "production")}


@app.post("/analyze")
def analyze(data: dict = {}):
    return {"status": "mock_analysis", "input": data}


@app.get("/api/available-models")
def models():
    return {"models": ["gpt-4", "claude-3"]}


@app.post("/api/auth/login")
def login(data: dict = {}):
    return {
        "token": "mock_token",
        "user": {"email": data.get("email", "user@test.com")},
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app_ultra_simple:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000))
    )
