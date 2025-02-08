from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
from ultra_hyper_m2 import TriLLMOrchestrator
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PromptRequest(BaseModel):
    prompt: str
    engine: str = "llama"
    selectedEngines: list[str]
    options: dict = {
        "keepDataPrivate": False,
        "useNoTraceEncryption": False
    }

@app.post("/api/analyze")
async def analyze_prompt(request: PromptRequest):
    try:
        orchestrator = TriLLMOrchestrator(
            api_keys={
                "openai": os.getenv("OPENAI_API_KEY"),
                "google": os.getenv("GOOGLE_API_KEY")
            },
            ultra_engine=request.engine,
            output_format="json" if request.options.get("keepDataPrivate") else "plain"
        )
        
        results = await orchestrator.orchestrate_full_process(request.prompt)
        return {
            "status": "success",
            "data": results,
            "output_directory": orchestrator.run_dir
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/status")
async def check_status():
    try:
        env_ok = await test_env()
        return {"status": "operational" if env_ok else "error"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 