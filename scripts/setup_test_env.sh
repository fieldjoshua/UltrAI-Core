#!/bin/bash
# Setup test environment for Ultra

echo "🔧 Ultra Test Environment Setup"
echo "=============================="

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to create .env.test if it doesn't exist
setup_test_env_file() {
    if [ ! -f .env.test ]; then
        echo "📝 Creating .env.test file..."
        cat > .env.test << 'EOF'
# Test Environment Configuration
TEST_MODE=OFFLINE
JWT_SECRET_KEY=test-secret-key-for-testing
ENVIRONMENT=test

# Database (for INTEGRATION mode)
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/ultra_test

# Redis (for INTEGRATION mode)
REDIS_URL=redis://localhost:6379/1

# LLM API Keys (for LIVE mode)
# OPENAI_API_KEY=your-key-here
# ANTHROPIC_API_KEY=your-key-here
# GOOGLE_API_KEY=your-key-here

# Production Test Token (for PRODUCTION mode)
# PRODUCTION_TEST_TOKEN=your-token-here
EOF
        echo "✅ Created .env.test with default configuration"
        echo "   Edit this file to add API keys for LIVE testing"
    else
        echo "✅ .env.test already exists"
    fi
}

# Function to check Python dependencies
check_python_deps() {
    echo ""
    echo "📦 Checking Python dependencies..."
    
    if command_exists poetry; then
        echo "✅ Poetry is installed"
        poetry install --no-interaction
    elif [ -f requirements.txt ]; then
        echo "⚠️  Poetry not found, using pip"
        pip install -r requirements.txt
    else
        echo "❌ No dependency file found"
        return 1
    fi
    
    # Install test-specific dependencies
    pip install pytest-timeout pytest-asyncio pytest-mock
}

# Function to setup local services
setup_local_services() {
    echo ""
    echo "🐳 Checking local services for INTEGRATION testing..."
    
    if command_exists docker; then
        echo "✅ Docker is installed"
        
        # Check if docker-compose.test.yml exists
        if [ ! -f docker-compose.test.yml ]; then
            echo "📝 Creating docker-compose.test.yml..."
            cat > docker-compose.test.yml << 'EOF'
version: '3.8'

services:
  postgres-test:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: ultra_test
    ports:
      - "5432:5432"
    volumes:
      - postgres-test-data:/var/lib/postgresql/data

  redis-test:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis-test-data:/data

volumes:
  postgres-test-data:
  redis-test-data:
EOF
            echo "✅ Created docker-compose.test.yml"
        fi
        
        read -p "Start local test services with Docker? (y/N) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            docker-compose -f docker-compose.test.yml up -d
            echo "✅ Test services started"
            echo "   PostgreSQL: localhost:5432"
            echo "   Redis: localhost:6379"
        fi
    else
        echo "⚠️  Docker not installed - INTEGRATION tests will require manual service setup"
    fi
}

# Function to display test mode information
show_test_modes() {
    echo ""
    echo "📋 Available Test Modes:"
    echo ""
    echo "  OFFLINE     - Fast unit tests with all dependencies mocked (default)"
    echo "  MOCK        - Tests with sophisticated mocks simulating real behavior"
    echo "  INTEGRATION - Tests against local PostgreSQL and Redis"
    echo "  LIVE        - Tests against real LLM providers (requires API keys)"
    echo "  PRODUCTION  - Tests against deployed production endpoints"
    echo ""
    echo "🚀 Quick Start Commands:"
    echo ""
    echo "  make test              - Run offline tests (default)"
    echo "  make test-mock         - Run tests with sophisticated mocks"
    echo "  make test-integration  - Run integration tests"
    echo "  make test-live         - Run live tests (costs money!)"
    echo "  make test-production   - Run production tests"
    echo ""
    echo "🔧 Manual Test Execution:"
    echo ""
    echo "  TEST_MODE=OFFLINE pytest tests/unit/ -v"
    echo "  TEST_MODE=MOCK pytest tests/ -v"
    echo "  TEST_MODE=INTEGRATION pytest tests/integration/ -v"
    echo "  TEST_MODE=LIVE pytest tests/live/ -v"
    echo ""
}

# Main setup flow
main() {
    echo ""
    
    # Check Python environment
    if [ -z "$VIRTUAL_ENV" ] && [ ! -f "/.dockerenv" ]; then
        echo "⚠️  Warning: Not in a virtual environment"
        echo "   Run 'source venv/bin/activate' or 'poetry shell' first"
        echo ""
    fi
    
    # Setup test environment file
    setup_test_env_file
    
    # Check Python dependencies
    check_python_deps
    
    # Setup local services
    setup_local_services
    
    # Show test modes
    show_test_modes
    
    echo "✅ Test environment setup complete!"
    echo ""
    echo "Next steps:"
    echo "1. Edit .env.test to add API keys for LIVE testing"
    echo "2. Run 'make test' to verify everything works"
    echo "3. Check tests/TEST_CONFIGURATION.md for detailed documentation"
}

# Run main function
main