#!/bin/bash

# Build script for Agentic AI Agent System
# Usage: ./build.sh [production|development]

set -e

BUILD_TYPE=${1:-production}

echo "🚀 Building Agentic AI Agent System for $BUILD_TYPE..."

# Create build directories
mkdir -p dist/{frontend,backend,sandbox}

if [ "$BUILD_TYPE" = "production" ]; then
    echo "📦 Building production images..."
    
    # Build frontend
    cd frontend
    npm run build
    cd ..
    
    # Build with production docker-compose
    docker-compose -f docker-compose.yml build --no-cache
    
    echo "✅ Production build completed!"
    echo "📋 Next steps:"
    echo "   1. Run: docker-compose up -d"
    echo "   2. Or deploy to Railway: railway up"
    
else
    echo "🔧 Building development images..."
    docker-compose -f docker-compose-development.yml build --no-cache
    echo "✅ Development build completed!"
    echo "📋 Next steps:"
    echo "   1. Run: ./dev.sh up"
fi
