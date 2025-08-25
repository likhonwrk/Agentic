#!/bin/bash

# Development script for Agentic AI Agent System
# Usage: ./dev.sh [up|down|logs|restart|build]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker first."
        exit 1
    fi
}

# Create necessary directories
create_directories() {
    print_status "Creating project directories..."
    mkdir -p frontend/src/{components,pages,services,types,assets}
    mkdir -p backend/{core,api,utils,scripts}
    mkdir -p sandbox/{api,tools,vnc}
    mkdir -p mockserver
    mkdir -p docs
    mkdir -p deploy
    mkdir -p data/{mongodb,redis}
    mkdir -p logs
}

# Pull required Docker images
pull_images() {
    print_status "Pulling required Docker images..."
    
    # AI models from Docker Hub
    docker pull ai/llama2:latest || print_warning "Failed to pull ai/llama2:latest"
    docker pull ai/mistral:latest || print_warning "Failed to pull ai/mistral:latest"
    docker pull ai/codellama:latest || print_warning "Failed to pull ai/codellama:latest"
    
    # MCP and browser automation
    docker pull mcp/puppeteer:latest || print_warning "Failed to pull mcp/puppeteer:latest"
    docker pull browseruse/browseruse:buildcache || print_warning "Failed to pull browseruse/browseruse:buildcache"
    
    # Infrastructure
    docker pull mongo:7
    docker pull redis:7-alpine
    docker pull nginx:alpine
}

# Main command handling
case "${1:-up}" in
    "up")
        check_docker
        create_directories
        pull_images
        print_status "Starting Agentic development environment..."
        docker-compose -f docker-compose-development.yml up -d
        print_status "Services started successfully!"
        print_status "Frontend: http://localhost:5173"
        print_status "Backend API: http://localhost:8000"
        print_status "Sandbox API: http://localhost:8080"
        print_status "VNC Viewer: http://localhost:5900"
        print_status "Chrome CDP: http://localhost:9222"
        ;;
    "down")
        print_status "Stopping Agentic development environment..."
        docker-compose -f docker-compose-development.yml down
        print_status "Services stopped successfully!"
        ;;
    "logs")
        if [ -n "$2" ]; then
            docker-compose -f docker-compose-development.yml logs -f "$2"
        else
            docker-compose -f docker-compose-development.yml logs -f
        fi
        ;;
    "restart")
        print_status "Restarting Agentic development environment..."
        docker-compose -f docker-compose-development.yml restart
        print_status "Services restarted successfully!"
        ;;
    "build")
        check_docker
        print_status "Building Agentic services..."
        docker-compose -f docker-compose-development.yml build --no-cache
        print_status "Build completed successfully!"
        ;;
    "status")
        docker-compose -f docker-compose-development.yml ps
        ;;
    "clean")
        print_warning "This will remove all containers, images, and volumes. Are you sure? (y/N)"
        read -r response
        if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
            docker-compose -f docker-compose-development.yml down -v --rmi all
            docker system prune -f
            print_status "Cleanup completed!"
        fi
        ;;
    *)
        echo "Usage: $0 {up|down|logs|restart|build|status|clean}"
        echo ""
        echo "Commands:"
        echo "  up       - Start all services"
        echo "  down     - Stop all services"
        echo "  logs     - Show logs (optionally specify service name)"
        echo "  restart  - Restart all services"
        echo "  build    - Build all services"
        echo "  status   - Show service status"
        echo "  clean    - Remove all containers and images"
        exit 1
        ;;
esac
