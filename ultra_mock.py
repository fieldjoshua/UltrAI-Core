from flask import Flask, request, jsonify
from flask_cors import CORS

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


@app.route("/api/documents", methods=["GET"])
def get_documents():
    # Return empty document list for now
    return jsonify([])


@app.route("/api/analyze", methods=["POST"])
def analyze():
    request_data = request.json or {}
    prompt = request_data.get("prompt", "")

    # Prepare response with appropriate formatting to avoid long lines
    gpt_response = (
        f"GPT-4o response to: {prompt}\n\n"
        "This is a simulated response using advanced AI techniques to answer your prompt."
    )

    claude_response = (
        f"Claude response to: {prompt}\n\n"
        "Here is a thoughtful simulation of how Claude would analyze this prompt."
    )

    gemini_response = (
        f"Gemini analysis of: {prompt}\n\n"
        "This simulated response demonstrates how Gemini might approach your question."
    )

    analysis = (
        f"Comparison analysis of: {prompt}\n\n"
        "The three models showed different approaches. GPT-4o was more detailed, "
        "Claude was more thoughtful, and Gemini was more concise."
    )

    return jsonify(
        {
            "status": "success",
            "data": {
                "prompt": prompt,
                "results": [
                    {
                        "model": "gpt-4o",
                        "provider": "openai",
                        "response": gpt_response,
                    },
                    {
                        "model": "claude-3-opus",
                        "provider": "anthropic",
                        "response": claude_response,
                    },
                    {
                        "model": "gemini-pro",
                        "provider": "google",
                        "response": gemini_response,
                    },
                ],
                "analysis": analysis,
            },
        }
    )


if __name__ == "__main__":
    print("Starting mock UltraAI API server on http://localhost:8000")
    app.run(host="127.0.0.1", port=8000)
