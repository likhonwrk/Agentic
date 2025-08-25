# 🤖 Agentic - AI Agent Platform

[![Docker](https://img.shields.io/badge/Docker-20.10+-blue.svg)](https://www.docker.com/)
[![Python](https://img.shields.io/badge/Python-3.9+-green.svg)](https://www.python.org/)
[![Vue.js](https://img.shields.io/badge/Vue.js-3.0+-4FC08D.svg)](https://vuejs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A comprehensive, self-contained AI agent platform that runs entirely locally using Docker Model Runner for LLM inference. Build, deploy, and manage intelligent agents without external API dependencies.

## 🌟 Key Features

- **🏠 Fully Local**: Run LLMs locally using Docker Model Runner - no cloud APIs required
- **🔧 Multi-Tool Support**: Browser automation, shell commands, file operations, web search
- **🖥️ VNC Integration**: Real-time sandbox viewing with remote desktop capabilities
- **⚡ Real-time Communication**: WebSocket and SSE for live agent interactions
- **🔒 Secure Sandboxing**: Isolated Docker environments for safe tool execution
- **📱 Modern UI**: Responsive Vue.js interface with dark theme
- **🔐 Authentication**: JWT-based security with role-based access control
- **📊 Session Management**: Persistent conversations with MongoDB/Redis

## 🏗️ Architecture

\`\`\`
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │    Sandbox      │
│   (Vue.js)      │◄──►│   (FastAPI)     │◄──►│   (Ubuntu)      │
│   Port: 5173    │    │   Port: 8000    │    │   Port: 8080    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐              │
         │              │   Docker LLM    │              │
         └──────────────►│  Model Runner   │◄─────────────┘
                        │  Port: 11434    │
                        └─────────────────┘
\`\`\`

### Service Ports
- **5173**: Web frontend (Vue.js + Vite)
- **8000**: Backend API (FastAPI)
- **8080**: Sandbox API (Tool execution)
- **5900**: VNC remote desktop
- **9222**: Chrome DevTools Protocol
- **11434**: Local LLM inference

## 🚀 Quick Start

### Prerequisites
- Docker Desktop 4.30+ (for Model Runner support)
- 8GB+ RAM (16GB recommended for larger models)
- 20GB+ free disk space

### 1. Clone Repository
\`\`\`bash
git clone https://github.com/likhonwrk/Agentic.git
cd Agentic
\`\`\`

### 2. Pull AI Model
Choose from available models on [Docker Hub AI](https://hub.docker.com/u/ai):

\`\`\`bash
# Recommended: IBM Granite (4.5GB, optimized for agents)
docker model pull ibm-granite/granite-3.1-8b-instruct

# Alternative options:
docker model pull meta-llama/llama-3.3-8b        # 5GB
docker model pull google/gemma-3-9b              # 5.5GB
docker model pull microsoft/phi-4                # 2.5GB (smaller)
\`\`\`

### 3. Start Development Environment
\`\`\`bash
# Start all services
./dev.sh up -d

# View logs
./dev.sh logs

# Stop services
./dev.sh down
\`\`\`

### 4. Access the Platform
- **Web Interface**: http://localhost:5173
- **API Documentation**: http://localhost:8000/docs
- **Sandbox API**: http://localhost:8080/docs

## 📁 Project Structure

\`\`\`
Agentic/
├── frontend/           # Vue.js web interface
│   ├── src/
│   │   ├── components/ # Reusable UI components
│   │   ├── pages/      # Page components
│   │   ├── services/   # API integration
│   │   └── types/      # TypeScript definitions
│   ├── Dockerfile.dev
│   └── package.json
├── backend/            # FastAPI server
│   ├── app/
│   │   ├── api/        # API routes
│   │   ├── core/       # Core services
│   │   ├── models/     # Data models
│   │   └── utils/      # Utilities
│   ├── Dockerfile.dev
│   └── requirements.txt
├── sandbox/            # Isolated execution environment
│   ├── app/            # Sandbox API
│   ├── supervisord.conf
│   └── Dockerfile.dev
├── mockserver/         # Testing mock server
├── docs/              # Documentation site
├── docker-compose-development.yml
├── dev.sh             # Development script
├── build.sh           # Build script
└── run.sh             # Production script
\`\`\`

## 🛠️ Development

### Available Scripts

\`\`\`bash
# Development (with hot reload)
./dev.sh up -d

# Build all services
./build.sh

# Production deployment
./run.sh

# View service logs
./dev.sh logs [service-name]

# Update documentation
./update_doc.sh
\`\`\`

### VS Code Integration
The project includes `.vscode/tasks.json` for integrated development:
- `Ctrl+Shift+P` → "Tasks: Run Task" → Select task

## 🤖 Supported AI Models

### Recommended Models from Docker Hub

| Model | Size | Use Case | Command |
|-------|------|----------|---------|
| **IBM Granite 3.1 8B** | 4.5GB | General agents, instruction following | `docker model pull ibm-granite/granite-3.1-8b-instruct` |
| **Meta Llama 3.3 8B** | 5GB | Reasoning, complex tasks | `docker model pull meta-llama/llama-3.3-8b` |
| **Google Gemma 3 9B** | 5.5GB | Tool calling, structured output | `docker model pull google/gemma-3-9b` |
| **Microsoft Phi-4** | 2.5GB | Lightweight, fast inference | `docker model pull microsoft/phi-4` |
| **SmolLM2 1.7B** | 1GB | Resource-constrained environments | `docker model pull huggingface/smollm2-1.7b` |

### Model Configuration
Edit `docker-compose-development.yml` to change the model:

\`\`\`yaml
services:
  llm:
    image: docker/model-runner:latest
    command: run --model ibm-granite/granite-3.1-8b-instruct --port 11434
    # ... rest of configuration
\`\`\`

## 🔧 Configuration

### Environment Variables

Create `.env` files in each service directory:

**Backend (.env)**
\`\`\`env
LLM_ENDPOINT=http://llm:11434/v1
MONGO_URI=mongodb://mongo:27017/agentic
REDIS_HOST=redis
JWT_SECRET=your-secret-key
\`\`\`

**Frontend (.env)**
\`\`\`env
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000/ws
\`\`\`

### MCP Server Configuration
Copy and customize the MCP configuration:
\`\`\`bash
cp mcp.json.example mcp.json
# Edit mcp.json to add your MCP servers
\`\`\`

## 🎯 Usage Examples

### Creating an Agent Session
\`\`\`python
import requests

# Create new session
response = requests.post("http://localhost:8000/api/sessions", json={
    "name": "My Agent Session",
    "agent_type": "general"
})
session_id = response.json()["session_id"]

# Send message to agent
requests.post(f"http://localhost:8000/api/sessions/{session_id}/messages", json={
    "content": "Help me analyze this website: https://example.com",
    "message_type": "user"
})
\`\`\`

### Browser Automation
\`\`\`javascript
// Frontend: Request browser action
const response = await fetch(`/api/sessions/${sessionId}/tools/browser`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    action: 'navigate',
    url: 'https://example.com'
  })
});
\`\`\`

## 🔒 Security Features

- **JWT Authentication**: Secure API access
- **Role-based Access Control**: Fine-grained permissions
- **Sandboxed Execution**: Isolated tool environments
- **Rate Limiting**: API protection
- **Input Validation**: Request sanitization
- **CORS Configuration**: Cross-origin security

## 📊 Monitoring & Debugging

### Health Checks
\`\`\`bash
# Check service health
curl http://localhost:8000/health
curl http://localhost:8080/health

# Monitor LLM service
curl http://localhost:11434/v1/models
\`\`\`

### Logs
\`\`\`bash
# View all logs
./dev.sh logs

# Specific service logs
./dev.sh logs backend
./dev.sh logs sandbox
./dev.sh logs llm
\`\`\`

### VNC Access
Connect to sandbox desktop:
- **VNC Viewer**: `localhost:5900`
- **Web VNC**: http://localhost:5173 (integrated NoVNC)

## 🚀 Deployment

### Production Deployment
\`\`\`bash
# Build production images
./build.sh

# Deploy to production
./run.sh

# Or use Docker Compose directly
docker-compose -f docker-compose.yml up -d
\`\`\`

### Railway Deployment
The project includes Railway configuration:
\`\`\`bash
# Deploy to Railway
railway up
\`\`\`

### Kubernetes (Roadmap)
Future support for K8s deployment with Helm charts.

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

### Development Guidelines
- Follow Python PEP 8 for backend code
- Use Vue 3 Composition API for frontend
- Add tests for new features
- Update documentation

## 📚 Documentation

- **API Documentation**: http://localhost:8000/docs (when running)
- **Architecture Guide**: [docs/architecture.md](docs/architecture.md)
- **Development Guide**: [docs/development.md](docs/development.md)
- **Deployment Guide**: [docs/deployment.md](docs/deployment.md)

## 🐛 Troubleshooting

### Common Issues

**Model not loading**
\`\`\`bash
# Check model availability
docker model list

# Pull model if missing
docker model pull ibm-granite/granite-3.1-8b-instruct
\`\`\`

**Port conflicts**
\`\`\`bash
# Check port usage
netstat -tulpn | grep :5173

# Stop conflicting services
./dev.sh down
\`\`\`

**Memory issues**
- Ensure 8GB+ RAM available
- Use smaller models (phi-4, smollm2)
- Enable swap if needed

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Docker Model Runner](https://www.docker.com/blog/introducing-docker-model-runner/) for local LLM inference
- [FastAPI](https://fastapi.tiangolo.com/) for the robust backend framework
- [Vue.js](https://vuejs.org/) for the reactive frontend
- [Playwright](https://playwright.dev/) for browser automation
- Open source AI models from Hugging Face, Meta, IBM, and Google

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/likhonwrk/Agentic/issues)
- **Discussions**: [GitHub Discussions](https://github.com/likhonwrk/Agentic/discussions)
- **Documentation**: [docs/](docs/)

---

**Built with ❤️ by [Likhon Sheikh](https://github.com/likhonwrk)**

*Empowering developers to build intelligent agents locally, privately, and efficiently.*
