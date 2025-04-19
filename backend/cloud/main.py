from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
import time
from datetime import datetime

app = FastAPI(title="UltraAI Cloud API")

# Configure CORS to allow requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, replace with specific frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Sample models data
MODELS = [
    {"id": "gpt-4", "name": "GPT-4", "provider": "OpenAI", "type": "thinking"},
    {"id": "claude-3-opus", "name": "Claude 3 Opus", "provider": "Anthropic", "type": "thinking"},
    {"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo", "provider": "OpenAI", "type": "processing"},
    {"id": "gemini-pro", "name": "Gemini Pro", "provider": "Google", "type": "processing"},
    {"id": "llama-3", "name": "Llama 3", "provider": "Meta", "type": "processing"},
]

# Analysis types
ANALYSIS_TYPES = [
    {"id": "standard", "name": "Standard Analysis", "description": "Multiple models analyze your prompt in parallel"},
    {"id": "depth", "name": "In-Depth Analysis", "description": "Ultra performs a detailed analysis with all models"},
    {"id": "comparative", "name": "Comparative Analysis", "description": "Compare results across different models"},
]

# A la carte options
ALACARTE_OPTIONS = [
    {"id": "detailed_analysis", "name": "Detailed Analysis", "description": "Provides more in-depth results"},
    {"id": "code_generation", "name": "Code Generation", "description": "Generate code implementations"},
    {"id": "citation", "name": "Citation", "description": "Include citations for information sources"},
    {"id": "summary", "name": "Executive Summary", "description": "Include a concise summary of findings"},
]

# Output formats
OUTPUT_FORMATS = [
    {"id": "text", "name": "Plain Text", "description": "Results as plain text"},
    {"id": "markdown", "name": "Markdown", "description": "Results formatted with markdown"},
    {"id": "html", "name": "HTML", "description": "Results as HTML for rich formatting"},
    {"id": "json", "name": "JSON", "description": "Results in structured JSON format"},
]

# Models for request/response validation
class AnalysisRequest(BaseModel):
    prompt: str
    models: List[str]
    options: Optional[Dict[str, Any]] = {}
    analysis_type: Optional[str] = "standard"
    output_format: Optional[str] = "text"

class ModelResponse(BaseModel):
    id: str
    name: str
    provider: str
    type: str

# API Routes
@app.get("/")
async def root():
    return {"message": "UltraAI Cloud API is running"}

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/api/models", response_model=List[ModelResponse])
async def get_models():
    return MODELS

@app.get("/api/analysis-types")
async def get_analysis_types():
    return ANALYSIS_TYPES

@app.get("/api/alacarte-options")
async def get_alacarte_options():
    return ALACARTE_OPTIONS

@app.get("/api/output-formats")
async def get_output_formats():
    return OUTPUT_FORMATS

@app.post("/api/analyze")
async def analyze(request: AnalysisRequest):
    # Validate requested models
    valid_model_ids = [model["id"] for model in MODELS]
    for model_id in request.models:
        if model_id not in valid_model_ids:
            raise HTTPException(status_code=400, detail=f"Invalid model ID: {model_id}")

    # Validate analysis type
    valid_analysis_types = [at["id"] for at in ANALYSIS_TYPES]
    if request.analysis_type not in valid_analysis_types:
        raise HTTPException(status_code=400, detail=f"Invalid analysis type: {request.analysis_type}")

    # Validate output format
    valid_output_formats = [of["id"] for of in OUTPUT_FORMATS]
    if request.output_format not in valid_output_formats:
        raise HTTPException(status_code=400, detail=f"Invalid output format: {request.output_format}")

    # Process a la carte options
    selected_options = request.options.get("selected_options", [])

    # Simulate processing time
    time.sleep(1)

    # Generate mock responses for each model
    responses = {}
    for model_id in request.models:
        model_info = next(model for model in MODELS if model["id"] == model_id)

        # Customize response based on options
        response_text = f"Analysis from {model_info['name']} by {model_info['provider']}\n\n"

        # Add analysis type info
        analysis_type_info = next(at for at in ANALYSIS_TYPES if at["id"] == request.analysis_type)
        response_text += f"Analysis Type: {analysis_type_info['name']}\n"

        # Add a la carte options if selected
        if selected_options:
            response_text += "\nSelected Options:\n"
            for option_id in selected_options:
                option = next((o for o in ALACARTE_OPTIONS if o["id"] == option_id), None)
                if option:
                    response_text += f"- {option['name']}\n"

        response_text += f"\nResponse to: {request.prompt}\n\n"

        if model_info["type"] == "thinking":
            response_text += "This is an in-depth analysis with multiple perspectives and considerations."
            if "detailed_analysis" in selected_options:
                response_text += "\n\nDetailed Analysis Section:\n• Point 1: Additional details and considerations\n• Point 2: Further analysis on implications\n• Point 3: Alternative viewpoints to consider"
        else:
            response_text += "This is a straightforward processing of your request with key points."
            if "summary" in selected_options:
                response_text += "\n\nExecutive Summary: This analysis provides a concise overview of the key findings and recommendations based on your prompt."

        # Format response according to specified output format
        if request.output_format == "markdown":
            response_text = f"# Analysis from {model_info['name']}\n\n" + response_text.replace("\n\n", "\n\n## ")
        elif request.output_format == "html":
            response_text = f"<h1>Analysis from {model_info['name']}</h1><p>" + response_text.replace("\n\n", "</p><h2>") + "</h2>"

        responses[model_id] = {
            "text": response_text,
            "metadata": {
                "processing_time": 0.98,
                "model_type": model_info["type"],
                "analysis_type": request.analysis_type,
                "output_format": request.output_format,
                "timestamp": datetime.now().isoformat()
            }
        }

    # Return combined response
    return {
        "request": {
            "prompt": request.prompt,
            "models": request.models,
            "analysis_type": request.analysis_type,
            "options": request.options,
            "output_format": request.output_format
        },
        "responses": responses,
        "timestamp": datetime.now().isoformat()
    }

# For local development
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    # For production, change host to "0.0.0.0" - for development, use "127.0.0.1"
    uvicorn.run(app, host="127.0.0.1", port=port)