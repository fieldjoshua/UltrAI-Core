"""
Orchestration Service Fixes for Big 3 LLMs Implementation

This file contains critical fixes to ensure the 3-stage orchestration pipeline
works correctly with the Big 3 providers (OpenAI, Anthropic, Google).

Key fixes:
1. Prompt extraction in ultra_synthesis stage
2. Error normalization across adapters
3. Timeout and retry configuration
4. SSE event standardization
"""


# Fix 1: Enhanced prompt extraction for ultra_synthesis
def extract_original_prompt(data):
    """
    Extract the original user prompt from various data structures.
    This handles all the different ways the prompt can be nested.
    """
    original_prompt = "Unknown prompt"

    # Path 1: Direct in data (from initial response stage)
    if isinstance(data, dict) and "prompt" in data:
        original_prompt = data["prompt"]

    # Path 2: In the input structure (when stages pass data)
    elif isinstance(data, dict) and "input" in data and isinstance(data["input"], dict):
        if "prompt" in data["input"]:
            original_prompt = data["input"]["prompt"]
        # Check deeper nesting
        elif "input" in data["input"] and isinstance(data["input"]["input"], dict):
            if "prompt" in data["input"]["input"]:
                original_prompt = data["input"]["input"]["prompt"]

    # Path 3: In input_data (less common)
    elif isinstance(data, dict) and "input_data" in data:
        if isinstance(data["input_data"], str):
            original_prompt = data["input_data"]
        elif isinstance(data["input_data"], dict) and "prompt" in data["input_data"]:
            original_prompt = data["input_data"]["prompt"]

    # Path 4: From original_responses in peer review data
    elif isinstance(data, dict) and "original_responses" in data:
        if (
            isinstance(data["original_responses"], dict)
            and "prompt" in data["original_responses"]
        ):
            original_prompt = data["original_responses"]["prompt"]

    return original_prompt


# Fix 2: Standardized error response format
def normalize_error_response(error, provider, model=None):
    """
    Normalize error responses across all LLM adapters to a consistent format.
    No cost fields included as per requirements.
    """
    return {
        "error": "SERVICE_ERROR",
        "message": str(error),
        "provider": provider,
        "model": model,
        "details": {"error_type": type(error).__name__, "timestamp": time.time()},
    }


# Fix 3: Enhanced timeout configuration
ADAPTER_TIMEOUT_CONFIG = {
    "default": {
        "timeout": 60.0,  # Total timeout
        "connect": 10.0,  # Connection timeout
        "read": 50.0,  # Read timeout
    },
    "openai": {
        "timeout": 60.0,
        "connect": 10.0,
        "read": 50.0,
        "max_retries": 2,
    },
    "anthropic": {
        "timeout": 60.0,
        "connect": 10.0,
        "read": 50.0,
        "max_retries": 2,
    },
    "google": {
        "timeout": 60.0,
        "connect": 10.0,
        "read": 50.0,
        "max_retries": 2,
    },
}


# Fix 4: SSE Event Schema
def create_sse_event(stage, event_type, data=None, **kwargs):
    """
    Create a standardized SSE event following the agreed schema.

    Event types:
    - stage_started
    - model_completed
    - stage_completed
    - synthesis_chunk
    - error
    """
    event = {
        "stage": stage,
        "type": event_type,
        "timestamp": time.time(),
    }

    # Add optional fields
    if data is not None:
        event["data"] = data

    # Add any additional fields from kwargs
    for key, value in kwargs.items():
        if key in ["provider", "model", "latency_ms", "tokens", "jobId"]:
            event[key] = value

    return event


# Fix 5: Provider detection helper
def get_provider_from_model(model_name):
    """
    Detect provider from model name.
    """
    if model_name.startswith("gpt") or model_name.startswith("o1"):
        return "openai"
    elif model_name.startswith("claude"):
        return "anthropic"
    elif model_name.startswith("gemini"):
        return "google"
    elif "/" in model_name:  # HuggingFace format
        return "huggingface"
    return "unknown"


# Fix 6: Model health check
async def check_model_health(model_name, adapter):
    """
    Quick health check for a model.
    """
    try:
        test_prompt = "Hi"
        result = await adapter.generate(test_prompt)
        if result and "generated_text" in result:
            return True, None
    except Exception as e:
        return False, str(e)
    return False, "Unknown error"


import time
