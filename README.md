# AI Agent System

A powerful AI agent system with browser automation, MCP integration, and multi-modal capabilities.

## 🚀 Features

- **Multi-Agent System**: Support for multiple AI agents with different capabilities
- **Browser Automation**: Automated web browsing using Playwright and Selenium
- **MCP Integration**: Model Context Protocol servers for extended functionality
- **Real-time Communication**: WebSocket support for live interactions
- **Session Management**: Persistent conversation sessions with Redis and MongoDB
- **VNC Visualization**: Remote desktop viewing for browser automation
- **Docker Support**: Containerized deployment with all dependencies

## 🏗️ Architecture

```
Agentic/
├── frontend/          # Vue.js frontend application
├── backend/           # FastAPI Python backend
├── docker-compose.yml # Docker orchestration
├── Dockerfile        # Multi-stage build configuration
└── mcp-config.json   # MCP server configurations
```

## 🛠️ Quick Start

### Prerequisites

- Docker and Docker Compose
- Node.js 20+ (for local development)
- Python 3.11+ (for local development)

### Using Docker (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Agentic
   ```

2. **Start the services**
   ```bash
   docker-compose up --build
   ```

3. **Access the application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - Health Check: http://localhost:8000/health

### Local Development

#### Frontend Setup

1. **Install dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Start development server**
   ```bash
   npm run dev
   ```

#### Backend Setup

1. **Install dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Start the backend**
   ```bash
   python main.py
   ```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```env
# Server Configuration
HOST=0.0.0.0
PORT=8000

# Database Configuration
REDIS_URL=redis://localhost:6379
MONGODB_URL=mongodb://localhost:27017

# AI API Keys
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
GOOGLE_API_KEY=your_google_key

# Security
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret

# MCP Configuration
MCP_CONFIG_PATH=./mcp-config.json
```

### MCP Servers

The system supports multiple MCP servers:
- **Playwright**: Browser automation
- **Puppeteer**: Web scraping and automation
- **Fetch**: HTTP requests and web content
- **Filesystem**: File operations
- **Memory**: Persistent storage
- **Sequential Thinking**: Advanced reasoning

## 📡 API Endpoints

### Session Management

- `POST /api/v1/sessions` - Create new session
- `GET /api/v1/sessions/{session_id}` - Get session info
- `GET /api/v1/sessions` - List all sessions
- `DELETE /api/v1/sessions/{session_id}` - Delete session
- `POST /api/v1/sessions/{session_id}/stop` - Stop session
- `POST /api/v1/sessions/{session_id}/chat` - Send message (SSE)

### Agent Operations

- `POST /agent/chat` - Chat with AI agent
- `POST /browser/execute` - Execute browser task
- `GET /health` - System health check

## 🐛 Troubleshooting

### Common Issues

1. **Port conflicts**: Ensure ports 5173, 8000, 6379, 27017 are available
2. **Docker permissions**: Run `docker-compose` with appropriate permissions
3. **Missing environment variables**: Check all required env vars are set
4. **Browser automation**: Ensure Chrome/Chromium is available

### Logs

- Backend logs: `docker-compose logs ai-agent-system`
- Frontend logs: `docker-compose logs frontend`
- Database logs: `docker-compose logs redis` / `docker-compose logs mongodb`

## 🧪 Testing

### Frontend Tests
```bash
cd frontend
npm run test
```

### Backend Tests
```bash
cd backend
python -m pytest
```

## 📦 Deployment

### Production Build

1. **Build frontend**
   ```bash
   cd frontend
   npm run build
   ```

2. **Build Docker image**
   ```bash
   docker build -t agentic-system .
   ```

3. **Deploy with Docker Compose**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- [Documentation](docs/)
- [API Reference](docs/api.md)
- [MCP Server Docs](docs/mcp-servers.md)
- [Contributing Guide](CONTRIBUTING.md)
