#!/bin/bash

# Local Registry Management Script
set -e

echo "🐳 Docker Desktop Registry Management"

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

case "$1" in
    "start")
        print_status "Starting local Docker registry..."
        docker run -d -p 5001:5000 --name registry registry:2
        print_status "Registry started at http://localhost:5001"
        ;;
    "stop")
        print_status "Stopping local Docker registry..."
        docker stop registry
        docker rm registry
        print_status "Registry stopped"
        ;;
    "status")
        if docker ps | grep -q registry; then
            print_status "Registry is running at http://localhost:5001"
        else
            print_warning "Registry is not running"
        fi
        ;;
    "list")
        print_status "Images in local registry:"
        curl -s http://localhost:5001/v2/_catalog | jq .
        ;;
    *)
        echo "Usage: $0 {start|stop|status|list}"
        echo ""
        echo "Commands:"
        echo "  start   - Start the local registry"
        echo "  stop    - Stop the local registry"
        echo "  status  - Check if registry is running"
        echo "  list    - List images in registry"
        exit 1
        ;;
esac
