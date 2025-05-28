#!/bin/bash

# Render CLI Deployment Script
# Handles deployment with verification for UltraAI production service

set -e  # Exit on any error

# Configuration
RENDER_CLI_PATH="/Users/joshuafield/.local/bin/render"
PRODUCTION_URL="https://ultrai-core-4lut.onrender.com"
SERVICE_NAME="ultrai-core"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 UltraAI Render Deployment Script${NC}"
echo "=================================="

# Function to print status messages
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Add Render CLI to PATH
export PATH=$PATH:/Users/joshuafield/.local/bin

# Verify CLI is available
if ! command -v render &> /dev/null; then
    print_error "Render CLI not found. Please install it first."
    exit 1
fi

print_status "Render CLI version: $(render --version)"

# Check authentication
print_status "Checking authentication..."
if ! render whoami &> /dev/null; then
    print_error "Not authenticated with Render. Please run: render login"
    exit 1
fi

AUTH_INFO=$(render whoami)
print_success "Authenticated as: $AUTH_INFO"

# Pre-deployment checks
print_status "Running pre-deployment checks..."

# Check git status
if [ -n "$(git status --porcelain)" ]; then
    print_warning "Working directory has uncommitted changes:"
    git status --short
    read -p "Continue with deployment? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_error "Deployment cancelled"
        exit 1
    fi
fi

# Check if we're on main branch
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "main" ]; then
    print_warning "Currently on branch: $CURRENT_BRANCH (not main)"
    read -p "Continue with deployment? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_error "Deployment cancelled"
        exit 1
    fi
fi

print_success "Pre-deployment checks completed"

# Get current production status
print_status "Checking current production status..."
CURRENT_HEALTH=$(curl -s "$PRODUCTION_URL/health" || echo "failed")
print_status "Current production health: $CURRENT_HEALTH"

# Note: Due to CLI limitations with non-interactive mode, we'll provide instructions
# for manual deployment trigger and then verify the results

echo ""
print_status "Due to Render CLI limitations in non-interactive mode, please:"
echo "1. Go to Render Dashboard: https://dashboard.render.com"
echo "2. Navigate to the '$SERVICE_NAME' service"
echo "3. Click 'Manual Deploy' -> 'Deploy latest commit'"
echo "4. Monitor the deployment progress"
echo ""
read -p "Press Enter when deployment is complete and service shows 'Live' status..."

# Post-deployment verification
print_status "Starting post-deployment verification..."

# Wait a moment for service to stabilize
sleep 5

# Test health endpoint
print_status "Testing health endpoint..."
HEALTH_RESPONSE=$(curl -s "$PRODUCTION_URL/health" | jq '.' 2>/dev/null || echo "failed")
if [ "$HEALTH_RESPONSE" != "failed" ]; then
    print_success "Health endpoint responding"
    echo "$HEALTH_RESPONSE"
else
    print_error "Health endpoint failed"
fi

# Test sophisticated orchestrator endpoints
print_status "Testing sophisticated orchestrator endpoints..."

# Test models endpoint
MODELS_TEST=$(curl -s "$PRODUCTION_URL/api/orchestrator/models" 2>/dev/null || echo "failed")
if [ "$MODELS_TEST" != "failed" ] && [ "$MODELS_TEST" != '{"detail":"Not Found"}' ]; then
    print_success "Orchestrator models endpoint found"
else
    print_error "Orchestrator models endpoint not found - may be using antiquated code"
fi

# Test patterns endpoint
PATTERNS_TEST=$(curl -s "$PRODUCTION_URL/api/orchestrator/patterns" 2>/dev/null || echo "failed")
if [ "$PATTERNS_TEST" != "failed" ] && [ "$PATTERNS_TEST" != '{"detail":"Not Found"}' ]; then
    print_success "Orchestrator patterns endpoint found"
else
    print_error "Orchestrator patterns endpoint not found - may be using antiquated code"
fi

# Test feather endpoint
FEATHER_TEST=$(curl -s "$PRODUCTION_URL/api/orchestrator/feather" 2>/dev/null || echo "failed")
if [ "$FEATHER_TEST" != "failed" ] && [ "$FEATHER_TEST" != '{"detail":"Not Found"}' ]; then
    print_success "Feather orchestration endpoint found"
else
    print_error "Feather orchestration endpoint not found - may be using antiquated code"
fi

# Test OpenAPI documentation
print_status "Checking OpenAPI documentation..."
OPENAPI_TEST=$(curl -s "$PRODUCTION_URL/openapi.json" | jq '.paths | keys | length' 2>/dev/null || echo "0")
print_status "Available API endpoints: $OPENAPI_TEST"

# Final verification summary
echo ""
print_status "Deployment Verification Summary"
echo "==============================="
echo "Production URL: $PRODUCTION_URL"
echo "Health Status: $(echo "$HEALTH_RESPONSE" | jq -r '.status // "unknown"' 2>/dev/null || echo "unknown")"
echo "Timestamp: $(date)"
echo ""

if [ "$MODELS_TEST" != "failed" ] && [ "$PATTERNS_TEST" != "failed" ]; then
    print_success "✅ Sophisticated orchestrator endpoints detected"
    print_success "✅ Deployment appears successful"
else
    print_error "❌ Sophisticated orchestrator endpoints not found"
    print_error "❌ May be running antiquated code - check deployment"
fi

echo ""
print_status "Deployment script completed"