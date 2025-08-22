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

# Check deployment mode
USE_REGISTRY=false
if [[ "$1" == "--registry" ]]; then
    USE_REGISTRY=true
    print_warning "Registry mode: will pull image from registry instead of building"
fi

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

# Check and start minikube if needed
if command -v minikube &> /dev/null; then
    if ! minikube status | grep -q "Running"; then
        print_warning "Minikube is not running. Starting minikube..."
        # Check if there's an existing cluster that might have certificate issues
        if minikube status | grep -q "Stopped\|Saved\|Nonexistent"; then
            print_warning "Existing minikube cluster found. Deleting to avoid certificate issues..."
            minikube delete
        fi
        minikube start
    else
        # Check if the running cluster has certificate issues
        if minikube status | grep -q "kubelet: Stopped\|apiserver: Stopped"; then
            print_warning "Minikube cluster has issues. Deleting and recreating..."
            minikube delete
            minikube start
        fi
    fi
    # Set Docker environment for minikube
    eval $(minikube docker-env)
else
    print_error "Minikube is not installed. Please install minikube and try again."
    exit 1
fi

# Handle image deployment based on mode
if [[ "$USE_REGISTRY" == "true" ]]; then
    # Registry mode - pull image from registry
    print_status "Pulling Docker image from local registry..."
    docker pull localhost:5001/stock-portfolio:latest
    docker tag localhost:5001/stock-portfolio:latest stock-portfolio:latest
else
    # Local mode - build image in minikube context
    print_status "Building Docker image in minikube context..."
    docker build -t stock-portfolio:latest .
fi

# Deploy Redis
print_status "Deploying Redis..."
kubectl apply -f k8s/redis-deployment.yaml

print_status "Waiting for Redis to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/redis

# Deploy application secret
print_status "Deploying Stock Portfolio secret..."
kubectl apply -f k8s/stock-portfolio-secret.yaml

# Deploy Stock Portfolio application
print_status "Deploying Stock Portfolio application..."
if [[ "$USE_REGISTRY" == "true" ]]; then
    kubectl apply -f k8s/stock-portfolio-deployment.yaml
else
    kubectl apply -f k8s/stock-portfolio-deployment-local.yaml
fi

print_status "Waiting for application to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/stock-portfolio

# Get service URL
print_status "Getting service URL..."
MINIKUBE_IP=$(minikube ip)
NODEPORT=$(kubectl get service stock-portfolio-service -o jsonpath='{.spec.ports[0].nodePort}')
print_status "Application URL: http://$MINIKUBE_IP:$NODEPORT"

print_status "Deployment completed successfully! 🎉"

# Show logs
print_status "Showing application logs..."
kubectl logs -f deployment/stock-portfolio --tail=50 