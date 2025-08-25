#!/bin/bash

# Railway Deployment Script for AI Agent System
set -e

echo "🚀 Starting Railway deployment for AI Agent System..."

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Installing..."
    npm install -g @railway/cli
fi

# Login to Railway (if not already logged in)
echo "🔐 Checking Railway authentication..."
railway login

# Create new project or link existing one
echo "📦 Setting up Railway project..."
if [ ! -f ".railway" ]; then
    railway init
else
    echo "✅ Railway project already linked"
fi

# Set environment variables
echo "🔧 Setting up environment variables..."

# Required environment variables
railway variables set NODE_ENV=production
railway variables set PYTHONPATH=/app/backend
railway variables set DOCKER_CONTAINER=true
railway variables set LOG_LEVEL=INFO
railway variables set HOST=0.0.0.0
railway variables set PORT=8000
railway variables set BROWSER_HEADLESS=true
railway variables set BROWSER_TIMEOUT=30000
railway variables set MCP_CONFIG_PATH=/app/mcp-config.json
railway variables set ACCESS_TOKEN_EXPIRE_MINUTES=30
railway variables set MAX_WORKERS=4
railway variables set WORKER_TIMEOUT=300

# Generate secure secret key if not provided
if [ -z "$SECRET_KEY" ]; then
    SECRET_KEY=$(openssl rand -hex 32)
    railway variables set SECRET_KEY="$SECRET_KEY"
    echo "🔑 Generated new SECRET_KEY"
fi

# Set API keys if provided
if [ ! -z "$OPENAI_API_KEY" ]; then
    railway variables set OPENAI_API_KEY="$OPENAI_API_KEY"
    echo "✅ Set OpenAI API key"
fi

if [ ! -z "$ANTHROPIC_API_KEY" ]; then
    railway variables set ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY"
    echo "✅ Set Anthropic API key"
fi

if [ ! -z "$GROQ_API_KEY" ]; then
    railway variables set GROQ_API_KEY="$GROQ_API_KEY"
    echo "✅ Set Groq API key"
fi

# Add Redis addon
echo "📊 Adding Redis addon..."
railway add redis

# Add MongoDB addon
echo "🗄️ Adding MongoDB addon..."
railway add mongodb

# Deploy the application
echo "🚀 Deploying to Railway..."
railway up --detach

# Wait for deployment
echo "⏳ Waiting for deployment to complete..."
sleep 30

# Get the deployment URL
DEPLOYMENT_URL=$(railway status --json | jq -r '.deployments[0].url')

echo "✅ Deployment completed successfully!"
echo "🌐 Your AI Agent System is available at: $DEPLOYMENT_URL"
echo "📊 Health check: $DEPLOYMENT_URL/health"
echo "📚 API docs: $DEPLOYMENT_URL/docs"

# Run health check
echo "🏥 Running health check..."
if curl -f "$DEPLOYMENT_URL/health" > /dev/null 2>&1; then
    echo "✅ Health check passed!"
else
    echo "❌ Health check failed. Check the logs with: railway logs"
fi

echo "🎉 Deployment script completed!"
