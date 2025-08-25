---
applyTo: "**/*"
---

# 🚀 Quick Start Guide

Get up and running with Agentic in under 5 minutes.

## Prerequisites

- **Docker Desktop 4.30+** (required for Model Runner)
- **8GB+ RAM** (16GB recommended for larger models)
- **20GB+ free disk space**

## Step 1: Clone the Repository

\`\`\`bash
git clone https://github.com/likhonwrk/Agentic.git
cd Agentic
\`\`\`

## Step 2: Pull an AI Model

Choose from available models on [Docker Hub AI](https://hub.docker.com/u/ai):

\`\`\`bash
# Recommended: IBM Granite (4.5GB, optimized for agents)
docker model pull ibm-granite/granite-3.1-8b-instruct

# Alternative options:
docker model pull meta-llama/llama-3.3-8b        # 5GB
docker model pull google/gemma-3-9b              # 5.5GB
docker model pull microsoft/phi-4                # 2.5GB (smaller)
\`\`\`

## Step 3: Start the Platform

\`\`\`bash
# Start all services in development mode
./dev.sh up -d

# Check status
./dev.sh logs
\`\`\`

## Step 4: Access the Interface

- **Web Interface**: http://localhost:5173
- **API Documentation**: http://localhost:8000/docs
- **Sandbox API**: http://localhost:8080/docs

## Step 5: Create Your First Agent

1. Open http://localhost:5173
2. Click "Create New Agent"
3. Choose agent type (Browser, API, Data, Chat)
4. Start chatting with your agent!

## Next Steps

- [Configuration Guide](configuration.md)
- [API Reference](api-reference.md)
- [Development Setup](development.md)

## Troubleshooting

**Model not loading?**
\`\`\`bash
# Check available models
docker model list

# Restart services
./dev.sh down && ./dev.sh up -d
\`\`\`

**Port conflicts?**
\`\`\`bash
# Check port usage
netstat -tulpn | grep :5173

# Stop conflicting services
./dev.sh down
\`\`\`

Need help? Check our [Troubleshooting Guide](troubleshooting.md) or [open an issue](https://github.com/likhonwrk/Agentic/issues).
