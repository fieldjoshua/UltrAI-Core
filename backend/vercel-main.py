from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Create FastAPI app
app = FastAPI(title="Ultra AI API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)


class AnalysisRequest(BaseModel):
    prompt: str
    models: List[str] = []


@app.get("/")
async def root():
    return {"message": "Welcome to Ultra AI API"}


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "version": "1.0.0"}


@app.get("/api/status")
async def status():
    return {
        "status": "operational",
        "api_version": "1.0.0",
        "environment": "production",
    }


@app.post("/api/analyze")
async def analyze(request: AnalysisRequest):
    try:
        # Mock response for testing
        return {
            "status": "success",
            "results": {
                "message": f"Analyzed '{request.prompt}' using {len(request.models) or 'default'} models",
                "analysis": "This is a sample response from the Ultra AI backend.",
                "models_used": request.models or ["default-model"],
            },
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error processing request: {str(e)}"
        )


# Add an options route to handle preflight requests
@app.options("/{full_path:path}")
async def options_route(request: Request, full_path: str):
    return JSONResponse(
        content={"message": "OK"},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With",
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
