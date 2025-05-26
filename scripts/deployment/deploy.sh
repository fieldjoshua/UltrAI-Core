#!/bin/bash
# Ultra MVP Deployment Script

echo "🚀 Starting Ultra MVP Deployment..."

# Check if .env.production exists
if [ ! -f .env.production ]; then
    echo "❌ Error: .env.production not found!"
    echo "Please create .env.production with your configuration"
    exit 1
fi

# Check if SSL certificates exist
if [ ! -f nginx/certs/api.crt ] || [ ! -f nginx/certs/api.key ]; then
    echo "⚠️  Warning: SSL certificates not found in nginx/certs/"
    echo "Using self-signed certificates for testing..."
    mkdir -p nginx/certs
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout nginx/certs/api.key \
        -out nginx/certs/api.crt \
        -subj "/CN=api.ultrai.app" \
        -quiet
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout nginx/certs/app.key \
        -out nginx/certs/app.crt \
        -subj "/CN=app.ultrai.app" \
        -quiet
fi

# Build images
echo "🔨 Building Docker images..."
docker build -t ultra-backend:latest . || exit 1
docker build -t ultra-frontend:latest ./frontend || exit 1

# Stop existing containers
echo "🛑 Stopping existing containers..."
docker-compose -f docker-compose.production.yml down

# Start services
echo "🚀 Starting services..."
docker-compose -f docker-compose.production.yml up -d

# Wait for database to be ready
echo "⏳ Waiting for database..."
sleep 10

# Run migrations
echo "📊 Running database migrations..."
docker-compose -f docker-compose.production.yml exec -T backend alembic upgrade head

# Show status
echo "✅ Deployment complete!"
echo ""
echo "📊 Service Status:"
docker-compose -f docker-compose.production.yml ps

echo ""
echo "🔍 Health Check:"
sleep 5
curl -s https://api.ultrai.app/api/health | jq . || echo "API not accessible via HTTPS yet"

echo ""
echo "📝 View logs:"
echo "docker-compose -f docker-compose.production.yml logs -f"

echo ""
echo "🌐 Access your application at:"
echo "Frontend: https://app.ultrai.app"
echo "API: https://api.ultrai.app"