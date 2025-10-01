#!/usr/bin/env python3
"""
Ultra AI - Simple Working Version
Just calls the APIs directly. No middleware, no health checks, no bullshit.
"""
import os
from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import anthropic
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalysisRequest(BaseModel):
    query: str
    analysis_type: str = "simple"
    models: list[str] = None

@app.get("/")
async def root():
    return FileResponse("frontend/public/index.html")

@app.get("/api/health")
async def health():
    return {"status": "ok"}

@app.post("/api/orchestrator/analyze")
async def analyze(request: AnalysisRequest):
    try:
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        
        if not anthropic_key:
            return JSONResponse(
                status_code=500,
                content={"error": "No Anthropic API key configured"}
            )
        
        client = anthropic.Anthropic(api_key=anthropic_key)
        
        # Initial response from Haiku
        initial = client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=1024,
            messages=[{"role": "user", "content": request.query}]
        )
        initial_text = initial.content[0].text
        
        # Meta review from Sonnet
        meta_prompt = f"""Original query: {request.query}

Here is an initial response:
{initial_text}

Please provide an improved response that addresses any limitations and provides a more comprehensive answer."""
        
        meta = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2048,
            messages=[{"role": "user", "content": meta_prompt}]
        )
        meta_text = meta.content[0].text
        
        # Ultra synthesis - using latest Sonnet
        ultra_prompt = f"""Original query: {request.query}

Initial response:
{initial_text}

Improved response:
{meta_text}

Please synthesize these into a final optimal response."""
        
        ultra = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2048,
            messages=[{"role": "user", "content": ultra_prompt}]
        )
        ultra_text = ultra.content[0].text
        
        return {
            "status": "success",
            "ultra_synthesis": ultra_text,
            "initial_responses": {
                "claude-3-5-haiku-20241022": initial_text
            },
            "meta_responses": {
                "claude-3-5-sonnet-20241022": meta_text
            },
            "models_used": ["claude-3-5-haiku-20241022", "claude-3-5-sonnet-20241022"],
            "query": request.query
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "error": str(e)
            }
        )

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
