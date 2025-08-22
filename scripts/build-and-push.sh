#!/bin/bash

# Build and Push Script for Stock Portfolio
set -e

echo "🔨 Building and pushing Stock Portfolio image..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Configuration
REGISTRY_URL="localhost:5001"  # Docker Desktop local registry
IMAGE_NAME="stock-portfolio"
TAG="latest"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

# Build the image
print_status "Building Docker image..."
docker build -t $IMAGE_NAME:$TAG .

# Tag for registry
FULL_IMAGE_NAME="$REGISTRY_URL/$IMAGE_NAME:$TAG"
print_status "Tagging image as $FULL_IMAGE_NAME..."
docker tag $IMAGE_NAME:$TAG $FULL_IMAGE_NAME

# Push to registry
print_status "Pushing image to registry..."
docker push $FULL_IMAGE_NAME

print_status "Image successfully pushed to registry! 🎉"
print_status "You can now deploy using: ./scripts/deploy.sh --registry"
