from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/api/analyze", methods=["POST"])
def analyze():
    request_data = request.json
    prompt = request_data.get("prompt", "")

    return jsonify(
        {
            "status": "success",
            "data": {
                "prompt": prompt,
                "results": [
                    {
                        "model": "gpt-4o",
                        "provider": "openai",
                        "response": f"GPT-4o response to: {prompt}\n\nThis is a simulated response using advanced AI techniques to answer your prompt.",
                    },
                    {
                        "model": "claude-3-opus",
                        "provider": "anthropic",
                        "response": f"Claude response to: {prompt}\n\nHere is a thoughtful simulation of how Claude would analyze this prompt.",
                    },
                    {
                        "model": "gemini-pro",
                        "provider": "google",
                        "response": f"Gemini analysis of: {prompt}\n\nThis simulated response demonstrates how Gemini might approach your question.",
                    },
                ],
                "analysis": f"Comparison analysis of: {prompt}\n\nThe three models showed different approaches. GPT-4o was more detailed, Claude was more thoughtful, and Gemini was more concise.",
            },
        }
    )


if __name__ == "__main__":
    print("Starting mock UltraAI API server on http://localhost:8000")
    app.run(host="127.0.0.1", port=8000, debug=True)
