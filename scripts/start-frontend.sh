#!/bin/bash

# Start the frontend
cd "$(dirname "$0")/../frontend" || exit

echo "Starting Ultra frontend development server..."
echo "The frontend will be available at http://localhost:3009"

npm run dev

echo "Frontend server stopped." 