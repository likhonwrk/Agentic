# AGENTS.md - AI Agent Instructions

## Purpose

This file provides specialized instructions and context for AI coding agents interacting with the Agentic project. While README.md serves human contributors, AGENTS.md contains structured information optimized for machine comprehension and automated development workflows.

## Project Context

Agentic is a distributed, containerized AI agent system with:

1. Frontend (Vue.js/TypeScript)
2. Backend (Python/FastAPI)
3. Sandbox (Ubuntu Container) 
4. LLM Service (Docker Model Runner)

### Build Process Details

For automated builds and testing:

```bash
# Frontend Build Steps
cd frontend
npm ci  # Deterministic installs
npm run type-check
npm run build

# Backend Build Steps 
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest tests/

# Full System Build
docker-compose -f docker-compose.yml up -d --build
```

### Code Structure Rules

1. Frontend:
   - All Vue components in `frontend/src/components/`
   - Types in `frontend/src/types/`
   - Services in `frontend/src/services/`
   - State management in Vuex store
   - Strict TypeScript checking enabled

2. Backend:
   - FastAPI routes in `backend/api/`
   - Core logic in `backend/core/`
   - Models in `backend/core/models.py`
   - Utils in `backend/utils/`
   - 100% type hints required
   - pytest for all new code

3. Common Rules:
   - Clear error handling
   - Comprehensive logging
   - Input validation
   - Security checks
   - Performance considerations

### Testing Requirements

1. Unit Tests:
   - Frontend: Jest + Vue Test Utils
   - Backend: pytest
   - Coverage threshold: 80%

2. Integration Tests:
   - API contract tests
   - End-to-end flows
   - Browser automation tests

3. Performance Tests:
   - Load testing with K6
   - Memory profiling
   - Response time benchmarks

### Conventions

1. Commit Messages:
   - Conventional Commits format
   - Link to issues when relevant
   - Include test coverage info

2. Code Style:
   - Frontend: ESLint + Prettier
   - Backend: Black + isort
   - Max line length: 88 characters
   - Docstrings required

3. Error Handling:
   - Custom error classes
   - Structured error responses
   - Detailed logging
   - Graceful degradation

### Agent-Specific Guidelines

1. Code Generation:
   - Follow existing patterns
   - Include tests
   - Add type hints
   - Document assumptions

2. Refactoring:
   - Maintain backward compatibility
   - Update tests
   - Verify performance
   - Check dependencies

3. Review Process:
   - Run linters
   - Execute test suite
   - Check coverage
   - Verify build

4. Documentation:
   - Update relevant docs
   - Add code comments
   - Include examples
   - Note changes

## API Documentation

Detailed API documentation for automated integration:

1. Frontend APIs:
   - Session management
   - Authentication
   - WebSocket events
   - Tool integration

2. Backend APIs:
   - User management
   - Agent control
   - System monitoring
   - Tool execution

3. Integration Points:
   - Browser automation
   - LLM services
   - External tools
   - Data storage

## Common Patterns

1. State Management:
   - Redis for caching
   - MongoDB for persistence
   - WebSocket for real-time
   - JWT for auth

2. Error Handling:
   - Custom exceptions
   - Status codes
   - Error messages
   - Recovery steps

3. Security:
   - Input validation
   - Authorization checks
   - Rate limiting
   - Sandbox isolation

4. Performance:
   - Caching strategies
   - Query optimization
   - Resource pooling
   - Load balancing

## Maintenance Tasks

1. Regular Checks:
   - Dependency updates
   - Security patches
   - Performance metrics
   - Error rates

2. Cleanup:
   - Log rotation
   - Cache invalidation
   - Session cleanup
   - Temp files

3. Monitoring:
   - System health
   - Resource usage
   - Error tracking
   - User activity

## Development Environment

Required tools and configurations:

1. Core Requirements:
   - Node.js 16+
   - Python 3.8+
   - Docker
   - Git

2. Development Tools:
   - VS Code
   - ESLint
   - Black
   - pytest

3. Environment Variables:
   - API keys
   - Database URLs
   - Feature flags
   - Debug settings

## Troubleshooting Guide

Common issues and solutions:

1. Build Problems:
   - Clear node_modules
   - Rebuild virtual env
   - Check Docker cache
   - Verify dependencies

2. Runtime Issues:
   - Check logs
   - Verify configs
   - Test connectivity
   - Monitor resources

3. Integration Errors:
   - Validate APIs
   - Check permissions
   - Test network
   - Verify tokens

## Version History

Document changes and migrations:

1. Major Updates:
   - Breaking changes
   - Migration steps
   - Rollback procedures
   - Compatibility notes

2. Feature Additions:
   - New capabilities
   - Integration points
   - Configuration options
   - Usage examples

3. Bug Fixes:
   - Issue details
   - Root causes
   - Fix verification
   - Prevention measures
