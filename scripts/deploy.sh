#!/bin/bash

# Stock Portfolio Deployment Script
set -e

echo "🚀 Starting Stock Portfolio deployment..."

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

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    print_error "kubectl is not installed. Please install kubectl and try again."
    exit 1
fi

# Check if minikube is running (for local development)
if command -v minikube &> /dev/null; then
    if ! minikube status | grep -q "Running"; then
        print_warning "Minikube is not running. Starting minikube..."
        minikube start
    fi
    # Set Docker environment for minikube
    eval $(minikube docker-env)
fi

print_status "Building Docker image..."
docker build -t stock-portfolio:latest .

print_status "Deploying Redis..."
kubectl apply -f k8s/redis-deployment.yaml

print_status "Waiting for Redis to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/redis

print_status "Deploying Stock Portfolio application..."
kubectl apply -f k8s/stock-portfolio-deployment.yaml

print_status "Waiting for application to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/stock-portfolio

print_status "Getting service URLs..."

if command -v minikube &> /dev/null; then
    print_status "Minikube detected. Getting service URL..."
    MINIKUBE_IP=$(minikube ip)
    print_status "Application URL: http://$MINIKUBE_IP:$(kubectl get service stock-portfolio-service -o jsonpath='{.spec.ports[0].nodePort}')"
else
    print_status "Getting LoadBalancer IP..."
    kubectl get service stock-portfolio-service
fi

print_status "Deployment completed successfully! 🎉"

# Show logs
print_status "Showing application logs..."
kubectl logs -f deployment/stock-portfolio --tail=50 