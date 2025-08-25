# Agentic AI Platform Coding Agent Instructions

## Repository Overview

Agentic is a distributed, containerized AI agent system built with browser automation, MCP (Model Context Protocol) integration, and multi-modal capabilities. The system consists of four main components:

1. Frontend (Vue.js/TypeScript)
2. Backend (Python/FastAPI) 
3. Sandbox (Ubuntu Container)
4. LLM Service (Docker Model Runner)

### Key Project Information
- Languages: Python, TypeScript
- Frameworks: Vue.js 3, FastAPI
- Runtime Requirements: Node.js, Python 3.8+, Docker
- Database: MongoDB, Redis
- Project Size: Medium
- Key Dependencies: OpenAI API, Chrome/Puppeteer, VNC

## Build and Validation Steps

### Prerequisites
- Docker and Docker Compose installed
- Node.js 16+ for frontend development
- Python 3.8+ for backend development
- Git

### Development Environment Setup
1. Clone and enter the repository:
```bash
git clone https://github.com/YOUR_USERNAME/Agentic.git
cd Agentic
```

2. Start development environment:
```bash
./dev.sh up -d
```

### Build Steps
Always execute in this order:

1. Frontend build:
```bash
cd frontend
npm install
npm run build
```

2. Backend setup:
```bash
cd backend
pip install -r requirements.txt
```

3. Full system build:
```bash
docker-compose -f docker-compose.yml up -d --build
```

### Validation Steps

1. Type checking:
```bash
cd frontend && npm run type-check
```

2. Linting:
```bash
# Frontend
cd frontend
npm run lint

# Backend 
cd backend
flake8 .
black . --check
```

3. Tests:
```bash
# Backend tests
cd backend
pytest tests/

# Frontend tests 
cd frontend
npm run test

# Integration tests
./dev.sh test
```

### Common Build Issues and Solutions

1. Frontend build fails:
   - Clear node_modules and package-lock.json
   - Run npm install with --legacy-peer-deps
   - Ensure compatible Node.js version (16+)

2. Docker build issues:
   - Ensure Docker daemon is running
   - Clean Docker cache: docker system prune
   - Check available disk space

3. Backend dependency conflicts:
   - Use a clean virtual environment
   - Update pip: pip install --upgrade pip
   - Install requirements with --no-cache-dir

## Project Structure and Architecture

### Key Directories
```
/
├── frontend/               # Vue.js frontend
│   ├── src/
│   │   ├── components/    # Vue components
│   │   ├── services/      # API services
│   │   └── types/         # TypeScript types
├── backend/               # FastAPI backend
│   ├── api/              # API routes
│   ├── core/             # Business logic
│   ├── models/           # Data models
│   └── utils/            # Utilities
├── sandbox/              # Isolation container
└── docs/                # Documentation
```

### Important Configuration Files
- `/docker-compose.yml` - Main Docker configuration
- `/docker-compose-development.yml` - Development setup
- `/frontend/tsconfig.json` - TypeScript config
- `/frontend/vite.config.ts` - Vite bundler config
- `/backend/requirements.txt` - Python dependencies
- `/mcp-config.json` - Model Context Protocol config

### Key Architecture Points
1. All browser automation runs in sandbox container
2. API routes require JWT authentication
3. WebSocket used for real-time communication
4. Redis handles session management
5. MongoDB stores persistent data
6. MCP servers handle tool integration

### Pre-Commit Validations
All changes must pass:
1. Type checking
2. Linting
3. Unit tests
4. Integration tests
5. Format verification

### Continuous Integration
GitHub Actions workflow validates:
1. Build success
2. Test passage
3. Linting compliance
4. Type safety
5. Docker build

## Development Guidelines

1. Always use TypeScript strict mode in frontend
2. Follow PEP 8 style guide in Python code
3. Add type hints for all Python functions
4. Document new APIs in OpenAPI format
5. Add tests for new features
6. Follow conventional commit format
7. Keep dependencies updated

Remember to trust these instructions and only perform additional searches if information is incomplete or needs verification.
