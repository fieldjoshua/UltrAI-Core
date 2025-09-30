#!/bin/bash
set -e

echo "🚀 Deploying to production..."

git push origin main

echo "⏳ Waiting for Render to detect changes..."
sleep 10

echo "📊 Checking service deploy status..."
./scripts/render-check-deploys.sh

echo "✅ Deploy initiated for all services"
echo "🔍 Monitor at: https://dashboard.render.com"