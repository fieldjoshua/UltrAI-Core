#!/usr/bin/env python3
import http.server
import socketserver
import os

# Change to the frontend dist directory
os.chdir('/Users/joshuafield/Documents/Ultra/frontend/dist')

PORT = 3000

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        super().end_headers()

    def do_GET(self):
        # Serve index.html for all routes (SPA routing)
        if not os.path.exists(self.path[1:]) and not self.path.startswith('/assets'):
            self.path = '/index.html'
        return super().do_GET()

with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
    print(f"Frontend server running at http://localhost:{PORT}")
    print("Test your models loading at step 4!")
    httpd.serve_forever()