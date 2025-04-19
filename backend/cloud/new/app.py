from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import json

app = FastAPI(title="UltraAI Cloud API")

# Configure CORS to allow requests from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models for request validation
class ProcessRequest(BaseModel):
    prompt: str
    models: List[str]
    analysisType: str
    alacarteOptions: List[str] = []
    outputFormat: str

# Basic routes
@app.get("/")
def read_root():
    return {"message": "UltraAI Cloud API is running"}

@app.get("/api/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# Data routes
@app.get("/api/models")
def get_models():
    """Return list of available AI models"""
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
def get_analysis_types():
    """Return list of available analysis types"""
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
def get_alacarte_options():
    """Return list of available a la carte options"""
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
def get_output_formats():
    """Return list of available output formats"""
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

@app.post("/api/process")
async def process(request: ProcessRequest):
    """Process an analysis request"""
    # Create a simulated response based on the request data
    selected_models = [model for model in request.models]
    model_names = ", ".join(selected_models)

    # Format options list
    options_text = ""
    if request.alacarteOptions:
        option_ids = ", ".join(request.alacarteOptions)
        options_text = f"with options: {option_ids}"

    content = f"""# Analysis Results

## Summary
Analysis for prompt: "{request.prompt}"

## Models Used
{model_names}

## Analysis Type
{request.analysisType}

## Output Format
{request.outputFormat}

{options_text}

## Detailed Analysis
This is a sample analysis that would be generated by comparing results from multiple models.
Each model would provide its own perspective, and those would be synthesized here.

## Conclusion
This demonstrates successful processing through all 7 steps of the UltraAI analysis pipeline.
"""

    return {
        "status": "success",
        "content": content
    }

# For local testing
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)