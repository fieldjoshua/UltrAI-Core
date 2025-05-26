import logging

from flask import Flask, jsonify, request
from flask_cors import CORS

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/api/available-models", methods=["GET"])
def available_models():
    return jsonify(
        {
            "status": "success",
            "available_models": [
                "gpt4o",
                "gpt4turbo",
                "claude3opus",
                "claude3sonnet",
                "gemini15flash",
                "gemini15pro",
            ],
        }
    )


@app.route("/api/analyze", methods=["POST"])
def analyze():
    logger.info("Received analyze request")
    try:
        request_data = request.json or {}
        prompt = request_data.get("prompt", "")
        selected_models = request_data.get("selected_models", ["gpt-4o"])
        ultra_model = request_data.get("ultra_model", "gpt-4o")

        logger.debug(f"Request data: {request_data}")

        # Create response data matching frontend expectations
        response_data = {
            "status": "success",
            "model_responses": {
                model: f"Mock response from {model} for prompt: '{prompt[:50]}{'...' if len(prompt) > 50 else ''}'\n\nThis is a simulated response that would normally come from the {model} AI model. In a real scenario, this would contain the actual analysis, insights, and answers provided by the model."
                for model in selected_models
            },
            "ultra_response": f"Ultra Analysis Summary\n{'='*50}\n\nPrompt: {prompt}\nModels Used: {', '.join(selected_models)}\nPrimary Model: {ultra_model}\n\nCombined Analysis:\nThis is the Ultra AI synthesis that combines insights from all selected models. It would normally provide a comprehensive analysis that leverages the strengths of each model to give you the best possible response.\n\nKey Points:\n- Mock response from {len(selected_models)} model(s)\n- Using {ultra_model} as the primary reasoning model\n- This demonstrates the multi-model analysis capability",
            "performance": {
                "total_time_seconds": 3.2,
                "model_times": {model: 1.5 for model in selected_models},
                "token_counts": {model: {"prompt_tokens": 25, "completion_tokens": 150, "total_tokens": 175} for model in selected_models},
            },
        }

        logger.info("Sending successful response")
        return jsonify(response_data)
    except Exception as e:
        logger.error(f"Error in analyze endpoint: {str(e)}", exc_info=True)
        return jsonify({"status": "error", "message": str(e)})


if __name__ == "__main__":
    print("Starting mock UltraAI API server on http://localhost:8086")
    # Run on port 8086 to match the Docker port mapping
    app.run(host="0.0.0.0", port=8087, debug=True)
