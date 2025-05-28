#!/bin/bash
# Script to start the Ultra application using Docker Compose

set -e

# Function to display usage information
show_usage() {
  echo "Usage: $0 [options]"
  echo
  echo "Options:"
  echo "  -h, --help                 Show this help message"
  echo "  -d, --detach               Run containers in detached mode"
  echo "  -b, --build                Build containers before starting"
  echo "  -r, --rebuild              Force rebuild containers before starting"
  echo "  -c, --clean                Remove all containers and volumes before starting"
  echo "  -l, --logs                 Show logs after starting in detached mode"
  echo "  -s, --service SERVICE      Start only specified service (e.g., backend, postgres, redis)"
  echo "  -e, --env-file FILE        Specify custom .env file (default: .env)"
  echo
  echo "Examples:"
  echo "  $0                         Start all services in foreground"
  echo "  $0 -d                      Start all services in detached mode"
  echo "  $0 -d -l                   Start all services in detached mode and show logs"
  echo "  $0 -b -s backend           Build and start only the backend service"
  echo "  $0 -c                      Clean up and start all services"
  echo
}

# Default options
DETACHED=""
BUILD=""
REBUILD=""
CLEAN=""
LOGS=""
SERVICE=""
ENV_FILE=".env"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case "$1" in
    -h|--help)
      show_usage
      exit 0
      ;;
    -d|--detach)
      DETACHED="-d"
      shift
      ;;
    -b|--build)
      BUILD="--build"
      shift
      ;;
    -r|--rebuild)
      REBUILD="--build --no-cache"
      shift
      ;;
    -c|--clean)
      CLEAN="yes"
      shift
      ;;
    -l|--logs)
      LOGS="yes"
      shift
      ;;
    -s|--service)
      SERVICE="$2"
      shift 2
      ;;
    -e|--env-file)
      ENV_FILE="$2"
      shift 2
      ;;
    *)
      echo "Unknown option: $1"
      show_usage
      exit 1
      ;;
  esac
done

# Check if .env file exists
if [ ! -f "$ENV_FILE" ]; then
  echo "Environment file '$ENV_FILE' not found. Creating from example..."
  if [ -f "env.example" ]; then
    cp env.example "$ENV_FILE"
    echo "Created $ENV_FILE from env.example. Please edit it with your configuration."
  else
    echo "env.example not found. Please create $ENV_FILE manually."
    exit 1
  fi
fi

# Clean up if requested
if [ "$CLEAN" = "yes" ]; then
  echo "Cleaning up containers and volumes..."
  docker-compose down -v
fi

# Check for Docker Compose
if ! command -v docker-compose &> /dev/null; then
  if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed or not in PATH"
    exit 1
  fi

  # Check if docker compose V2 is available
  if ! docker compose version &> /dev/null; then
    echo "Error: Neither docker-compose nor docker compose is available"
    echo "Please install Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
  fi

  # Use docker compose V2 syntax
  CMD="docker compose"
else
  # Use classic docker-compose
  CMD="docker-compose"
fi

# Create necessary directories
mkdir -p logs
mkdir -p document_storage
mkdir -p temp
mkdir -p temp_uploads

# Build and start containers
if [ -n "$REBUILD" ]; then
  echo "Rebuilding and starting containers..."
  $CMD up $DETACHED $REBUILD $SERVICE
elif [ -n "$BUILD" ]; then
  echo "Building and starting containers..."
  $CMD up $DETACHED $BUILD $SERVICE
else
  echo "Starting containers..."
  $CMD up $DETACHED $SERVICE
fi

# Show logs if requested and in detached mode
if [ "$LOGS" = "yes" ] && [ "$DETACHED" = "-d" ]; then
  echo "Showing logs..."
  if [ -n "$SERVICE" ]; then
    $CMD logs -f $SERVICE
  else
    $CMD logs -f
  fi
fi

# Print information if in detached mode
if [ "$DETACHED" = "-d" ] && [ "$LOGS" != "yes" ]; then
  echo
  echo "Containers are running in the background."
  echo "- To view logs: docker-compose logs -f"
  echo "- To stop containers: docker-compose down"
  echo "- Backend API is available at: http://localhost:8000"
  echo "- Frontend is available at: http://localhost:3009"
  echo
fi
