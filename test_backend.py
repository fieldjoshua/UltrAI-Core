from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uvicorn

app = FastAPI(title="Ultra Test API")

# Configure CORS to allow requests from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalyzeRequest(BaseModel):
    prompt: str
    models: List[str]
    ultra_model: Optional[str] = "gpt4o"
    pattern: Optional[str] = "confidence"

@app.get("/")
async def root():
    return {"message": "Ultra API is running", "status": "ok"}

@app.get("/api/health")
async def health_check():
    return {"status": "ok", "service": "ultra-test-api"}

@app.get("/api/models")
async def get_models():
    return {
        "available_models": [
            "gpt4o", "gpt4turbo", "gpto3mini",
            "claude37", "claude3opus", "gemini15"
        ]
    }

@app.post("/api/analyze")
async def analyze(request: AnalyzeRequest):
    # Mock analysis response with the requested models
    results = {}
    for model in request.models:
        results[model] = {
            "response": f"This is a test response from {model} model analyzing: '{request.prompt[:50]}...'",
            "time_taken": 2.3 if "gpt" in model else 1.8
        }

    ultra_response = f"ULTRA ANALYSIS: Combined analysis of {len(request.models)} models on prompt: '{request.prompt[:50]}...'"

    return {
        "results": results,
        "ultra_response": ultra_response,
        "pattern": request.pattern
    }

# This is only used when running the API locally
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8085)