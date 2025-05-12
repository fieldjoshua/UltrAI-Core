from flask import Flask, request, jsonify
from flask_cors import CORS
import logging

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
                "gpt-4o",
                "gpt-4-turbo",
                "gpt-3.5-turbo",
                "claude-3-opus",
                "claude-3-sonnet",
                "gemini-pro",
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

        # Create response data
        response_data = {
            "status": "success",
            "analysis_id": "analysis_123456789",
            "results": {
                "model_responses": {
                    model: {
                        "response": f"Mock response from {model} for prompt: {prompt[:50]}...",
                        "time_taken": 2.5,
                        "tokens_used": 150
                    } for model in selected_models
                },
                "ultra_response": f"Ultra analysis using {ultra_model} model for prompt: {prompt[:50]}...\n\nThis is a combined view of all model responses.",
                "performance": {
                    "total_time_seconds": 5.0,
                    "model_times": {model: 2.5 for model in selected_models},
                    "token_counts": {model: 150 for model in selected_models},
                }
            }
        }
        
        logger.info("Sending successful response")
        return jsonify(response_data)
    except Exception as e:
        logger.error(f"Error in analyze endpoint: {str(e)}", exc_info=True)
        return jsonify({"status": "error", "message": str(e)})


if __name__ == "__main__":
    print("Starting mock UltraAI API server on http://localhost:8086")
    # Run on port 8086 to match the Docker port mapping
    app.run(host="0.0.0.0", port=8086, debug=True)
