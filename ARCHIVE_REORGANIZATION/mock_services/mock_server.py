from flask import Flask

app = Flask(__name__)

@app.route(\"/api/health\")
def health():
    return {\"status\": \"ok\"}

@app.route(\"/api/analyze\", methods=[\"POST\"])
def analyze():
    return {
        \"status\": \"success\",
        \"results\": [
            {
                \"model\": \"gpt-4o\",
                \"provider\": \"openai\",
                \"response\": \"This is a simulated GPT-4o response.\"
            },
            {
                \"model\": \"claude-3-opus\",
                \"provider\": \"anthropic\",
                \"response\": \"This is a simulated Claude-3 response.\"
            }
        ]
    }

if __name__ == \"__main__\":
    print(\"Starting mock UltrAI API server on http://localhost:8085\")
    app.run(host=\"127.0.0.1\", port=8085)
