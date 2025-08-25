#!/bin/bash

# Production run script for Agentic AI Agent System
# Usage: ./run.sh [start|stop|restart|status]

set -e

case "${1:-start}" in
    "start")
        echo "🚀 Starting Agentic production environment..."
        docker-compose up -d
        echo "✅ Services started successfully!"
        echo "🌐 Frontend: http://localhost:5173"
        echo "🔧 Backend API: http://localhost:8000"
        echo "📦 Sandbox API: http://localhost:8080"
        ;;
    "stop")
        echo "🛑 Stopping Agentic production environment..."
        docker-compose down
        echo "✅ Services stopped successfully!"
        ;;
    "restart")
        echo "🔄 Restarting Agentic production environment..."
        docker-compose restart
        echo "✅ Services restarted successfully!"
        ;;
    "status")
        docker-compose ps
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status}"
        exit 1
        ;;
esac
