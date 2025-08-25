# AGENTS.md - AI Agent Development Guide

## Purpose

This file provides comprehensive instructions and context for AI coding agents interacting with the Agentic project. It serves as the authoritative guide for automated development workflows, code generation, and system integration patterns.

## Project Architecture

### System Overview
Agentic is a distributed, containerized AI agent system designed for maximum flexibility and scalability:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   Sandbox       │
│   Vue.js/TS     │◄──►│  Python/FastAPI │◄──►│  Ubuntu Container│
│   Port: 3000    │    │   Port: 8000    │    │   Isolated Env  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 ▼
                    ┌─────────────────┐
                    │  LLM Service    │
                    │ Docker Models   │
                    │  Port: 8001     │
                    └─────────────────┘
```

### Core Components

1. **Frontend Layer** (`frontend/`)
   - Vue.js 3 with TypeScript
   - Composition API pattern
   - Vuex for state management
   - Axios for HTTP requests
   - WebSocket for real-time communication

2. **Backend Layer** (`backend/`)
   - FastAPI with Python 3.8+
   - Async/await patterns
   - Pydantic models
   - JWT authentication
   - Redis caching

3. **Agent System** (`backend/core/`)
   - MCP protocol integration
   - Tool wrapper system
   - Session management
   - Browser automation

4. **Infrastructure**
   - Docker containers
   - Docker Compose orchestration
   - MongoDB persistence
   - Redis caching

## Core Agents

### 1. Browser Automation Agent
**Location**: `backend/core/browser_automation.py`

**Purpose**: Handles automated browser interactions via Chrome DevTools Protocol (CDP)

**Key Features**:
- Isolated sandbox execution for security
- Support for both sync/async operations
- Selenium integration for complex scenarios
- Screenshot and video recording capabilities

**Code Pattern**:
```python
class BrowserAutomationAgent:
    def __init__(self, sandbox_url: str):
        self.sandbox_url = sandbox_url
        self.cdp_client = CDPClient()
    
    async def execute_action(self, action: BrowserAction) -> ActionResult:
        # Implementation follows CDP protocol
        pass
```

### 2. MCP Integration Agent
**Location**: `backend/core/mcp_integration.py`

**Purpose**: Manages Model Context Protocol integration between LLMs and tools

**Key Features**:
- Standardized tool interface
- Dynamic tool registration
- Protocol versioning support
- Error handling and recovery

**Code Pattern**:
```python
class MCPIntegrationAgent:
    def __init__(self, config: MCPConfig):
        self.servers = {}
        self.tools_registry = ToolsRegistry()
    
    async def register_tool(self, tool: MCPTool) -> bool:
        # Tool registration logic
        pass
```

### 3. GitHub MCP Server Agent
**Location**: `backend/core/github_mcp_server.py`

**Purpose**: Specialized agent for GitHub repository operations

**Key Features**:
- Repository cloning and management
- Git operations (commit, push, pull, merge)
- Code analysis and review
- Issue and PR management

**Code Pattern**:
```python
class GitHubMCPServerAgent:
    def __init__(self, token: str):
        self.github_client = GitHubClient(token)
        self.git_ops = GitOperations()
    
    async def clone_repository(self, repo_url: str) -> RepoInfo:
        # Repository management logic
        pass
```

### 4. Session Manager Agent
**Location**: `backend/core/session_manager.py`

**Purpose**: Manages user sessions, state, and multi-user coordination

**Key Features**:
- Redis-based session storage
- Authentication state management
- WebSocket connection handling
- Session cleanup and expiry

**Code Pattern**:
```python
class SessionManagerAgent:
    def __init__(self, redis_client: RedisClient):
        self.redis = redis_client
        self.active_sessions = {}
    
    async def create_session(self, user_id: str) -> SessionInfo:
        # Session creation and management
        pass
```

## Tool Integration System

### MCP Tools Wrapper
**Location**: `backend/core/mcp_tools_wrapper.py`

**Purpose**: Unified interface for all MCP-compatible tools

**Architecture**:
```python
class MCPToolsWrapper:
    """
    Provides standardized interface for MCP tools
    Handles tool discovery, registration, and execution
    """
    
    def __init__(self):
        self.registered_tools = {}
        self.tool_configs = {}
    
    async def discover_tools(self) -> List[ToolInfo]:
        """Auto-discover available MCP tools"""
        pass
    
    async def execute_tool(self, tool_name: str, params: dict) -> ToolResult:
        """Execute registered tool with parameters"""
        pass
```

### KQL Integration Server
**Location**: `mcp-kql-server/`

**Purpose**: Kusto Query Language integration for data analysis

**Features**:
- Data querying and analysis
- Authentication and access control
- Memory management for query results
- Real-time streaming support

## Development Guidelines

### Code Standards

#### Frontend Development
```typescript
// Component Structure
<template>
  <!-- Vue 3 Composition API template -->
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import type { ComponentProps } from '@/types'

// Props definition
interface Props {
  modelValue: string
  placeholder?: string
}

const props = withDefaults(defineProps<Props>(), {
  placeholder: 'Enter value...'
})

// Reactive state
const inputValue = ref(props.modelValue)
const isLoading = ref(false)

// Computed properties
const isValid = computed(() => inputValue.value.length > 0)

// Methods
const handleSubmit = async () => {
  isLoading.value = true
  try {
    // Implementation
  } catch (error) {
    console.error('Submission failed:', error)
  } finally {
    isLoading.value = false
  }
}
</script>
```

#### Backend Development
```python
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import asyncio

# Models
class AgentRequest(BaseModel):
    action: str
    parameters: dict
    timeout: Optional[int] = 30

class AgentResponse(BaseModel):
    success: bool
    result: dict
    execution_time: float
    error_message: Optional[str] = None

# Router
router = APIRouter(prefix="/api/agents", tags=["agents"])

@router.post("/execute", response_model=AgentResponse)
async def execute_agent_action(
    request: AgentRequest,
    current_user: str = Depends(get_current_user)
) -> AgentResponse:
    """Execute agent action with proper error handling"""
    start_time = time.time()
    
    try:
        # Input validation
        if not request.action:
            raise HTTPException(400, "Action is required")
        
        # Execute action
        result = await agent_executor.execute(
            action=request.action,
            params=request.parameters,
            timeout=request.timeout
        )
        
        return AgentResponse(
            success=True,
            result=result,
            execution_time=time.time() - start_time
        )
    
    except Exception as e:
        logger.error(f"Agent execution failed: {e}")
        return AgentResponse(
            success=False,
            result={},
            execution_time=time.time() - start_time,
            error_message=str(e)
        )
```

### Testing Patterns

#### Unit Tests
```python
import pytest
from unittest.mock import Mock, AsyncMock
from backend.core.browser_automation import BrowserAutomationAgent

class TestBrowserAutomationAgent:
    @pytest.fixture
    def agent(self):
        return BrowserAutomationAgent("http://sandbox:3000")
    
    @pytest.mark.asyncio
    async def test_execute_click_action(self, agent):
        # Arrange
        action = BrowserAction(type="click", selector="#button")
        
        # Act
        result = await agent.execute_action(action)
        
        # Assert
        assert result.success is True
        assert result.execution_time < 5.0
```

#### Integration Tests
```typescript
// Frontend integration test
import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import AgentControl from '@/components/AgentControl.vue'

describe('AgentControl', () => {
  it('executes agent action successfully', async () => {
    const wrapper = mount(AgentControl, {
      props: { agentId: 'browser-automation' }
    })
    
    await wrapper.find('[data-testid="execute-button"]').trigger('click')
    
    expect(wrapper.emitted('action-executed')).toBeTruthy()
  })
})
```

### Build and Deployment

#### Automated Build Process
```bash
#!/bin/bash
# build.sh - Automated build script

set -e

echo "Building Agentic System..."

# Frontend Build
echo "Building frontend..."
cd frontend
npm ci --silent
npm run type-check
npm run lint
npm run test:unit
npm run build
cd ..

# Backend Build
echo "Building backend..."
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m pytest tests/ -v --cov=. --cov-report=term-missing
cd ..

# Docker Build
echo "Building containers..."
docker-compose -f docker-compose.yml build --parallel

# System Integration Test
echo "Running integration tests..."
docker-compose -f docker-compose.test.yml up --abort-on-container-exit

echo "Build completed successfully!"
```

#### Production Deployment
```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.prod
    ports:
      - "80:80"
    environment:
      - NODE_ENV=production
    depends_on:
      - backend

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
      - REDIS_URL=redis://redis:6379
      - MONGODB_URL=mongodb://mongo:27017/agentic
    depends_on:
      - redis
      - mongo

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

  mongo:
    image: mongo:6
    volumes:
      - mongo_data:/data/db

volumes:
  redis_data:
  mongo_data:
```

## Agent Communication Patterns

### WebSocket Events
```typescript
// WebSocket event handling
interface AgentEvent {
  type: 'agent.status' | 'agent.result' | 'agent.error'
  agentId: string
  data: any
  timestamp: number
}

class AgentWebSocketClient {
  private ws: WebSocket
  private eventHandlers: Map<string, Function[]> = new Map()
  
  connect(url: string): Promise<void> {
    return new Promise((resolve, reject) => {
      this.ws = new WebSocket(url)
      
      this.ws.onopen = () => resolve()
      this.ws.onerror = reject
      
      this.ws.onmessage = (event) => {
        const agentEvent: AgentEvent = JSON.parse(event.data)
        this.handleEvent(agentEvent)
      }
    })
  }
  
  private handleEvent(event: AgentEvent): void {
    const handlers = this.eventHandlers.get(event.type) || []
    handlers.forEach(handler => handler(event))
  }
}
```

### HTTP API Patterns
```python
# Standardized API response format
from typing import Generic, TypeVar, Optional
from pydantic import BaseModel

T = TypeVar('T')

class APIResponse(BaseModel, Generic[T]):
    success: bool
    data: Optional[T] = None
    message: Optional[str] = None
    error_code: Optional[str] = None
    execution_time: float
    request_id: str

# Usage example
@router.get("/agents/{agent_id}/status")
async def get_agent_status(agent_id: str) -> APIResponse[AgentStatus]:
    try:
        status = await agent_manager.get_status(agent_id)
        return APIResponse(
            success=True,
            data=status,
            execution_time=0.05,
            request_id=generate_request_id()
        )
    except AgentNotFound:
        return APIResponse(
            success=False,
            message="Agent not found",
            error_code="AGENT_NOT_FOUND",
            execution_time=0.01,
            request_id=generate_request_id()
        )
```

## Security and Performance

### Security Guidelines
1. **Input Validation**: All inputs must be validated using Pydantic models
2. **Authentication**: JWT tokens for API access, session-based for WebSocket
3. **Sandbox Isolation**: Browser automation runs in isolated containers
4. **Rate Limiting**: Implement rate limiting for all public endpoints
5. **Logging**: Comprehensive audit logging for all operations

### Performance Optimization
1. **Async Operations**: Use async/await for all I/O operations
2. **Connection Pooling**: Database and HTTP connection pools
3. **Caching Strategy**: Redis for frequently accessed data
4. **Resource Monitoring**: Track memory and CPU usage
5. **Load Balancing**: Horizontal scaling for high traffic

## Error Handling and Recovery

### Error Classification
```python
from enum import Enum

class ErrorCode(Enum):
    # Client errors (4xx)
    INVALID_INPUT = "INVALID_INPUT"
    UNAUTHORIZED = "UNAUTHORIZED"
    AGENT_NOT_FOUND = "AGENT_NOT_FOUND"
    
    # Server errors (5xx)
    INTERNAL_ERROR = "INTERNAL_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    TIMEOUT = "TIMEOUT"

class AgenticError(Exception):
    def __init__(self, code: ErrorCode, message: str, details: dict = None):
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(message)

# Error handler
@app.exception_handler(AgenticError)
async def handle_agentic_error(request: Request, exc: AgenticError):
    return JSONResponse(
        status_code=get_status_code(exc.code),
        content={
            "success": False,
            "error_code": exc.code.value,
            "message": exc.message,
            "details": exc.details
        }
    )
```

### Recovery Strategies
1. **Retry Logic**: Exponential backoff for transient failures
2. **Circuit Breakers**: Prevent cascade failures
3. **Graceful Degradation**: Fallback to basic functionality
4. **Health Checks**: Automatic service recovery

## Monitoring and Observability

### Logging Strategy
```python
import structlog
from typing import Any

logger = structlog.get_logger()

class AgentLogger:
    @staticmethod
    def log_agent_action(
        agent_id: str,
        action: str,
        user_id: str,
        duration: float,
        success: bool,
        **kwargs: Any
    ):
        logger.info(
            "agent_action_executed",
            agent_id=agent_id,
            action=action,
            user_id=user_id,
            duration_ms=duration * 1000,
            success=success,
            **kwargs
        )
```

### Metrics Collection
```python
from prometheus_client import Counter, Histogram, Gauge

# Metrics
agent_requests_total = Counter(
    'agent_requests_total',
    'Total agent requests',
    ['agent_id', 'action', 'status']
)

agent_execution_time = Histogram(
    'agent_execution_seconds',
    'Agent execution time',
    ['agent_id', 'action']
)

active_agents = Gauge(
    'active_agents',
    'Number of active agents',
    ['agent_type']
)
```

## Configuration Management

### Environment Configuration
```python
from pydantic import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    mongodb_url: str = "mongodb://localhost:27017/agentic"
    redis_url: str = "redis://localhost:6379"
    
    # Authentication
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Services
    sandbox_url: str = "http://sandbox:3000"
    llm_service_url: str = "http://llm:8001"
    
    # Features
    enable_browser_automation: bool = True
    enable_github_integration: bool = True
    max_concurrent_agents: int = 10
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"
    
    class Config:
        env_file = ".env"

settings = Settings()
```

## MCP Server Configuration

### Perfect VS Code Integration
```json
{
  "mcpServers": {
    "agentic-core": {
      "command": "python",
      "args": ["-m", "backend.core.mcp_integration"],
      "env": {
        "AGENTIC_CONFIG_PATH": "${workspaceFolder}/.agentic/config.json",
        "PYTHONPATH": "${workspaceFolder}"
      },
      "cwd": "${workspaceFolder}"
    },
    "browser-automation": {
      "command": "python",
      "args": ["-m", "backend.core.browser_automation"],
      "env": {
        "SANDBOX_URL": "http://localhost:3001",
        "CDP_PORT": "9222"
      }
    },
    "github-integration": {
      "command": "python",
      "args": ["-m", "backend.core.github_mcp_server"],
      "env": {
        "GITHUB_TOKEN": "${env:GITHUB_TOKEN}",
        "WORKSPACE_PATH": "${workspaceFolder}"
      }
    }
  }
}
```

## Development Workflow

### Agent Development Lifecycle
1. **Planning**: Define agent purpose and interface
2. **Implementation**: Follow coding standards and patterns
3. **Testing**: Unit, integration, and performance tests
4. **Documentation**: Update API docs and examples
5. **Deployment**: Container build and orchestration
6. **Monitoring**: Metrics, logging, and alerting

### Code Review Checklist
- [ ] Type hints and proper typing
- [ ] Error handling and recovery
- [ ] Input validation
- [ ] Security considerations
- [ ] Performance optimization
- [ ] Test coverage (>80%)
- [ ] Documentation updates
- [ ] Logging and monitoring

## Troubleshooting Guide

### Common Issues

#### Build Failures
```bash
# Clear caches and rebuild
docker system prune -f
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

#### Agent Communication Issues
```python
# Debug WebSocket connections
import websockets
import asyncio

async def test_websocket():
    uri = "ws://localhost:8000/ws/agents"
    async with websockets.connect(uri) as websocket:
        await websocket.send(json.dumps({"type": "ping"}))
        response = await websocket.recv()
        print(f"Response: {response}")
```

#### Performance Problems
```python
# Profile agent execution
import cProfile
import pstats

def profile_agent_execution():
    profiler = cProfile.Profile()
    profiler.enable()
    
    # Agent execution code here
    
    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative').print_stats(20)
```

## Migration and Updates

### Version Compatibility
- Maintain backward compatibility for minor versions
- Provide migration scripts for major version changes
- Document breaking changes clearly
- Support graceful degradation

### Update Process
1. **Backup**: Create system backup before updates
2. **Test**: Validate in staging environment
3. **Deploy**: Rolling deployment for zero downtime
4. **Verify**: Health checks and smoke tests
5. **Rollback**: Automated rollback on failure

This comprehensive guide ensures consistent, maintainable, and secure development of AI agents within the Agentic platform. All agents must follow these patterns and guidelines to maintain system integrity and performance.