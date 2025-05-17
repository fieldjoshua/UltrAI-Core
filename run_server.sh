#!/bin/bash
set -e

echo "Stopping Docker containers..."
docker-compose stop

echo "Starting simple mock server..."
python3 -c "
from http.server import HTTPServer, BaseHTTPRequestHandler
import json

class SimpleHandler(BaseHTTPRequestHandler):
    def _set_headers(self, content_type='application/json'):
        self.send_response(200)
        self.send_header('Content-type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers()
        self.wfile.write(b'{}')

    def do_GET(self):
        self._set_headers()

        if self.path == '/api/health':
            response = {'status': 'ok', 'uptime': 123}
        elif self.path == '/api/available-models':
            response = {
                'status': 'success',
                'available_models': [
                    'gpt4o',
                    'claude3opus',
                    'gemini15'
                ]
            }
        else:
            response = {'status': 'success', 'message': 'Mock API endpoint'}

        self.wfile.write(json.dumps(response).encode())

    def do_POST(self):
        content_length = int(self.headers['Content-Length']) if 'Content-Length' in self.headers else 0
        post_data = self.rfile.read(content_length).decode('utf-8')

        try:
            data = json.loads(post_data) if post_data else {}
        except:
            data = {}

        self._set_headers()

        if self.path == '/api/analyze':
            prompt = data.get('prompt', 'No prompt provided')
            selected_models = data.get('selected_models', ['gpt4o'])

            response = {
                'status': 'success',
                'analysis_id': 'analysis_123456789',
                'results': {
                    'model_responses': {
                        model: {
                            'response': f'Response from {model} for: {prompt[:50]}...',
                            'time_taken': 2.5,
                            'tokens_used': 150
                        } for model in selected_models
                    },
                    'ultra_response': f'Ultra analysis of: {prompt[:50]}...',
                    'performance': {
                        'total_time_seconds': 5.0,
                        'model_times': {model: 2.5 for model in selected_models},
                        'token_counts': {model: 150 for model in selected_models}
                    }
                }
            }
        else:
            response = {'status': 'error', 'message': 'Unknown endpoint'}

        self.wfile.write(json.dumps(response).encode())

# Run the server on port 8086
print('Starting mock server on port 8086...')
server = HTTPServer(('0.0.0.0', 8086), SimpleHandler)
server.serve_forever()
"
