from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uvicorn
from datetime import datetime

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

class ProcessRequest(BaseModel):
    prompt: str
    models: List[str]
    analysisType: str
    alacarteOptions: List[str]
    outputFormat: str

@app.get("/")
async def root():
    return {"message": "Ultra API is running", "status": "ok"}

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/api/models")
async def get_models():
    models = [
        {
            "id": "gpt4o",
            "name": "GPT-4o",
            "provider": "OpenAI",
            "description": "OpenAI's most advanced multimodal model."
        },
        {
            "id": "claude37",
            "name": "Claude 3.7 Sonnet",
            "provider": "Anthropic",
            "description": "High-performance AI model with excellent reasoning capabilities."
        },
        {
            "id": "gemini15",
            "name": "Gemini 1.5 Pro",
            "provider": "Google",
            "description": "Multimodal model with strong coding and reasoning skills."
        },
        {
            "id": "mistral",
            "name": "Mistral Large",
            "provider": "Mistral AI",
            "description": "Powerful open-weight model with strong reasoning capabilities."
        }
    ]
    return models

@app.get("/api/analysis-types")
async def get_analysis_types():
    analysis_types = [
        {
            "id": "confidence",
            "name": "Confidence Analysis",
            "description": "Analyzes how confident each model is about its answers and highlights areas of disagreement."
        },
        {
            "id": "critique",
            "name": "Critique",
            "description": "Models critique each other's responses to find potential flaws or improvements."
        },
        {
            "id": "gut_check",
            "name": "Gut Check",
            "description": "Quick instinctive responses from models to get directional guidance."
        },
        {
            "id": "scenarios",
            "name": "Scenario Analysis",
            "description": "Explore multiple potential outcomes and perspectives for deeper understanding."
        }
    ]
    return analysis_types

@app.get("/api/alacarte-options")
async def get_alacarte_options():
    options = [
        {
            "id": "citations",
            "name": "Include Citations",
            "description": "Add citations to sources when models reference external information."
        },
        {
            "id": "uncertainty",
            "name": "Highlight Uncertainty",
            "description": "Explicitly highlight areas where models express uncertainty or conflicting views."
        },
        {
            "id": "extremes",
            "name": "Explore Extremes",
            "description": "Include extreme or edge-case perspectives in the analysis."
        },
        {
            "id": "alternatives",
            "name": "Alternative Viewpoints",
            "description": "Actively seek contrasting perspectives on the topic."
        }
    ]
    return options

@app.get("/api/output-formats")
async def get_output_formats():
    formats = [
        {
            "id": "concise",
            "name": "Concise Summary",
            "description": "Brief, to-the-point summary focusing on key insights."
        },
        {
            "id": "detailed",
            "name": "Detailed Analysis",
            "description": "Comprehensive analysis with all supporting details and reasoning."
        },
        {
            "id": "bullet",
            "name": "Bullet Points",
            "description": "Key findings presented as easy-to-scan bullet points."
        },
        {
            "id": "pros_cons",
            "name": "Pros and Cons",
            "description": "Analysis organized into advantages and disadvantages."
        }
    ]
    return formats

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

@app.post("/api/process")
async def process(request: ProcessRequest):
    # Simulate processing time
    import time
    time.sleep(1)

    # Create a simulated response based on the request data
    selected_models = [model for model in request.models]
    model_names = ", ".join(selected_models)

    # Format options list
    options = ""
    if request.alacarteOptions:
        option_ids = ", ".join(request.alacarteOptions)
        options = f"with options: {option_ids}"

    content = f"""# Analysis Results

## Summary
This is a simulated result for prompt: "{request.prompt}"

## Models Used
{model_names}

## Analysis Type
{request.analysisType}

## Output Format
{request.outputFormat}

{options}

## Detailed Analysis
Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam in dui mauris.
Vivamus hendrerit arcu sed erat molestie vehicula. Sed auctor neque eu tellus rhoncus ut eleifend nibh porttitor.

## Conclusion
This is a test conclusion that would normally contain insights from the analysis.
"""

    return {
        "status": "success",
        "content": content
    }

# This is only used when running the API locally
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)