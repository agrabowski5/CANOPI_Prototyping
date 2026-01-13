#!/bin/bash
# Production startup script for CANOPI Energy Planning Platform

set -e

echo "=========================================="
echo "CANOPI Energy Planning Platform"
echo "Production Deployment Script"
echo "=========================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "Error: Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Load environment variables
if [ -f .env.prod ]; then
    echo "Loading production environment variables..."
    export $(cat .env.prod | grep -v '^#' | xargs)
else
    echo "Warning: .env.prod file not found. Using default values."
fi

# Check if Mapbox token is configured
if [ ! -f frontend/.env.production ]; then
    echo "Warning: frontend/.env.production not found. Creating from template..."
    cat > frontend/.env.production << EOF
REACT_APP_API_URL=/api
REACT_APP_API_TIMEOUT=30000
REACT_APP_MAPBOX_TOKEN=your_mapbox_token_here
REACT_APP_ENVIRONMENT=production
REACT_APP_VERSION=1.0.0
REACT_APP_ENABLE_ANALYTICS=false
REACT_APP_ENABLE_DEBUG=false
EOF
fi

echo ""
echo "Building Docker images..."
docker-compose -f docker-compose.prod.yml build

echo ""
echo "Starting production services..."
docker-compose -f docker-compose.prod.yml up -d

echo ""
echo "Waiting for services to be healthy..."
sleep 10

# Check service health
echo ""
echo "Checking service status..."
docker-compose -f docker-compose.prod.yml ps

echo ""
echo "=========================================="
echo "CANOPI is now running in production mode!"
echo "=========================================="
echo ""
echo "Access points:"
echo "  - Frontend:  http://localhost"
echo "  - Backend API: http://localhost:8000"
echo "  - API Docs: http://localhost:8000/api/docs"
echo "  - Flower (Celery): http://localhost:5555"
echo ""
echo "To view logs:"
echo "  docker-compose -f docker-compose.prod.yml logs -f"
echo ""
echo "To stop services:"
echo "  docker-compose -f docker-compose.prod.yml down"
echo ""
echo "To stop and remove volumes (WARNING: deletes data):"
echo "  docker-compose -f docker-compose.prod.yml down -v"
echo ""
