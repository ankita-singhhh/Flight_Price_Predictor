#!/bin/bash

# Flight Price Predictor - Deployment Script
# This script automates the deployment process

set -e  # Exit on any error

echo "🚀 Starting Flight Price Predictor Deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    print_warning ".env file not found. Creating from template..."
    cp .env.example .env
    print_status "Please edit .env file with your configuration before continuing."
    print_status "Press Enter to continue or Ctrl+C to exit..."
    read -r
fi

# Create logs directory if it doesn't exist
mkdir -p logs

# Stop existing containers
print_status "Stopping existing containers..."
docker-compose down 2>/dev/null || true

# Build and start containers
print_status "Building Docker images..."
docker-compose build

print_status "Starting containers..."
docker-compose up -d

# Wait for application to be ready
print_status "Waiting for application to start..."
sleep 10

# Health check
print_status "Performing health check..."
if curl -f http://localhost:5000/health > /dev/null 2>&1; then
    print_status "✅ Application is healthy and running!"
else
    print_error "❌ Health check failed. Please check logs:"
    docker-compose logs web
    exit 1
fi

# Display access information
echo ""
print_status "🎉 Deployment completed successfully!"
echo ""
echo "📱 Access the application:"
echo "   Web Interface: http://localhost"
echo "   API Endpoint:  http://localhost/api/predict"
echo "   Health Check:  http://localhost/health"
echo ""
echo "📊 Monitor the application:"
echo "   View logs:     docker-compose logs -f"
echo "   Stop app:      docker-compose down"
echo "   Restart app:    docker-compose restart"
echo ""

# Show container status
print_status "Container status:"
docker-compose ps
