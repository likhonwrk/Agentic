# 🏗️ System Architecture

Agentic is built as a distributed, containerized system designed for scalability and modularity, with a focus on composable, markdown-driven development.

## Design Philosophy

### Markdown-First Development
- Define agents and workflows in plain Markdown
- Auto-generate code from markdown specifications
- Version control friendly documentation
- Single source of truth for system behavior

### State Machine Generation
- Convert Mermaid diagrams to XState machines
- Visual workflow representation
- Automatic code generation
- Type-safe state transitions

### Composable Architecture
- Build complex systems from simple components
- Reusable agent definitions
- Plug-and-play workflow modules
- Type-safe composition patterns

## High-Level Architecture

\`\`\`
┌─────────────────────────────────────────────────────────────────┐
│                        Agentic Platform                        │
├─────────────────┬─────────────────┬─────────────────┬───────────┤
│   Frontend      │    Backend      │    Sandbox      │    LLM    │
│   (Vue.js)      │   (FastAPI)     │   (Ubuntu)      │  (Docker) │
│   Port: 5173    │   Port: 8000    │   Port: 8080    │Port: 11434│
└─────────────────┴─────────────────┴─────────────────┴───────────┘
         │                 │                 │             │
         │        ┌────────┴────────┐        │             │
         │        │   Data Layer    │        │             │
         │        │ MongoDB + Redis │        │             │
         │        └─────────────────┘        │             │
         │                 │                 │             │
         └─────────────────┼─────────────────┼─────────────┘
                           │                 │
                  ┌────────┴────────┐       │
                  │  External APIs  │       │
                  │ MCP Servers     │       │
                  └─────────────────┘       │
                           │                │
                  ┌────────┴────────────────┴──────┐
                  │        VNC/CDP Services        │
                  │     Ports: 5900, 9222         │
                  └────────────────────────────────┘
\`\`\`

## Core Components

### 1. Frontend (Vue.js)
- **Technology**: Vue 3 + TypeScript + Vite
- **Port**: 5173
- **Responsibilities**:
  - User interface and experience
  - Real-time chat with agents
  - Tool panel management
  - VNC viewer integration
  - Session management

### 2. Backend (FastAPI)
- **Technology**: Python 3.12 + FastAPI + Pydantic
- **Port**: 8000
- **Responsibilities**:
  - API endpoints and routing
  - Agent orchestration
  - Session persistence
  - WebSocket/SSE communication
  - Authentication and authorization
  - LLM integration

### 3. Sandbox (Ubuntu Container)
- **Technology**: Ubuntu 22.04 + Chrome + VNC
- **Ports**: 8080 (API), 5900 (VNC), 9222 (CDP)
- **Responsibilities**:
  - Isolated tool execution
  - Browser automation
  - Shell command execution
  - File operations
  - Remote desktop access

### 4. LLM Service (Docker Model Runner)
- **Technology**: Docker Model Runner + OpenAI API
- **Port**: 11434
- **Responsibilities**:
  - Local LLM inference
  - OpenAI-compatible API
  - Model management
  - GPU acceleration (optional)

## Data Flow

### 1. User Interaction Flow
\`\`\`
User Input → Frontend → Backend → Agent Manager → Tool Execution → Response
     ↑                                                                ↓
     └────────────────── WebSocket/SSE ←──────────────────────────────┘
\`\`\`

### 2. Agent Processing Flow
\`\`\`
Message → Backend → LLM Service → Tool Selection → Sandbox Execution
    ↓                                                        ↓
Session Storage ←─────────── Response Generation ←──────────┘
\`\`\`

### 3. Tool Execution Flow
\`\`\`
Tool Request → Sandbox API → Tool Execution → Result Capture → Response
      ↓                                                           ↑
   VNC Stream ←─────────── Real-time Monitoring ←─────────────────┘
\`\`\`

## Service Communication

### Internal Communication
- **HTTP/REST**: API calls between services
- **WebSocket**: Real-time bidirectional communication
- **SSE**: Server-sent events for streaming responses
- **Docker Network**: Internal service discovery

### External Communication
- **MCP Protocol**: Model Context Protocol for tool integration
- **CDP**: Chrome DevTools Protocol for browser control
- **VNC**: Virtual Network Computing for remote desktop

## Security Architecture

### Authentication Layer
\`\`\`
Client Request → JWT Validation → Role Check → API Access
                      ↓
                Rate Limiting → Input Validation → Execution
\`\`\`

### Sandbox Isolation
- **Container Isolation**: Each session gets isolated environment
- **Resource Limits**: CPU, memory, and disk quotas
- **Network Isolation**: Controlled external access
- **File System**: Temporary, disposable storage

## Scalability Considerations

### Horizontal Scaling
- **Load Balancer**: Distribute requests across backend instances
- **Session Affinity**: Maintain user sessions with specific instances
- **Database Sharding**: Distribute data across multiple databases

### Vertical Scaling
- **Resource Allocation**: Dynamic CPU/memory allocation
- **GPU Utilization**: Efficient model inference scaling
- **Cache Optimization**: Redis for session and response caching

## Deployment Architecture

### Development Environment
\`\`\`
Docker Compose → Local Services → Hot Reload → Development
\`\`\`

### Production Environment
\`\`\`
Container Registry → Orchestration Platform → Load Balancer → Production
\`\`\`

### Supported Platforms
- **Local**: Docker Compose
- **Cloud**: Railway, AWS, GCP, Azure
- **Kubernetes**: Helm charts (roadmap)
- **Docker Swarm**: Multi-node deployment (roadmap)

## Performance Characteristics

### Latency Targets
- **API Response**: < 100ms (95th percentile)
- **Agent Response**: < 2s (typical)
- **Tool Execution**: < 5s (typical)
- **VNC Streaming**: < 50ms (local network)

### Throughput Targets
- **Concurrent Users**: 100+ (single instance)
- **Messages/Second**: 1000+ (with caching)
- **Tool Executions**: 50+ concurrent

### Resource Requirements
- **Minimum**: 4 CPU cores, 8GB RAM, 20GB storage
- **Recommended**: 8 CPU cores, 16GB RAM, 100GB storage
- **GPU**: Optional, improves LLM inference speed

## Monitoring and Observability

### Metrics Collection
- **Application Metrics**: Response times, error rates
- **System Metrics**: CPU, memory, disk usage
- **Business Metrics**: Agent usage, tool execution stats

### Logging Strategy
- **Structured Logging**: JSON format for easy parsing
- **Log Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Log Aggregation**: Centralized logging system

### Health Checks
- **Service Health**: HTTP endpoints for status checks
- **Dependency Health**: Database, Redis, LLM service status
- **Resource Health**: System resource monitoring

This architecture provides a solid foundation for building and scaling AI agent applications while maintaining security, performance, and reliability.
