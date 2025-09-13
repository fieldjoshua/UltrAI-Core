#!/bin/bash
#
# Setup script for local E2E testing
# This configures the frontend to connect to local backend
#

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[SETUP]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Navigate to frontend directory
cd "$(dirname "$0")/../frontend"

# Create local environment file for testing
print_status "Creating local environment configuration..."

cat > .env.local << EOF
# Local E2E testing configuration
# This file is used when running E2E tests locally

# Connect to local backend instead of production
VITE_API_URL=http://localhost:8000/api

# Other test-specific settings can go here
EOF

print_status "Frontend configured for local testing"
print_status "The frontend will now connect to http://localhost:8000/api"

# Also create a script to restore production settings
cat > ../scripts/restore-production.sh << 'EOF'
#!/bin/bash
# Restore production settings by removing local overrides
cd "$(dirname "$0")/../frontend"
rm -f .env.local
echo "Frontend restored to production settings"
EOF

chmod +x ../scripts/restore-production.sh

print_status "Setup complete!"
echo ""
print_warning "To restore production settings later, run: ./scripts/restore-production.sh"