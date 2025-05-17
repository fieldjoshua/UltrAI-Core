#!/bin/bash

# Restart the Ultra API server
# This script will restart the server (assume we're running in development mode with hot reload)

echo "Touching app.py to trigger hot reload..."
touch /Users/joshuafield/Documents/Ultra/backend/app.py

# Wait for the server to restart
echo "Waiting for server to restart..."
sleep 5

# Test that the server is running
echo "Testing server health..."
curl -s http://localhost:8085/api/health

echo ""
echo "Server restarted! Available Models endpoint should now be accessible."
echo "You can test it with: curl http://localhost:8085/api/available-models -H 'X-Test-Mode: true'"
