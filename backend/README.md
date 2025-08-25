---
applyTo: "backend/**/*.py"
---

# AI Agent Backend

FastAPI-based backend for the AI Agent system with multi-modal capabilities, session management, and MCP integration.

## 🚀 Features

- **FastAPI Framework**: High-performance async API framework
- **Session Management**: Redis and MongoDB for persistent sessions
- **MCP Integration**: Model Context Protocol server support
- **Real-time Communication**: Server-Sent Events (SSE) for live updates
- **Docker Support**: Containerized deployment ready
- **Multi-modal Support**: Text, images, and file processing
- **Browser Automation**: Playwright and Puppeteer integration

## 🏗️ Architecture

```
backend/
├── app/
│   ├── domain/          # Core business logic
│   │   ├── models/      # Domain models
│   │   ├── services/    # Domain services
│   │   ├── external/    # External interfaces
│   │   └── prompts/     # AI prompt templates
│   ├── application/     # Application layer
│   │   ├── services/    # Application services
│   │   └── schemas/     # Data schemas
│   ├── interfaces/      # API interfaces
│   │   └── api/         # REST API routes
│   ├── infrastructure/  # Technical implementation
│   └── main.py          # Application entry point
├── requirements.txt     # Python dependencies
├── Dockerfile          # Docker configuration
├── dev.sh              # Development startup script
└── run.sh              # Production startup script
```

## 🛠️ Setup

### Prerequisites

- Python 3.11+
- Redis
- MongoDB
- Docker (optional)

### Local Development

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set environment variables**
   Create `.env` file:
   ```env
   HOST=0.0.0.0
   PORT=8000
   REDIS_URL=redis://localhost:6379
   MONGODB_URL=mongodb://localhost:27017
   OPENAI_API_KEY=your_openai_key
   ANTHROPIC_API_KEY=your_anthropic_key
   GOOGLE_API_KEY=your_google_key
   SECRET_KEY=your-secret-key
   JWT_SECRET_KEY=your-jwt-secret
   MCP_CONFIG_PATH=./mcp-config.json
   ```

3. **Start the backend**
   ```bash
   python main.py
   ```

### Docker Development

1. **Build and run**
   ```bash
   docker build -t agentic-backend .
   docker run -p 8000:8000 agentic-backend
   ```

2. **With Docker Compose**
   ```bash
   docker-compose up --build
   ```

## 📡 API Endpoints

### Session Management

- `POST /api/v1/sessions` - Create new session
- `GET /api/v1/sessions/{session_id}` - Get session info
- `GET /api/v1/sessions` - List all sessions
- `DELETE /api/v1/sessions/{session_id}` - Delete session
- `POST /api/v1/sessions/{session_id}/stop` - Stop session
- `POST /api/v1/sessions/{session_id}/chat` - Send message (SSE)

### Health Check

- `GET /health` - System health status

### Agent Operations

- `POST /agent/chat` - Direct chat with AI agent
- `POST /browser/execute` - Execute browser automation task

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| HOST | Server host | 0.0.0.0 |
| PORT | Server port | 8000 |
| REDIS_URL | Redis connection URL | redis://localhost:6379 |
| MONGODB_URL | MongoDB connection URL | mongodb://localhost:27017 |
| OPENAI_API_KEY | OpenAI API key | - |
| ANTHROPIC_API_KEY | Anthropic API key | - |
| GOOGLE_API_KEY | Google API key | - |
| SECRET_KEY | Application secret | - |
| JWT_SECRET_KEY | JWT signing secret | - |
| MCP_CONFIG_PATH | MCP configuration file path | ./mcp-config.json |

### MCP Configuration

The backend supports multiple MCP servers through the `mcp-config.json` file. See the main project README for MCP server details.

## 🧪 Testing

### Run tests
```bash
python -m pytest
```

### Run with coverage
```bash
python -m pytest --cov=app tests/
```

## 📦 Production Deployment

### Using Docker

1. **Build production image**
   ```bash
   docker build -t agentic-backend:prod .
   ```

2. **Run with environment**
   ```bash
   docker run -d \
     --name agentic-backend \
     -p 8000:8000 \
     -e REDIS_URL=redis://redis:6379 \
     -e MONGODB_URL=mongodb://mongodb:27017 \
     agentic-backend:prod
   ```

### Using systemd

Create `/etc/systemd/system/agentic-backend.service`:
```ini
[Unit]
Description=AI Agent Backend
After=network.target

[Service]
Type=exec
User=agentic
WorkingDirectory=/opt/agentic/backend
ExecStart=/opt/agentic/backend/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

## 🐛 Troubleshooting

### Common Issues

1. **Import errors**: Ensure all dependencies are installed
2. **Redis connection**: Check Redis is running and accessible
3. **MongoDB connection**: Verify MongoDB is running
4. **Port conflicts**: Ensure port 8000 is available
5. **Environment variables**: Check all required env vars are set

### Debug Mode

Enable debug logging:
```bash
export DEBUG=true
python main.py
```

## 🔗 Integration

### Frontend Integration

The backend is designed to work with the Vue.js frontend at:
- Development: http://localhost:5173
- Production: Configured via frontend build

### External Services

- **Redis**: Session storage and caching
- **MongoDB**: Persistent data storage
- **AI APIs**: OpenAI, Anthropic, Google APIs
- **MCP Servers**: Browser automation, file operations, etc.

## 📄 License

MIT License - see main project LICENSE file.